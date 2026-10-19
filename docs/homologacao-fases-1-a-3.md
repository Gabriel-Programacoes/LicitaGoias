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

## Atualização de evidências — 19/10/2026

Esta seção complementa o registro histórico acima; não apaga as limitações observadas em 16/10.

### F0 — Baseline definido

O recorte inicial foi registrado em [homologacao-fase-0.md](homologacao-fase-0.md): Goiás, modalidades PNCP 1–14, consulta de propostas abertas, janela diária de 7 dias e reconciliação semanal de 30 dias. Os dois IDs de referência — `01567601000143-1-000276/2026` e `01005727000124-1-000301/2026` — estão no banco, com municípios e objetos esperados. A amostra é de fumaça e não atesta revocação estadual. Considera-se F0 fechada como definição de baseline, com a ressalva de que uma amostra independente estratificada ainda é necessária para medir cobertura.

### F1 — Repetição estadual e paginação ao vivo

O workflow do GitHub Actions concluiu uma coleta estadual (`c7af47a6-a504-4ee1-a7b7-b3dcda115b2d`) para 12–19/10. Em seguida, uma repetição local, usando Session Pooler e o mesmo recorte, concluiu como `complete` (`ccd82519-9b1e-4c9a-990e-5a8e2ef6644f`). A repetição percorreu 15 segmentos e 65 páginas; houve paginação ao vivo nas modalidades 6 (4 páginas), 8 (42) e 9 (7). Foram lidas 2.703 ocorrências de página; 2.702 IDs PNCP distintos ficaram persistidos, sem itens marcados para revisão. Ambos os IDs da amostra permaneceram presentes.

Na repetição, o total de oportunidades subiu de 2.698 para 2.702. A inspeção identificou quatro oportunidades genuinamente novas na janela, com quatro versões/snapshots iniciais, e 2.687 snapshots existentes observados novamente. Logo, a variação não é duplicação; o PNCP devolveu quatro IDs que ainda não estavam no banco. Para separar idempotência de chegada tardia da fonte, ainda é necessário repetir o mesmo recorte estável e confirmar que o número de oportunidades e de versões permanece igual.

Uma falha de rede anterior, causada pelo proxy do ambiente local, ficou registrada como execução `failed` e não gravou páginas. A retomada após falha intermediária está coberta por teste automatizado (página 1 persistida, falha na página 2, retomada desde página 2 e término `complete`), mas ainda não foi induzida numa coleta remota real.

**Estado F1:** coleta conectada, paginação real e amostra de presença confirmadas; idempotência com contagem estável e cobertura estadual ainda aguardam evidência adicional. Não declarar cobertura completa do PNCP.

### F2 — API e isolamento

Os testes automatizados exercitam duas identidades e negam leitura/alteração de organização alheia por ID (404), além de separar perfis, feedback e acompanhamentos. A troca de duas contas reais pela interface já foi homologada pelo usuário. Essa combinação comprova a jornada básica e o isolamento exercitado pelo backend, mas não substitui requisições com JWTs reais de ambas as contas para todos os endpoints. Não há ambiente separado de staging: o provedor de hospedagem não foi escolhido e a criação de branch Supabase foi bloqueada por uma confirmação de custo que esta sessão não consegue aprovar.

**Estado F2:** parcial; separar staging e fazer uma prova direta com tokens reais ainda são pendências.

### F3 — Busca e perfis

A busca foi ajustada para ignorar capitalização e acentos, encontrar palavras em qualquer ordem e atualizar os resultados após 350 ms de pausa na digitação. Os testes locais cobrem o comportamento e a paginação. Também executei a consulta alterada diretamente no PostgreSQL Supabase: `ELETRODOMESTICOS bens` e `eletrodomésticos COMUNS` retornaram o mesmo edital UFG (`01567601000143-1-000276/2026`). Contra a base remota, a paginação de 30 itens retornou 30 itens nas páginas 1 e 2, sem sobreposição; o total era 2.702 oportunidades (91 páginas).

O código ainda precisa ser publicado e a busca em tempo real, os perfis com a base aprovada e a navegação paginada precisam de validação visual na aplicação hospedada. O endpoint de feed continua classificando as oportunidades que já foram coletadas, não buscando diretamente no PNCP por perfil.

**Estado F3:** consulta PostgreSQL e lógica comprovadas; publicação e homologação visual ainda pendentes.

### F4 e F5

O SMTP permanece deliberadamente desligado, conforme decisão do usuário. A estrutura interna de alertas pode ser revisada depois, mas nenhum envio real será habilitado antes da estabilidade da base e da relevância. F5 e piloto comercial continuam fora de avaliação até os critérios acima serem aceitos.
