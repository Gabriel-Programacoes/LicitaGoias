# Plano da Ferramenta de Prospeccao de Licitacoes em Goias

## Visao geral

A ferramenta identifica oportunidades de licitacao publicadas por orgaos estaduais e municipais de Goias, transforma dados desorganizados em uma base confiavel e entrega listas comerciais segmentadas por tipo de fornecedor.

O valor do produto nao esta apenas na captura. A captura e instavel por natureza, especialmente em portais publicos antigos. O diferencial e a curadoria: deduplicar, remover licitacoes canceladas ou irrelevantes, padronizar campos e separar oportunidades em pacotes vendaveis.

O estado atual do projeto e um MVP de linha de comando. Ele processa CSV bruto, consulta o PNCP para Aparecida de Goiania, gera planilhas por pacote e cria relatorios HTML/texto para distribuicao manual.

## Fontes alvo

Fontes do MVP:

- Portal de Compras do Estado de Goias.
- TCM-GO.
- Diarios Oficiais municipais da Regiao Metropolitana de Goiania.
- PNCP como fonte complementar estruturada.

O PNCP deve ser priorizado sempre que trouxer o mesmo dado com API ou dados abertos, pois o portal oficial centraliza informacoes sobre contratacoes publicas e disponibiliza consulta/dados abertos. Os portais locais continuam necessarios porque podem publicar anexos, detalhes ou oportunidades antes de integrarem corretamente ao PNCP.

## Estrategia tecnica

### Coleta

- Usar `Playwright` para sites com JavaScript, formularios, ASP.NET ViewState, iframes e paginacao quebrada.
- Usar `requests` para APIs ou endpoints estaveis, especialmente PNCP.
- Salvar snapshots brutos de HTML/JSON/PDF em `data/raw/` para auditoria e reprocessamento.
- Registrar erros por fonte sem interromper a execucao inteira.

No codigo atual, o coletor implementado e `PNCPCollector`, que consulta endpoints publicos do PNCP para Aparecida de Goiania usando `requests`. A infraestrutura de Playwright existe como base para coletores futuros, mas os seletores dos portais locais ainda nao foram implementados.

### Normalizacao

Cada oportunidade deve ser convertida para um modelo unico com:

- `orgao_comprador`
- `objeto`
- `data_abertura`
- `data_fechamento`
- `valor_estimado`
- `link_edital`
- `fonte`
- `municipio`
- `uf`
- `modalidade`
- `status`
- `numero_processo`
- `data_coleta`
- `hash_deduplicacao`
- `link_origem`
- `texto_bruto`

### Curadoria

Regras iniciais:

- Excluir status como `cancelada`, `suspensa`, `revogada`, `anulada`, `fracassada`, `deserta` e equivalentes.
- Exigir link rastreavel para edital, pagina de detalhe ou publicacao oficial.
- Deduplicar por uma chave estavel formada por fonte, orgao, numero do processo, objeto, datas e link.
- Preservar texto bruto para investigacao quando algum campo normalizado estiver incompleto.

## Pacotes comerciais

Classificacao inicial por palavras-chave:

- Obras: asfalto, pavimentacao, cimento, concreto, reforma, escola, ponte, drenagem, maquinario, construcao, engenharia.
- Saude: medicamentos, insumos hospitalares, EPI, luvas, mascaras, ambulancia, exames, material odontologico, hospitalar.
- Eventos/Alimentacao: merenda, generos alimenticios, buffet, coffee break, tendas, som, palco, iluminacao, eventos.
- Tecnologia: computadores, notebooks, impressoras, toners, cartuchos, rede, internet, firewall, software, cameras, servidores.

Uma oportunidade pode aparecer em mais de um pacote se o objeto for ambiguo. Isso e aceitavel no MVP porque reduz falso negativo comercial.

## Estrutura implementada

```text
FoodCall/
  data/
    reports/
  docs/
    plano-ferramenta-licitacoes-goias.md
  src/
    licitagoias/
      collectors/
      classification.py
      cleaning.py
      cli.py
      export.py
      formatting.py
      models.py
      pipeline.py
      reporting.py
      storage.py
  tests/
  pyproject.toml
  README.md
```

## Interface de linha de comando

