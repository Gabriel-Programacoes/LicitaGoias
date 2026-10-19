# Prompt de Migração de UI/UX para o Codex — Portal LicitaGoiás (Glassmorphism + Dock Estilo iPhone)

Copie o prompt completo abaixo e envie para o **Codex** (ou salve como `MIGRATION_PROMPT.md` na raiz do seu repositório e peça ao agente para executá-lo).

---

## Prompt para Copiar e Colar no Codex

```markdown
# Tarefa: Refatoração Completa da Interface do Portal LicitaGoiás para Design Glassmorphism Moderno com Dock Central Estilo iPhone (iOS)

Você é um Engenheiro Front-End Sênior e Especialista em Design Systems. Sua missão é migrar a interface atual do portal **LicitaGoiás** para uma nova arquitetura visual baseada em **Glassmorphism moderno, otimizado e eficiente**, substituindo a barra lateral fixa tradicional por uma **Barra de Contexto Superior Flutuante** e um **Menu Central Inferior Flutuante estilo iPhone/iOS (Floating Glass Dock)**.

## 1. Regras Inegociáveis de Preservação de Código e Negócio
1. **Não quebre a lógica existente**: Preserve 100% das rotas, chamadas de API (PNCP, perfis, acompanhadas, alertas, autenticação), gerenciamento de estado, hooks, nomes de campos de formulário, validações e regras de negócio já implementadas no projeto.
2. **Apoie tanto o Estado Vazio quanto o Estado Populado**: Todas as telas devem renderizar com perfeição tanto quando não há dados (estados vazios originais do sistema) quanto quando há licitações, perfis e alertas carregados da API.
3. **Mantenha a Paleta Oficial do Tema Claro**: Utilize rigorosamente os tokens de cor do tema claro do portal como base cromática para as camadas translúcidas.

---

## 2. Tokens de Cores, Tipografia e Superfícies Glassmorphism (CSS Variables)

Adicione ou atualize no arquivo CSS global do projeto as seguintes variáveis e classes utilitárias:

```css
:root {
  /* Paleta Base do Tema Claro Original */
  --bg-primary: #f5f5ef;
  --bg-secondary: #f0f1e9;
  --bg-elevated: #fbfcf8;
  --surface-tint: #e0e8dc;
  --border-structural: #dfe4da;
  --ink-primary: #101816;
  --ink-secondary: #1e2b28;
  --ink-muted: #5e6b65;
  --brand-emerald: #0a4a3a;
  --brand-emerald-hover: #0d5e4a;
  --brand-mint-glow: #defcf3;
  --accent-dot: #d97724;
  --accent-warm: #ffe8b7;

  /* Camadas de Vidro (Glassmorphism Otimizado) */
  --glass-surface: rgba(255, 255, 255, 0.66);
  --glass-surface-strong: rgba(251, 252, 248, 0.84);
  --glass-surface-subtle: rgba(240, 241, 233, 0.58);
  --glass-pill: rgba(224, 232, 220, 0.72);
  --glass-border-light: rgba(255, 255, 255, 0.88);
  --glass-border-outer: rgba(10, 74, 58, 0.10);
  --glass-shadow-sm: 0 4px 20px -2px rgba(16, 24, 22, 0.05), 0 1px 3px rgba(16, 24, 22, 0.03);
  --glass-shadow-md: 0 14px 36px -6px rgba(16, 24, 22, 0.07), 0 2px 8px -1px rgba(10, 74, 58, 0.04);
  --glass-shadow-dock: 0 22px 55px -8px rgba(16, 24, 22, 0.16), 0 6px 18px -3px rgba(10, 74, 58, 0.08), inset 0 1.5px 0 rgba(255, 255, 255, 0.95);
}

