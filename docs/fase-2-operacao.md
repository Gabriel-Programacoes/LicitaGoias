# Fase 2: API, autenticação e organizações

A API da Fase 2 está em `licitagoias.api.app:app`. O backend consulta o Supabase Auth em `/auth/v1/user` para validar cada Bearer token e obter o estado de confirmação do e-mail. O projeto Supabase deve ter **Confirm email** habilitado. O banco de domínio é acessado somente pelo backend.

## Configuração local

Instale as dependências de `pyproject.toml`. O arquivo `.env` deste computador já contém as variáveis para desenvolvimento local e é ignorado pelo Git; `.env.example` documenta o formato sem credenciais reais. Os ambientes `local`, `staging` e `production` devem usar bancos, projetos Supabase e credenciais separados antes de uma implantação pública. A URL do Supabase deve ser a origem do projeto, por exemplo `https://projeto.supabase.co`. Use somente chave publicável na variável `LICITAGOIAS_SUPABASE_PUBLISHABLE_KEY`; nenhuma chave de serviço é necessária para a API.

```powershell
pip install -e ".[dev]"
./scripts/run-local.ps1
```

A migração `0002_phase2` cria `users`, `organizations`, `memberships` e `audit_events` sem modificar as tabelas da ingestão. O banco remoto já recebeu todas as migrações; execute `alembic upgrade head` apenas para novos bancos ou futuras migrações. A verificação local fica em `GET /v1/health`; o contrato está em `/docs` e `/openapi.json`.

### Banco Supabase do projeto LicitaGoias

O projeto Supabase conectado ao Codex tem a referência `mekgyrwzkfpfoavdvwlk` e a origem Auth `https://mekgyrwzkfpfoavdvwlk.supabase.co`. A referência e a URL não são credenciais. A senha do banco e a chave publicável devem ficar somente no ambiente de execução.

Em 15/10/2026, o banco remoto recebeu o esquema até `0007_phase4_fk_indexes`. As revisões `0005`–`0007` acrescentaram busca/acompanhamento e notificações; RLS e política do papel de backend foram verificadas nas tabelas novas. O papel PostgreSQL `licitagoias_app` tem apenas DML necessário nas tabelas de domínio; a senha dele fica fora das migrações.

As migrações Alembic `0001_phase1` a `0004_backend_role` formam o esquema inicial. A terceira habilita RLS nas tabelas de domínio e na tabela de versões do Alembic, retira privilégios de acesso direto dos papéis de API quando existirem e cria índices para chaves estrangeiras. A quarta cria o papel usado exclusivamente pelo backend, seus privilégios e as políticas RLS que permitem as operações do servidor. A API FastAPI valida o token e a associação à organização antes de usar essa conexão. Não use `licitagoias_app` no navegador ou em clientes públicos.

Para desenvolvimento neste computador, o arquivo `.env` ignorado pelo Git contém a URI do Session pooler, a senha gerada para `licitagoias_app`, a origem Auth e a chave publicável. Execute `./scripts/run-local.ps1` em PowerShell para carregar essas variáveis e iniciar a API em `http://127.0.0.1:8000`. Não copie a senha para `.env.example`, CI ou mensagens. Para outro computador ou hospedagem, gere uma credencial própria e configure as variáveis no gerenciador de segredos do ambiente. Em outro banco, aplique `alembic upgrade head` com credencial administrativa e configure a senha do papel runtime separadamente. Cada nova tabela em `public` precisa receber RLS e privilégios definidos na mesma migração.

### Verificação local em 15/10/2026

Com as variáveis do `.env` carregadas no processo, `GET /v1/health` respondeu `200`; a busca no banco remoto retornou 25 oportunidades com cobertura `complete`. Rotas privadas sem token responderam `401`, e OpenAPI respondeu `200`. Depois da validação web, o Supabase contém duas contas Auth confirmadas, dois usuários de domínio, duas organizações e duas memberships. A troca entre contas foi exercitada pela interface; a negação de IDs cruzados ainda precisa de uma verificação autenticada direta pela API, e não há uma implantação separada de homologação.

O Supabase Auth está configurado para confirmação de e-mail e aceita redirecionamentos para `http://localhost:3000/**` e `http://127.0.0.1:3000/**`. O `site_url` é `http://localhost:3000`. A interface web ainda não existe; o fluxo de confirmação com retorno ao navegador dependerá dela. Um provedor SMTP próprio e URLs públicas serão necessários antes de abrir o cadastro para usuários reais.

## Fluxo de identidade

O usuário se autentica no Supabase. A API recebe o JWT no cabeçalho `Authorization: Bearer <token>`, envia o token ao endpoint de usuário do projeto configurado e confere `iss`, `aud`, `exp`, `role` e `sub`. O identificador local `users.auth_subject` corresponde ao `sub` validado. A API atualiza e-mail e estado de confirmação com o objeto de usuário retornado pelo Supabase. Sem confirmação de e-mail, a criação de organização retorna 403.

Um usuário confirmado chama `POST /v1/organizations` com `{"name":"Empresa Exemplo"}`. O backend cria a organização, o vínculo `owner` e o evento de auditoria em uma transação. Repetir o mesmo corpo devolve a organização existente; usar outro nome depois da primeira criação retorna 409. `GET /v1/me` lista apenas os vínculos daquele usuário. `GET` e `PATCH /v1/organizations/{id}` exigem associação; alterar o nome exige papel `owner`.

## CI e implantação

O fluxo `.github/workflows/ci.yml` instala o projeto, sobe PostgreSQL temporário, aplica as migrações e executa as verificações automatizadas. O `Dockerfile` produz a imagem da API. Em homologação, aplique migrações antes de trocar a versão da aplicação e confira `/v1/health` e uma requisição autenticada. Uma reversão da aplicação usa a imagem anterior e mantém o banco na migração nova; não execute `alembic downgrade` automaticamente em produção.

Configure URL pública da API, HTTPS e regras de rede no provedor escolhido. Não habilite acesso direto do navegador ao banco de domínio nem exponha chaves de serviço. A API atual consulta o Supabase Auth em toda requisição privada; uma indisponibilidade do Auth retorna 503 e impede acesso privado. Nenhuma implantação externa está automatizada até definir o provedor de hospedagem e as credenciais de homologação.
