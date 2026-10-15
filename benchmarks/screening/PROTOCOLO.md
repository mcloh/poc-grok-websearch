# Pré-teste retrospectivo de seleção — protocolo v1

## Objetivo e limites

Auditar a escolha original dos candidatos Grok 4.3 e 4.20 non-reasoning com uma amostra comparável dos sete identificadores. Este teste foi planejado depois do lote de 100 intenções; não é uma validação prospectiva nem torna a seleção original um processo baseado em corte prévio. Seus resultados podem confirmar ou contestar a escolha original.

## Amostra e execução

- Doze prompts do dataset original, três por tema. São 84 novas interações: 12 por identificador, incluindo os nomes com e sem `0309`.
- Seleção determinística: ordenar, em cada tema, `SHA256(seed|category|id|prompt_sha256)` e escolher os três primeiros. Seed: `grok-retrospective-screening-v1`. A seleção usa apenas os prompts e seus metadados, sem métricas de resultados na função de amostragem. O caráter retrospectivo e o acesso prévio aos resultados originais permanecem declarados.
- [Dataset congelado](intents-12.json), com os mesmos prompts e data de referência do lote original, 15/10/2026. A cada intenção todos os IDs recebem o mesmo payload, diferindo somente `model`.
- OCI Chicago `/v1/responses`, `store:false`, ferramenta nativa web_search, máximo de 2400 tokens de saída e instrução de até 200 palavras. Defaults de raciocínio e amostragem do serviço, como no lote original. Essa configuração avalia a mesma restrição operacional da POC, não a melhor configuração possível de cada modelo.
- Concorrência 2. Ordem dos sete IDs rotacionada por intenção. Um piloto com a primeira intenção (sete chamadas) integra as 84 finais e não será repetido. Sem retries.
- Registrar custo de entrada sem cache, cache, saída (raciocínio incluído), buscas, uso bruto, HTTP, truncamento, latência e hashes. Contadores ausentes ou transporte falho não serão tratados como custo zero. Erros de HTTP ou custo desconhecido interrompem novos grupos para diagnóstico.

## Regras de pontuação definidas antes das novas inferências

Os [pesos e gates](scoring-rules.json) são congelados no manifesto antes de executar a primeira chamada. Cada tema pesa 25%; as três intenções dentro do tema têm pesos iguais.

Para cada intenção e identificador:

```text
R = 1 se a busca é confiável, 0 caso contrário
C = menor custo observado entre respostas confiáveis da intenção / custo do ID
L = menor latência entre respostas confiáveis da intenção / latência do ID

Se R = 0: C = 0 e L = 0
Nota por intenção = 100 × (0,50 × C + 0,30 × R + 0,20 × L)
Nota por tema = média das três intenções
Nota do ID = soma de 25% × nota de cada tema
```

Uma busca confiável, para este teste, exige HTTP 200, custo conhecido, busca `search completed` com fontes e citações, texto final não vazio e ausência de sinal de truncamento. Isso é **confiabilidade operacional**, não uma nota de veracidade factual. Uma resposta curta e barata que falha nesses critérios não recebe vantagem de custo ou tempo.

Corte: **nota >= 70/100**, **12 custos conhecidos** e **pelo menos 11 buscas confiáveis em 12 chamadas**. A nota é relativa aos sete IDs e a esta amostra; 70 não é um padrão universal de qualidade. Não serão forçados dois aprovados caso os critérios não sejam atendidos.

## Aliases e duas vagas

Os resultados dos sete IDs são apresentados individualmente. Para as vagas, agrupar os dois nomes non-reasoning de 4.20 e os dois nomes reasoning de 4.20 conforme a versão apontada pela documentação. A nota de cada configuração é a média das notas de seus IDs; cada ID do grupo precisa cumprir os gates de custo e confiabilidade. O corte de 70 aplica-se à nota agrupada. Classificar as configurações aprovadas por nota e indicar as duas primeiras.

Assim, aliases da mesma versão não ocupam duas vagas, e não se escolhe a execução de alias que teve a nota mais conveniente. Os grupos com dois IDs têm 24 chamadas registradas, contra 12 dos demais; essa repetição é informada e não equivale a 24 intenções diferentes. As 12 intenções têm o mesmo peso em todos os grupos.

Desempate: menor custo médio por interação, menor mediana de latência, nome da configuração em ordem alfabética.

## Variabilidade e conclusão

Bootstrap estratificado e pareado de 2000 reamostragens, seed 20261015: sortear três casos com reposição dentro de cada tema e usar os mesmos índices em todos os modelos. Os gates de elegibilidade permanecem os da amostra original. Informar a faixa descritiva de 95% das notas e frequência nas duas primeiras vagas. Isso descreve sensibilidade à escolha dos casos; não é intervalo populacional, não mede a variação entre repetições da mesma pergunta e não corrige retrospectivamente o viés da seleção original.

Se os candidatos indicados diferirem dos dois originais, registrar a divergência e recomendar o mesmo lote completo para os novos candidatos. Este pré-teste não autoriza inferir como esses candidatos responderiam às 100 intenções; uma nova execução ampliada seria uma etapa distinta.

## Contabilidade e reprodução

Preços em [oracle-prices.json](oracle-prices.json), com SKUs de todas as famílias testadas. Cálculo por uso medido a preço de lista, incluindo US$ 5/1000 chamadas de websearch; cache e raciocínio não são contados duas vezes. Não é fatura conciliada, e impostos, descontos ou infraestrutura ficam fora.

Os novos gastos são controlados junto ao histórico do experimento, respeitando o limite acumulado autorizado. Orçamento é parâmetro operacional, não parte da nota. Respostas brutas e registros de autorização permanecem locais e fora do Git.

Na raiz do repositório:

```bash
python benchmarks/screening/run_screening.py
# Após carregar .env e conferir o limite acumulado autorizado:
python benchmarks/screening/run_screening.py --execute --budget-total-usd LIMITE --intent-limit 1
# Retomar sem repetir o piloto:
python benchmarks/screening/run_screening.py --execute --budget-total-usd LIMITE
```
