# Benchmarks Grok via OCI — consumo, ferramentas e custo

Consolidação dos testes realizados em **14 e 15/10/2026**, com custos valorados pela lista Oracle consultada em **15/10/2026**. Todos os valores financeiros estão em **USD**, para processamento padrão, com faixas de contexto curto e longo quando aplicáveis.

## Sumário executivo

**Benchmark em dois turnos: Grok 4.3 e Grok 4.20 non-reasoning são os finalistas; Grok 4.3 vence a comparação de custo do conjunto completo.** Como em uma eleição, o 1º turno compara todos os candidatos sob a mesma regra; o 2º turno concentra a análise nos dois classificados.

| Turno | Disputa | Critério | Resultado |
|---|---|---|---|
| **1º — seleção dos finalistas** | 12 perguntas iguais × sete IDs; três por tema | Nota ponderada: 50% custo, 30% busca operacional confiável, 20% latência; corte 70/100 | Grok 4.3: **97,15**; Grok 4.20 non-reasoning: **73,39** |
| **2º — comparação completa** | 100 perguntas iguais × dois finalistas; 25 por tema | Custo total por interação, incluindo tokens e websearch | Grok 4.3: **US$ 0,040643/interação**, economia de **43,38%** |

A [apuração do 1º turno](screening/README.md) explica a classificação da dupla; o 2º turno detalha sua comparação na massa completa. A vitória é econômica, sob a configuração e os casos avaliados; não é uma nota de qualidade factual.

A confirmação da segunda vaga depende do cache observado: no cenário contábil secundário sem desconto de cache, somente Grok 4.3 passa o corte. O teste não pontua qualidade factual.

No 2º turno, com 100 intenções por finalista, Grok 4.3 custou **US$ 0,040643 por interação**, contra **US$ 0,071787** no 4.20 non-reasoning: economia de **43,38%** entre esses dois candidatos. Esse resultado não estabelece superioridade perante todos os modelos.

A comparação usou **as mesmas 100 intenções por modelo**, distribuídas entre culinária, esportes, clima e entretenimento. A tabela abaixo apresenta o custo unitário observado, incluindo os tokens consumidos durante o uso das ferramentas e a cobrança do websearch.

| Indicador por interação | Grok 4.20 non-reasoning | Grok 4.3 |
|---|---:|---:|
| Tokens médios: entrada + saída | 49.082,23 | 21.473,81 |
| Chamadas médias de websearch | 6,47 | 3,12 |
| Custo médio dos tokens — USD | 0,039437 | 0,025043 |
| Custo médio do websearch — USD | 0,032350 | 0,015600 |
| **Custo médio total — USD** | 0,071787 | 0,040643 |

O resultado é explicado pelo comportamento de execução: embora as tarifas por token dos dois candidatos sejam iguais, o Grok 4.3 fez menos buscas e processou menos contexto. Ele custou menos em **95 dos 100 pares** e apresentou mediana de resposta de **10,60 s**, ante **13,55 s** do 4.20 non-reasoning.

**Investimento conhecido:** US$ 20,963443 em **294 respostas com uso**, incluindo US$ 9,458169 nas 84 respostas do 1º turno. Essa etapa exigiu 91 tentativas HTTP, com sete rejeições de infraestrutura sem custo determinável por ausência de `usage`. A qualidade factual ainda não foi pontuada.

## Escopo e evidências

| Etapa | Data | Chamadas | Objetivo |
|---|---|---:|---|
| Validação da POC | 14/10/2026 | 3 | Confirmar rotas Responses, REST público e busca com Grok 4.3 |
| Matriz de compatibilidade | 14/10/2026 | 7 | Uma consulta de notícia por identificador Grok |
| 1º turno — seleção | 15/10/2026 | 84 respostas / 91 tentativas HTTP | Mesmas 12 perguntas nos sete IDs, três por tema; corte ponderado |
| 2º turno — comparação completa | 15/10/2026 | 200 | As mesmas 100 intenções em Grok 4.20 non-reasoning e Grok 4.3 |
| **Total com uso preservado** | **14–15/10/2026** | **294** | **Inventário financeiro, não uma única amostra comparável** |

