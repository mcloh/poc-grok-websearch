# Benchmarks Grok via OCI — consumo, ferramentas e custo

Consolidação dos testes realizados em **14 e 15/10/2026**, com custos valorados pela lista Oracle consultada em **15/10/2026**. Todos os valores financeiros estão em **USD**, para processamento padrão e contexto curto.

## Sumário executivo

**Decisão recomendada: manter Grok 4.3 como modelo padrão de custo para o chatbot cotidiano com websearch desta POC.** No conjunto avaliado, cada interação custou em média **US$ 0,040643**, contra **US$ 0,071787** no Grok 4.20 non-reasoning: economia de **43,38%**, com busca confirmada nos dois modelos em todas as consultas.

A comparação usou **as mesmas 100 intenções por modelo**, distribuídas entre culinária, esportes, clima e entretenimento. A tabela abaixo apresenta o custo unitário observado, incluindo os tokens consumidos durante o uso das ferramentas e a cobrança do websearch.

| Indicador por interação | Grok 4.20 non-reasoning | Grok 4.3 |
|---|---:|---:|
| Tokens médios: entrada + saída | 49.082,23 | 21.473,81 |
| Chamadas médias de websearch | 6,47 | 3,12 |
| Custo médio dos tokens — USD | 0,039437 | 0,025043 |
| Custo médio do websearch — USD | 0,032350 | 0,015600 |
| **Custo médio total — USD** | 0,071787 | 0,040643 |

O resultado é explicado pelo comportamento de execução: embora as tarifas por token dos dois candidatos sejam iguais, o Grok 4.3 fez menos buscas e processou menos contexto. Ele custou menos em **95 dos 100 pares** e apresentou mediana de resposta de **10,60 s**, ante **13,55 s** do 4.20 non-reasoning.

**Investimento no experimento:** US$ 11,243038 nas 200 interações do lote principal. O histórico completo, incluindo a POC e a triagem de todos os identificadores, soma US$ 11,505274 em 210 chamadas. Somente o lote pareado sustenta a comparação econômica entre os dois finalistas. A qualidade factual das respostas ainda não foi pontuada.

## Escopo e evidências

| Etapa | Data | Chamadas | Objetivo |
|---|---|---:|---|
| Validação da POC | 14/10/2026 | 3 | Confirmar rotas Responses, REST público e busca com Grok 4.3 |
| Matriz de compatibilidade | 14/10/2026 | 7 | Uma consulta de notícia por identificador Grok |
| Benchmark pareado | 15/10/2026 | 200 | As mesmas 100 intenções em Grok 4.20 non-reasoning e Grok 4.3 |
| **Total com uso preservado** | **14–15/10/2026** | **210** | **Inventário financeiro, não uma única amostra comparável** |

Os sete identificadores incluem os aliases `xai.grok-4.20-reasoning` e `xai.grok-4.20-non-reasoning`, que, na documentação consultada, apontam para as versões `0309` correspondentes. Portanto, sete identificadores testados não representam sete configurações independentes de modelo. Voice Agent e Multi-Agent não integram este estudo.

As três etapas são contabilizadas sem sobreposição. Os erros de diagnóstico sem contadores de uso não entram no total: ausência de `usage` não é tratada como prova de custo zero. O consolidado não substitui a fatura OCI.

## Resultado financeiro consolidado

### Preços de referência

Valores por **1 milhão de tokens**, exceto websearch:

| Família comercial | Entrada sem cache USD | Entrada em cache USD | Saída USD |
|---|---:|---:|---:|
| Grok 4.20 — rubrica comercial Grok 4.2 | 1,25 | 0,20 | 2,50 |
| Grok 4.3 | 1,25 | 0,20 | 2,50 |
| Grok 4.6 | 2,00 | 0,50 | 6,00 |
| Grok 4.7 | 2,00 | 0,50 | 6,00 |

