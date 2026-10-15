# 1º turno — seleção dos finalistas Grok via OCI

## Sumário executivo

**Classificados para a comparação do 2º turno: Grok 4.3 e Grok 4.20 non-reasoning**, com notas de **97,15** e **73,39**. O 1º turno compara os sete identificadores sob as mesmas regras e reserva as duas vagas para as configurações aprovadas com maior pontuação. O [2º turno](../README.md) apresenta a comparação das 100 intenções entre os finalistas.

Foram avaliadas **12 novas respostas por identificador**, com as mesmas perguntas e três casos de cada tema: culinária, esportes, clima e entretenimento. As 84 respostas exigiram 91 tentativas HTTP: 7 rejeições de quota compartilhada foram recuperadas uma vez, com preservação das evidências. O custo dessas rejeições sem `usage` permanece desconhecido.

**Custo conhecido desta etapa: US$ 9,458169**, com tokens e websearch incluídos. **Acumulado conhecido do projeto: US$ 20,963443 em 294 respostas**, frente ao teto autorizado de US$ 50. Valores calculados a preço de lista Oracle; não são conciliação de fatura.

## Regras do 1º turno — corte e duas vagas

Os critérios foram congelados antes das novas inferências: **50% eficiência de custo total, 30% confiabilidade operacional da busca e 20% eficiência de latência**. Cada tema pesa 25%, com três casos igualmente ponderados. Para cada pergunta, eficiência é a razão entre o melhor custo/tempo confiável e o custo/tempo do identificador. Falhas operacionais recebem zero em todos os componentes.

O corte é **70/100**, com **12 custos conhecidos e ao menos 11 buscas confiáveis por ID**. Busca confiável exige HTTP 200, busca concluída com fontes e citações, texto final e ausência de truncamento; **não mede correção factual**. Os sete IDs foram testados, mas representam cinco configurações: aliases com e sem `0309` têm suas notas promediadas e não ocupam duas vagas.

## Apuração dos sete identificadores

| ID OCI | Nota /100 | Busca confiável | Passa corte | Tokens/interação | Buscas/interação | USD/interação | Mediana s |
|---|---|---|---|---|---|---|---|
| `xai.grok-4.3` | 97,15 | 12/12 | sim | 22.087,92 | 3,25 | 0,042403 | 11,37 |
| `xai.grok-4.20-0309-non-reasoning` | 74,01 | 12/12 | sim | 49.058,42 | 6,75 | 0,072876 | 12,64 |
| `xai.grok-4.20-non-reasoning` | 72,76 | 12/12 | sim | 50.843,83 | 6,58 | 0,075544 | 12,38 |
| `xai.grok-4.20-reasoning` | 72,24 | 12/12 | sim | 37.148,58 | 4,67 | 0,060809 | 29,15 |
| `xai.grok-4.20-0309-reasoning` | 67,93 | 12/12 | não | 43.295,25 | 5,00 | 0,066099 | 33,05 |
| `xai.grok-4.6` | 45,51 | 12/12 | não | 84.555,58 | 8,00 | 0,167256 | 65,83 |
| `xai.grok-4.7` | 43,34 | 12/12 | não | 154.035,50 | 10,58 | 0,303195 | 50,16 |

## Seleção por configuração

| Configuração | Nota /100 | Passa corte | Selecionada | Frequência top 2 no bootstrap |
|---|---|---|---|---|
| `grok-4.3` | 97,15 | sim | sim | 100,0% |
| `grok-4.20-non-reasoning` | 73,39 | sim | sim | 99,8% |
| `grok-4.20-reasoning` | 70,08 | sim | não | 0,0% |
| `grok-4.6` | 45,51 | não | não | 0,0% |
| `grok-4.7` | 43,34 | não | não | 0,0% |

A configuração 4.20 reasoning também superou o corte agrupado (70,08), mas ficou em terceiro. Seu custo médio agrupado foi menor que o do non-reasoning, porém a maior latência reduziu sua nota com os pesos definidos. O corte de 70 é aplicado à média da configuração; cada alias precisa atender aos gates de custo conhecido e confiabilidade, não a um corte individual adicional.

A frequência no bootstrap descreve a sensibilidade a 2.000 reamostragens pareadas dos casos, estratificadas por tema. Não é probabilidade de superioridade nem intervalo de confiança populacional. Os grupos com aliases têm duas execuções de cada pergunta; continuam tendo somente 12 intenções distintas.

## Consumo e resultado financeiro

