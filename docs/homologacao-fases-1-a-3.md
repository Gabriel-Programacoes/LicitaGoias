# Homologação das Fases 1–3

**Data:** 16/10/2026

**Projeto:** Supabase `mekgyrwzkfpfoavdvwlk`

**Resultado:** homologação parcial; nenhuma das três fases recebe aceite integral com as evidências atuais.

## Evidências executadas

| Fase | Verificação | Resultado |
| --- | --- | --- |
| F1 — ingestão | Duas execuções reais do PNCP, Aparecida de Goiânia (`5201405`), GO, modalidades `6,8,9,5`, período `2026-10-01` a `2026-10-15` | Ambas `complete`; 5 segmentos/páginas por execução. A primeira trouxe 25 registros; a segunda não duplicou dados. |
| F1 — integridade | Contagem no PostgreSQL após repetição | 25 oportunidades, 25 IDs externos distintos (todos oficiais), 25 versões iniciais e 25 snapshots distintos; nenhum processo marcado para revisão. 11 oportunidades não têm data de encerramento informada pela fonte. |
| F1 — lógica | Testes locais | Reexecução idempotente, versão posterior comparável e alerta após acompanhamento passaram; paginação de duas páginas simulada passou. |
| F2 — conexão | Aplicação local com variáveis do `.env` carregadas | `GET /v1/health` retornou `200`; as chamadas executaram `SELECT 1` com a conexão runtime ao PostgreSQL remoto. O `.env` não foi exibido. |
| F2 — contrato e recusa | API local | `/openapi.json` retornou `200`; `/v1/me` e `/v1/opportunities` sem credencial retornaram `401`. |
| F2 — identidade e organização | Testes locais existentes | Validação de claims inválidas, confirmação de e-mail, criação idempotente e isolamento entre organizações simulados passaram. |
| F2 — jornada Auth real | Duas contas confirmadas usadas no app local | Supabase contém 2 usuários Auth confirmados, 2 usuários de domínio, 2 organizações e 2 memberships. O usuário confirmou a troca entre contas pela interface. |
| F3 — leitura real | API local conectada ao Supabase, usando identidade substituída somente em memória para o teste | Busca retornou 25 oportunidades com cobertura `complete`; ficha e histórico retornaram `200`; o histórico inicial teve zero alterações falsas. Lista de perfis retornou vazia. |
| F3 — isolamento | Teste local com SQLite em memória e dois usuários/organizações | Perfis, acompanhamentos e feedback ficaram isolados; repetição de acompanhamento foi idempotente. |
| F3 — sessão real e interface | App local com duas contas confirmadas | O usuário confirmou que a interface limpa os dados da conta anterior ao trocar de conta. |
| F3 — ações reais e isolamento entre contas | Verificação manual concluída pelo usuário em 16/10/2026 | O usuário confirmou que todos os passos de criar/remover acompanhamentos, enviar feedback e verificar a separação entre as contas foram concluídos com sucesso. |
| F1 — utilidade da cobertura | Consulta PNCP usada para a validação | O usuário informou que ainda não retornou resultados válidos; cobertura e reconciliação permanecem pendentes. |
| Suíte automatizada | `pytest -q -k "not test_process_records_exports_files" -p no:cacheprovider` | 17 passaram. Um teste de exportação foi excluído porque o Windows negou acesso ao diretório temporário do pytest; não é falha funcional do teste. |

## Estado encontrado no Supabase

- Alembic está em `0007_phase4_fk_indexes`; a tabela de execução de migrações também lista `0005`, `0006` e `0007`.
- A coleta PNCP criou duas execuções completas, 25 oportunidades, 25 versões e 25 snapshots.
- No recheck de 15/10, o banco continha 2 usuários Auth confirmados, 2 usuários de domínio, 2 organizações, 2 memberships e 2 perfis, além de 25 oportunidades. A contagem de acompanhamentos/feedback documentada acima é anterior à verificação manual concluída pelo usuário em 16/10 e não deve ser tomada como estado atual.
- A execução real cobriu somente uma página por segmento; a paginação com mais de uma página foi simulada localmente, não observada ao vivo. Não houve retificação real no período para validar uma nova versão contra a fonte.

## Decisão por fase

### Fase 1 — Parcial

Esquema, conexão runtime, coleta ao vivo, registros completos, IDs oficiais e repetição idempotente foram verificados. A cobertura aceita da Fase 0 ainda precisa ser definida; não há amostra/SQLite legado reconciliada; a execução ao vivo não exercitou múltiplas páginas, falha intermediária, retry de 429/timeout ou retificação real. As lógicas simuladas passaram nos testes locais. A cobertura medida neste relatório é apenas o recorte de Aparecida/modalidades/janela informados.

### Fase 2 — Parcial (jornada básica validada)

API, health, OpenAPI, recusa de acesso sem token e testes simulados de claims e autorização passaram. A autenticação real, sincronização dos dois usuários, criação de organizações distintas e acesso pela interface foram exercitados. Falta provar em requisições autenticadas diretas que IDs cruzados de organização são sempre negados; também não há implantação separada de homologação comprovada nesta execução.

### Fase 3 — Jornada manual confirmada; integração de dados pendente

Busca, ficha e histórico leram dados reais do PostgreSQL; os perfis e a troca de contas foram validados. Em 16/10, o usuário confirmou a conclusão com sucesso dos fluxos reais de acompanhamento, remoção, feedback e separação entre contas. A jornada ainda não recebe aceite integral enquanto a coleta PNCP não apresentar resultados considerados válidos e a amostra não for reconciliada à cobertura aprovada.

## Próximas evidências necessárias para aceite integral

1. Definir e registrar a cobertura PNCP aprovada na Fase 0, com amostra e reconciliação documentadas; investigar por que a consulta atual não retornou resultados válidos para o uso esperado.
2. Validar multipágina, erro/retomada e retificação com fixtures e pelo menos um caso controlado observado na fonte.
3. Reconciliar uma amostra real válida com a cobertura escolhida na Fase 0 e exercitar cenários de erro/retomada previstos para F1.
4. Validar via API autenticada a negação de leitura/alteração direta por IDs de outra organização.
5. Registrar a confirmação do usuário sobre a jornada com duas contas e reavaliar o aceite após resolver a cobertura PNCP.
