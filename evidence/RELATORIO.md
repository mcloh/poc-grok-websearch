# Validação — 14/10/2026

A POC foi publicada em uma VM OCI e testada por HTTPS. O resumo compartilhável está em [validation-summary.json](validation-summary.json).

| Critério | Resultado |
|---|---|
| REST sobre notícia de hoje | HTTP 200; 36,12 segundos |
| Serviço e modelo | OCI Chicago; xai.grok-4.3 |
| Busca nativa | Duas buscas concluídas e uma abertura de página; uma tentativa inicial falhou |
| Citações | Duas citações da mesma notícia |
| Fonte verificada independentemente | HTTP 200; data visível 14/10/2026 às 08:17 |
| Acesso não autenticado | HTTP 401 |
| Histórico com papel inválido | HTTP 422 |
| Desktop e celular | Sem erros de JavaScript e sem overflow horizontal |
| Renderização | Resposta REST real usada como fixture; texto e links conferidos |

Fonte: [Agência Brasil — Confira a agenda dos presidenciáveis nesta quarta-feira (14)](https://agenciabrasil.ebc.com.br/politica/noticia/2026-10/confira-agenda-dos-presidenciaveis-nesta-quarta-feira-14). A data coincide no texto visível e no metadado; o horário difere (08:17 no texto e 11:17 no metadado). O resumo registra o horário visível.

A ferramenta executou uma busca inicial que falhou, reformulou consultas e concluiu a pesquisa. As respostas brutas, identificadores OCI, capturas e cópia integral da fonte permanecem locais e não são versionados. O SHA-256 da fonte permite conferir o artefato local.

A chamada final consumiu 15.544 tokens. Incluindo os diagnósticos bem-sucedidos, foram 34.829 tokens e nove ferramentas contabilizadas pelo serviço. A escala financeira de cost_in_usd_ticks não foi verificada; o campo é preservado sem conversão para dólares.
