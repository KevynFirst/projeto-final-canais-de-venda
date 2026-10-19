"""Orquestrador do pipeline de transição de canais de venda (MEIs e MEs no Brasil, 2018–2026).

Uso:
    python main.py                 # offline: usa os snapshots versionados em data/raw/api
    python main.py --atualizar     # baixa novamente as fontes oficiais e grava novos snapshots
    python main.py --nivel-log DEBUG

Etapas: extração → limpeza → simulação calibrada + arquivo bruto → limpeza do bruto → tratamento
(KPIs) → transformação (tabelas e CSV final) → visualização (10 gráficos PNG).
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import traceback

import pandas as pd

from src import ErroExtracao, ErroQualidadeDados
from src import config, extracao, limpeza, transformacao, tratamento, visualizacao

logger = logging.getLogger("pipeline")


def configurar_logging(nivel: str = "INFO") -> None:
    """Configura o log no console e em ``outputs/logs/pipeline.log`` (UTF-8, sobrescrito a cada execução).

    Args:
        nivel: nível mínimo de log.
    """
    config.DIR_LOGS.mkdir(parents=True, exist_ok=True)
    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    raiz = logging.getLogger()
    raiz.handlers.clear()
    raiz.setLevel(getattr(logging, nivel))
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formato)
    arquivo = logging.FileHandler(config.CAMINHO_LOG, mode="w", encoding="utf-8")
    arquivo.setFormatter(formato)
    raiz.addHandler(console)
    raiz.addHandler(arquivo)
    for ruidoso in ("matplotlib", "PIL", "urllib3"):
        logging.getLogger(ruidoso).setLevel(logging.WARNING)


def ler_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    """Lê os argumentos de linha de comando.

    Args:
        argv: argumentos (padrão: ``sys.argv``).

    Returns:
        Namespace com ``atualizar`` e ``nivel_log``.
    """
    parser = argparse.ArgumentParser(description="Pipeline de análise da transição de canais de venda de MEIs e MEs.")
    parser.add_argument("--atualizar", action="store_true", help="baixa novamente as fontes oficiais e grava novos snapshots")
    parser.add_argument("--nivel-log", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="nível de log (padrão: INFO)")
    return parser.parse_args(argv)


def executar(atualizar: bool) -> None:
    """Executa o pipeline completo.

    Args:
        atualizar: se ``True``, baixa novamente as fontes oficiais.
    """
    inicio = time.monotonic()
    logger.info("Início do pipeline (modo %s)", "atualização" if atualizar else "offline")
    # 1. Extração dos dados reais
    brutos = extracao.obter_dados_reais(atualizar)
    # 2. Limpeza dos dados reais
    reais, rel_reais = limpeza.limpar_dados_reais(brutos)
    data_fim = config.calcular_data_fim(reais["pmc_8880"]["data"].max(),
                                        reais["pmc_8882"].dropna(subset=["vol_nsa"])["data"].max(),
                                        reais["ipca"]["data"].max(), pd.Timestamp.now())
    logger.info("Período da série: %s a %s", config.DATA_INICIO.strftime("%Y-%m"), data_fim.strftime("%Y-%m"))
    # 3. Simulação calibrada e arquivo bruto com problemas de qualidade
    painel = extracao.simular_painel_canais(reais["pmc_8882"], reais["ipca"], data_fim)
    caminho_bruto, gabarito = extracao.gravar_painel_bruto(painel, reais["snapshots"])
    # 4. Limpeza do painel bruto
    painel_limpo, rel_painel = limpeza.limpar_painel_simulado(caminho_bruto, gabarito)
    limpeza.gravar_relatorio_qualidade({"dados_reais": rel_reais, "painel_simulado": rel_painel})
    # 5. Tratamento: períodos, macro, medidas derivadas, KPIs e validações
    base = tratamento.preparar_base_analitica(painel_limpo, reais, data_fim)
    # 6. Transformação: tabelas de apoio e CSV final
    tabelas = transformacao.construir_tabelas(base, reais)
    csv_final = transformacao.exportar_csv_final(base, config.CAMINHO_CSV_FINAL)
    caminhos_tabelas = transformacao.exportar_tabelas(tabelas)
    # 7. Visualização
    graficos = visualizacao.gerar_graficos(tabelas, reais["fonte_ipca"])
    # 8. Resumo
    logger.info("Resumo: %d linhas | período %s a %s | IPCA: %s", len(base), config.DATA_INICIO.strftime("%Y-%m"),
                data_fim.strftime("%Y-%m"), reais["fonte_ipca"])
    for caminho in [caminho_bruto, config.CAMINHO_GABARITO_SIMULADO, config.CAMINHO_RELATORIO_QUALIDADE, csv_final]:
        logger.info("Arquivo: %s", config.caminho_relativo(caminho))
    logger.info("Arquivos: %d tabelas em %s e %d gráficos em %s", len(caminhos_tabelas), config.caminho_relativo(config.DIR_TABELAS),
                len(graficos), config.caminho_relativo(config.DIR_GRAFICOS))
    logger.info("Pipeline concluído em %.1f s", time.monotonic() - inicio)


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da linha de comando.

    Args:
        argv: argumentos (padrão: ``sys.argv``).

    Returns:
        Código de saída: 0 = sucesso; 1 = erro tratado.
    """
    args = ler_argumentos(argv)
    configurar_logging(args.nivel_log)
    try:
        executar(args.atualizar)
    except (ErroExtracao, ErroQualidadeDados, ValueError, OSError) as exc:
        logger.error("Falha no pipeline: %s", exc)
        logger.debug("Detalhes:\n%s", traceback.format_exc())
        return 1
    except Exception:
        logger.exception("Erro inesperado no pipeline")
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
