"""Visualização: geração automática dos 10 gráficos analíticos em PNG (Matplotlib/Seaborn).

Cada gráfico lê apenas as tabelas de apoio construídas na transformação, usa títulos, eixos e
legendas em português, formatação numérica brasileira, cores fixas por canal e rodapé de fonte.
Os gráficos temporais marcam as fases (Pandemia e Cenário Atual sombreados) e os marcos da OMS e
do fim da ESPIN; o Pix aparece nos gráficos 01, 06 e 07(a).
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.transforms as mtransforms  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, MultipleLocator, NullFormatter  # noqa: E402

from src import config  # noqa: E402

logger = logging.getLogger(__name__)

ROTULOS_COMPONENTES = {
    "cmv": "CMV",
    "comissoes_tarifas": "Comissões/tarifas",
    "frete_subsidiado": "Frete subsidiado",
    "investimento_marketing": "Marketing",
    "custos_fixos": "Custos fixos",
    "impostos": "Impostos",
    "margem_liquida": "Margem líquida",
}
CORES_COMPONENTES = {
    "cmv": "#8C96A5",
    "comissoes_tarifas": "#E59866",
    "frete_subsidiado": "#F7DC6F",
    "investimento_marketing": "#BB8FCE",
    "custos_fixos": "#85C1E9",
    "impostos": "#D98880",
}
COR_MARGEM_POSITIVA = "#1E7B45"
COR_MARGEM_NEGATIVA = "#C0392B"
CORES_SEGMENTOS = {
    "moda": "#8E44AD", "casa": "#B9770E", "eletronicos": "#1F618D", "beleza": "#C2185B", "alimentos": "#117864",
}
MARCADORES_SEGMENTOS = {"moda": "o", "casa": "s", "eletronicos": "D", "beleza": "^", "alimentos": "v"}
ABREV_CANAL = {"Loja Física": "Física", "Marketplace": "Marketplace", "E-commerce Próprio": "Próprio"}
_ESTADO: dict[str, str] = {"mes_base": "mês-base"}


# ---------------------------------------------------------------------------
# Estilo e formatação
# ---------------------------------------------------------------------------
def configurar_estilo() -> None:
    """Aplica o tema padrão dos gráficos (seaborn whitegrid, DejaVu Sans, fundo branco)."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "figure.figsize": config.TAMANHO_PADRAO,
        "figure.dpi": 100,
        "savefig.dpi": config.DPI_GRAFICOS,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "legend.fontsize": 9.5,
        "legend.framealpha": 0.92,
    })


def _br(x: float, casas: int = 1) -> str:
    """Formata um número no padrão brasileiro (ponto de milhar e vírgula decimal).

    Args:
        x: número.
        casas: casas decimais.

    Returns:
        Texto formatado.
    """
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_moeda(x: float, pos: int | None = None) -> str:
    """Formatador de eixo em reais abreviados ("R$ 1,2 mi", "R$ 350 mil", "R$ 950").

    Args:
        x: valor em R$.
        pos: posição do tick (exigida pelo ``FuncFormatter``).

    Returns:
        Texto do tick.
    """
    if x < 0:
        return "-" + formatar_moeda(-x)
    a = abs(x)
    if a >= 1e6:
        return f"R$ {_br(x / 1e6, 1)} mi"
    if a >= 1e4:
        return f"R$ {_br(x / 1e3, 0)} mil"
    if a >= 1e3:
        return f"R$ {_br(x / 1e3, 0 if float(x / 1e3).is_integer() else 1)} mil"
    return f"R$ {_br(x, 0)}"


def formatar_pct(x: float, pos: int | None = None, casas: int = 1) -> str:
    """Formatador de fração como percentual brasileiro ("12,5%").

    Args:
        x: fração (0,125 = 12,5%).
        pos: posição do tick.
        casas: casas decimais.

    Returns:
        Texto do tick.
    """
    if abs(x) < 1e-9:
        x = 0.0  # evita "-0%" por ruído de ponto flutuante
    return f"{_br(x * 100, casas)}%"


def formatar_milhar(x: float, pos: int | None = None) -> str:
    """Formatador com ponto de milhar ("1.234").

    Args:
        x: número.
        pos: posição do tick.

    Returns:
        Texto do tick.
    """
    return _br(x, 0)


