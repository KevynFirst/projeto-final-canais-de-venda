"""Limpeza dos dados reais (SIDRA/BCB) e do painel bruto simulado, com relatório de qualidade.

Dados reais: mapeamento das colunas do SIDRA pelos rótulos do cabeçalho, conversão dos sinais
convencionais do IBGE ("-" = zero; "X", ".." e "..." = ausente), datas, cobertura, escolha da
fonte do IPCA e soma estrita da PAC por forma de comercialização.

Painel bruto: cabeçalhos, duplicatas exatas, rótulos, datas em formatos mistos, números em
formato brasileiro, duplicatas por chave, imputação por razão (preservando a coerência da linha),
tipos, validação de invariantes e conferência com o gabarito da injeção.
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

from src import ErroQualidadeDados
from src import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Utilitários de texto, datas e números
# ---------------------------------------------------------------------------
def normalizar_texto(s: str) -> str:
    """Normaliza um rótulo: sem acentos, minúsculas, "&" → "e", hífens e espaços colapsados.

    Args:
        s: texto original.

    Returns:
        Texto normalizado.
    """
    t = unicodedata.normalize("NFKD", str(s))
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.lower().replace("&", " e ").replace("-", " ")
    return re.sub(r"\s+", " ", t).strip()


_RE_AAAA_MM = re.compile(r"^\d{4}-\d{2}$")
_RE_MM_AAAA = re.compile(r"^\d{2}/\d{4}$")
_RE_AAAA_MM_DD = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_mes_referencia(s: str) -> pd.Timestamp:
    """Converte um mês de referência em um dos 3 formatos aceitos para o 1º dia do mês.

    Formatos: ``AAAA-MM``, ``MM/AAAA`` e ``AAAA-MM-01`` (dia obrigatoriamente 01).

    Args:
        s: texto da data.

    Returns:
        Timestamp do 1º dia do mês.

    Raises:
        ValueError: formato fora dos três aceitos ou mês inválido.
    """
    t = str(s).strip()
    if _RE_AAAA_MM.match(t):
        return pd.Timestamp(pd.to_datetime(t, format="%Y-%m"))
    if _RE_MM_AAAA.match(t):
        return pd.Timestamp(pd.to_datetime(t, format="%m/%Y"))
    if _RE_AAAA_MM_DD.match(t):
        d = pd.Timestamp(pd.to_datetime(t, format="%Y-%m-%d"))
        if d.day != 1:
            raise ValueError(f"Mês de referência com dia diferente de 01: {s!r}")
        return d
    raise ValueError(f"Formato de mês de referência não reconhecido: {s!r}")


def _formato_data(s: str) -> str:
    """Identifica o formato textual de uma data do bruto.

    Args:
        s: texto da data.

    Returns:
        Rótulo do formato ou ``"outro"``.
    """
    t = str(s).strip()
    if _RE_AAAA_MM.match(t):
        return "AAAA-MM"
    if _RE_MM_AAAA.match(t):
        return "MM/AAAA"
    if _RE_AAAA_MM_DD.match(t):
        return "AAAA-MM-01"
    return "outro"


def parse_numero_br(s: str) -> float:
    """Converte números monetários em texto (``1.234,56``, ``R$ 1.234,56`` ou ``1234.56``).

    Args:
        s: texto do número.

    Returns:
        Valor numérico.

    Raises:
        ValueError: texto não numérico.
    """
    t = str(s).replace("R$", "").replace("\u00a0", "").replace(" ", "").strip()
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    return float(t)


def parse_inteiro(s: str) -> int:
    """Converte contagens em texto (``1.234`` ou ``1234``) para inteiro.

    Args:
        s: texto da contagem.

    Returns:
        Valor inteiro.

    Raises:
        ValueError: texto não numérico.
    """
    t = str(s).strip().replace(".", "")
    if not re.fullmatch(r"-?\d+", t):
        raise ValueError(f"Contagem não numérica: {s!r}")
    return int(t)


# ---------------------------------------------------------------------------
# Dados reais
# ---------------------------------------------------------------------------
def normalizar_sidra(dados: list[dict]) -> pd.DataFrame:
    """Normaliza uma resposta do SIDRA em tabela com colunas nomeadas pelo cabeçalho.

    Os sinais convencionais do IBGE são convertidos: "-" → 0; "X", ".." e "..." → NaN. As
    contagens por símbolo e as duplicatas removidas ficam em ``df.attrs``.

    Args:
        dados: lista JSON do SIDRA (1º elemento = cabeçalho).

    Returns:
        Tabela com ``periodo``, ``data`` ou ``ano``, ids, nomes, ``valor`` e ``simbolo``.

    Raises:
        ErroQualidadeDados: valor de texto que não é número nem sinal convencional.
    """
    cabecalho = dados[0]
    renomear: dict[str, str] = {}
    for chave, rotulo in cabecalho.items():
        if chave.startswith("D") and chave.endswith("C") and rotulo in config.MAPA_CABECALHO_SIDRA:
            nome = config.MAPA_CABECALHO_SIDRA[rotulo]
            renomear[chave] = nome
            renomear[chave[:-1] + "N"] = nome.replace("_id", "") + "_nome" if nome != "periodo" else "periodo_nome"
    df = pd.DataFrame(dados[1:])
    df = df[[c for c in list(renomear) + ["V"] if c in df.columns]].rename(columns=renomear)
    texto = df["V"].astype(str).str.strip()
    simbolos = {"-": int((texto == "-").sum()), "X": int((texto == "X").sum()),
                "..": int((texto == "..").sum()), "...": int((texto == "...").sum())}
    convertido = texto.where(~texto.isin(config.SIMBOLOS_ZERO_SIDRA), "0")
    convertido = convertido.where(~convertido.isin(config.SIMBOLOS_NAN_SIDRA), None)
    valor = pd.to_numeric(convertido, errors="coerce")
    invalidos = texto[valor.isna() & ~texto.isin(config.SIMBOLOS_NAN_SIDRA)]
    if len(invalidos):
        raise ErroQualidadeDados(f"SIDRA com {len(invalidos)} valores não numéricos (ex.: {invalidos.unique()[:5].tolist()})")
    df["valor"] = valor.astype(float)
    df["simbolo"] = texto.where(texto.isin(config.SIMBOLOS_NAN_SIDRA | config.SIMBOLOS_ZERO_SIDRA), "")
    df = df.drop(columns=["V"])
    for col in ("variavel_id", "tipo_indice_id", "atividade_id", "forma_id", "classe_id"):
        if col in df.columns:
            df[col] = df[col].astype(int)
    periodo = df["periodo"].astype(str)
    if periodo.str.len().eq(6).all():
        df["data"] = pd.to_datetime(periodo, format="%Y%m")
    else:
        df["ano"] = periodo.astype(int)
    antes = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    df.attrs["simbolos"] = simbolos
    df.attrs["duplicatas_removidas"] = int(antes - len(df))
    df.attrs["linhas"] = int(len(df))
    return df


def _verificar_meses_contiguos(datas: pd.Series, rotulo: str) -> dict:
    """Confere se uma série mensal não tem lacunas entre o primeiro e o último mês.

    Args:
        datas: datas da série.
        rotulo: nome da série para mensagens.

    Returns:
        Cobertura (``inicio``, ``fim``, ``meses``).

    Raises:
        ErroQualidadeDados: mês faltando no intervalo.
    """
    unicas = pd.DatetimeIndex(sorted(pd.Series(datas).unique()))
    esperado = pd.date_range(unicas.min(), unicas.max(), freq="MS")
    faltando = esperado.difference(unicas)
    if len(faltando):
        raise ErroQualidadeDados(f"{rotulo}: {len(faltando)} meses sem dado (ex.: {faltando[0]:%Y-%m})")
    return {"inicio": unicas.min().strftime("%Y-%m"), "fim": unicas.max().strftime("%Y-%m"), "meses": int(len(unicas))}


def _pmc_largo(df: pd.DataFrame, chaves: list[str]) -> pd.DataFrame:
    """Converte a PMC normalizada para o formato largo (vol/nom × com/sem ajuste).

    Args:
        df: PMC normalizada.
        chaves: colunas de identificação (``data`` e, na 8882, ``atividade_id``).

    Returns:
        Tabela com ``vol_nsa``, ``vol_sa``, ``nom_nsa`` e ``nom_sa``.
    """
    nomes = {
        (config.PMC_VAR_NSA, config.PMC_TIPO_VOLUME): "vol_nsa",
        (config.PMC_VAR_SA, config.PMC_TIPO_VOLUME): "vol_sa",
        (config.PMC_VAR_NSA, config.PMC_TIPO_RECEITA): "nom_nsa",
        (config.PMC_VAR_SA, config.PMC_TIPO_RECEITA): "nom_sa",
    }
    df = df.assign(medida=[nomes.get((v, t), "outro") for v, t in zip(df["variavel_id"], df["tipo_indice_id"])])
    largo = df.pivot_table(index=chaves, columns="medida", values="valor", aggfunc="first").reset_index()
    largo.columns.name = None
    return largo


def limpar_pmc(df8880: pd.DataFrame, df8882: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Limpa a PMC Brasil (8880) e por atividade (8882) e confere a cobertura mensal.

    Args:
        df8880: PMC 8880 normalizada.
        df8882: PMC 8882 normalizada.

    Returns:
        ``(pmc_8880, pmc_8882)`` em formato largo; a 8882 traz também ``atividade_nome``.

    Raises:
        ErroQualidadeDados: lacuna em alguma série.
    """
    p80 = _pmc_largo(df8880, ["data"]).sort_values("data").reset_index(drop=True)
    _verificar_meses_contiguos(p80.loc[p80["vol_sa"].notna(), "data"], "PMC 8880")
    nomes = df8882.drop_duplicates("atividade_id").set_index("atividade_id")["atividade_nome"]
    p82 = _pmc_largo(df8882, ["data", "atividade_id"]).sort_values(["atividade_id", "data"]).reset_index(drop=True)
    p82["atividade_nome"] = p82["atividade_id"].map(nomes).astype(str)
    for atividade, grupo in p82.groupby("atividade_id"):
        validos = grupo.dropna(subset=["vol_nsa", "vol_sa", "nom_nsa"])
        _verificar_meses_contiguos(validos["data"], f"PMC 8882 atividade {atividade}")
    return p80, p82


