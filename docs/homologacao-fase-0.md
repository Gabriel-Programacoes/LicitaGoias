# Fase 0 — recorte e amostra de homologação

**Versão inicial:** 19/10/2026  
**Finalidade:** definir um recorte operacional reproduzível e uma amostra de fumaça antes de ampliar a alegação de cobertura.

## Recorte escolhido para a primeira validação

- **Fonte:** consultas públicas do PNCP.
- **UF:** Goiás (`GO`), sem limitar município.
- **Modalidades:** códigos PNCP 1 a 14.
- **Consultas:** publicações por modalidade, mais contratações com propostas abertas.
- **Janela operacional:** últimos 7 dias em cada execução; reconciliação semanal dos últimos 30 dias.
- **Paginação:** 50 registros por página, até a última página informada pela API.
- **Propósito:** disponibilizar oportunidades publicadas na base coletada. Os perfis classificam essas oportunidades depois da coleta e não devem impedir que a oportunidade seja persistida.

Este recorte reflete o workflow atualmente implantado. Ele é adequado para homologar a coleta incremental de Goiás; não prova que alterações antigas, fora da janela de 30 dias, serão descobertas. A API de consulta por data de atualização global ainda não faz parte do coletor.

## Amostra oficial de fumaça

Os dois identificadores abaixo vieram de editais que o usuário trouxe como exemplos e foram encontrados na base persistida. Devem continuar aparecendo quando a janela consultada inclui suas datas de publicação. As páginas oficiais do PNCP são a referência para conferir o identificador, o órgão, o município e o objeto.

| Identificador de controle PNCP | Publicação | Modalidade | Município | Órgão / objeto resumido | Página PNCP |
| --- | --- | --- | --- | --- | --- |
| `01567601000143-1-000276/2026` | 16/10/2026 | Pregão eletrônico (6) | Goiânia | UFG — aquisição de eletrodomésticos e bens comuns | [Abrir no PNCP](https://pncp.gov.br/app/editais/01567601000143/2026/276) |
| `01005727000124-1-000301/2026` | 14/10/2026 | Dispensa (8) | Aparecida de Goiânia | APARECIDAPREV — consultoria e assessoria para certificação/manutenção do Pró-Gestão RPPS | [Abrir no PNCP](https://pncp.gov.br/app/editais/01005727000124/2026/301) |

### Resultado no banco em 19/10/2026

Ambos os identificadores foram encontrados em `public.opportunity_records`, com seus identificadores oficiais, município, modalidade, objeto e sem marcação de revisão. Eles estão dentro da janela da execução estadual de 12 a 19/10/2026.

Essa amostra confirma a presença de dois casos conhecidos em modalidades e municípios distintos. Ela **não** mede revocação estadual, não cobre todas as 14 modalidades e não constitui garantia de que nenhum edital será perdido. Uma amostra maior, selecionada independentemente da base coletada e estratificada por modalidade, continuará necessária antes de anunciar cobertura completa.

## Aceite da Fase 0

O recorte e os identificadores desta versão ficam registrados como baseline da primeira homologação. Uma mudança de UF, modalidades, janela ou finalidade exige nova versão deste documento e reconciliação da amostra.