def _rodape(fig: plt.Figure, tipo: str, fonte_ipca: str) -> None:
    """Acrescenta o rodapé de fonte ao gráfico.

    Args:
        fig: figura.
        tipo: ``simulado``, ``real`` ou ``tarifas``.
        fonte_ipca: rótulo da fonte do IPCA.
    """
    textos = {
        "simulado": f"Fonte: painel simulado calibrado com dados do IBGE (PMC/PAC) e IPCA ({fonte_ipca}). Elaboração própria.",
        "real": f"Fonte: IBGE — PMC (tabela 8880), PAC (tabelas 9349 e 10656) e IPCA ({fonte_ipca}). Elaboração própria.",
        "tarifas": f"Fonte: páginas oficiais de tarifas (Mercado Livre, Shopee, Amazon), consulta em {config.DATA_CONSULTA_TARIFAS}.",
        "simulado_tarifas": (f"Fonte: (a) painel simulado calibrado com dados do IBGE (PMC/PAC) e IPCA ({fonte_ipca}); "
                             f"(b) páginas oficiais de tarifas (Mercado Livre, Shopee, Amazon), consulta em "
                             f"{config.DATA_CONSULTA_TARIFAS}. Elaboração própria."),
    }
    fig.text(0.01, 0.005, textos[tipo], fontsize=8, color="#666666", ha="left", va="bottom")


