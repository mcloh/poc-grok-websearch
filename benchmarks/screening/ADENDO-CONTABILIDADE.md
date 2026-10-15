# Adendo de contabilidade — resolução sem nova inferência

Durante a coleta, a interação `I075` com `xai.grok-4.7` retornou HTTP 200 e resposta final com fontes e citações. A classificação financeira inicial foi conservadoramente marcada como desconhecida porque o uso agregado ultrapassou 200 mil tokens de entrada. O coletor concluiu o grupo e parou, como previsto no protocolo.

## Memória de cálculo

Uso da mesma resposta original, preservada sem repetir a chamada:

- Entrada agregada: **249.047 tokens**, dos quais **193.408 em cache**.
- Saída agregada: **6.231 tokens**, dos quais **5.191 de raciocínio**.
- Websearch tarifado: **15 chamadas**.
- Campo nativo transportado na resposta OCI: `cost_in_usd_ticks = 5657360000`.
- `context_details.input_tokens = 56428` não é o mesmo contador que a entrada total do loop. Não foi usado em substituição ao total para precificação.

A [documentação oficial do campo de custo](https://docs.x.ai/developers/cost-tracking) define 10.000.000.000 ticks por USD. Ela foi consultada apenas como documentação; **nenhuma chamada de inferência foi enviada à API direta da xAI**.

Os SKUs Oracle de contexto longo para Grok 4.7, congelados antes do teste, são US$ 4 de entrada, US$ 1 de cache e US$ 12 de saída por milhão de tokens; a busca custa US$ 5 por mil chamadas.

```text
Entrada sem cache: (249047 - 193408) × 4 / 1.000.000 = USD 0,222556
Cache:             193408 × 1 / 1.000.000          = USD 0,193408
Saída:             6231 × 12 / 1.000.000           = USD 0,074772
Websearch:         15 × 5 / 1.000                  = USD 0,075000
Total calculado pelos SKUs Oracle                 = USD 0,565736
Custo nativo:      5657360000 / 10.000.000.000     = USD 0,565736
```

A fórmula de contexto curto resultaria em USD 0,320368 e não coincide com o valor nativo. Assim, a faixa longa foi identificada de maneira única por conciliação aritmética dos SKUs Oracle com a mesma resposta. Isso não constitui conciliação com a fatura da conta OCI.

## Tratamento neutro e rastreável

O evento inicial com custo desconhecido permanece no registro. Um evento adicional `cost_reconciled` resolve a faixa e a confiabilidade financeira da **mesma execução**, preservando os contadores e o hash do payload. Os pesos, o corte, a amostra e os critérios de busca não foram alterados. Não se penaliza o modelo pela limitação do classificador de custos quando a cobrança pode ser determinada.

A partir desse diagnóstico, qualquer interação com uso agregado acima de 200 mil tokens terá a faixa resolvida somente se uma das fórmulas de preço congeladas coincidir exatamente com o campo nativo. Se não houver correspondência única, continuará com custo desconhecido e exigirá diagnóstico.

Também foi observado que o parâmetro `max_output_tokens=2400` não impediu que o `usage` agregado da execução com ferramentas reportasse mais de 2400 tokens de saída. O valor configurado permanece igual nos modelos. A medição e a cobrança usam o uso total retornado, não um teto teórico de tokens por interação. Não houve truncamento indicado nessa resposta.
