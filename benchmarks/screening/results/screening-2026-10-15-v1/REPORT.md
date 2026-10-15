# Pré-teste retrospectivo — 12 consultas por identificador

**A amostra confirma os dois candidatos originais segundo a regra operacional congelada.**

84 novas respostas avaliadas; 91 tentativas HTTP, das quais 7 rejeitadas por infraestrutura; custo conhecido US$ 9.45816885; buscas operacionais confiáveis 84/84.

A seleção original antecedeu este teste. Esta etapa é uma auditoria posterior e não reescreve a cronologia.

## Classificação por identificador

| ID OCI | Nota /100 | Busca confiável | Gate operacional | Corte >=70 | USD/interação | Tokens/interação | Mediana s | Faixa bootstrap das notas |
|---|---:|---:|---|---|---:|---:|---:|---|
| `xai.grok-4.3` | 97.1490 | 12/12 | True | True | 0.0424 | 22087.92 | 11.370 | 95.68–99.31 |
| `xai.grok-4.20-0309-non-reasoning` | 74.0107 | 12/12 | True | True | 0.0729 | 49058.42 | 12.639 | 70.94–77.03 |
| `xai.grok-4.20-non-reasoning` | 72.7615 | 12/12 | True | True | 0.0755 | 50843.83 | 12.383 | 69.97–76.11 |
| `xai.grok-4.20-reasoning` | 72.2381 | 12/12 | True | True | 0.0608 | 37148.58 | 29.154 | 69.53–75.30 |
| `xai.grok-4.20-0309-reasoning` | 67.9261 | 12/12 | True | False | 0.0661 | 43295.25 | 33.049 | 63.87–71.67 |
| `xai.grok-4.6` | 45.5086 | 12/12 | True | False | 0.1673 | 84555.58 | 65.825 | 43.92–47.39 |
| `xai.grok-4.7` | 43.3442 | 12/12 | True | False | 0.3032 | 154035.50 | 50.155 | 40.61–46.41 |

## Corte por configuração, com aliases agrupados

| Configuração | IDs agrupados | Nota /100 | Aprovada | Selecionada | Frequência top 2 no bootstrap |
|---|---:|---:|---|---|---:|
| `grok-4.3` | 1 | 97.1490 | True | True | 100.0% |
| `grok-4.20-non-reasoning` | 2 | 73.3861 | True | True | 99.8% |
| `grok-4.20-reasoning` | 2 | 70.0821 | True | False | 0.0% |
| `grok-4.6` | 1 | 45.5086 | False | False | 0.0% |
| `grok-4.7` | 1 | 43.3442 | False | False | 0.0% |

## Sensibilidade ao desconto de cache

Análise secundária e exploratória, sem alterar a seleção principal. Nos mesmos registros, cobrar toda a entrada pela tarifa sem cache e reaplicar os mesmos pesos. Selecionadas nesse cenário contábil: `grok-4.3`. Não é uma simulação física de serviço sem cache.

A amostra não é holdout: os dois candidatos originais já receberam esses prompts no lote anterior. O cache da API não foi controlado. A sensibilidade apenas verifica a contribuição do desconto financeiro, mantendo tokens e tempos observados.

## Interpretação dos aliases

A nota agrupada é a média dos IDs da configuração. As duas versões de alias não ocupam vagas separadas. O gate operacional exige 12 custos conhecidos e ao menos 11 buscas confiáveis por ID; o corte de 70 aplica-se à nota da configuração.

## Regra e limites

- Pesos: 50% custo total, 30% busca operacional confiável e 20% latência; 25% por tema, com três consultas cada.
- Eficiência de custo e tempo normalizada pela melhor resposta confiável da mesma intenção. Uma resposta não confiável recebe zero nos três componentes.
- Busca confiável requer HTTP 200, custo conhecido, search completed, fontes, citações, texto final não vazio e ausência de sinal de truncamento. Não é avaliação factual.
- Faixa bootstrap: sensibilidade descritiva aos casos em 2000 reamostragens estratificadas e pareadas. Não é intervalo de confiança populacional e não mede repetições independentes da mesma pergunta.
- Gates de custo e confiabilidade ficam fixos na reamostragem; o corte de 70 é reaplicado às notas de cada reamostragem.
- As 84 respostas avaliadas são novas; nenhuma resposta do lote original de 200 foi reutilizada como execução deste pré-teste.
- As rejeições compartilhadas por HTTP 429 foram preservadas e recuperadas uma vez após controle de taxa; não foram computadas como custo zero ou como falha de um modelo. Veja o [adendo operacional](../../ADENDO-TAXA.md).
- O contador financeiro cobre respostas com usage; o custo das rejeições sem usage permanece desconhecido e não integra as médias nem o custo conhecido publicado.
- O limite de 2400 tokens de saída e os defaults do modelo são iguais aos do experimento. Truncamentos são penalizados; isso avalia esta configuração operacional, não a capacidade máxima de cada modelo.
- Custos calculados a preço de lista Oracle incluem tokens e websearch; não são fatura conciliada.
- O caso de contexto longo foi conciliado sem repetir a inferência; a memória de cálculo consta no [adendo de contabilidade](../../ADENDO-CONTABILIDADE.md).
- O parâmetro max_output_tokens=2400 não limitou o uso agregado de saída do loop a 2400 em todas as respostas. Os custos usam o usage total retornado, incluindo etapas internas.

## Evidências

- [Protocolo anterior às novas chamadas](../../PROTOCOLO.md).
- [Dataset de 12 intenções](../../intents-12.json), [regras de corte](../../scoring-rules.json) e [sensibilidade de cache](../../SENSIBILIDADES.md).
- [CSV das 84 interações](interactions.csv), [métricas medidas](measured-usage.json) e [resumo com bootstrap](summary.json).
