# Sensibilidade complementar — cache

A nota de corte principal permanece a definida em `scoring-rules.json`, congelada antes das novas chamadas. Esta análise secundária não altera a seleção principal.

Como a amostra é retirada de um conjunto já usado pelos dois candidatos originais, ela não é holdout. O estado de cache da API gerenciada não foi controlado. Por isso será calculado também um cenário contábil sem desconto de cache:

```text
custo hipotético = input_tokens × tarifa de entrada sem cache / 1.000.000
                + output_tokens × tarifa de saída / 1.000.000
                + web_search_calls × tarifa de busca / 1.000
```

Reaplicar a mesma regra de pontuação aos mesmos 84 registros, mudando apenas essa precificação hipotética da entrada. As latências e os tokens continuam sendo os observados, e não há nova inferência. Isso testa sensibilidade ao desconto financeiro de cache; não simula uma execução fisicamente sem cache nem remove seus efeitos sobre tempo de resposta.

A análise foi especificada durante a coleta e será identificada como secundária e exploratória. A classificação primária usa o custo efetivamente calculado do uso medido a preço de lista, com cache.
