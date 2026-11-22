# Spec Delta

## MODIFIED Requirements

### Requirement: Controles interativos exibem foco visível
O sistema MUST apresentar um indicador visual distinguível de foco `:focus-visible` em campos e botões quando alcançados por navegação de teclado. Campos de texto MUST ter uma única demarcação visual, altura mínima de 44 px e foco perceptível no controle que os contém, sem borda ou sombra duplicada no conteúdo interno.

#### Scenario: Foco por teclado em campo
- **WHEN** visitante move o foco para um campo usando teclado
- **THEN** o campo apresenta um indicador visual perceptível no controle externo, sem demarcação duplicada no texto

#### Scenario: Campo mantém tamanho e borda únicos
- **WHEN** qualquer formulário exibe um campo de texto, seleção ou busca
- **THEN** o controle tem pelo menos 44 px de altura e uma única borda, raio e fundo visíveis

#### Scenario: Foco por teclado em botão
- **WHEN** visitante move o foco para um botão usando teclado
- **THEN** o botão apresenta um indicador visual de foco perceptível

### Requirement: Tema escuro respeita preferência do sistema e contraste
O sistema MUST oferecer alternância de tema escuro com tokens aplicados ao contêiner principal, respeitar a preferência de cor do sistema na inicialização e manter contraste de texto de pelo menos 4.5:1 nos dois temas. Preferências de aparência podem ser persistidas somente no navegador e não podem incluir dados pessoais ou ser enviadas ao servidor.

#### Scenario: Preferência inicial do sistema
- **WHEN** a página é carregada sem escolha de tema salva
- **THEN** o tema acompanha `prefers-color-scheme`

#### Scenario: Alternar tema
- **WHEN** pessoa ativa Modo escuro em Perfil
- **THEN** o tema alterna imediatamente em todas as áreas dentro do contêiner principal sem recarregar a página

#### Scenario: Escolha não é persistida
- **WHEN** pessoa muda a aparência ou encerra a sessão autenticada
- **THEN** nenhuma preferência é gravada em cookie, perfil ou backend; somente os quatro valores de aparência podem permanecer no navegador

#### Scenario: Preferências de aparência persistem localmente
- **WHEN** pessoa altera tema, escala da fonte, alto contraste ou redução de movimento e navega ou recarrega
- **THEN** somente esses quatro valores simples permanecem no navegador, sem token, identidade ou dado pessoal e sem envio ao servidor

#### Scenario: Preferências são aplicadas antes da pintura
- **WHEN** pessoa abre qualquer rota com preferências de aparência salvas
- **THEN** as preferências são aplicadas ao contêiner principal antes da primeira pintura da página

#### Scenario: Armazenamento local indisponível
- **WHEN** o navegador bloqueia ou falha ao acessar o armazenamento local
- **THEN** a página continua utilizável e aplica o tema padrão do sistema sem expor erro ou dado de sessão

#### Scenario: Alto contraste permanece disponível
- **WHEN** pessoa usa qualquer tema e ativa alto contraste
- **THEN** os tokens de alto contraste continuam aplicados e os controles permanecem operáveis por teclado

### Requirement: Telas principais mantêm hierarquia visual coerente
A aplicação MUST apresentar uma hierarquia visual consistente entre autenticação, catálogo, área pessoal, acervo e circulação, sem reduzir legibilidade ou acessibilidade.

#### Scenario: Navegação entre jornadas principais
- **WHEN** pessoa navega entre telas públicas, pessoais e administrativas
- **THEN** cabeçalho, títulos, formulários, ações e mensagens de estado mantêm padrões visuais coerentes e distinguíveis

#### Scenario: Operações de bibliotecário e admin mostram feedback
- **WHEN** bibliotecário ou admin consulta, cria, edita ou opera acervo, reservas, circulação ou contas
- **THEN** estados de carregamento, vazio, sucesso e erro são visíveis, e ações destrutivas são distinguíveis das principais

#### Scenario: Listas operacionais em tela estreita
- **WHEN** pessoa consulta tabelas ou listas operacionais em viewport de 360 px
- **THEN** conteúdo permanece legível e qualquer rolagem horizontal fica contida na própria lista, sem rolagem horizontal da página

## ADDED Requirements

### Requirement: Visitantes podem ajustar a aparência
O Perfil de visitante MUST oferecer os mesmos controles de aparência disponíveis a pessoas autenticadas, além das ações de entrada e cadastro.

#### Scenario: Controles de aparência no Perfil visitante
- **WHEN** visitante expande Perfil
- **THEN** pode ajustar tamanho da fonte, alto contraste, redução de movimento e modo escuro, além de abrir Entrar ou Cadastrar-se

### Requirement: Home mantém um hero de vitrine sem ações
A home MUST apresentar no hero somente a etiqueta, o título, a frase de apoio e estatísticas do catálogo; busca e ações de navegação ficam fora do hero.

#### Scenario: Hero simplificado em qualquer perfil
- **WHEN** visitante, estudante, bibliotecário ou admin abre a home
- **THEN** o hero não contém campo ou botão de busca, botão para catálogo, ações de autenticação ou atalhos de perfil

#### Scenario: Seções públicas e rodapé da home
- **WHEN** pessoa percorre a home
- **THEN** encontra Livros em destaque com “Ver mais” para o catálogo, a seção “Sobre a biblioteca” e um rodapé identificado como “Biblioteca escolar”
