# Spec Delta

## MODIFIED Requirements

### Requirement: Aplicação apresenta estrutura base navegável
O sistema MUST apresentar uma estrutura comum com a home como vitrine pública, navegação por perfil e acesso ao catálogo, sem executar operações de negócio nesta capability.

#### Scenario: Abertura da aplicação
- **WHEN** visitante abre `/`
- **THEN** o sistema apresenta a vitrine pública e permite navegar ao catálogo, entrar ou cadastrar-se

#### Scenario: Usuário autenticado abre a aplicação
- **WHEN** usuário autenticado abre `/`
- **THEN** o sistema apresenta a vitrine e atalhos correspondentes à sua identidade e visão ativa

#### Scenario: Navegação por teclado
- **WHEN** pessoa percorre a estrutura base usando teclado
- **THEN** os controles podem ser alcançados e ativados sem ponteiro, com foco visível

### Requirement: Navegação compartilhada apresenta opções adequadas à sessão
A aplicação MUST exibir em todas as telas uma barra compacta de uma linha, com a marca ligada a `/`, acesso ao catálogo e opções coerentes com a identidade e a visão ativa. O controle Perfil MUST apresentar os dados e ações adequados sem expor token ou senha.

#### Scenario: Visitante navega entre áreas públicas
- **WHEN** visitante abre qualquer tela
- **THEN** a barra apresenta a marca ligada a `/`, Catálogo e Perfil, e Perfil oferece Entrar, Cadastrar-se e Modo escuro sem link separado de Início

#### Scenario: Estudante autenticado navega na aplicação
- **WHEN** estudante autenticado abre qualquer tela
- **THEN** a barra apresenta Catálogo, Reservas e Perfil

#### Scenario: Bibliotecário autenticado navega na aplicação
- **WHEN** bibliotecário autenticado abre qualquer tela
- **THEN** a barra apresenta Catálogo, Acervo, Reservas e Perfil, sem ações de admin

#### Scenario: Administrador autenticado navega na aplicação
- **WHEN** admin autenticado está na visão Administrador
- **THEN** a barra apresenta Catálogo, Contas e Perfil

#### Scenario: Usuário autenticado navega na aplicação
- **WHEN** pessoa autenticada expande Perfil
- **THEN** vê nome, e-mail e o cargo “Estudante”, “Bibliotecário” ou “Administrador”, controles de fonte, alto contraste e movimento, Modo escuro e Sair, sem token ou senha

#### Scenario: Admin autenticado navega na aplicação
- **WHEN** admin abre a aplicação na visão Administrador
- **THEN** vê Catálogo e Contas além do controle Perfil e não recebe ações de estudante

#### Scenario: Admin alterna para visualização de estudante
- **WHEN** admin seleciona Estudante no seletor de visão dentro de Perfil
- **THEN** a barra mostra Catálogo, Reservas e Perfil, identifica a visão ativa e mantém identidade, token e permissões efetivas de admin

#### Scenario: Visualização de estudante respeita a sessão admin
- **WHEN** admin em visão de estudante abre Reservas
- **THEN** a aplicação usa somente a própria sessão admin e apresenta a recusa do backend sem simular registros pessoais

#### Scenario: Admin alterna para visualização de bibliotecário
- **WHEN** admin seleciona Bibliotecário no seletor de visão dentro de Perfil
- **THEN** a barra apresenta Catálogo, Acervo, Reservas e Perfil sem mudar a identidade, token ou permissões efetivas

#### Scenario: Admin retorna à visualização de bibliotecário
- **WHEN** admin escolhe a visualização de bibliotecário
- **THEN** o cabeçalho mostra “Modo de visualização: Bibliotecária” e as opções administrativas, sem mudar as permissões efetivas do admin

#### Scenario: Bibliotecário tenta abrir gestão de bibliotecários
- **WHEN** bibliotecário autenticado abre a rota de gestão de contas
- **THEN** a interface nega o acesso e não envia operações de gestão

