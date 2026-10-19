# LicitaGoiás — guia de marca e interface

Este documento define a identidade visual e os padrões de interface do LicitaGoiás. Use-o como referência ao criar telas, componentes, mensagens, materiais de produto e apresentações. O objetivo é manter o produto reconhecível, legível e consistente enquanto a aplicação evolui.

## 1. Essência da marca

**Propósito:** ajudar fornecedores a descobrir e acompanhar oportunidades de compras públicas com clareza.

**Público:** empresas e profissionais que fornecem produtos ou serviços ao setor público, começando pelo estado de Goiás.

**Personalidade:** confiável, objetiva, local, cuidadosa com dados e profissional. A interface deve parecer uma ferramenta de trabalho, não um portal governamental nem uma página promocional genérica.

**Princípios de experiência:**

- Mostrar primeiro a informação necessária para a próxima decisão.
- Distinguir dados oficiais, critérios do perfil e estados calculados pelo LicitaGoiás.
- Comunicar falhas, cobertura parcial e ausência de dados sem sugerir certeza indevida.
- Deixar filtros opcionais visivelmente opcionais e preservar estados vazios úteis.
- Não esconder ações essenciais em hover ou em ícones sem rótulo acessível.

## 2. Identidade e uso do logo

O logo combina o nome **licita**goias com um símbolo quadrado de cantos suaves. O símbolo usa a letra “L” e uma seta ascendente, sugerindo busca e avanço. O nome deve aparecer junto do símbolo em cabeçalhos, login e materiais institucionais.

- Use a versão colorida sobre superfícies claras.
- Não estique, gire, aplique gradientes ou altere a relação entre símbolo e nome.
- Preserve espaço livre ao redor equivalente à largura do símbolo.
- O símbolo pode aparecer sozinho em espaços pequenos, desde que exista texto alternativo ou nome acessível.
- A marca não deve ser confundida com endosso ou vínculo oficial com o PNCP ou Compras.gov.br.

## 3. Paleta de cores

Os tokens abaixo são a fonte única de cores da interface. A paleta clara está ativa por padrão. Os nomes `--muted` e `--muted-foreground` têm funções diferentes: `--muted` é uma superfície neutra; `--muted-foreground` é texto secundário.

### Tema claro

| Token | Valor | Uso |
|---|---|---|
| `--background` | `#f5f5f5` | Fundo geral |
| `--card` | `#ffffff` | Cartões e superfícies elevadas |
| `--popover` | `#ffffff` | Menus, diálogos e popovers |
| `--foreground` | `#1a1a1a` | Texto principal |
| `--primary` | `#1a1a1a` | Ação primária e alto contraste |
| `--primary-foreground` | `#ffffff` | Texto sobre ação primária |
| `--secondary` | `#e0e0e0` | Superfície secundária |
| `--secondary-foreground` | `#1a1a1a` | Texto sobre superfície secundária |
| `--muted` | `#e0e0e0` | Superfície discreta |
| `--muted-foreground` | `#666666` | Texto de apoio e metadados |
| `--accent` | `#e9e9e9` | Destaque neutro e hover |
| `--accent-foreground` | `#1a1a1a` | Texto sobre destaque neutro |
| `--border` | `#cccccc` | Divisórias e contornos |
| `--input` | `#e0e0e0` | Contorno dos campos |
| `--ring` | `#1a1a1a` | Foco de teclado |
| `--chart-1` | `#2e8b57` | Estado positivo e série 1; não é a cor primária |
| `--chart-2` | `#4682b4` | Série de dados 2 |
| `--chart-3` | `#d2691e` | Avisos e série de dados 3 |
| `--chart-4` | `#8a2be2` | Série de dados 4 |
| `--chart-5` | `#a0522d` | Série de dados 5 |
| `--destructive` | `#ef4444` | Erro e ação destrutiva |
| `--destructive-foreground` | `#ffffff` | Texto de erro |
| `--sidebar` | `#ffffff` | Superfície de navegação lateral, se usada |
| `--sidebar-foreground` | `#1a1a1a` | Texto de navegação lateral |
| `--sidebar-primary` | `#1a1a1a` | Ação ativa da navegação |
| `--sidebar-primary-foreground` | `#ffffff` | Texto sobre ação ativa |
| `--sidebar-accent` | `#e9e9e9` | Hover de navegação |
| `--sidebar-accent-foreground` | `#1a1a1a` | Texto em hover |
| `--sidebar-border` | `#cccccc` | Divisórias da navegação |
| `--sidebar-ring` | `#1a1a1a` | Foco na navegação |
| `--radius` | `0rem` | Raio primitivo |
| `--spacing` | `.25rem` | Unidade de espaçamento |
| `--font-sans` | `Clash Display, ui-sans-serif, sans-serif, system-ui` | Família geral da interface |
| `--font-mono` | `Geist Mono, ui-monospace, monospace` | Família monoespaçada |
| `--font-serif` | `Zodiak, ui-serif, serif` | Família para ênfases especiais |
| `--shadow-blur` / `--shadow-spread` | `0px` / `0px` | Primitivos de sombra |
| `--shadow-color` / `--shadow-opacity` | `#000000` / `0` | Cor e opacidade primitivas |
| `--shadow-offset-x` / `--shadow-offset-y` | `0px` / `.125rem` | Deslocamento primitivo |
| `--letter-spacing` | `0em` | Espaçamento tipográfico padrão |

