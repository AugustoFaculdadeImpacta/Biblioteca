# Spec Delta

## MODIFIED Requirements

### Requirement: Aplicação apresenta estrutura base navegável
O sistema MUST apresentar uma estrutura comum de aplicação com navegação simples entre áreas, sem executar operações de negócio nesta capability.

#### Scenario: Abertura da aplicação
- **WHEN** visitante abre a aplicação na rota `/`
- **THEN** o sistema apresenta a tela de login e oferece acesso explícito ao catálogo público sem exigir autenticação

#### Scenario: Usuário autenticado abre a aplicação
- **WHEN** usuário com sessão autenticada abre a rota `/`
- **THEN** o sistema direciona o usuário ao catálogo

#### Scenario: Navegação por teclado
- **WHEN** visitante percorre a estrutura base usando teclado
- **THEN** os controles de navegação podem ser alcançados e ativados sem uso de ponteiro

### Requirement: Navegação compartilhada apresenta opções adequadas à sessão
A aplicação MUST exibir em todas as telas um cabeçalho navegável com opções coerentes com a sessão e o perfil autenticado e acesso ao catálogo público.

#### Scenario: Visitante navega entre áreas públicas
- **WHEN** visitante abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece links para Catálogo, Entrar e Cadastrar-se, identifica a ação de entrada como “Entrar”, e não apresenta um destino separado de Início

#### Scenario: Usuário autenticado navega na aplicação
- **WHEN** usuário autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho apresenta “Olá, <nome>” com o nome recebido na sessão, sem exibir e-mail, senha ou token, e oferece Catálogo e Sair

#### Scenario: Estudante autenticado navega na aplicação
- **WHEN** estudante autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Minha biblioteca e não exibe Cadastrar-se nem acesso administrativo

#### Scenario: Bibliotecário autenticado navega na aplicação
- **WHEN** bibliotecário autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Cadastrar livro em `/admin/acervo` e Reservas para estudantes

#### Scenario: Administrador autenticado navega na aplicação
- **WHEN** administrador autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece as opções de bibliotecário e o acesso à gestão de bibliotecários

#### Scenario: Usuário encerra a sessão
- **WHEN** usuário autenticado ativa Sair
- **THEN** a sessão privada é removida e a aplicação retorna à rota raiz com navegação de visitante

## ADDED Requirements

### Requirement: Login oferece acesso ao catálogo público
A tela de login MUST oferecer uma ação claramente rotulada para acessar o catálogo público sem autenticação.

#### Scenario: Visitante abre catálogo pelo login
- **WHEN** visitante ativa “Ver catálogo sem entrar” na tela de login
- **THEN** o sistema abre o catálogo público sem exigir sessão autenticada

### Requirement: Preferências de acessibilidade são globais e persistentes
O sistema MUST oferecer controles de acessibilidade operáveis por teclado, aplicar suas escolhas em todas as telas e preservá-las entre navegações e recargas no mesmo navegador.

#### Scenario: Aumentar fonte respeita o limite superior
- **WHEN** usuário aumenta a fonte enquanto a escala está em 150%
- **THEN** a escala permanece em 150%

#### Scenario: Diminuir fonte respeita o limite inferior
- **WHEN** usuário diminui a fonte enquanto a escala está em 100%
- **THEN** a escala permanece em 100%

#### Scenario: Restaurar fonte ao tamanho padrão
- **WHEN** usuário ativa “Restaurar fonte”
- **THEN** a escala volta a 100%

#### Scenario: Preferência de fonte persiste
- **WHEN** usuário altera a escala e navega para outra tela ou recarrega a página
- **THEN** a escala escolhida permanece aplicada

#### Scenario: Alto contraste alterna em todas as telas
- **WHEN** usuário ativa ou desativa “Alto contraste”
- **THEN** o modo escolhido é aplicado em todas as telas, persiste após recarga e mantém contraste de texto de pelo menos 4.5:1

#### Scenario: Redução de animações alterna em todas as telas
- **WHEN** usuário ativa ou desativa “Reduzir animações”
- **THEN** a preferência é aplicada em todas as telas e persiste após navegação ou recarga

#### Scenario: Controles de acessibilidade são operáveis por teclado
- **WHEN** usuário navega pelo cabeçalho usando teclado
- **THEN** consegue alcançar e ativar os controles de fonte, contraste e animação, com rótulos em português e foco visível

#### Scenario: Layout permanece utilizável em telas estreitas e largas
- **WHEN** a aplicação é exibida nas larguras de 360px ou 1366px
- **THEN** o conteúdo e os controles de acessibilidade não provocam rolagem horizontal
