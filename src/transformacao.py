"""Transformação: agregações por canal e período (sempre razão de somas), tabelas de apoio e exportação.

Toda agregação soma as medidas aditivas no nível desejado e só depois recalcula os KPIs com
``tratamento.kpis_de_componentes``. Nenhum KPI é obtido pela média de razões já calculadas.
"""

from __future__ import annotations

import json
import logging
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from src import ErroQualidadeDados
from src import config
from src.extracao import take_rate_item_2026
from src.tratamento import kpis_de_componentes, validar_kpis

logger = logging.getLogger(__name__)

MEDIDAS = config.MEDIDAS_ADITIVAS
COMPONENTES_CUSTO = ["cmv", "comissoes_tarifas", "frete_subsidiado", "investimento_marketing", "custos_fixos", "impostos", "margem_liquida"]
CUSTOS_VARIAVEIS = ["cmv", "comissoes_tarifas", "frete_subsidiado", "impostos_variaveis", "investimento_marketing"]


# ---------------------------------------------------------------------------
# Agregações
# ---------------------------------------------------------------------------
def agregar(df: pd.DataFrame, dimensoes: list[str]) -> pd.DataFrame:
    """Soma as medidas aditivas por ``dimensoes`` e recalcula os KPIs pela razão das somas.

    Args:
        df: base analítica.
        dimensoes: colunas de agrupamento.

    Returns:
        Tabela agregada (dimensões + medidas + KPIs) na ordem canônica.
    """
    somas = df.groupby(dimensoes, sort=False, observed=True)[MEDIDAS].sum().reset_index()
    tabela = pd.concat([somas, kpis_de_componentes(somas)], axis=1)
    return config.ordenar_canonico(tabela, dimensoes)


def participacao_por_canal(df: pd.DataFrame, recorte_col: str | list[str]) -> pd.DataFrame:
    """Participação de cada canal na receita real dentro de cada recorte (soma 100% por recorte).

    Args:
        df: base analítica.
        recorte_col: coluna(s) que definem o recorte.

    Returns:
        Tabela com o recorte, ``canal`` e ``participacao_canal``.
    """
    recorte = [recorte_col] if isinstance(recorte_col, str) else list(recorte_col)
    g = df.groupby(recorte + ["canal"], sort=False, observed=True)["receita_bruta_real"].sum().reset_index()
    total = g.groupby(recorte, sort=False, observed=True)["receita_bruta_real"].transform("sum")
    g["participacao_canal"] = g["receita_bruta_real"] / total
    return g.drop(columns=["receita_bruta_real"])


def parametros_cvp(df: pd.DataFrame, filtro: pd.Series, chaves: list[str]) -> pd.DataFrame:
    """Parâmetros de custo-volume-lucro por (chaves, canal): v, F, PE e R_ref.

    ``v`` = custos variáveis ÷ receita; ``F`` = (custos fixos + impostos fixos) ÷ negócios-mês;
    ``PE`` = F ÷ (1 − v); ``R_ref`` = receita por negócio de todos os canais do grupo.

    Args:
        df: base analítica.
        filtro: máscara booleana das linhas (ex.: Cenário Atual).
        chaves: ``["porte"]`` ou ``["porte", "segmento"]``.

    Returns:
        Tabela ``porte, segmento, canal, v, F, PE, R_ref`` (``segmento = "Todos"`` no nível do porte).
    """
    base = df[filtro]
    g = base.groupby(chaves + ["canal"], sort=False, observed=True)[MEDIDAS].sum().reset_index()
    g["v"] = g[CUSTOS_VARIAVEIS].sum(axis=1) / g["receita_bruta"]
    g["F"] = (g["custos_fixos"] + g["impostos_fixos"]) / g["negocios_ativos"]
    g["PE"] = np.where(g["v"] < 1, g["F"] / (1.0 - g["v"]), np.nan)
    ref = base.groupby(chaves, sort=False, observed=True)[["receita_bruta", "negocios_ativos"]].sum()
    ref["R_ref"] = ref["receita_bruta"] / ref["negocios_ativos"]
    g = g.merge(ref[["R_ref"]].reset_index(), on=chaves, how="left")
    if "segmento" not in chaves:
        g["segmento"] = "Todos"
    g = g[["porte", "segmento", "canal", "v", "F", "PE", "R_ref"]]
    return config.ordenar_canonico(g, ["porte", "segmento", "canal"]) if "segmento" in chaves else config.ordenar_canonico(g, ["porte", "canal"])


