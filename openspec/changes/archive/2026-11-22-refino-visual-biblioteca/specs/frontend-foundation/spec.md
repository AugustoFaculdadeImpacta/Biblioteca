# Spec Delta

## MODIFIED Requirements

### Requirement: Telas principais mantêm hierarquia visual coerente
A aplicação MUST apresentar uma hierarquia visual consistente entre autenticação, catálogo, área pessoal, acervo e circulação, sem reduzir legibilidade ou acessibilidade. A identidade visual deve distinguir marca, títulos, conteúdo, ações e estados, funcionar em telas móveis e desktop e não depender de recursos externos.

#### Scenario: Navegação entre jornadas principais
- **WHEN** pessoa navega entre telas públicas, pessoais e administrativas
- **THEN** cabeçalho, títulos, formulários, ações e mensagens de estado mantêm padrões visuais coerentes e distinguíveis

#### Scenario: Preferência de movimento reduzido
- **WHEN** o sistema ou a preferência de acessibilidade solicita movimento reduzido
- **THEN** transições e animações decorativas são removidas ou reduzidas sem esconder informação ou feedback

#### Scenario: Identidade funciona offline
- **WHEN** a aplicação é aberta sem acesso a fontes, imagens ou ícones de terceiros
- **THEN** tipografia de sistema, capas CSS e controles locais mantêm a interface completa e utilizável

## ADDED Requirements

### Requirement: Página inicial apresenta uma entrada visual para o acervo
A página inicial MUST combinar uma saudação, uma chamada clara ao catálogo e seções com conteúdo real do catálogo, sem fabricar métricas ou novidades.

#### Scenario: Visitante explora a página inicial
- **WHEN** visitante abre `/`
- **THEN** vê somente uma vitrine com boas-vindas, busca que leva ao catálogo, botão “Ver catálogo”, ações “Entrar” e “Cadastrar-se” e seções tituladas com apoio visual e links “Ver mais”, sem formulário ou campo de senha

#### Scenario: Catálogo da página inicial está carregando, vazio ou indisponível
- **WHEN** os dados públicos ainda carregam, não contêm títulos ou falham
- **THEN** a página apresenta respectivamente estado de carregamento, vazio ou erro em português e não inventa contagens, títulos ou datas de novidade

#### Scenario: Usuário autenticado abre a página inicial
- **WHEN** estudante, bibliotecário ou admin abre `/`
- **THEN** vê a vitrine sem formulários e atalhos correspondentes ao perfil efetivo ou à visão selecionada pelo admin

### Requirement: Cabeçalho único orienta navegação por perfil e visão
A aplicação MUST exibir em todas as rotas um único cabeçalho responsivo com marca à esquerda, Catálogo e destinos do perfil no centro e um menu “Perfil” à direita.

#### Scenario: Menu Perfil para visitante
- **WHEN** visitante abre o menu Perfil
- **THEN** encontra Entrar e Cadastrar-se, operáveis por teclado, com fechamento por Escape e foco devolvido ao acionador

#### Scenario: Menu Perfil para pessoa autenticada
- **WHEN** pessoa autenticada abre o menu Perfil
- **THEN** encontra nome e papel em modo somente leitura, Meu perfil, Acessibilidade e Sair

#### Scenario: Navegação central por perfil e visão efetiva
- **WHEN** estudante, bibliotecário ou admin navega, incluindo visão simulada pelo admin
- **THEN** Catálogo permanece visível e os demais links correspondem somente à visão ativa; o admin conserva fora do menu o estado da visão e a ação para retornar à visão Admin

#### Scenario: Navegação em viewport móvel
- **WHEN** a aplicação é exibida em 360 px
- **THEN** marca e botão de menu recolhível aparecem na barra; ao expandir, os links centrais e o menu Perfil continuam disponíveis com alvos de pelo menos 44 px e suporte a teclado

### Requirement: Formulários de login e cadastro são páginas independentes
As rotas `/login` e `/cadastro` MUST apresentar somente o formulário correspondente, sem duplicar o formulário da outra rota.

#### Scenario: Visitante abre login ou cadastro
- **WHEN** visitante abre `/login` ou `/cadastro`
- **THEN** vê respectivamente somente login ou somente cadastro, com links recíprocos; login mantém “Ver catálogo sem entrar”

#### Scenario: Pessoa autenticada abre uma rota de autenticação
- **WHEN** sessão autenticada abre `/login` ou `/cadastro`
- **THEN** Reflex redireciona à página inicial do perfil/visão ativa, sem apresentar o formulário