### Tema escuro

Os tokens escuros são definidos para permitir evolução futura. A aplicação ainda não oferece um controle para alternar o tema; não apresente a alternância como funcional até existir uma preferência acessível e testada.

| Token | Valor | Token | Valor |
|---|---|---|---|
| `--background` | `#10100E` | `--foreground` | `#FFFFE3` |
| `--card` | `#10100E` | `--card-foreground` | `#FFFFE3` |
| `--popover` | `#10100E` | `--popover-foreground` | `#FFFFE3` |
| `--primary` | `#FFFFE3` | `--primary-foreground` | `#10100E` |
| `--secondary` | `#606055` | `--secondary-foreground` | `#FFFFE3` |
| `--muted` | `#10100E` | `--muted-foreground` | `#8C8C7D` |
| `--accent` | `#8C8C7D` | `--accent-foreground` | `#1a1a1a` |
| `--border` | `#606055` | `--input` | `#606055` |
| `--ring` | `#FFFFE3` | `--destructive` | `#ef4444` |
| `--destructive-foreground` | `#FFFFE3` | `--chart-1` | `#2e8b57` |
| `--chart-2` | `#4682b4` | `--chart-3` | `#d2691e` |
| `--chart-4` | `#8a2be2` | `--chart-5` | `#a0522d` |
| `--sidebar` | `#1a1a1a` | `--sidebar-foreground` | `#f5f5f5` |
| `--sidebar-primary` | `#f5f5f5` | `--sidebar-primary-foreground` | `#1a1a1a` |
| `--sidebar-accent` | `#303030` | `--sidebar-accent-foreground` | `#f5f5f5` |
| `--sidebar-border` | `#404040` | `--sidebar-ring` | `#f5f5f5` |
| `--radius` | `0rem` | `--spacing` | `.25rem` |
| `--font-sans` | `Clash Display, ui-sans-serif, sans-serif, system-ui` | `--font-mono` | `Geist Mono, ui-monospace, monospace` |
| `--font-serif` | `Zodiak, ui-serif, serif` | `--letter-spacing` | `0em` |
| `--shadow-blur` / `--shadow-spread` | `0px` / `0px` | `--shadow-color` | `#000000` |
| `--shadow-opacity` | `0` | `--shadow-offset-x` / `--shadow-offset-y` | `0px` / `.125rem` |