def receita_indiferenca(params: pd.DataFrame) -> pd.DataFrame:
    """Receita mensal por negócio em que dois canais dão a mesma margem: R* = (F_A − F_B) ÷ (v_B − v_A).

    Acima de R*, vence o canal de menor ``v``; abaixo, o outro. Se R* ≤ 0 ou não houver
    cruzamento, o mesmo canal domina em toda receita positiva.

    Args:
        params: parâmetros CVP no nível do porte (``segmento = "Todos"``).

    Returns:
        Tabela ``porte, canal_a, canal_b, r_estrela, vencedor_abaixo, vencedor_acima, situacao``.
    """
    linhas = []
    for porte in config.PORTES:
        sub = params[(params["porte"] == porte) & (params["segmento"] == "Todos")].set_index("canal")
        for a, b in combinations(config.CANAIS, 2):
            va, vb = float(sub.at[a, "v"]), float(sub.at[b, "v"])
            fa, fb = float(sub.at[a, "F"]), float(sub.at[b, "F"])
            menor_v = a if va < vb else b
            outro = b if menor_v == a else a
            if va != vb:
                r = (fa - fb) / (vb - va)
            else:
                r = np.nan
            if pd.notna(r) and r > 0:
                linhas.append({"porte": porte, "canal_a": a, "canal_b": b, "r_estrela": r,
                               "vencedor_abaixo": outro, "vencedor_acima": menor_v, "situacao": "cruzamento"})
            else:
                dominante = menor_v if va != vb else (a if fa <= fb else b)
                linhas.append({"porte": porte, "canal_a": a, "canal_b": b, "r_estrela": np.nan,
                               "vencedor_abaixo": dominante, "vencedor_acima": dominante, "situacao": "domina"})
    return pd.DataFrame(linhas)


def matriz_recomendacao(params: pd.DataFrame) -> pd.DataFrame:
    """Recomendação de canal por porte × segmento, pela margem em R_ref = R_ref × (1 − v) − F.

    Se a vantagem do 1º sobre o 2º for ≥ 1,0 p.p. de R_ref, recomenda o 1º; senão, "Híbrido".

    Args:
        params: parâmetros CVP por segmento.

    Returns:
        Tabela ``porte, segmento, canal_1, margem_1, canal_2, margem_2, vantagem_pp, recomendacao``.
    """
    linhas = []
    base = params[params["segmento"] != "Todos"].copy()
    base["margem"] = base["R_ref"] * (1.0 - base["v"]) - base["F"]
    for porte in config.PORTES:
        for seg in config.SEGMENTOS:
            sub = base[(base["porte"] == porte) & (base["segmento"] == seg)].sort_values("margem", ascending=False)
            p1, p2 = sub.iloc[0], sub.iloc[1]
            vantagem = (p1["margem"] - p2["margem"]) / p1["R_ref"] * 100.0
            reco = p1["canal"] if vantagem >= config.LIMIAR_RECOMENDACAO_PP else f"Híbrido: {p1['canal']} + {p2['canal']}"
            linhas.append({"porte": porte, "segmento": seg, "canal_1": p1["canal"], "margem_1": p1["margem"],
                           "canal_2": p2["canal"], "margem_2": p2["margem"], "vantagem_pp": vantagem, "recomendacao": reco})
    return pd.DataFrame(linhas)


def tabela_tarifas_marketplaces_2026() -> pd.DataFrame:
    """*Take rate* efetivo por valor de item com as regras oficiais vigentes (consulta em 18/10/2026).

    Returns:
        Tabela ``valor_item, plataforma, plano, take_rate, tipo_ponto, observacao`` com a grade de
        R$ 20 a R$ 500 (passo 1) e os pontos discretos da tabela do artigo.
    """
    linhas = []
    grade = [float(v) for v in range(config.TARIFAS_GRADE[0], config.TARIFAS_GRADE[1] + 1)]
    for tipo, valores in (("grade", grade), ("discreto", config.TARIFAS_PONTOS)):
        for p in config.TARIFAS_PLATAFORMAS:
            for v in valores:
                linhas.append({"valor_item": v, "plataforma": p["plataforma"], "plano": p["plano"],
                               "take_rate": take_rate_item_2026(p["chave"], v), "tipo_ponto": tipo,
                               "observacao": p["observacao"]})
    return pd.DataFrame(linhas)