#### Scenario: Seletor de visão do admin
- **WHEN** admin expande Perfil
- **THEN** pode selecionar Administrador, Bibliotecário ou Estudante, e a visão Administrador restaura a navegação Catálogo e Contas

#### Scenario: Retorno à visão de administrador
- **WHEN** admin está em uma visão simulada
- **THEN** a indicação do modo e o controle Voltar à visão de admin permanecem visíveis fora de Perfil

#### Scenario: Usuário encerra a sessão
- **WHEN** pessoa autenticada ativa Sair
- **THEN** a sessão privada é removida e a navegação passa a ser a de visitante

#### Scenario: Navegação móvel
- **WHEN** a aplicação é exibida em viewport de 360 px
- **THEN** marca e controle de menu cabem na barra, o menu contém os mesmos destinos/ações, não causa rolagem horizontal e os alvos interativos têm pelo menos 44 px

#### Scenario: Navegação de bibliotecário em visão admin
- **WHEN** admin seleciona a visão Bibliotecário
- **THEN** mantém o acesso visual às operações de bibliotecário sem alterar as permissões efetivas de admin

#### Scenario: Rotas antigas de perfil e acessibilidade
- **WHEN** pessoa abre `/perfil` ou `/acessibilidade`
- **THEN** a aplicação redireciona para `/` e os controles de acessibilidade continuam disponíveis em Perfil

## ADDED Requirements

### Requirement: Caixa Perfil fecha por teclado e interação externa
A caixa Perfil MUST ser operável por teclado, fechar com Escape e fechar quando a pessoa ativa uma área fora dela, devolvendo o foco ao controle Perfil quando o fechamento for iniciado por Escape.

#### Scenario: Abrir e fechar pelo teclado
- **WHEN** pessoa alcança Perfil por teclado, expande a caixa e pressiona Escape
- **THEN** a caixa fecha e o foco retorna ao controle Perfil

#### Scenario: Fechar ao clicar fora
- **WHEN** a caixa Perfil está expandida e pessoa ativa outro ponto da página
- **THEN** a caixa fecha sem impedir a ação no destino

### Requirement: Rodapé comum não duplica a navegação principal
Todas as rotas MUST apresentar um rodapé curto compartilhado com a identificação “Sobre a biblioteca” e somente links já disponíveis, sem repetir atalhos soltos no conteúdo principal.

#### Scenario: Rodapé compartilhado
- **WHEN** pessoa abre qualquer rota da aplicação
- **THEN** encontra um único rodapé com “Sobre a biblioteca” e destinos existentes

#### Scenario: Navegação do corpo da página
- **WHEN** pessoa percorre o conteúdo de qualquer rota
- **THEN** não encontra cópias de links de navegação global que já estão no cabeçalho

### Requirement: Tema escuro respeita preferência do sistema e contraste
O sistema MUST oferecer alternância de tema escuro com tokens aplicados ao contêiner principal, respeitar a preferência de cor do sistema na inicialização e manter contraste de texto de pelo menos 4.5:1 nos dois temas.

#### Scenario: Preferência inicial do sistema
- **WHEN** a página é carregada sem escolha de tema nesta sessão
- **THEN** o tema acompanha `prefers-color-scheme`

#### Scenario: Alternar tema
- **WHEN** pessoa ativa Modo escuro em Perfil
- **THEN** o tema alterna imediatamente em todas as áreas dentro do contêiner principal sem recarregar a página

#### Scenario: Escolha não é persistida
- **WHEN** a pessoa encerra ou recarrega a sessão da página
- **THEN** nenhuma escolha de tema é gravada em localStorage, cookie, perfil ou backend e a preferência inicial do sistema volta a ser aplicada

#### Scenario: Alto contraste permanece disponível
- **WHEN** pessoa usa qualquer tema e ativa alto contraste
- **THEN** os tokens de alto contraste continuam aplicados e os controles permanecem operáveis por teclado