def _salvar(fig: plt.Figure, destino: Path) -> Path:
    """Salva a figura em PNG e fecha.

    Args:
        fig: figura.
        destino: caminho do PNG.

    Returns:
        Caminho gravado.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=config.DPI_GRAFICOS, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    logger.info("Gráfico gravado: %s", config.caminho_relativo(destino))
    return destino


def sombrear_fases(ax: plt.Axes, com_pix: bool = False) -> None:
    """Sombreia a Pandemia e o Cenário Atual, rotula as fases e marca OMS, fim da ESPIN e (opcional) Pix.

    Deve ser chamada depois de plotar os dados (usa os limites do eixo x).

    Args:
        ax: eixo temporal.
        com_pix: acrescenta a linha pontilhada do Pix (16/11/2020).
    """
    x0, x1 = ax.get_xlim()
    ini_pand = mdates.date2num(config.INICIO_PANDEMIA)
    ini_pos = mdates.date2num(config.INICIO_POS_PANDEMIA)
    ini_atual = mdates.date2num(config.INICIO_CENARIO_ATUAL)
    ax.axvspan(ini_pand, ini_pos, color=config.COR_FASE_PANDEMIA, alpha=0.25, zorder=0, lw=0)
    ax.axvspan(ini_atual, x1, color=config.COR_FASE_ATUAL, alpha=0.20, zorder=0, lw=0)
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    for ini, fim, rotulo in ((x0, ini_pand, "Pré-pandemia"), (ini_pand, ini_pos, "Pandemia"),
                             (ini_pos, ini_atual, "Pós-pandemia"), (ini_atual, x1, "Cenário Atual")):
        ax.text((ini + fim) / 2, 1.012, rotulo, transform=trans, ha="center", va="bottom", fontsize=8.5,
                color="#444444", fontweight="bold" if rotulo in ("Pandemia", "Cenário Atual") else "normal")
    marcos = [("2020-03-11", "OMS: pandemia", "--"), ("2022-05-22", "Fim da ESPIN", "--")]
    if com_pix:
        marcos.insert(1, ("2020-11-16", "Pix", ":"))
    for data, rotulo, estilo in marcos:
        x = mdates.date2num(pd.Timestamp(data))
        ax.axvline(x, color="#555555", ls=estilo, lw=1.1, zorder=1)
        ax.text(x, 0.015, f" {rotulo}", transform=trans, rotation=90, ha="right", va="bottom", fontsize=7.5, color="#444444")
    ax.set_xlim(x0, x1)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def _limitar_datas(ax: plt.Axes, datas: pd.Series) -> None:
    """Ajusta o eixo x temporal ao intervalo dos dados (com folga de meio mês).

    Args:
        ax: eixo temporal.
        datas: datas plotadas.
    """
    ax.set_xlim(pd.Timestamp(datas.min()) - pd.Timedelta(days=20), pd.Timestamp(datas.max()) + pd.Timedelta(days=20))


def _mm3_razao(sub: pd.DataFrame, num: str, den: str) -> pd.Series:
    """Média móvel de 3 meses de uma razão, como razão das somas móveis.

    Args:
        sub: série mensal de um canal (ordenada por data).
        num: numerador.
        den: denominador.

    Returns:
        Série Σ3 num ÷ Σ3 den.
    """
    return sub[num].rolling(3).sum() / sub[den].rolling(3).sum()


def _exigir(tabelas: dict[str, pd.DataFrame], chave: str) -> pd.DataFrame:
    """Lê uma tabela do dicionário, com erro claro se faltar.

    Args:
        tabelas: tabelas de apoio.
        chave: nome da tabela.

    Returns:
        Tabela.

    Raises:
        KeyError: chave ausente.
    """
    if chave not in tabelas:
        raise KeyError(chave)
    return tabelas[chave]


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def grafico_01_receita_real_por_canal(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 01: receita real mensal por canal (série fina + média móvel de 3 meses)."""
    sm = _exigir(tabelas, "serie_mensal_canal")
    mes_base = config.rotulo_mes_base(sm["data"].max())
    fig, ax = plt.subplots(figsize=config.TAMANHO_PADRAO)
    for canal in config.CANAIS:
        sub = sm[sm["canal"] == canal].sort_values("data")
        cor = config.CORES_CANAIS[canal]
        ax.plot(sub["data"], sub["receita_bruta_real"], color=cor, alpha=0.35, lw=1.0)
        ax.plot(sub["data"], sub["receita_bruta_real"].rolling(3).mean(), color=cor, lw=2.4, label=f"{canal} (média móvel de 3 meses)")
    ax.yaxis.set_major_formatter(FuncFormatter(formatar_moeda))
    ax.set_ylabel(f"Receita real mensal (R$ de {mes_base})")
    ax.set_xlabel("Mês")
    ax.set_ylim(bottom=0)
    _limitar_datas(ax, sm["data"])
    sombrear_fases(ax, com_pix=True)
    ax.set_title("Evolução da receita real por canal de venda (2018–2026)", pad=24)
    h, lab = ax.get_legend_handles_labels()
    h.append(Line2D([], [], color="#777777", alpha=0.35, lw=1.0))
    lab.append("Série mensal (linhas finas)")
    ax.legend(h, lab, loc="upper right", bbox_to_anchor=(0.995, 0.985), ncol=2, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    _rodape(fig, "simulado", fonte_ipca)
    return _salvar(fig, destino)


def grafico_02_participacao_canal_por_fase(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 02: participação dos canais na receita real por recorte (barras 100% empilhadas)."""
    rc = _exigir(tabelas, "kpis_recorte_canal")
    piv = rc.pivot_table(index="recorte_ordem", columns="canal", values="participacao_canal", aggfunc="first")
    piv = piv.reindex(columns=config.CANAIS).sort_index()
    rotulos = [config.RECORTES[i - 1].replace(" (", "\n(") for i in piv.index]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    base = np.zeros(len(piv))
    for canal in config.CANAIS:
        vals = piv[canal].to_numpy(copy=True)
        ax.bar(rotulos, vals, bottom=base, color=config.CORES_CANAIS[canal], label=canal, width=0.62, edgecolor="white")
        for i, v in enumerate(vals):
            if v >= 0.03:
                ax.text(i, base[i] + v / 2, formatar_pct(v), ha="center", va="center", fontsize=10.5,
                        color="white", fontweight="bold")
        base += vals
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: formatar_pct(x, p, 0)))
    ax.set_ylim(0, 1)
    ax.set_ylabel("Participação na receita real")
    ax.set_xlabel("Recorte temporal")
    ax.set_title("Participação dos canais na receita real, por fase")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, frameon=False)
    ax.grid(axis="x", visible=False)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    _rodape(fig, "simulado", fonte_ipca)
    return _salvar(fig, destino)


def grafico_03_composicao_custos_margem_por_canal(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 03: composição de custos e margem líquida em % da receita, Cenário Atual, MEI | ME."""
    comp = _exigir(tabelas, "composicao_custos_atual")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), sharey=True)
    for ax, porte in zip(axes, config.PORTES):
        sub = comp[comp["porte"] == porte]
        for i, canal in enumerate(config.CANAIS):
            linha = sub[sub["canal"] == canal].set_index("componente")["pct_receita"]
            esquerda = 0.0
            for comp_nome in ROTULOS_COMPONENTES:
                v = float(linha[comp_nome])
                if comp_nome == "margem_liquida":
                    cor = COR_MARGEM_POSITIVA if v >= 0 else COR_MARGEM_NEGATIVA
                    largura = abs(v)
                else:
                    cor = CORES_COMPONENTES[comp_nome]
                    largura = v
                ax.barh(i, largura, left=esquerda, color=cor, edgecolor="white", height=0.62)
                if comp_nome == "margem_liquida":
                    # Rótulo da margem fora da barra, para não colidir com blocos estreitos
                    ax.text(esquerda + largura + 0.008, i, formatar_pct(v), ha="left", va="center", fontsize=9.5,
                            color=cor, fontweight="bold")
                elif largura >= 0.045:
                    claro = comp_nome in ("frete_subsidiado", "custos_fixos", "investimento_marketing", "comissoes_tarifas")
                    ax.text(esquerda + largura / 2, i, formatar_pct(v), ha="center", va="center", fontsize=9,
                            color="#222222" if claro else "white", fontweight="bold")
                esquerda += largura
        ax.set_yticks(range(len(config.CANAIS)), config.CANAIS)
        ax.invert_yaxis()
        ax.set_xlim(0, 1.09)
        ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: formatar_pct(x, p, 0)))
        ax.set_title(porte, fontsize=12)
        ax.set_xlabel("% da receita bruta")
        ax.grid(axis="y", visible=False)
    handles = [Patch(color=CORES_COMPONENTES[c], label=ROTULOS_COMPONENTES[c]) for c in CORES_COMPONENTES]
    handles.append(Patch(color=COR_MARGEM_POSITIVA, label="Margem líquida (≥ 0)"))
    handles.append(Patch(color=COR_MARGEM_NEGATIVA, label="Margem líquida (< 0)"))
    fig.legend(handles=handles, loc="lower center", ncol=8, bbox_to_anchor=(0.5, 0.035), frameon=False, fontsize=9)
    fig.suptitle("Composição de custos e margem líquida por canal — Cenário Atual (2025–2026)", fontweight="bold", fontsize=13)
    fig.tight_layout(rect=(0, 0.1, 1, 0.97))
    _rodape(fig, "simulado", fonte_ipca)
    return _salvar(fig, destino)


