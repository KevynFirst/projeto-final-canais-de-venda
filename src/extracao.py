"""Extração de dados: APIs oficiais (IBGE/SIDRA e BCB/SGS), snapshots locais e simulação do painel.

Responsabilidades:

* baixar as séries reais com novas tentativas e validação de formato;
* gravar e reler snapshots com carimbo de data/hora e SHA-256 (execução offline e reprodutível);
* simular o painel mensal de canais de MEIs e MEs, calibrado com a PMC, o IPCA e regras oficiais;
* gravar o arquivo bruto do painel com problemas de qualidade deliberados e o gabarito da injeção.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from src import ErroExtracao, ErroQualidadeDados
from src import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Cliente HTTP
# ---------------------------------------------------------------------------
def criar_sessao_http() -> requests.Session:
    """Cria a sessão HTTP com os cabeçalhos padrão do projeto.

    Returns:
        Sessão ``requests`` com ``User-Agent`` e ``Accept: application/json``.
    """
    sessao = requests.Session()
    sessao.headers.update({"User-Agent": config.USER_AGENT, "Accept": "application/json"})
    return sessao


def _validar_formato(dados: object, fonte_id: str) -> None:
    """Valida o formato mínimo da resposta de cada API.

    Args:
        dados: JSON decodificado.
        fonte_id: identificador da fonte.

    Raises:
        ErroExtracao: formato inesperado (sem nova tentativa).
    """
    if fonte_id.startswith("ipca_bcb"):
        if not isinstance(dados, list) or not dados:
            raise ErroExtracao(fonte_id, "resposta do BCB vazia ou não é lista")
        for item in dados:
            if not isinstance(item, dict) or "data" not in item or "valor" not in item:
                raise ErroExtracao(fonte_id, "registro do BCB sem 'data' ou 'valor'")
            try:
                datetime.strptime(str(item["data"]), "%d/%m/%Y")
            except ValueError as exc:
                raise ErroExtracao(fonte_id, f"data inválida no BCB: {item['data']!r}") from exc
        return
    if not isinstance(dados, list) or len(dados) < 2:
        raise ErroExtracao(fonte_id, "resposta do SIDRA com menos de 2 elementos")
    cabecalho = dados[0]
    if not isinstance(cabecalho, dict) or "V" not in cabecalho or "D1C" not in cabecalho:
        raise ErroExtracao(fonte_id, "cabeçalho do SIDRA sem 'V' ou 'D1C'")
    if any(not isinstance(r, dict) or "V" not in r for r in dados):
        raise ErroExtracao(fonte_id, "registro do SIDRA sem 'V'")


def requisitar_json(
    sessao: requests.Session,
    url: str,
    params: dict[str, str] | None = None,
    *,
    fonte_id: str,
) -> tuple[object, dict]:
    """Faz um GET com até 3 tentativas e devolve o JSON validado e os metadados da coleta.

    Repete em erro de conexão, timeout, HTTP 429/5xx e resposta 200 sem JSON (caso do SGS 433
    que devolve uma página HTML "Requisição inválida!"). Não repete em outros 4xx nem em JSON com
    formato inesperado.

    Args:
        sessao: sessão HTTP.
        url: endpoint.
        params: parâmetros de consulta.
        fonte_id: identificador da fonte, usado em logs e metadados.

    Returns:
        Tupla ``(dados, meta)``.

    Raises:
        ErroExtracao: falha definitiva.
    """
    motivo = ""
    for tentativa in range(1, config.HTTP_TENTATIVAS + 1):
        inicio = time.monotonic()
        try:
            resposta = sessao.get(url, params=params, timeout=config.HTTP_TIMEOUT)
        except (requests.ConnectionError, requests.Timeout) as exc:
            duracao = time.monotonic() - inicio
            motivo = f"{type(exc).__name__} após {duracao:.1f} s"
            logger.warning("%s: tentativa %d/%d falhou (%s)", fonte_id, tentativa, config.HTTP_TENTATIVAS, motivo)
        else:
            duracao = time.monotonic() - inicio
            status = resposta.status_code
            tipo = resposta.headers.get("Content-Type", "")
            if status in config.HTTP_STATUS_REPETIR:
                motivo = f"HTTP {status}, conteúdo '{tipo}', {duracao:.1f} s"
                logger.warning("%s: tentativa %d/%d falhou (%s)", fonte_id, tentativa, config.HTTP_TENTATIVAS, motivo)
            elif status >= 400:
                logger.warning("%s: HTTP %d sem nova tentativa (%.1f s)", fonte_id, status, duracao)
                try:
                    resposta.raise_for_status()
                except requests.HTTPError as exc:
                    raise ErroExtracao(fonte_id, f"HTTP {status}") from exc
            elif "json" not in tipo.lower():
                motivo = f"HTTP {status} com conteúdo '{tipo}' (não JSON), {duracao:.1f} s"
                logger.warning("%s: tentativa %d/%d falhou (%s)", fonte_id, tentativa, config.HTTP_TENTATIVAS, motivo)
            else:
                try:
                    dados = resposta.json()
                except ValueError:
                    motivo = f"HTTP {status} com corpo que não é JSON, {duracao:.1f} s"
                    logger.warning("%s: tentativa %d/%d falhou (%s)", fonte_id, tentativa, config.HTTP_TENTATIVAS, motivo)
                else:
                    try:
                        _validar_formato(dados, fonte_id)
                    except ErroExtracao:
                        logger.warning("%s: JSON com formato inesperado (sem nova tentativa)", fonte_id)
                        raise
                    linhas = len(dados) if isinstance(dados, list) else 0
                    logger.info("%s: %d registros obtidos em %.1f s (tentativa %d)", fonte_id, linhas, duracao, tentativa)
                    meta = {
                        "fonte_id": fonte_id,
                        "fonte": config.FONTES[fonte_id]["fonte"],
                        "endpoint": url,
                        "parametros": dict(params or {}),
                        "obtido_em": datetime.now().astimezone().isoformat(timespec="seconds"),
                        "http_status": status,
                        "content_type": tipo,
                        "tentativas": tentativa,
                        "linhas": linhas,
                    }
                    return dados, meta
        if tentativa < config.HTTP_TENTATIVAS:
            time.sleep(config.HTTP_ESPERAS_S[tentativa - 1])
    raise ErroExtracao(fonte_id, f"falha após {config.HTTP_TENTATIVAS} tentativas: {motivo}")


# ---------------------------------------------------------------------------
# Snapshots locais
# ---------------------------------------------------------------------------
def _sha256(caminho: Path) -> str:
    """Calcula o SHA-256 de um arquivo.

    Args:
        caminho: arquivo.

    Returns:
        Hash hexadecimal.
    """
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def salvar_snapshot(dados: object, meta: dict) -> Path:
    """Grava os dados brutos de uma fonte e o arquivo de metadados com SHA-256.

    Args:
        dados: JSON exatamente como veio da API.
        meta: metadados da coleta.

    Returns:
        Caminho do arquivo de dados gravado.

    Raises:
        OSError: falha de escrita (fatal).
    """
    config.DIR_RAW_API.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.fromisoformat(meta["obtido_em"]).strftime("%Y%m%dT%H%M%S")
    base = f"{meta['fonte_id']}_{carimbo}"
    caminho_dados = config.DIR_RAW_API / f"{base}.json"
    caminho_meta = config.DIR_RAW_API / f"{base}.meta.json"
    with open(caminho_dados, "w", encoding="utf-8", newline="\n") as arq:
        json.dump(dados, arq, ensure_ascii=False, indent=1)
    meta_completo = dict(meta)
    meta_completo["arquivo_dados"] = caminho_dados.name
    meta_completo["sha256"] = _sha256(caminho_dados)
    with open(caminho_meta, "w", encoding="utf-8", newline="\n") as arq:
        json.dump(meta_completo, arq, ensure_ascii=False, indent=2)
    logger.info("Snapshot gravado: %s", config.caminho_relativo(caminho_dados))
    return caminho_dados


def carregar_snapshot_mais_recente(fonte_id: str) -> tuple[object, dict] | None:
    """Carrega o snapshot válido mais recente de uma fonte.

    Escolhe o maior carimbo cujo ``.meta.json`` exista e cujo SHA-256 confira; arquivo corrompido
    gera WARNING e o anterior é tentado.

    Args:
        fonte_id: identificador da fonte.

    Returns:
        ``(dados, meta)`` ou ``None`` se não houver snapshot válido.
    """
    if not config.DIR_RAW_API.exists():
        return None
    metas = sorted(config.DIR_RAW_API.glob(f"{fonte_id}_????????T??????.meta.json"), reverse=True)
    for caminho_meta in metas:
        try:
            meta = json.loads(caminho_meta.read_text(encoding="utf-8"))
            caminho_dados = config.DIR_RAW_API / meta["arquivo_dados"]
            if _sha256(caminho_dados) != meta["sha256"]:
                logger.warning("%s: SHA-256 não confere em %s; tentando o anterior", fonte_id, caminho_meta.name)
                continue
            dados = json.loads(caminho_dados.read_text(encoding="utf-8"))
        except (OSError, ValueError, KeyError) as exc:
            logger.warning("%s: snapshot inválido %s (%s); tentando o anterior", fonte_id, caminho_meta.name, type(exc).__name__)
            continue
        return dados, meta
    return None


def _endpoint(fonte_id: str, fim: pd.Timestamp) -> tuple[str, dict[str, str] | None]:
    """Monta URL e parâmetros de uma fonte para o mês final ``fim``.

    Args:
        fonte_id: identificador da fonte.
        fim: mês anterior ao mês da execução.

    Returns:
        ``(url, params)``.
    """
    modelo = config.FONTES[fonte_id]["modelo"]
    if fonte_id == "ipca_bcb_433":
        ultimo_dia = (fim + pd.offsets.MonthEnd(0)).strftime("%d/%m/%Y")
        return modelo, {"formato": "json", "dataInicial": "01/01/2018", "dataFinal": ultimo_dia}
    return modelo.format(fim=fim.strftime("%Y%m")), None


def obter_dados_reais(atualizar: bool) -> dict[str, tuple[object, dict]]:
    """Obtém as 6 fontes reais, das APIs (``atualizar=True``) ou dos snapshots locais.

    Args:
        atualizar: se ``True``, baixa novamente e grava novos snapshots; senão, só lê snapshots.

    Returns:
        Dicionário ``fonte_id → (dados, meta)`` com as fontes disponíveis.

    Raises:
        ErroExtracao: fonte obrigatória ausente ou nenhum IPCA disponível.
    """
    resultado: dict[str, tuple[object, dict]] = {}
    if atualizar:
        fim = config.mes_fim_consulta(pd.Timestamp.now())
        logger.info("Atualizando fontes reais (mês final da consulta: %s)", fim.strftime("%Y-%m"))
        sessao = criar_sessao_http()
        for fonte_id in config.ORDEM_FONTES:
            url, params = _endpoint(fonte_id, fim)
            try:
                dados, meta = requisitar_json(sessao, url, params, fonte_id=fonte_id)
            except ErroExtracao as exc:
                anterior = carregar_snapshot_mais_recente(fonte_id)
                if anterior is not None:
                    logger.warning("%s indisponível (%s); usando snapshot de %s", fonte_id, exc.motivo, anterior[1]["obtido_em"])
                    resultado[fonte_id] = anterior
                else:
                    logger.warning("%s indisponível (%s) e sem snapshot anterior", fonte_id, exc.motivo)
                continue
            salvar_snapshot(dados, meta)
            resultado[fonte_id] = (dados, meta)
    else:
        logger.info("Modo offline: lendo snapshots de %s", config.caminho_relativo(config.DIR_RAW_API))
        for fonte_id in config.ORDEM_FONTES:
            snap = carregar_snapshot_mais_recente(fonte_id)
            if snap is not None:
                resultado[fonte_id] = snap
                logger.info("%s: snapshot de %s (%d registros)", fonte_id, snap[1]["obtido_em"], snap[1].get("linhas", 0))
            elif fonte_id in config.FONTES_OBRIGATORIAS:
                raise ErroExtracao(fonte_id, f"Snapshot ausente para {fonte_id}. Execute: python main.py --atualizar")
            else:
                logger.info("%s: sem snapshot local (fonte opcional)", fonte_id)
    for fonte_id in config.FONTES_OBRIGATORIAS:
        if fonte_id not in resultado:
            raise ErroExtracao(fonte_id, f"Fonte obrigatória indisponível e sem snapshot: {fonte_id}")
    if not any(f in resultado for f in config.FONTES_IPCA):
        raise ErroExtracao("ipca", "Nenhuma fonte de IPCA disponível (BCB 433 e SIDRA 1737)")
    if "ipca_bcb_433" not in resultado:
        logger.warning("IPCA: BCB/SGS 433 indisponível; será usado o fallback IBGE/SIDRA 1737")
    return resultado


# ---------------------------------------------------------------------------
# Regras tributárias e de tarifas
# ---------------------------------------------------------------------------
def aliquota_efetiva_simples(rbt12: float) -> float:
    """Alíquota efetiva do Simples Nacional, Anexo I (comércio).

    Fórmula do art. 18, §1º-A da LC 123: (RBT12 × Alíquota − Parcela a deduzir) ÷ RBT12.

    Args:
        rbt12: receita bruta acumulada nos 12 meses anteriores (R$).

    Returns:
        Alíquota efetiva (fração).
    """
    if rbt12 <= 0:
        return float(config.PARAMETROS["simples_anexo_i"][0]["aliquota"])  # type: ignore[index]
    faixas = config.PARAMETROS["simples_anexo_i"]
    for faixa in faixas:  # type: ignore[union-attr]
        if rbt12 <= faixa["ate"]:
            return (rbt12 * faixa["aliquota"] - faixa["deducao"]) / rbt12
    ultima = faixas[-1]  # type: ignore[index]
    return (rbt12 * ultima["aliquota"] - ultima["deducao"]) / rbt12


def _vigente(tabela: list[dict], datas: pd.DatetimeIndex, campo: str) -> np.ndarray:
    """Valor vigente de um campo numa tabela de vigências ordenada por ``inicio``.

    Args:
        tabela: lista de dicionários com ``inicio`` (AAAA-MM-DD) e o campo.
        datas: datas de consulta.
        campo: nome do campo.

    Returns:
        Vetor com o valor vigente em cada data.
    """
    inicios = pd.to_datetime([t["inicio"] for t in tabela]).to_numpy()
    valores = np.array([t[campo] for t in tabela], dtype=float)
    idx = np.searchsorted(inicios, pd.DatetimeIndex(datas).to_numpy(), side="right") - 1
    return valores[np.clip(idx, 0, None)]


def _tarifa_ml_vetor(datas: pd.DatetimeIndex, receita: np.ndarray, pedidos: np.ndarray) -> np.ndarray:
    """Tarifa do Mercado Livre (Clássico) em R$ para vetores de linhas simuladas.

    ``receita × pct(t) + pedidos × fixo(t) × q``, com ``q`` = fração lognormal de pedidos abaixo
    do limite de preço ``L(t)`` (média = ticket da linha, σ_ln = 0,6).

    Args:
        datas: mês de cada linha.
        receita: receita bruta (R$).
        pedidos: número de pedidos.

    Returns:
        Comissões e tarifas (R$, sem arredondar).
    """
    receita = np.asarray(receita, dtype=float)
    pedidos = np.asarray(pedidos, dtype=float)
    pct = _vigente(config.PARAMETROS["ml_comissao_pct"], datas, "pct")  # type: ignore[arg-type]
    fixo = _vigente(config.PARAMETROS["ml_custo_fixo"], datas, "fixo")  # type: ignore[arg-type]
    limite = _vigente(config.PARAMETROS["ml_custo_fixo"], datas, "limite")  # type: ignore[arg-type]
    sigma = float(config.PARAMETROS["ml_sigma_ln_pedido"])  # type: ignore[arg-type]
    ticket = receita / pedidos
    mu = np.log(ticket) - sigma**2 / 2.0
    q = np.zeros_like(receita)
    ativo = (fixo > 0) & (limite > 0)
    if ativo.any():
        z = (np.log(limite[ativo]) - mu[ativo]) / (sigma * math.sqrt(2.0))
        q[ativo] = 0.5 * (1.0 + np.array([math.erf(v) for v in z]))
    return receita * pct + pedidos * fixo * q


def tarifa_marketplace_ml(data: pd.Timestamp, receita: float, pedidos: int) -> float:
    """Tarifa do Mercado Livre (anúncio Clássico) de uma linha simulada, em R$.

    Args:
        data: mês de referência.
        receita: receita bruta da linha (R$).
        pedidos: pedidos da linha.

    Returns:
        Comissão + custo fixo esperado (R$).
    """
    valor = _tarifa_ml_vetor(pd.DatetimeIndex([pd.Timestamp(data)]), np.array([receita]), np.array([pedidos]))
    return float(valor[0])


def take_rate_item_2026(plataforma: str, valor_item: float) -> float:
    """*Take rate* efetivo de um item pela regra oficial vigente em out/2026.

    Args:
        plataforma: ``ml_classico``, ``shopee_cnpj``, ``amazon_individual`` ou ``amazon_profissional``.
        valor_item: preço do item (R$).

    Returns:
        Tarifa como fração do valor do item.

    Raises:
        ValueError: plataforma desconhecida ou valor não positivo.
    """
    if valor_item <= 0:
        raise ValueError("valor_item deve ser positivo")
    regras = config.TARIFAS_2026
    if plataforma == "ml_classico":
        r = regras["ml_classico"]
        return r["pct"] + (r["fixo"] / valor_item if valor_item < r["limite"] else 0.0)  # type: ignore[index]
    if plataforma == "shopee_cnpj":
        faixa = [f for f in regras["shopee_cnpj"] if valor_item >= f["de"]][-1]  # type: ignore[union-attr]
        return faixa["pct"] + faixa["fixo"] / valor_item
    if plataforma == "amazon_individual":
        r = regras["amazon_individual"]
        return r["pct"] + r["fixo"] / valor_item  # type: ignore[index]
    if plataforma == "amazon_profissional":
        return float(regras["amazon_profissional"]["pct"])  # type: ignore[index]
    raise ValueError(f"Plataforma desconhecida: {plataforma}")


# ---------------------------------------------------------------------------
# Simulação do painel de canais (seção 7)
# ---------------------------------------------------------------------------
def interpolar_ancoras(ancoras: dict[str, float], datas: pd.DatetimeIndex, antes: float | None = None) -> np.ndarray:
    """Interpola âncoras temporais no tempo e mantém o último valor depois da última âncora.

    Args:
        ancoras: ``data ISO → valor``.
        datas: datas da grade.
        antes: valor para datas anteriores à primeira âncora (``None`` mantém NaN).

    Returns:
        Vetor alinhado a ``datas``.
    """
    serie = pd.Series(list(ancoras.values()), index=pd.to_datetime(list(ancoras.keys())), dtype=float)
    indice = serie.index.union(pd.DatetimeIndex(datas))
    serie = serie.reindex(indice).interpolate(method="time").ffill()
    if antes is not None:
        serie = serie.fillna(antes)
    return serie.reindex(pd.DatetimeIndex(datas)).to_numpy(copy=True)


def _fator_precos(ipca: pd.DataFrame, datas: pd.DatetimeIndex) -> np.ndarray:
    """Índice de preços P(t) encadeado do IPCA, com P(2017-12) = 1.

    Args:
        ipca: tabela com ``data`` e ``ipca_variacao_mensal``.
        datas: grade a partir de 2017-12.

    Returns:
        Vetor P(t).

    Raises:
        ErroQualidadeDados: mês de IPCA faltando entre 2018-01 e o fim da grade.
    """
    serie = ipca.set_index("data")["ipca_variacao_mensal"]
    meses = datas[datas >= config.DATA_INICIO]
    faltando = meses.difference(serie.index)
    if len(faltando):
        raise ErroQualidadeDados(f"IPCA sem cobertura em {len(faltando)} meses (ex.: {faltando[0]:%Y-%m})")
    fatores = 1.0 + serie.reindex(meses).to_numpy(copy=True) / 100.0
    return np.concatenate([[1.0], np.cumprod(fatores)])


def _direcionadores_segmento(pmc_8882: pd.DataFrame, codigo: str, datas: pd.DatetimeIndex) -> dict[str, np.ndarray | float]:
    """Calcula V_s(t), PI_s(t) e D_s(t) de um segmento a partir da PMC 8882 (seção 7.2).

    Args:
        pmc_8882: PMC por atividade (formato largo: ``data, atividade_id, vol_nsa, vol_sa, nom_nsa``).
        codigo: código do segmento.
        datas: grade a partir de 2017-12.

    Returns:
        Dicionário com ``V``, ``PI``, ``D`` (vetores) e ``b`` (inclinação mensal removida).

    Raises:
        ErroQualidadeDados: mês faltando na PMC.
    """
    atividade = config.SEGMENTO_ATIVIDADE_PMC[codigo]["id"]
    dados = pmc_8882[pmc_8882["atividade_id"] == atividade].set_index("data").reindex(datas)
    if dados[["vol_nsa", "vol_sa", "nom_nsa"]].isna().any().any():
        raise ErroQualidadeDados(f"PMC 8882 sem cobertura completa para a atividade {atividade} ({codigo})")
    vol_nsa = dados["vol_nsa"].to_numpy(copy=True)
    vol_sa = dados["vol_sa"].to_numpy(copy=True)
    nom_nsa = dados["nom_nsa"].to_numpy(copy=True)
    k = ((datas.year - 2019) * 12 + (datas.month - 7)).to_numpy()
    fora = ((datas < config.INICIO_PANDEMIA) | (datas >= config.INICIO_POS_PANDEMIA))
    b = float(np.polyfit(k[fora], np.log(vol_sa[fora]), 1)[0])
    em_2019 = datas.year == 2019
    V = vol_nsa / vol_nsa[em_2019].mean() * np.exp(-b * k)
    preco = nom_nsa / vol_nsa
    PI = preco / preco[em_2019].mean()
    return {"V": V, "PI": PI, "D": V * PI, "b": b}


def verificar_tetos_legais(painel: pd.DataFrame) -> dict[str, float]:
    """Confere os tetos legais de receita anual por negócio (MEI ≤ R$ 81 mil; ME ≤ R$ 360 mil).

    Receita anual por negócio = Σ receita_bruta ÷ (Σ negocios_ativos ÷ 12), por (ano, canal, porte,
    segmento), somente de 2018-01 em diante.

    Args:
        painel: painel com ``data``, dimensões, ``receita_bruta`` e ``negocios_ativos``.

    Returns:
        Máximo anual por negócio de cada porte.

    Raises:
        ErroQualidadeDados: alguma combinação acima do teto.
    """
    base = painel[painel["data"] >= config.DATA_INICIO].assign(ano=lambda d: d["data"].dt.year)
    g = base.groupby(["ano", "canal", "porte", "segmento"], observed=True)[["receita_bruta", "negocios_ativos"]].sum()
    g["anual"] = g["receita_bruta"] / (g["negocios_ativos"] / 12.0)
    tetos = {"MEI": config.TETO_MEI, "ME": config.TETO_ME}
    violacoes = []
    maximos = {}
    for porte, teto in tetos.items():
        sub = g.xs(porte, level="porte")
        maximos[porte] = float(sub["anual"].max())
        for idx, valor in sub["anual"][sub["anual"] > teto].items():
            violacoes.append(f"{porte} {idx}: R$ {valor:,.2f}")
    if violacoes:
        raise ErroQualidadeDados(f"Teto legal violado em {len(violacoes)} combinações: {violacoes[:5]}")
    return maximos


def simular_painel_canais(pmc_8882: pd.DataFrame, ipca: pd.DataFrame, data_fim: pd.Timestamp) -> pd.DataFrame:
    """Simula o painel mensal mês × canal × porte × segmento (seção 7).

    A simulação é determinística (semente fixa e ordem de sorteio fixa). O mês de aquecimento
    (2017-12) é usado só para a defasagem de clientes e o RBT12, e é descartado na saída.

    Args:
        pmc_8882: PMC por atividade (formato largo).
        ipca: IPCA mensal (``data``, ``ipca_variacao_mensal``).
        data_fim: último mês da série.

    Returns:
        Painel limpo de 2018-01 a ``data_fim`` com as 14 medidas base, na ordem canônica.

    Raises:
        ErroQualidadeDados: cobertura insuficiente ou teto legal violado.
    """
    P = config.PARAMETROS
    datas = pd.date_range(config.DATA_AQUECIMENTO, data_fim, freq="MS")
    n = len(datas)
    precos = _fator_precos(ipca, datas)
    pi = precos / precos[datas.year == 2019].mean()
    anos = ((datas.year - 2018) + (datas.month - 1) / 12.0).to_numpy()
    das_mes = config.das_mei_em(datas)
    pix_ecom = interpolar_ancoras(P["pix_ecommerce_ancoras"], datas, antes=0.0)  # type: ignore[arg-type]
    pix_fis = interpolar_ancoras(P["pix_fisica_ancoras"], datas, antes=0.0)  # type: ignore[arg-type]
    impulso = interpolar_ancoras(P["impulso_digital_ancoras"], datas)  # type: ignore[arg-type]
    ret_ecom = interpolar_ancoras(P["retencao_ecommerce_ancoras"], datas)  # type: ignore[arg-type]
    choque = P["retencao_choque_fisica"]
    em_choque = (datas >= pd.Timestamp(choque["inicio"])) & (datas <= pd.Timestamp(choque["fim"]))  # type: ignore[index]
    inicio_pix = pd.Timestamp(P["inicio_taxa_pix_ecommerce"])  # type: ignore[arg-type]
    taxa_ecom = np.where(
        datas < inicio_pix,
        P["taxa_proc_ecommerce_pre_pix"],
        (1 - pix_ecom) * P["taxa_proc_ecommerce_cartao"] + pix_ecom * P["taxa_proc_ecommerce_pix"],  # type: ignore[operator]
    )
    ret_min, ret_max = P["retencao_limites"]  # type: ignore[misc]
    rng = np.random.default_rng(config.SEMENTE_SIMULACAO)

    blocos: list[pd.DataFrame] = []
    for seg, s in zip(config.SEGMENTOS, config.SEGMENTO_CODIGOS):
        drv = _direcionadores_segmento(pmc_8882, s, datas)
        logger.info("Direcionador %s: tendência removida de %.2f%% a.a.; V(abr/2020) = %.3f",
                    s, drv["b"] * 12 * 100, drv["V"][datas.get_loc(pd.Timestamp("2020-04-01"))] if pd.Timestamp("2020-04-01") in datas else float("nan"))
        for porte in config.PORTES:
            n_neg = P["negocios_por_segmento"][porte]  # type: ignore[index]
            mult = P["phi_multiplicador_segmento"][s]  # type: ignore[index]
            phi_mkt = interpolar_ancoras(P["phi_ancoras"][porte]["marketplace"], datas) * mult["marketplace"]  # type: ignore[index]
            phi_eco = interpolar_ancoras(P["phi_ancoras"][porte]["ecommerce_proprio"], datas) * mult["ecommerce_proprio"]  # type: ignore[index]
            phis = {"fisica": 1.0 - phi_mkt - phi_eco, "marketplace": phi_mkt, "ecommerce_proprio": phi_eco}
            for canal, c in zip(config.CANAIS, config.CANAL_CODIGOS):
                # Ordem de sorteio fixa: ε_rec, ε_tk, ε_cac, ε_cmv (seção 7.7)
                e_rec = rng.lognormal(0.0, P["sigma_ruido_receita"], n)  # type: ignore[arg-type]
                e_tk = rng.lognormal(0.0, P["sigma_ruido_ticket"], n)  # type: ignore[arg-type]
                e_cac = rng.lognormal(0.0, P["sigma_ruido_cac"], n)  # type: ignore[arg-type]
                e_cmv = rng.normal(0.0, P["sigma_ruido_cmv"], n)  # type: ignore[arg-type]

                negocios = np.maximum(1, np.round(n_neg * phis[c])).astype(np.int64)
                r_bar = P["receita_media_2019"][porte][s]  # type: ignore[index]
                rho = P["rho_canal"][porte][c]  # type: ignore[index]
                B = impulso if c != "fisica" else np.ones(n)
                receita = np.round(negocios * r_bar * rho * drv["D"] * B * e_rec, 2)
                ticket_alvo = P["ticket_2019"][s][c] * drv["PI"] * e_tk  # type: ignore[index]
                pedidos = np.maximum(1, np.round(receita / ticket_alvo)).astype(np.int64)
                freq = P["frequencia_compra"][s][c]  # type: ignore[index]
                ativos = np.maximum(1, np.round(pedidos / freq)).astype(np.int64)

                # Retenção-alvo: base do canal + ajuste do segmento + choque, limitada
                base_ret = ret_ecom if c == "ecommerce_proprio" else np.full(n, P["retencao_base"][c])  # type: ignore[index]
                r = base_ret + P["retencao_ajuste_segmento"][s]  # type: ignore[index]
                if c == "fisica":
                    r = r + np.where(em_choque, choque["valor"], 0.0)  # type: ignore[index]
                r = np.clip(r, ret_min, ret_max)

                anterior = np.empty(n, dtype=np.int64)
                recorrentes = np.empty(n, dtype=np.int64)
                for t in range(n):
                    anterior[t] = ativos[t - 1] if t > 0 else ativos[0]
                    recorrentes[t] = max(0, min(ativos[t] - 1, int(np.round(r[t] * anterior[t]))))
                novos = ativos - recorrentes

                # Custos, tarifas e impostos (seção 7.6)
                cac0 = P["cac_2019"][s][c]  # type: ignore[index]
                g = P["cac_tendencia_real_aa"][c]  # type: ignore[index]
                marketing = np.round(novos * cac0 * pi * (1.0 + g) ** anos * e_cac, 2)
                if c == "marketplace":
                    comissoes = _tarifa_ml_vetor(datas, receita, pedidos)
                elif c == "ecommerce_proprio":
                    comissoes = receita * taxa_ecom
                else:
                    comissoes = receita * (1.0 - pix_fis) * P["mdr_cartao_fisica"]  # type: ignore[operator]
                comissoes = np.round(comissoes, 2)
                frete = np.round(pedidos * P["frete_medio_2019"][c] * P["frete_parcela_vendedor"][c] * pi, 2)  # type: ignore[index]
                cmv = np.round(receita * (P["cmv_pct_segmento"][s] + P["cmv_delta_canal"][c] + e_cmv), 2)  # type: ignore[index]
                custos_fixos = np.round(
                    negocios * P["custos_fixos_2019"][porte][c] * P["custos_fixos_mult_segmento"][s] * pi, 2  # type: ignore[index]
                )
                if porte == "MEI":
                    imp_fixos = np.round(negocios * das_mes, 2)
                    imp_var = np.zeros(n)
                else:
                    imp_fixos = np.zeros(n)
                    por_negocio = receita / negocios
                    referencia = P["receita_media_2019"]["ME"][s] * P["rho_canal"]["ME"][c] * drv["PI"]  # type: ignore[index]
                    aliq = np.zeros(n)
                    for t in range(1, n):
                        h = min(12, t)
                        rbt12 = por_negocio[t - h:t].sum() + (12 - h) * referencia[t]
                        aliq[t] = aliquota_efetiva_simples(float(rbt12))
                    imp_var = np.round(receita * aliq, 2)

                blocos.append(pd.DataFrame({
                    "data": datas, "canal": canal, "porte": porte, "segmento": seg,
                    "negocios_ativos": negocios, "receita_bruta": receita, "pedidos": pedidos,
                    "clientes_ativos": ativos, "clientes_novos": novos, "clientes_recorrentes": recorrentes,
                    "clientes_ativos_mes_anterior": anterior, "investimento_marketing": marketing,
                    "comissoes_tarifas": comissoes, "frete_subsidiado": frete, "cmv": cmv,
                    "custos_fixos": custos_fixos, "impostos_fixos": imp_fixos, "impostos_variaveis": imp_var,
                }))

    painel = pd.concat(blocos, ignore_index=True)
    painel = painel[painel["data"] >= config.DATA_INICIO]
    painel = config.ordenar_canonico(painel)
    maximos = verificar_tetos_legais(painel)
    logger.info("Painel simulado: %d linhas (%s a %s); máximo anual por negócio MEI R$ %.0f, ME R$ %.0f",
                len(painel), painel["data"].min().strftime("%Y-%m"), painel["data"].max().strftime("%Y-%m"),
                maximos["MEI"], maximos["ME"])
    return painel


# ---------------------------------------------------------------------------
# Arquivo bruto com problemas de qualidade (seção 8)
# ---------------------------------------------------------------------------
def _formatar_moeda_br(valor: float, cifrao: bool) -> str:
    """Formata um valor como ``1.234,56`` (opcionalmente com ``R$ ``).

    Args:
        valor: número.
        cifrao: inclui o prefixo ``R$ ``.

    Returns:
        Texto no formato brasileiro.
    """
    texto = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}" if cifrao else texto


def _formatar_data(d: pd.Timestamp, formato: int) -> str:
    """Formata uma data mensal num dos 3 formatos do bruto.

    Args:
        d: data (1º dia do mês).
        formato: 0 = ``AAAA-MM``; 1 = ``MM/AAAA``; 2 = ``AAAA-MM-01``.

    Returns:
        Texto da data.
    """
    if formato == 0:
        return d.strftime("%Y-%m")
    if formato == 1:
        return d.strftime("%m/%Y")
    return d.strftime("%Y-%m-01")


def sortear_celulas_ausentes(rng: np.random.Generator, n_linhas: int, primeiro_mes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sorteia as células que ficarão ausentes no bruto: no máximo 1 por linha e o mesmo total por coluna.

    ``total = round(0,025 × n_linhas × 14)``, ajustado para múltiplo de 14; a defasagem de clientes
    nunca fica ausente no primeiro mês (troca circular com a próxima posição válida).

    Args:
        rng: gerador aleatório (semente dos problemas).
        n_linhas: número de linhas limpas.
        primeiro_mes: máscara das linhas do primeiro mês exportado.

    Returns:
        ``(linhas, colunas)``: índices de linha e de coluna (posição em ``COLUNAS_MEDIDA_BRUTAS``).
    """
    medidas = config.COLUNAS_MEDIDA_BRUTAS
    n_med = len(medidas)
    fracao = config.PARAMETROS["injecao_problemas"]["fracao_celulas_ausentes"]  # type: ignore[index]
    total = int(np.round(fracao * n_linhas * n_med))
    por_coluna = total // n_med
    total = por_coluna * n_med
    linhas = rng.permutation(n_linhas)[:total]
    colunas = rng.permutation(np.repeat(np.arange(n_med), por_coluna))
    idx_defasagem = medidas.index("clientes_ativos_mes_anterior")
    for i in range(total):
        if colunas[i] == idx_defasagem and primeiro_mes[linhas[i]]:
            for passo in range(1, total):
                j = (i + passo) % total
                if colunas[j] != idx_defasagem and not primeiro_mes[linhas[j]]:
                    colunas[i], colunas[j] = colunas[j], colunas[i]
                    break
    return linhas, colunas


