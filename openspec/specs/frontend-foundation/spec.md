# frontend-foundation Specification

## Purpose

Estabelecer a base acessível e segura do frontend da biblioteca para que capacidades futuras possam ser implementadas sem expor credenciais ou antecipar regras de negócio.

## Requirements

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
### Requirement: Controles interativos exibem foco visível
O sistema MUST apresentar um indicador visual distinguível de foco `:focus-visible` em campos e botões quando alcançados por navegação de teclado.

#### Scenario: Foco por teclado em campo
- **WHEN** visitante move o foco para um campo usando teclado
- **THEN** o campo apresenta um indicador visual de foco perceptível

#### Scenario: Foco por teclado em botão
- **WHEN** visitante move o foco para um botão usando teclado
- **THEN** o botão apresenta um indicador visual de foco perceptível
### Requirement: Cliente Xano usa configuração de ambiente no backend
O sistema MUST enviar requisições ao Xano a partir do backend Reflex e obter a URL base de uma variável de ambiente, sem embutir a URL no código cliente ou no bundle público.

#### Scenario: URL base configurada
- **WHEN** o backend Reflex prepara uma requisição ao Xano
- **THEN** o cliente usa a URL base definida em `XANO_API_BASE_URL`

#### Scenario: URL base ausente ou inválida
- **WHEN** o cliente precisa enviar uma requisição e `XANO_API_BASE_URL` está ausente ou inválida
- **THEN** o backend informa um erro de configuração sem realizar a requisição
### Requirement: Token de sessão permanece privado no backend Reflex
O sistema MUST manter o token de sessão somente em estado isolado por sessão no backend Reflex e impedir que ele seja exposto ao navegador, ao bundle público ou aos logs da aplicação.

#### Scenario: Requisição autenticada pelo backend
- **WHEN** uma requisição ao Xano necessita de autenticação
- **THEN** o backend usa o token associado à sessão sem enviá-lo como estado ou conteúdo acessível ao navegador

#### Scenario: Sessões de usuários diferentes
- **WHEN** duas sessões Reflex distintas mantêm tokens diferentes
- **THEN** uma sessão não pode usar nem observar o token da outra

#### Scenario: Registro de erros de rede
- **WHEN** uma requisição autenticada falha
- **THEN** o erro apresentado e os logs não contêm o token nem o cabeçalho de autorização
### Requirement: Navegação compartilhada apresenta opções adequadas à sessão

A aplicação MUST exibir em todas as telas um cabeçalho navegável com opções coerentes com a sessão e o perfil autenticado e acesso ao catálogo público.

#### Scenario: Visitante navega entre áreas públicas
- **WHEN** visitante abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece links para Início, Catálogo, Entrar e Cadastrar-se, além de navegação por teclado com foco visível

#### Scenario: Usuário autenticado navega na aplicação
- **WHEN** usuário autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho apresenta “Olá, <nome>” com o nome recebido na sessão, sem exibir e-mail, senha ou token, e oferece Catálogo e Sair

#### Scenario: Estudante autenticado navega na aplicação
- **WHEN** estudante autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Início, Catálogo, Minha biblioteca e Sair e não exibe Entrar, Cadastrar-se ou acesso administrativo

#### Scenario: Bibliotecário autenticado navega na aplicação
- **WHEN** bibliotecário autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece Início, Catálogo, Cadastrar livro em `/admin/acervo` e Sair

#### Scenario: Administrador autenticado navega na aplicação
- **WHEN** administrador autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece as opções de bibliotecário e o acesso à gestão de bibliotecários

#### Scenario: Usuário encerra a sessão
- **WHEN** usuário autenticado ativa Sair
- **THEN** a sessão privada é removida e a aplicação retorna à página inicial com navegação de visitante

#### Scenario: Admin autenticado navega na aplicação
- **WHEN** admin autenticado abre qualquer tela da aplicação
- **THEN** o cabeçalho oferece as mesmas opções administrativas que ao bibliotecário, acesso à gestão de bibliotecários e não oferece ações exclusivas de estudante