def grafico_04_dispersao_cac_ltv(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 04: dispersão CAC × LTV (log-log), Cenário Atual, com retas LTV = CAC e LTV = 3 × CAC."""
    t = _exigir(tabelas, "kpis_atual_canal_porte_segmento").copy()
    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    for canal in config.CANAIS:
        for porte in config.PORTES:
            sub = t[(t["canal"] == canal) & (t["porte"] == porte)]
            ax.scatter(sub["cac"], sub["ltv"], color=config.CORES_CANAIS[canal], marker=config.MARCADORES_PORTE[porte],
                       s=85, edgecolor="#222222", linewidth=0.6, zorder=3)
    xmin, xmax = t["cac"].min() / 1.1, t["cac"].max() * 1.1
    ymin, ymax = t["ltv"].min() / 1.6, t["ltv"].max() * 1.1
    xs = np.geomspace(xmin, xmax, 100)
    ax.plot(xs, xs, color="#888888", ls=":", lw=1.4, zorder=2)
    ax.plot(xs, 3 * xs, color="black", ls="--", lw=1.4, zorder=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ticks_x = [v for v in (1, 2, 3, 5, 10, 20, 30, 50, 100) if xmin <= v <= xmax]
    ticks_y = [v for v in (5, 10, 20, 30, 50, 100, 200) if ymin <= v <= ymax]
    ax.xaxis.set_major_locator(FixedLocator(ticks_x))
    ax.yaxis.set_major_locator(FixedLocator(ticks_y))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"R$ {_br(x, 0)}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"R$ {_br(x, 0)}"))
    ax.set_xlabel("CAC — custo de aquisição por cliente novo (R$, escala log)")
    ax.set_ylabel("LTV — valor do cliente no tempo de vida (R$, escala log)")
    ax.set_title("CAC × LTV por canal, porte e segmento — Cenário Atual (2025–2026)")
    # Rótulos dos 3 pontos extremos
    escolhidos = []
    for idx in (t["ltv_cac"].idxmax(), t["ltv_cac"].idxmin(), t["cac"].idxmax()):
        if idx not in escolhidos:
            escolhidos.append(idx)
    if len(escolhidos) < 3:
        for idx in t.sort_values("cac").index:
            if idx not in escolhidos:
                escolhidos.append(idx)
                break
    for idx in escolhidos:
        r = t.loc[idx]
        texto = f"{r['segmento'].split(' e ')[0]} · {ABREV_CANAL[r['canal']]} · {r['porte']}\nLTV/CAC = {_br(r['ltv_cac'], 1)}"
        ax.annotate(texto, (r["cac"], r["ltv"]), xytext=(10, -4), textcoords="offset points", fontsize=8.5,
                    bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#BBBBBB", "alpha": 0.9})
    handles = [Line2D([], [], marker="o", ls="", color=config.CORES_CANAIS[c], markeredgecolor="#222222", markersize=9, label=c)
               for c in config.CANAIS]
    handles += [Line2D([], [], marker=config.MARCADORES_PORTE[p], ls="", color="#BBBBBB", markeredgecolor="#222222",
                       markersize=9, label=p) for p in config.PORTES]
    handles += [Line2D([], [], color="black", ls="--", label="LTV = 3 × CAC (referência)"),
                Line2D([], [], color="#888888", ls=":", label="LTV = CAC")]
    ax.legend(handles=handles, loc="lower right", ncol=2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    _rodape(fig, "simulado", fonte_ipca)
    return _salvar(fig, destino)


def grafico_05_ticket_medio_canal_fase(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 05: ticket médio real por canal e recorte (barras agrupadas)."""
    rc = _exigir(tabelas, "kpis_recorte_canal")
    mes_base = _ESTADO["mes_base"]
    fig, ax = plt.subplots(figsize=(12, 6.5))
    largura = 0.26
    x = np.arange(len(config.RECORTES))
    for j, canal in enumerate(config.CANAIS):
        sub = rc[rc["canal"] == canal].set_index("recorte_ordem").reindex(range(1, 5))
        vals = sub["ticket_medio_real"].to_numpy(copy=True)
        barras = ax.bar(x + (j - 1) * largura, vals, width=largura, color=config.CORES_CANAIS[canal], label=canal, edgecolor="white")
        for b, v in zip(barras, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"R$ {_br(v, 0)}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x, [r.replace(" (", "\n(") for r in config.RECORTES])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"R$ {_br(v, 0)}"))
    ax.set_ylabel(f"Ticket médio real (R$ de {mes_base})")
    ax.set_xlabel("Recorte temporal")
    ax.set_ylim(0, rc["ticket_medio_real"].max() * 1.15)
    ax.set_title("Ticket médio real por canal e fase")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, frameon=False)
    ax.grid(axis="x", visible=False)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    _rodape(fig, "simulado", fonte_ipca)
    return _salvar(fig, destino)


def grafico_06_taxa_retencao_tempo(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 06: taxa de retenção mensal por canal (média móvel de 3 meses por razão de somas)."""
    sm = _exigir(tabelas, "serie_mensal_canal")
    fig, ax = plt.subplots(figsize=config.TAMANHO_PADRAO)
    for canal in config.CANAIS:
        sub = sm[sm["canal"] == canal].sort_values("data")
        ax.plot(sub["data"], _mm3_razao(sub, "clientes_recorrentes", "clientes_ativos_mes_anterior"),
                color=config.CORES_CANAIS[canal], lw=2.4, label=canal)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: formatar_pct(x, p, 0)))
    ax.set_ylim(0, 0.5)
    ax.set_ylabel("Taxa de retenção mensal (média móvel de 3 meses)")
    ax.set_xlabel("Mês")
    _limitar_datas(ax, sm["data"])
    sombrear_fases(ax, com_pix=True)
    ax.set_title("Taxa de retenção mensal de clientes por canal", pad=24)
    ax.legend(loc="upper left", bbox_to_anchor=(0.005, 0.93))
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    _rodape(fig, "simulado", fonte_ipca)
    return _salvar(fig, destino)


def grafico_07_take_rate_marketplace_vs_cac_ecommerce(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 07: (a) take rate do marketplace × custos do canal próprio; (b) take rate oficial 2026 × valor do item."""
    sm = _exigir(tabelas, "serie_mensal_canal")
    tar = _exigir(tabelas, "tarifas_marketplaces_2026")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 11.5), gridspec_kw={"height_ratios": [1, 1], "hspace": 0.42})
    mkt = sm[sm["canal"] == "Marketplace"].sort_values("data")
    eco = sm[sm["canal"] == "E-commerce Próprio"].sort_values("data")
    ax1.plot(mkt["data"], _mm3_razao(mkt, "comissoes_tarifas", "receita_bruta"), color=config.CORES_CANAIS["Marketplace"], lw=2.4,
             label="Marketplace: take rate (comissões e tarifas ÷ receita)")
    ax1.plot(eco["data"], _mm3_razao(eco, "investimento_marketing", "receita_bruta"), color=config.CORES_CANAIS["E-commerce Próprio"],
             lw=2.4, label="E-commerce Próprio: custo de aquisição (marketing ÷ receita)")
    ax1.plot(eco["data"], _mm3_razao(eco, "comissoes_tarifas", "receita_bruta"), color=config.CORES_CANAIS["E-commerce Próprio"],
             lw=1.8, ls="--", label="E-commerce Próprio: tarifas de pagamento/plataforma ÷ receita")
    ax1.yaxis.set_major_locator(MultipleLocator(0.02))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: formatar_pct(x, p, 0)))
    ax1.set_ylim(0, 0.20)
    ax1.set_ylabel("% da receita (média móvel de 3 meses)")
    ax1.set_xlabel("Mês")
    _limitar_datas(ax1, mkt["data"])
    sombrear_fases(ax1, com_pix=True)
    ax1.set_title("(a) Painel simulado: comissão do marketplace × custos do canal próprio", pad=24, fontsize=12)
    ax1.legend(loc="center right", bbox_to_anchor=(0.995, 0.355), fontsize=9)

    grade = tar[tar["tipo_ponto"] == "grade"]
    ax2.axhspan(0.10, 0.14, color=config.CORES_CANAIS["Marketplace"], alpha=0.12, lw=0,
                label="Mercado Livre Clássico: faixa oficial de 10% a 14% por categoria")
    estilos = [("Mercado Livre", "Clássico", "#F18F01", "-"), ("Shopee", "CNPJ", "#D35400", "-"), ("Amazon", "Individual", "#34495E", "-")]
    for plat, plano, cor, ls in estilos:
        sub = grade[(grade["plataforma"] == plat) & (grade["plano"] == plano)].sort_values("valor_item")
        cor_linha = "#EE4D2D" if plat == "Shopee" else cor
        ax2.plot(sub["valor_item"], sub["take_rate"], color=cor_linha, lw=2.2, ls=ls, label=f"{plat} {plano}", drawstyle="default")
    for v in (80, 100, 200):
        ax2.axvline(v, color="#EE4D2D", lw=0.8, ls=":", alpha=0.7)
    ax2.set_xlim(20, 500)
    ax2.set_ylim(0, 0.45)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: formatar_pct(x, p, 0)))
    ax2.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"R$ {_br(x, 0)}"))
    ax2.set_xlabel("Valor do item (R$)")
    ax2.set_ylabel("Take rate efetivo (% do valor do item)")
    ax2.set_title(f"(b) Regras oficiais vigentes (consulta em {config.DATA_CONSULTA_TARIFAS}): take rate efetivo × valor do item",
                  fontsize=12)
    ax2.legend(loc="upper right", fontsize=9)
    ax2.text(0.99, 0.74, "Shopee: inclui transação e frete grátis; subsídio Pix não incluído\n"
             "(desconto ao comprador custeado pela plataforma). Degraus em R$ 80, R$ 100 e R$ 200.",
             transform=ax2.transAxes, ha="right", va="top", fontsize=8.5, color="#333333",
             bbox={"boxstyle": "round,pad=0.35", "fc": "white", "ec": "#CCCCCC"})
    fig.suptitle("Take rate do marketplace × custo de aquisição do e-commerce próprio", fontweight="bold", fontsize=13.5, y=0.995)
    fig.subplots_adjust(top=0.92, bottom=0.07)
    _rodape(fig, "simulado_tarifas", fonte_ipca)
    return _salvar(fig, destino)


