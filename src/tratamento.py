"""Tratamento: períodos, integração dos indicadores macro, medidas derivadas, KPIs e validações.

A função ``kpis_de_componentes`` é a única implementação dos KPIs do projeto. Ela recebe colunas
aditivas (de uma linha ou já somadas num agrupamento) e devolve os indicadores sempre como razão
de somas, nunca como média de razões.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src import ErroQualidadeDados
from src import config
from src.extracao import verificar_tetos_legais

logger = logging.getLogger(__name__)


def adicionar_periodos(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta as colunas de calendário, fase e recorte temporal (seção 5).

    Pré-pandemia = 2018-01 a 2020-02 (fev/2020 é a base pré-choque); Pandemia = 2020-03 a 2022-05;
    Pós-pandemia = 2022-06 em diante, com os recortes "Pós-pandemia (jun/2022–dez/2024)" e
    "Cenário Atual (2025–2026)".

    Args:
        df: tabela com a coluna ``data`` (1º dia do mês).

    Returns:
        Cópia com ``ano``, ``mes``, ``trimestre``, ``ano_mes``, ``fase``, ``fase_ordem``,
        ``recorte_temporal``, ``recorte_ordem`` e ``flag_cenario_atual``.
    """
    df = df.copy()
    d = pd.to_datetime(df["data"])
    df["ano"] = d.dt.year.astype(np.int64)
    df["mes"] = d.dt.month.astype(np.int64)
    df["trimestre"] = d.dt.quarter.astype(np.int64)
    df["ano_mes"] = d.dt.strftime("%Y-%m").astype(str)
    fase_ordem = np.where(d < config.INICIO_PANDEMIA, 1, np.where(d < config.INICIO_POS_PANDEMIA, 2, 3))
    recorte_ordem = np.where(fase_ordem < 3, fase_ordem, np.where(d <= config.FIM_POS_ATE_2024, 3, 4))
    df["fase"] = pd.Series(np.array(config.FASES, dtype=object)[fase_ordem - 1], index=df.index).astype(str)
    df["fase_ordem"] = fase_ordem.astype(np.int64)
    df["recorte_temporal"] = pd.Series(np.array(config.RECORTES, dtype=object)[recorte_ordem - 1], index=df.index).astype(str)
    df["recorte_ordem"] = recorte_ordem.astype(np.int64)
    df["flag_cenario_atual"] = (d >= config.INICIO_CENARIO_ATUAL).astype(np.int64)
    return df


def indice_ipca(ipca: pd.DataFrame) -> pd.DataFrame:
    """Calcula o índice encadeado do IPCA com base dez/2017 = 100.

    Args:
        ipca: ``data`` e ``ipca_variacao_mensal`` a partir de 2018-01.

    Returns:
        Cópia com a coluna ``ipca_indice``.
    """
    ipca = ipca.sort_values("data").reset_index(drop=True).copy()
    ipca["ipca_indice"] = 100.0 * np.cumprod(1.0 + ipca["ipca_variacao_mensal"].to_numpy(copy=True) / 100.0)
    return ipca


def integrar_macro(df: pd.DataFrame, pmc: dict[str, pd.DataFrame], ipca: pd.DataFrame, fonte_ipca: str) -> pd.DataFrame:
    """Une os indicadores oficiais (PMC e IPCA) ao painel e define o deflator.

    O deflator é P(t) ÷ P(data_fim): os valores reais ficam em "R$ do mês de data_fim".

    Args:
        df: painel com ``data`` e ``segmento``.
        pmc: ``{"pmc_8880": ..., "pmc_8882": ...}`` no formato largo.
        ipca: IPCA mensal.
        fonte_ipca: rótulo da fonte do IPCA.

    Returns:
        Painel com as colunas macro e ``atividade_pmc_referencia``.

    Raises:
        ErroQualidadeDados: ausente após a junção.
    """
    data_fim = df["data"].max()
    p80 = pmc["pmc_8880"][["data", "vol_sa"]].rename(columns={"vol_sa": "pmc_indice_volume_varejo_sa"})
    p82 = pmc["pmc_8882"][["data", "atividade_id", "atividade_nome", "vol_nsa", "nom_nsa"]].rename(
        columns={"vol_nsa": "pmc_indice_volume_segmento", "nom_nsa": "pmc_indice_receita_segmento",
                 "atividade_nome": "atividade_pmc_referencia"})
    ip = indice_ipca(ipca)
    base_fim = ip.loc[ip["data"] == data_fim, "ipca_indice"]
    if base_fim.empty:
        raise ErroQualidadeDados(f"IPCA sem o mês-base {data_fim:%Y-%m}")
    ip["deflator_ipca"] = ip["ipca_indice"] / float(base_fim.iloc[0])
    out = df.copy()
    out["atividade_id"] = out["segmento"].map(lambda s: config.SEGMENTO_ATIVIDADE_PMC[config.SEGMENTO_PARA_CODIGO[s]]["id"])
    out = out.merge(p80, on="data", how="left").merge(p82, on=["data", "atividade_id"], how="left")
    out = out.merge(ip[["data", "ipca_variacao_mensal", "ipca_indice", "deflator_ipca"]], on="data", how="left")
    out["fonte_ipca"] = fonte_ipca
    out = out.drop(columns=["atividade_id"])
    cols = config.COLUNAS_MACRO + ["atividade_pmc_referencia"]
    if out[cols].isna().any().any():
        raise ErroQualidadeDados(f"Indicadores macro ausentes após a junção: {out[cols].isna().sum()[lambda s: s > 0].to_dict()}")
    out["atividade_pmc_referencia"] = out["atividade_pmc_referencia"].astype(str)
    return out