Os sete identificadores incluem os aliases `xai.grok-4.20-reasoning` e `xai.grok-4.20-non-reasoning`, que, na documentação consultada, apontam para as versões `0309` correspondentes. Portanto, sete identificadores testados não representam sete configurações independentes de modelo. Voice Agent e Multi-Agent não integram este estudo.

As quatro etapas são contabilizadas sem sobreposição. Os erros de diagnóstico sem contadores de uso não entram no total: ausência de `usage` não é tratada como prova de custo zero. O consolidado não substitui a fatura OCI.

## Resultado financeiro consolidado

### Preços de referência

Valores por **1 milhão de tokens**, exceto websearch:

| Família comercial | Entrada sem cache USD | Entrada em cache USD | Saída USD |
|---|---:|---:|---:|
| Grok 4.20 — rubrica comercial Grok 4.2 | 1,25 | 0,20 | 2,50 |
| Grok 4.3 | 1,25 | 0,20 | 2,50 |
| Grok 4.6 | 2,00 | 0,50 | 6,00 |
| Grok 4.7 | 2,00 | 0,50 | 6,00 |

As tarifas da tabela são de contexto curto. A faixa longa dobra as tarifas da família 4.20/4.3 para 2,50/0,40/5,00 e da família 4.6/4.7 para 4,00/1,00/12,00 (entrada/cache/saída, por milhão). A aplicação observada está documentada no [adendo](screening/ADENDO-CONTABILIDADE.md).

**Websearch nativo xAI via OCI: US$ 5,00 por 1.000 chamadas**, SKU `B112610`. A contabilização usa o número de chamadas tarifadas informado pelo provedor, não o número de perguntas nem uma contagem manual de eventos.

