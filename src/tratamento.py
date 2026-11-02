"""
Tratamento dos dados brutos do Banco Central.
Junta as séries em uma base mensal e cria indicadores derivados.
Salva o resultado em data/tratado/base_mensal.csv.

Uso (na raiz do projeto):  python src/tratamento.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PASTA_BRUTO = RAIZ / "data" / "bruto"
PASTA_TRATADO = RAIZ / "data" / "tratado"

SERIES_MENSAIS = ["ipca_mensal", "inad_total", "inad_pf", "inad_pj", "spread_total"]


def ler_serie(nome):
    """Lê um CSV bruto e devolve uma série com a data como índice."""
    df = pd.read_csv(PASTA_BRUTO / f"{nome}.csv", parse_dates=["data"])
    return df.set_index("data")["valor"].rename(nome)


def montar_base():
    # A Selic é diária: pegamos o valor vigente no último dia de cada mês
    selic = ler_serie("selic_meta").resample("MS").last()

    # As demais já são mensais (datadas no dia 1º de cada mês)
    mensais = [ler_serie(nome) for nome in SERIES_MENSAIS]

    base = pd.concat([selic, *mensais], axis=1).sort_index()
    base.index.name = "data"

    # --- Indicadores derivados ---
    # IPCA acumulado em 12 meses: juros compostos, não soma simples
    fator = 1 + base["ipca_mensal"] / 100
    base["ipca_12m"] = (fator.rolling(12).apply(lambda x: x.prod(), raw=True) - 1) * 100

    # Juro real (equação de Fisher): quanto a Selic rende acima da inflação
    base["juro_real"] = ((1 + base["selic_meta"] / 100) / (1 + base["ipca_12m"] / 100) - 1) * 100

    # Variação da Selic em 12 meses (em pontos percentuais)
    base["selic_var_12m"] = base["selic_meta"].diff(12)

    return base.round(2)


def relatorio_qualidade(base):
    """Mostra um resumo para conferir se o tratamento deu certo."""
    print(f"Período: {base.index.min():%m/%Y} a {base.index.max():%m/%Y} ({len(base)} meses)\n")
    print("Valores faltantes por coluna:")
    print(base.isna().sum().to_string())
    completos = base.dropna()
    print(f"\nÚltimo mês com todas as séries: {completos.index.max():%m/%Y}")
    print("\nÚltimos 3 meses completos:")
    print(completos.tail(3).to_string())


def main():
    PASTA_TRATADO.mkdir(parents=True, exist_ok=True)
    base = montar_base()
    base.to_csv(PASTA_TRATADO / "base_mensal.csv")
    relatorio_qualidade(base)
    print(f"\nBase salva em {PASTA_TRATADO / 'base_mensal.csv'}")


if __name__ == "__main__":
    main()