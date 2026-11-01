"""
Coleta de séries temporais do SGS (Sistema Gerenciador de Séries do Banco Central).
Salva os dados brutos em data/bruto/, um CSV por série.

Uso (na raiz do projeto):  python src/coleta.py
"""
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

# Pasta de destino, calculada a partir da localização deste arquivo
PASTA_BRUTO = Path(__file__).resolve().parent.parent / "data" / "bruto"

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
DATA_INICIO = date(2012, 1, 1)

# nome_da_coluna: (código SGS, descrição)
SERIES = {
    "selic_meta":   (432,   "Meta da taxa Selic definida pelo Copom (% a.a.)"),
    "ipca_mensal":  (433,   "IPCA - variação mensal (%)"),
    "inad_total":   (21082, "Inadimplência da carteira de crédito - total (%)"),
    "inad_pj":      (21083, "Inadimplência da carteira de crédito - PJ (%)"),
    "inad_pf":      (21084, "Inadimplência da carteira de crédito - PF (%)"),
    "spread_total": (20783, "Spread médio das operações de crédito - total (p.p.)"),
}


def baixar_janela(codigo, inicio, fim, tentativas=3):
    """Baixa um intervalo de datas de uma série, tentando de novo em caso de falha."""
    parametros = {
        "formato": "json",
        "dataInicial": inicio.strftime("%d/%m/%Y"),
        "dataFinal": fim.strftime("%d/%m/%Y"),
    }
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(
                URL.format(codigo=codigo),
                params=parametros,
                headers={"User-Agent": "painel-credito-bcb"},
                timeout=60,
            )
            if resposta.status_code == 404:  # sem dados nesse intervalo
                return []
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException as erro:
            print(f"   tentativa {tentativa} falhou: {erro}")
            time.sleep(2 * tentativa)
    raise RuntimeError(f"Não foi possível baixar a série {codigo}")


def baixar_serie(codigo):
    """Baixa a série inteira em janelas de 5 anos (a API limita séries diárias a 10 anos)."""
    registros = []
    inicio = DATA_INICIO
    hoje = date.today()
    while inicio <= hoje:
        fim = min(date(inicio.year + 4, 12, 31), hoje)
        registros += baixar_janela(codigo, inicio, fim)
        inicio = date(fim.year + 1, 1, 1)

    if not registros:
        raise ValueError(f"A série {codigo} veio vazia. Confira o código no portal SGS.")

    df = pd.DataFrame(registros)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df.drop_duplicates("data").sort_values("data")


def main():
    PASTA_BRUTO.mkdir(parents=True, exist_ok=True)
    for nome, (codigo, descricao) in SERIES.items():
        print(f"Baixando {nome} (SGS {codigo}): {descricao}")
        df = baixar_serie(codigo)
        df.to_csv(PASTA_BRUTO / f"{nome}.csv", index=False)
        ultimo = df.iloc[-1]
        print(f"   {len(df)} registros | {df['data'].min():%m/%Y} a {df['data'].max():%m/%Y}"
              f" | último valor: {ultimo['valor']} em {ultimo['data']:%d/%m/%Y}")
    print(f"\nPronto! Arquivos salvos em {PASTA_BRUTO}")


if __name__ == "__main__":
    main()