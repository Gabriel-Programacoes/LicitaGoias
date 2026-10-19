# LicitaGoias — Planejamento da plataforma por assinatura

**Versão:** 1.0 • **Data:** 14 de outubro de 2026 • **Responsável pelo projeto:** Gabriel Barbosa

**Status:** proposta de produto e execução para validação. Preços, limites, orçamento e esforço são hipóteses de planejamento, não cotações, compromissos comerciais ou demanda comprovada.

## 1. Decisão central

Transformar o MVP Python em uma plataforma web por assinatura para empresas encontrarem, entenderem e acompanharem oportunidades de compras públicas em Goiás, com seleção personalizada e comunicação por e-mail.

O produto deve responder rapidamente:

1. Esta oportunidade corresponde ao que minha empresa fornece?
2. Onde será feita a entrega ou execução e ainda dá tempo de participar?
3. Quais itens, documentos e condições preciso conferir?
4. O que mudou desde a última vez que consultei?

**Proposta de valor:** reduzir o trabalho de procurar e filtrar licitações, apresentar informações verificáveis e acompanhar mudanças nas oportunidades escolhidas pelo cliente.

O LicitaGoias será uma ferramenta de descoberta e acompanhamento. A participação continuará nas plataformas oficiais indicadas por cada processo. Não haverá promessa de vitória, habilitação automática ou cobertura integral de publicações não verificadas.

## 2. Premissas e limites deste documento

- Produto destinado inicialmente a fornecedores privados; assessorias entram em uma expansão posterior.
- Desenvolvimento conduzido principalmente por uma pessoa, reaproveitando Python e a experiência existente com React, TypeScript e Next.js.
- Primeiro lançamento com um plano pago. A arquitetura comercial contempla três planos, ativados conforme as funcionalidades amadurecerem.
- Cobertura inicial proposta: Aparecida de Goiânia e Goiânia, condicionada à validação das fontes e à existência de oportunidades úteis para o segmento escolhido.
- A coleta implementada hoje é do PNCP, configurada por padrão para Aparecida. As demais fontes são candidatas, não integrações prontas.
- Análise do repositório feita nesta conversa por leitura de README, planejamento e módulos centrais. Não foram executados testes nem uma auditoria integral do código.
- Referências de mercado e documentação técnica foram consultadas em 14/10/2026. Confirmar versões, contratos e preços dos fornecedores ao iniciar a implementação.

## 3. Mercado, posicionamento e público inicial

O PNCP permite consulta pública e gratuita [S1]. A Effecti também anuncia um plano gratuito com oportunidades relacionadas ao perfil da empresa [S2]. Portanto, busca personalizada e acesso a dados públicos não devem ser apresentados como diferenciais exclusivos.

**Hipótese competitiva:** fornecedores locais podem pagar por resultados mais relevantes para seus produtos, uma ficha mais clara, acompanhamento confiável e configuração inicial assistida. Essa hipótese precisa ser testada com empresas reais.

### 3.1 Cliente ideal inicial

Pequena empresa que já participou ou está preparada para participar de licitações, possui alguém responsável pela atividade e pesquisa manualmente oportunidades na região em que atende.

Segmentos candidatos: equipamentos e manutenção de informática; materiais e serviços de manutenção predial; alimentação e eventos. Escolher **um segmento principal** após observar volume, qualidade dos dados e acesso a potenciais clientes. A familiaridade de Gabriel com TI ajuda nas entrevistas e na classificação, mas não comprova demanda suficiente nesse segmento.

### 3.2 Públicos para expansão

| Público | Necessidade | Momento |
| --- | --- | --- |
| Pequeno fornecedor com responsável único | Seleção, clareza e lembretes | Lançamento |
| Empresa com equipe comercial | Divisão de acompanhamento, responsáveis e notas | Plano Equipe |
| Assessoria com vários clientes | Separação por empresa e relatórios por carteira | Produto posterior |
| Empresa sem experiência em licitações | Orientação operacional extensa | Não priorizar; avaliar conteúdo e parceiros |

Não transformar o suporte da assinatura em consultoria ilimitada. Publicar claramente o que o atendimento cobre.

## 4. Estado atual e reaproveitamento

Base observada em [R1–R7].

| Componente | Situação observada | Evolução proposta |
| --- | --- | --- |
| Coletor PNCP | Consultas recentes e propostas; recorte padrão em Aparecida | Cobertura configurável, paginação completa e registro de execução |
| Normalização e modelo | Campos principais e hash de deduplicação | Identidade estável, proveniência, publicação e horários preservados |
| Classificação | Palavras-chave em objeto e texto bruto | Produtos, termos negativos, regras por contexto e revisão |
| Pipeline | CSV e geração de relatórios | Ingestão persistente, incremental e reprocessável |
| SQLite | Módulo de persistência independente | Migração para PostgreSQL e integração aos fluxos |
| Relatórios | CSV, XLSX, HTML e texto para WhatsApp | Exportação no painel e modelos de e-mail |
| Testes | Arquivos para limpeza, classificação, formatação, relatório e exportação | Acrescentar contratos de coleta, isolamento, cobrança e entrega |
| Web e assinatura | Não identificadas na árvore consultada | Implementar aplicação, autenticação, acesso e cobrança |

### 4.1 Correções prioritárias antes da cobrança

1. **Paginação:** eliminar o uso de primeira/última página como substituto de uma coleta abrangente. Guardar checkpoints e marcar execuções incompletas.
2. **Identidade:** usar identificador oficial, como número de controle PNCP, quando disponível. Datas e objeto pertencem à versão, não à identidade principal.
3. **Deduplicação:** remover a deduplicação definitiva baseada apenas nos primeiros 12 termos e valor. Conservar processos diferentes; usar similaridade somente para sugerir vínculos.
4. **Prazos:** não preencher encerramento com data de publicação. Preservar ausências, horário e fuso; separar data de publicação de abertura.
5. **Falhas:** distinguir resultado vazio, parcial, indisponibilidade e erro de formato. Não comunicar “nenhuma oportunidade” após falha de coleta.
6. **Histórico:** conservar suspensões, cancelamentos e retificações na base. Retirá-los das recomendações ativas, sem apagar o acompanhamento do cliente.
7. **Classificação:** evitar que todo o JSON bruto produza associações irrelevantes. Classificar campos escolhidos, com regras versionadas e motivo rastreável.

## 5. Escopo por versão

### 5.1 Piloto operacional

Base persistente confiável, coleta monitorada, um segmento, uma região e relatórios personalizados com revisão humana. Pode ser operado antes de a plataforma inteira estar pronta, com entrega e cobertura combinadas com os participantes.

### 5.2 V1 comercial — plano Essencial

- Cadastro, confirmação de e-mail, recuperação de acesso e perfil da empresa.
- Pesquisa por objeto, filtros, ordenação e buscas salvas.
- Feed por interesse com motivos de correspondência.
- Ficha da licitação com fonte, prazo, valor, atualização e documentos disponíveis.
- Favoritos, acompanhamento e histórico de alterações detectadas desde a coleta.
- Resumo diário ou semanal; alertas críticos de alterações nas acompanhadas.
- Preferências, descadastro de alertas e controle de entregas.
- Checkout, assinatura, cancelamento e controle de acesso.
- Administração de coleta, revisão, clientes e falhas.
- Página pública de cobertura e atualização.

### 5.3 V1.1 — plano Profissional

Busca em itens estruturados, maior número de perfis e acompanhamentos, resumo duas vezes ao dia, exportações ampliadas e calendário. Incorporar dados extraídos de PDF apenas com referências e tratamento de falhas.

### 5.4 V2 — plano Equipe

Convites, papéis, notas compartilhadas, responsáveis e etapas de acompanhamento. Cada organização representa uma empresa; várias empresas na carteira de uma assessoria exigirão modelo e plano próprios.

### 5.5 Fora do escopo inicial

Robô de lances; envio automático de propostas; certificação digital; execução de procedimentos no portal oficial; parecer jurídico; ERP; gestão completa de contratos; aplicativo nativo; API pública para revenda; cobertura nacional; chat genérico com IA; repositório de documentos privados da empresa.

## 6. Jornadas do usuário

### 6.1 Primeiro acesso

Cadastro → verificação do e-mail → empresa e região → produtos/serviços → exclusões → prévia dos resultados → preferências de e-mail → pesquisa e primeiro acompanhamento.

O usuário deve ver resultados durante a configuração. Se não houver correspondências, explicar se a causa é filtro restrito, falta de dados ou indisponibilidade da fonte. Não apresentar oportunidades inventadas ou dados demonstrativos como reais.

### 6.2 Descoberta

Abrir “Para minha empresa”, entender o motivo de indicação, consultar a ficha, abrir a fonte e acompanhar ou dispensar. “Não é relevante” deve permitir indicar produto errado, localização, prazo ou outro motivo. A correção afeta o perfil daquela organização; não altera automaticamente a classificação global.

### 6.3 Monitoramento

Ao acompanhar, registrar a versão atual. Uma mudança futura gera evento comparável, aparece na plataforma e entra no canal configurado. O primeiro carregamento de uma licitação antiga não deve produzir falsos alertas de retificação.

### 6.4 Rotina pelo e-mail

Resumo com seleção e motivo → clique na ficha → autenticação, se necessária, preservando o destino → acompanhar ou dispensar. Links de preferências não devem exigir uma sequência longa de telas.

### 6.5 Encerramento da assinatura

Cliente solicita cancelamento → visualiza data final de acesso → confirmação registrada → acesso até o fim do período pago → interrupção de novos alertas na expiração. Manter acesso às configurações de conta e cobrança. Excluir a conta é uma operação distinta de cancelar a assinatura.

## 7. Requisitos funcionais e critérios de aceite

| ID | Requisito | Aceite mínimo | Versão |
| --- | --- | --- | --- |
| RF01 | Empresa e interesses | Salvar produtos, região e exclusões; prévia coerente | V1 |
| RF02 | Pesquisa | Filtros combináveis, paginação, URL reproduzível e resultados sem duplicação visual | V1 |
| RF03 | Recomendação explicável | Cada recomendação informa os sinais usados; exclusões são respeitadas | V1 |
| RF04 | Ficha | Campos ausentes explícitos, fonte clicável e última consulta visível | V1 |
| RF05 | Acompanhamento | Salvar e remover; não misturar favoritos entre empresas | V1 |
| RF06 | Alterações | Mesmo processo mantém identidade e exibe antes/depois | V1 |
| RF07 | E-mails | Respeitar frequência, preferências, supressão e deduplicação | V1 |
| RF08 | Cobrança | Pagamento confirmado libera acesso; reenvio de evento não duplica efeitos | V1 |
| RF09 | Administração | Revisar registro e reprocessar execução com trilha de auditoria | V1 |
| RF10 | Cobertura | Exibir fontes, municípios, limitações e estado da atualização | V1 |
| RF11 | Itens | Resultado aponta item correspondente e sua origem; ausência não vira inexistência | V1.1 |
| RF12 | Equipe | Convites expiram; permissões aplicadas no backend | V2 |
| RF13 | Exportação | Exportar filtros atuais, respeitar limite e registrar geração | V1.1 |
| RF14 | Atendimento | Cliente relata erro a partir da ficha com referência do registro | V1 |