def _participacao_digital(df: pd.DataFrame, mascara: pd.Series, coluna: str = "receita_bruta_real") -> float:
    """Participação de Marketplace + E-commerce Próprio na receita de um recorte.

    Args:
        df: base analítica.
        mascara: linhas do recorte.
        coluna: medida de receita.

    Returns:
        Fração digital.
    """
    sub = df[mascara]
    return float(sub.loc[sub["canal"].isin(config.CANAIS_DIGITAIS), coluna].sum() / sub[coluna].sum())


def tabela_calibracao(df: pd.DataFrame, pac: pd.DataFrame, pmc: pd.DataFrame) -> pd.DataFrame:
    """Checagens de calibração C1–C6 (seção 7.9), com referências recalculadas dos dados oficiais.

    Args:
        df: base analítica.
        pac: tabela ``pac_internet``.
        pmc: PMC 8880 (formato largo).

    Returns:
        Tabela ``codigo, metrica, valor_simulado, faixa_min, faixa_max, referencia, fonte, status``.
    """
    digital = df["canal"].isin(config.CANAIS_DIGITAIS)
    ano = df["ano"]
    c1 = float(df.loc[digital & (ano == 2024), "receita_bruta"].sum() / df.loc[digital & (ano == 2019), "receita_bruta"].sum())
    c2 = _participacao_digital(df, ano == 2021) / _participacao_digital(df, ano == 2019)

    def variacao(mascara_canal: pd.Series) -> float:
        """Variação da receita real entre fev/2020 e abr/2020."""
        abr = df.loc[mascara_canal & (df["data"] == "2020-04-01"), "receita_bruta_real"].sum()
        fev = df.loc[mascara_canal & (df["data"] == "2020-02-01"), "receita_bruta_real"].sum()
        return float(abr / fev - 1.0)

    c3 = variacao(df["canal"] == "Loja Física")
    c4 = variacao(digital)
    atual = df["recorte_temporal"] == config.RECORTE_ATUAL
    c5 = _participacao_digital(df, atual)
    mkt = df[atual & (df["canal"] == "Marketplace")]
    c6 = float(mkt["comissoes_tarifas"].sum() / mkt["receita_bruta"].sum())
    valores = {"C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5, "C6": c6}

    tot = pac[pac["papel"] == "total"].set_index("ano")
    pmc_sa = pmc.set_index("data")["vol_sa"]
    ref_extra = {
        "C1": f" | recalculado: {tot.at[2024, 'receita_internet_mil_reais'] / tot.at[2019, 'receita_internet_mil_reais']:.2f}",
        "C2": f" | recalculado: {tot.at[2021, 'participacao_internet'] / tot.at[2019, 'participacao_internet']:.2f}",
        "C3": f" | recalculado: {(pmc_sa.loc['2020-04-01'] / pmc_sa.loc['2020-02-01'] - 1) * 100:.1f}%",
    }
    linhas = []
    for codigo, spec in config.CALIBRACAO.items():
        v = valores[codigo]
        ok = spec["min"] <= v <= spec["max"]  # type: ignore[operator]
        if not ok:
            logger.warning("Calibração %s fora da faixa: %.4f (faixa %s a %s)", codigo, v, spec["min"], spec["max"])
        linhas.append({
            "codigo": codigo, "metrica": spec["metrica"], "valor_simulado": v,
            "faixa_min": spec["min"] if np.isfinite(spec["min"]) else np.nan,  # type: ignore[arg-type]
            "faixa_max": spec["max"] if np.isfinite(spec["max"]) else np.nan,  # type: ignore[arg-type]
            "referencia": str(spec["referencia"]) + ref_extra.get(codigo, ""), "fonte": spec["fonte"],
            "status": "OK" if ok else "FORA DA FAIXA",
        })
    tabela = pd.DataFrame(linhas)
    logger.info("Calibração: %s", {r["codigo"]: f"{r['valor_simulado']:.4f} {r['status']}" for _, r in tabela.iterrows()})
    return tabela


def serie_macro_mensal(pmc: pd.DataFrame, ipca: pd.DataFrame, fonte_ipca: str, data_fim: pd.Timestamp) -> pd.DataFrame:
    """Série mensal oficial para o gráfico 09: PMC 8880 com ajuste, IPCA mensal, índice e acumulado em 12 meses.

    O acumulado em 12 meses = (Π dos 12 últimos (1 + ipca ÷ 100) − 1) × 100, NaN até 2018-11.

    Args:
        pmc: PMC 8880 (formato largo).
        ipca: IPCA mensal.
        fonte_ipca: rótulo da fonte do IPCA.
        data_fim: último mês.

    Returns:
        Tabela ``data, pmc_indice_volume_varejo_sa, ipca_variacao_mensal, ipca_indice, ipca_acumulado_12m, fonte_ipca``.
    """
    ip = ipca.sort_values("data").reset_index(drop=True).copy()
    fator = 1.0 + ip["ipca_variacao_mensal"] / 100.0
    ip["ipca_indice"] = 100.0 * fator.cumprod()
    ip["ipca_acumulado_12m"] = (fator.rolling(12).apply(np.prod, raw=True) - 1.0) * 100.0
    out = ip.merge(pmc[["data", "vol_sa"]].rename(columns={"vol_sa": "pmc_indice_volume_varejo_sa"}), on="data", how="left")
    out = out[(out["data"] >= config.DATA_INICIO) & (out["data"] <= data_fim)].copy()
    out["fonte_ipca"] = fonte_ipca
    return out[["data", "pmc_indice_volume_varejo_sa", "ipca_variacao_mensal", "ipca_indice", "ipca_acumulado_12m", "fonte_ipca"]].reset_index(drop=True)


def indicadores_reais(pmc: dict[str, pd.DataFrame], ipca: pd.DataFrame, pac_internet: pd.DataFrame,
                      data_fim: pd.Timestamp, fonte_ipca: str) -> pd.DataFrame:
    """Indicadores oficiais citados no artigo, em formato longo (valores sob sigilo ficam NaN).

    Args:
        pmc: ``{"pmc_8880": ..., "pmc_8882": ...}``.
        ipca: IPCA mensal.
        pac_internet: tabela da PAC.
        data_fim: último mês.
        fonte_ipca: rótulo da fonte do IPCA.

    Returns:
        Tabela ``indicador, ano, segmento, valor, unidade, fonte``.
    """
    linhas: list[dict] = []

    def add(indicador: str, ano: int, segmento: str, valor: float, unidade: str, fonte: str) -> None:
        """Acrescenta uma linha ao formato longo."""
        linhas.append({"indicador": indicador, "ano": int(ano), "segmento": segmento, "valor": float(valor) if pd.notna(valor) else np.nan,
                       "unidade": unidade, "fonte": fonte})

    p80 = pmc["pmc_8880"].set_index("data")
    add("pmc_variacao_volume_sa_abr2020_vs_fev2020", 2020, "Total",
        (p80.at[pd.Timestamp("2020-04-01"), "vol_sa"] / p80.at[pd.Timestamp("2020-02-01"), "vol_sa"] - 1) * 100, "%", "IBGE PMC 8880")
    add(f"pmc_indice_volume_sa_{config.rotulo_mes_base(data_fim)}", data_fim.year, "Total",
        p80.at[data_fim, "vol_sa"], "índice 2022 = 100", "IBGE PMC 8880")
    p82 = pmc["pmc_8882"]
    for seg, cod in zip(config.SEGMENTOS, config.SEGMENTO_CODIGOS):
        sub = p82[p82["atividade_id"] == config.SEGMENTO_ATIVIDADE_PMC[cod]["id"]].set_index("data")
        add("pmc_variacao_volume_nsa_abr2020_vs_fev2020", 2020, seg,
            (sub.at[pd.Timestamp("2020-04-01"), "vol_nsa"] / sub.at[pd.Timestamp("2020-02-01"), "vol_nsa"] - 1) * 100, "%", "IBGE PMC 8882")

    ip = ipca[(ipca["data"] >= config.DATA_INICIO) & (ipca["data"] <= data_fim)].sort_values("data")
    fator = float(np.prod(1.0 + ip["ipca_variacao_mensal"].to_numpy(copy=True) / 100.0))
    rot = f"jan/2018–{config.rotulo_mes_base(data_fim)}"
    add(f"ipca_acumulado ({rot})", data_fim.year, "Total", (fator - 1) * 100, "%", fonte_ipca)
    add(f"ipca_fator_acumulado ({rot})", data_fim.year, "Total", fator, "fator", fonte_ipca)
    add("teto_mei_poder_compra_dez2017", data_fim.year, "Total", config.TETO_MEI / fator, "R$ de dez/2017", fonte_ipca)
    add("teto_mei_corrigido_pelo_ipca", data_fim.year, "Total", config.TETO_MEI * fator, f"R$ de {config.rotulo_mes_base(data_fim)}", fonte_ipca)
    macro = serie_macro_mensal(pmc["pmc_8880"], ipca, fonte_ipca, data_fim)
    dez = macro[macro["data"].dt.month == 12].dropna(subset=["ipca_acumulado_12m"])
    for _, r in dez.iterrows():
        add("ipca_acumulado_12m_dezembro", r["data"].year, "Total", r["ipca_acumulado_12m"], "%", fonte_ipca)
    pico = macro.loc[macro["ipca_acumulado_12m"].idxmax()]
    add(f"ipca_acumulado_12m_maximo ({config.rotulo_mes_base(pico['data'])})", pico["data"].year, "Total",
        pico["ipca_acumulado_12m"], "%", fonte_ipca)

    nomes_seg = dict(zip(config.SEGMENTO_CODIGOS, config.SEGMENTOS))
    for _, r in pac_internet.iterrows():
        fonte = f"IBGE PAC {r['serie']}"
        if r["papel"] == "total":
            add("pac_participacao_internet_varejo", r["ano"], "Total", r["participacao_internet"] * 100, "%", fonte)
            add("pac_receita_internet_varejo", r["ano"], "Total", r["receita_internet_mil_reais"], "mil R$", fonte)
            add("pac_empresas_vendendo_internet", r["ano"], "Total", r["empresas_internet"], "empresas", fonte)
        elif r["papel"] == "concentracao":
            add("pac_concentracao_internet_classe_nao_especializada", r["ano"], "Total",
                r["participacao_no_total_internet"] * 100, "%", fonte)
            add("pac_empresas_internet_classe_nao_especializada", r["ano"], "Total", r["empresas_internet"], "empresas", fonte)
        else:
            add("pac_participacao_internet_segmento", r["ano"], nomes_seg[r["papel"]],
                r["participacao_internet"] * 100 if pd.notna(r["participacao_internet"]) else np.nan, "%", fonte)
    tot = pac_internet[pac_internet["papel"] == "total"].set_index("ano")
    add("pac_multiplicador_receita_internet_2019_2024", 2024, "Total",
        tot.at[2024, "receita_internet_mil_reais"] / tot.at[2019, "receita_internet_mil_reais"], "vezes", "IBGE PAC 9349 e 10656")
    return pd.DataFrame(linhas)


def tabela_premissas() -> pd.DataFrame:
    """Tabela de premissas: uma linha por chave de ``config.PARAMETROS``.

    Returns:
        Tabela ``chave, valor, tipo, referencia, justificativa``.
    """
    linhas = []
    for chave, valor in config.PARAMETROS.items():
        origem = config.ORIGEM_PARAMETROS[chave]
        linhas.append({"chave": chave, "valor": json.dumps(valor, ensure_ascii=False), "tipo": origem.tipo,
                       "referencia": origem.referencia, "justificativa": origem.justificativa})
    return pd.DataFrame(linhas)


def _com_participacao(tabela: pd.DataFrame, df: pd.DataFrame, recorte: list[str]) -> pd.DataFrame:
    """Une a participação do canal (por recorte) a uma tabela agregada.

    Args:
        tabela: tabela agregada com ``canal`` e as colunas do recorte.
        df: base analítica.
        recorte: colunas do recorte.

    Returns:
        Tabela com ``participacao_canal``.
    """
    part = participacao_por_canal(df, recorte)
    return tabela.merge(part, on=recorte + ["canal"], how="left")


def construir_tabelas(base: pd.DataFrame, reais: dict) -> dict[str, pd.DataFrame]:
    """Constrói as 14 tabelas de apoio da seção 11.1 (as mesmas alimentam os gráficos).

    Args:
        base: base analítica (59 colunas).
        reais: dados reais limpos.

    Returns:
        Dicionário ``chave → tabela``.
    """
    data_fim = base["data"].max()
    atual = base["recorte_temporal"] == config.RECORTE_ATUAL
    t: dict[str, pd.DataFrame] = {}

    rc = agregar(base, ["recorte_temporal", "recorte_ordem", "canal"])
    t["kpis_recorte_canal"] = _com_participacao(rc, base, ["recorte_temporal", "recorte_ordem"])
    rcp = agregar(base, ["recorte_temporal", "recorte_ordem", "canal", "porte"])
    part = participacao_por_canal(base, ["recorte_temporal", "recorte_ordem", "porte"])
    t["kpis_recorte_canal_porte"] = rcp.merge(part, on=["recorte_temporal", "recorte_ordem", "porte", "canal"], how="left")
    t["kpis_atual_canal_porte_segmento"] = agregar(base[atual], ["canal", "porte", "segmento"])
    sm = agregar(base, ["data", "canal"])
    t["serie_mensal_canal"] = _com_participacao(sm, base, ["data"])

    comp = agregar(base[atual], ["porte", "canal"])
    linhas = []
    for _, r in comp.iterrows():
        for c in COMPONENTES_CUSTO:
            linhas.append({"porte": r["porte"], "canal": r["canal"], "componente": c, "pct_receita": r[c] / r["receita_bruta"]})
    t["composicao_custos_atual"] = pd.DataFrame(linhas)

    cvp = pd.concat([parametros_cvp(base, atual, ["porte"]), parametros_cvp(base, atual, ["porte", "segmento"])], ignore_index=True)
    t["cvp_parametros_atual"] = cvp
    t["receita_indiferenca_canais"] = receita_indiferenca(cvp)
    t["matriz_recomendacao"] = matriz_recomendacao(cvp)
    t["tarifas_marketplaces_2026"] = tabela_tarifas_marketplaces_2026()
    t["calibracao"] = tabela_calibracao(base, reais["pac_internet"], reais["pmc_8880"])
    t["indicadores_reais"] = indicadores_reais({"pmc_8880": reais["pmc_8880"], "pmc_8882": reais["pmc_8882"]},
                                               reais["ipca"], reais["pac_internet"], data_fim, reais["fonte_ipca"])
    t["premissas"] = tabela_premissas()
    t["serie_macro_mensal"] = serie_macro_mensal(reais["pmc_8880"], reais["ipca"], reais["fonte_ipca"], data_fim)
    t["pac_internet"] = reais["pac_internet"].copy()

    # Ordem das colunas conforme a seção 11.1
    cols_kpi = config.MEDIDAS_ADITIVAS + config.KPIS
    ordem = {
        "kpis_recorte_canal": ["recorte_temporal", "recorte_ordem", "canal"] + cols_kpi + ["participacao_canal"],
        "kpis_recorte_canal_porte": ["recorte_temporal", "recorte_ordem", "canal", "porte"] + cols_kpi + ["participacao_canal"],
        "kpis_atual_canal_porte_segmento": ["canal", "porte", "segmento"] + cols_kpi,
        "serie_mensal_canal": ["data", "canal"] + cols_kpi + ["participacao_canal"],
        "pac_internet": ["ano", "serie", "papel", "receita_total_mil_reais", "receita_internet_mil_reais",
                         "participacao_internet", "participacao_no_total_internet", "empresas_internet", "situacao"],
    }
    for chave, cols in ordem.items():
        t[chave] = t[chave][cols]
    t["kpis_recorte_canal_porte"] = config.ordenar_canonico(t["kpis_recorte_canal_porte"], ["recorte_ordem", "canal", "porte"])
    t["kpis_recorte_canal"] = config.ordenar_canonico(t["kpis_recorte_canal"], ["recorte_ordem", "canal"])
    logger.info("Tabelas de apoio construídas: %d", len(t))
    return t


# ---------------------------------------------------------------------------
# Exportação
# ---------------------------------------------------------------------------
COLUNAS_DUAS_CASAS: set[str] = set(config.COLUNAS_MOEDA_FINAL) | {
    "pmc_indice_volume_varejo_sa", "pmc_indice_volume_segmento", "pmc_indice_receita_segmento", "ipca_variacao_mensal",
    "F", "PE", "R_ref", "margem_1", "margem_2", "r_estrela", "valor_item", "receita_total_mil_reais", "receita_internet_mil_reais",
}


def _arredondar(df: pd.DataFrame) -> pd.DataFrame:
    """Arredonda: R$ e índices PMC a 2 casas; razões, KPIs e demais números a 6 casas.

    Args:
        df: tabela.

    Returns:
        Cópia arredondada (inteiros preservados).
    """
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].round(2 if c in COLUNAS_DUAS_CASAS else 6)
    return df