/* Iluminação Ambiente de Fundo para Refração Óptica Real do Blur */
.ambient-canvas {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
  background:
    radial-gradient(circle at 14% 12%, rgba(224, 232, 220, 0.85) 0%, transparent 45%),
    radial-gradient(circle at 86% 18%, rgba(222, 252, 243, 0.65) 0%, transparent 42%),
    radial-gradient(circle at 75% 82%, rgba(255, 232, 183, 0.38) 0%, transparent 48%),
    radial-gradient(circle at 22% 85%, rgba(224, 232, 220, 0.70) 0%, transparent 50%),
    linear-gradient(180deg, #f7f8f3 0%, #f5f5ef 52%, #f0f1e9 100%);
}

.ambient-grid {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: radial-gradient(rgba(10, 74, 58, 0.055) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: radial-gradient(ellipse at center, black 45%, transparent 90%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 45%, transparent 90%);
}

/* Painéis e Cartões Glassmorphism */
.glass-panel {
  background: var(--glass-surface);
  backdrop-filter: blur(22px) saturate(165%);
  -webkit-backdrop-filter: blur(22px) saturate(165%);
  border: 1px solid var(--glass-border-outer);
  box-shadow: var(--glass-shadow-md), inset 0 1px 0 var(--glass-border-light);
  border-radius: 24px;
}

.glass-panel-strong {
  background: var(--glass-surface-strong);
  backdrop-filter: blur(26px) saturate(180%);
  -webkit-backdrop-filter: blur(26px) saturate(180%);
  border: 1px solid rgba(10, 74, 58, 0.12);
  box-shadow: var(--glass-shadow-md), inset 0 1.5px 0 rgba(255, 255, 255, 0.95);
  border-radius: 24px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(16px) saturate(150%);
  -webkit-backdrop-filter: blur(16px) saturate(150%);
  border: 1px solid rgba(10, 74, 58, 0.09);
  box-shadow: var(--glass-shadow-sm), inset 0 1px 0 rgba(255, 255, 255, 0.85);
  border-radius: 20px;
  transition: all 0.24s cubic-bezier(0.16, 1, 0.3, 1);
}

.glass-card:hover {
  background: rgba(255, 255, 255, 0.82);
  border-color: rgba(10, 74, 58, 0.22);
  transform: translateY(-2px);
  box-shadow: 0 18px 40px -10px rgba(10, 74, 58, 0.10), 0 4px 12px rgba(16, 24, 22, 0.04), inset 0 1px 0 #ffffff;
}

.glass-input {
  background: rgba(251, 252, 248, 0.78);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(10, 74, 58, 0.14);
  box-shadow: inset 0 1px 2px rgba(16, 24, 22, 0.03), 0 1px 0 rgba(255, 255, 255, 0.8);
  color: var(--ink-primary);
  border-radius: 12px;
  transition: all 0.18s ease;
}

.glass-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.96);
  border-color: var(--brand-emerald);
  box-shadow: 0 0 0 3.5px rgba(10, 74, 58, 0.12);
}

