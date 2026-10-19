"""Configuração central do pipeline: caminhos, fontes, períodos, parâmetros e premissas.

Todas as constantes do projeto ficam neste módulo. Os demais módulos importam daqui e não
definem números "mágicos". Cada parâmetro numérico da simulação tem a sua origem registrada em
``ORIGEM_PARAMETROS`` (fonte oficial, fonte de mercado, fonte com ajuste do autor ou premissa).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Caminhos (sempre relativos à raiz do projeto nas saídas)
# ---------------------------------------------------------------------------
RAIZ: Path = Path(__file__).resolve().parents[1]
DIR_DATA: Path = RAIZ / "data"
DIR_RAW_API: Path = DIR_DATA / "raw" / "api"
DIR_RAW_SIMULADO: Path = DIR_DATA / "raw" / "simulado"
DIR_PROCESSED: Path = DIR_DATA / "processed"
DIR_OUTPUTS: Path = RAIZ / "outputs"
DIR_GRAFICOS: Path = DIR_OUTPUTS / "graficos"
DIR_TABELAS: Path = DIR_OUTPUTS / "tabelas"
DIR_LOGS: Path = DIR_OUTPUTS / "logs"

CAMINHO_BRUTO_SIMULADO: Path = DIR_RAW_SIMULADO / "canais_vendas_bruto.csv"
CAMINHO_GABARITO_SIMULADO: Path = DIR_RAW_SIMULADO / "canais_vendas_bruto.meta.json"
CAMINHO_CSV_FINAL: Path = DIR_PROCESSED / "dados_processados_canais_vendas.csv"
CAMINHO_RELATORIO_QUALIDADE: Path = DIR_OUTPUTS / "relatorio_qualidade_dados.json"
CAMINHO_LOG: Path = DIR_LOGS / "pipeline.log"

MESES_ABREV: list[str] = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def caminho_relativo(p: Path) -> str:
    """Converte um caminho em texto relativo à raiz do projeto (com barras "/").

    Args:
        p: caminho absoluto ou relativo.

    Returns:
        Caminho relativo à raiz; se estiver fora dela, apenas o nome do arquivo.
    """
    p = Path(p)
    try:
        return p.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return p.name


def rotulo_mes_base(d: pd.Timestamp) -> str:
    """Rótulo curto de um mês no formato brasileiro (ex.: ``ago/2026``).

    Args:
        d: data qualquer dentro do mês.

    Returns:
        Texto ``mmm/aaaa``.
    """
    d = pd.Timestamp(d)
    return f"{MESES_ABREV[d.month - 1]}/{d.year}"


def calcular_data_fim(
    ultimo_pmc_8880: pd.Timestamp,
    ultimo_pmc_8882: pd.Timestamp,
    ultimo_ipca: pd.Timestamp,
    hoje: pd.Timestamp,
) -> pd.Timestamp:
    """Calcula o último mês da série exportada (regra da seção 5 do design).

    ``data_fim`` = mínimo entre o último mês da PMC 8880, o da PMC 8882, o do IPCA usado e o mês
    anterior ao mês da execução.

    Args:
        ultimo_pmc_8880: último mês disponível na PMC 8880.
        ultimo_pmc_8882: último mês disponível na PMC 8882.
        ultimo_ipca: último mês disponível no IPCA usado.
        hoje: data da execução.

    Returns:
        Primeiro dia do mês final.
    """
    hoje = pd.Timestamp(hoje)
    mes_anterior = (hoje.to_period("M") - 1).to_timestamp()
    candidatos = [pd.Timestamp(x).to_period("M").to_timestamp() for x in (ultimo_pmc_8880, ultimo_pmc_8882, ultimo_ipca)]
    return min(candidatos + [mes_anterior])


def ordenar_canonico(df: pd.DataFrame, colunas: list[str] | None = None) -> pd.DataFrame:
    """Ordena um DataFrame pela ordem canônica das dimensões (não alfabética).

    A ordem de ``canal``, ``porte`` e ``segmento`` segue as listas ``CANAIS``, ``PORTES`` e
    ``SEGMENTOS``; ``recorte_temporal`` e ``fase`` seguem ``RECORTES`` e ``FASES``; as demais
    colunas (ex.: ``data``) usam a ordem natural.

    Args:
        df: tabela a ordenar.
        colunas: colunas de ordenação, na prioridade desejada (padrão: chave do painel).

    Returns:
        Cópia ordenada, com índice reiniciado.
    """
    colunas = colunas or ["data", "canal", "porte", "segmento"]
    ordens = {"canal": CANAIS, "porte": PORTES, "segmento": SEGMENTOS, "recorte_temporal": RECORTES, "fase": FASES}
    chaves = {}
    for col in colunas:
        if col in ordens:
            posicao = {v: i for i, v in enumerate(ordens[col])}
            chaves[col] = df[col].map(lambda v, p=posicao: p.get(v, len(p)))
        else:
            chaves[col] = df[col]
    aux = pd.DataFrame(chaves, index=df.index)
    ordem = aux.sort_values(colunas, kind="mergesort").index
    return df.loc[ordem].reset_index(drop=True)


def mes_fim_consulta(hoje: pd.Timestamp) -> pd.Timestamp:
    """Mês anterior ao mês da execução, usado como ``{fim}`` nas consultas às APIs.

    Args:
        hoje: data da execução.

    Returns:
        Primeiro dia do mês anterior.
    """
    return (pd.Timestamp(hoje).to_period("M") - 1).to_timestamp()


# ---------------------------------------------------------------------------
# Fontes de dados reais (seção 6.1)
# ---------------------------------------------------------------------------
URL_SIDRA = "https://apisidra.ibge.gov.br/values"
URL_BCB_433 = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
USER_AGENT = "Mozilla/5.0 (compatible; projeto-canais-vendas/1.0; +https://github.com/KevynFirst)"
HTTP_TIMEOUT: tuple[int, int] = (10, 60)
HTTP_TENTATIVAS: int = 3
HTTP_ESPERAS_S: list[int] = [2, 4]
HTTP_STATUS_REPETIR: set[int] = {429, 500, 502, 503, 504}

FONTES: dict[str, dict[str, str]] = {
    "pmc_8880": {
        "fonte": "IBGE/SIDRA — PMC, tabela 8880 (Brasil, 2022 = 100)",
        "modelo": URL_SIDRA + "/t/8880/n1/all/v/7169,7170/p/201712-{fim}/c11046/56733,56734",
    },
    "pmc_8882": {
        "fonte": "IBGE/SIDRA — PMC, tabela 8882 (atividades, 2022 = 100)",
        "modelo": URL_SIDRA
        + "/t/8882/n1/all/v/7169,7170/p/201712-{fim}/c11046/56733,56734/c85/90672,90673,2759,103155,103157",
    },
    "ipca_bcb_433": {
        "fonte": "BCB/SGS — série 433 (IPCA, variação mensal)",
        "modelo": URL_BCB_433,
    },
    "ipca_sidra_1737": {
        "fonte": "IBGE/SIDRA — IPCA, tabela 1737, variável 63",
        "modelo": URL_SIDRA + "/t/1737/n1/all/v/63/p/201801-{fim}",
    },
    "pac_9349": {
        "fonte": "IBGE/SIDRA — PAC, tabela 9349 (2019–2023)",
        "modelo": URL_SIDRA
        + "/t/9349/n1/all/v/540,866/p/all/c12352/all/c11070/106721,106725,106726,106727,7129,7130,7131,7133",
    },
    "pac_10656": {
        "fonte": "IBGE/SIDRA — PAC, tabela 10656 (2024, série nova)",
        "modelo": URL_SIDRA
        + "/t/10656/n1/all/v/540,866/p/all/c12352/all/c11070/83337,83341,83342,83346,83347,83348,83349,83351,83353,83354",
    },
}
ORDEM_FONTES: list[str] = ["pmc_8880", "pmc_8882", "ipca_bcb_433", "ipca_sidra_1737", "pac_9349", "pac_10656"]
FONTES_OBRIGATORIAS: list[str] = ["pmc_8880", "pmc_8882", "pac_9349", "pac_10656"]
FONTES_IPCA: list[str] = ["ipca_bcb_433", "ipca_sidra_1737"]
TOLERANCIA_IPCA_PP: float = 0.005

ROTULO_IPCA_BCB = "BCB SGS 433"
ROTULO_IPCA_BCB_CONFERIDO = "BCB SGS 433 (conferida com IBGE SIDRA 1737)"
ROTULO_IPCA_SIDRA = "IBGE SIDRA 1737"

# Mapeamento dos rótulos do cabeçalho do SIDRA para nomes de coluna (seção 9.1)
MAPA_CABECALHO_SIDRA: dict[str, str] = {
    "Mês (Código)": "periodo",
    "Ano (Código)": "periodo",
    "Variável (Código)": "variavel_id",
    "Tipos de índice (Código)": "tipo_indice_id",
    "Atividades (Código)": "atividade_id",
    "Formas de comercialização (Código)": "forma_id",
    "Divisão de comércio, grupo e classe de atividade (Código)": "classe_id",
}
SIMBOLOS_ZERO_SIDRA: set[str] = {"-"}
SIMBOLOS_NAN_SIDRA: set[str] = {"X", "..", "..."}

# PMC: variáveis e tipos de índice
PMC_VAR_NSA = 7169
PMC_VAR_SA = 7170
PMC_TIPO_RECEITA = 56733
PMC_TIPO_VOLUME = 56734

# PAC: formas de comercialização e papéis das classes (seção 6.1)
PAC_FORMAS: list[int] = [106744, 106745, 106746, 106748, 106749, 106751, 106754]
PAC_FORMA_INTERNET: int = 106749
PAC_VAR_EMPRESAS = 540
PAC_VAR_RECEITA = 866
PAC_SERIES: dict[str, str] = {"pac_9349": "9349 (2019–2023)", "pac_10656": "10656 (2024, série nova)"}
PAC_PAPEIS: dict[str, dict[str, list[int]]] = {
    "pac_9349": {
        "total": [106721],
        "moda": [106727],
        "casa": [7131],
        "eletronicos": [7130, 7133],
        "beleza": [7129],
        "alimentos": [106726],
        "concentracao": [106725],
    },
    "pac_10656": {
        "total": [83337],
        "moda": [83349, 83353, 83354],
        "casa": [83348],
        "eletronicos": [83346, 83347],
        "beleza": [83351],
        "alimentos": [83342],
        "concentracao": [83341],
    },
}
PAC_ORDEM_PAPEIS: list[str] = ["total", "moda", "casa", "eletronicos", "beleza", "alimentos", "concentracao"]

# ---------------------------------------------------------------------------
# Períodos e recortes (seção 5)
# ---------------------------------------------------------------------------
DATA_AQUECIMENTO = pd.Timestamp("2017-12-01")
DATA_INICIO = pd.Timestamp("2018-01-01")
INICIO_PANDEMIA = pd.Timestamp("2020-03-01")
INICIO_POS_PANDEMIA = pd.Timestamp("2022-06-01")
FIM_POS_ATE_2024 = pd.Timestamp("2024-12-01")
INICIO_CENARIO_ATUAL = pd.Timestamp("2025-01-01")

FASE_PRE = "Pré-pandemia"
FASE_PANDEMIA = "Pandemia"
FASE_POS = "Pós-pandemia"
FASES: list[str] = [FASE_PRE, FASE_PANDEMIA, FASE_POS]

RECORTE_PRE = "Pré-pandemia"
RECORTE_PANDEMIA = "Pandemia"
RECORTE_POS = "Pós-pandemia (jun/2022–dez/2024)"
RECORTE_ATUAL = "Cenário Atual (2025–2026)"
RECORTES: list[str] = [RECORTE_PRE, RECORTE_PANDEMIA, RECORTE_POS, RECORTE_ATUAL]

MARCOS: list[dict[str, str]] = [
    {"data": "2020-03-11", "rotulo": "OMS: pandemia", "fonte": "https://www.paho.org/pt/news/11-3-2020-who-characterizes-covid-19-pandemic"},
    {"data": "2020-11-16", "rotulo": "Pix", "fonte": "https://agenciabrasil.ebc.com.br/economia/noticia/2020-11/pix-novo-sistema-de-pagamento-instantaneo-entra-em-funcionamento"},
    {"data": "2022-05-22", "rotulo": "Fim da ESPIN", "fonte": "https://www.in.gov.br/en/web/dou/-/portaria-gm/ms-n-913-de-22-de-abril-de-2022-394545491"},
    {"data": "2024-06-27", "rotulo": "Lei 14.902", "fonte": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14902.htm"},
    {"data": "2025-05-08", "rotulo": "TikTok Shop", "fonte": "https://newsroom.tiktok.com/pt-br/tiktok-shop-chega-ao-brasil"},
]

# ---------------------------------------------------------------------------
# Dimensões do painel (ordem canônica, seção 7.1)
# ---------------------------------------------------------------------------
SEGMENTOS: list[str] = [
    "Moda e Acessórios",
    "Casa e Decoração",
    "Eletrônicos e Acessórios",
    "Beleza e Cuidados Pessoais",
    "Alimentos e Bebidas",
]
SEGMENTO_CODIGOS: list[str] = ["moda", "casa", "eletronicos", "beleza", "alimentos"]
SEGMENTO_PARA_CODIGO: dict[str, str] = dict(zip(SEGMENTOS, SEGMENTO_CODIGOS))
PORTES: list[str] = ["MEI", "ME"]
CANAIS: list[str] = ["Loja Física", "Marketplace", "E-commerce Próprio"]
CANAL_CODIGOS: list[str] = ["fisica", "marketplace", "ecommerce_proprio"]
CANAL_PARA_CODIGO: dict[str, str] = dict(zip(CANAIS, CANAL_CODIGOS))
CANAIS_DIGITAIS: list[str] = ["Marketplace", "E-commerce Próprio"]

# Segmento → atividade da PMC 8882 (classificação c85)
SEGMENTO_ATIVIDADE_PMC: dict[str, dict[str, object]] = {
    "moda": {"id": 90673, "nome": "Tecidos, vestuário e calçados"},
    "casa": {"id": 2759, "nome": "Móveis e eletrodomésticos"},
    "eletronicos": {"id": 103157, "nome": "Equipamentos e materiais para escritório, informática e comunicação"},
    "beleza": {"id": 103155, "nome": "Artigos farmacêuticos, médicos, ortopédicos, de perfumaria e cosméticos"},
    "alimentos": {"id": 90672, "nome": "Hipermercados, supermercados, produtos alimentícios, bebidas e fumo"},
}

# ---------------------------------------------------------------------------
# Parâmetros da simulação (seções 7.1–7.7 e 8) e registro de premissas (seção 7.10)
# ---------------------------------------------------------------------------
PARAMETROS: dict[str, object] = {
    "negocios_por_segmento": {"MEI": 400, "ME": 100},
    "phi_ancoras": {
        "MEI": {
            "marketplace": {"2017-12-01": 0.07, "2020-02-01": 0.08, "2020-05-01": 0.17, "2021-12-01": 0.22,
                            "2022-05-01": 0.22, "2024-12-01": 0.26, "2026-08-01": 0.28},
            "ecommerce_proprio": {"2017-12-01": 0.05, "2020-02-01": 0.06, "2020-05-01": 0.13, "2021-12-01": 0.14,
                                  "2022-05-01": 0.14, "2024-12-01": 0.14, "2026-08-01": 0.14},
        },
        "ME": {
            "marketplace": {"2017-12-01": 0.060, "2020-02-01": 0.065, "2020-05-01": 0.130, "2021-12-01": 0.170,
                            "2022-05-01": 0.170, "2024-12-01": 0.200, "2026-08-01": 0.210},
            "ecommerce_proprio": {"2017-12-01": 0.040, "2020-02-01": 0.045, "2020-05-01": 0.090, "2021-12-01": 0.110,
                                  "2022-05-01": 0.110, "2024-12-01": 0.120, "2026-08-01": 0.130},
        },
    },
    "phi_multiplicador_segmento": {
        "moda": {"marketplace": 1.10, "ecommerce_proprio": 1.20},
        "casa": {"marketplace": 1.15, "ecommerce_proprio": 1.00},
        "eletronicos": {"marketplace": 1.60, "ecommerce_proprio": 1.00},
        "beleza": {"marketplace": 1.00, "ecommerce_proprio": 1.25},
        "alimentos": {"marketplace": 0.45, "ecommerce_proprio": 0.70},
    },
    "receita_media_2019": {
        "MEI": {"moda": 3900.0, "casa": 4000.0, "eletronicos": 4100.0, "beleza": 3500.0, "alimentos": 3700.0},
        "ME": {"moda": 16000.0, "casa": 17000.0, "eletronicos": 17500.0, "beleza": 14500.0, "alimentos": 15500.0},
    },
    "rho_canal": {
        "MEI": {"fisica": 1.00, "marketplace": 0.80, "ecommerce_proprio": 0.75},
        "ME": {"fisica": 1.00, "marketplace": 0.85, "ecommerce_proprio": 0.90},
    },
    "impulso_digital_ancoras": {
        "2017-12-01": 1.00, "2020-02-01": 1.00, "2020-03-01": 1.10, "2020-04-01": 1.70, "2020-05-01": 1.60,
        "2020-06-01": 1.45, "2020-12-01": 1.25, "2021-06-01": 1.15, "2021-12-01": 1.08, "2022-05-01": 1.03,
        "2022-12-01": 1.00,
    },
    "sigma_ruido_receita": 0.05,
    "ticket_2019": {
        "moda": {"fisica": 95.0, "marketplace": 85.0, "ecommerce_proprio": 115.0},
        "casa": {"fisica": 140.0, "marketplace": 120.0, "ecommerce_proprio": 165.0},
        "eletronicos": {"fisica": 120.0, "marketplace": 95.0, "ecommerce_proprio": 160.0},
        "beleza": {"fisica": 70.0, "marketplace": 65.0, "ecommerce_proprio": 85.0},
        "alimentos": {"fisica": 45.0, "marketplace": 70.0, "ecommerce_proprio": 80.0},
    },
    "sigma_ruido_ticket": 0.03,
    "frequencia_compra": {
        "moda": {"fisica": 1.10, "marketplace": 1.02, "ecommerce_proprio": 1.08},
        "casa": {"fisica": 1.05, "marketplace": 1.01, "ecommerce_proprio": 1.03},
        "eletronicos": {"fisica": 1.05, "marketplace": 1.01, "ecommerce_proprio": 1.03},
        "beleza": {"fisica": 1.20, "marketplace": 1.03, "ecommerce_proprio": 1.15},
        "alimentos": {"fisica": 1.60, "marketplace": 1.05, "ecommerce_proprio": 1.35},
    },
    "retencao_base": {"fisica": 0.32, "marketplace": 0.10},
    "retencao_ecommerce_ancoras": {"2017-12-01": 0.20, "2026-08-01": 0.30},
    "retencao_ajuste_segmento": {"moda": 0.0, "casa": -0.06, "eletronicos": -0.07, "beleza": 0.06, "alimentos": 0.12},
    "retencao_choque_fisica": {"valor": -0.10, "inicio": "2020-04-01", "fim": "2020-06-01"},
    "retencao_limites": [0.02, 0.85],
    "cac_2019": {
        "moda": {"fisica": 5.0, "marketplace": 5.0, "ecommerce_proprio": 16.0},
        "casa": {"fisica": 7.0, "marketplace": 6.0, "ecommerce_proprio": 20.0},
        "eletronicos": {"fisica": 6.0, "marketplace": 6.0, "ecommerce_proprio": 16.0},
        "beleza": {"fisica": 4.0, "marketplace": 4.0, "ecommerce_proprio": 14.0},
        "alimentos": {"fisica": 2.0, "marketplace": 4.0, "ecommerce_proprio": 10.0},
    },
    "cac_tendencia_real_aa": {"fisica": 0.0, "marketplace": 0.02, "ecommerce_proprio": 0.03},
    "sigma_ruido_cac": 0.08,
    "ml_comissao_pct": [{"inicio": "2017-12-01", "pct": 0.11}, {"inicio": "2022-09-01", "pct": 0.12}],
    "ml_custo_fixo": [
        {"inicio": "2017-12-01", "fixo": 0.0, "limite": 0.0},
        {"inicio": "2018-07-01", "fixo": 5.0, "limite": 120.0},
        {"inicio": "2020-10-01", "fixo": 5.0, "limite": 99.0},
        {"inicio": "2021-04-01", "fixo": 5.0, "limite": 79.0},
        {"inicio": "2023-03-01", "fixo": 5.5, "limite": 79.0},
        {"inicio": "2024-01-01", "fixo": 6.0, "limite": 79.0},
    ],
    "ml_sigma_ln_pedido": 0.6,
    "taxa_proc_ecommerce_pre_pix": 0.045,
    "taxa_proc_ecommerce_cartao": 0.0419,
    "taxa_proc_ecommerce_pix": 0.0099,
    "inicio_taxa_pix_ecommerce": "2020-11-01",
    "pix_ecommerce_ancoras": {"2020-10-01": 0.0, "2022-12-01": 0.35, "2026-08-01": 0.45},
    "mdr_cartao_fisica": 0.022,
    "pix_fisica_ancoras": {"2020-10-01": 0.0, "2022-12-01": 0.30, "2026-08-01": 0.40},
    "frete_medio_2019": {"fisica": 0.0, "marketplace": 18.0, "ecommerce_proprio": 22.0},
    "frete_parcela_vendedor": {"fisica": 0.0, "marketplace": 0.25, "ecommerce_proprio": 0.40},
    "cmv_pct_segmento": {"moda": 0.551, "casa": 0.593, "eletronicos": 0.580, "beleza": 0.602, "alimentos": 0.657},
    "cmv_delta_canal": {"fisica": 0.0, "marketplace": 0.0, "ecommerce_proprio": -0.010},
    "sigma_ruido_cmv": 0.005,
    "custos_fixos_2019": {
        "MEI": {"fisica": 950.0, "marketplace": 260.0, "ecommerce_proprio": 320.0},
        "ME": {"fisica": 4200.0, "marketplace": 1000.0, "ecommerce_proprio": 1400.0},
    },
    "custos_fixos_mult_segmento": {"moda": 1.00, "casa": 1.00, "eletronicos": 0.90, "beleza": 0.95, "alimentos": 0.85},
    "das_pct_salario_minimo": 0.05,
    "das_icms": 1.00,
    "salario_minimo": {
        "2018-01-01": 954.0, "2019-01-01": 998.0, "2020-01-01": 1039.0, "2020-02-01": 1045.0,
        "2021-01-01": 1100.0, "2022-01-01": 1212.0, "2023-01-01": 1302.0, "2023-05-01": 1320.0,
        "2024-01-01": 1412.0, "2025-01-01": 1518.0, "2026-01-01": 1621.0,
    },
    "simples_anexo_i": [
        {"ate": 180000.00, "aliquota": 0.040, "deducao": 0.0},
        {"ate": 360000.00, "aliquota": 0.073, "deducao": 5940.0},
        {"ate": 720000.00, "aliquota": 0.095, "deducao": 13860.0},
        {"ate": 1800000.00, "aliquota": 0.107, "deducao": 22500.0},
        {"ate": 3600000.00, "aliquota": 0.143, "deducao": 87300.0},
        {"ate": 4800000.00, "aliquota": 0.190, "deducao": 378000.0},
    ],
    "rbt12_inicial": {"janela_meses": 12, "complemento": "receita de referência R̄[ME][s] × ρ[ME][c] × PI_s(t)"},
    "teto_receita_mei": 81000.00,
    "teto_receita_me": 360000.00,
    "semente_simulacao": 2026,
    "semente_problemas": 2027,
    "injecao_problemas": {
        "formatos_data": {"AAAA-MM": 0.60, "MM/AAAA": 0.25, "AAAA-MM-01": 0.15},
        "fracao_rotulo_canal": 0.20,
        "fracao_rotulo_porte": 0.10,
        "fracao_rotulo_segmento": 0.10,
        "fracao_moeda_br": 0.35,
        "fracao_moeda_br_cifrao": 0.05,
        "fracao_milhar_contagem": 0.10,
        "fracao_celulas_ausentes": 0.025,
        "fracao_duplicatas_exatas": 0.015,
        "fracao_duplicatas_formatadas": 0.005,
    },
}


@dataclass(frozen=True)
class Origem:
    """Origem de um parâmetro da simulação.

    Attributes:
        tipo: "fonte oficial", "fonte de mercado", "fonte + ajuste do autor" ou "premissa do autor".
        referencia: URL da fonte (vazia para premissa do autor).
        justificativa: frase curta explicando o valor.
    """

    tipo: str
    referencia: str
    justificativa: str


_URL_PAC_9349 = "https://servicodados.ibge.gov.br/api/v3/agregados/9349/metadados"
_URL_PAC_10645 = "https://servicodados.ibge.gov.br/api/v3/agregados/10645/periodos/2024/variaveis/1400|503|502"
_URL_SEBRAE_2021 = "https://agenciasebrae.com.br/inovacao-e-tecnologia/vendas-online-representam-mais-da-metade-do-faturamento-de-30-dos-mei/"
_URL_LC123 = "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm"
_URL_ML = "https://www.mercadolivre.com.br/ajuda/quanto-custa-vender-um-produto_1338"
_URL_NUVEMSHOP = "https://www.nuvemshop.com.br/planos-e-precos"

ORIGEM_PARAMETROS: dict[str, Origem] = {
    "negocios_por_segmento": Origem("premissa do autor", "", "Tamanho do painel sintético: 400 MEIs e 100 MEs por segmento."),
    "phi_ancoras": Origem("fonte + ajuste do autor", _URL_SEBRAE_2021,
                          "Migração de negócios para canais digitais acelerada na pandemia, calibrada com Sebrae (2021) e PAC."),
    "phi_multiplicador_segmento": Origem("fonte + ajuste do autor", _URL_PAC_9349,
                                         "Reproduz a ordem real da participação da Internet por segmento na PAC (Eletrônicos ≫ Casa/Moda > Beleza > Alimentos)."),
    "receita_media_2019": Origem("premissa do autor", "", "Receita mensal média por negócio em 2019, com folga em relação aos tetos legais do MEI e da ME."),
    "rho_canal": Origem("premissa do autor", "", "Negócios de canal digital tendem a faturar menos que os da loja física no início."),
    "impulso_digital_ancoras": Origem("premissa do autor", "", "Impulso temporário da demanda digital na pandemia (o choque físico já vem da PMC)."),
    "sigma_ruido_receita": Origem("premissa do autor", "", "Ruído lognormal de 5% na receita mensal."),
    "ticket_2019": Origem("premissa do autor", "", "Ticket típico por segmento e canal em 2019, corrigido pelo preço implícito da PMC."),
    "sigma_ruido_ticket": Origem("premissa do autor", "", "Ruído lognormal de 3% no ticket."),
    "frequencia_compra": Origem("premissa do autor", "", "Pedidos por cliente ativo no mês, sempre ≥ 1,01."),
    "retencao_base": Origem("premissa do autor", "", "Recompra mensal típica: alta no ponto físico de bairro e baixa no marketplace."),
    "retencao_ecommerce_ancoras": Origem("premissa do autor", "", "Retenção do canal próprio cresce com CRM, WhatsApp e recompra direta."),
    "retencao_ajuste_segmento": Origem("premissa do autor", "", "Itens de consumo recorrente (alimentos, beleza) têm mais recompra."),
    "retencao_choque_fisica": Origem("premissa do autor", "", "Fechamento do comércio presencial entre abr e jun/2020."),
    "retencao_limites": Origem("premissa do autor", "", "Limites técnicos da taxa de retenção mensal."),
    "cac_2019": Origem("premissa do autor", "", "Custo de aquisição por cliente novo; o tráfego da loja física é pago pelo aluguel do ponto."),
    "cac_tendencia_real_aa": Origem("premissa do autor", "", "Mais concorrência por mídia paga e anúncios patrocinados nos canais digitais."),
    "sigma_ruido_cac": Origem("premissa do autor", "", "Ruído lognormal de 8% no investimento em marketing."),
    "ml_comissao_pct": Origem("fonte de mercado", _URL_ML, "Comissão do anúncio Clássico do Mercado Livre (11% e depois ponto médio de 10–14%)."),
    "ml_custo_fixo": Origem("fonte de mercado", _URL_ML, "Custo fixo por unidade abaixo do limite de preço, conforme cópias arquivadas da página oficial."),
    "ml_sigma_ln_pedido": Origem("premissa do autor", "", "Dispersão lognormal do valor dos pedidos para estimar a fração abaixo do limite."),
    "taxa_proc_ecommerce_pre_pix": Origem("premissa do autor", "", "Custo médio de cartão e boleto antes do Pix."),
    "taxa_proc_ecommerce_cartao": Origem("fonte de mercado", _URL_NUVEMSHOP, "Processamento do Nuvem Pago no plano Essencial (out/2026)."),
    "taxa_proc_ecommerce_pix": Origem("fonte de mercado", _URL_NUVEMSHOP, "Tarifa do Pix no Nuvem Pago (out/2026)."),
    "inicio_taxa_pix_ecommerce": Origem("fonte oficial", "https://agenciabrasil.ebc.com.br/economia/noticia/2020-11/pix-novo-sistema-de-pagamento-instantaneo-entra-em-funcionamento",
                                        "Pix em funcionamento pleno a partir de 16/11/2020."),
    "pix_ecommerce_ancoras": Origem("premissa do autor", "", "Adoção gradual do Pix no checkout do canal próprio."),
    "mdr_cartao_fisica": Origem("premissa do autor", "", "MDR médio das maquininhas de cartão no varejo de pequeno porte."),
    "pix_fisica_ancoras": Origem("premissa do autor", "", "Adoção gradual do Pix no balcão (sem custo para o lojista)."),
    "frete_medio_2019": Origem("premissa do autor", "", "Frete médio por pedido a preços de 2019."),
    "frete_parcela_vendedor": Origem("premissa do autor", "", "Parcela do frete subsidiada pelo vendedor em cada canal."),
    "cmv_pct_segmento": Origem("fonte + ajuste do autor", _URL_PAC_10645,
                               "CMV ÷ receita líquida de revenda da PAC 2024; Eletrônicos com −7,8 p.p. por predominância de acessórios."),
    "cmv_delta_canal": Origem("premissa do autor", "", "Preço um pouco maior no canal próprio reduz o CMV relativo."),
    "sigma_ruido_cmv": Origem("premissa do autor", "", "Ruído normal de 0,5 p.p. no CMV relativo."),
    "custos_fixos_2019": Origem("premissa do autor", "", "Aluguel e operação do ponto físico; ERP, embalagens e plataforma nos canais digitais."),
    "custos_fixos_mult_segmento": Origem("premissa do autor", "", "Diferenças de espaço e estrutura entre segmentos."),
    "das_pct_salario_minimo": Origem("fonte oficial", "https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm",
                                     "Contribuição previdenciária do MEI de 5% do salário mínimo (Lei 8.212, art. 21)."),
    "das_icms": Origem("fonte oficial", _URL_LC123, "R$ 1,00 de ICMS no DAS do MEI do comércio (LC 123, art. 18-A)."),
    "salario_minimo": Origem("fonte oficial", "http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='MTE12_SALMIN12')",
                             "Salário mínimo vigente mês a mês (Ipeadata)."),
    "simples_anexo_i": Origem("fonte oficial", _URL_LC123, "Faixas do Anexo I do Simples Nacional (comércio), vigência 01/01/2018."),
    "rbt12_inicial": Origem("premissa do autor", "", "O painel não tem histórico anterior a dez/2017; os meses que faltam no RBT12 usam a receita de referência."),
    "teto_receita_mei": Origem("fonte oficial", _URL_LC123, "Teto anual do MEI (LC 123, art. 18-A, §1º)."),
    "teto_receita_me": Origem("fonte oficial", _URL_LC123, "Teto anual da ME (LC 123, art. 3º, I)."),
    "semente_simulacao": Origem("premissa do autor", "", "Semente fixa para reprodutibilidade do painel."),
    "semente_problemas": Origem("premissa do autor", "", "Semente separada para a injeção de problemas de qualidade."),
    "injecao_problemas": Origem("premissa do autor", "", "Proporções dos problemas de qualidade injetados no arquivo bruto."),
}

SEMENTE_SIMULACAO: int = int(PARAMETROS["semente_simulacao"])  # type: ignore[arg-type]
SEMENTE_PROBLEMAS: int = int(PARAMETROS["semente_problemas"])  # type: ignore[arg-type]
TETO_MEI: float = float(PARAMETROS["teto_receita_mei"])  # type: ignore[arg-type]
TETO_ME: float = float(PARAMETROS["teto_receita_me"])  # type: ignore[arg-type]
VERSAO_MODELO = "1.0"


def salario_minimo_em(datas: pd.Series | pd.DatetimeIndex) -> np.ndarray:
    """Salário mínimo vigente em cada data (tabela da seção 2.1).

    Args:
        datas: datas (1º dia do mês).

    Returns:
        Vetor com o salário mínimo de cada data (NaN antes de 2018-01).
    """
    tabela = PARAMETROS["salario_minimo"]
    inicios = pd.to_datetime(list(tabela.keys()))  # type: ignore[union-attr]
    valores = np.array(list(tabela.values()), dtype=float)  # type: ignore[union-attr]
    d = pd.to_datetime(pd.Series(datas)).to_numpy()
    idx = np.searchsorted(inicios.to_numpy(), d, side="right") - 1
    saida = np.where(idx >= 0, valores[np.clip(idx, 0, None)], np.nan)
    return saida


def das_mei_em(datas: pd.Series | pd.DatetimeIndex) -> np.ndarray:
    """Valor mensal do DAS-MEI do comércio: 5% do salário mínimo + R$ 1,00 de ICMS.

    Args:
        datas: datas (1º dia do mês).

    Returns:
        Vetor com o DAS por negócio em cada data.
    """
    sm = salario_minimo_em(datas)
    return PARAMETROS["das_pct_salario_minimo"] * sm + PARAMETROS["das_icms"]  # type: ignore[operator]


# ---------------------------------------------------------------------------
# Arquivo bruto simulado e limpeza (seções 8 e 9)
# ---------------------------------------------------------------------------
MAPA_COLUNAS_BRUTAS: dict[str, str] = {
    "Mês Referência": "mes_referencia",
    "Canal de Venda": "canal",
    "Porte": "porte",
    "Segmento": "segmento",
    "Negócios Ativos": "negocios_ativos",
    "Receita Bruta (R$)": "receita_bruta",
    "Pedidos": "pedidos",
    "Clientes Ativos": "clientes_ativos",
    "Clientes Novos": "clientes_novos",
    "Clientes Recorrentes": "clientes_recorrentes",
    "Clientes Ativos Mês Anterior": "clientes_ativos_mes_anterior",
    "Investimento Marketing (R$)": "investimento_marketing",
    "Comissões e Tarifas (R$)": "comissoes_tarifas",
    "Frete Subsidiado (R$)": "frete_subsidiado",
    "CMV (R$)": "cmv",
    "Custos Fixos (R$)": "custos_fixos",
    "Impostos Fixos - DAS (R$)": "impostos_fixos",
    "Impostos Variáveis - Simples (R$)": "impostos_variaveis",
}
COLUNAS_MEDIDA_BRUTAS: list[str] = list(MAPA_COLUNAS_BRUTAS.values())[4:]
COLUNAS_CONTAGEM: list[str] = [
    "negocios_ativos", "pedidos", "clientes_ativos", "clientes_novos", "clientes_recorrentes", "clientes_ativos_mes_anterior",
]
COLUNAS_MONETARIAS: list[str] = [c for c in COLUNAS_MEDIDA_BRUTAS if c not in COLUNAS_CONTAGEM]
CHAVE_PAINEL: list[str] = ["data", "canal", "porte", "segmento"]
CHAVE_SERIE: list[str] = ["canal", "porte", "segmento"]

FORMATOS_DATA_BRUTA: list[str] = ["AAAA-MM", "MM/AAAA", "AAAA-MM-01"]

# Variantes de rótulo injetadas no bruto (seção 8, passo 2)
VARIANTES_ROTULOS: dict[str, dict[str, list[str]]] = {
    "canal": {
        "Loja Física": ["loja fisica", "LOJA FÍSICA ", "Físico", "Loja física"],
        "Marketplace": ["marketplace ", "MKT", "Mkt place", "MARKETPLACE"],
        "E-commerce Próprio": ["E-commerce próprio", "ecommerce proprio", "Loja Virtual Própria", "E-COMMERCE PRÓPRIO"],
    },
    "porte": {
        "MEI": ["mei", "Microempreendedor Individual"],
        "ME": ["me", "Microempresa"],
    },
    "segmento": {
        "Moda e Acessórios": ["moda e acessorios", "  Moda e  Acessórios "],
        "Casa e Decoração": ["casa e decoracao", "  Casa e  Decoração "],
        "Eletrônicos e Acessórios": ["eletronicos e acessorios", "  Eletrônicos e  Acessórios "],
        "Beleza e Cuidados Pessoais": ["beleza e cuidados pessoais", "  Beleza e  Cuidados Pessoais "],
        "Alimentos e Bebidas": ["alimentos e bebidas", "  Alimentos e  Bebidas "],
    },
}

# Mapa de rótulos normalizados → rótulo canônico (seção 9.2, passo 4)
MAPA_ROTULOS: dict[str, dict[str, str]] = {
    "canal": {
        "loja fisica": "Loja Física",
        "fisico": "Loja Física",
        "fisica": "Loja Física",
        "marketplace": "Marketplace",
        "mkt": "Marketplace",
        "mkt place": "Marketplace",
        "e commerce proprio": "E-commerce Próprio",
        "ecommerce proprio": "E-commerce Próprio",
        "loja virtual propria": "E-commerce Próprio",
    },
    "porte": {
        "mei": "MEI",
        "microempreendedor individual": "MEI",
        "me": "ME",
        "microempresa": "ME",
    },
    "segmento": {
        "moda e acessorios": "Moda e Acessórios",
        "casa e decoracao": "Casa e Decoração",
        "eletronicos e acessorios": "Eletrônicos e Acessórios",
        "beleza e cuidados pessoais": "Beleza e Cuidados Pessoais",
        "alimentos e bebidas": "Alimentos e Bebidas",
    },
}

# ---------------------------------------------------------------------------
# Medidas, KPIs e contrato do CSV final (seções 10 e 12)
# ---------------------------------------------------------------------------
MEDIDAS_ADITIVAS: list[str] = [
    "negocios_ativos", "receita_bruta", "receita_bruta_real", "pedidos", "clientes_ativos", "clientes_novos",
    "clientes_recorrentes", "clientes_ativos_mes_anterior", "investimento_marketing", "comissoes_tarifas",
    "frete_subsidiado", "cmv", "custos_fixos", "impostos_fixos", "impostos_variaveis", "impostos",
    "margem_contribuicao", "margem_liquida", "margem_liquida_real",
]
KPIS: list[str] = [
    "ticket_medio", "ticket_medio_real", "frequencia_compra", "cac", "take_rate", "margem_contribuicao_pct",
    "margem_liquida_pct", "taxa_retencao", "tempo_vida_meses", "ltv", "ltv_cac", "payback_cac_meses",
    "receita_por_negocio", "ponto_equilibrio_receita", "folga_ponto_equilibrio_pct", "flag_pe_inviavel",
]
COLUNAS_MACRO: list[str] = [
    "pmc_indice_volume_varejo_sa", "pmc_indice_volume_segmento", "pmc_indice_receita_segmento",
    "ipca_variacao_mensal", "ipca_indice", "deflator_ipca", "fonte_ipca",
]
COLUNAS_CSV_FINAL: list[str] = (
    ["data", "ano", "mes", "ano_mes", "trimestre", "fase", "fase_ordem", "recorte_temporal", "recorte_ordem",
     "flag_cenario_atual", "canal", "canal_codigo", "porte", "segmento", "segmento_codigo", "atividade_pmc_referencia",
     "negocios_ativos", "receita_bruta", "receita_bruta_real", "pedidos", "clientes_ativos", "clientes_novos",
     "clientes_recorrentes", "clientes_ativos_mes_anterior", "investimento_marketing", "comissoes_tarifas",
     "frete_subsidiado", "cmv", "custos_fixos", "impostos_fixos", "impostos_variaveis", "impostos",
     "margem_contribuicao", "margem_liquida", "margem_liquida_real"]
    + KPIS
    + COLUNAS_MACRO
    + ["qtd_campos_imputados"]
)
COLUNAS_INTEIRAS: list[str] = [
    "ano", "mes", "trimestre", "fase_ordem", "recorte_ordem", "flag_cenario_atual", "negocios_ativos", "pedidos",
    "clientes_ativos", "clientes_novos", "clientes_recorrentes", "clientes_ativos_mes_anterior", "flag_pe_inviavel",
    "qtd_campos_imputados",
]
COLUNAS_TEXTO: list[str] = [
    "ano_mes", "fase", "recorte_temporal", "canal", "canal_codigo", "porte", "segmento", "segmento_codigo",
    "atividade_pmc_referencia", "fonte_ipca",
]
COLUNAS_MOEDA_FINAL: list[str] = [
    "receita_bruta", "receita_bruta_real", "investimento_marketing", "comissoes_tarifas", "frete_subsidiado", "cmv",
    "custos_fixos", "impostos_fixos", "impostos_variaveis", "impostos", "margem_contribuicao", "margem_liquida",
    "margem_liquida_real",
]
COLUNAS_ANULAVEIS: list[str] = ["ponto_equilibrio_receita", "folga_ponto_equilibrio_pct"]

# Faixas de sanidade linha a linha (seção 10.3): (mínimo, máximo, inclui_min, inclui_max)
FAIXAS_KPI: dict[str, tuple[float, float, bool, bool]] = {
    "ticket_medio": (5.0, 2000.0, False, False),
    "frequencia_compra": (1.0, np.inf, True, False),
    "cac": (0.0, 500.0, False, False),
    "take_rate": (0.0, 0.50, True, True),
    "taxa_retencao": (0.0, 1.0, True, False),
    "margem_contribuicao_pct": (0.0, 0.70, False, False),
    "margem_liquida_pct": (-3.00, 0.50, False, False),
    "ltv_cac": (0.0, 60.0, False, False),
    "payback_cac_meses": (0.0, 24.0, False, False),
}

# Checagens de calibração (seção 7.9)
CALIBRACAO: dict[str, dict[str, object]] = {
    "C1": {"metrica": "Multiplicador da receita digital nominal 2019→2024 (Marketplace + Próprio)", "min": 3.21, "max": 13.4,
           "referencia": "PAC Internet 20+ PO (217,91 ÷ 67,79 = 3,21); MDIC, MPE (67 ÷ 5 = 13,4)",
           "fonte": "IBGE PAC 9349/10656; MDIC (2025)"},
    "C2": {"metrica": "Razão da participação digital 2021 ÷ 2019", "min": 1.87, "max": 4.0,
           "referencia": "PAC (9,84 ÷ 5,26 = 1,87); teto = premissa", "fonte": "IBGE PAC 9349"},
    "C3": {"metrica": "Variação da receita real da Loja Física, abr/2020 vs fev/2020", "min": -np.inf, "max": -0.15,
           "referencia": "PMC 8880 volume com ajuste: −19,7%", "fonte": "IBGE PMC 8880"},
    "C4": {"metrica": "Variação da receita real digital, abr/2020 vs fev/2020", "min": 0.0, "max": np.inf,
           "referencia": "migração para o digital", "fonte": "Sebrae (2021)"},
    "C5": {"metrica": "Participação digital na receita real no Cenário Atual (2025–2026)", "min": 0.25, "max": 0.45,
           "referencia": "1/3 dos MEI online com > 50% do faturamento online; faixa = premissa", "fonte": "Sebrae (2021)"},
    "C6": {"metrica": "Take rate do Marketplace no Cenário Atual (2025–2026)", "min": 0.10, "max": 0.19,
           "referencia": "faixas Clássico (10–14%) e Premium (15–19%) do Mercado Livre", "fonte": "Mercado Livre (2026)"},
}

# Matriz de recomendação: limiar de materialidade em pontos percentuais de R_ref (premissa do autor)
LIMIAR_RECOMENDACAO_PP: float = 1.0

# Tarifas oficiais vigentes em out/2026 (seção 11)
TARIFAS_2026: dict[str, object] = {
    "ml_classico": {"pct": 0.12, "fixo": 6.0, "limite": 79.0},
    "shopee_cnpj": [
        {"de": 0.0, "pct": 0.20, "fixo": 4.50},
        {"de": 80.0, "pct": 0.14, "fixo": 16.0},
        {"de": 100.0, "pct": 0.14, "fixo": 20.0},
        {"de": 200.0, "pct": 0.14, "fixo": 26.0},
    ],
    "amazon_individual": {"pct": 0.125, "fixo": 2.0},
    "amazon_profissional": {"pct": 0.125, "mensalidade": 19.0},
}
TARIFAS_GRADE: tuple[int, int] = (20, 500)
TARIFAS_PONTOS: list[float] = [30.0, 50.0, 79.99, 80.0, 99.99, 100.0, 150.0, 199.99, 200.0, 300.0, 500.0]
TARIFAS_PLATAFORMAS: list[dict[str, str]] = [
    {"chave": "ml_classico", "plataforma": "Mercado Livre", "plano": "Clássico",
     "observacao": "faixa oficial de 10% a 14% por categoria (ponto médio de 12%) + R$ 6 abaixo de R$ 79; frete à parte"},
    {"chave": "shopee_cnpj", "plataforma": "Shopee", "plano": "CNPJ",
     "observacao": "inclui taxa de transação e Programa de Frete Grátis; subsídio Pix de 5% (até 8% acima de R$ 500) "
                   "não incluído no cálculo, pois é desconto ao comprador custeado pela plataforma"},
    {"chave": "amazon_individual", "plataforma": "Amazon", "plano": "Individual",
     "observacao": "comissão de 10% a 15% por categoria (ponto médio de 12,5%) + R$ 2 por produto vendido; frete à parte"},
    {"chave": "amazon_profissional", "plataforma": "Amazon", "plano": "Profissional",
     "observacao": "comissão de 12,5% (ponto médio) + R$ 19/mês fora da tarifa por item (a partir do 13º mês); frete à parte"},
]

# ---------------------------------------------------------------------------
# Visualização (seção 13)
# ---------------------------------------------------------------------------
CORES_CANAIS: dict[str, str] = {"Loja Física": "#2E86AB", "Marketplace": "#F18F01", "E-commerce Próprio": "#3BB273"}
MARCADORES_PORTE: dict[str, str] = {"MEI": "o", "ME": "^"}
COR_FASE_PANDEMIA = "#BDBDBD"
COR_FASE_ATUAL = "#9ECAE1"
DPI_GRAFICOS: int = 160
TAMANHO_PADRAO: tuple[float, float] = (12.0, 6.5)
DATA_CONSULTA_TARIFAS = "18/10/2026"
ARQUIVOS_GRAFICOS: list[str] = [
    "01_receita_real_por_canal.png",
    "02_participacao_canal_por_fase.png",
    "03_composicao_custos_margem_por_canal.png",
    "04_dispersao_cac_ltv.png",
    "05_ticket_medio_canal_fase.png",
    "06_taxa_retencao_tempo.png",
    "07_take_rate_marketplace_vs_cac_ecommerce.png",
    "08_heatmap_margem_canal_porte.png",
    "09_contexto_macro_real.png",
    "10_ponto_equilibrio_canal.png",
]