def gravar_painel_bruto(painel: pd.DataFrame, snapshots: list[str]) -> tuple[Path, dict]:
    """Converte o painel limpo num "export de sistema" com problemas documentados e grava o gabarito.

    Problemas injetados (gerador com a semente 2027, nesta ordem): datas em 3 formatos, rótulos
    inconsistentes, números como texto (padrão brasileiro e com "R$"), no máximo 1 célula ausente
    por linha (78 por coluna), duplicatas exatas e duplicatas "formatadas".

    Args:
        painel: painel limpo (2018-01 a ``data_fim``) na ordem canônica.
        snapshots: nomes dos arquivos de snapshot usados.

    Returns:
        ``(caminho do CSV bruto, gabarito)``.
    """
    inj = config.PARAMETROS["injecao_problemas"]
    rng = np.random.default_rng(config.SEMENTE_PROBLEMAS)
    painel = config.ordenar_canonico(painel)
    n = len(painel)
    medidas = config.COLUNAS_MEDIDA_BRUTAS
    texto = pd.DataFrame(index=range(n))
    gab: dict = {}

    # 1. Datas em formatos mistos
    probs = list(inj["formatos_data"].values())  # type: ignore[index]
    formatos = rng.choice(3, size=n, p=probs)
    datas = painel["data"].tolist()
    texto["mes_referencia"] = [_formatar_data(d, f) for d, f in zip(datas, formatos)]
    gab["datas_por_formato"] = {config.FORMATOS_DATA_BRUTA[i]: int((formatos == i).sum()) for i in range(3)}

    # 2. Rótulos inconsistentes
    variantes_usadas: dict[str, dict[str, int]] = {}
    variante_canal = np.full(n, -1)
    for coluna, fracao in (("canal", inj["fracao_rotulo_canal"]), ("porte", inj["fracao_rotulo_porte"]),  # type: ignore[index]
                           ("segmento", inj["fracao_rotulo_segmento"])):  # type: ignore[index]
        mascara = rng.random(n) < fracao
        escolhas = rng.integers(0, 4, size=n)
        valores = painel[coluna].tolist()
        saida = []
        contagem: dict[str, int] = {}
        for i, v in enumerate(valores):
            opcoes = config.VARIANTES_ROTULOS[coluna][v]
            if mascara[i]:
                j = int(escolhas[i]) % len(opcoes)
                saida.append(opcoes[j])
                contagem[opcoes[j]] = contagem.get(opcoes[j], 0) + 1
                if coluna == "canal":
                    variante_canal[i] = j
            else:
                saida.append(v)
        texto[coluna] = saida
        variantes_usadas[coluna] = dict(sorted(contagem.items()))
    gab["rotulos_por_variante"] = variantes_usadas

    # 3. Números como texto
    n_br = 0
    n_br_cifrao = 0
    n_milhar = 0
    for coluna in medidas:
        valores = painel[coluna].to_numpy(copy=True)
        u = rng.random(n)
        if coluna in config.COLUNAS_MONETARIAS:
            col_txt = []
            for v, x in zip(valores, u):
                if x < inj["fracao_moeda_br"]:  # type: ignore[index]
                    col_txt.append(_formatar_moeda_br(float(v), False))
                elif x < inj["fracao_moeda_br"] + inj["fracao_moeda_br_cifrao"]:  # type: ignore[index]
                    col_txt.append(_formatar_moeda_br(float(v), True))
                else:
                    col_txt.append(f"{float(v):.2f}")
        else:
            col_txt = []
            for v, x in zip(valores, u):
                if v >= 1000 and x < inj["fracao_milhar_contagem"]:  # type: ignore[index]
                    col_txt.append(f"{int(v):,}".replace(",", "."))
                else:
                    col_txt.append(str(int(v)))
        texto[coluna] = col_txt

    # 4. Valores ausentes: no máximo 1 por linha, 78 por coluna
    n_med = len(medidas)
    primeiro_mes = (painel["data"] == painel["data"].min()).to_numpy()
    linhas, colunas = sortear_celulas_ausentes(rng, n, primeiro_mes)
    total = len(linhas)
    celulas_ausentes = []
    for lin, col in zip(linhas, colunas):
        nome = medidas[int(col)]
        texto.iat[int(lin), texto.columns.get_loc(nome)] = ""
        celulas_ausentes.append({
            "data": painel["data"].iat[int(lin)].strftime("%Y-%m-01"),
            "canal": painel["canal"].iat[int(lin)], "porte": painel["porte"].iat[int(lin)],
            "segmento": painel["segmento"].iat[int(lin)], "coluna": nome,
        })
    gab["celulas_ausentes_por_coluna"] = {m: int((colunas == i).sum()) for i, m in enumerate(medidas)}
    gab["celulas_ausentes_total"] = int(total)

    # Contagem de números no formato brasileiro (só células presentes)
    for coluna in config.COLUNAS_MONETARIAS:
        serie = texto[coluna]
        n_br_cifrao += int(serie.str.startswith("R$").sum())
        n_br += int(((~serie.str.startswith("R$")) & serie.str.contains(",", regex=False)).sum())
    for coluna in config.COLUNAS_CONTAGEM:
        n_milhar += int(texto[coluna].str.contains(".", regex=False).sum())
    gab["numeros_formato_br"] = {"moeda_br": n_br, "moeda_br_com_cifrao": n_br_cifrao, "contagem_com_milhar": n_milhar}

    # 5–6. Duplicatas exatas e formatadas (origens disjuntas, sem reposição)
    n_exatas = int(np.round(inj["fracao_duplicatas_exatas"] * n))  # type: ignore[index]
    n_formatadas = int(np.round(inj["fracao_duplicatas_formatadas"] * n))  # type: ignore[index]
    origens = rng.choice(n, size=n_exatas + n_formatadas, replace=False)
    copias_exatas = texto.iloc[origens[:n_exatas]].copy()
    copias_formatadas = texto.iloc[origens[n_exatas:]].copy()
    novas_datas = []
    novos_canais = []
    for pos, i in enumerate(origens[n_exatas:]):
        i = int(i)
        outros_formatos = [f for f in range(3) if f != formatos[i]]
        f_novo = outros_formatos[int(rng.integers(0, len(outros_formatos)))]
        novas_datas.append(_formatar_data(datas[i], f_novo))
        canonico = painel["canal"].iat[i]
        opcoes = [canonico] + config.VARIANTES_ROTULOS["canal"][canonico]
        atual = texto["canal"].iat[i]
        restantes = [o for o in opcoes if o != atual]
        novos_canais.append(restantes[int(rng.integers(0, len(restantes)))])
    copias_formatadas["mes_referencia"] = novas_datas
    copias_formatadas["canal"] = novos_canais

    # 7. Duplicatas inseridas em posições sorteadas
    copias = pd.concat([copias_exatas, copias_formatadas])
    chave_ordem = np.concatenate([np.arange(n, dtype=float), rng.uniform(0, n, size=len(copias))])
    bruto = pd.concat([texto, copias], ignore_index=True)
    bruto = bruto.iloc[np.argsort(chave_ordem, kind="mergesort")].reset_index(drop=True)
    inverso = {v: k for k, v in config.MAPA_COLUNAS_BRUTAS.items()}
    bruto = bruto[list(config.MAPA_COLUNAS_BRUTAS.values())].rename(columns=inverso)

    config.DIR_RAW_SIMULADO.mkdir(parents=True, exist_ok=True)
    caminho = config.CAMINHO_BRUTO_SIMULADO
    bruto.to_csv(caminho, sep=";", index=False, encoding="utf-8-sig", lineterminator="\n")

    gabarito = {
        "descricao": "Gabarito da injeção de problemas de qualidade no painel simulado (não é dado real).",
        "semente_simulacao": config.SEMENTE_SIMULACAO,
        "semente_problemas": config.SEMENTE_PROBLEMAS,
        "versao_modelo": config.VERSAO_MODELO,
        "snapshots_usados": sorted(snapshots),
        "data_inicio": painel["data"].min().strftime("%Y-%m-%d"),
        "data_fim": painel["data"].max().strftime("%Y-%m-%d"),
        "linhas_limpas": int(n),
        "linhas_brutas": int(len(bruto)),
        "arquivo": caminho.name,
        "sha256": _sha256(caminho),
        "gerado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "duplicatas_exatas": n_exatas,
        "duplicatas_formatadas": n_formatadas,
        **gab,
        "celulas_ausentes": celulas_ausentes,
    }
    with open(config.CAMINHO_GABARITO_SIMULADO, "w", encoding="utf-8", newline="\n") as arq:
        json.dump(gabarito, arq, ensure_ascii=False, indent=2)
    logger.info("Bruto simulado gravado: %s (%d linhas = %d limpas + %d duplicatas exatas + %d formatadas; %d células ausentes)",
                config.caminho_relativo(caminho), len(bruto), n, n_exatas, n_formatadas, total)
    return caminho, gabarito