**Websearch nativo xAI via OCI: US$ 5,00 por 1.000 chamadas**, SKU `B112610`. A contabilização usa o número de chamadas tarifadas informado pelo provedor, não o número de perguntas nem uma contagem manual de eventos.

Fontes: [lista de preços Oracle](https://www.oracle.com/cloud/price-list/), [preços congelados do benchmark](oracle-prices.json) e [consolidado com SKUs complementares de 4.6/4.7](financial-consolidation.json). O consolidado registra preços, datas, hashes e contadores históricos suficientes para refazer a soma. O arquivo original de preços do lote foi preservado para manter o hash do manifesto.

### Custos por etapa

| Etapa | Entrada sem cache USD | Cache USD | Saída USD | Websearch USD | Total USD |
|---|---:|---:|---:|---:|---:|
| Validação da POC | 0,023511 | 0,002534 | 0,008370 | 0,045000 | 0,079416 |
| Matriz de compatibilidade | 0,091164 | 0,003290 | 0,023366 | 0,065000 | 0,182820 |
| Benchmark pareado | 5,428386 | 0,501094 | 0,518558 | 4,795000 | 11,243038 |
| **Total** | **5,543062** | **0,506918** | **0,550294** | **4,905000** | **11,505274** |

### Todos os identificadores testados

A tabela abaixo consolida financeiramente as três etapas. Os tamanhos de amostra são diferentes; a média histórica é descritiva e **não deve ser usada como ranking entre os sete identificadores**.

| Identificador OCI | Chamadas | Custo dos tokens¹ USD | Websearch USD | Total USD | Média histórica USD/interação |
|---|---:|---:|---:|---:|---:|
| `xai.grok-4.20-0309-non-reasoning` | 1 | 0,011960 | 0,010000 | 0,021960 | 0,021960 |
| `xai.grok-4.20-0309-reasoning` | 1 | 0,013099 | 0,005000 | 0,018099 | 0,018099 |
| `xai.grok-4.20-non-reasoning` | 101 | 3,956892 | 3,245000 | 7,201892 | 0,071306 |
| `xai.grok-4.20-reasoning` | 1 | 0,012605 | 0,010000 | 0,022605 | 0,022605 |
| `xai.grok-4.3` | 104 | 2,549742 | 1,615000 | 4,164742 | 0,040046 |
| `xai.grok-4.6` | 1 | 0,020772 | 0,005000 | 0,025772 | 0,025772 |
| `xai.grok-4.7` | 1 | 0,035204 | 0,015000 | 0,050204 | 0,050204 |

¹ Inclui entrada sem cache, cache e saída; tokens de raciocínio já estão na saída. Valores são arredondados somente na apresentação; o [JSON consolidado](financial-consolidation.json) preserva a precisão de cálculo.

### Comparação controlada — 100 intenções por modelo

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

## Consumo e custo médios por interação — lote de 100 intenções

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

### Por que Grok 4.3 e Grok 4.20 non-reasoning receberam as 100 intenções

A escolha foi feita **antes da execução do lote completo**, para responder a uma pergunta de negócio: **qual dos candidatos de menor tarifa consegue atender consultas cotidianas com busca web pelo menor custo total por interação?** Os dois já tinham demonstrado busca nativa funcionando pela OCI e estavam na mesma faixa de preço: US$ 1,25 por milhão de tokens de entrada, US$ 0,20 de cache e US$ 2,50 de saída.

| Candidato | Motivo para entrar no lote completo | Hipótese avaliada |
|---|---|---|
| **Grok 4.3** | Era o padrão funcional da POC, já validado no REST público, e tinha a tarifa base mais baixa entre as famílias testadas, empatada com 4.20. | Medir o custo de manter o padrão da aplicação nas 100 consultas cotidianas, incluindo busca e contexto. |
| **Grok 4.20 non-reasoning** | Representava a alternativa focada em respostas diretas, sem tokens de raciocínio reportados na triagem. Na amostra inicial respondeu em 3,22–3,62 s, ante 9,24 s do 4.3, com a mesma tarifa unitária. | Testar se a rapidez e a ausência de raciocínio reportado se converteriam em menor consumo e menor custo da interação completa. |

A triagem inicial tinha uma consulta por identificador. Esses números justificaram uma **hipótese de seleção**, não uma conclusão sobre desempenho ou qualidade. No lote ampliado, a vantagem inicial de tempo do 4.20 non-reasoning não se repetiu na mediana, e ele fez mais buscas; é justamente esse tipo de diferença que o experimento buscava medir.

Os demais identificadores permaneceram na triagem por estes critérios de escopo:

- **Grok 4.6 e 4.7:** tinham tarifas superiores — US$ 2,00 de entrada, US$ 0,50 de cache e US$ 6,00 de saída por milhão de tokens. Para o primeiro comparativo de consultas cotidianas, priorizaram-se os candidatos da faixa de menor custo. Não foi testado se uma eventual melhora de qualidade desses modelos compensaria a diferença de tarifa.
- **Grok 4.20 reasoning:** o recorte inicial priorizou recuperação de informação atual e resposta direta, em vez de raciocínio complexo em múltiplas etapas. A variante permaneceu como compatibilidade confirmada, sem participar da disputa financeira de 100 intenções. Isso não demonstra inadequação ou inferioridade dessa variante.
- **Identificadores com e sem `0309`:** os aliases apontavam para as mesmas versões na documentação consultada. Repetir as 100 intenções nos dois nomes não acrescentaria uma configuração independente ao estudo; foi utilizado o alias `xai.grok-4.20-non-reasoning`.

Portanto, a conclusão de menor custo é **entre os dois candidatos selecionados**, não um ranking geral dos sete identificadores nem uma afirmação de qualidade equivalente.

### Desenho e execução

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

`cached_tokens` é subconjunto da entrada, e `reasoning_tokens` é subconjunto da saída: nenhum deles é somado novamente. O contexto recuperado pelas ferramentas já aparece nos tokens informados pelo serviço. O contador de chamadas tarifadas é `usage.server_side_tool_usage_details.web_search_calls`; aberturas de página e eventos falhos não são tarifados por uma contagem inferida nossa. `cost_in_usd_ticks` é preservado nas evidências históricas, mas não é a fonte da conversão financeira deste relatório.

O custo corresponde ao **uso medido valorado a preço de lista**, sem impostos, descontos contratuais, VM, rede ou armazenamento. As chamadas de 14/10 foram reprecificadas pela referência de 15/10 para produzir um consolidado homogêneo. Não há conciliação com faturamento ou análise de todas as possíveis despesas da conta.

## Estatísticas consolidadas de tokens e tool calls

### Inventário histórico por identificador — 210 interações

| Identificador OCI | Entrada² | Cache² | Saída³ | Raciocínio³ | Total de tokens | Chamadas websearch |
|---|---:|---:|---:|---:|---:|---:|
| `xai.grok-4.20-0309-non-reasoning` | 10.036 | 1.024 | 196 | 0 | 10.232 | 2 |
| `xai.grok-4.20-0309-reasoning` | 7.712 | 256 | 1.491 | 1.375 | 9.203 | 1 |
| `xai.grok-4.20-non-reasoning` | 4.826.397 | 2.198.656 | 92.994 | 0 | 4.919.391 | 649 |
| `xai.grok-4.20-reasoning` | 7.882 | 1.024 | 1.531 | 1.329 | 9.413 | 2 |
| `xai.grok-4.3` | 2.072.301 | 321.792 | 118.899 | 72.106 | 2.191.200 | 323 |
| `xai.grok-4.6` | 8.712 | 1.280 | 878 | 732 | 9.590 | 1 |
| `xai.grok-4.7` | 16.570 | 3.456 | 1.208 | 988 | 17.778 | 3 |
| **Total** | **6.949.610** | **2.527.488** | **217.197** | **76.530** | **7.166.807** | **981** |

² A coluna entrada já inclui cache. ³ A coluna saída já inclui raciocínio. **Total de tokens = entrada + saída**. Os sete testes pontuais e as três validações da POC não são uma amostra equivalente ao lote pareado.

### Médias unitárias de todos os identificadores — histórico

Este quadro atende à visão unitária do inventário completo. Ele mistura etapas com perguntas e tamanhos de amostra distintos: **não usar seus valores como comparação controlada ou ranking**. Para os modelos com uma única chamada, a média é apenas o valor daquela consulta. As médias dos finalistas nesta tabela incluem as validações anteriores; por isso diferem das médias do lote principal de 100 intenções.

| Identificador OCI | Interações na amostra | Tokens médios/interação | Buscas médias/interação | USD médios/interação |
|---|---:|---:|---:|---:|
| `xai.grok-4.20-0309-non-reasoning` | 1 | 10.232,00 | 2,00 | 0,02195980 |
| `xai.grok-4.20-0309-reasoning` | 1 | 9.203,00 | 1,00 | 0,01809870 |
| `xai.grok-4.20-non-reasoning` | 101 | 48.706,84 | 6,43 | 0,07130587 |
| `xai.grok-4.20-reasoning` | 1 | 9.413,00 | 2,00 | 0,02260480 |
| `xai.grok-4.3` | 104 | 21.069,23 | 3,11 | 0,04004560 |
| `xai.grok-4.6` | 1 | 9.590,00 | 1,00 | 0,02577200 |
| `xai.grok-4.7` | 1 | 17.778,00 | 3,00 | 0,05020400 |

Tokens totais de entrada + saída, já incluindo cache e raciocínio nos respectivos contadores.

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

**Recomendação:** manter Grok 4.3 como padrão de custo para o conjunto de consultas cotidianas com websearch avaliado nesta POC. O ganho observado foi consistente no total, nas quatro categorias e em 95% dos pares; a tarifa unitária igual reforça a importância de medir a execução completa, incluindo ferramentas e contexto.

Grok 4.6, Grok 4.7 e as variantes reasoning da família 4.20 tiveram busca confirmada na triagem, mas somente uma consulta por identificador. Não há evidência neste repositório para classificá-los acima ou abaixo dos finalistas em qualidade, custo médio de 100 intenções ou custo-benefício geral. Os aliases `0309` e sem data também não devem ser tratados como alternativas independentes.

Este estudo mede custo, uso de ferramentas e latência observada. Não pontua correção factual, completude, precisão de datas, cobertura das fontes ou satisfação do usuário. Mais buscas não provam maior qualidade; menos buscas não provam pior qualidade. Uma execução por intenção, cache real do serviço e conteúdo volátil da web limitam a extrapolação. Os resultados valem para os identificadores, região, endpoint, preços e datas documentados.

Para uma decisão mais ampla de produto, o próximo passo é avaliar as respostas dos mesmos 100 pares com uma rubrica factual e de utilidade, antes de transformar a economia em uma conclusão de custo-benefício com qualidade equivalente.

## Arquivos e reprodução

| Arquivo | Conteúdo |
|---|---|
| [INTENCOES.md](INTENCOES.md) / [intents.json](intents.json) | Lista de 100 intenções e prompts exatos com hashes |
| [PROTOCOLO.md](PROTOCOLO.md) | Regras de execução, custos, orçamento e retomada |
| [oracle-prices.json](oracle-prices.json) | Preços e SKUs congelados do lote pareado |
| [financial-consolidation.json](financial-consolidation.json) | Consolidação das 210 chamadas e SKUs dos sete identificadores |
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

Para uma nova execução paga, consultar o [protocolo](PROTOCOLO.md), definir orçamento autorizado e usar um novo `--run-id` quando apropriado. Credenciais, respostas brutas e registros operacionais não são versionados. Este README e o consolidado financeiro foram produzidos a partir das evidências existentes, sem novas chamadas de inferência.