### Uso semântico

- Preto e branco definem as ações principais e a identidade visual da interface. Verde (`--chart-1`) fica restrito a estados positivos e gráficos; não o use como fundo de botão primário ou navegação ativa.
- Laranja (`--chart-3`) indica atenção, prazo próximo e alerta relevante.
- Vermelho (`--destructive`) fica reservado para falhas e ações destrutivas.
- Azul, roxo e marrom são cores categóricas para gráficos. Não os distribua como decoração.
- Use `--foreground` e `--muted-foreground` para texto; confirme contraste suficiente em cada superfície.
- Transparências de vidro devem preservar a legibilidade sobre superfícies claras e neutras.

## 4. Tipografia

| Papel | Família | Aplicação |
|---|---|---|
| Uso geral e títulos | Clash Display | Navegação, formulários, botões, títulos e leitura geral |
| Dados técnicos | Geist Mono | Códigos PNCP, datas compactas, kickers e metadados |
| Textos especiais | Zodiak | Ênfase editorial pontual, especialmente em palavras ou frases curtas em itálico |

Pesos de Clash Display: 400–450 para leitura corrente; 500 para títulos e ênfase; 550–600 para ações e destaques curtos. Evite aplicar 700 em grandes blocos ou frases longas: a família tem presença visual forte. Zodiak deve ficar restrita a trechos especiais e curtos, geralmente em itálico. Geist Mono atende dados e metadados. As fontes Clash Display e Zodiak são servidas localmente a partir de `public/fonts`; use fallbacks `ui-sans-serif`, `ui-serif` e `ui-monospace`. Não use caixa alta em parágrafos ou textos longos.

## 5. Forma, espaço e superfícies

- Unidade de espaçamento: `--spacing: .25rem` (4 px). Priorize múltiplos de 4 px.
- O token primitivo `--radius: 0rem` mantém a linguagem geométrica do tema fornecido. Componentes de identidade, como o dock e pílulas de estado, podem ter cantos próprios para comunicar agrupamento.
- Contornos estruturais usam `--border`; evite bordas mais escuras que o conteúdo principal.
- Sombras são discretas e neutras. Não use brilho verde intenso em cartões ou controles.
- O efeito glassmorphism usa branco translúcido, blur moderado, reflexo interno discreto e uma borda leve. Reserve-o para cabeçalho, dock, cartões de resumo, painéis, busca e cartões de oportunidade.
- Preserve superfícies opacas quando houver dados densos, texto longo ou formulário que exija foco.
- Use fundo liso `--background`. Não aplique gradientes, manchas de cor, ruído ou textura decorativa no fundo da plataforma.
- Use vidro fosco com moderação, em cartões pontuais e navegação, sempre com contraste suficiente.
- O tema claro usa fundo `#F2F1ED` e cartões `#FAF9F6`, evitando grandes planos de branco puro. O controle “Conforto visual” aplica uma variante mais quente e menos luminosa (`#EAE7DF` / `#F3F0E8`), persistida localmente no navegador; a preferência não é vinculada à conta.

Classes existentes: `.glass-panel`, `.glass-panel-strong`, `.glass-card`, `.glass-input`, `.ios-dock` e `.btn-emerald`. Prefira essas classes antes de criar variações locais.

## 6. Componentes e padrões

### Cabeçalho e navegação

O cabeçalho superior apresenta marca, empresa ativa, busca rápida ampliada e conta autenticada. O estado da coleta PNCP aparece junto aos resultados quando afeta sua confiabilidade, sem ocupar um cartão permanente no cabeçalho. O dock inferior central contém Radar, Explorar, Acompanhadas, Perfil e Alertas. O item ativo tem alto contraste e nome visível; badges aparecem apenas quando ajudam a entender contagem ou novidade.

Não mova esses controles sem atualizar acessibilidade por teclado, navegação por hash e comportamento em telas estreitas.

### Login

