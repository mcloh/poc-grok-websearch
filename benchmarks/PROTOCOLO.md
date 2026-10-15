# Comparativo pareado de custo de 100 intenções

## Escopo executado

- [100 intenções](INTENCOES.md): 25 de culinária, esportes, clima e entretenimento.
- Dois finalistas: `xai.grok-4.20-non-reasoning` e `xai.grok-4.3`. São 200 interações independentes.
- [Prompts exatos](intents.json) com a mesma data e hashes. A cada intenção, enviar aos dois modelos o mesmo payload, diferindo apenas `model`. Sem histórico de conversa.
- Consultas escolhidas exigem dados atuais: horários, preços, previsão, boletins, resultados, programação e disponibilidade. Se um modelo não pesquisar, isso será registrado; não se presume busca apenas porque a ferramenta foi habilitada.
- OCI Chicago, `/v1/responses`, `tools: [{"type":"web_search"}]`, `store:false`, saída limitada a 2400 tokens. Mesmos parâmetros de amostragem e raciocínio omitidos para os dois.
- Dois envios simultâneos, pareados por intenção, alternando as categorias. Um piloto de quatro intenções, uma por categoria, representa oito chamadas e integra o lote final sem repetições.
- Sem retries automáticos. Erros de HTTP, cobrança desconhecida ou timeout interrompem novos pares e exigem diagnóstico. Falha de transporte não significa custo zero.

## Custo por interação

Preços congelados em [oracle-prices.json](oracle-prices.json), com SKUs, moeda USD, data, fonte e hash dos dados consultados. Os dois candidatos usam os SKUs comerciais Grok 4.2 e Grok 4.3, respectivamente.

```text
entrada sem cache = input_tokens - cached_tokens
custo entrada = entrada sem cache × preço entrada / 1.000.000
custo cache = cached_tokens × preço cache / 1.000.000
custo saída = output_tokens × preço saída / 1.000.000
custo busca = usage.server_side_tool_usage_details.web_search_calls × US$ 5 / 1.000
custo total = entrada + cache + saída + busca
```

Os tokens de raciocínio são um subconjunto de output_tokens: serão informados, mas não somados novamente. O contexto recuperado pelas ferramentas já entra nos contadores de uso do provedor. Os eventos de busca são preservados para auditoria, mas o número de chamadas tarifadas vem de `usage`, evitando contar abertura de página ou evento falho como cobrança adicional por inferência nossa.

O resultado é **custo calculado do uso medido a preço de lista**, não uma fatura conciliada da OCI. Descontos, impostos, VM, rede e armazenamento ficam fora deste custo variável por interação. Não se atribui escala financeira a `cost_in_usd_ticks`; o valor bruto é preservado para conferência.

Contadores ausentes, uso de outras ferramentas ou contextos agregados acima de 200 mil tokens serão classificados como custo desconhecido, em vez de precificados com suposições. Todos os dados brutos ficam locais, fora do Git.

## Orçamento e controle

A estimativa inicial foi US$ 4,42 para 200 chamadas, extrapolando uma amostra anterior de cada candidato. A estimativa não garante o custo do lote; o piloto mostrou custo maior. O orçamento deve ser definido e autorizado pelo operador antes de executar. O registro local dessa autorização não é versionado.

O coletor reserva US$ 0,25 por chamada antes de enviar o próximo par. Essa reserva supera amplamente o custo observado por chamada na amostra, mas **não é um limite imposto pela OCI**. Uma resposta com muitas buscas pode ultrapassar a reserva; chamadas em andamento não podem ser canceladas com garantia de ausência de cobrança. O orçamento é uma condição para interromper novos envios, não uma garantia de teto absoluto na fatura.

## Reprodução

Na raiz do repositório, com o ambiente Python preparado:

```bash
python benchmarks/run_benchmark.py
```

Isso valida o conjunto sem inferência. Somente após definir orçamento autorizado:

```bash
set -a
. ./.env
set +a
python benchmarks/run_benchmark.py --execute --budget-usd LIMITE_AUTORIZADO --pair-limit 4
# Conferir o piloto e depois continuar com o MESMO run-id:
python benchmarks/run_benchmark.py --execute --budget-usd LIMITE_AUTORIZADO
```

A retomada ignora chamadas concluídas e não repete automaticamente interações interrompidas. O manifesto impede misturar prompts, instruções ou preços alterados. Cada execução precisa de um `--run-id` próprio caso se altere o experimento.

Os arquivos em `runs/<run-id>/` incluem registro incremental, respostas brutas, CSV por interação e resumo por modelo. Haverá custo total, média, mediana, percentil 95, buscas, cache, saída, raciocínio, latência e taxa de execução confirmada da busca. Ausência de confirmação não deve ser confundida com resposta factualmente errada; avaliação factual exige uma etapa distinta.

## Resultado executado

O lote completo de 200 interações foi concluído em 15/10/2026. A execução teve uma parada de controle de orçamento após 170 chamadas e retomou sem reenviar nenhuma interação. Foram conferidos 100 pares com payload compartilhado idêntico, 25 intenções por categoria em cada modelo, HTTP 200 e busca confirmada nas 200 respostas.

Os resultados selecionados estão no [relatório final](results/comparison-2026-10-15/REPORT.md). O CSV contém o prompt exato, tokens totais de entrada, cache, saída, raciocínio, chamadas tarifadas e os quatro componentes de custo por interação.

Para regenerar os artefatos selecionados a partir dos registros locais, sem inferência adicional:

```bash
python benchmarks/report.py
```