def calcular_medidas_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula impostos, margens e valores reais (seção 10, passo 3).

    Args:
        df: painel com as medidas base e ``deflator_ipca``.

    Returns:
        Cópia com ``impostos``, ``margem_contribuicao``, ``margem_liquida``, ``receita_bruta_real`` e
        ``margem_liquida_real`` (R$ a 2 casas).
    """
    df = df.copy()
    df["impostos"] = np.round(df["impostos_fixos"] + df["impostos_variaveis"], 2)
    df["margem_contribuicao"] = np.round(
        df["receita_bruta"] - df["cmv"] - df["comissoes_tarifas"] - df["frete_subsidiado"] - df["impostos_variaveis"], 2)
    df["margem_liquida"] = np.round(
        df["receita_bruta"] - df["cmv"] - df["comissoes_tarifas"] - df["frete_subsidiado"]
        - df["investimento_marketing"] - df["custos_fixos"] - df["impostos"], 2)
    df["receita_bruta_real"] = np.round(df["receita_bruta"] / df["deflator_ipca"], 2)
    df["margem_liquida_real"] = np.round(df["margem_liquida"] / df["deflator_ipca"], 2)
    return df


def _dividir(num: pd.Series | np.ndarray, den: pd.Series | np.ndarray) -> np.ndarray:
    """Divisão vetorial que devolve NaN quando o denominador é ≤ 0.

    Args:
        num: numerador.
        den: denominador.

    Returns:
        Vetor com a razão.
    """
    num = np.asarray(num, dtype=float)
    den = np.asarray(den, dtype=float)
    saida = np.full(num.shape, np.nan)
    ok = den > 0
    saida[ok] = num[ok] / den[ok]
    return saida


def kpis_de_componentes(somas: pd.DataFrame) -> pd.DataFrame:
    """Calcula os KPIs a partir de colunas aditivas (implementação única, razão de somas).

    Args:
        somas: colunas de ``MEDIDAS_ADITIVAS`` (de uma linha ou somadas num agrupamento).

    Returns:
        DataFrame com as colunas de ``config.KPIS``, no mesmo índice.
    """
    s = somas
    k = pd.DataFrame(index=s.index)
    k["ticket_medio"] = _dividir(s["receita_bruta"], s["pedidos"])
    k["ticket_medio_real"] = _dividir(s["receita_bruta_real"], s["pedidos"])
    k["frequencia_compra"] = _dividir(s["pedidos"], s["clientes_ativos"])
    k["cac"] = _dividir(s["investimento_marketing"], s["clientes_novos"])
    k["take_rate"] = _dividir(s["comissoes_tarifas"], s["receita_bruta"])
    k["margem_contribuicao_pct"] = _dividir(s["margem_contribuicao"], s["receita_bruta"])
    k["margem_liquida_pct"] = _dividir(s["margem_liquida"], s["receita_bruta"])
    k["taxa_retencao"] = _dividir(s["clientes_recorrentes"], s["clientes_ativos_mes_anterior"])
    k["tempo_vida_meses"] = _dividir(np.ones(len(s)), 1.0 - k["taxa_retencao"].to_numpy())
    receita_por_cliente = _dividir(s["receita_bruta"], s["clientes_ativos"])
    k["ltv"] = receita_por_cliente * k["margem_contribuicao_pct"].to_numpy() * k["tempo_vida_meses"].to_numpy()
    k["ltv_cac"] = _dividir(k["ltv"], k["cac"])
    k["payback_cac_meses"] = _dividir(k["cac"], _dividir(s["margem_contribuicao"], s["clientes_ativos"]))
    k["receita_por_negocio"] = _dividir(s["receita_bruta"], s["negocios_ativos"])
    fixos_por_negocio = _dividir(s["custos_fixos"] + s["impostos_fixos"], s["negocios_ativos"])
    margem_apos_marketing = _dividir(s["margem_contribuicao"] - s["investimento_marketing"], s["receita_bruta"])
    k["ponto_equilibrio_receita"] = _dividir(fixos_por_negocio, margem_apos_marketing)
    k["folga_ponto_equilibrio_pct"] = k["receita_por_negocio"] / k["ponto_equilibrio_receita"] - 1.0
    k["flag_pe_inviavel"] = (~(np.nan_to_num(margem_apos_marketing, nan=-1.0) > 0)).astype(np.int64)
    return k[config.KPIS]


def validar_kpis(df: pd.DataFrame, registrar: bool = True) -> None:
    """Valida as faixas de sanidade dos KPIs linha a linha e os tetos legais (seção 10.3).

    Registra em INFO as 5 menores margens líquidas e a menor margem de contribuição.

    Args:
        df: base analítica com KPIs.
        registrar: se ``False``, não repete os registros informativos (uso no portão de exportação).

    Raises:
        ErroQualidadeDados: KPI fora da faixa ou teto legal violado.
    """
    problemas = []
    for kpi, (minimo, maximo, inc_min, inc_max) in config.FAIXAS_KPI.items():
        x = df[kpi]
        ok_min = x >= minimo if inc_min else x > minimo
        ok_max = x <= maximo if inc_max else x < maximo
        ruins = df[~(ok_min & ok_max) | x.isna()]
        if len(ruins):
            exemplos = ruins[["data", "canal", "porte", "segmento", kpi]].head(5).to_dict("records")
            problemas.append(f"{kpi}: {len(ruins)} linhas fora de ({minimo}, {maximo}); ex.: {exemplos}")
    pe = df["ponto_equilibrio_receita"]
    pe_ruim = ~(((pe > 0) & (df["flag_pe_inviavel"] == 0)) | (pe.isna() & (df["flag_pe_inviavel"] == 1)))
    if pe_ruim.any():
        problemas.append(f"ponto_equilibrio_receita inconsistente em {int(pe_ruim.sum())} linhas")
    if problemas:
        raise ErroQualidadeDados("Faixas de KPI violadas: " + " | ".join(problemas))
    verificar_tetos_legais(df)
    if not registrar:
        return
    menores = df.nsmallest(5, "margem_liquida_pct")
    for _, r in menores.iterrows():
        logger.info("Menor margem líquida: %s | %s | %s | %s | %.4f",
                    r["data"].strftime("%Y-%m"), r["canal"], r["porte"], r["segmento"], r["margem_liquida_pct"])
    r = df.loc[df["margem_contribuicao_pct"].idxmin()]
    logger.info("Menor margem de contribuição: %s | %s | %s | %s | %.4f",
                r["data"].strftime("%Y-%m"), r["canal"], r["porte"], r["segmento"], r["margem_contribuicao_pct"])
    logger.info("KPIs validados em %d linhas (faixas da seção 10.3 e tetos legais)", len(df))


def preparar_base_analitica(painel: pd.DataFrame, reais: dict, data_fim: pd.Timestamp) -> pd.DataFrame:
    """Executa o tratamento completo e devolve a base no layout das 59 colunas do contrato.

    Args:
        painel: painel limpo.
        reais: dados reais limpos (``pmc_8880``, ``pmc_8882``, ``ipca``, ``fonte_ipca``).
        data_fim: último mês da série.

    Returns:
        Base analítica ordenada na ordem canônica.

    Raises:
        ErroQualidadeDados: violação de cobertura, faixas ou tetos.
    """
    base = painel[painel["data"] <= data_fim].copy()
    base = adicionar_periodos(base)
    base["canal_codigo"] = base["canal"].map(config.CANAL_PARA_CODIGO).astype(str)
    base["segmento_codigo"] = base["segmento"].map(config.SEGMENTO_PARA_CODIGO).astype(str)
    base = integrar_macro(base, {"pmc_8880": reais["pmc_8880"], "pmc_8882": reais["pmc_8882"]},
                          reais["ipca"], reais["fonte_ipca"])
    base = calcular_medidas_derivadas(base)
    kpis = kpis_de_componentes(base)
    base = pd.concat([base.drop(columns=[c for c in config.KPIS if c in base.columns]), kpis], axis=1)
    validar_kpis(base)
    base = config.ordenar_canonico(base)[config.COLUNAS_CSV_FINAL]
    logger.info("Base analítica: %d linhas × %d colunas (R$ reais de %s)", len(base), base.shape[1],
                config.rotulo_mes_base(data_fim))
    return base