def grafico_08_heatmap_margem_canal_porte(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 08: heatmaps da margem líquida % (canal × porte), Pré-pandemia | Cenário Atual, escala comum."""
    rcp = _exigir(tabelas, "kpis_recorte_canal_porte")
    recortes = [config.RECORTE_PRE, config.RECORTE_ATUAL]
    matrizes = []
    for rec in recortes:
        sub = rcp[rcp["recorte_temporal"] == rec]
        m = sub.pivot_table(index="canal", columns="porte", values="margem_liquida_pct", aggfunc="first")
        matrizes.append(m.reindex(index=config.CANAIS, columns=config.PORTES))
    limite = max(float(np.nanmax(np.abs(m.to_numpy()))) for m in matrizes)
    limite = float(np.ceil(limite * 100) / 100)
    fig = plt.figure(figsize=(13, 5.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.05], wspace=0.25)
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    cax = fig.add_subplot(gs[0, 2])
    for i, (ax, m, rec) in enumerate(zip(axes, matrizes, recortes)):
        anot = m.map(lambda v: formatar_pct(v))
        sns.heatmap(m, ax=ax, cmap="RdYlGn", vmin=-limite, vmax=limite, center=0, annot=anot.to_numpy(), fmt="",
                    annot_kws={"fontsize": 13, "fontweight": "bold"}, linewidths=1.5, linecolor="white",
                    cbar=i == 1, cbar_ax=cax if i == 1 else None)
        ax.set_title(rec, fontsize=12)
        ax.set_xlabel("Porte")
        ax.set_ylabel("Canal" if i == 0 else "")
        ax.tick_params(axis="y", rotation=0)
        if i == 1:
            ax.set_yticklabels([])
    cax.yaxis.set_major_locator(MultipleLocator(0.02))
    cax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: formatar_pct(x, p, 0)))
    cax.set_ylabel("Margem líquida (% da receita)")
    fig.suptitle("Margem líquida estimada por canal e porte (razão de somas)", fontweight="bold", fontsize=13)
    fig.subplots_adjust(top=0.86, bottom=0.17, left=0.13, right=0.93)
    _rodape(fig, "simulado", fonte_ipca)
    return _salvar(fig, destino)


def grafico_09_contexto_macro_real(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 09: somente dados reais — PMC 8880, IPCA mensal e em 12 meses, participação da Internet (PAC)."""
    macro = _exigir(tabelas, "serie_macro_mensal")
    pac = _exigir(tabelas, "pac_internet")
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), gridspec_kw={"hspace": 0.5})
    # (a) PMC
    ax1.plot(macro["data"], macro["pmc_indice_volume_varejo_sa"], color="#1F4E79", lw=2.2)
    ax1.set_ylabel("Índice (2022 = 100)")
    ax1.set_xlabel("Mês")
    _limitar_datas(ax1, macro["data"])
    sombrear_fases(ax1)
    ax1.set_title("(a) PMC — volume de vendas do varejo, com ajuste sazonal (tabela 8880)", pad=24, fontsize=12)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: _br(x, 0)))
    # (b) IPCA
    ax2.bar(macro["data"], macro["ipca_variacao_mensal"], width=24, color="#7FB3D5", label="IPCA mensal (%)")
    ax2.axhline(0, color="#555555", lw=0.8)
    ax2.set_ylabel("IPCA mensal (%)")
    ax2.set_xlabel("Mês")
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: _br(x, 1)))
    ax2b = ax2.twinx()
    ok = macro.dropna(subset=["ipca_acumulado_12m"])
    ax2b.plot(ok["data"], ok["ipca_acumulado_12m"], color="#922B21", lw=2.2, label="IPCA acumulado em 12 meses (a partir de dez/2018)")
    ax2b.set_ylabel("Acumulado em 12 meses (%)")
    ax2b.yaxis.set_major_formatter(FuncFormatter(lambda x, p: _br(x, 0)))
    ax2b.grid(False)
    ax2b.set_ylim(0, max(14.0, float(ok["ipca_acumulado_12m"].max()) * 1.1))
    ax2.set_ylim(min(-0.8, float(macro["ipca_variacao_mensal"].min()) * 1.2), max(2.0, float(macro["ipca_variacao_mensal"].max()) * 1.3))
    _limitar_datas(ax2, macro["data"])
    sombrear_fases(ax2)
    ax2.set_title(f"(b) IPCA — variação mensal e acumulado em 12 meses ({fonte_ipca})", pad=24, fontsize=12)
    h1, l1 = ax2.get_legend_handles_labels()
    h2, l2 = ax2b.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.005, 0.97), fontsize=9)
    # (c) PAC
    tot = pac[pac["papel"] == "total"].sort_values("ano")
    ax3.plot(tot["ano"], tot["participacao_internet"], color="black", lw=2.6, marker="o", label="Total do varejo (20+ pessoas ocupadas)")
    for _, r in tot.iterrows():
        ax3.annotate(formatar_pct(r["participacao_internet"]), (r["ano"], r["participacao_internet"]), xytext=(7, 7),
                     textcoords="offset points", ha="left", va="bottom", fontsize=8.5, fontweight="bold")
    nomes = dict(zip(config.SEGMENTO_CODIGOS, config.SEGMENTOS))
    for cod in config.SEGMENTO_CODIGOS:
        sub = pac[(pac["papel"] == cod) & (pac["situacao"] == "ok")].sort_values("ano")
        ax3.scatter(sub["ano"], sub["participacao_internet"], color=CORES_SEGMENTOS[cod], marker=MARCADORES_SEGMENTOS[cod],
                    s=70, edgecolor="#222222", linewidth=0.5, label=nomes[cod], zorder=3)
    ax3.axvline(2023.5, color="#777777", ls="--", lw=1)
    ax3.text(2023.52, 0.38, "quebra de série", rotation=90, fontsize=8, color="#555555", va="bottom", ha="left")
    ax3.set_xticks(sorted(pac["ano"].unique()))
    ax3.set_xlim(2018.6, 2024.4)
    ax3.yaxis.set_major_formatter(FuncFormatter(lambda x, p: formatar_pct(x, p, 0)))
    ax3.set_ylim(0, max(0.62, float(pac["participacao_internet"].max()) * 1.4))
    ax3.set_xlabel("Ano")
    ax3.set_ylabel("Participação da Internet na receita")
    ax3.set_title("(c) PAC — participação da Internet na receita de revenda do varejo (empresas com 20+ pessoas ocupadas)", fontsize=12)
    ax3.legend(loc="upper left", ncol=3, fontsize=9)
    ax3.text(0.99, 0.52, "Anos sem ponto: alguma parcela sob sigilo estatístico (X).\n2024: série nova da PAC (quebra de série).",
             transform=ax3.transAxes, ha="right", va="top", fontsize=8.5, color="#333333",
             bbox={"boxstyle": "round,pad=0.35", "fc": "white", "ec": "#CCCCCC"})
    fig.suptitle("Contexto macroeconômico real (IBGE)", fontweight="bold", fontsize=14, y=0.995)
    fig.subplots_adjust(top=0.94, bottom=0.05)
    _rodape(fig, "real", fonte_ipca)
    return _salvar(fig, destino)


