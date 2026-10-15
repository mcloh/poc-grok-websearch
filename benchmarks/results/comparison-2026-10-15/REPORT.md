# Comparativo de 100 intenções — 2026-10-15

Estado: **complete**. 200 de 200 interações concluídas.

Resultados calculados do uso medido a preço de lista Oracle, incluindo tokens de busca e chamadas da ferramenta. Não representam fatura OCI conciliada.

| Modelo | Interações | Busca confirmada | Entrada¹ | Cache² | Saída³ | Buscas tarifadas | Custo USD | Média USD | Mediana USD | P95 USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `xai.grok-4.20-non-reasoning` | 100 | 100 | 4815453 | 2197632 | 92770 | 647 | 7.178728 | 0.071787 | 0.069751 | 0.094497 |
| `xai.grok-4.3` | 100 | 100 | 2032728 | 307840 | 114653 | 312 | 4.064310 | 0.040643 | 0.038978 | 0.056172 |

¹ Entrada total inclui cache. ² Cache é subconjunto da entrada. ³ Saída inclui raciocínio; este não é somado novamente.

## Custos por categoria

| Categoria | Modelo | Interações | Custo USD | Média USD | Buscas tarifadas |
|---|---|---:|---:|---:|---:|
| culinaria | `xai.grok-4.20-non-reasoning` | 25 | 1.676109 | 0.067044 | 160 |
| culinaria | `xai.grok-4.3` | 25 | 1.053508 | 0.042140 | 82 |
| esportes | `xai.grok-4.20-non-reasoning` | 25 | 1.881921 | 0.075277 | 158 |
| esportes | `xai.grok-4.3` | 25 | 0.976945 | 0.039078 | 71 |
| clima | `xai.grok-4.20-non-reasoning` | 25 | 1.818597 | 0.072744 | 164 |
| clima | `xai.grok-4.3` | 25 | 0.966295 | 0.038652 | 77 |
| entretenimento | `xai.grok-4.20-non-reasoning` | 25 | 1.802101 | 0.072084 | 165 |
| entretenimento | `xai.grok-4.3` | 25 | 1.067563 | 0.042703 | 82 |

## Composição do custo

| Modelo | Entrada sem cache USD | Cache USD | Saída USD | Busca USD | Raciocínio (tokens) | Mediana de tempo (s) |
|---|---:|---:|---:|---:|---:|---:|
| `xai.grok-4.20-non-reasoning` | 3.272276 | 0.439526 | 0.231925 | 3.235000 | 0 | 13.5515 |
| `xai.grok-4.3` | 2.156110 | 0.061568 | 0.286632 | 1.560000 | 69002 | 10.594999999999999 |

## Auditoria e limites

- 100 pares completos com custo conhecido; os hashes do payload compartilhado coincidiram em todos esses pares.
- Comparações pareadas de menor custo: {"xai.grok-4.3": 95, "xai.grok-4.20-non-reasoning": 5}.
- Custos desconhecidos: 0; se houver, ficam fora das médias de custo e não são tratados como zero.
- Uma execução por intenção e modelo, com cache e condições reais do serviço; não há controle de todo o estado interno de cache ou dos resultados voláteis da web.
- A mesma pergunta pode provocar números diferentes de buscas e tamanhos de contexto. Esse comportamento faz parte do custo observado.
- Busca confirmada exige ação search completed, fontes e citações estruturadas. Isso não substitui avaliação factual da resposta.
- Preços e metodologia: [protocolo](../../PROTOCOLO.md) e [SKUs Oracle](../../oracle-prices.json).
- [CSV por interação](interactions.csv), [métricas e composição de custo](measured-usage.json), [resumo estruturado](summary.json).