## 8. Telas e navegação

Navegação principal: **Para minha empresa • Explorar • Acompanhadas • Alertas • Configurações**. Itens e calendário entram na V1.1; Equipe entra na V2. Administração fica separada.

| Tela / rota proposta | Conteúdo e ações | Estados indispensáveis |
| --- | --- | --- |
| Início público `/` | Benefício, exemplos identificados, cobertura e chamada para teste | Sem números comerciais fictícios |
| Planos `/planos` | Preços, limites, recursos disponíveis e cancelamento | Não vender recurso em desenvolvimento |
| Cobertura `/cobertura` | Fontes e municípios homologados, periodicidade e falhas | Parcial, atrasado, indisponível |
| Cadastro e login `/entrar` | Autenticação, confirmação e recuperação | Link expirado, credencial inválida |
| Configuração `/configurar` | Empresa, produtos, região, exclusões e prévia | Sem resultados; salvar e continuar depois |
| Para minha empresa `/app` | Seleção, motivos, novidades e prazos das acompanhadas | Sem novidades; fonte desatualizada |
| Explorar `/app/oportunidades` | Pesquisa, filtros, lista/tabela e busca salva | Carregando, vazio, erro e paginação |
| Ficha `/app/oportunidades/:id` | Resumo, objeto, itens, documentos, mudanças e fonte | Prazo ausente, documento indisponível |
| Acompanhadas `/app/acompanhadas` | Favoritos, prazo, status e última mudança | Limite do plano atingido sem apagar dados |
| Alertas `/app/alertas` | Eventos, lidos/não lidos e preferências | Entrega de e-mail falhou |
| Interesses `/app/interesses` | Perfis e buscas salvas com prévia | Filtro excessivamente restrito |
| Conta `/app/configuracoes` | Empresa, e-mail, segurança e dados | Alteração pendente de verificação |
| Assinatura `/app/assinatura` | Plano, período, cobranças e cancelamento | Teste, pendente, ativa, atraso, expirada |
| Ajuda `/app/ajuda` | Guia curto, dúvidas e contato | Ticket vinculado à oportunidade |
| Calendário `/app/calendario` | Prazos das acompanhadas; link para a ficha | Horário desconhecido claramente marcado |
| Equipe `/app/equipe` | Membros, convites e funções | Convite expirado e acesso revogado |
| Operação `/admin` | Execuções, revisão, entregas e clientes | Reprocessamento, incidentes e auditoria |

### 8.1 Composição da ficha

No topo: título descritivo, órgão, situação, município, prazo e botões “Acompanhar” e “Ver na fonte”. Em seguida, motivo da recomendação e resumo factual. Abaixo: objeto original, valor e sua natureza, entrega/execução, plataforma de disputa, itens, documentos e linha do tempo.

Separar “local do órgão” de “local de entrega”. Identificar valor total, por item, estimado ou sigiloso. Se houver participação por item/lote, mostrar apenas quando sustentada pelos dados ou documento. Um item correspondente não comprova que ele pode ser disputado isoladamente.

### 8.2 Direção de interface

Interface de trabalho, com tipografia legível, boa densidade e filtros persistentes. A página inicial deve mostrar oportunidades e ações, não uma coleção de gráficos decorativos. Usar cores com rótulos textuais; teclado funcional; foco visível; datas completas; contraste e leitura em celular. Projetar para desktop, mas garantir o fluxo completo no navegador móvel.

## 9. Planos de assinatura propostos

**Todos os preços abaixo são hipóteses próprias para teste, não resultado de pesquisa de disposição a pagar.** O valor deve ser revisto após medir uso, retenção e custo de suporte. Não presumir que preço menor supera concorrentes gratuitos.

| Recurso | Essencial | Profissional | Equipe |
| --- | --- | --- | --- |
| Mensal proposto | R$ 79 | R$ 149 | R$ 299 |
| Anual futuro, pagamento único | R$ 790 | R$ 1.490 | R$ 2.990 |
| Equivalente mensal anual | R$ 65,83 | R$ 124,17 | R$ 249,17 |
| Organizações / empresas | 1 | 1 | 1 |
| Usuários incluídos | 1 | 1 | 5 |
| Perfis de interesse ativos | 2 | 10 | 25 compartilhados |
| Buscas salvas | 5 | 20 | 50 compartilhadas |
| Acompanhamentos ativos | 50 | 200 | 500 compartilhados |
| Pesquisa na cobertura homologada | Sim | Sim | Sim |
| Ficha completa, fonte e atualização | Sim | Sim | Sim |
| Motivos de correspondência | Sim | Sim | Sim |
| Histórico coletado e mudanças críticas | Sim | Sim | Sim |
| Resumo de novas oportunidades | Diário ou semanal | Até 2 por dia | Até 2 por dia por membro inscrito |
| Alterações críticas nas acompanhadas | Após detecção e processamento | Após detecção e processamento | Após detecção e processamento |
| Busca dedicada em itens | Não | Sim, quando disponível | Sim, quando disponível |
| Calendário de acompanhadas | Não | Sim | Sim |
| Exportação CSV/XLSX | Não | Até 5 mil linhas/mês | Até 20 mil linhas/mês |
| Notas, responsáveis e etapas compartilhadas | Não | Não | Sim |
| Atendimento | E-mail, até 2 dias úteis como meta | E-mail, até 1 dia útil como meta | E-mail, até 1 dia útil como meta |
| Configuração assistida | Uma revisão inicial do perfil | Uma sessão inicial de até 30 min | Uma sessão inicial de até 45 min |
| Disponibilidade planejada | V1 | V1.1 | V2 |

**Regras dos limites:** acompanhamento ativo é um registro sob monitoramento escolhido pelo cliente. Arquivados ficam consultáveis sem consumir esse limite. Perfis são conjuntos de produtos, regiões e exclusões; buscas salvas guardam filtros de pesquisa. No Equipe, cotas são por organização, não multiplicadas pelo número de membros. Cada pessoa recebe no próprio endereço verificado; não cadastrar listas externas de destinatários.

Todos os planos usam a mesma qualidade e atualidade de dados. Não reter alertas de suspensão ou prazo para induzir upgrade. O plano limita a quantidade de acompanhamentos e ferramentas, não a correção das informações. Se uma ficha possui itens disponíveis, não esconder a informação factual; a diferenciação paga está na busca estruturada por itens.

### 9.1 Estratégia de lançamento

- Piloto: 3–5 empresas, proposta experimental de R$ 49 por 30 dias, entrega delimitada e acompanhamento próximo. Não renovar automaticamente sem contratação clara.
- V1: vender apenas Essencial, a R$ 79/mês como hipótese inicial.
- Teste público: 7 dias sem cartão, limites do Essencial, e-mail verificado. Ajustar duração se o volume local for insuficiente para avaliar valor nesse período.
- Não oferecer plano gratuito permanente inicialmente: já existe oferta gratuita concorrente, e o produto precisa provar valor pago sem ampliar suporte indiscriminadamente.
- Liberar Profissional e Equipe somente quando seus recursos estiverem funcionando e testados.
- Anual: habilitar após observar renovação mensal e validar cancelamento/reembolso; desconto proposto equivalente a dois meses sobre doze mensalidades.
- IA e assessoria multiempresa não estão incluídas nesses preços; eventual oferta exige medição de custo e escopo próprios.

### 9.2 Cobrança e acesso

Estados internos: `trialing`, `pending`, `active`, `past_due`, `canceled` com acesso até `access_until`, e `expired`. Separar estado do contrato de confirmação financeira: assinatura criada não equivale a pagamento recebido.

Política proposta: atraso mantém 3 dias de tolerância; depois interrompe novos alertas e acesso premium, preservando conta e cobrança. Cancelamento voluntário mantém acesso até o fim do período pago. Reembolso ou contestação exige tratamento específico e revisão da vigência, sem usar apenas a data da assinatura.

Na V1 vender somente mensal, sem prorrateio. Na expansão, upgrade/downgrade passa a valer no próximo ciclo inicialmente. Downgrade não apaga favoritos, perfis ou exportações anteriores: solicitar seleção do que ficará ativo, conservar o restante arquivado e comunicar a data de aplicação.

## 10. Fontes, cobertura e qualidade

### 10.1 Ordem de integração

| Fonte | Papel | Condição para integrar |
| --- | --- | --- |
| PNCP | Primeira fonte estruturada | Validar endpoints, paginação, campos, modalidades e limites |
| Portal de Compras de Goiás | Complemento estadual | Comprovar informação útil ausente ou atualização mais completa |
| TCM-GO | Fonte candidata para complemento/verificação | Avaliar dados efetivamente disponíveis e método permitido |
| Portais/diários municipais | Avisos e documentos locais | Priorizar municípios e lacunas demonstradas |

Preferir APIs e dados estruturados. Playwright só quando necessário e permitido; não depender de contornar CAPTCHA ou bloqueios. Os serviços de consulta e de publicação/manutenção do PNCP têm finalidades diferentes; este produto começa consumindo consultas, sem credenciais de publicação [S3].

### 10.2 Processo de ingestão

Agendador cria execução → coletor busca páginas → snapshot bruto é persistido → normalização → resolução de identidade → atualização da versão → classificação e índice → eventos de mudança → seleção por cliente → fila de notificação.

Usar janelas sobrepostas e checkpoints por fonte/município/modalidade. Não concluir a sincronização se uma página falhar. Após retomar, reprocessar com segurança, sem duplicar oportunidades ou alertas. Além de coletar novas publicações, revisitar as acompanhadas: alterações podem não aparecer em uma busca por data de publicação original.

Cadência inicial proposta: varredura de novas publicações a cada 6 horas; acompanhadas a cada 2 horas, se suportado; reconciliação diária de uma janela recente de 30 dias e revisão semanal mais ampla. São parâmetros operacionais a calibrar, não garantias de atualização da fonte. Distribuir consultas entre clientes: a mesma licitação é consultada uma vez por ciclo, não uma vez por assinante.

### 10.3 Identidade e proveniência

Priorizar `source + external_id`; manter UUID interno. Para fontes sem ID estável, combinar órgão, processo, ano e unidade com revisão de ambiguidades. Usar hash de conteúdo para detectar mudanças. Preservar registros de fontes distintas e criar vínculos quando houver evidência suficiente de que representam o mesmo processo.

Guardar, por campo relevante, origem e instante observado. Divergências de prazo ou situação vão para revisão; não escolher silenciosamente a informação mais conveniente. Snapshot bruto em JSON válido, documento com checksum e endereço original. Conservar o que foi visto para explicar alertas e reprocessar regras.