def limpar_ipca(df_bcb: pd.DataFrame | None, df_sidra: pd.DataFrame | None) -> tuple[pd.DataFrame, str]:
    """Escolhe e limpa a série do IPCA (BCB 433 como primária; SIDRA 1737 como conferência e fallback).

    Regras (seção 6.4): as duas disponíveis e iguais (≤ 0,005 p.p.) → BCB conferida; divergentes →
    SIDRA 1737 com WARNING; só uma disponível → essa.

    Args:
        df_bcb: série do BCB (``data``, ``valor`` em texto) ou ``None``.
        df_sidra: série do SIDRA normalizada ou ``None``.

    Returns:
        ``(tabela com data e ipca_variacao_mensal, rótulo fonte_ipca)``.

    Raises:
        ErroQualidadeDados: nenhuma fonte disponível ou lacuna na série.
    """
    sidra = None
    if df_sidra is not None:
        sidra = df_sidra[["data", "valor"]].rename(columns={"valor": "ipca_variacao_mensal"}).sort_values("data")
    bcb = None
    if df_bcb is not None:
        bcb = pd.DataFrame({
            "data": pd.to_datetime(df_bcb["data"], format="%d/%m/%Y"),
            "ipca_variacao_mensal": pd.to_numeric(df_bcb["valor"], errors="raise").astype(float),
        }).sort_values("data")
    if bcb is not None and sidra is not None:
        comum = bcb.merge(sidra, on="data", suffixes=("_bcb", "_sidra"))
        dif = float((comum["ipca_variacao_mensal_bcb"] - comum["ipca_variacao_mensal_sidra"]).abs().max())
        if dif <= config.TOLERANCIA_IPCA_PP:
            escolhido, fonte = bcb, config.ROTULO_IPCA_BCB_CONFERIDO
            logger.info("IPCA: BCB 433 e SIDRA 1737 conferem (diferença máxima %.4f p.p.)", dif)
        else:
            escolhido, fonte = sidra, config.ROTULO_IPCA_SIDRA
            logger.warning("IPCA: BCB 433 e SIDRA 1737 divergem (%.4f p.p.); usando SIDRA 1737 (produtor oficial)", dif)
    elif bcb is not None:
        escolhido, fonte = bcb, config.ROTULO_IPCA_BCB
        logger.info("IPCA: apenas BCB 433 disponível")
    elif sidra is not None:
        escolhido, fonte = sidra, config.ROTULO_IPCA_SIDRA
        logger.warning("IPCA: BCB/SGS 433 indisponível; fallback para IBGE/SIDRA 1737")
    else:
        raise ErroQualidadeDados("Nenhuma série de IPCA disponível")
    escolhido = escolhido[escolhido["data"] >= config.DATA_INICIO].drop_duplicates("data").reset_index(drop=True)
    _verificar_meses_contiguos(escolhido["data"], "IPCA")
    if escolhido["data"].min() != config.DATA_INICIO:
        raise ErroQualidadeDados("IPCA não começa em 2018-01")
    return escolhido, fonte


