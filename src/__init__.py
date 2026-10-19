"""Pacote do pipeline de análise da transição de canais de venda de MEIs e MEs no Brasil.

O pipeline segue as etapas extração → limpeza → tratamento → transformação → visualização,
combinando dados públicos oficiais (IBGE/SIDRA e BCB/SGS) com um painel simulado e calibrado
de micro e pequenos negócios do varejo.
"""

__version__ = "1.0.0"


class ErroExtracao(Exception):
    """Falha ao obter dados de uma fonte externa (API ou snapshot local)."""

    def __init__(self, fonte_id: str, motivo: str) -> None:
        """Cria o erro com a identificação da fonte e o motivo da falha.

        Args:
            fonte_id: identificador da fonte (ex.: ``pmc_8880``).
            motivo: descrição legível do problema.
        """
        self.fonte_id = fonte_id
        self.motivo = motivo
        super().__init__(f"[{fonte_id}] {motivo}")


class ErroQualidadeDados(Exception):
    """Violação de um invariante de qualidade (grão, cobertura, faixas de KPI, tetos legais)."""