### 10.4 Campos de domínio

Identidade; órgão e unidade; município/UF do órgão; local de execução; objeto original; título de apresentação; modalidade; situação oficial; estado derivado; publicação; abertura e encerramento com horário/fuso quando informados; valor e tipo; processo; itens/lotes; documentos; fonte e plataforma de disputa; primeira observação; última consulta bem-sucedida; última alteração.

Não derivar “aberta” apenas de situação “divulgada”. Combinar evidências de prazo e situação, mantendo “prazo desconhecido” quando necessário. Conservar timestamp original, precisão e timezone conhecido; não inventar meia-noite como horário oficial. Identificadores como CNPJ devem ser strings e sua validação deve acompanhar o padrão oficial vigente.

## 11. Busca, classificação e relevância

V1: pesquisa textual no objeto, termos positivos/negativos, municípios e categorias; ordenar por relevância, publicação ou encerramento. Padrão “Para minha empresa”: compatibilidade primeiro, desempate por prazo utilizável e atualidade. Em “Explorar”, usuário escolhe livremente a ordenação.

Não restringir permanentemente resultados ao CNAE. Ele pode ajudar na configuração futura, mas o catálogo de produtos e serviços informado pela empresa é mais preciso para o uso proposto.

Motor inicial sugerido:

1. Aplicar exclusões fortes e recorte geográfico escolhido.
2. Identificar termos com limites de palavra, sinônimos e contexto.
3. Priorizar correspondência em objeto/itens; não usar qualquer palavra do JSON bruto.
4. Gerar motivos determinísticos, como “notebook no objeto” e “município selecionado”.
5. Classificar como correspondência forte ou possível; evitar porcentagens sem calibração.
6. Registrar versão da regra e feedback de relevância.

Se o local de entrega for desconhecido, explicar que o filtro usou a localização do órgão. Não interpretar ausência de item como prova de que o produto não está no edital.

Manter amostra rotulada de pelo menos 100 oportunidades para a primeira avaliação, com positivos e negativos. Comparar precisão dos primeiros resultados e perdas de oportunidades relevantes na amostra. Não alegar recall de todo o mercado sem conhecer todas as publicações.

## 12. E-mail como parte do produto

Categorias separadas: acesso e segurança; cobrança; resumo de oportunidades; mudanças nas acompanhadas; lembretes de prazo. Marketing deve ser tratado separadamente das comunicações do serviço.

Resumo inicial: até 10 oportunidades, cada uma com título, motivo, órgão/local, prazo, valor quando disponível e link. Acima disso, mostrar contagem e botão para ver o restante. Deduplicar entre perfis da mesma empresa e destinatário. Não reenviar oportunidade inalterada como novidade.

Horário padrão proposto: 7h30 em `America/Sao_Paulo`; segunda edição do Profissional às 16h30. Usuário pode preferir semanal. Se não houver novidades, não enviar resumo vazio. Alterações críticas são processadas após a detecção, respeitando a infraestrutura e as preferências; não chamar isso de atualização em tempo real.

Lembretes iniciais: 48h e 24h antes do encerramento quando o prazo for conhecido e a oportunidade ainda estiver elegível. Recalcular e invalidar lembretes antigos após retificação. Se a coleta está atrasada, informar a data da última verificação em vez de sugerir confirmação recente.

### 12.1 Confiabilidade de entrega

- Outbox persistente; job de envio separado da requisição web.
- Chave única por destinatário, evento/versão e tipo de comunicação.
- Idempotência no banco e no provedor. A proteção de idempotência do Resend tem janela de 24 horas; não substitui o histórico interno permanente de envio [S8].
- Tentativas com espera progressiva; após limite, fila de falhas para operação.
- Registrar aceito, entregue, rejeitado, reclamação e cancelamento quando informados pelo provedor. “Aceito” não significa entregue na caixa de entrada.
- SPF, DKIM e DMARC configurados; subdomínio para envio; reputação monitorada.
- Suprimir destinos com hard bounce ou reclamação. Descadastro de alertas não deve exigir login.
- Não enviar todos os clientes em cópia nem permitir destinatários não verificados.
- Registrar versão das preferências e conferir novamente antes de enviar.

Métricas: entregas, rejeições, cliques e ações após o clique. Abertura é sinal auxiliar, sujeito a bloqueios e pré-carregamentos; não é prova de leitura.

## 13. Arquitetura técnica recomendada

**Monólito modular com processos separados para web, API e worker.** Manter um domínio Python compartilhado por API e processamento. Evitar microserviços e reescrita dos coletores em outra linguagem nesta etapa.

| Camada | Escolha inicial | Motivo e responsabilidade |
| --- | --- | --- |
| Frontend | Next.js, React e TypeScript | Aproveitar experiência; páginas públicas e área autenticada [S4] |
| Interface | Tailwind CSS e componentes acessíveis revisados | Consistência visual com componentes reaproveitáveis |
| API | FastAPI e Pydantic | Expor domínio Python com contratos explícitos [S5] |
| Persistência | PostgreSQL, SQLAlchemy e Alembic | Relacionamentos, migrações e histórico |
| Autenticação | Supabase Auth | Evitar implementação própria de senhas e recuperação |
| Banco gerenciado | PostgreSQL do Supabase | Operação inicial simplificada; conexões e limites a validar |
| Busca | Full-text do PostgreSQL, índices e normalização | Começar sem mecanismo externo de busca [S7] |
| Tarefas | Celery, Redis e um agendador único | Coleta, reprocessamento e e-mails fora da requisição [S6] |
| Objetos | Bucket privado para snapshots e arquivos | Separar documentos e payloads do banco transacional |
| E-mail | Provedor ainda não escolhido; Resend é candidato | Comparar entrega, limites, eventos, supressão, custo e saída durante a Fase 4 [S8] |
| Cobrança | Asaas com checkout hospedado | Assinaturas e integração local; validar fluxo no sandbox [S9] |
| Testes | pytest, testes de componentes e Playwright E2E | Cobrir regras e jornadas críticas |
| Operação | Docker, GitHub Actions, logs estruturados e rastreamento de erros | Reprodutibilidade, CI e diagnóstico |

Selecionar versões estáveis compatíveis no início, fixar dependências e manter arquivos de lock. O plano não exige uma versão específica de framework ainda não testada em conjunto.

### 13.1 Limites entre camadas

Frontend renderiza e interage; FastAPI é a autoridade para regras, planos e autorização. Supabase Auth autentica; não determina por si só quem pode ler os dados de uma organização. API valida JWT, associação e permissão em toda operação privada. Não duplicar as mesmas regras em rotas do Next.js e FastAPI.

Banco de domínio acessado pelo backend. Desabilitar exposição desnecessária via APIs públicas do banco. Para tabelas expostas, configurar e testar RLS. Papéis privilegiados podem contornar políticas: não confiar em RLS para corrigir consultas feitas com credenciais administrativas; nunca enviar chaves de serviço ao navegador [S10].

API e worker podem compartilhar imagem Python, mas usar credenciais e permissões distintas. Redis transporta tarefas; estado durável, eventos e controle de envio ficam no PostgreSQL. Não usar apenas tarefas em memória ou `BackgroundTasks` para trabalhos que precisam sobreviver a reinícios.

### 13.2 Hospedagem

Piloto: aplicação web, API, worker e Redis em serviços com contêineres; banco gerenciado e armazenamento externo. Uma VPS pode reduzir custo nominal, mas transfere responsabilidade por atualizações, rede e restauração ao operador. Escolher o provedor após comparar custo completo e disponibilidade na região; não contratar múltiplas plataformas sem necessidade.

Ambientes separados: local, homologação e produção. Nunca compartilhar banco ou credenciais de cobrança entre homologação e produção. Checkout e webhooks testados no sandbox antes de qualquer transação real.

## 14. Modelo de dados

| Grupo | Entidades propostas | Regras |
| --- | --- | --- |
| Identidade | users, organizations, memberships, invitations | Organização representa a empresa cliente |
| Interesses | interest_profiles, profile_terms, saved_searches | Sempre vinculados à organização |
| Dados públicos | sources, agencies, opportunities, source_records | Registro público compartilhado, sem duplicar por cliente |
| Histórico | opportunity_versions, change_events | Versões imutáveis; comparação reproduzível |
| Itens e arquivos | opportunity_items, lots, documents, extractions | Documento e extração têm versão e origem |
| Uso privado | follows, feedback, notes, assignments | tenant obrigatório; acesso por associação |
| Comunicação | notification_preferences, outbox, email_deliveries, suppressions | Unicidade por evento e destinatário |
| Comercial | plan_versions, entitlements, subscriptions, payments, webhook_events | Plano versionado e evento idempotente |
| Operação | collection_runs, checkpoints, review_queue, audit_events | Status parcial explícito e rastreio |

Campos comuns: UUID, timestamps de criação/atualização e índices necessários. Usar tipo decimal para valores monetários; moeda explícita. Documento deve guardar URL, hash, tamanho, tipo e instante de obtenção. Correções manuais não apagam o valor bruto: registrar override, autor, motivo e regra de conciliação com a próxima coleta.

Usuário pode pertencer a mais de uma organização por convite futuro, mas cada operação resolve o contexto ativo e valida associação. Uma requisição não pode escolher livremente um `organization_id` para acessar dados alheios.

## 15. Contratos de API e estrutura do repositório

Rotas iniciais propostas:

| Grupo | Exemplos | Regra |
| --- | --- | --- |
| Conta | `GET /v1/me`, `GET/PATCH /v1/organization` | Identidade e vínculo validados |
| Oportunidades | `GET /v1/opportunities`, `GET /v1/opportunities/{id}` | Paginação e filtros documentados |
| Histórico | `GET /v1/opportunities/{id}/changes` | Informar início da observação |
| Interesses | `/v1/interest-profiles`, `/v1/saved-searches` | Limite do plano no servidor |
| Acompanhamento | `/v1/follows`, `/v1/feedback` | Idempotência e escopo privado |
| Alertas | `/v1/notifications`, `/v1/preferences` | Preferência por destinatário |
| Cobrança | `/v1/billing/checkout`, `/v1/billing/subscription` | Sem aceitar preço enviado pelo cliente |
| Eventos externos | `/v1/webhooks/billing`, `/v1/webhooks/email` | Autenticidade, persistência e deduplicação |
| Operação | `/v1/admin/collection-runs`, `/v1/admin/reviews` | Papel de operação separado |

Contrato OpenAPI para gerar tipos do frontend. Limitar tamanho de página, filtros e exportações. Consultas devem ter índices e plano de execução avaliado com dados representativos.

Estrutura proposta sem mover tudo no primeiro commit:

- `src/licitagoias/domain/`: entidades, regras e eventos.
- `src/licitagoias/collectors/`: adaptadores de fonte existentes e novos.
- `src/licitagoias/services/`: ingestão, matching, alertas e acesso.
- `src/licitagoias/repositories/`: persistência e transações.
- `src/licitagoias/api/`: endpoints e dependências de autenticação.
- `src/licitagoias/workers/`: tarefas e agendamento.
- `web/`: aplicação Next.js.
- `migrations/`, `tests/`, `docs/`, `infra/`: migrações, verificação, decisões e implantação.

Preservar CLI e testes existentes durante a migração; adaptar fluxos para chamar os mesmos serviços usados pela API. Não criar dois motores divergentes de curadoria.

## 16. Integração financeira e permissões

Asaas é a escolha inicial a validar, não um compromisso de contratação. Sua documentação oferece assinaturas e eventos de webhook [S9]. Confirmar meios de pagamento elegíveis ao fluxo escolhido: cobrança periódica por Pix/boleto não deve ser apresentada automaticamente como débito recorrente autorizado.

1. Backend resolve versão do plano e cria checkout no provedor.
2. Retorno do navegador mostra pagamento pendente até confirmação confiável.
3. Webhook autenticado é persistido com ID único e recebe resposta rápida.
4. Worker aplica transição idempotente e atualiza vigência/permissões.
5. Rotina de reconciliação consulta divergências e recupera eventos perdidos.

Tratar eventos repetidos, atrasados e fora de ordem. Não reativar assinatura cancelada por um evento antigo sem conferir a situação atual. Asaas documenta entrega de webhook pelo modelo “ao menos uma vez”, exigindo deduplicação [S9].

Não armazenar dados brutos de cartão. Separar recibo do provedor e emissão fiscal da empresa; definir o fluxo fiscal com o contador antes do lançamento.

Papéis V2: proprietário administra assinatura, empresa e membros; administrador gerencia perfis e equipe; analista pesquisa e acompanha; leitor apenas consulta. Administrador interno do LicitaGoias é outro papel, com auditoria e acesso mínimo necessário.

## 17. Segurança, privacidade e operação

Medidas de engenharia propostas: HTTPS; segredos fora do repositório; MFA para operação administrativa; limites de requisição; validação de entrada; autorização de cada objeto; auditoria; backups e teste de restauração. O guia da ANPD para pequenos agentes é referência de preparação, não substitui a definição das obrigações aplicáveis ao negócio [S11].

- Separar dados públicos da licitação de e-mails, preferências e histórico privado dos clientes.
- Avisos de privacidade, termos e cobertura devem refletir a operação real. Definir finalidade, base aplicável, fornecedores e atendimento a solicitações antes do lançamento.
- Proposta operacional de retenção: logs de operação por 90 dias; dados privados após cancelamento por até 90 dias para recuperação, sujeitos à política final e às obrigações aplicáveis; registros financeiros conforme orientação contábil/jurídica. Não apresentar esses prazos propostos como exigências legais.
- Definir expurgo de backups e documentos; excluir conta não significa apagar registros sujeitos a retenção obrigatória.
- Downloads externos: limitar tamanho, tempo e tipos; bloquear endereços internos e redirecionamentos perigosos; processar PDFs em ambiente restrito. Servir conteúdo não confiável sem execução de scripts.
- Conferir termos e métodos permitidos de acesso às fontes antes de cada coletor.
- Não adicionar dados de clientes a prompts ou registros de diagnóstico sem necessidade.

### 17.1 Objetivos operacionais internos

Disponibilidade-alvo inicial da aplicação: 99,5% ao mês, sem oferecer SLA contratual antes de medir. Coleta e aplicação têm indicadores separados. Busca: p95 abaixo de 1,5 s na API em uma carga de homologação definida, por exemplo 100 mil registros e 20 usuários simultâneos. São metas de teste, não desempenho já observado.

Backups diários com meta inicial RPO de 24h e RTO de 8h, condicionados ao serviço contratado e a ensaio real de restauração. Antes de operações pagas, documentar como reconstruir cobrança por reconciliação e recuperar outbox. Evoluir para recuperação pontual se perda de 24h se tornar inaceitável.

Rotina: verificar diariamente falhas de coleta, e-mail e cobrança; semanalmente revisar amostra de relevância e divergências; mensalmente restaurar backup em ambiente isolado e revisar custos.

## 18. Uso futuro de IA e extração de documentos

Primeiro coletar itens estruturados. Depois, extrair texto de PDFs digitais; OCR somente quando necessário. IA entra após existir corpus de avaliação e necessidade comprovada.

Aplicações possíveis: título legível; resumo factual; identificação de produtos; extração de prazos, local de entrega e documentos solicitados. Cada afirmação deve apontar documento, versão e página/trecho. Campo não localizado permanece desconhecido. O sistema não deve emitir conclusão automática de habilitação.

Tratar o edital como conteúdo não confiável: instruções contidas nele não comandam ferramentas. Usar esquema estruturado, validação de tipos e comparação de valores/datas com a fonte. Cache por hash do documento e versão do extrator, limites de páginas e orçamento por tarefa. Uma extração compartilhada é reutilizada por todos os clientes autorizados a ver a informação pública.

Não incluir análise ilimitada em um plano de baixo preço. Definir cobrança ou cota somente depois de medir custo por documento, taxa de erro e utilidade.

## 19. Estratégia de testes e aceite de lançamento

| Camada | Casos relevantes |
| --- | --- |
| Coleta | Mais de duas páginas, 429, timeout, resposta vazia, JSON inesperado, retomada e parcial |
| Identidade | Prazo muda sem novo processo; processos semelhantes permanecem distintos |
| Datas | Horário e fuso, ausência, alteração e cancelamento de lembretes |
| Relevância | Termos negativos, sinônimos, falsos positivos e itens não disponíveis |
| Isolamento | Cliente A não lê/edita favoritos, perfis, exportações ou notas de B |
| Assinatura | Pendente não libera; repetição não duplica; cancelamento, atraso e reconciliação |
| E-mail | Reexecução após 24h, falha parcial, supressão e mudança de preferência |
| E2E | Cadastro → perfil → pesquisa → acompanhar → alerta → cobrança → cancelamento |
| Operação | Deploy, migração compatível, restauração e recuperação de worker |

Executar testes de integração com amostras versionadas da fonte; validação ao vivo controlada, sem depender da disponibilidade externa em todo teste de CI. Bloqueios de lançamento: vazamento entre clientes, prazo falso, cobrança/acesso inconsistente, alerta duplicado recorrente ou coleta silenciosamente incompleta.

Checklist de go-live: fontes homologadas; cobertura publicada; 14 dias de operação monitorada; entrega nos provedores de e-mail usados pelos pilotos; restauração demonstrada; cancelamento funcional; autenticação de webhooks; termos e atendimento definidos; painel de falhas; pelo menos três clientes piloto com feedback registrado.

## 20. Fases de desenvolvimento e esforço

Estimativas próprias para uma pessoa, incluindo implementação e verificação. Horas não pressupõem aceleração garantida por IA. Integrações novas e retrabalho de produto podem ampliar a faixa.

| Fase | Entregas | Dependências | Esforço estimado | Saída verificável |
| --- | --- | --- | --- | --- |
| 0 — Validação e recorte | Entrevistas, amostra, segmento, cobertura e piloto | Nenhuma | 20–30 h | Problema e entrega definidos com 3–5 empresas |
| 1 — Dados confiáveis | PostgreSQL, identidade, histórico, paginação e logs | F0 | 60–90 h | Reexecução consistente e alterações preservadas |
| 2 — Fundação SaaS | API, autenticação, organização, CI e ambientes | F1 | 45–65 h | Usuários isolados e implantação repetível |
| 3 — Experiência principal | Login de desenvolvimento, perfil de interesse, busca, ficha, acompanhamento e feedback | F2; aceite de dados da F1 | 65–95 h | Jornada web completa com oportunidades reais e isolamento provado |
| 4 — Monitoramento e e-mail | Eventos, outbox, preferências, resumo e falhas | F1–F3 | 45–65 h | Entregas rastreáveis e reexecução sem duplicação |
| 5 — Comercial e administração | Checkout, assinatura, cancelamento, revisão e suporte | F2–F4 | 45–65 h | Ciclo comercial funcional no sandbox |
| 6 — Piloto e lançamento | Ajustes, testes críticos, restauração e operação | F3–F5 | 40–60 h | Aceite de V1 e primeiros ciclos acompanhados |
| 7 — Profissional | Itens estruturados, calendário e exportação | V1 validada | 50–80 h | Benefício adicional confirmado |
| 8 — Equipe | Membros, papéis, responsáveis e notas | V1 + demanda | 45–70 h | Colaboração com permissões testadas |

Fases 0–6: **320–470 horas**, antes de reserva. Com 20% de contingência: **384–564 horas**. A 20h semanais: aproximadamente **19–28 semanas**; a 30h: **13–19 semanas**; a 10h: **38–56 semanas**. Espera por clientes, DNS, aprovação de contas e período de observação pode ampliar o calendário. O piloto manual pode começar muito antes da V1 completa.

Fases 7–8 acrescentam 95–150 horas antes de contingência. OCR, IA, novos portais e assessoria multiempresa não estão nessas estimativas; precisam de investigação própria.

### 20.1 Definição executável da Fase 1 — Dados confiáveis

**Objetivo:** transformar a coleta PNCP existente em um fluxo persistente, retomável e auditável para a cobertura escolhida na Fase 0. Ao final, uma nova coleta não cria outra oportunidade para o mesmo processo, uma retificação atualiza a oportunidade existente e uma falha fica visível como parcial ou malsucedida. Esta fase prepara a base de dados; não entrega ainda a aplicação SaaS.

**Entrada:** decisões da Fase 0 registradas: segmento usado para avaliar os dados, municípios e modalidades pretendidos, amostra de referência, campos essenciais e limites de cobertura. Se essas escolhas não estiverem fechadas, executar apenas o baseline e a investigação; não declarar homologada a cobertura.

**Verificação em 15/10/2026:** duas coletas PNCP reais de Aparecida de Goiânia (5201405), modalidades 6/8/9/5, janela 01–15/10 terminaram `complete`. A repetição manteve 25 oportunidades, IDs externos, versões e snapshots sem duplicação. Testes locais cobriram retificação lógica e paginação multipágina simulada. F1 permanece parcial: a cobertura da Fase 0 não foi formalmente aceita, a execução ao vivo teve apenas uma página por segmento e não houve retificação real ou falha/retomada observada.