def _validar_contrato(df: pd.DataFrame) -> None:
    """Valida o contrato do CSV final: colunas, grão único e completo, nulos e faixas.

    Args:
        df: base analítica.

    Raises:
        ErroQualidadeDados: violação do contrato.
    """
    erros = []
    if list(df.columns) != config.COLUNAS_CSV_FINAL:
        erros.append("colunas fora do contrato")
    if df.duplicated(config.CHAVE_PAINEL).any():
        erros.append("grão duplicado")
    n_meses = df["data"].nunique()
    esperado = n_meses * len(config.CANAIS) * len(config.PORTES) * len(config.SEGMENTOS)
    if len(df) != esperado or len(pd.date_range(df["data"].min(), df["data"].max(), freq="MS")) != n_meses:
        erros.append(f"grade incompleta ({len(df)} linhas, esperado {esperado})")
    obrig = [c for c in config.COLUNAS_CSV_FINAL if c not in config.COLUNAS_ANULAVEIS]
    nulos = df[obrig].isna().sum()
    if nulos.any():
        erros.append(f"nulos em {nulos[nulos > 0].to_dict()}")
    anul = df[config.COLUNAS_ANULAVEIS].isna().any(axis=1)
    if (anul & (df["flag_pe_inviavel"] == 0)).any():
        erros.append("ponto de equilíbrio nulo sem flag_pe_inviavel = 1")
    if erros:
        raise ErroQualidadeDados("Portão de exportação: " + "; ".join(erros))
    validar_kpis(df, registrar=False)


