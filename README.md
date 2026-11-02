# Selic × Inadimplência no Brasil (2012–2026)

> **Quando os juros sobem, quanto tempo leva para os atrasos aparecerem — e a Selic explica a alta
> recente da inadimplência das famílias?**

Análise com 14 anos de dados públicos do Banco Central para entender como a taxa básica de juros se
transmite à inadimplência de pessoas físicas e jurídicas — uma questão central para a política de
crédito e para o cálculo da provisão para perdas (IFRS 9 / Resolução CMN 4.966).

![Selic e inadimplência de pessoas físicas](figuras/01_selic_vs_inad_pf.png)

---

## Resumo executivo

| Pergunta | Resposta |
|---|---|
| A inadimplência reage à Selic? | Sim, com defasagem: **~6 meses (PF)** e **~9 meses (PJ)** |
| Quem é mais sensível? | **Pessoa jurídica** — reage mais tarde, mas com mais intensidade e consistência |
| Quanto? | +4 p.p. na Selic ≈ **+0,44 p.p.** de inadimplência PF e **+0,59 p.p.** PJ |
| A Selic explica a alta recente das famílias? | **Não.** A PF subiu +2,24 p.p. desde nov/2024, **~4× o previsto** pela relação histórica |

**Implicação para o negócio:** em ciclos de alta, o efeito sobre a carteira PJ é previsível e chega
em cerca de 9 meses — tempo para ajustar política e provisão. Na carteira PF, a Selic explica apenas
~27% da variação da inadimplência: monitorar só os juros subestima o risco das famílias.

---

## Principais resultados

### 1. A inadimplência reage com defasagem
A correlação entre a variação da Selic e a da inadimplência é máxima **6 meses depois para PF** e
**9 meses depois para PJ**.

![Correlação por defasagem](figuras/04_correlacao_defasada.png)

### 2. Hipótese rejeitada: a PF *não* é mais sensível que a PJ
| | Defasagem | Sensibilidade (inclinação) | Correlação | R² |
|---|---|---|---|---|
| Pessoa física | 6 meses | 0,111 | 0,52 | 0,27 |
| Pessoa jurídica | 9 meses | **0,148** | **0,81** | **0,66** |

A PF reage **antes**; a PJ reage **com mais força e consistência**. Interpretação: o crédito PJ é em
boa parte pós-fixado, mas empresas têm caixa, garantias e capacidade de renegociar, e demoram mais para
atrasar. A inadimplência das famílias depende também de emprego, renda e endividamento.

![Sensibilidade PF e PJ](figuras/05_sensibilidade_pf_pj.png)

### 3. O achado principal: a alta recente da PF não é explicada pela Selic
| Ciclo 2024–2025 (Selic ~+4,5 p.p.) | Previsto pela relação histórica | Observado (nov/24 → set/26) |
|---|---|---|
| Pessoa jurídica | ~+0,7 p.p. | +0,78 p.p. ✅ |
| Pessoa física | ~+0,5 p.p. | **+2,24 p.p.** ⚠️ |

As empresas se comportaram como o histórico prevê; as famílias, não. Algo além dos juros pressiona a
inadimplência PF desde 2025 — candidatos a investigar: endividamento, comprometimento de renda e
possíveis efeitos da mudança contábil de 2025.

### 4. Contexto: juro real em níveis historicamente altos
O juro real ex-post atingiu **10,78% em fev/2026**, o maior da série, e segue em 8,77% (set/2026) —
mais que o dobro da média do período (~4%).

![Juro real](figuras/03_juro_real.png)

---

## Metodologia

**Dados:** API pública do SGS (Banco Central do Brasil).

| Série | Código SGS |
|---|---|
| Selic meta (% a.a.) | 432 |
| IPCA — variação mensal (%) | 433 |
| Inadimplência — total / PJ / PF (%) | 21082 / 21083 / 21084 |
| Spread médio das operações de crédito (p.p.) | 20783 |

**Pipeline:**
```
API do BCB → src/coleta.py → data/bruto/ → src/tratamento.py → data/tratado/ → notebooks
```

**Decisões de tratamento:**
- Selic diária → valor vigente no último dia de cada mês.
- IPCA 12 meses por juros compostos; juro real ex-post pela equação de Fisher.
- Análise sobre **variações em 12 meses**, não níveis — evita correlação espúria entre séries com
  tendência e remove a sazonalidade.
- **Período da pandemia excluído** (mar/2020–dez/2022) na análise principal: carências e renegociações
  derrubaram artificialmente a inadimplência enquanto a Selic caía, inflando a correlação PF
  (0,64 → 0,52 sem a pandemia).

**Verificações de qualidade:**
- **Quebra de série (Resolução CMN 4.966, jan/2025):** sem evidência de salto abrupto; a alta é
  gradual e coerente com o ciclo da Selic.
- **Sazonalidade:** a inadimplência PF cai em média em junho e dezembro (fechamentos semestrais de
  balanço, baixas a prejuízo, 13º salário) e sobe em janeiro.

**Técnicas:** correlação defasada (0 a 24 meses) e regressão linear simples para estimar a
sensibilidade, com e sem o período da pandemia.

---

## Limitações
- As variações em 12 meses se sobrepõem: a amostra contém, na prática, 3–4 ciclos da Selic. Os
  resultados indicam direção e defasagem, não prova estatística.
- Análise bivariada: não controla emprego, renda, endividamento nem programas de renegociação
  (ex.: Desenrola).
- Correlação não implica causalidade.
- Dados de crédito divulgados com ~2 meses de defasagem.

## Próximos passos
- Incluir endividamento e comprometimento de renda das famílias para explicar a alta da
  inadimplência PF.
- Modelo multivariado (Selic, desemprego, renda) e comparação com o juro real ex-ante.
- Usar as relações estimadas como cenário macro (forward-looking) no cálculo de perda esperada.

---

## Estrutura do projeto
```
painel-credito-bcb/
├── data/
│   ├── bruto/              # dados como vieram da API (um CSV por série)
│   └── tratado/            # base mensal com indicadores derivados
├── figuras/                # gráficos usados no README e nas publicações
├── notebooks/
│   ├── 01_exploracao.ipynb # análise exploratória e qualidade dos dados
│   └── 02_defasagem.ipynb  # correlação defasada, sensibilidade e hipóteses
├── src/
│   ├── coleta.py           # coleta das séries na API do BCB
│   └── tratamento.py       # limpeza, base mensal e indicadores
└── requirements.txt
```

## Como reproduzir
```bash
git clone https://github.com/nediao03/painel-credito-bcb.git
cd painel-credito-bcb
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash) | Linux/Mac: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/coleta.py               # baixa os dados atualizados do Banco Central
python src/tratamento.py           # gera data/tratado/base_mensal.csv
```
Depois, abra os notebooks em `notebooks/`.

**Tecnologias:** Python · pandas · NumPy · Matplotlib · Requests · Jupyter · Git

---

## Autor
**Guilherme Fernandes da Costa** — Analista e Cientista de Dados 
(https://www.linkedin.com/in/guilhermefernandesdacosta/)