def grafico_10_ponto_equilibrio_canal(tabelas: dict[str, pd.DataFrame], destino: Path, fonte_ipca: str) -> Path:
    """Gráfico 10: diagrama custo-volume-lucro do Cenário Atual (MEI | ME), ponto de equilíbrio e receitas de indiferença."""
    cvp = _exigir(tabelas, "cvp_parametros_atual")
    ind = _exigir(tabelas, "receita_indiferenca_canais")
    limites = {"MEI": 9000.0, "ME": 35000.0}
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.8))
    for ax, porte in zip(axes, config.PORTES):
        sub = cvp[(cvp["porte"] == porte) & (cvp["segmento"] == "Todos")].set_index("canal")
        R = np.linspace(0, limites[porte], 400)
        linhas_quadro = ["Ponto de equilíbrio (PE, ●):"]
        for canal in config.CANAIS:
            v, F, pe = float(sub.at[canal, "v"]), float(sub.at[canal, "F"]), float(sub.at[canal, "PE"])
            ax.plot(R, R * (1 - v) - F, color=config.CORES_CANAIS[canal], lw=2.3, label=canal)
            if 0 < pe <= limites[porte]:
                ax.scatter([pe], [0], color=config.CORES_CANAIS[canal], s=75, zorder=4, edgecolor="black")
            linhas_quadro.append(f"   {canal}: {formatar_moeda(pe)}/mês")
        linhas_quadro.append("Receitas de indiferença (R*, ✕):")
        cruz = ind[(ind["porte"] == porte) & (ind["situacao"] == "cruzamento")].reset_index(drop=True)
        for n, r in cruz.iterrows():
            rs = float(r["r_estrela"])
            linhas_quadro.append(f"   {n + 1}. {ABREV_CANAL[r['canal_a']]} × {ABREV_CANAL[r['canal_b']]}: {formatar_moeda(rs)}"
                                 f" (acima: {ABREV_CANAL[r['vencedor_acima']]})")
            if 0 < rs <= limites[porte]:
                v, F = float(sub.at[r["canal_a"], "v"]), float(sub.at[r["canal_a"], "F"])
                y = rs * (1 - v) - F
                ax.scatter([rs], [y], marker="X", color="black", s=80, zorder=5)
                ax.annotate(str(n + 1), (rs, y), xytext=(-4, 7), textcoords="offset points", fontsize=9.5,
                            fontweight="bold", ha="right")
        ax.text(0.015, 0.975, "\n".join(linhas_quadro), transform=ax.transAxes, ha="left", va="top", fontsize=8.6,
                color="#222222", bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": "#BBBBBB", "alpha": 0.95})
        r_ref = float(sub["R_ref"].iloc[0])
        ax.axvline(r_ref, color="#555555", ls="--", lw=1.2)
        ax.text(r_ref, 0.02, f" Receita média por negócio\n {formatar_moeda(r_ref)}/mês", transform=mtransforms.blended_transform_factory(ax.transData, ax.transAxes),
                ha="left", va="bottom", fontsize=8.5, color="#333333")
        ax.axhline(0, color="black", lw=0.9)
        ax.set_xlim(0, limites[porte])
        ax.xaxis.set_major_locator(MultipleLocator(1500 if porte == "MEI" else 5000))
        ax.xaxis.set_major_formatter(FuncFormatter(formatar_moeda))
        ax.yaxis.set_major_formatter(FuncFormatter(formatar_moeda))
        ax.set_xlabel("Receita mensal por negócio (R$)")
        ax.set_ylabel("Margem líquida mensal por negócio (R$)")
        ax.set_title(porte, fontsize=12)
        # Legenda erguida acima do rótulo da receita média (rente ao eixo x), para não cobri-lo
        ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.11), fontsize=9)
    fig.suptitle("Ponto de equilíbrio e receitas de indiferença entre canais — Cenário Atual (2025–2026)", fontweight="bold", fontsize=13)
    fig.text(0.5, 0.06, "Margem(R) = R × (1 − v) − F, com v = custos variáveis ÷ receita e F = custos fixos + DAS por negócio. "
             "PE = ponto de equilíbrio; R* = receita em que dois canais empatam.", ha="center", fontsize=8.8, color="#333333")
    fig.tight_layout(rect=(0, 0.09, 1, 0.96))
    _rodape(fig, "simulado", fonte_ipca)
    return _salvar(fig, destino)