/* Botões Primários e de Vidro */
.btn-emerald {
  background: linear-gradient(180deg, #0d5946 0%, #0a4a3a 100%);
  color: #ffffff;
  border: 1px solid #063529;
  border-radius: 12px;
  box-shadow: 0 6px 16px -3px rgba(10, 74, 58, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.22);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-emerald:hover {
  background: linear-gradient(180deg, #0f6852 0%, #0c5442 100%);
  transform: translateY(-1px);
}

.btn-glass {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: var(--ink-primary);
  border: 1px solid rgba(10, 74, 58, 0.15);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(16, 24, 22, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transition: all 0.2s ease;
}

.btn-glass:hover {
  background: rgba(224, 232, 220, 0.75);
  border-color: rgba(10, 74, 58, 0.28);
  color: var(--brand-emerald);
}
```

### Hierarquia Tipográfica
- **Títulos Principais (`h1`)**: Fonte `Plus Jakarta Sans` ou `Inter` (700/800), tamanho `clamp(2rem, 4vw, 3rem)`, cor `--ink-primary`, sempre finalizados com o ponto colorido de assinatura `<span style="color: var(--accent-dot)">.</span>` (ex.: `Para sua empresa.`, `Explorar oportunidades.`, `Acompanhadas.`, `Perfil de interesse.`, `Alertas.`).
- **Kickers / Badges Superiores**: Fonte `JetBrains Mono` (uppercase, `letter-spacing: 0.08em`, `font-size: 11px`), dentro de uma pílula translúcida `#e0e8dc` com texto `--brand-emerald`.
- **Corpo e Controles**: Fonte `Inter` (400/500/600).

---

## 3. Reestruturação do App Shell (Layout Principal)

Remova a barra lateral (`sidebar`) esquerda fixa tradicional e substitua-a por três elementos coordenados:

### A. Barra Superior Flutuante de Contexto (`<header>`)
Fixada no topo (`sticky top-0 z-40`), centralizada (`max-w-7xl mx-auto`), usando `.glass-panel-strong`:
1. **Esquerda**:
   - Logo **licita**goias: ícone quadrado arredondado verde `#0a4a3a` com `L↗` em branco/menta + texto `licita` (bold) `goias` (regular).
   - Breadcrumb dinâmico abaixo ou ao lado em fonte mono: `LICITAGOIAS / [NOME DA SEÇÃO ATIVA]`.
   - Pílula do Espaço de Trabalho: `ESPAÇO DE TRABALHO: [Nome da Empresa]` (ex.: `Empresa de Teste`).
2. **Centro**:
   - Pílula interativa da **Fonte PNCP**: ponto verde pulsante (`#22c55e`) + título `Fonte PNCP` + subtítulo dinâmico `Coleta concluída · [Data da última coleta]`.
3. **Direita**:
   - Atalho de busca rápida (redireciona/foca na busca de `Explorar`).
   - E-mail do usuário autenticado (`teste@gmail.com`), avatar circular em `#dce5d7` com iniciais (`TE`) e botão/ação de `Sair da conta`.

### B. Menu Central Flutuante Estilo iPhone / iOS (`<nav class="ios-dock-wrapper">`)
Posicionado de forma fixa e centralizada na parte inferior da tela (`position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%); z-index: 50`), garantindo `padding-bottom: 7rem` no `<body>` para que nenhum conteúdo fique encoberto:

```css
.ios-dock-wrapper {
  position: fixed;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 50;
  max-width: calc(100vw - 24px);
}

.ios-dock {
  background: rgba(251, 252, 248, 0.72);
  backdrop-filter: blur(30px) saturate(200%);
  -webkit-backdrop-filter: blur(30px) saturate(200%);
  border: 1px solid rgba(10, 74, 58, 0.13);
  box-shadow: var(--glass-shadow-dock);
  border-radius: 28px;
  padding: 7px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dock-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  border-radius: 20px;
  color: #2c3a35;
  font-weight: 500;
  font-size: 0.84rem;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  white-space: nowrap;
}

.dock-item:hover {
  background: rgba(224, 232, 220, 0.65);
  color: var(--brand-emerald);
  transform: translateY(-4px) scale(1.03);
}

.dock-item.active {
  background: var(--brand-emerald);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 8px 20px -4px rgba(10, 74, 58, 0.42), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}
```

- **Itens obrigatórios no Dock**:
  1. `Para minha empresa` (ícone de estrela/radar + badge numérico de oportunidades encontradas)
  2. `Explorar` (ícone de bússola/lupa)
  3. `Acompanhadas` (ícone de marcador/favorito + badge numérico de licitações acompanhadas)
  4. `Perfil de interesse` (ícone de ajustes/sliders)
  5. `Alertas` (ícone de sino + indicador de status)
- Em telas mobile (`< 640px`), exiba os ícones e os badges de forma compacta, mantendo os rótulos visíveis em telas `sm:` ou superiores (ou via tooltip).

### C. Rodapé Institucional (`<footer>`)
Mantém a informação `LICITAGOIAS · AMBIENTE LOCAL`, o aviso legal `Dados de fonte pública. Confirme condições e prazos no edital oficial.` e o link `API / ESTADO ↗`.

---

## 4. Diretrizes de Layout para Cada uma das 5 Telas

### 1. Para minha empresa (`SELEÇÃO PERSONALIZADA`)
- **Hero Panel (`.glass-panel`)**:
  - Kicker em pílula: `SELEÇÃO PERSONALIZADA · [STATUS DO PERFIL ATIVO OU SEM PERFIL]`.
  - Título: `Para sua empresa.` + subtítulo `Oportunidades com sinais claros de correspondência.`
  - Ações no topo direito: botão `Ajustar perfil ↗` (navega para Perfil de Interesse) e botão de atualizar/recarregar (`↻`).
  - Se houver oportunidades, exiba uma faixa de **Bento Cards de Resumo (KPIs)** dentro do painel principal (Total de oportunidades no radar, Volume estimado, Aderência média, Aberturas próximas).
- **Listagem / Grid de Oportunidades**:
  - Barra `.glass-panel` com chips de filtro rápido e contador `X oportunidades encontradas`.
  - Grid de 2 colunas em desktop (`grid-cols-1 lg:grid-cols-2 gap-4`) usando `.glass-card` para cada edital, destacando: pílula de correspondência (`#defcf3` com texto `#0a4a3a`), modalidade, código PNCP, título do objeto, órgão + município, tags CATMAT/CATSER, valor estimado, data de abertura e ações (`Acompanhar` e `Edital ↗`).
- **Estado Vazio (quando sem perfil ou sem resultados)**:
  - Card central `.glass-panel` com ícone, contador `— oportunidades encontradas`, mensagem `Configure seu primeiro perfil para receber uma seleção personalizada.` e botão `.btn-emerald` `Criar perfil ↗`.

### 2. Explorar oportunidades (`BASE PÚBLICA`)
- **Header + Barra de Comando Unificada (`.glass-panel`)**:
  - Kicker `BASE PÚBLICA`, título `Explorar oportunidades.`, subtítulo `Pesquise pelo objeto, órgão ou modalidade.`
  - Barra de busca horizontal em vidro (`.glass-panel-strong`) organizada em grid responsivo contendo todos os filtros originais:
    1. Input de busca textual (`Ex.: manutenção de computadores`) com ícone de lupa.
    2. Campo/Select `Município`.
    3. Campo/Select `Situação`.
    4. Campo de data `Abertura desde` (`01/01/2026`).
    5. Campo de data `Abertura até` (`31/10/2026`).
    6. Botão primário `.btn-emerald` `Buscar ↗`.
  - Chips rápidos de sugestões de busca logo abaixo da barra.
- **Resultados**:
  - Barra de contagem `X resultados na base` + ordenação.
  - Lista de cartões `.glass-card` horizontais ou estado vazio `Digite um termo ou município para pesquisar.` quando nenhuma busca estiver ativa.

### 3. Acompanhadas (`MONITORAMENTO DA EMPRESA`)
- **Header (`.glass-panel`)**:
  - Kicker `MONITORAMENTO DA EMPRESA`, título `Acompanhadas.`, subtítulo `O histórico começa no momento em que você acompanha.`
- **Lista de Monitoramento**:
  - Cartões `.glass-card` exibindo status de monitoramento PNCP, órgão, município, valor, data da sessão, badge da última atualização detectada e botão para deixar de acompanhar ou abrir detalhes.
- **Estado Vazio**:
  - Card `.glass-panel` centralizado com a mensagem `Você ainda não acompanha oportunidades.` e atalho para `Explorar oportunidades ↗`.

### 4. Perfil de interesse (`CALIBRE SEU RADAR`)
- **Header (`.glass-panel`)**:
  - Kicker `CALIBRE SEU RADAR`, título `Perfil de interesse.`, subtítulo `Diga o que sua empresa fornece. Os termos negativos sempre têm prioridade.` e botão `+ Novo perfil` à direita.
- **Layout em 2 Colunas Assimétricas (`lg:grid-cols-12 gap-6`)**:
  - **Coluna Principal (8 colunas — `.glass-panel-strong`)**:
    - Campo `Nome deste perfil` (`Ex.: Tecnologia e suporte`).
    - Seção `Produtos e serviços` com badge `opcional` e indicador `Busca ampla` (quando sem itens) ou quantidade de filtros CATMAT ativos:
      - Sub-card `.glass-card` contendo o seletor `Catálogo` (`CATMAT · materiais` / `CATSER · serviços`), seletor de grupo (`Selecione grupo...`), botão `Adicionar item específico` e lista de chips dos itens adicionados.
      - Notas informativas de rodapé da seção (`Busca ampla: nenhum filtro CATMAT/CATSER será aplicado.` e `Fonte oficial: Compras.gov.br · CATMAT/CATSER...`).
    - Accordion/Details `.glass-card` expansível: `▸ Excluir produtos ou serviços específicos (opcional)`.
    - Linha dupla com os seletores `Município` (`Qualquer município da cobertura`) e `Prazo máximo para abertura` (`Sem limite`).
    - Botão de submissão `.btn-emerald` para salvar o perfil.
  - **Coluna Lateral Sticky (4 colunas — `.glass-panel`)**:
    - Card `Diagnóstico do Radar` resumindo em tempo real o nome do perfil em edição, cobertura geográfica, janela de abertura e status dos filtros CATMAT/CATSER.

### 5. Alertas (`ACOMPANHAMENTO E AVISOS`)
- **Header (`.glass-panel`)**:
  - Kicker `ACOMPANHAMENTO E AVISOS`, título `Alertas.`, subtítulo `Alterações em oportunidades que sua empresa acompanha.` e botão `Atualizar` à direita.
- **Layout em 2 Colunas (`lg:grid-cols-12 gap-6`)**:
  - **Coluna Esquerda (6 colunas — `.glass-panel-strong`) — Card `Notificações por e-mail`**:
    - Subtítulo `O envio fica sujeito à configuração do serviço de e-mail.`
    - Switch/Toggle estilo iOS para `Ativar notificações por e-mail` (mantendo o vínculo com o checkbox/estado original).
    - Grid de 2 colunas com `Resumo` (`Desativado`, `Diário`, etc.) e `Horário (0-23)` (`8`).
    - Campo `Fuso horário` (`America/Sao_Paulo`).
    - Switch/Toggle estilo iOS para `Receber alertas críticos imediatamente`.
    - Botão `.btn-emerald` `Salvar preferências ↗`.
  - **Coluna Direita (6 colunas — `.glass-panel`) — Histórico / Feed de Alterações**:
    - Lista de eventos recentes das oportunidades acompanhadas em `.glass-card`, ou o estado vazio `Ainda não há alterações em oportunidades acompanhadas.`

---

## 5. Plano de Execução Passo a Passo
1. **Inspeção**: Liste os arquivos de layout, estilos globais e páginas/rotas atuais do projeto para mapear onde cada uma das 5 telas está implementada.
2. **Estilos Globais**: Injete as variáveis CSS do tema claro, o fundo `.ambient-canvas` / `.ambient-grid`, as classes `.glass-panel`, `.glass-card`, `.glass-input`, `.ios-dock` e `.ios-switch` no CSS global.
3. **Layout Principal (Shell)**: Substitua a sidebar lateral pelo novo `<header>` flutuante superior e pelo `<nav class="ios-dock-wrapper">` centralizado na parte inferior, mantendo os links/rotas e ações de logout e status PNCP funcionando.
4. **Refatoração das Views**: Atualize o JSX/HTML/Template das 5 views (`Para minha empresa`, `Explorar`, `Acompanhadas`, `Perfil de interesse`, `Alertas`) aplicando a nova estrutura de Bento Cards em vidro sem remover nenhum `id`, `name`, `onChange`, `onSubmit` ou integração de dados existente.
5. **Validação**: Execute o build/typecheck do projeto e verifique se não há erros de compilação, imports quebrados ou regressões funcionais.
```