O pacote instala o comando `licitagoias`.

### `process`

Processa um CSV bruto e exporta arquivos curados:

```powershell
licitagoias process --input data/raw/amostra.csv --output-dir data/exports
```

Saidas:

- `oportunidades_curadas.csv`
- `oportunidades_curadas.xlsx`
- arquivos `pacote_<nome>.csv`
- arquivos `pacote_<nome>.xlsx`

### `recent-aparecida`

Consulta o PNCP, normaliza e imprime oportunidades recentes de Aparecida de Goiania:

```powershell
licitagoias recent-aparecida --limit 5 --days-back 90
```

### `report-aparecida`

Gera um relatorio HTML e um texto para envio manual por WhatsApp:

```powershell
licitagoias report-aparecida --limit 12 --days-back 90 --output-dir data/reports
```

Saidas padrao:

- `relatorio_aparecida.html`
- `whatsapp_aparecida.txt`

## Fluxo do pipeline

1. Receber registros brutos via CSV ou coletor PNCP.
2. Converter cada registro para o modelo normalizado `Opportunity`.
3. Padronizar textos, datas e valores monetarios.
4. Remover registros cancelados, suspensos, sem link rastreavel, sem orgao ou sem objeto.
5. Deduplicar oportunidades por hash estavel.
6. Classificar por pacote comercial.
7. Exportar CSV/XLSX geral e por pacote ou renderizar relatorios.

## Componentes principais

- `models.py`: define o dataclass `Opportunity` e a chave de deduplicacao.
- `cleaning.py`: normaliza registros brutos, parseia datas/valores e aplica regras de curadoria.
- `classification.py`: classifica oportunidades por palavras-chave.
- `collectors/pncp.py`: coleta oportunidades recentes do PNCP para Aparecida de Goiania.
- `pipeline.py`: orquestra os fluxos usados pelo CLI.
- `export.py`: gera planilhas CSV/XLSX.
- `reporting.py`: gera HTML e texto para WhatsApp.
- `storage.py`: oferece persistencia SQLite para uso futuro em historico local.

## Testes

A suite em `tests/` cobre:

- parse e limpeza de campos;
- remocao de oportunidades invalidas;
- deduplicacao;
- classificacao por pacote;
- formatacao de linhas comerciais;
- exportacao CSV/XLSX;
- geracao de relatorios HTML e WhatsApp.

Executar:

```powershell
python -m pytest
```

## Plano de evolucao

1. Implementar seletores reais do Portal de Compras de Goias com Playwright.
2. Implementar coletor TCM-GO com tolerancia a paginacao e downloads.
3. Mapear diarios municipais prioritarios: Goiania, Aparecida de Goiania, Senador Canedo, Trindade, Goianira e demais municipios metropolitanos.
4. Persistir coletas em SQLite usando `storage.py` para criar historico reprocessavel.
5. Adicionar extracao de texto de PDFs com OCR opcional quando o edital for imagem.
6. Criar revisao manual simples para corrigir classificacao antes da entrega ao cliente.
7. Separar configuracao por municipio, fonte e pacote comercial.
8. Trocar SQLite por Postgres se houver dashboard, multiplos usuarios ou grande volume historico.

## Criterios de aceite

- O pipeline processa um CSV bruto e gera planilhas por segmento.
- Os campos essenciais aparecem nas exportacoes.
- Licitacoes canceladas, suspensas ou sem link sao removidas.
- Datas e valores sao normalizados.
- Registros duplicados sao removidos.
- A classificacao separa oportunidades nos quatro pacotes iniciais.
- O comando de relatorio de Aparecida gera HTML e texto para WhatsApp.
- Testes automatizados cobrem limpeza, deduplicacao, classificacao, formatacao, relatorios e exportacao.

## Riscos

- Mudancas frequentes de layout nos portais.
- Captchas, bloqueios por IP ou instabilidade fora do horario comercial.
- PDFs escaneados sem texto extraivel.
- Dados inconsistentes entre fonte local e PNCP.
- Publicacoes municipais sem padrao de nomenclatura.

## Referencias

- PNCP: https://www.gov.br/pncp/pt-br
- API de consulta PNCP: https://pncp.gov.br/api/consulta/swagger-ui/index.html
