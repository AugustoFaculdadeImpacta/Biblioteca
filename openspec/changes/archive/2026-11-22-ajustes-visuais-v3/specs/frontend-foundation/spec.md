# Spec Delta

## ADDED Requirements

### Requirement: Campos suportam alinhamento e autofill seguros
O sistema MUST centralizar verticalmente o conteúdo digitado em campos de pelo menos 44 px e aplicar os tokens do tema ao caret e ao autofill sem cortar texto.

#### Scenario: Texto normal ou preenchido automaticamente
- **WHEN** pessoa digita ou recebe autofill em campo de texto
- **THEN** o texto fica centralizado verticalmente, sem corte, e caret e fundo seguem os tokens do tema

#### Scenario: Formulário de edição sem caixa dupla
- **WHEN** formulário de edição contém campo de texto, textarea ou select
- **THEN** somente o contêiner externo possui borda e foco

#### Scenario: Categoria em caixa de seleção
- **WHEN** pessoa usa uma categoria em formulário
- **THEN** caixa e rótulo ficam na mesma linha, centrados e dentro de alvo de pelo menos 44 px

### Requirement: Botões primários têm contraste no tema escuro
O sistema MUST aplicar aos botões primários no tema escuro fundo claro da marca e texto escuro com contraste adequado.

#### Scenario: Contraste dos botões primários
- **WHEN** tema escuro está ativo
- **THEN** o texto primário mantém contraste de pelo menos 4,5:1 e o botão mantém contraste de pelo menos 3:1 sobre o painel

### Requirement: Interruptor de tema anuncia seu destino efetivo
O interruptor MUST mostrar a ação oposta ao tema efetivo atual e manter o estado efetivo após recarregar.

#### Scenario: Tema claro ativo
- **WHEN** tema claro está ativo
- **THEN** o controle mostra “🌙 Modo escuro” e `aria-checked` indica tema escuro desativado

#### Scenario: Tema escuro ativo ou herdado
- **WHEN** tema escuro está explícito ou herdado de `prefers-color-scheme`
- **THEN** o controle mostra “☀️ Modo claro” e acompanha todas as rotas

### Requirement: Identificadores usam emojis decorativos
Marca, menus, perfil, seções, selos e ações MUST usar emojis em elementos próprios com `aria-hidden="true"`, preservando rótulos textuais para leitores de tela.

#### Scenario: Emoji decorativo em rótulo
- **WHEN** interface apresenta marca, destino, seção, selo ou botão com emoji solicitado
- **THEN** o emoji fica em `<span aria-hidden="true">` antes do texto correspondente

### Requirement: Interface usa animações leves e preferências de movimento
A interface MUST animar entrada, cascata, interação e tema sem deslocamento de layout e MUST desativar animações decorativas por preferência do usuário.

#### Scenario: Entrada e interação leves
- **WHEN** página, cartão, menu ou capa é exibido
- **THEN** usa entrada curta, cascata limitada, elevação ou zoom leves e transição curta sem layout shift

#### Scenario: Movimento reduzido
- **WHEN** `prefers-reduced-motion: reduce` está ativo ou `.a11y-reduce-motion` está presente
- **THEN** todas as regras de animação decorativa são desativadas

#### Scenario: Transição de tema
- **WHEN** pessoa alterna tema
- **THEN** fundo e texto fazem transição de até 200 ms