Fontes: [lista de preços Oracle](https://www.oracle.com/cloud/price-list/), [preços congelados do benchmark](oracle-prices.json) e [preços complementares e faixas longas](screening/oracle-prices.json). O consolidado registra preços, datas, hashes e contadores históricos suficientes para refazer a soma. O arquivo original de preços do lote foi preservado para manter o hash do manifesto.

### Custos por etapa

| Etapa | Entrada sem cache USD | Cache USD | Saída USD | Websearch USD | Total USD |
|---|---|---|---|---|---|
| Validação da POC | 0,023511 | 0,002534 | 0,008370 | 0,045000 | 0,079416 |
| Matriz de compatibilidade | 0,091164 | 0,003290 | 0,023366 | 0,065000 | 0,182820 |
| 1º turno — seleção | 4,575965 | 1,239002 | 0,953202 | 2,690000 | 9,458169 |
| 2º turno — comparação completa | 5,428386 | 0,501094 | 0,518558 | 4,795000 | 11,243038 |
| **Total** | 10,119027 | 1,745920 | 1,503496 | 7,595000 | 20,963443 |

### Todos os identificadores testados

Inventário das quatro etapas, com amostras diferentes: **as médias históricas não são ranking**. A comparação uniforme dos sete IDs está na [auditoria de seleção](screening/README.md).

| Identificador OCI | Respostas | Tokens USD | Websearch USD | Total USD | Média histórica USD/interação |
|---|---|---|---|---|---|
| `xai.grok-4.20-0309-non-reasoning` | 13 | 0,481469 | 0,415000 | 0,896469 | 0,068959 |
| `xai.grok-4.20-0309-reasoning` | 13 | 0,506283 | 0,305000 | 0,811283 | 0,062406 |
| `xai.grok-4.20-non-reasoning` | 113 | 4,468418 | 3,640000 | 8,108418 | 0,071756 |
| `xai.grok-4.20-reasoning` | 13 | 0,462307 | 0,290000 | 0,752307 | 0,057870 |
| `xai.grok-4.3` | 116 | 2,863576 | 1,810000 | 4,673576 | 0,040289 |
| `xai.grok-4.6` | 13 | 1,547842 | 0,485000 | 2,032842 | 0,156372 |
| `xai.grok-4.7` | 13 | 3,038548 | 0,650000 | 3,688548 | 0,283734 |

O [consolidado atual](screening/financial-consolidation.json) preserva valores completos; o [baseline de 210 respostas](financial-consolidation.json) continua intacto. Sete rejeições da auditoria sem `usage` estão fora dos custos conhecidos, sem serem tratadas como custo zero.

### 1º turno — apuração das cinco configurações

Os sete IDs representam cinco configurações, pois os aliases com e sem `0309` são agrupados. As notas dos aliases são promediadas; cada ID precisa ter 12 custos conhecidos e ao menos 11 buscas confiáveis. As duas maiores notas entre as configurações aprovadas ocupam as vagas.

| Configuração | Nota /100 | Corte >=70 | Classificação |
|---|---:|---|---|
| Grok 4.3 | 97,15 | Aprovado | **Finalista** |
| Grok 4.20 non-reasoning | 73,39 | Aprovado | **Finalista** |
| Grok 4.20 reasoning | 70,08 | Aprovado | Terceiro colocado |
| Grok 4.6 | 45,51 | Abaixo do corte | Fora das duas vagas |
| Grok 4.7 | 43,34 | Abaixo do corte | Fora das duas vagas |

Grok 4.20 reasoning passou o corte, mas teve nota menor que os dois primeiros. Seu custo médio foi inferior ao do non-reasoning; sua maior latência reduziu a pontuação. O [relatório do 1º turno](screening/README.md) apresenta os sete IDs, consumo e custo unitário, além da sensibilidade ao cache e aos casos da amostra.

### 2º turno — comparação controlada com 100 intenções por finalista

| Modelo | Total USD | Média USD/interação | Mediana USD/interação | P95 USD/interação | Websearch USD | Mediana de tempo (s) |
|---|---:|---:|---:|---:|---:|---:|
| `xai.grok-4.20-non-reasoning` | 7,178728 | 0,071787 | 0,069751 | 0,094497 | 3,235000 | 13,55 |
| `xai.grok-4.3` | 4,064310 | 0,040643 | 0,038978 | 0,056172 | 1,560000 | 10,60 |

A economia do Grok 4.3 neste lote foi de **US$ 3,114417 (43,38%)**. O P95 é o percentil empírico pelo método de posto mais próximo; não é uma garantia de custo máximo de futuras interações.

| Categoria — 25 intenções por modelo | Grok 4.20 non-reasoning USD | Grok 4.3 USD | Economia com Grok 4.3 |
|---|---:|---:|---:|
| Culinária | 1,676109 | 1,053508 | 37,15% |
| Esportes | 1,881921 | 0,976945 | 48,09% |
| Clima | 1,818597 | 0,966295 | 46,87% |
| Entretenimento | 1,802101 | 1,067563 | 40,76% |

## 2º turno — consumo e custo médios por interação

As médias desta seção usam **100 interações por modelo**, sem misturar os testes pontuais anteriores. O consumo inclui todas as etapas internas reportadas no `usage` da resposta OCI; não corresponde apenas ao tamanho do prompt digitado ou ao texto final apresentado ao usuário.

### Tokens e ferramentas por interação

| Métrica média por interação | Grok 4.20 non-reasoning | Grok 4.3 |
|---|---:|---:|
| Entrada total, cache incluído | 48.154,53 | 20.327,28 |
| Entrada atendida por cache¹ | 21.976,32 | 3.078,40 |
| Entrada sem cache | 26.178,21 | 17.248,88 |
| Saída total, raciocínio incluído | 927,70 | 1.146,53 |
| Raciocínio reportado² | 0,00 | 690,02 |
| **Total: entrada + saída** | **49.082,23** | **21.473,81** |
| Chamadas de websearch | 6,47 | 3,12 |

¹ Cache é parte da entrada, não consumo adicional. ² Raciocínio é parte da saída, não uma parcela somada novamente. A diferença de consumo vem principalmente do volume de contexto recuperado e do número de buscas realizadas.

### Composição do custo médio por interação

| Componente — USD/interação | Grok 4.20 non-reasoning | Grok 4.3 |
|---|---:|---:|
| Tokens de entrada sem cache | 0,03272276 | 0,02156110 |
| Tokens de entrada em cache | 0,00439526 | 0,00061568 |
| Tokens de saída, incluindo raciocínio | 0,00231925 | 0,00286632 |
| Chamadas de websearch | 0,03235000 | 0,01560000 |
| **Total por interação** | 0,07178728 | 0,04064310 |

**Leitura financeira:** menor tarifa por token não foi o fator de diferenciação, pois os dois candidatos tinham os mesmos preços. O Grok 4.3 consumiu mais tokens de saída, mas a redução de entrada e de buscas mais que compensou esse componente. Os valores são custos calculados do uso medido a preço de lista, e não valores conciliados de uma fatura.

## Metodologia

### 1º turno — regras de seleção

Cada um dos sete IDs recebe as mesmas 12 perguntas, três por tema. Cada tema pesa 25%. Por pergunta, a eficiência de custo é o menor custo confiável dividido pelo custo do ID; a eficiência de tempo usa a mesma razão com a latência. A nota combina **50% custo, 30% busca confiável e 20% latência**. Respostas não confiáveis recebem zero nos três componentes.

A elegibilidade exige 12 custos conhecidos e ao menos 11 buscas confiáveis por ID; o corte é 70/100 por configuração. Busca confiável exige HTTP 200, busca concluída com fontes e citações, texto final não vazio e ausência de truncamento. Aliases são agrupados antes da seleção das duas vagas. Pesos, corte, amostra e preços foram congelados antes das inferências desta etapa, no [protocolo do 1º turno](screening/PROTOCOLO.md).

### Passagem ao 2º turno — por que esta dupla

Grok 4.3 e Grok 4.20 non-reasoning são as duas configurações com maior nota entre as aprovadas no 1º turno. Ambos oferecem busca nativa funcional via OCI e têm a mesma tarifa base. O 2º turno compara o custo efetivo das mesmas 100 consultas, permitindo verificar quanto o comportamento de busca, o contexto recuperado e a saída gerada alteram a conta final.

A nota do 1º turno serve à classificação das vagas; o resultado financeiro do 2º turno vem de uma amostra maior. As notas de 12 casos não são extrapoladas para os modelos que não receberam as 100 intenções.

### Nota sobre a ordem de apresentação

Os turnos seguem a ordem lógica de leitura. Na execução real, o lote de 100 intenções veio primeiro, com escolha heurística da dupla; a seleção calculada foi realizada depois, como auditoria retrospectiva, e confirmou os mesmos finalistas. Portanto, o 1º turno fundamenta a classificação apresentada, mas não causou historicamente a escolha do lote completo. Os protocolos, manifestos e registros preservam essa cronologia.

### 2º turno — desenho e execução

1. **Triagem de compatibilidade:** uma consulta sobre notícia atual por identificador, executando a rota `/api/chat` em processos locais isolados via FastAPI TestClient com inferência OCI real. HTTP 200 isolado não foi suficiente para confirmar busca. Os parâmetros e o runtime dessa etapa estão na [matriz original](../evidence/grok-websearch-models.json).
2. **Conjunto pareado:** seleção prévia de 100 intenções, com 25 de cada tema. As perguntas exigem informação atual, como previsão do tempo, agenda, preços, resultados e disponibilidade. Os [prompts e hashes](intents.json) e a [lista legível](INTENCOES.md) foram congelados com referência a 15/10/2026.
3. **Envio uniforme:** o coletor do benchmark chama diretamente a Responses API OCI em `us-chicago-1`, endpoint `/v1/responses`, com payload compartilhado idêntico entre os candidatos, diferindo somente `model`. Não chama a API direta da xAI. Cada interação é independente, sem histórico de conversa.
4. **Configuração:** `tools: [{"type":"web_search"}]`, `store:false`, máximo de 2.400 tokens de saída e instrução de resposta em até 200 palavras. Temperatura e esforço de raciocínio ficam nos padrões do serviço. Há duas inferências simultâneas, pareadas por intenção e alternadas entre temas.
5. **Piloto e retomada:** as quatro primeiras intenções, uma por tema, geraram oito chamadas e integram as 200 finais. Não houve retries automáticos nem repetição do piloto. O controle de orçamento pausou após 170 chamadas; a retomada enviou somente as 30 restantes.
6. **Confirmação de busca:** exigir HTTP 200, evento `web_search_call` com ação `search` e status `completed`, fontes não vazias e citações estruturadas. Todas as 200 interações satisfizeram o critério.
7. **Auditoria:** conferir 200 chamadas únicas, 100 pares, 25 intenções por tema/modelo, hashes iguais em cada par e composição aritmética dos custos. Há zero interações com custo desconhecido no lote concluído.

A cobrança por interação é calculada assim:

```text
entrada sem cache = input_tokens - cached_tokens
custo = (entrada sem cache × tarifa entrada
       + cached_tokens × tarifa cache
       + output_tokens × tarifa saída) / 1.000.000
       + web_search_calls × 5 / 1.000
```

`cached_tokens` é subconjunto da entrada, e `reasoning_tokens` é subconjunto da saída: nenhum deles é somado novamente. O contexto recuperado pelas ferramentas já aparece nos tokens informados pelo serviço. O contador de chamadas tarifadas é `usage.server_side_tool_usage_details.web_search_calls`; aberturas de página e eventos falhos não são tarifados por uma contagem inferida nossa. O custo é calculado por SKUs Oracle. Na auditoria posterior, `cost_in_usd_ticks` também foi usado para resolver a faixa longa por correspondência única ao cálculo dos SKUs, conforme o [adendo contábil](screening/ADENDO-CONTABILIDADE.md).

O custo corresponde ao **uso medido valorado a preço de lista**, sem impostos, descontos contratuais, VM, rede ou armazenamento. As chamadas de 14/10 foram reprecificadas pela referência de 15/10 para produzir um consolidado homogêneo. Não há conciliação com faturamento ou análise de todas as possíveis despesas da conta.

## Estatísticas consolidadas de tokens e tool calls

### Inventário histórico por identificador — 294 respostas

| Identificador OCI | Entrada | Cache¹ | Saída | Raciocínio² | Total de tokens | Websearch |
|---|---|---|---|---|---|---|
| `xai.grok-4.20-0309-non-reasoning` | 586.469 | 269.312 | 12.464 | 0 | 598.933 | 83 |
| `xai.grok-4.20-0309-reasoning` | 493.766 | 188.928 | 34.980 | 25.922 | 528.746 | 61 |
| `xai.grok-4.20-non-reasoning` | 5.425.184 | 2.451.328 | 104.333 | 0 | 5.529.517 | 728 |
| `xai.grok-4.20-reasoning` | 423.457 | 139.392 | 31.739 | 23.469 | 455.196 | 58 |
| `xai.grok-4.3` | 2.323.819 | 354.560 | 132.436 | 80.151 | 2.456.255 | 362 |
| `xai.grok-4.6` | 981.041 | 449.024 | 43.216 | 35.777 | 1.024.257 | 97 |
| `xai.grok-4.7` | 1.812.889 | 1.144.704 | 53.315 | 43.212 | 1.866.204 | 130 |
| **Total** | 12.046.625 | 4.997.248 | 412.483 | 208.531 | 12.459.108 | 1.519 |

¹ Cache é subconjunto da entrada. ² Raciocínio é subconjunto da saída. Total = entrada + saída.

### Médias unitárias históricas — amostras diferentes

Estas médias misturam etapas e não classificam os modelos. Para médias pareadas dos sete IDs, usar a [amostra uniforme de 12 perguntas](screening/README.md).

| ID OCI | Respostas | Tokens/interação | Buscas/interação | USD/interação |
|---|---|---|---|---|
| `xai.grok-4.20-0309-non-reasoning` | 13 | 46.071,77 | 6,38 | 0,06895913 |
| `xai.grok-4.20-0309-reasoning` | 13 | 40.672,77 | 4,69 | 0,06240639 |
| `xai.grok-4.20-non-reasoning` | 113 | 48.933,78 | 6,44 | 0,07175591 |
| `xai.grok-4.20-reasoning` | 13 | 35.015,08 | 4,46 | 0,05786978 |
| `xai.grok-4.3` | 116 | 21.174,61 | 3,12 | 0,04028945 |
| `xai.grok-4.6` | 13 | 78.789,00 | 7,46 | 0,15637246 |
| `xai.grok-4.7` | 13 | 143.554,15 | 10,00 | 0,28373446 |

### Lote pareado isolado — 200 interações

| Métrica | Grok 4.20 non-reasoning | Grok 4.3 | Total do lote |
|---|---:|---:|---:|
| Tokens de entrada, cache incluído | 4.815.453 | 2.032.728 | 6.848.181 |
| Tokens em cache | 2.197.632 | 307.840 | 2.505.472 |
| Tokens de saída, raciocínio incluído | 92.770 | 114.653 | 207.423 |
| Tokens de raciocínio | 0 | 69.002 | 69.002 |
| Chamadas tarifadas de websearch | 647 | 312 | 959 |
| Total de tokens: entrada + saída | 4.908.223 | 2.147.381 | 7.055.604 |
| Buscas tarifadas por interação, média | 6,47 | 3,12 | 4,795 |
| Interações com busca confirmada | 100/100 | 100/100 | 200/200 |

As **959 chamadas de busca** custaram **US$ 4,795**, ou **42,65%** do custo do lote. O Grok 4.3 realizou **51,78% menos buscas**. Embora tenha gerado mais tokens de saída, incluindo 69.002 de raciocínio, sua menor entrada e menor quantidade de buscas compensaram esse componente de custo.

## Limitações e conclusão

**1º turno:** Grok 4.3 e Grok 4.20 non-reasoning ocupam as duas vagas pelo corte operacional. **2º turno:** Grok 4.3 apresenta o menor custo nas 100 perguntas, com economia de 43,38% frente ao outro finalista. Os demais modelos não receberam esse lote completo.

O [pré-teste retrospectivo](screening/README.md) amplia a evidência para todos os sete IDs, com 12 perguntas iguais, mas não sustenta extrapolação para 100 intenções nem ranking de qualidade factual. Aliases são agrupados em cinco configurações para a seleção das vagas.

Este estudo mede custo, uso de ferramentas e latência observada. Não pontua correção factual, completude, precisão de datas, cobertura das fontes ou satisfação do usuário. Mais buscas não provam maior qualidade; menos buscas não provam pior qualidade. Uma execução por intenção, cache real do serviço e conteúdo volátil da web limitam a extrapolação. Os resultados valem para os identificadores, região, endpoint, preços e datas documentados.

Para uma decisão mais ampla de produto, o próximo passo é avaliar as respostas dos mesmos 100 pares com uma rubrica factual e de utilidade, antes de transformar a economia em uma conclusão de custo-benefício com qualidade equivalente.

## Arquivos e reprodução

| Arquivo | Conteúdo |
|---|---|
| [INTENCOES.md](INTENCOES.md) / [intents.json](intents.json) | Lista de 100 intenções e prompts exatos com hashes |
| [PROTOCOLO.md](PROTOCOLO.md) | Regras de execução, custos, orçamento e retomada |
| [oracle-prices.json](oracle-prices.json) | Preços e SKUs congelados do lote pareado |
| [Consolidado atual](screening/financial-consolidation.json) / [baseline](financial-consolidation.json) | 294 respostas com custo conhecido / histórico preservado de 210 |
| [Auditoria da seleção](screening/README.md) | 12 perguntas × sete IDs, corte ponderado e resultados |
| [run_benchmark.py](run_benchmark.py) | Coletor: padrão dry run; execução paga exige flags e orçamento |
| [report.py](report.py) | Regenera relatório do lote a partir dos registros locais, sem inferência |
| [Relatório do lote](results/comparison-2026-10-15/REPORT.md) | Custos e estatísticas por categoria |
| [CSV por interação](results/comparison-2026-10-15/interactions.csv) | 200 linhas com prompts, tokens e composição de custo |
| [Uso medido](results/comparison-2026-10-15/measured-usage.json) | Métricas selecionadas de cada chamada do lote |
| [Resumo](results/comparison-2026-10-15/summary.json) / [hashes](results/comparison-2026-10-15/sha256.json) | Totais, manifesto e integridade dos artefatos |
| [Matriz original dos sete identificadores](../evidence/grok-websearch-models.json) | Resultados dos testes pontuais de compatibilidade |

Executados na raiz do repositório:

```bash
# Validar o dataset sem inferência:
python benchmarks/run_benchmark.py

# Regenerar o relatório se os registros locais da execução estiverem presentes:
python benchmarks/report.py
```

Para uma nova execução paga, consultar o [protocolo](PROTOCOLO.md), definir orçamento autorizado e usar um novo `--run-id` quando apropriado. Credenciais, respostas brutas e registros operacionais não são versionados. O consolidado agrega as evidências das etapas descritas; sua regeneração não faz inferências. A auditoria retrospectiva acrescentou 84 novas respostas, documentadas separadamente.
