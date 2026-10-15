# Adendo operacional — rejeições por limite compartilhado de tokens

Após seis intenções completas (42 respostas com uso), os sete identificadores receberam HTTP 429 no envio da intenção `I056`. O erro reportou consumo de 634.873 tokens diante de uma quota compartilhada de 600.000 tokens por minuto. Os identificadores de credenciais retornados no erro permanecem apenas nos arquivos privados e não são publicados.

## Recuperação limitada e igual para os sete IDs

As rejeições não retornaram resposta do modelo nem contadores de uso. Não são usadas como nota de qualidade ou de busca de um modelo. Para completar a mesma amostra de 12 respostas em cada ID:

- preservar cada tentativa 429 e seu corpo bruto em arquivo privado separado;
- registrar eventos `infrastructure_rejected`, sem apagar ou sobrescrever as tentativas no ledger;
- após a janela de taxa, repetir **uma vez** o grupo rejeitado, nos mesmos sete IDs e com o mesmo payload;
- não reexecutar nem escolher entre respostas já concluídas; inclusive os casos caros de contexto longo permanecem na amostra;
- inserir pausa de 75 segundos antes dos grupos restantes, mantendo concorrência 2 e rotação da ordem dos IDs;
- se houver outra rejeição, interromper novamente para diagnóstico; não há loop automático de retries.

A pausa não entra na latência individual: o cronômetro mede a requisição. O ritmo de envio mudou durante a coleta e isso é uma limitação operacional declarada; os sete IDs de cada intenção seguem a mesma política de execução e a comparação de tempo é relativa ao mesmo caso.

## Transparência de amostra e custo

A matriz avaliável continua com 12 respostas por ID, totalizando 84 inferências concluídas. Com a recuperação, há sete tentativas HTTP adicionais rejeitadas por infraestrutura, registradas separadamente. Portanto, não será declarado que foram feitos somente 84 POSTs HTTP.

Os sete erros não serão contabilizados como custo zero: não há `usage` para precificá-los. Eles ficam fora das médias da matriz de respostas com custo conhecido e mantêm uma reserva conservadora de US$ 0,50 por tentativa no controle interno do orçamento acumulado. O relatório financeiro continuará identificado como custo conhecido calculado a preço de lista, sem conciliação com fatura.

O protocolo primário continua preservado. Pesos, corte, gates para as 12 respostas de cada ID, amostra e preços não foram alterados. Este adendo documenta uma recuperação manual de falha compartilhada de infraestrutura e o controle de taxa necessário para completar a amostra, em vez de transformar a falta de resposta em uma penalização artificial de todos os candidatos.