### Requirement: Perfil e Acessibilidade usam a sessão e controles existentes
`/perfil` MUST exibir somente dados de identificação e papel já presentes na sessão; `/acessibilidade` MUST reutilizar os controles locais de fonte, contraste e movimento.

#### Scenario: Perfil autenticado
- **WHEN** pessoa autenticada abre `/perfil`
- **THEN** vê nome, e-mail e papel da própria sessão, sem edição ou chamada adicional ao Xano

#### Scenario: Perfil sem sessão
- **WHEN** visitante abre `/perfil`
- **THEN** é redirecionado para `/login`

#### Scenario: Preferências de acessibilidade
- **WHEN** visitante ou pessoa autenticada abre `/acessibilidade`
- **THEN** encontra os controles já existentes, com preferências persistidas e acessíveis por teclado

### Requirement: Todas as rotas compartilham um rodapé sem destinos inventados
As páginas públicas e protegidas MUST usar o mesmo rodapé e não repetir no conteúdo links que já pertencem à navegação global.

#### Scenario: Navegação entre rotas
- **WHEN** qualquer rota renderiza
- **THEN** aparece um único cabeçalho e o rodapé comum, com links apenas para destinos locais existentes e sem duplicatas de navegação no corpo da página

### Requirement: Cabeçalho e rodapé identificam a biblioteca e orientam a navegação
A aplicação MUST apresentar uma identidade textual própria e navegação coerente com o perfil, com destinos válidos e sem depender de identidade visual de terceiros.

#### Scenario: Cabeçalho em qualquer perfil
- **WHEN** visitante, estudante, bibliotecário ou admin abre uma tela
- **THEN** o cabeçalho mostra o nome da biblioteca, slogan curto e opções adequadas ao perfil, preservando alternância visual do admin e controles de acessibilidade existentes

#### Scenario: Rodapé oferece referências disponíveis
- **WHEN** qualquer perfil percorre o rodapé
- **THEN** encontra uma apresentação curta da biblioteca e acesso aos controles de acessibilidade; contato e privacidade só aparecem como links quando seus destinos oficiais estão disponíveis

### Requirement: Cartões de catálogo comunicam título e disponibilidade
Cada cartão público MUST apresentar os metadados existentes do título, uma capa local de fallback e estado de disponibilidade distinguível, sem criar dependências de imagem ou alterar o contrato público.

#### Scenario: Cartão apresenta título com categoria
- **WHEN** o catálogo renderiza um título com categoria conhecida
- **THEN** mostra título, autoria, categoria, disponibilidade e ação existente, com capa CSS cuja cor e inicial derivam da categoria

#### Scenario: Cartão não tem categoria ou imagem de capa
- **WHEN** título não tem categoria ou o contrato público não fornece imagem de capa
- **THEN** o cartão usa um fallback CSS legível, derivado do título quando não houver categoria, sem imagem externa ou erro de renderização

#### Scenario: Estudante consulta a disponibilidade
- **WHEN** estudante ou visitante vê um título disponível ou indisponível
- **THEN** o estado é informado por texto e estilo visual, e as ações permanecem compatíveis com o perfil e as regras existentes

### Requirement: Controles visuais permanecem acessíveis em telas móveis
A aplicação MUST preservar os recursos de acessibilidade existentes e dimensionar controles acionáveis para uso por toque em telas estreitas.

#### Scenario: Alvos de toque em tela móvel
- **WHEN** a aplicação é exibida em largura de 360 px
- **THEN** links, botões e controles acionáveis têm área mínima de 44 px, não causam rolagem horizontal e continuam legíveis

#### Scenario: Foco, fonte e contraste após a reformulação
- **WHEN** usuário navega por teclado, amplia a fonte ou ativa alto contraste
- **THEN** foco `:focus-visible`, limites de fonte, controles e contraste WCAG AA continuam funcionando em todas as telas alteradas

### Requirement: Formulários e estados usam padrões visuais consistentes
Formulários e painéis MUST distinguir ações e estados de carregamento, vazio, erro e sucesso sem depender somente de cor.

#### Scenario: Formulário ou painel apresenta um estado
- **WHEN** uma operação está carregando, não tem registros, falha ou termina com sucesso
- **THEN** a interface apresenta mensagem em português com semântica acessível e estilo consistente, sem ocultar erro ou confirmação