| Etapa | Trabalho | Evidência de conclusão |
| --- | --- | --- |
| F1.1 — Baseline e contrato de dados | Registrar comportamento dos fluxos atuais; mapear respostas PNCP usadas; definir identidade, datas, valores, campos ausentes e proveniência | Amostras versionadas e decisões de domínio documentadas; falhas e lacunas conhecidas listadas |
| F1.2 — Persistência e migração | Adicionar PostgreSQL e migrações reproduzíveis; separar fonte/identidade externa, oportunidade atual, execuções de coleta, snapshots e versões observadas | Banco novo pode ser criado do zero; dados legados úteis podem ser importados sem sobrescrever ou perder o original |
| F1.3 — Coleta completa e retomável | Implementar paginação sequencial e configurável; registrar páginas consultadas, checkpoints, tentativas e resultado por consulta; propagar erro e resposta inválida como falha, nunca como lista vazia | Execução multipágina termina completa ou declara parcial/falha; retomada não duplica registros; 429 e timeout têm retentativa limitada e registrada |
| F1.4 — Identidade, normalização e versões | Preferir `fonte + identificador oficial`; usar identificador substituto documentado quando ausente; manter snapshot bruto válido, valores normalizados e hash de conteúdo; criar versão apenas quando os campos acompanhados mudarem | Duas coletas iguais não criam nova versão; mudança de prazo/status mantém a mesma identidade e cria uma versão comparável; processos distintos semelhantes permanecem distintos |
| F1.5 — Estados e operação | Preservar suspensões, cancelamentos e retificações no histórico; separar status oficial do estado derivado; disponibilizar consulta administrativa simples de execuções e registros com erro para diagnóstico/reprocessamento | Operador distingue execução vazia completa, parcial, falha e sucesso; histórico não apaga estados encerrados; reprocessamento é rastreável |

**Decisões de domínio obrigatórias:** identificador oficial PNCP quando presente, com UUID interno próprio; publicação, abertura e encerramento em campos separados; ausência de prazo permanece ausente; horários e fusos são preservados como recebidos, sem inventar horário; valor mantém natureza e precisão; JSON bruto fica associado à fonte e ao instante de observação. Hash de conteúdo serve para detectar mudanças, não como identidade do processo. Uma identidade sem identificador oficial deve guardar o método e os componentes usados e ser sinalizada para revisão quando ambígua.

**Transição SQLite → PostgreSQL:** manter um caminho de migração repetível e uma cópia de segurança do arquivo original. Importar registros com contagem antes/depois e relatório de conflitos; não inferir identidade nova a partir do hash antigo quando isso puder fundir processos. A operação nova deve gravar no PostgreSQL; SQLite permanece somente como entrada legada/arquivo até a reconciliação ser aprovada. A migração não apaga nem altera silenciosamente a base de origem.

**Critérios de aceite da fase:**

1. Uma instalação vazia cria o esquema por migrações e importa a amostra legada com totais reconciliados.
2. Uma coleta real controlada percorre todas as páginas declaradas para o recorte aprovado; cada consulta registra parâmetros não sensíveis, horários, páginas, contagens e estado final.
3. Timeout, limite de requisição, erro HTTP, JSON inválido e falha em página intermediária não são apresentados como coleta completa nem como ausência de oportunidades.
4. Reexecutar a mesma amostra não duplica processos, snapshots idênticos não geram versões novas e uma alteração de prazo ou situação produz comparação antes/depois na mesma oportunidade.
5. Dois processos com objeto e valor semelhantes continuam separados quando seus identificadores oficiais diferem.
6. Datas desconhecidas permanecem desconhecidas; a publicação não preenche encerramento; suspensões e cancelamentos continuam consultáveis no histórico.
7. Há logs estruturados suficientes para identificar fonte, recorte, execução, página e erro, sem depender do JSON inteiro impresso no log.
8. Os casos acima passam com amostras locais versionadas, sem depender de disponibilidade do PNCP no CI; uma checagem ao vivo é feita separadamente e registrada.

**Fora do escopo:** autenticação e organizações, API para o produto, interface web, perfis de interesse, recomendação, busca para clientes, e-mails, cobrança, novos portais, extração de itens/PDF e agendamento de produção. Nesta fase, a operação pode ser acionada pela CLI ou por comando administrativo controlado; o agendador contínuo e as notificações entram depois.

**Sequência e dependências:** concluir F1.1 antes de fechar o esquema; F1.2 e F1.3 podem avançar em paralelo após o contrato da coleta estar definido; F1.4 depende da identidade e persistência; F1.5 e o aceite integrado dependem de todas as anteriores. Problemas de cobertura encontrados devem voltar à decisão da Fase 0, sem ampliar automaticamente o escopo para outras fontes.

**Estimativa de referência:** 60–90 horas, conforme a fase 1 da tabela, incluindo implementação e verificação dos critérios acima. A faixa assume um único adaptador PNCP e um recorte já escolhido na Fase 0; mudanças no contrato da fonte, múltiplas fontes ou revisão manual extensa exigem reestimativa. A Fase 1 termina quando os critérios de aceite forem demonstrados e as lacunas de cobertura estiverem documentadas, não quando o painel SaaS estiver pronto.

### Primeiras duas semanas, considerando 20h/semana

Semana 1: revisar repositório e rodar testes existentes; selecionar amostra real; conversar com fornecedores; fechar segmento/cobertura; registrar lacunas e criar backlog priorizado.

Semana 2: introduzir identificador oficial e datas corretas; estruturar esquema PostgreSQL; salvar snapshots/execuções; começar paginação e reprocessamento. Ao fim, demonstrar que uma retificação atualiza o mesmo processo. Não prometer interface e cobrança completas nesse intervalo.

### 20.2 Definição executável da Fase 2 — Fundação SaaS

**Objetivo:** entregar uma API implantável que autentica usuários pelo Supabase Auth e aplica autorização por organização no backend. A saída é uma base segura para a experiência de busca e acompanhamento da Fase 3; ainda não é uma aplicação comercial utilizável por clientes.

**Entrada:** decisões da Fase 0 registradas e aceite operacional da Fase 1 demonstrado em PostgreSQL: migração executada em banco limpo, coleta controlada persistida, falha distinguível de resultado vazio, retomada e histórico verificados. Se a Fase 1 ainda não passou por essa demonstração, limitar o trabalho da Fase 2 à estrutura da API e ambientes locais; não conectar cliente ou produção a uma base ainda não validada.

| Etapa | Trabalho | Evidência de conclusão |
| --- | --- | --- |
| F2.1 — Base da API | Criar aplicação FastAPI, configuração por ambiente, registro de dependências e erros, prefixo `/v1`, endpoints de saúde e OpenAPI | API inicia localmente; saúde não expõe segredos ou detalhes internos; contrato OpenAPI é acessível em homologação |
| F2.2 — Identidade autenticada | Integrar validação de JWT do Supabase Auth; conferir assinatura, emissor, audiência, validade e identificador do usuário; criar/atualizar perfil local vinculado ao `sub` do provedor | Token válido identifica um usuário; token ausente, expirado, adulterado ou de outro emissor recebe 401; nenhum segredo privilegiado aparece no navegador ou logs |
| F2.3 — Organizações e autorização | Criar migrações para `users`, `organizations` e `memberships`; permitir criação da primeira organização pelo usuário autenticado e confirmado; atribuir vínculo `owner` na mesma transação; resolver organização pelo vínculo validado no servidor | Proprietário consulta e altera sua organização; usuário sem vínculo recebe 403/404; trocar ou forjar `organization_id` não permite ler nem alterar organização alheia |
| F2.4 — Ambientes e entrega | Separar configuração local, homologação e produção; adicionar CI para qualidade, testes da API e migrações; documentar implantação, migração compatível e retorno operacional | CI reproduz instalação e banco temporário; homologação usa credenciais e banco próprios; implantação registra versão e resultado das migrações |
| F2.5 — Base de autorização | Implementar dependências reutilizáveis de autenticação e resolução de organização; aplicar escopo de organização em cada rota privada; registrar alterações de perfil e organização com ator e horário | Revisão das rotas e verificações automatizadas provam que toda operação privada passa pela mesma política de acesso |

**Modelo inicial de acesso:** o usuário do Supabase é a identidade de autenticação; a aplicação guarda seu `subject` externo como identificador único, e-mail verificado e timestamps necessários. `organizations` representa uma empresa. `memberships` liga usuários às organizações com papel. Na Fase 2, somente o criador recebe o papel `owner`; convites e papéis de equipe ficam na Fase 8. O contexto da organização vem da associação autenticada, nunca de um identificador enviado pelo cliente sem validação.

**Rotas limitadas desta fase:** `GET /v1/health`, `GET /v1/me`, `POST /v1/organizations`, `GET /v1/organizations/{id}` e `PATCH /v1/organizations/{id}`. `POST` cria uma única organização inicial para o usuário autenticado. Não incluir oportunidade, perfil de interesse, acompanhamento, alertas, plano ou cobrança nesta fase. Paginação de oportunidades e políticas comerciais pertencem às fases posteriores.

**Regras de segurança:** backend é a autoridade de autorização; nunca confiar em papel, e-mail ou `organization_id` declarado no corpo da requisição. Validar JWT em cada requisição privada e falhar fechado quando identidade ou associação não puder ser confirmada. Banco de domínio não recebe chamadas diretas do navegador. Segredos, chaves de serviço e tokens não são registrados em logs. Não habilitar acesso administrativo interno por uma flag controlada pelo usuário. RLS só será requisito para tabelas expostas diretamente; não substitui a autorização do backend.

**Critérios de aceite da fase:**

1. Um ambiente local e outro de homologação são configuráveis sem compartilhar banco, JWT ou segredos de produção.
2. Migrações de Fase 1 e 2 criam um banco vazio do início; a migração não elimina nem renomeia destrutivamente tabelas de ingestão.
3. Um usuário autenticado e com e-mail confirmado pode criar sua primeira organização; a associação `owner` é criada na mesma transação e repetição da requisição não cria organizações duplicadas.
4. Os endpoints privados rejeitam ausência de token, assinatura inválida, token expirado e emissor/audiência incorretos.
5. Em cenário com duas organizações e usuários distintos, nenhum usuário lê ou altera a organização sem associação, mesmo alterando IDs de rota ou corpo.
6. OpenAPI descreve erros 401/403/404 e os campos aceitos; validação de entrada impede atribuição de papel e vínculo arbitrário pelo cliente.
7. CI instala a aplicação, sobe PostgreSQL efêmero, aplica todas as migrações e executa verificações automatizadas de autenticação e isolamento.
8. Uma implantação em homologação tem instrução de migração, verificação de saúde, logs sem credenciais e procedimento documentado para voltar à versão anterior sem reverter dados destrutivamente.

**Revalidação em 15/10/2026:** com o `.env` local, `/v1/health` retornou `200` consultando o PostgreSQL remoto, OpenAPI retornou `200` e `/v1/me` sem token retornou `401`. Os testes locais de claims e isolamento simulado passaram. Duas contas Auth confirmadas foram usadas na interface; o banco contém dois usuários de domínio, duas organizações e duas memberships. A F2 permanece parcial: falta uma prova autenticada direta de negação para IDs cruzados e uma implantação de homologação separada.