A tela de login combina um painel claro com o formulário e um painel ilustrativo. A marca fica centralizada no painel do formulário. Mantenha a hierarquia tipográfica equilibrada, o título com peso moderado e o formulário com contraste suficiente. O painel ilustrativo deve priorizar uma frase curta e a silhueta correta de Goiás, derivada do GeoJSON local; evite acumular legendas, selos e cartões de benefício. O formulário vem primeiro na ordem de leitura e no mobile. Preserve os campos de e-mail e senha, labels persistentes, autofill e feedback de erro. A ação principal usa fundo `--primary`, texto `--primary-foreground`, rótulo curto centrado e sem seta decorativa. Não apresente criação de conta ou recuperação de senha enquanto esses fluxos não existirem.

A ilustração mostra a silhueta de Goiás e um marcador de Goiânia. Ela é decorativa, não um mapa para análise geográfica; mantenha o texto alternativo e não dependa da cor para transmitir a informação.

### Radar e oportunidades

- Use cartões com título do objeto, modalidade, situação, órgão/local, valor, datas e ações.
- Deixe o objeto como conteúdo mais destacado e metadados em segundo plano.
- Exiba sinais de correspondência e exclusões em etiquetas textuais distintas.
- Não infira volume ou aderência quando a resposta não fornecer dados suficientes; mostre “Não informado” ou “—”.
- Inclua acesso à ficha e à fonte oficial sem falsificar links ou status.

### Cartões com visual de pasta

- O visual de pasta de vidro é uma linguagem de superfície para cartões de indicadores; ele não representa arquivos nem ações de abrir, adicionar ou organizar conteúdo.
- Use uma aba discreta no fundo, uma frente translúcida clara e conteúdo com rótulo, valor e contexto útil.
- Mantenha o cartão estático, sem animação de abertura, menu ou elementos decorativos de papel que não acrescentem informação.
- Use ícones Tabler outline pequenos e consistentes para identificar indicadores e navegação.

### Busca

A barra de Explorar mantém todos os filtros atuais, incluindo município e situação em seletores personalizados reutilizáveis (`data-custom-select`) e intervalo de abertura em calendários personalizados no tema. A lista dos 246 municípios é derivada do GeoJSON local. O seletor oferece navegação por teclado e busca textual quando marcado como pesquisável. Calendários exibem seis semanas completas, têm controles de mês sempre visíveis, aceitam teclado, Escape e datas existentes nos links. Popovers são posicionados em uma camada sobre a página para não serem cortados por formulários ou superfícies com blur. Sugestões rápidas são botões de preenchimento e não substituem a busca manual. Estados sem consulta, sem resultados, carregamento e falha devem ter mensagens diferentes.

### Perfil de interesse

O nome do perfil é texto livre; critérios de catálogo, município, situação e prazo usam opções controladas. CATMAT/CATSER pode permanecer vazio para busca ampla. Diagnóstico lateral resume critérios atuais, não promete cobertura absoluta. Exclusões são opcionais e devem ficar visualmente separadas dos critérios de inclusão.

### Alertas e preferências

Separar configurações de e-mail do histórico de alertas. Mostrar que o envio depende da configuração do serviço de e-mail. Diferenciar lido/não lido, alertas críticos e estados vazios sem depender apenas de cor.

### Formulários, botões e feedback

- Labels visíveis e persistentes; placeholders servem apenas como exemplo.
- Campo de foco tem `--ring` visível em navegação por teclado.
- Botão primário usa `--primary` (`#1a1a1a`) e `--primary-foreground` (`#ffffff`); ações secundárias usam superfície e contorno. Reserve `--chart-1` (`#2e8b57`) para marca, sucesso e indicadores, sem usá-lo como fundo de ação primária.
- Botões destrutivos usam `--destructive` e pedem confirmação quando a ação não puder ser desfeita.
- Toast é breve, específico e dispensável. Erros de formulário também ficam junto do campo ou da ação que falhou.
- Estados desabilitados continuam legíveis e não parecem interativos.

