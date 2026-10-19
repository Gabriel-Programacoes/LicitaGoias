# Fase 3 — busca, relevância e acompanhamento

## Entrega inicial

A primeira implementação da Fase 3 acrescenta:

- `GET /v1/opportunities`, com busca textual, município, situação, intervalo de abertura e paginação limitada a 100 itens;
- ficha compartilhada e histórico por versão em `/v1/opportunities/{id}` e `/changes`;
- CRUD de perfis da organização, com categorias de licitação, municípios, modalidades PNCP, situações e prazo máximo até a abertura;
- feed com regras determinísticas identificadas como `rules-v2`; oportunidades são avaliadas contra as categorias selecionadas e os filtros estruturados;
- feedback privado por organização;
- acompanhamento idempotente, lista de acompanhadas e remoção;
- interface local em `/app`, servida pela FastAPI e conectada à API no mesmo domínio.

O feed e a busca livre exibem 30 oportunidades por página por padrão. A API aceita tamanhos de página entre 1 e 100.

Na página inicial, a visualização **Todas** também funciona sem perfil de interesse: ela lista a base coletada e mantém paginação. A visualização **Compatíveis** exige um perfil; sem um, a interface oferece a criação de perfil e não envia uma requisição inválida ao feed.

Na busca livre, cada palavra é procurada nos campos de objeto, informação complementar, órgão, município, modalidade, situação e identificador. A comparação não diferencia maiúsculas/minúsculas nem acentos, e a ordem entre palavras não importa. A interface atualiza a lista após uma pausa curta enquanto o usuário digita; respostas antigas não substituem uma consulta mais recente.

Os critérios do perfil são categorias de licitação mantidas pelo LicitaGoias, além de município, modalidade PNCP, situação e prazo máximo até a abertura. Apenas o nome do perfil aceita digitação. Categoria, município, modalidade, situação e prazo atuam sobre a oportunidade. As categorias são correspondidas pelo texto publicado no objeto e na informação complementar; o sistema não consulta códigos nem itens individuais do edital. Se várias categorias forem selecionadas, basta corresponder a uma delas. Sem categoria, o perfil considera todas as áreas, sujeito aos demais filtros.

Perfis criados com o filtro anterior de produtos/serviços continuam legíveis, mas não usam esses critérios no feed. Eles ficam marcados para revisão e precisam ser salvos novamente com categorias de licitação; ao salvar, os critérios antigos são removidos.

Novas tabelas ficam protegidas por RLS e sem acesso para `anon`, `authenticated` e `service_role`; apenas o papel de backend recebe privilégios. O backend continua responsável por validar JWT e vínculo com a organização. A interface usa somente a chave publicável para iniciar uma sessão normal do Supabase Auth.

## Preparar o ambiente

1. Configure as variáveis listadas em `.env.example` no arquivo local `.env`.
2. Mantenha o e-mail de confirmação habilitado no Supabase. O usuário de desenvolvimento precisa estar confirmado e ter senha definida pelo administrador no painel Supabase Auth.
3. No projeto Supabase do LicitaGoias, as revisões `0008_profile_query_filters` e `0009_opportunity_categories` já foram aplicadas em 19/10/2026. A `0009` armazena categorias de licitação nos perfis. Para outro banco existente, aplique com conexão administrativa; a conexão padrão de `.env` usa o papel restrito da API e não altera esquema. Configure `LICITAGOIAS_DATABASE_URL` temporariamente no processo do PowerShell com a URL administrativa `postgresql+psycopg://...` e execute:

   ```powershell
   .venv\Scripts\python.exe -m alembic upgrade head
   Remove-Item Env:LICITAGOIAS_DATABASE_URL
   ```

   Não salve nem compartilhe essa URL. Depois da migração, `scripts/run-local.ps1` carrega a URL restrita mantida em `.env`. Abra `http://127.0.0.1:8000/app`; o contrato da API fica em `/docs`.

Não desabilite a confirmação de e-mail e não use o `service_role` nem a senha de `licitagoias_app` no navegador. SMTP, cadastro público, recuperação por e-mail, cobrança, notificações e hospedagem continuam fora desta fase.

## Comportamento dos dados

- A busca é textual nos registros normalizados e usa paginação estável por `last_observed_at` e ID. Filtros temporais sem data conhecida não tratam o campo ausente como correspondência.
- O feed exige um perfil ativo e consulta apenas oportunidades já coletadas. A categoria é identificada somente a partir de objeto e informação complementar normalizados, sem leitura do JSON bruto nem dos itens do edital. A classificação é textual e pode não identificar objetos descritos de forma incomum; as categorias reduzem o universo de oportunidades, sem garantir correspondência perfeita.
- Municípios, modalidades e situações do perfil são filtros opcionais. A modalidade é pré-filtrada no PostgreSQL quando o registro tem código PNCP; registros legados sem código passam pelo avaliador normalizado. “Recebendo propostas” usa a janela de abertura/encerramento vigente e exclui situações suspensas, canceladas, revogadas ou anuladas. Quando `deadline_days` está definido, a data de abertura ausente, vencida ou além do limite exclui o resultado.
- Os perfis filtram as oportunidades já coletadas no banco. A coleta padrão consulta Goiás, todas as modalidades 1 a 14, e pode ser restringida com `--municipio-ibge`; a coleta estadual ainda precisa de homologação de cobertura.
- A ficha mantém a situação oficial separada do estado derivado, mostra campos ausentes e informa a última observação. Links externos só são apresentados como navegação quando usam HTTPS.
- Ao acompanhar, o hash atual vira a referência daquele cliente. O histórico não chama o primeiro carregamento de uma alteração nova.
- O feedback é armazenado por organização e não altera regras globais.
- A atualização é marcada atrasada após 24 horas. Isso é uma indicação operacional fixa nesta primeira versão, não uma garantia de frequência da fonte.

## Estado de validação

Em 19/10/2026, o banco avançou para `0009_opportunity_category_profiles`; a coluna de categorias foi conferida por introspecção. A busca, ficha e histórico responderam contra oportunidades persistidas. Duas contas Auth foram usadas na interface e o usuário confirmou o isolamento ao alterná-las; os fluxos de acompanhamento e feedback também foram confirmados manualmente. Testes locais exercitam busca sem acentos/case, paginação, autorização por organização, ingestão idempotente e retomada após falha. A cobertura e a classificação ainda precisam de uma amostra mais ampla e revisão de resultados pelo usuário. O fluxo de cadastro/recuperação por e-mail e SMTP permanece adiado. As alterações recentes da busca estão publicadas em `main` no commit `81e5f37`; faltam CI verde e implantação/homologação visual, pois não há hospedagem configurada.