**Fora do escopo:** frontend completo e onboarding comercial, recuperação de senha personalizada, convites/equipe, painel administrativo, busca/feed/ficha, e-mails, Redis/Celery, agendamento, cobrança, RLS em tabelas ainda não expostas, personalização por plano e operação pública. O fluxo de autenticação pode ser exercitado com uma interface mínima de documentação ou cliente de API.

**Ordem e dependências:** F2.1 cria o esqueleto e contratos; F2.2 valida o provedor e o formato de identidade; F2.3 modela a associação e as regras de tenant; F2.4 prepara a implantação e o CI; F2.5 integra e prova a política em todas as rotas. Não ampliar esta fase para construir a experiência da Fase 3.

**Estimativa de referência:** 45–65 horas para uma pessoa, conforme a tabela de fases. Inclui integração real com Supabase Auth em homologação e CI com PostgreSQL. Conta, aprovação ou configuração externa do provedor podem ampliar o calendário. Reestimar se a Fase 1 exigir mudanças de esquema ou se a escolha de hospedagem não estiver disponível.

**Saída da Fase 2:** API implantada em homologação, autenticação verificada com o provedor, uma organização por proprietário funcionando, isolamento entre organizações demonstrado e migrações repetíveis. A Fase 3 pode então adicionar dados de oportunidade e funcionalidades privadas sobre esse limite de autorização.

### 20.3 Definição executável da Fase 3 — Experiência principal

**Objetivo:** permitir que um usuário autenticado encontre oportunidades reais já coletadas, entenda por que são relevantes, consulte sua ficha e histórico, e acompanhe oportunidades para a própria organização. Ao final, o produto terá uma jornada web funcional em ambiente local, sem depender de cobrança ou envio de e-mail.

**Entrada e condição de início:** a Fase 2 deve iniciar localmente ligada ao banco Supabase, com `GET /v1/health` respondendo com sucesso, sessão Supabase Auth validada pela API e organização inicial criada. A Fase 1 precisa ter uma amostra real do PNCP persistida e reconciliada, com estado de coleta, fonte, identidade, datas e histórico confiáveis. Se a cobertura ainda não tiver sido homologada, desenvolver contra a amostra real versionada, mostrar claramente a cobertura disponível e não declarar o produto pronto para piloto externo. SMTP fica deliberadamente para a Fase 4 ou uma etapa posterior, depois de estabilizar a base.

**Revalidação em 15/10/2026:** além da implementação inicial, busca, ficha e histórico retornaram dados do PostgreSQL remoto (25 oportunidades; sem mudança fictícia na versão inicial); a API conectada retornou health 200. Testes locais com duas organizações simuladas cobrem perfis, acompanhamentos, feedback e idempotência. As revisões `0005_phase3_experience`, `0006_phase4_notifications` e `0007_phase4_fk_indexes` estão aplicadas. Duas contas Auth reais foram usadas na interface; há dois usuários, organizações, memberships e perfis, e o usuário confirmou o isolamento e a limpeza dos dados ao trocar de conta. A Fase 3 permanece parcial: acompanhamentos e feedback reais ainda não foram exercitados (tabelas sem registros), e a amostra PNCP ainda não foi reconciliada com a cobertura aprovada.

**Entregas incrementais:**

| Etapa | Trabalho | Evidência de conclusão |
| --- | --- | --- |
| F3.1 — Contratos de leitura | Expor oportunidades e ficha pela FastAPI; paginação limitada, filtros combináveis, ordenação estável, datas em fuso explícito, estado oficial/derivado, fonte e estado de atualização | Contrato OpenAPI documentado; paginação não duplica nem perde registros entre páginas; indisponibilidade ou cobertura atrasada não aparece como lista completa vazia |
| F3.2 — Perfil de interesse | Criar e editar perfis vinculados à organização com seleções hierárquicas dos catálogos oficiais CATMAT/CATSER, município, situação e prazo; somente o nome do perfil aceita texto livre | Um usuário lê e altera só perfis de organização à qual pertence; itens selecionados e exclusões vêm dos catálogos oficiais; atualização do perfil não muda classificação global |
| F3.3 — Relevância explicável | Aplicar regras determinísticas e versionadas aos campos normalizados; devolver sinais que justificam cada correspondência e razões de exclusão; permitir feedback privado como “relevante” ou “não relevante” com motivo | Casos de amostra mostram resultado e explicação reproduzíveis; termo negativo vence correspondência positiva quando definido como exclusão; feedback de uma empresa não altera o feed de outra |
| F3.4 — Busca, feed e ficha web | Criar aplicação web autenticada: início “Para minha empresa”, explorar com filtros, lista paginada, ficha, acesso à fonte oficial e histórico de versões observadas | Jornada opera no navegador com dados reais; filtros podem ser compartilhados pela URL; campo ausente, prazo desconhecido e cobertura atrasada são apresentados sem inferências inventadas |
| F3.5 — Acompanhamento | Criar e remover acompanhamentos por organização, mostrar status, prazo, última observação e mudanças desde o acompanhamento; tornar ações repetidas idempotentes | Um acompanhamento reapresentado não duplica; remoção não apaga histórico público; oportunidades já existentes não são anunciadas como alteração nova |
| F3.6 — Autorização e estabilidade | Revisar cada rota e consulta; paginar com limites; acrescentar testes de API, banco e navegador para autenticação, isolamento, filtros, feedback e acompanhamento | Dois usuários e organizações não acessam nem modificam dados privados alheios; testes automatizados cobrem permitir e negar; CI aplica migrações do zero |

**Jornada mínima incluída:** uma conta Supabase Auth já confirmada entra no sistema; conclui ou revisa o perfil da empresa; configura um perfil de interesse; consulta o feed e a busca; abre uma oportunidade e sua fonte; acompanha ou remove; consulta mudanças observadas e envia feedback privado. Em desenvolvimento, contas confirmadas podem ser provisionadas manualmente no painel do Supabase. Não desabilitar confirmação de e-mail nem criar um atalho de autenticação para contornar a falta de SMTP.

**Modelo e regras de dados:** oportunidades e versões são dados públicos compartilhados e não são duplicados por organização. Perfis, buscas salvas se forem incluídas, acompanhamentos e feedback são privados e carregam `organization_id`; toda leitura e escrita valida a associação no backend. A identidade Supabase não é substituída por identificadores enviados pelo navegador. Datas desconhecidas continuam explícitas; estado oficial permanece separado de estado derivado; histórico informa quando o LicitaGoias começou a observar a oportunidade.

**Busca e classificação da primeira entrega:** começar com pesquisa textual nos campos normalizados e filtros por região, situação e datas disponíveis. Usar mecanismos e índices nativos do PostgreSQL somente após avaliar a consulta e o tamanho real da amostra. O matching usa regras versionadas, termos positivos/negativos e sinais legíveis; não usar IA, OCR ou associação baseada no JSON bruto nesta fase. Limites de paginação e tamanho de consulta pertencem ao servidor. Feedback só calibra o perfil da organização até existir volume e método revisados para uma regra global.

**Segurança do Supabase:** a aplicação web chama a FastAPI; ela não consulta as tabelas de domínio pela Data API. Não colocar a senha do papel `licitagoias_app`, chave secreta ou credenciais administrativas no navegador. Novas tabelas precisam de migração reproduzível, RLS habilitada e privilégios mínimos na mesma alteração; a política do papel do backend não deve substituir as verificações de organização que a API faz. Revisar views e funções quanto a bypass de RLS. Testar negação para `anon`, `authenticated` e para usuário de outra organização, além dos caminhos autorizados pelo backend.

**Rotas previstas:** `GET /v1/opportunities`, `GET /v1/opportunities/{id}`, `GET /v1/opportunities/{id}/changes`, CRUD de `/v1/interest-profiles`, criação/listagem/remoção em `/v1/follows` e registro/listagem de `/v1/feedback`. Identificadores da organização são resolvidos pelo servidor ou validados contra a associação; paginação, filtros aceitos e limites são documentados no OpenAPI. Ajustar os nomes à convenção já adotada em `/v1/organizations` durante a implementação, sem duplicar contratos.

**Critérios de aceite da fase:**

1. Uma conta confirmada entra no ambiente local usando o fluxo normal do Supabase Auth; tokens ausentes, inválidos ou expirados são recusados pela API.
2. A busca e a ficha retornam oportunidades reais existentes no PostgreSQL, citam fonte e última observação, respeitam paginação e distinguem ausência de dados, coleta parcial e cobertura desatualizada.
3. Um perfil pode ser criado, alterado e removido pela organização correta; positivos, sinônimos e negativos geram explicações e resultados reproduzíveis em amostras versionadas.
4. Uma oportunidade mostra versões e alterações observadas sem criar mudanças fictícias na primeira leitura ou esconder suspensão/cancelamento registrado.
5. Acompanhar, repetir a ação e remover funciona sem duplicação e sem misturar registros entre organizações.
6. Cenários com dois usuários e organizações provam que adulterar IDs de rota, filtro ou corpo não expõe perfis, acompanhamentos ou feedback alheios.
7. Cada tabela nova tem migração, RLS e privilégios revisados; o frontend contém apenas URL e chave publicável; DB Advisors e verificações automatizadas não identificam exposição indevida.
8. CI executa migrações em banco PostgreSQL efêmero e cobre os casos de autorização, filtros e idempotência; a jornada do navegador termina em acompanhar e consultar a ficha, sem depender de e-mail.
9. Não existe envio de SMTP/e-mail, checkout, assinatura ou liberação de acesso por pagamento nesta fase; interfaces não apresentam esses recursos como disponíveis.

**Fora do escopo:** configurar SMTP ou campanhas, cadastro público e recuperação de senha por e-mail, notificações e resumos, worker e agendamento de produção, cobrança, limites comerciais por plano, console administrativo completo, novos portais, busca em itens, OCR/PDF, IA, exportações e hospedagem pública. O acesso local usa usuários confirmados provisionados no painel; a preparação dos fluxos públicos de conta depende de SMTP numa fase futura.

**Ordem e dependências:** provar F2 local e a amostra da F1 antes de iniciar a experiência; estabelecer contratos de leitura em F3.1; fazer perfil e regras em F3.2–F3.3; construir busca e ficha sobre esses contratos em F3.4; integrar acompanhamento e autorização em F3.5–F3.6. Alterações de esquema são iteradas diretamente no banco de desenvolvimento e registradas em uma migração limpa antes do aceite; dados de homologação/produção não recebem experimentos. Revisar RLS, concessões e índices antes de aplicar qualquer migração remota.

**Estimativa de referência:** 65–95 horas, incluídas as verificações dos critérios. A estimativa pressupõe uma amostra PNCP acessível e reconciliada, uma organização por usuário, uma interface web responsiva e regras determinísticas. Homologar nova cobertura, corrigir o contrato do PNCP, implementar convite de equipe ou estabilizar SMTP são reestimativas separadas.

