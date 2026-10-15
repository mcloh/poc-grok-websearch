# Benchmarks Grok via OCI — consumo, ferramentas e custo

Consolidação dos testes realizados em **14 e 15/10/2026**, com custos valorados pela lista Oracle consultada em **15/10/2026**. Todos os valores financeiros estão em **USD**, para processamento padrão e contexto curto.

## Sumário executivo

O teste principal enviou **as mesmas 100 intenções a dois modelos**, totalizando **200 interações** sobre culinária, esportes, clima e entretenimento. Todas tiveram HTTP 200 e busca web confirmada. O custo variável calculado foi de **US$ 11,243038**, incluindo **US$ 4,795 de websearch**.

O **Grok 4.3 custou 43,38% menos** que o Grok 4.20 non-reasoning e foi mais barato em **95 dos 100 pares**. Também apresentou menor mediana de tempo neste lote: **10,60 s**, contra **13,55 s**. Os dois modelos têm a mesma tarifa unitária na faixa usada; o comportamento de busca e o volume de contexto explicam a diferença financeira observada.

Incluindo as validações anteriores da POC e a triagem dos sete identificadores Grok testados, o inventário financeiro reúne **210 chamadas com uso preservado**, **7.166.807 tokens** e **981 chamadas de websearch**, por **US$ 11,505274**. Esse total histórico é distinto dos US$ 11,243038 do benchmark de 200 interações.

A conclusão sustentada pelos dados é de **menor custo operacional do Grok 4.3 entre os dois finalistas neste conjunto com websearch**. Não foi realizada pontuação de correção factual ou qualidade editorial, nem o lote de 100 intenções foi executado nos demais modelos.

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

| Identificador OCI | Chamadas | Custo dos tokens¹ USD | Websearch USD | Total USD | Média histórica USD |
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

| Modelo | Total USD | Média USD | Mediana USD | P95 USD | Websearch USD | Mediana de tempo (s) |
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

## Metodologia

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