def limpar_pac(df9349: pd.DataFrame, df10656: pd.DataFrame) -> pd.DataFrame:
    """Calcula a participação da Internet na receita do varejo (PAC) com soma estrita.

    Qualquer parcela ausente ("X", ".." ou "...") torna a soma NaN; nunca há soma parcial.

    Args:
        df9349: PAC 9349 normalizada (2019–2023).
        df10656: PAC 10656 normalizada (2024, série nova).

    Returns:
        Tabela ``pac_internet`` (seção 11.1).
    """
    linhas = []
    for fonte_id, df in (("pac_9349", df9349), ("pac_10656", df10656)):
        papeis = config.PAC_PAPEIS[fonte_id]
        for ano in sorted(df["ano"].unique()):
            dano = df[df["ano"] == ano]
            receita = dano[dano["variavel_id"] == config.PAC_VAR_RECEITA]
            empresas = dano[dano["variavel_id"] == config.PAC_VAR_EMPRESAS]
            internet_total = None
            registros = {}
            for papel in config.PAC_ORDEM_PAPEIS:
                classes = papeis[papel]
                r_todas = receita[receita["classe_id"].isin(classes) & receita["forma_id"].isin(config.PAC_FORMAS)]
                r_net = receita[receita["classe_id"].isin(classes) & (receita["forma_id"] == config.PAC_FORMA_INTERNET)]
                e_net = empresas[empresas["classe_id"].isin(classes) & (empresas["forma_id"] == config.PAC_FORMA_INTERNET)]
                total = r_todas["valor"].sum(min_count=len(classes) * len(config.PAC_FORMAS))
                if len(r_todas) < len(classes) * len(config.PAC_FORMAS):
                    total = np.nan
                net = r_net["valor"].sum(min_count=len(classes))
                if len(r_net) < len(classes):
                    net = np.nan
                emp = e_net["valor"].sum(min_count=len(classes))
                sigilo = bool((r_todas["simbolo"] == "X").any() or (r_net["simbolo"] == "X").any())
                registros[papel] = (total, net, emp, sigilo)
                if papel == "total":
                    internet_total = net
            for papel in config.PAC_ORDEM_PAPEIS:
                total, net, emp, sigilo = registros[papel]
                part = net / total if pd.notna(total) and pd.notna(net) and total > 0 else np.nan
                part_total = net / internet_total if pd.notna(net) and pd.notna(internet_total) and internet_total > 0 else np.nan
                if pd.notna(part):
                    situacao = "ok"
                else:
                    situacao = "sigilo" if sigilo else "indisponivel"
                linhas.append({
                    "ano": int(ano), "serie": config.PAC_SERIES[fonte_id], "papel": papel,
                    "receita_total_mil_reais": total, "receita_internet_mil_reais": net,
                    "participacao_internet": part, "participacao_no_total_internet": part_total,
                    "empresas_internet": emp, "situacao": situacao,
                })
    pac = pd.DataFrame(linhas)
    pac["empresas_internet"] = pac["empresas_internet"].round().astype("Int64")
    return pac