## 7. Layout responsivo

- **Acima de 1100 px:** cabeçalho completo, formulários em colunas quando útil, listagens em duas colunas e painel diagnóstico sticky.
- **761–1100 px:** reduzir espaços e esconder dados auxiliares do cabeçalho antes de comprimir controles.
- **Até 760 px:** uma coluna, dock compacto com rótulos ainda legíveis, formulários em largura total e nenhuma ação escondida.
- **Até 600 px:** login empilhado com formulário antes da ilustração; reduza elementos decorativos e mantenha rolagem normal.

Evite rolagem horizontal. Teste nomes de empresa longos, e-mails longos, títulos extensos de editais, zoom de 200% e conteúdo vazio.

## 8. Movimento e acessibilidade

- Use transições curtas e suaves em hover, foco e estado ativo; mantenha a interface estável durante carregamentos e mudanças de tela. Respeite `prefers-reduced-motion` sem movimento obrigatório para entender o estado.
- Use foco visível, ordem de tabulação natural, labels explícitos e alvos de toque confortáveis.
- Ícones decorativos usam `aria-hidden="true"`; controles com ícone têm nome acessível.
- Mensagens de erro e toasts usam regiões `role="alert"` ou `role="status"` conforme urgência.
- Não use cor como único indicador de situação; associe texto ou símbolo.
- Preserve contraste de texto e foco em superfícies translúcidas e opacas.

## 9. Tom de voz e conteúdo

Escreva em português do Brasil, com frases curtas e verbos concretos. Prefira “A coleta foi parcial” a “Ocorreu uma inconsistência”. Use datas, valores e números no padrão local. Explique a consequência para o usuário e a próxima ação disponível.

Evite garantias de resultado ou expressões que sugiram que o LicitaGoiás substitui o edital. Em pontos de decisão, lembre que prazos e condições devem ser confirmados na fonte oficial.

## 10. Implementação e manutenção

- A aplicação atual usa HTML, CSS e JavaScript sem React, Tailwind ou shadcn. Não migre frameworks para aplicar o visual dos cartões; mantenha IDs, eventos e o comportamento de negócio atuais.
- Os ícones usam a webfont oficial Tabler Icons, fixada na versão 3.49.0 em jsDelivr. Use classes `ti ti-nome-do-icone`, tamanho herdado do contexto e `aria-hidden="true"` para ícones decorativos. Ícones sem texto precisam de nome acessível no controle.
- Os tokens `--color-*` espelham o mapeamento da paleta para facilitar consistência; não adicione diretivas `@theme` que o navegador não processe.
- Declare cores em tokens, não espalhe novos hexadecimais por componentes.
- Não remova IDs, nomes de campos, handlers, atributos de acessibilidade ou integrações de API ao refatorar a aparência.
- Faça mudanças estruturais mantendo estados carregando, vazio, preenchido e erro.
- Atualize a versão de cache de `app.css`/`app.js` ao alterar assets estáticos.
- Verifique sintaxe, IDs, navegação por teclado e layouts desktop/mobile após mudanças de interface.

## 11. Referências e arquivos

- Paleta implementada em `src/licitagoias/api/static/app.css`.
- Telas e tokens semânticos em `src/licitagoias/api/static/index.html`.
- Interações e renderização em `src/licitagoias/api/static/app.js`.
- A silhueta do login é derivada do GeoJSON local `public/geojson/geojs-52-mun.json`, que contém os polígonos dos municípios goianos. O contorno externo é gerado pelo script `scripts/generate_goias_map.py` e salvo em `src/licitagoias/api/static/goias-map.svg`.
- A lista de municípios de Explorar também é derivada desse GeoJSON e gerada em `src/licitagoias/api/static/municipalities-go.json` pelo mesmo script.
