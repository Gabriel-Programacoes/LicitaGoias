# LicitaGoias

Ferramenta Python para coletar, limpar, classificar e exportar oportunidades de licitacao publica em Goias.

O projeto hoje funciona como um pipeline batch: recebe dados brutos em CSV ou coleta oportunidades recentes no PNCP para Aparecida de Goiania, normaliza os campos principais, remove registros sem utilidade comercial imediata, classifica por pacote e gera arquivos para analise ou envio.

## O que esta implementado

- Processamento de CSV bruto com normalizacao, curadoria, deduplicacao e classificacao.
- Exportacao geral e por pacote em `.csv` e `.xlsx`.
- Coletor PNCP para oportunidades recentes de Aparecida de Goiania.
- Relatorio HTML e texto pronto para WhatsApp com oportunidades recentes.
- Persistencia SQLite via modulo interno `storage.py`.
- Testes automatizados para limpeza, classificacao, formatacao, relatorios e exportacao.

## Estrutura

```text
FoodCall/
  data/
    reports/                 # Saidas de relatorios locais
  docs/
    plano-ferramenta-licitacoes-goias.md
  src/
    licitagoias/
      collectors/            # Contratos e coletores externos
      classification.py      # Pacotes comerciais por palavras-chave
      cleaning.py            # Normalizacao, datas, valores e curadoria
      cli.py                 # Interface de linha de comando
      export.py              # CSV/XLSX
      formatting.py          # Formatacao para leitura humana
      models.py              # Modelo Opportunity
      pipeline.py            # Orquestracao dos fluxos
      reporting.py           # Relatorios HTML e WhatsApp
      storage.py             # SQLite
  tests/
  pyproject.toml
  README.md
```

## Requisitos

- Python 3.11 ou superior.
- Acesso a internet para comandos que consultam o PNCP.
- Chromium do Playwright apenas quando forem implementados coletores baseados em navegador.

## Instalar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m playwright install chromium
```

## Rodar testes

```powershell
python -m pytest
```

## Processar CSV bruto

O CSV de entrada deve conter, idealmente, as colunas abaixo. Alguns aliases tambem sao aceitos pelo normalizador, como `orgao`, `unidade`, `descricao`, `abertura`, `fechamento`, `valor`, `edital`, `processo` e `url`.

- `orgao_comprador`
- `objeto`
- `data_abertura`
- `data_fechamento`
- `valor_estimado`
- `link_edital`
- `status`
- `fonte`
- `municipio`
- `uf`
- `modalidade`
- `numero_processo`
- `link_origem`
- `texto_bruto`

```powershell
licitagoias process --input data/raw/amostra.csv --output-dir data/exports
```

Saidas geradas:

- `oportunidades_curadas.csv`
- `oportunidades_curadas.xlsx`
- `pacote_obras.csv` e `.xlsx`
- `pacote_saude.csv` e `.xlsx`
- `pacote_eventos_alimentacao.csv` e `.xlsx`
- `pacote_tecnologia.csv` e `.xlsx`
- `pacote_sem_pacote.csv` e `.xlsx`, quando houver itens sem classificacao comercial

## Consultar PNCP para Aparecida de Goiania

Lista oportunidades recentes no terminal:

```powershell
licitagoias recent-aparecida --limit 5 --days-back 90
```

Gera relatorio HTML e texto para envio manual por WhatsApp:

```powershell
licitagoias report-aparecida --limit 12 --days-back 90 --output-dir data/reports
```

Saidas padrao:

- `data/reports/relatorio_aparecida.html`
- `data/reports/whatsapp_aparecida.txt`

## Regras de curadoria

O pipeline remove oportunidades que:

- tenham status cancelado, suspenso, revogado, anulado, fracassado ou deserto;
- nao tenham `link_edital` nem `link_origem`;
- nao tenham orgao comprador ou objeto;
- sejam duplicadas pela chave hash calculada a partir de fonte, orgao, processo, objeto, datas e link.

## Pacotes comerciais

A classificacao inicial e baseada em palavras-chave no objeto e no texto bruto:

- `obras`
- `saude`
- `eventos_alimentacao`
- `tecnologia`
- `sem_pacote`

Uma mesma oportunidade pode ser replicada em mais de um pacote quando o texto combina com varias categorias.

## Documentacao complementar

Veja [docs/plano-ferramenta-licitacoes-goias.md](docs/plano-ferramenta-licitacoes-goias.md) para contexto do produto, arquitetura e plano de evolucao.