| Indicador | Total nas 84 respostas | Média/interação |
|---|---|---|
| Tokens de entrada, cache incluído | 5.097.015 | 60.678,75 |
| Tokens de cache, subconjunto da entrada | 2.469.760 | 29.401,90 |
| Tokens de saída, raciocínio incluído | 195.286 | 2.324,83 |
| Tokens de raciocínio, subconjunto da saída | 132.001 | 1.571,44 |
| **Total de tokens: entrada + saída** | **5.292.301** | **63.003,58** |
| Chamadas tarifadas de websearch | 538 | 6,40 |

| Componente | Total USD | USD/interação |
|---|---|---|
| Entrada sem cache | 4,575965 | 0,054476 |
| Entrada em cache | 1,239002 | 0,014750 |
| Saída | 0,953202 | 0,011348 |
| Websearch | 2,690000 | 0,032024 |
| Total | 9,458169 | 0,112597 |

Preços e SKUs estão em [oracle-prices.json](oracle-prices.json), incluindo as faixas curta e longa. Websearch custa US$ 5 por 1.000 chamadas. Cache e raciocínio não são somados novamente aos tokens totais. O acumulado de todas as etapas e sete IDs consta no [consolidado de 294 respostas](financial-consolidation.json); o [baseline anterior de 210](../financial-consolidation.json) foi preservado.

## Nota sobre a ordem de apresentação

“1º turno” identifica a etapa lógica de seleção. Na cronologia real, esta amostra foi executada depois do lote completo, como auditoria retrospectiva, e confirmou a dupla escolhida inicialmente por heurística. A apresentação em turnos não implica que essa apuração tenha causado a escolha original.

## Metodologia, exceções e limites

- Amostra determinística por hash dos prompts, sem usar métricas financeiras na função de seleção. Os 12 casos saem do dataset anterior de 100; não são holdout. Os dois candidatos originais já haviam recebido essas perguntas.
- Mesmo payload por pergunta, alterando somente o modelo; OCI Chicago Responses, ferramenta nativa `web_search`, sem API de inferência direta xAI. Ordem rotacionada e concorrência 2.
- Critérios, prompts e preços registrados antes das chamadas no [protocolo](PROTOCOLO.md) e no manifesto publicado no resumo. O piloto integra as 84 respostas.
- A aplicação do preço longo foi conciliada contra o contador monetário nativo, com correspondência única ao cálculo por SKUs Oracle; ver [adendo contábil](ADENDO-CONTABILIDADE.md). Nenhuma resposta cara foi descartada ou repetida.
- Sete HTTP 429 foram rejeições de quota compartilhada. A recuperação única e a inclusão de pausas entre grupos estão no [adendo operacional](ADENDO-TAXA.md). O tempo da pausa não integra a latência da requisição; a mudança de ritmo limita a comparação.
- `max_output_tokens=2400` é um parâmetro comum; o uso agregado de saída do ciclo de ferramentas superou esse valor em algumas respostas. A cobrança usa o `usage` integral.
- O estado de cache não foi controlado. Há uma [sensibilidade contábil sem desconto de cache](SENSIBILIDADES.md), exploratória e posterior ao início da coleta, sem alterar a seleção primária nem simular uma execução física sem cache.

Nesse cenário secundário, apenas `grok-4.3` supera o corte. A segunda vaga depende do desconto de cache observado e não se mantém nessa hipótese contábil; isso restringe a robustez da confirmação da dupla.

## Passagem ao 2º turno

O corte ponderado classifica Grok 4.3 e Grok 4.20 non-reasoning para as duas vagas. O [2º turno](../README.md) compara o custo de 100 intenções iguais por finalista e aponta economia de 43,38% com Grok 4.3. A nota do 1º turno justifica a classificação; o lote completo sustenta a comparação financeira da dupla. Não se pode extrapolar o desempenho dos demais modelos para 100 intenções nem afirmar qualidade factual equivalente.

## Evidências e reprodução

- [Relatório detalhado](results/screening-2026-10-15-v1/REPORT.md), [resumo estruturado](results/screening-2026-10-15-v1/summary.json), [CSV das 84 respostas](results/screening-2026-10-15-v1/interactions.csv) e [hashes](results/screening-2026-10-15-v1/sha256.json).
- [12 prompts](intents-12.json), [regras congeladas](scoring-rules.json), [baseline do estudo](study.json), [preços](oracle-prices.json) e [consolidado financeiro](financial-consolidation.json).

Na raiz do projeto, a validação sem inferência é `python benchmarks/screening/run_screening.py`. Os relatórios são regenerados a partir dos registros privados locais com `python benchmarks/screening/report_screening.py` e `python benchmarks/screening/consolidate_financial.py`. Execução paga exige flags explícitas e orçamento; credenciais, respostas brutas e ledger operacional não são publicados.