#### Scenario: Admin alterna para visualização de estudante
- **WHEN** admin autenticado escolhe a visualização de estudante
- **THEN** o cabeçalho mostra “Modo de visualização: Estudante” e a opção Minha biblioteca, sem alterar perfil, token ou permissões da sessão

#### Scenario: Visualização de estudante respeita a sessão admin
- **WHEN** admin em visualização de estudante abre Minha biblioteca
- **THEN** a interface usa somente o token da própria sessão admin e apresenta a recusa do backend sem simular registros pessoais

#### Scenario: Admin retorna à visualização de bibliotecário
- **WHEN** admin escolhe a visualização de bibliotecário
- **THEN** o cabeçalho mostra “Modo de visualização: Bibliotecária” e as opções administrativas, sem mudar as permissões efetivas do admin

#### Scenario: Bibliotecário tenta abrir gestão de bibliotecários
- **WHEN** bibliotecário autenticado abre a rota de gestão de bibliotecários
- **THEN** a interface nega o acesso e não envia operações de gestão de contas
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
### Requirement: Telas principais mantêm hierarquia visual coerente
A aplicação MUST apresentar uma hierarquia visual consistente entre autenticação, catálogo, área pessoal, acervo e circulação, sem reduzir legibilidade ou acessibilidade.

#### Scenario: Navegação entre jornadas principais
- **WHEN** pessoa navega entre telas públicas, pessoais e administrativas
- **THEN** cabeçalho, títulos, formulários, ações e mensagens de estado mantêm padrões visuais coerentes e distinguíveis
### Requirement: Navegação administrativa oferece acesso às reservas por estudante

A interface MUST oferecer acesso à tela de reservas administrativas somente a bibliotecários e admins autenticados, mantendo a autorização do backend para qualquer busca ou criação.

#### Scenario: Bibliotecário abre a navegação
- **WHEN** bibliotecário autenticado abre o cabeçalho compartilhado
- **THEN** vê um link para a área de reservas administrativas em `/admin/reservas`

#### Scenario: Admin abre a navegação
- **WHEN** admin autenticado abre o cabeçalho compartilhado
- **THEN** vê o mesmo link de reservas administrativas disponível ao bibliotecário

#### Scenario: Visitante ou estudante abre a navegação
- **WHEN** visitante ou estudante abre o cabeçalho compartilhado
- **THEN** não vê o link de reservas administrativas

#### Scenario: Perfil sem privilégio tenta acessar a tela
- **WHEN** visitante ou estudante acessa diretamente `/admin/reservas`
- **THEN** a interface bloqueia ou redireciona e não envia busca de estudante nem criação de reserva
### Requirement: Execução local do Reflex funciona no Windows

O projeto MUST oferecer um fluxo documentado para iniciar frontend e backend Reflex no Windows com `reflex run`, sem editar manualmente a saída gerada nem reduzir as proteções do sistema operacional.

#### Scenario: Inicialização local completa
- **WHEN** desenvolvedor executa `reflex run` no ambiente Windows configurado conforme o projeto
- **THEN** frontend e backend iniciam e o navegador consegue carregar uma rota da aplicação e estabelecer a conexão de estado com o backend

#### Scenario: Configuração regenerada
- **WHEN** o Reflex recria seus arquivos de frontend gerados
- **THEN** o fluxo documentado continua iniciando a aplicação sem depender de edições manuais nesses arquivos
### Requirement: Falha de inicialização preserva o erro original

O projeto MUST encerrar os processos iniciados pela tentativa e apresentar a falha original de inicialização sem substituí-la por uma exceção secundária de limpeza.

#### Scenario: Frontend falha ao iniciar
- **WHEN** o processo frontend iniciado pelo comando Reflex termina antes de ficar disponível
- **THEN** o comando reporta a causa original, não gera uma exceção de processo inexistente durante a limpeza e não deixa subprocessos da tentativa em execução