def limpar_dados_reais(brutos: dict[str, tuple[object, dict]]) -> tuple[dict, dict]:
    """Limpa todas as fontes reais e monta a seção ``dados_reais`` do relatório de qualidade.

    Args:
        brutos: saída de ``extracao.obter_dados_reais``.

    Returns:
        ``(reais, relatorio)``; ``reais`` contém ``pmc_8880``, ``pmc_8882``, ``ipca``, ``fonte_ipca``,
        ``pac_internet``, ``snapshots`` e ``metas``.
    """
    relatorio: dict = {}
    normalizados: dict[str, pd.DataFrame] = {}
    for fonte_id, (dados, meta) in brutos.items():
        if fonte_id == "ipca_bcb_433":
            df = pd.DataFrame(dados)
            antes = len(df)
            df = df.drop_duplicates().reset_index(drop=True)
            relatorio[fonte_id] = {"linhas": int(len(df)), "valores_nao_numericos": {}, "duplicatas_removidas": int(antes - len(df))}
        else:
            df = normalizar_sidra(dados)  # type: ignore[arg-type]
            relatorio[fonte_id] = {
                "linhas": df.attrs["linhas"],
                "valores_nao_numericos": df.attrs["simbolos"],
                "duplicatas_removidas": df.attrs["duplicatas_removidas"],
            }
            logger.info("%s: %d linhas; sinais convencionais %s; duplicatas removidas %d",
                        fonte_id, df.attrs["linhas"], df.attrs["simbolos"], df.attrs["duplicatas_removidas"])
        relatorio[fonte_id]["snapshot"] = meta.get("arquivo_dados", "")
        relatorio[fonte_id]["obtido_em"] = meta.get("obtido_em", "")
        normalizados[fonte_id] = df

    pmc_8880, pmc_8882 = limpar_pmc(normalizados["pmc_8880"], normalizados["pmc_8882"])
    relatorio["pmc_8880"]["cobertura"] = _verificar_meses_contiguos(pmc_8880["data"], "PMC 8880")
    relatorio["pmc_8882"]["cobertura"] = _verificar_meses_contiguos(pmc_8882["data"], "PMC 8882")
    ipca, fonte_ipca = limpar_ipca(normalizados.get("ipca_bcb_433"), normalizados.get("ipca_sidra_1737"))
    cobertura_ipca = _verificar_meses_contiguos(ipca["data"], "IPCA")
    if "ipca_sidra_1737" in normalizados:
        relatorio["ipca_sidra_1737"]["cobertura"] = _verificar_meses_contiguos(normalizados["ipca_sidra_1737"]["data"], "IPCA SIDRA 1737")
    if "ipca_bcb_433" in normalizados:
        datas_bcb = pd.to_datetime(normalizados["ipca_bcb_433"]["data"], format="%d/%m/%Y")
        relatorio["ipca_bcb_433"]["cobertura"] = _verificar_meses_contiguos(datas_bcb, "IPCA BCB 433")
    relatorio["ipca_escolhido"] = {"fonte_ipca": fonte_ipca, "cobertura": cobertura_ipca,
                                   "bcb_433_disponivel": "ipca_bcb_433" in brutos}
    pac = limpar_pac(normalizados["pac_9349"], normalizados["pac_10656"])
    relatorio["pac_internet"] = {
        "linhas": int(len(pac)), "situacao": pac["situacao"].value_counts().to_dict(),
        "anos": sorted(int(a) for a in pac["ano"].unique()),
    }
    snapshots = sorted(meta.get("arquivo_dados", "") for _, meta in brutos.values())
    reais = {
        "pmc_8880": pmc_8880, "pmc_8882": pmc_8882, "ipca": ipca, "fonte_ipca": fonte_ipca,
        "pac_internet": pac, "snapshots": snapshots, "metas": {k: m for k, (_, m) in brutos.items()},
    }
    logger.info("Dados reais limpos: PMC até %s; IPCA (%s) até %s; PAC %s",
                pmc_8880["data"].max().strftime("%Y-%m"), fonte_ipca, ipca["data"].max().strftime("%Y-%m"),
                relatorio["pac_internet"]["anos"])
    return reais, relatorio