**Saída da Fase 3:** um usuário de desenvolvimento autenticado consegue localizar e avaliar oportunidades reais, compreender a indicação, consultar fonte e histórico e acompanhá-las em sua organização; o isolamento entre clientes está demonstrado. Esse resultado permite validar a utilidade do produto antes de iniciar a Fase 4 de monitoramento e comunicação.

### 20.4 Definição executável da Fase 4 — Monitoramento e comunicação

**Objetivo:** detectar alterações nas oportunidades acompanhadas e comunicar apenas eventos relevantes, com preferências controladas pelo usuário, entrega rastreável e tratamento seguro de falhas. Esta fase habilita um piloto operacional com e-mail; não inclui cobrança nem lançamento comercial amplo.

**Entrada e condição de início:** os critérios de saída da Fase 1 e da Fase 3 precisam estar demonstrados: coleta real reconciliada, histórico consistente, migrações aplicadas, autorização entre organizações provada e jornada de acompanhamento validada. Antes de emitir mensagens reais, escolher e testar os provedores de SMTP/e-mail transacional, verificar domínio remetente e DNS e revisar consentimento, descadastro, privacidade e retenção. Se a base ainda não estiver estável, executar primeiro em sandbox sem destinatários reais.

**Andamento em 15/10/2026:** implementada a primeira fatia local: evento derivado de nova versão somente para oportunidade acompanhada, caixa e preferências por usuário/organização, outbox e worker SMTP genérico, descadastro por token e endpoint de webhook normalizado. As revisões `0005_phase3_experience`, `0006_phase4_notifications` e `0007_phase4_fk_indexes` foram aplicadas remotamente via MCP; RLS, políticas e privilégios do papel `licitagoias_app` foram conferidos. Envio segue desativado por padrão e não há provedor escolhido. F1/F3 ainda aguardam homologação, e agendamento da coleta, métricas/alertas operacionais, revisão de segurança e validação com destinatários continuam pendentes. Este registro não representa aceite da Fase 4.

**Entregas incrementais:**

| Etapa | Trabalho | Evidência de conclusão |
| --- | --- | --- |
| F4.1 — Eventos notificáveis | Derivar eventos de versões observadas para processos acompanhados; definir alterações críticas (suspensão, cancelamento, mudança de situação ou prazo) e informativas; a primeira observação nunca vira alteração | Fixtures com versões antes/depois geram eventos determinísticos, sem evento falso na carga inicial e sem misturar processos |
| F4.2 — Preferências e alertas | Persistir frequência diária/semanal, fuso horário, canais, preferências para eventos críticos, leitura/arquivo e descadastro por organização/usuário | Preferências sobrevivem a reprocessamento, são aplicadas no servidor e não permitem um usuário alterar as de outra organização |
| F4.3 — Outbox e worker | Gravar mensagens transacionais em outbox antes do envio; processar fora da requisição web, com reserva concorrente, idempotência, tentativas limitadas, espera crescente e fila de falhas para revisão/reenvio auditado | Reiniciar ou executar duas instâncias não duplica mensagens; falhas temporárias retomam; falhas permanentes são visíveis e não entram em ciclo infinito |
| F4.4 — Integração de e-mail | Configurar separadamente o SMTP do Supabase Auth (confirmação/recuperação) e o remetente transacional do produto, mesmo que o provedor escolhido suporte ambos; proteger credenciais, validar domínio e implementar modelos acessíveis em texto e HTML | Confirmação/recuperação e mensagens do produto funcionam em sandbox; domínio e remetentes autorizados; segredos não aparecem no frontend, logs ou repositório |
| F4.5 — Preferências e supressão | Oferecer descadastro seguro dos resumos, endereço de preferências, supressão de bounces/complaints e deduplicação de eventos recebidos do provedor; preservar somente os alertas legalmente/operacionalmente necessários após descadastro | Link com token opaco, expirável e de escopo limitado altera apenas a inscrição correspondente; destinatários suprimidos não recebem novo envio de marketing/resumo |
| F4.6 — Operação e observabilidade | Agendar coleta e geração de resumos em worker separado; expor estado da fila, latência, entregas, falhas, supressões e idade da última coleta; alarmar falha de coleta e crescimento da fila | Operador encontra execução e mensagem por IDs correlacionados, reprocessa com trilha e distingue ausência de oportunidades de falha da fonte |
| F4.7 — Segurança e estabilidade | Aplicar migrações/RLS/privilégios mínimos a novas tabelas; validar tokens de descadastro/webhook, assinatura do provedor, limites de frequência, isolamento por tenant e retenção | Casos automatizados autorizados e negados passam; webhook repetido não duplica efeitos; não há envio após descadastro/supressão |

**Jornada mínima:** uma mudança posterior ao acompanhamento gera evento com comparação antes/depois; o usuário vê o evento na área de alertas e recebe aviso imediato se for crítico ou no resumo configurado se for informativo; a ficha mantém a fonte oficial e o instante de observação; preferências e descadastro funcionam sem pedir login no link enviado. Confirmação e recuperação de acesso seguem o fluxo oficial do Supabase Auth, sem bypass da confirmação.

**Modelo e idempotência:** introduzir modelos separados para eventos de alerta, preferências, outbox e entregas/supressões. Dados de oportunidade permanecem compartilhados; destinatários, preferências, feedback e histórico de entrega são privados por organização/usuário. Cada evento derivado tem chave única baseada em processo, versão e tipo de alteração; cada tentativa de envio tem chave idempotente persistente e identificador do provedor. A retenção do provedor não substitui a idempotência local. Não apagar o evento original ao descadastrar ou falhar uma entrega.

**Política de comunicação:** resumos respeitam o fuso horário da organização e frequência escolhida; alertas críticos têm preferência explícita, não são repetidos em cada execução e continuam consultáveis no produto. Mensagens identificam fonte, processo, alteração observada e link para a ficha; deixam claro que o usuário precisa validar o edital e conduzir a participação no portal oficial. Falha da coleta nunca produz e-mail afirmando que não há oportunidades. Não enviar conteúdo de oportunidade a endereço não verificado.

**Decisão de provedores:** a escolha entre SMTP próprio do Supabase e provedor transacional (por exemplo, Resend, já listado como candidato no planejamento) fica para o início da Fase 4. Comparar limites e entregabilidade, webhooks e assinaturas, política de supressão, idempotência, região e tratamento de dados, preço para o volume piloto e facilidade de saída/migração. Validar planos, contratos e documentação vigentes no momento da escolha; não assumir que o nome do provedor no plano equivale a uma decisão aprovada.

**Critérios de aceite da fase:**

1. Uma alteração observada depois do acompanhamento aparece com campos anterior/novo e fonte; primeira carga não gera falso alerta.
2. Suspensão, cancelamento e mudança de prazo são classificados de acordo com regra versionada, deduplicados e consultáveis no produto.
3. Resumo diário/semanal respeita fuso, preferências, verificação de e-mail, descadastro e supressão; eventos críticos seguem preferência definida.
4. Processamento usa outbox persistente e worker separado; falha, timeout, repetição de webhook e reexecução não causam perda nem duplicidade lógica.
5. Tentativas e entregas têm estados rastreáveis; erro permanente vai para revisão, e reenvio é explícito, idempotente e auditado.
6. Webhooks são verificados e deduplicados; bounces/complaints atualizam supressão e impedem novos envios conforme política documentada.
7. Duas organizações não recebem eventos, resumos ou mudanças de preferência uma da outra; descadastro de um endereço não afeta outros destinatários.
8. Confirmação e recuperação Supabase Auth funcionam em ambiente controlado; SMTP e chaves não são expostos ao navegador.
9. Operação distingue fila atrasada, coleta parcial/falha, lista legitimamente vazia e falha de envio; alertas técnicos não incluem tokens ou conteúdo sensível desnecessário.
10. Execução de carga/repetição, testes de segurança e ciclo com destinatários piloto aprovados precedem qualquer envio amplo.

**Fora do escopo:** campanhas comerciais, prospecção por e-mail, WhatsApp/SMS/push, caixa de entrada integrada, envio de documentos privados, automação de participação em portal, cobrança/assinatura, garantias de entrega instantânea e novas fontes de coleta. Fila de notificação não decide acesso pago nem altera o estado oficial da licitação.

**Ordem e dependências:** concluir e homologar F1/F3; validar eventos em fixtures e base real; decidir os provedores e a política de privacidade/descadastro; implementar preferências e modelos; criar outbox/worker com sandbox; validar webhooks, supressão e restauração; só então habilitar destinatários do piloto. Migrações remotas requerem credencial administrativa separada do papel restrito usado pela API. Testar restauração e replay antes de produção.

**Estimativa de referência:** 45–70 horas de engenharia, incluindo testes e operação inicial, assumindo um provedor transacional, um canal e resumos diário/semanal simples. Configuração e aquecimento de domínio, aprovação de conta do provedor, incidentes de entregabilidade, requisitos jurídicos e novos canais podem ampliar o prazo. Confirmar cotações e limites antes de selecionar fornecedor.

**Saída da Fase 4:** usuários-piloto recebem alterações e resumos corretos segundo suas preferências, podem descadastrar-se, e a equipe consegue explicar e recuperar cada falha sem duplicar notificações. A fase prepara a validação comercial e decisões posteriores de cobrança, mas não ativa pagamentos.

## 21. Backlog inicial executável

| ID | Tarefa | Prioridade | Depende de | Evidência de conclusão |
| --- | --- | --- | --- | --- |
| B01 | Rodar baseline e documentar comportamento atual | P0 | — | Resultado dos testes e amostra de saída |
| B02 | Definir identidade e semântica de datas | P0 | B01 | Modelo e exemplos revisados |
| B03 | PostgreSQL e migrações | P0 | B02 | Banco reproduzido do zero |
| B04 | Paginação, falhas e checkpoints | P0 | B01 | Coleta multipágina retomável |
| B05 | Snapshots, versões e eventos | P0 | B03–B04 | Retificação reproduzível |
| B06 | Preservar suspensões/cancelamentos | P0 | B05 | Histórico intacto e feed correto |
| B07 | API, auth e organizações | P0 | B03 | Isolamento demonstrado |
| B08 | Perfis, exclusões e regras explicáveis | P0 | B05, B07, aceite F1/F2 | Regras reproduzíveis e feedback isolado por organização |
| B09 | Busca, ficha, histórico e acompanhamento web | P0 | B07–B08 | Jornada E2E com oportunidade real |
| B10 | Outbox, preferências e e-mail | P0 | F1/F3 aceitas, provedores definidos e base estabilizada | Alertas e resumos idempotentes; descadastro/supressão e replay auditados (Fase 4) |
| B11 | Cobrança e entitlements | P0 | B07 | Sandbox e reconciliação |
| B12 | Administração e publicação de cobertura | P0 | B04–B11 | Operador identifica e trata falhas |
| B13 | Piloto, segurança e restauração | P0 | B09–B12 | Checklist de lançamento aprovado |
| B14 | Itens estruturados e exportação | P1 | B13 | Produto encontrado fora do título |
| B15 | Equipe e colaboração | P2 | B13 + validação | Permissões e uso por equipe |
| B16 | OCR e análise assistida | P2 | Corpus e orçamento | Extração avaliada e rastreável |

