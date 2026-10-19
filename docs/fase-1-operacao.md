# Fase 1: ingestão PNCP

A ingestão persistente usa PostgreSQL. Os comandos antigos de CSV e relatório continuam disponíveis. A coleta padrão consulta todo o estado de Goiás, sem filtro de município, e percorre as modalidades PNCP 1 a 14; use `--municipio-ibge` para restringir uma execução. A cobertura ainda precisa ser homologada contra uma amostra oficial antes de ser anunciada como completa. Em 16/10/2026, o usuário informou que a consulta anterior não retornou resultados válidos para a validação esperada; a nova janela estadual precisa ser reconciliada com uma amostra oficial.

## Preparação

Instale o projeto com `pip install -e .`. Crie um banco PostgreSQL vazio e configure `LICITAGOIAS_DATABASE_URL` como URL `postgresql+psycopg://usuario:senha@host:5432/banco`. No PowerShell:

```powershell
$env:LICITAGOIAS_DATABASE_URL = "postgresql+psycopg://usuario:senha@localhost:5432/licitagoias"
alembic upgrade head
```

Mantenha credenciais fora do repositório. A migração `0001_phase1` cria execuções, progresso por segmento, páginas, oportunidades, versões e snapshots brutos.

## Coletar e retomar

```powershell
licitagoias sync-pncp --uf GO --start 2026-10-01 --end 2026-10-15
licitagoias sync-pncp --municipio-ibge 5201405 --uf GO --start 2026-10-01 --end 2026-10-15
licitagoias collection-runs
licitagoias sync-pncp --municipio-ibge 5201405 --uf GO --start 2026-10-01 --end 2026-10-15 --resume-run ID_DA_EXECUCAO
licitagoias opportunity-history --external-id NUMERO_CONTROLE_PNCP
```

A retomada exige o mesmo município (ou a mesma coleta estadual), UF, datas e modalidades. Cada página e seu checkpoint são gravados na mesma transação. Uma página com erro interrompe a execução; o status fica `partial` se páginas anteriores foram gravadas e `failed` caso contrário. Uma resposta vazia válida fica registrada como página concluída com zero registros. Uma nova execução, sem `--resume-run`, revisita a janela inteira e permite detectar retificações. A coleta estadual percorre mais páginas; prefira janelas menores e execuções incrementais agendadas.

O campo `current_data` contém o valor normalizado; `source_snapshots.raw_data` preserva a resposta original do PNCP. Datas guardam texto original, precisão e indicação de fuso. Prazo ausente continua ausente. O status oficial é preservado; `derived_state` só distingue suspenso, encerrado e desconhecido nesta fase. Um identificador oficial PNCP define a identidade. Quando ausente, o sistema usa órgão, processo, ano e unidade, ou o hash bruto em último caso, e marca o registro para revisão.

## Importar SQLite legado

Faça uma cópia de segurança do arquivo antes da importação. O importador abre o SQLite em modo somente leitura e separa seus registros na fonte `legacy_sqlite`. Ele não presume que um hash antigo identifique o mesmo processo no PNCP.

```powershell
licitagoias import-legacy-sqlite --input data/licitagoias.db
```

A saída mostra linhas lidas, importadas e conflitos. Execute novamente para conferir idempotência. Conflitos precisam de revisão manual; o comando não altera a origem nem associa registros legados a oportunidades PNCP automaticamente.

## Limites operacionais

A coleta de propostas abertas é consultada uma vez por execução, e as publicações são consultadas por modalidade no intervalo informado. O workflow [pncp-sync.yml](../.github/workflows/pncp-sync.yml) agenda seis coletas diárias com janela móvel de sete dias e uma reconciliação semanal de 30 dias. Para ativá-lo, publique o workflow no repositório GitHub e cadastre o secret `LICITAGOIAS_DATABASE_URL` com a URI PostgreSQL do projeto. O status `complete` indica que os segmentos configurados terminaram, não que todas as publicações do mercado estejam presentes; indisponibilidade ou atraso na fonte ainda pode afetar a cobertura. A API de sincronização por data de atualização global ainda não está integrada, então alterações em processos mais antigos que a janela semanal podem não ser detectadas por este agendamento.
