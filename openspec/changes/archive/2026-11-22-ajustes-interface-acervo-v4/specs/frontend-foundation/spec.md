# Spec Delta

## MODIFIED Requirements

### Requirement: Caixa Perfil fecha por teclado e interação externa
A caixa Perfil e a caixa Acessibilidade MUST fechar por Escape e por interação externa. Abrir uma delas MUST fechar a outra; Escape devolve o foco ao controle que abriu a caixa fechada.

#### Scenario: Abrir e fechar pelo teclado
- **WHEN** pessoa alcança Perfil por teclado, expande a caixa e pressiona Escape
- **THEN** a caixa fecha e o foco retorna ao controle Perfil

#### Scenario: Fechar Acessibilidade por Escape
- **WHEN** pessoa expande Acessibilidade e pressiona Escape
- **THEN** Acessibilidade fecha e o foco retorna ao controle Acessibilidade

#### Scenario: Fechar ao clicar fora
- **WHEN** qualquer uma das caixas está expandida e pessoa ativa outro ponto da página
- **THEN** a caixa fecha sem impedir a ação no destino

#### Scenario: Abrir uma caixa fecha a outra
- **WHEN** Perfil ou Acessibilidade está aberta e pessoa abre a outra caixa
- **THEN** somente a caixa recém-aberta permanece expandida

### Requirement: Visitantes podem ajustar a aparência
O cabeçalho MUST oferecer aos visitantes os controles globais de aparência, separados das ações de Perfil para entrar ou cadastrar-se.

#### Scenario: Controles de aparência no cabeçalho visitante
- **WHEN** visitante abre Acessibilidade
- **THEN** pode ajustar tamanho da fonte, alto contraste, redução de movimento e tema claro ou escuro

#### Scenario: Controles de aparência no Perfil visitante
- **WHEN** visitante abre o controle Acessibilidade
- **THEN** pode ajustar tamanho da fonte, alto contraste, redução de movimento e modo escuro, além de abrir Entrar ou Cadastrar-se pelo controle Perfil

#### Scenario: Perfil do visitante
- **WHEN** visitante abre Perfil
- **THEN** encontra Entrar e Cadastrar-se sem controles de aparência duplicados

### Requirement: Campos suportam alinhamento e autofill seguros
Campos de formulário MUST usar controles nativos estilizados de forma compartilhada, com uma borda, altura mínima de 44 px, texto centralizado verticalmente, foco visível e autofill compatível com os tokens do tema.

#### Scenario: Texto normal ou preenchido automaticamente
- **WHEN** pessoa digita ou recebe autofill em campo de texto
- **THEN** o texto fica centralizado verticalmente, sem corte nem faixa azulada, e caret e fundo seguem os tokens do tema

#### Scenario: Formulário de edição sem caixa dupla
- **WHEN** formulário de edição contém campo de texto, textarea ou select
- **THEN** somente o contêiner externo possui borda e foco, sem borda interna duplicada

#### Scenario: Formulários sem componentes de campo Radix
- **WHEN** pessoa usa campos de texto, área de texto, seleção ou caixas de seleção
- **THEN** os controles são elementos HTML nativos com uma borda, altura mínima de 44 px e rótulo associado

#### Scenario: Foco visível em campo nativo
- **WHEN** pessoa navega por teclado até um campo
- **THEN** o campo mostra contorno de foco visível de 3 px

#### Scenario: Campo oculto de formulário
- **WHEN** formulário envia identificador de registro não editável
- **THEN** o identificador é enviado como campo `hidden` e não aparece como barra visual

#### Scenario: Categoria em caixa de seleção
- **WHEN** pessoa usa uma categoria em formulário
- **THEN** caixa e rótulo ficam na mesma linha, centrados e dentro de alvo de pelo menos 44 px

### Requirement: Identificadores usam emojis decorativos
Marca, navegação, ações e selos MUST usar o símbolo previsto no guia, com texto curto visível. O emoji decorativo fica em elemento próprio com `aria-hidden="true"`; cada botão também fornece `title` e `aria-label` descritivos.

#### Scenario: Emoji decorativo em rótulo
- **WHEN** interface apresenta marca, destino, seção, selo ou botão com emoji
- **THEN** o emoji fica em elemento próprio com `aria-hidden="true"` antes do texto correspondente

#### Scenario: Ação com texto acessível
- **WHEN** pessoa encontra um botão de ação
- **THEN** encontra um emoji e um texto de uma a três palavras, com `title` e `aria-label` correspondentes

#### Scenario: Ações distintas usam emojis exclusivos
- **WHEN** duas ações distintas aparecem no site
- **THEN** cada uma usa emoji exclusivo conforme o dicionário documentado

#### Scenario: Confirmação destrutiva inline
- **WHEN** pessoa confirma ou cancela uma ação destrutiva
- **THEN** os controles oferecem “✅ Sim, desativar” e “❌ Não”

## ADDED Requirements

### Requirement: Cabeçalho separa Acessibilidade do Perfil
O cabeçalho MUST apresentar controles de Acessibilidade e Perfil independentes, disponíveis conforme o perfil autenticado e sem alterar a autorização real da sessão.

#### Scenario: Controles para visitante
- **WHEN** visitante consulta qualquer página
- **THEN** vê Acessibilidade e Entrar, e Entrar oferece acesso a Entrar e Cadastrar-se

#### Scenario: Controles para pessoa autenticada
- **WHEN** pessoa autenticada consulta qualquer página
- **THEN** vê Acessibilidade e Perfil com nome, e Perfil apresenta e-mail, cargo e Sair

#### Scenario: Seletor de visão do admin
- **WHEN** admin real abre Perfil
- **THEN** pode escolher Administrador, Bibliotecário ou Estudante, vê a visão ativa e pode voltar à visão de admin

#### Scenario: Perfil não admin tenta usar visão administrativa
- **WHEN** estudante ou bibliotecário abre Perfil
- **THEN** não vê controles de visão administrativa

#### Scenario: Uso em tela estreita
- **WHEN** pessoa usa os controles em viewport de 360 px
- **THEN** Perfil e Acessibilidade permanecem identificáveis e operáveis sem sobreposição ou corte de conteúdo

### Requirement: Variantes de botões mantêm contraste acessível
Botões primários, secundários, de perigo, de aviso e sutis MUST manter texto e fundo próprios por tema, com estados hover, foco e desabilitado legíveis.

#### Scenario: Contraste de cada variante em ambos os temas
- **WHEN** botão de qualquer variante é exibido em tema claro ou escuro
- **THEN** o contraste entre texto e fundo é de pelo menos 4,5:1

#### Scenario: Estados interativos
- **WHEN** botão recebe hover, foco ou estado desabilitado em qualquer tema
- **THEN** seu estado continua distinguível e o foco permanece visível
