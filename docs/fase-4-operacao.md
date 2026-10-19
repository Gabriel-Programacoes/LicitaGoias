# Fase 4 — Alertas e notificações

## O que esta implementação entrega

- Registra um alerta por organização acompanhando quando uma versão observada muda; a carga inicial só estabelece a referência.
- Disponibiliza caixa de alertas e preferências de e-mail por usuário e organização, incluindo resumos diário/semanal e alertas críticos.
- Mantém uma outbox idempotente, worker separado, lease de processamento, novas tentativas com espera crescente e estado `dead` após oito tentativas.
- Inclui cancelamento de inscrição por token aleatório, armazenado apenas como hash, e endpoint de webhook assinado para eventos normalizados de entrega, bounce e reclamação.
- Mantém o envio desligado por padrão. O worker só envia com `LICITAGOIAS_EMAIL_ENABLED=true` e `LICITAGOIAS_EMAIL_DOMAIN_VERIFIED=true`.

## Migração do banco

No projeto Supabase conectado, as revisões `0005_phase3_experience`, `0006_phase4_notifications` e `0007_phase4_fk_indexes` já foram aplicadas via MCP; `public.alembic_version` registra `0007_phase4_fk_indexes`. Para outros ambientes, a revisão `0006_phase4_notifications` depende de `0005_phase3_experience`, e `0007_phase4_fk_indexes` adiciona índices cobridores às FKs das duas fases. Aplique-as usando uma credencial administrativa de migração disponível somente no ambiente local. A credencial runtime `licitagoias_app` não tem permissão para alterar `alembic_version` e não deve receber privilégios de DDL.

```powershell
$env:LICITAGOIAS_DATABASE_URL = "postgresql+psycopg://<usuario-de-migracao>:<senha>@<host>:5432/postgres?sslmode=require"
alembic upgrade head
```

Não coloque a URL administrativa no `.env.example`, em commits ou em mensagens. Depois da migração, reconecte a API com a URL runtime `licitagoias_app`.

## Execução local

```powershell
pip install -e .
licitagoias-notify --once
```

Para operação contínua, execute `licitagoias-notify` como processo separado supervisionado pelo serviço do ambiente. Com o e-mail desativado, ele calcula vencimentos de resumos e pode preencher a fila, mas não envia mensagens. A coleta PNCP continua sendo disparada pelo comando de coleta já existente e deve ser agendada pelo operador; esta fase não instala um scheduler de coleta.

## E-mail e Supabase Auth

O transporte da aplicação é SMTP genérico com TLS STARTTLS. Para habilitá-lo, configure host, porta, usuário, senha, remetente, URL pública da aplicação, SPF/DKIM/DMARC e valide primeiro em homologação. Só então habilite as duas flags do worker. A aplicação não escolhe nem presume um provedor.

O SMTP transacional da aplicação é independente do SMTP de autenticação do Supabase. O SMTP Auth (confirmação, recuperação e convite) é configurado no Dashboard do Supabase, em Authentication → SMTP Settings. Não use o remetente transacional para autenticação sem configurar e validar explicitamente os dois fluxos.

Configure `LICITAGOIAS_MAIL_WEBHOOK_SECRET` apenas se o provedor tiver webhook e adapte a assinatura do provedor ao formato documentado pelo endpoint: header `X-LicitaGoias-Signature: sha256=<HMAC-SHA256 do JSON recebido>`. O payload normalizado contém `provider_event_id`, `message_id`, `event_type` (`delivered`, `bounced`, `complained`) e `occurred_at`. Bounces e reclamações suprimem o endereço para futuros envios.

## Limites operacionais conhecidos

- A política de leitura da outbox é destinada ao papel de backend `licitagoias_app`; as tabelas não são expostas aos papéis Data API (`anon`, `authenticated`, `service_role`).
- SMTP não oferece garantia de exatamente uma entrega: se a conexão cair depois de o servidor aceitar a mensagem, a tentativa pode ser repetida. A chave idempotente impede duplicação na fila, mas não pode resolver a ambiguidade de transporte sem idempotência oferecida pelo provedor.
- A tela de preferências funciona por membro da organização atual; o modelo permite várias organizações, mas a interface seleciona a primeira associação até existir seletor de espaço.
- Fase 1/3 precisam ser homologadas antes de tratar estes alertas como operacionais. Nenhuma migração remota foi aplicada nesta implementação.