FUNCOES_GRAFICOS = [
    grafico_01_receita_real_por_canal,
    grafico_02_participacao_canal_por_fase,
    grafico_03_composicao_custos_margem_por_canal,
    grafico_04_dispersao_cac_ltv,
    grafico_05_ticket_medio_canal_fase,
    grafico_06_taxa_retencao_tempo,
    grafico_07_take_rate_marketplace_vs_cac_ecommerce,
    grafico_08_heatmap_margem_canal_porte,
    grafico_09_contexto_macro_real,
    grafico_10_ponto_equilibrio_canal,
]


def gerar_graficos(tabelas: dict[str, pd.DataFrame], fonte_ipca: str) -> list[Path]:
    """Gera os 10 gráficos na ordem e grava em ``outputs/graficos``.

    Args:
        tabelas: tabelas de apoio (seção 11.1).
        fonte_ipca: rótulo da fonte do IPCA para os rodapés.

    Returns:
        Caminhos dos PNGs.

    Raises:
        KeyError: tabela necessária ausente.
    """
    configurar_estilo()
    # Mês-base dos valores reais (último mês da série), usado nos rótulos de eixo
    _ESTADO["mes_base"] = config.rotulo_mes_base(_exigir(tabelas, "serie_macro_mensal")["data"].max())
    caminhos = []
    for funcao, nome in zip(FUNCOES_GRAFICOS, config.ARQUIVOS_GRAFICOS):
        caminhos.append(funcao(tabelas, config.DIR_GRAFICOS / nome, fonte_ipca))
    logger.info("Gráficos gerados: %d em %s", len(caminhos), config.caminho_relativo(config.DIR_GRAFICOS))
    return caminhos
