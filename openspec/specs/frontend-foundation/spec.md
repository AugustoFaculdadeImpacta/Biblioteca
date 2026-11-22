# frontend-foundation Specification

## Purpose

Estabelecer a base acessível e segura do frontend da biblioteca para que capacidades futuras possam ser implementadas sem expor credenciais ou antecipar regras de negócio.

## Requirements

### Requirement: Aplicação apresenta estrutura base navegável
O sistema MUST apresentar uma estrutura comum com a home como vitrine pública e navegação por perfil, sem executar operações de negócio nesta capability.

#### Scenario: Abertura da aplicação
- **WHEN** visitante abre `/`
- **THEN** o sistema apresenta a vitrine pública e permite navegar ao catálogo, entrar ou cadastrar-se

#### Scenario: Usuário autenticado abre a aplicação
- **WHEN** usuário autenticado abre `/`
- **THEN** o sistema apresenta a vitrine e atalhos correspondentes à sua identidade e visão ativa

#### Scenario: Navegação por teclado
- **WHEN** visitante percorre a estrutura base usando teclado
- **THEN** os controles podem ser alcançados e ativados sem ponteiro, com foco visível
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

A aplicação MUST exibir em todas as telas uma barra compacta de uma linha, com a marca ligada a `/`, acesso ao catálogo e opções coerentes com a identidade e a visão ativa. O controle Perfil MUST apresentar os dados e ações adequados sem expor token ou senha.

#### Scenario: Visitante navega entre áreas públicas
- **WHEN** visitante abre qualquer tela da aplicação
- **THEN** a barra apresenta a marca ligada a `/`, Catálogo e Perfil, e Perfil oferece Entrar, Cadastrar-se e Modo escuro sem link separado de Início

#### Scenario: Estudante autenticado navega na aplicação
- **WHEN** estudante autenticado abre qualquer tela da aplicação
- **THEN** a barra apresenta Catálogo, Reservas e Perfil

#### Scenario: Bibliotecário autenticado navega na aplicação
- **WHEN** bibliotecário autenticado abre qualquer tela da aplicação
- **THEN** a barra apresenta Catálogo, Acervo, Reservas e Perfil, sem ações de admin

#### Scenario: Administrador autenticado navega na aplicação
- **WHEN** admin autenticado está na visão Administrador
- **THEN** a barra apresenta Catálogo, Contas e Perfil

#### Scenario: Usuário autenticado navega na aplicação
- **WHEN** pessoa autenticada expande Perfil
- **THEN** vê nome, e-mail e o cargo “Estudante”, “Bibliotecário” ou “Administrador”, controles de fonte, alto contraste e movimento, Modo escuro e Sair, sem token ou senha

#### Scenario: Admin alterna para visualização de estudante
- **WHEN** admin seleciona Estudante no seletor de visão dentro de Perfil
- **THEN** a barra mostra Catálogo, Reservas e Perfil, identifica a visão ativa e mantém identidade, token e permissões efetivas de admin

#### Scenario: Visualização de estudante respeita a sessão admin
- **WHEN** admin em visão de estudante abre Reservas
- **THEN** a aplicação usa somente a própria sessão admin e apresenta a recusa do backend sem simular registros pessoais

#### Scenario: Admin retorna à visualização de bibliotecário
- **WHEN** admin seleciona Bibliotecário no seletor de visão dentro de Perfil
- **THEN** a barra apresenta Catálogo, Acervo, Reservas e Perfil sem mudar a identidade, token ou permissões efetivas

#### Scenario: Bibliotecário tenta abrir gestão de bibliotecários
- **WHEN** bibliotecário autenticado abre a rota de gestão de contas
- **THEN** a interface nega o acesso e não envia operações de gestão

#### Scenario: Admin autenticado navega na aplicação
- **WHEN** admin abre qualquer tela na visão Administrador
- **THEN** vê Catálogo e Contas além do controle Perfil e não recebe ações de estudante

#### Scenario: Admin alterna para visualização de bibliotecário
- **WHEN** admin seleciona Bibliotecário no seletor de visão dentro de Perfil
- **THEN** a barra apresenta as opções da visão de bibliotecário sem alterar a identidade, o token ou as permissões efetivas

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
- **THEN** mantém o acesso visual às operações de bibliotecário sem alterar as permissões efetivas do admin

#### Scenario: Rotas antigas de perfil e acessibilidade
- **WHEN** pessoa abre `/perfil` ou `/acessibilidade`
- **THEN** a aplicação redireciona para `/` e os controles de acessibilidade continuam disponíveis em Perfil

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

#### Scenario: Operações de bibliotecário e admin mostram feedback
- **WHEN** bibliotecário ou admin consulta, cria, edita ou opera acervo, reservas, circulação ou contas
- **THEN** estados de carregamento, vazio, sucesso e erro são visíveis, e ações destrutivas são distinguíveis das principais

#### Scenario: Listas operacionais em tela estreita
- **WHEN** pessoa consulta tabelas ou listas operacionais em viewport de 360 px
- **THEN** conteúdo permanece legível e qualquer rolagem horizontal fica contida na própria lista, sem rolagem horizontal da página
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
- **THEN** o emoji fica em elemento próprio com `aria-hidden="true"` antes do texto correspondente

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