def exportar_csv_final(df: pd.DataFrame, caminho: Path) -> Path:
    """Portão de exportação do CSV final (contrato da seção 12).

    Revalida o contrato, ordena, arredonda, grava em UTF-8 sem BOM (vírgula, ponto decimal, datas
    ISO, fim de linha ``\\n``) e relê o arquivo para conferir colunas, linhas e tipos.

    Args:
        df: base analítica.
        caminho: destino do CSV.

    Returns:
        Caminho gravado.

    Raises:
        ErroQualidadeDados: violação do contrato antes ou depois da gravação.
    """
    _validar_contrato(df)
    out = config.ordenar_canonico(df)[config.COLUNAS_CSV_FINAL]
    out = _arredondar(out)
    for c in config.COLUNAS_INTEIRAS:
        out[c] = out[c].astype(np.int64)
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(caminho, index=False, encoding="utf-8", sep=",", date_format="%Y-%m-%d", lineterminator="\n")
    relido = pd.read_csv(caminho, encoding="utf-8")
    problemas = []
    if list(relido.columns) != config.COLUNAS_CSV_FINAL:
        problemas.append("colunas relidas diferentes")
    if len(relido) != len(out):
        problemas.append("número de linhas relido diferente")
    for c in config.COLUNAS_INTEIRAS:
        if not pd.api.types.is_integer_dtype(relido[c]):
            problemas.append(f"{c} não é inteiro na releitura")
    for c in config.COLUNAS_MOEDA_FINAL + config.KPIS[:-1]:
        if not pd.api.types.is_numeric_dtype(relido[c]):
            problemas.append(f"{c} não é numérico na releitura")
    if problemas:
        raise ErroQualidadeDados("CSV final inválido na releitura: " + "; ".join(problemas))
    logger.info("CSV final exportado: %s (%d linhas × %d colunas)", config.caminho_relativo(caminho), len(out), out.shape[1])
    return caminho


def exportar_tabelas(tabelas: dict[str, pd.DataFrame]) -> list[Path]:
    """Grava as tabelas de apoio em ``outputs/tabelas`` (UTF-8 sem BOM, vírgula, ponto decimal).

    Args:
        tabelas: dicionário ``chave → tabela``.

    Returns:
        Caminhos gravados.
    """
    config.DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    caminhos = []
    for chave, tabela in tabelas.items():
        caminho = config.DIR_TABELAS / f"{chave}.csv"
        _arredondar(tabela).to_csv(caminho, index=False, encoding="utf-8", sep=",", date_format="%Y-%m-%d", lineterminator="\n")
        caminhos.append(caminho)
    logger.info("Tabelas de apoio exportadas: %d arquivos em %s", len(caminhos), config.caminho_relativo(config.DIR_TABELAS))
    return caminhos