Cada issue deve conter problema, escopo, itens fora do escopo, aceite e dependências. Este documento não cria issues, branches ou alterações no GitHub automaticamente.

## 22. Orçamento e sustentabilidade

Envelopes ilustrativos para planejamento, **não preços consultados de provedores**. Servem para avaliar cenários e devem ser substituídos por cotações no desenho final de implantação.

| Item mensal | Faixa de reserva proposta |
| --- | --- |
| Hospedagem de web/API/worker/Redis | R$ 150–450 |
| Banco, backups e armazenamento | R$ 100–300 |
| E-mail transacional | R$ 0–150 |
| Monitoramento e serviços auxiliares | R$ 0–100 |
| Total base ilustrativo | R$ 250–1.000 |

Não somar duas vezes serviços incluídos em um mesmo contrato. Domínio, câmbio, impostos, taxas de pagamento, atendimento, contabilidade, aquisição e trabalho do desenvolvedor estão fora desse total. Planos gratuitos podem ajudar no piloto, mas limites e continuidade precisam ser verificados. IA/OCR são despesas adicionais.

### 22.1 Exemplo de margem de contribuição

Cenário puramente ilustrativo: Essencial a R$ 79; reserva variável de 10% da receita para taxas/tributos; R$ 5 por cliente para consumo; R$ 10 por cliente para suporte; custo fixo de R$ 500/mês. Os 10% não representam alíquota legal nem tarifa de provedor.

Contribuição unitária = 79 × 0,90 − 5 − 10 = **R$ 56,10**. Cobertura dos R$ 500 fixos: **9 clientes**, arredondando para cima. Incluindo remuneração hipotética de R$ 2.500/mês para o trabalho: **54 clientes** para cobrir R$ 3.000. Não inclui aquisição nem recuperação do investimento inicial.

| Clientes Essencial | Receita mensal | Saldo após variáveis e R$ 500 fixos, antes da remuneração |
| --- | --- | --- |
| 10 | R$ 790 | R$ 61 |
| 30 | R$ 2.370 | R$ 1.183 |
| 60 | R$ 4.740 | R$ 2.866 |

Estes números não são previsão de vendas ou lucro. O custo de suporte pode ser o principal limite de um plano barato. Registrar minutos por cliente e revisar preço/escopo se o uso exigir atendimento frequente.

## 23. Validação, aquisição e métricas

### 23.1 Piloto comercial

Entrevistar 10–15 fornecedores, observar como pesquisam hoje e apresentar oportunidades reais do segmento. Recrutar 3–5 pagantes para um piloto de 30 dias. Registrar o que foi útil, oportunidades perdidas, tempo gasto e interesse na renovação. Uma amostra pequena dá direção, não valida o mercado inteiro.

Critério inicial de decisão: ao menos 3 pilotos usarem semanalmente e pelo menos 2 desejarem renovar nas condições apresentadas. Se não acontecer, investigar relevância, volume, preço, suporte e aquisição antes de ampliar funcionalidades.

Canais candidatos: indicações de fornecedores, contatos profissionais, parcerias consentidas com escritórios contábeis e demonstrações locais. Não usar carteiras de clientes de terceiros sem autorização. Conteúdo público pode explicar como pesquisar oportunidades e apresentar exemplos com fonte.

### 23.2 Métricas de produto e operação

| Indicador | Definição | Uso |
| --- | --- | --- |
| Ativação | Perfil concluído + primeira oportunidade acompanhada em 7 dias | Qualidade do primeiro uso |
| Relevância | Resultados marcados úteis sobre resultados avaliados | Ajustar regras sem confundir com cobertura total |
| Tempo até encontrar | Tempo observado para selecionar uma oportunidade adequada | Demonstrar economia de esforço |
| Uso semanal | Organizações com pesquisa, abertura de ficha ou acompanhamento | Acompanhar hábito |
| Renovação | Assinantes elegíveis que renovam no ciclo | Validar valor pago |
| MRR | Receita recorrente mensal equivalente, descontando canceladas/inativas | Operação comercial |
| Churn de clientes | Cancelamentos no período / clientes no início | Retenção; separar fim de teste |
| CAC | Gastos de aquisição, incluindo esforço atribuído / novos pagantes | Sustentabilidade do canal |
| Latência de detecção | Tempo entre publicação/alteração conhecida e observação | Qualidade da coleta |
| Sucesso de coleta | Execuções completas / previstas, por fonte | Não mascarar execução parcial |
| Custo de atendimento | Minutos e custo por organização/mês | Ajustar preço e suporte |

Meta exploratória de relevância: pelo menos 70% dos primeiros 10 resultados avaliados como úteis em perfis com volume suficiente. Não é promessa comercial. Comparar com a ferramenta ou método que cada piloto já usa. Não usar contratos ganhos como único indicador: o LicitaGoias não controla preço, habilitação ou disputa.

## 24. Riscos e respostas

| Risco | Sinal | Resposta |
| --- | --- | --- |
| Dados gratuitos/concorrência | Clientes não percebem diferença | Validar triagem, mudanças e itens; não competir só por preço |
| Pouco volume local | Resumos frequentemente vazios | Rever segmento ou região antes de cobrar amplamente |
| Falha de fonte | Atualização vencida | Estado público, retentativa e comunicação transparente |
| Falso positivo | Clientes dispensam a maioria | Melhorar perfil, termos negativos e contexto |
| Oportunidade perdida | Cliente encontra fora da plataforma | Investigar paginação, cobertura, modalidade e matching |
| Prazo incorreto | Divergência com edital | Proveniência, revisão e alerta corretivo aos afetados |
| Custo de suporte | Atendimento cresce mais que receita | Guias, configuração simples, limites e revisão comercial |
| E-mails bloqueados | Rejeição/reclamação | Supressão, autenticação de domínio e ajuste de frequência |
| Vazamento entre clientes | Acesso cruzado | Bloquear lançamento, corrigir autorização e tratar incidente |
| Cobrança inconsistente | Pagamento sem acesso ou acesso sem vigência | Reconciliação e auditoria |
| Escopo excessivo | Várias frentes inacabadas | V1 fixa; itens, equipe e IA em gates separados |

## 25. Decisões pendentes e recomendação de execução

| Decisão | Padrão recomendado | Como confirmar |
| --- | --- | --- |
| Segmento inicial | TI como primeiro candidato | Volume e entrevistas |
| Região | Aparecida + Goiânia após homologação | Comparar coleta com amostra oficial |
| Preço | Essencial R$ 79/mês | Piloto pago e renovação |
| Infraestrutura | Banco gerenciado e poucos serviços | Cotação e restauração testada |
| Provedor de cobrança | Asaas | Sandbox, meios elegíveis e contrato |
| Ritmo de desenvolvimento | Planejar com 20h/semana | Disponibilidade real de Gabriel |
| Expansão de fontes | Somente para preencher lacuna demonstrada | Medir ganho de cobertura e manutenção |

**Primeiro marco concreto:** obter uma base que sobreviva a reexecuções, preserve alterações e entregue uma seleção útil a alguns fornecedores. A interface web, os e-mails e a cobrança devem se apoiar nessa base. O perfil de interesse navega pelos catálogos oficiais CATMAT/CATSER para reduzir divergências de escrita.

## 26. Referências e rastreabilidade

Referências de código lidas na conversa; o repositório pode evoluir depois desta análise. As recomendações de produto, preços, cronograma e metas são propostas próprias, não afirmações extraídas dos fornecedores.

### Repositório

- [R1 — README](https://github.com/Gabriel-Programacoes/LicitaGoias/blob/main/README.md)
- [R2 — Planejamento existente](https://github.com/Gabriel-Programacoes/LicitaGoias/blob/main/docs/plano-ferramenta-licitacoes-goias.md)
- [R3 — Coletor PNCP](https://github.com/Gabriel-Programacoes/LicitaGoias/blob/main/src/licitagoias/collectors/pncp.py)
- [R4 — Modelo](https://github.com/Gabriel-Programacoes/LicitaGoias/blob/main/src/licitagoias/models.py)
- [R5 — Pipeline](https://github.com/Gabriel-Programacoes/LicitaGoias/blob/main/src/licitagoias/pipeline.py)
- [R6 — Classificação](https://github.com/Gabriel-Programacoes/LicitaGoias/blob/main/src/licitagoias/classification.py)
- [R7 — Persistência](https://github.com/Gabriel-Programacoes/LicitaGoias/blob/main/src/licitagoias/storage.py)

### Fontes externas consultadas em 14/10/2026

- [S1 — PNCP: perguntas e respostas](https://www.gov.br/pncp/pt-br/pncp/perguntas-e-respostas/): acesso público e consulta.
- [S2 — Effecti: oferta gratuita](https://effecti.com.br/licitacao-gratis/): evidência de concorrência com personalização gratuita; descrição do próprio fornecedor, não comparação independente de qualidade.
- [S3 — PNCP: manuais](https://www.gov.br/pncp/pt-br/pncp/manuais) e [acesso ao PNCP](https://pncp.gov.br/manual/pt-br/latest/acesso_ao_pncp/index.html): orientar validação dos serviços; conferir contrato da API de consulta na implementação.
- [S4 — Next.js: App Router](https://nextjs.org/docs/app/getting-started): estrutura da aplicação web.
- [S5 — FastAPI: tarefas em segundo plano](https://fastapi.tiangolo.com/pt/tutorial/background-tasks/): limites entre trabalho na aplicação e processamento separado.
- [S6 — Celery: tarefas](https://docs.celeryq.dev/en/stable/userguide/tasks.html): execução e confiabilidade dos workers.
- [S7 — PostgreSQL: busca textual](https://www.postgresql.org/docs/current/textsearch.html): base da busca inicial.
- [S8 — Resend: idempotência](https://resend.com/docs/dashboard/emails/idempotency-keys): proteção no provedor e janela de retenção das chaves.
- [S9 — Asaas: assinaturas](https://docs.asaas.com/docs/assinaturas) e [webhooks](https://docs.asaas.com/docs/webhooks-2): contratos de integração a validar no sandbox.
- [S10 — Supabase: RLS](https://supabase.com/docs/guides/database/postgres/row-level-security): controles de acesso ao banco.
- [S11 — ANPD: guia de segurança para pequenos agentes](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-sobre-seguranca-da-informacao-para-agentes-de-tratamento-de-pequeno-porte): referência para preparação de segurança e privacidade.
