"""Testes unitários do pipeline (offline, rápidos): ``python -m unittest discover -s tests -v``."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config  # noqa: E402
from src.extracao import (  # noqa: E402
    aliquota_efetiva_simples,
    sortear_celulas_ausentes,
    take_rate_item_2026,
    tarifa_marketplace_ml,
)
from src.limpeza import (  # noqa: E402
    imputar_ausentes,
    limpar_pac,
    normalizar_sidra,
    normalizar_texto,
    parse_inteiro,
    parse_mes_referencia,
    parse_numero_br,
)
from src.tratamento import adicionar_periodos, kpis_de_componentes  # noqa: E402


def _componentes(**valores: list[float]) -> pd.DataFrame:
    """Cria linhas com todas as medidas aditivas (padrões coerentes) para testar os KPIs."""
    n = len(next(iter(valores.values())))
    base = {
        "negocios_ativos": [10] * n, "receita_bruta": [10000.0] * n, "pedidos": [100] * n, "clientes_ativos": [90] * n,
        "clientes_novos": [60] * n, "clientes_recorrentes": [30] * n, "clientes_ativos_mes_anterior": [95] * n,
        "investimento_marketing": [600.0] * n, "comissoes_tarifas": [1200.0] * n, "frete_subsidiado": [300.0] * n,
        "cmv": [5500.0] * n, "custos_fixos": [1500.0] * n, "impostos_fixos": [700.0] * n, "impostos_variaveis": [0.0] * n,
    }
    base.update(valores)
    df = pd.DataFrame(base)
    df["receita_bruta_real"] = df["receita_bruta"]
    df["impostos"] = df["impostos_fixos"] + df["impostos_variaveis"]
    df["margem_contribuicao"] = df["receita_bruta"] - df["cmv"] - df["comissoes_tarifas"] - df["frete_subsidiado"] - df["impostos_variaveis"]
    df["margem_liquida"] = df["margem_contribuicao"] - df["investimento_marketing"] - df["custos_fixos"] - df["impostos_fixos"]
    df["margem_liquida_real"] = df["margem_liquida"]
    return df


def _serie_sintetica(porte: str = "MEI", n: int = 13) -> pd.DataFrame:
    """Série mensal coerente (2018-01 em diante) com pico de dezembro na receita."""
    datas = pd.date_range("2018-01-01", periods=n, freq="MS")
    receita = np.where(datas.month == 12, 2000.0, 1000.0)
    pedidos = np.round(receita / 50.0)
    ativos = np.round(pedidos / 1.1)
    recorrentes = np.round(ativos * 0.3)
    novos = ativos - recorrentes
    anterior = np.concatenate([[ativos[0]], ativos[:-1]])
    negocios = np.full(n, 10.0)
    df = pd.DataFrame({
        "data": datas, "canal": "Loja Física", "porte": porte, "segmento": "Moda e Acessórios",
        "negocios_ativos": negocios, "receita_bruta": receita, "pedidos": pedidos, "clientes_ativos": ativos,
        "clientes_novos": novos, "clientes_recorrentes": recorrentes, "clientes_ativos_mes_anterior": anterior,
        "investimento_marketing": novos * 5.0, "comissoes_tarifas": receita * 0.12, "frete_subsidiado": receita * 0.05,
        "cmv": receita * 0.55, "custos_fixos": negocios * 300.0,
        "impostos_fixos": np.round(negocios * config.das_mei_em(datas), 2) if porte == "MEI" else np.zeros(n),
        "impostos_variaveis": np.zeros(n) if porte == "MEI" else receita * 0.04,
    })
    return df


class TestTextoEParsers(unittest.TestCase):
    """Testes 1–3: rótulos, datas e números."""

    def test_rotulos(self) -> None:
        for coluna, variantes in config.VARIANTES_ROTULOS.items():
            for canonico, lista in variantes.items():
                for v in lista + [canonico]:
                    self.assertEqual(config.MAPA_ROTULOS[coluna][normalizar_texto(v)], canonico)
        self.assertNotIn(normalizar_texto("Atacado"), config.MAPA_ROTULOS["canal"])

    def test_datas(self) -> None:
        for s in ("2020-03", "03/2020", "2020-03-01"):
            self.assertEqual(parse_mes_referencia(s), pd.Timestamp("2020-03-01"))
        for s in ("2020-13", "13/2020", "2020-03-15", "março 2020"):
            with self.assertRaises(ValueError):
                parse_mes_referencia(s)

    def test_numeros(self) -> None:
        for s in ("1.234,56", "R$ 1.234,56", "1234.56"):
            self.assertAlmostEqual(parse_numero_br(s), 1234.56)
        self.assertEqual(parse_inteiro("1.234"), 1234)
        with self.assertRaises(ValueError):
            parse_inteiro("abc")


class TestKpis(unittest.TestCase):
    """Teste 4: razão de somas e identidade do ponto de equilíbrio."""

    def test_razao_de_somas(self) -> None:
        df = _componentes(receita_bruta=[100.0, 300.0], pedidos=[10, 20])
        linhas = kpis_de_componentes(df)
        somas = df.sum().to_frame().T
        agregado = kpis_de_componentes(somas)["ticket_medio"].iloc[0]
        self.assertAlmostEqual(agregado, 400.0 / 30.0)
        self.assertNotAlmostEqual(agregado, linhas["ticket_medio"].mean())

    def test_identidade_ponto_equilibrio(self) -> None:
        df = _componentes(receita_bruta=[10000.0, 14000.0], cmv=[5500.0, 7600.0], investimento_marketing=[600.0, 900.0])
        k = kpis_de_componentes(df)
        variaveis = df[["cmv", "comissoes_tarifas", "frete_subsidiado", "impostos_variaveis", "investimento_marketing"]].sum(axis=1)
        v = variaveis / df["receita_bruta"]
        esquerda = df["margem_liquida"] / df["negocios_ativos"]
        direita = (k["receita_por_negocio"] - k["ponto_equilibrio_receita"]) * (1 - v)
        for a, b in zip(esquerda, direita):
            self.assertTrue(math.isclose(a, b, rel_tol=1e-9))


class TestRegras(unittest.TestCase):
    """Testes 5–8: Simples Nacional, períodos, tarifas e registro de premissas."""

    def test_simples(self) -> None:
        self.assertAlmostEqual(aliquota_efetiva_simples(150000), 0.04)
        self.assertAlmostEqual(aliquota_efetiva_simples(240000), (240000 * 0.073 - 5940) / 240000)
        self.assertAlmostEqual(aliquota_efetiva_simples(240000), 0.04825)
        self.assertAlmostEqual(aliquota_efetiva_simples(360000), 0.0565)

    def test_periodos(self) -> None:
        datas = pd.to_datetime(["2020-02-01", "2020-03-01", "2022-05-01", "2022-06-01", "2024-12-01", "2025-01-01"])
        p = adicionar_periodos(pd.DataFrame({"data": datas}))
        self.assertEqual(p["fase"].tolist(), ["Pré-pandemia", "Pandemia", "Pandemia", "Pós-pandemia", "Pós-pandemia", "Pós-pandemia"])
        self.assertEqual(p["recorte_temporal"].iloc[4], "Pós-pandemia (jun/2022–dez/2024)")
        self.assertEqual(p["recorte_temporal"].iloc[5], "Cenário Atual (2025–2026)")
        self.assertEqual(p["flag_cenario_atual"].tolist(), [0, 0, 0, 0, 0, 1])

    def test_tarifa_ml_simulada(self) -> None:
        def q(ticket: float, limite: float) -> float:
            mu = math.log(ticket) - 0.18
            return 0.5 * (1 + math.erf((math.log(limite) - mu) / (0.6 * math.sqrt(2))))

        self.assertAlmostEqual(tarifa_marketplace_ml(pd.Timestamp("2019-06-01"), 8500.0, 100),
                               8500 * 0.11 + 100 * 5.0 * q(85.0, 120.0), places=6)
        self.assertAlmostEqual(tarifa_marketplace_ml(pd.Timestamp("2024-06-01"), 8500.0, 100),
                               8500 * 0.12 + 100 * 6.0 * q(85.0, 79.0), places=6)
        self.assertAlmostEqual(tarifa_marketplace_ml(pd.Timestamp("2018-03-01"), 8500.0, 100), 8500 * 0.11, places=6)

    def test_tarifas_2026(self) -> None:
        esperados = {50: 0.29, 79.99: 0.2563, 80: 0.34, 100: 0.34, 200: 0.27, 500: 0.192}
        for valor, taxa in esperados.items():
            self.assertAlmostEqual(take_rate_item_2026("shopee_cnpj", valor), taxa, places=4)
        self.assertAlmostEqual(take_rate_item_2026("ml_classico", 50), 0.24)
        self.assertAlmostEqual(take_rate_item_2026("ml_classico", 100), 0.12)
        self.assertAlmostEqual(take_rate_item_2026("amazon_individual", 100), 0.145)

    def test_premissas(self) -> None:
        self.assertEqual(set(config.PARAMETROS), set(config.ORIGEM_PARAMETROS))
        for chave, origem in config.ORIGEM_PARAMETROS.items():
            if origem.tipo != "premissa do autor":
                self.assertTrue(origem.referencia.startswith(("https://", "http://")), chave)


class TestImputacao(unittest.TestCase):
    """Testes 9–10: imputação por razão."""

    def test_pico_de_dezembro(self) -> None:
        verdadeiro = _serie_sintetica()
        df = verdadeiro.copy()
        dez = df["data"] == "2018-12-01"
        df.loc[dez, "receita_bruta"] = np.nan
        imputado, rel = imputar_ausentes(df)
        linha = imputado[imputado["data"] == "2018-12-01"].iloc[0]
        receita = linha["receita_bruta"]
        self.assertLessEqual(abs(receita / 2000.0 - 1), 0.01)
        mc = (receita - linha["cmv"] - linha["comissoes_tarifas"] - linha["frete_subsidiado"]) / receita
        self.assertLessEqual(abs(mc - 0.28), 0.01)
        self.assertEqual(rel["imputacoes_por_metodo"], {"razao_cmv": 1})
        self.assertEqual(int(linha["qtd_campos_imputados"]), 1)

    def test_demais_regras(self) -> None:
        verdadeiro = _serie_sintetica()
        casos = {
            "pedidos": "2018-06-01", "clientes_ativos": "2018-03-01", "clientes_novos": "2018-04-01",
            "clientes_recorrentes": "2018-05-01", "impostos_fixos": "2018-07-01", "impostos_variaveis": "2018-08-01",
            "negocios_ativos": "2018-09-01",
        }
        for coluna, data in casos.items():
            df = verdadeiro.copy()
            mascara = df["data"] == data
            df.loc[mascara, coluna] = np.nan
            imputado, _ = imputar_ausentes(df)
            linha = imputado[imputado["data"] == data].iloc[0]
            certo = verdadeiro[mascara].iloc[0]
            if coluna == "pedidos":
                self.assertGreaterEqual(linha["pedidos"], linha["clientes_ativos"])
                self.assertLessEqual(abs(linha["pedidos"] - certo["pedidos"]), 1)
            elif coluna == "negocios_ativos":
                self.assertLessEqual(abs(linha["negocios_ativos"] - certo["negocios_ativos"]), 1)
            elif coluna == "impostos_variaveis":
                self.assertEqual(linha["impostos_variaveis"], 0.0)
            else:
                self.assertAlmostEqual(linha[coluna], certo[coluna], places=2)
            self.assertEqual(linha["clientes_ativos"], linha["clientes_novos"] + linha["clientes_recorrentes"])


class TestPacEInjecao(unittest.TestCase):
    """Testes 11–12: soma estrita da PAC e injeção de ausentes."""

    @staticmethod
    def _sidra(ano: int, classes_valores: dict[int, dict[int, str]], empresas: dict[int, str]) -> list[dict]:
        cab = {"V": "Valor", "D1C": "Brasil (Código)", "D2C": "Variável (Código)", "D3C": "Ano (Código)",
               "D4C": "Formas de comercialização (Código)", "D5C": "Divisão de comércio, grupo e classe de atividade (Código)"}
        cab = {k: v for k, v in cab.items()}
        cab.update({"D1N": "Brasil", "D2N": "Variável", "D3N": "Ano", "D4N": "Formas de comercialização",
                    "D5N": "Divisão de comércio, grupo e classe de atividade"})
        registros = [cab]
        for classe, formas in classes_valores.items():
            for forma, valor in formas.items():
                registros.append({"V": valor, "D1C": "1", "D2C": "866", "D3C": str(ano), "D4C": str(forma), "D5C": str(classe),
                                  "D1N": "Brasil", "D2N": "Receita", "D3N": str(ano), "D4N": "f", "D5N": "c"})
            registros.append({"V": empresas[classe], "D1C": "1", "D2C": "540", "D3C": str(ano), "D4C": str(config.PAC_FORMA_INTERNET),
                              "D5C": str(classe), "D1N": "Brasil", "D2N": "Empresas", "D3N": str(ano), "D4N": "f", "D5N": "c"})
        return registros

    def test_soma_estrita(self) -> None:
        formas_total = {f: "100" for f in config.PAC_FORMAS}
        formas_total[106745] = "-"
        formas_total[config.PAC_FORMA_INTERNET] = "50"
        formas_moda = {f: "10" for f in config.PAC_FORMAS}
        formas_moda[106746] = "X"
        d9349 = normalizar_sidra(self._sidra(2019, {106721: formas_total, 106727: formas_moda}, {106721: "7", 106727: "3"}))
        d10656 = normalizar_sidra(self._sidra(2024, {83337: dict(formas_total)}, {83337: "9"}))
        self.assertEqual(d9349.attrs["simbolos"]["-"], 1)
        self.assertEqual(d9349.attrs["simbolos"]["X"], 1)
        pac = limpar_pac(d9349, d10656)
        total = pac[(pac["ano"] == 2019) & (pac["papel"] == "total")].iloc[0]
        self.assertAlmostEqual(total["receita_total_mil_reais"], 550.0)
        self.assertAlmostEqual(total["participacao_internet"], 50.0 / 550.0)
        self.assertEqual(total["situacao"], "ok")
        moda = pac[(pac["ano"] == 2019) & (pac["papel"] == "moda")].iloc[0]
        self.assertTrue(pd.isna(moda["receita_total_mil_reais"]))
        self.assertTrue(pd.isna(moda["participacao_internet"]))
        self.assertEqual(moda["situacao"], "sigilo")

    def test_injecao_ausentes(self) -> None:
        n = 3120
        primeiro = np.zeros(n, dtype=bool)
        primeiro[:30] = True
        linhas, colunas = sortear_celulas_ausentes(np.random.default_rng(config.SEMENTE_PROBLEMAS), n, primeiro)
        self.assertEqual(len(linhas), 1092)
        self.assertEqual(len(set(linhas.tolist())), 1092)
        self.assertTrue((np.bincount(colunas, minlength=14) == 78).all())
        idx = config.COLUNAS_MEDIDA_BRUTAS.index("clientes_ativos_mes_anterior")
        self.assertFalse(any(primeiro[l] and c == idx for l, c in zip(linhas, colunas)))
        l2, c2 = sortear_celulas_ausentes(np.random.default_rng(config.SEMENTE_PROBLEMAS), n, primeiro)
        self.assertTrue((linhas == l2).all() and (colunas == c2).all())


if __name__ == "__main__":
    unittest.main()