# ---------------------------------------------------------------------------
# Painel bruto simulado
# ---------------------------------------------------------------------------
def _interp_serie(x: pd.Series, grupos: pd.Series) -> pd.Series:
    """Interpola linearmente dentro de cada série (nas duas direções).

    Args:
        x: valores (NaN onde ausente).
        grupos: identificador da série de cada linha.

    Returns:
        Série interpolada.
    """
    return x.groupby(grupos, sort=False).transform(lambda v: v.interpolate(method="linear", limit_direction="both"))


def imputar_ausentes(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Imputa células ausentes por razão estável, preservando a coerência da linha (seção 9.2).

    Cada ausente é reconstruído com valores presentes na própria linha × uma razão interpolada dos
    meses vizinhos da mesma série (canal × porte × segmento). As razões são calculadas uma única
    vez, sobre os valores originais. Clientes usam a identidade ativos = novos + recorrentes; a
    defasagem é recalculada; o DAS do MEI segue a regra legal.

    Args:
        df: painel com ``data``, dimensões e as 14 medidas (NaN onde ausente).

    Returns:
        ``(painel imputado, relatório)``; o painel ganha ``qtd_campos_imputados``.

    Raises:
        ValueError: defasagem ausente no primeiro mês.
    """
    df = config.ordenar_canonico(df, ["canal", "porte", "segmento", "data"])
    medidas = config.COLUNAS_MEDIDA_BRUTAS
    ausente = df[medidas].isna()
    df["qtd_campos_imputados"] = ausente.sum(axis=1).astype(np.int64)
    grupos = df["canal"] + "|" + df["porte"] + "|" + df["segmento"]
    orig = df[medidas].astype(float)

    def razao(num: str, den: str) -> pd.Series:
        """Razão num ÷ den nos valores originais, interpolada dentro da série."""
        r = (orig[num] / orig[den]).where(orig[num].notna() & orig[den].notna())
        return _interp_serie(r, grupos)

    r_cmv = razao("cmv", "receita_bruta")
    r_freq = razao("pedidos", "clientes_ativos")
    r_rec = {c: razao(c, "receita_bruta") for c in ("cmv", "comissoes_tarifas", "frete_subsidiado", "impostos_variaveis")}
    r_cac = razao("investimento_marketing", "clientes_novos")
    r_cf = razao("custos_fixos", "negocios_ativos")
    metodos: dict[str, int] = {}
    por_coluna: dict[str, int] = {m: int(ausente[m].sum()) for m in medidas}
    imputadas: list[tuple[str, str, str, str, str]] = []
    mei = df["porte"] == "MEI"

    def registrar(mascara: pd.Series, coluna: str, metodo: str) -> None:
        """Conta as imputações por método e guarda as células imputadas."""
        k = int(mascara.sum())
        if k:
            metodos[metodo] = metodos.get(metodo, 0) + k
            for _, linha in df.loc[mascara, ["data", "canal", "porte", "segmento"]].iterrows():
                imputadas.append((linha["data"].strftime("%Y-%m-01"), linha["canal"], linha["porte"], linha["segmento"], coluna))

    # Identidade de clientes (exata)
    m = ausente["clientes_ativos"]
    df.loc[m, "clientes_ativos"] = df.loc[m, "clientes_novos"] + df.loc[m, "clientes_recorrentes"]
    registrar(m, "clientes_ativos", "identidade_clientes")
    m = ausente["clientes_novos"]
    df.loc[m, "clientes_novos"] = df.loc[m, "clientes_ativos"] - df.loc[m, "clientes_recorrentes"]
    registrar(m, "clientes_novos", "identidade_clientes")
    m = ausente["clientes_recorrentes"]
    df.loc[m, "clientes_recorrentes"] = df.loc[m, "clientes_ativos"] - df.loc[m, "clientes_novos"]
    registrar(m, "clientes_recorrentes", "identidade_clientes")

    # Defasagem: clientes ativos do mês anterior (exata, recalculada)
    primeiro = df["data"] == df["data"].min()
    if (ausente["clientes_ativos_mes_anterior"] & primeiro).any():
        raise ValueError("clientes_ativos_mes_anterior ausente no primeiro mês: impossível reconstruir a defasagem")
    defasado = df.groupby(grupos, sort=False)["clientes_ativos"].shift(1)
    recalc = (~primeiro)
    divergencias = int(((df["clientes_ativos_mes_anterior"] != defasado) & recalc & ~ausente["clientes_ativos_mes_anterior"]).sum())
    df.loc[recalc, "clientes_ativos_mes_anterior"] = defasado[recalc]
    registrar(ausente["clientes_ativos_mes_anterior"], "clientes_ativos_mes_anterior", "defasagem")

    # Receita: CMV ÷ (CMV/receita)
    m = ausente["receita_bruta"]
    df.loc[m, "receita_bruta"] = np.round(df.loc[m, "cmv"] / r_cmv[m], 2)
    registrar(m, "receita_bruta", "razao_cmv")

    # Pedidos: clientes ativos × frequência (nunca abaixo de clientes ativos)
    m = ausente["pedidos"]
    df.loc[m, "pedidos"] = np.maximum(df.loc[m, "clientes_ativos"], np.round(df.loc[m, "clientes_ativos"] * r_freq[m]))
    registrar(m, "pedidos", "razao_frequencia")

    # Componentes proporcionais à receita
    for coluna in ("cmv", "comissoes_tarifas", "frete_subsidiado"):
        m = ausente[coluna]
        df.loc[m, coluna] = np.round(df.loc[m, "receita_bruta"] * r_rec[coluna][m], 2)
        registrar(m, coluna, "razao_receita")
    m = ausente["impostos_variaveis"] & ~mei
    df.loc[m, "impostos_variaveis"] = np.round(df.loc[m, "receita_bruta"] * r_rec["impostos_variaveis"][m], 2)
    registrar(m, "impostos_variaveis", "razao_receita")
    m = ausente["impostos_variaveis"] & mei
    df.loc[m, "impostos_variaveis"] = 0.0
    registrar(m, "impostos_variaveis", "regra_porte")

    # Marketing: clientes novos × CAC
    m = ausente["investimento_marketing"]
    df.loc[m, "investimento_marketing"] = np.round(df.loc[m, "clientes_novos"] * r_cac[m], 2)
    registrar(m, "investimento_marketing", "razao_cac")

    # Custos fixos e negócios ativos: custo fixo por negócio
    m = ausente["custos_fixos"]
    df.loc[m, "custos_fixos"] = np.round(df.loc[m, "negocios_ativos"] * r_cf[m], 2)
    registrar(m, "custos_fixos", "razao_negocio")
    m = ausente["negocios_ativos"]
    df.loc[m, "negocios_ativos"] = np.maximum(1, np.round(df.loc[m, "custos_fixos"] / r_cf[m]))
    registrar(m, "negocios_ativos", "razao_negocio")

    # Impostos fixos: DAS legal do MEI; zero para a ME
    m = ausente["impostos_fixos"] & mei
    df.loc[m, "impostos_fixos"] = np.round(df.loc[m, "negocios_ativos"] * config.das_mei_em(df.loc[m, "data"]), 2)
    registrar(m, "impostos_fixos", "regra_das")
    m = ausente["impostos_fixos"] & ~mei
    df.loc[m, "impostos_fixos"] = 0.0
    registrar(m, "impostos_fixos", "regra_porte")

    relatorio = {
        "imputacoes_por_coluna": por_coluna,
        "imputacoes_por_metodo": dict(sorted(metodos.items())),
        "total_imputado": int(sum(por_coluna.values())),
        "divergencias_defasagem": divergencias,
        "_celulas": imputadas,
    }
    return config.ordenar_canonico(df), relatorio


def _validar_painel(df: pd.DataFrame, n_meses: int) -> list[str]:
    """Valida os invariantes do painel limpo (grão, nulos, identidades, mínimos).

    Args:
        df: painel limpo.
        n_meses: número de meses esperado.

    Returns:
        Lista de violações (vazia se tudo estiver correto).
    """
    erros = []
    cols = config.CHAVE_PAINEL + config.COLUNAS_MEDIDA_BRUTAS
    if df[cols].isna().any().any():
        erros.append(f"nulos restantes: {df[cols].isna().sum()[lambda s: s > 0].to_dict()}")
    if df.duplicated(config.CHAVE_PAINEL).any():
        erros.append(f"chave duplicada em {int(df.duplicated(config.CHAVE_PAINEL).sum())} linhas")
    esperado = n_meses * len(config.CANAIS) * len(config.PORTES) * len(config.SEGMENTOS)
    if len(df) != esperado:
        erros.append(f"grade incompleta: {len(df)} linhas, esperado {esperado}")
    if (df[config.COLUNAS_MEDIDA_BRUTAS] < 0).any().any():
        erros.append("medidas negativas")
    for c in ("receita_bruta", "pedidos", "clientes_ativos", "negocios_ativos"):
        if (df[c] < 1).any():
            erros.append(f"{c} < 1")
    if (df["clientes_ativos"] != df["clientes_novos"] + df["clientes_recorrentes"]).any():
        erros.append("identidade ativos = novos + recorrentes violada")
    if (df["clientes_recorrentes"] > df["clientes_ativos_mes_anterior"]).any():
        erros.append("recorrentes > ativos do mês anterior")
    if (df["clientes_novos"] < 1).any():
        erros.append("clientes_novos < 1")
    if (df["pedidos"] < df["clientes_ativos"]).any():
        erros.append("pedidos < clientes_ativos")
    return erros


def limpar_painel_simulado(caminho: Path, gabarito: dict) -> tuple[pd.DataFrame, dict]:
    """Limpa o painel bruto simulado e confere o resultado com o gabarito da injeção (seção 9.2).

    Args:
        caminho: CSV bruto (``;``, ``utf-8-sig``).
        gabarito: gabarito da injeção.

    Returns:
        ``(painel limpo, seção painel_simulado do relatório)``.

    Raises:
        ValueError: coluna obrigatória ausente, rótulo desconhecido, data ou número ilegível.
        ErroQualidadeDados: invariantes violados após a limpeza.
    """
    # 1. Leitura
    bruto = pd.read_csv(caminho, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    antes = {"linhas": int(len(bruto)), "colunas": int(bruto.shape[1])}
    # 2. Cabeçalhos
    faltando = [c for c in config.MAPA_COLUNAS_BRUTAS if c not in bruto.columns]
    if faltando:
        raise ValueError(f"Colunas obrigatórias ausentes no bruto: {faltando}")
    extras = [c for c in bruto.columns if c not in config.MAPA_COLUNAS_BRUTAS]
    if extras:
        logger.warning("Colunas extras descartadas no bruto: %s", extras)
    df = bruto[list(config.MAPA_COLUNAS_BRUTAS)].rename(columns=config.MAPA_COLUNAS_BRUTAS)
    antes["nulos_por_coluna"] = {c: int((df[c] == "").sum()) for c in df.columns}
    antes["formatos_data"] = df["mes_referencia"].map(_formato_data).value_counts().to_dict()
    moeda = df[config.COLUNAS_MONETARIAS]
    antes["numeros_formato_br"] = {
        "moeda_br": int(((~moeda.apply(lambda s: s.str.startswith("R$"))) & moeda.apply(lambda s: s.str.contains(",", regex=False))).sum().sum()),
        "moeda_br_com_cifrao": int(moeda.apply(lambda s: s.str.startswith("R$")).sum().sum()),
        "contagem_com_milhar": int(df[config.COLUNAS_CONTAGEM].apply(lambda s: s.str.contains(".", regex=False)).sum().sum()),
    }
    antes["rotulos_variantes"] = {
        c: {str(k): int(v) for k, v in df[c].value_counts().sort_index().items() if k not in config.MAPA_ROTULOS[c].values()}
        for c in ("canal", "porte", "segmento")
    }
    # 3. Duplicatas exatas (texto bruto)
    n_dup_exatas = int(df.duplicated().sum())
    antes["duplicatas_exatas"] = n_dup_exatas
    df = df.drop_duplicates().reset_index(drop=True)
    logger.info("Limpeza: %d linhas brutas; %d duplicatas exatas removidas → %d", antes["linhas"], n_dup_exatas, len(df))
    # 4. Rótulos
    for coluna in ("canal", "porte", "segmento"):
        normal = df[coluna].map(normalizar_texto)
        mapeado = normal.map(config.MAPA_ROTULOS[coluna])
        desconhecidos = df.loc[mapeado.isna(), coluna].unique().tolist()
        if desconhecidos:
            raise ValueError(f"Rótulos desconhecidos em {coluna}: {desconhecidos[:5]}")
        df[coluna] = mapeado.astype(str)
    # 5. Datas
    datas = []
    invalidas = []
    for s in df["mes_referencia"]:
        try:
            datas.append(parse_mes_referencia(s))
        except ValueError:
            invalidas.append(s)
            datas.append(pd.NaT)
    if invalidas:
        raise ValueError(f"Datas ilegíveis no bruto ({len(invalidas)}): {invalidas[:5]}")
    df["data"] = pd.to_datetime(pd.Series(datas, index=df.index))
    df = df.drop(columns=["mes_referencia"])
    # 6. Números
    for coluna in config.COLUNAS_MEDIDA_BRUTAS:
        conv = parse_inteiro if coluna in config.COLUNAS_CONTAGEM else parse_numero_br
        valores = []
        ruins = []
        for s in df[coluna]:
            if s == "":
                valores.append(np.nan)
                continue
            try:
                valores.append(float(conv(s)))
            except ValueError:
                ruins.append(s)
        if ruins:
            raise ValueError(f"Números ilegíveis em {coluna}: {ruins[:5]}")
        df[coluna] = np.array(valores, dtype=float)
    # 7. Duplicatas por chave: mantém a linha com menos ausentes (empate: a primeira)
    df["_ausentes"] = df[config.COLUNAS_MEDIDA_BRUTAS].isna().sum(axis=1)
    df["_ordem"] = np.arange(len(df))
    antes_chave = len(df)
    df = df.sort_values(["_ausentes", "_ordem"], kind="mergesort").drop_duplicates(config.CHAVE_PAINEL, keep="first")
    df = df.sort_values("_ordem").drop(columns=["_ausentes", "_ordem"]).reset_index(drop=True)
    n_dup_chave = int(antes_chave - len(df))
    logger.info("Limpeza: %d duplicatas por chave (data, canal, porte, segmento) removidas → %d linhas", n_dup_chave, len(df))
    nulos_antes_imput = int(df[config.COLUNAS_MEDIDA_BRUTAS].isna().sum().sum())
    # 8. Imputação por razão
    df, rel_imp = imputar_ausentes(df)
    logger.info("Limpeza: %d células ausentes imputadas por razão; métodos %s", rel_imp["total_imputado"], rel_imp["imputacoes_por_metodo"])
    if rel_imp["divergencias_defasagem"]:
        logger.warning("Limpeza: %d divergências na defasagem de clientes", rel_imp["divergencias_defasagem"])
    # 9. Tipos finais
    for coluna in config.COLUNAS_CONTAGEM:
        df[coluna] = np.round(df[coluna].to_numpy(dtype=float)).astype(np.int64)
    for coluna in config.COLUNAS_MONETARIAS:
        df[coluna] = np.round(df[coluna].astype(float), 2)
    for coluna in ("canal", "porte", "segmento"):
        df[coluna] = df[coluna].astype(str)
    df = df[config.CHAVE_PAINEL + config.COLUNAS_MEDIDA_BRUTAS + ["qtd_campos_imputados"]]
    # 10. Validação
    n_meses = int(df["data"].nunique())
    erros = _validar_painel(df, n_meses)
    depois = {
        "linhas": int(len(df)),
        "nulos_total": int(df.isna().sum().sum()),
        "duplicatas_chave": int(df.duplicated(config.CHAVE_PAINEL).sum()),
        "duplicatas_chave_removidas": n_dup_chave,
        "celulas_ausentes_antes_imputacao": nulos_antes_imput,
        "imputacoes_por_coluna": rel_imp["imputacoes_por_coluna"],
        "imputacoes_por_metodo": rel_imp["imputacoes_por_metodo"],
        "total_imputado": rel_imp["total_imputado"],
        "divergencias_defasagem": rel_imp["divergencias_defasagem"],
        "linhas_com_imputacao": int((df["qtd_campos_imputados"] > 0).sum()),
    }
    # 11. Conferência com o gabarito
    esperadas = {(c["data"], c["canal"], c["porte"], c["segmento"], c["coluna"]) for c in gabarito.get("celulas_ausentes", [])}
    conferencia = {
        "duplicatas_exatas": n_dup_exatas == gabarito.get("duplicatas_exatas"),
        "duplicatas_chave": n_dup_chave == gabarito.get("duplicatas_formatadas"),
        "celulas_imputadas": rel_imp["total_imputado"] == gabarito.get("celulas_ausentes_total"),
        "conjunto_celulas": set(rel_imp["_celulas"]) == esperadas,
        "linhas_limpas": len(df) == gabarito.get("linhas_limpas"),
    }
    for chave, ok in conferencia.items():
        if not ok:
            logger.warning("Conferência com o gabarito falhou: %s", chave)
    relatorio = {"antes": antes, "depois": depois, "conferencia_gabarito": conferencia,
                 "arquivo_bruto": config.caminho_relativo(caminho)}
    logger.info("Limpeza concluída: antes %d linhas / %d ausentes → depois %d linhas / %d nulos; gabarito %s",
                antes["linhas"], sum(antes["nulos_por_coluna"].values()), depois["linhas"], depois["nulos_total"],
                "OK" if all(conferencia.values()) else "COM DIVERGÊNCIAS")
    if erros:
        relatorio["erros_validacao"] = erros
        gravar_relatorio_qualidade({"painel_simulado": relatorio})
        raise ErroQualidadeDados(f"Painel limpo inválido: {erros}")
    return df, relatorio


def gravar_relatorio_qualidade(relatorio: dict) -> Path:
    """Grava o relatório de qualidade em JSON (UTF-8, só caminhos relativos).

    Args:
        relatorio: dicionário com ``dados_reais`` e ``painel_simulado``.

    Returns:
        Caminho do arquivo gravado.
    """
    config.CAMINHO_RELATORIO_QUALIDADE.parent.mkdir(parents=True, exist_ok=True)

    def limpar(obj: object) -> object:
        """Converte tipos numpy/pandas em tipos nativos do JSON."""
        if isinstance(obj, dict):
            return {str(k): limpar(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [limpar(v) for v in obj]
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        return obj

    with open(config.CAMINHO_RELATORIO_QUALIDADE, "w", encoding="utf-8", newline="\n") as arq:
        json.dump(limpar(relatorio), arq, ensure_ascii=False, indent=2)
    logger.info("Relatório de qualidade gravado: %s", config.caminho_relativo(config.CAMINHO_RELATORIO_QUALIDADE))
    return config.CAMINHO_RELATORIO_QUALIDADE
