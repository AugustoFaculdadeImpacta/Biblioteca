# catalog Specification

## Purpose

Define consulta pública e administração autorizada do acervo, preservando a distinção entre obra bibliográfica, categorias e exemplares físicos.

## Requirements

### Requirement: Catálogo é consultável publicamente

O sistema MUST permitir a visitantes consultar títulos ativos e disponibilidade agregada sem autenticação, derivando disponibilidade dos exemplares elegíveis.

#### Scenario: Consulta pública
- **WHEN** visitante solicita o catálogo ou um título
- **THEN** o sistema retorna metadados bibliográficos publicados e disponibilidade agregada de títulos ativos, sem dados pessoais de estudantes

#### Scenario: Disponibilidade por exemplares
- **WHEN** o sistema informa disponibilidade de um título ativo
- **THEN** o resultado deriva dos exemplares físicos elegíveis e não de uma quantidade independente mantida no título

#### Scenario: Título desativado não aparece publicamente
- **WHEN** visitante solicita catálogo ou detalhe de título desativado
- **THEN** o título não é incluído no catálogo público e seu detalhe não é exposto
### Requirement: Título pode relacionar múltiplas categorias e exemplares
O sistema MUST representar uma obra bibliográfica separada de suas categorias e unidades físicas, permitindo relação muitos-para-muitos entre títulos e categorias e um-para-muitos entre título e exemplar.

#### Scenario: Metadados bibliográficos
- **WHEN** bibliotecário cria ou atualiza um título
- **THEN** título e autor(es) são obrigatórios; ISBN, editora, edição, ano de publicação e descrição são opcionais

#### Scenario: Título em várias categorias
- **WHEN** título é associado a mais de uma categoria
- **THEN** consulta do título e consultas por categoria refletem todas as associações

#### Scenario: Múltiplas unidades físicas
- **WHEN** um título possui vários exemplares
- **THEN** cada exemplar mantém identidade e condição próprias sob o título correspondente

#### Scenario: Código de tombo do exemplar
- **WHEN** bibliotecário cria uma unidade física
- **THEN** o sistema atribui ao exemplar um código de tombo único e imutável, no formato exemplificado por `EX-000001`; cada exemplar recebe código diferente e o código não é o ISBN

#### Scenario: Código de tombo não é informado pelo cliente
- **WHEN** cliente tenta definir ou alterar o código de tombo em uma operação de exemplar
- **THEN** o backend gera e preserva o código, sem aceitar valor fornecido ou alteração pelo cliente
### Requirement: Administração do acervo exige perfil bibliotecário

O sistema MUST autorizar no backend a bibliotecários e admins autenticados consultar e manter metadados do acervo, criar ou atualizar títulos, categorias e associações e criar exemplares. Estados operacionais de exemplares são alterados somente pelos fluxos de empréstimo, reserva e condição.

#### Scenario: Bibliotecário mantém metadados do acervo
- **WHEN** bibliotecário autenticado cria ou atualiza título/categoria, associa título e categoria ou cria exemplar
- **THEN** o sistema aplica a alteração solicitada e a consulta posterior reflete o resultado

#### Scenario: Estudante ou visitante tenta administrar acervo
- **WHEN** estudante autenticado ou visitante tenta consultar dados administrativos, criar ou atualizar metadados, associar categorias ou criar exemplar
- **THEN** o backend recusa a operação sem revelar dados administrativos nem alterar dados

#### Scenario: Remoção sem política aprovada
- **WHEN** uma operação tenta remover fisicamente título, categoria, associação, exemplar, empréstimo ou reserva sem política de exclusão/arquivamento aprovada
- **THEN** o contrato não oferece a remoção e preserva o registro e seu histórico

#### Scenario: Admin mantém metadados do acervo
- **WHEN** admin autenticado cria ou atualiza título/categoria, associa título e categoria ou cria exemplar
- **THEN** o sistema aplica a alteração solicitada e a consulta posterior reflete o resultado
### Requirement: API de catálogo valida relações
O sistema MUST validar existência e compatibilidade das relações de título, categoria e exemplar antes de persistir alterações administrativas.

#### Scenario: Referência inválida
- **WHEN** pedido administrativo referencia título, categoria ou exemplar inexistente ou incompatível
- **THEN** o sistema recusa a alteração e preserva o estado anterior
### Requirement: Interface administrativa do acervo é exclusiva de bibliotecários

A interface MUST permitir acesso às ações administrativas somente após autenticação com perfil `bibliotecario` ou `admin`; a autorização do backend permanece obrigatória para toda leitura administrativa e escrita.

#### Scenario: Bibliotecário autenticado acessa administração do acervo
- **WHEN** usuário autenticado com perfil `bibliotecario` abre a área de administração
- **THEN** a interface permite acessar os formulários administrativos e envia as operações com a sessão autenticada em cada chamada

#### Scenario: Estudante ou visitante tenta acessar a administração
- **WHEN** estudante autenticado ou visitante abre uma rota ou tenta uma ação administrativa
- **THEN** a interface bloqueia ou redireciona o acesso e não envia requisição administrativa

#### Scenario: Backend recusa operação administrativa
- **WHEN** o backend recusa a operação por perfil insuficiente
- **THEN** a interface não indica sucesso e informa a recusa sem expor detalhes internos

#### Scenario: Admin autenticado acessa administração do acervo
- **WHEN** usuário autenticado com perfil `admin` abre a área de administração
- **THEN** a interface permite as mesmas ações administrativas disponíveis ao bibliotecário e envia as operações com a sessão autenticada em cada chamada
### Requirement: Cadastro de título usa somente os campos definidos
A interface MUST enviar somente os campos aceitos pelo endpoint local de criação de título e usar o registro retornado para obter seu identificador.

#### Scenario: Metadados do título no formulário
- **WHEN** bibliotecário autenticado preenche o cadastro ou edição de um título
- **THEN** título e autores são obrigatórios, e ISBN, editora, edição, ano de publicação, descrição e link HTTPS da capa são opcionais

#### Scenario: Envio do título
- **WHEN** bibliotecário confirma cadastro ou edição com dados válidos
- **THEN** a interface envia somente campos opcionais preenchidos entre `titulo`, `autores`, `isbn`, `editora`, `edicao`, `ano_publicacao`, `descricao` e `capa_url`, obtendo o identificador retornado na criação

#### Scenario: URL de capa inválida
- **WHEN** bibliotecário informa um link de capa que não usa HTTPS ou não é uma URL válida
- **THEN** a interface informa a validação e não envia a operação
### Requirement: Título pode ser associado a categorias existentes
A interface MUST permitir selecionar categorias obtidas da listagem pública e associá-las ao título recém-criado usando os identificadores retornados pelos endpoints.

#### Scenario: Carregar categorias para seleção
- **WHEN** bibliotecário autenticado abre o cadastro de título
- **THEN** a interface lista as categorias retornadas por `GET /catalogo/categorias` usando os campos `id` e `nome`

#### Scenario: Associar categorias selecionadas
- **WHEN** bibliotecário seleciona uma ou mais categorias para um título criado
- **THEN** a interface envia uma associação para cada seleção usando `titulo_id` como identificador de rota e `categoria_id` como entrada e apresenta sucesso somente para associações confirmadas

#### Scenario: Título já associado à categoria ou referência inválida
- **WHEN** a associação é recusada por duplicidade ou referência inexistente
- **THEN** a interface informa a falha sem indicar associação inexistente como concluída e permite retomar sem recriar o título
### Requirement: Bibliotecário pode criar exemplares físicos do título

A interface MUST permitir criar exemplares para título novo ou existente, enviando somente o identificador do título e exibindo o código de tombo gerado pelo servidor para cada unidade.

#### Scenario: Criar exemplares
- **WHEN** bibliotecário ou admin conclui o cadastro de um título e solicita exemplares
- **THEN** a interface cria cada unidade para o título e apresenta os registros e códigos de tombo retornados

#### Scenario: Falha parcial ao criar exemplares
- **WHEN** uma chamada sequencial de criação falha após outras terem sido confirmadas
- **THEN** a interface distingue as unidades criadas das pendentes e não repete automaticamente escritas já confirmadas

#### Scenario: Resposta não contém identificador ou código esperado
- **WHEN** uma resposta bem-sucedida de criação não contém os campos necessários definidos pela implementação local
- **THEN** a interface informa que o resultado precisa ser conferido, não presume sucesso completo e não repete automaticamente a escrita

#### Scenario: Adicionar exemplares a título existente
- **WHEN** bibliotecário ou admin seleciona título existente e solicita um ou mais exemplares
- **THEN** a interface cria as unidades para o identificador selecionado e apresenta os registros e códigos de tombo retornados
### Requirement: Interface pública apresenta títulos e disponibilidade
A interface MUST permitir que visitantes e estudantes consultem o catálogo público por lista e detalhe, sem autenticação, exibindo a disponibilidade informada pelo serviço e os metadados opcionais disponíveis.

#### Scenario: Consultar títulos públicos
- **WHEN** visitante ou estudante abre o catálogo
- **THEN** a interface apresenta títulos ativos em cartões com capa disponível ou capa CSS de fallback e permite abrir o detalhe

#### Scenario: Consultar disponibilidade no detalhe
- **WHEN** visitante ou estudante abre o detalhe de um título
- **THEN** a interface apresenta capa disponível ou fallback, título, autoria, categorias, descrição e exemplares disponíveis sem expor dados pessoais

#### Scenario: Descrição ausente
- **WHEN** o título não tem descrição preenchida
- **THEN** o detalhe apresenta “Sem descrição cadastrada.”

#### Scenario: Campo de capa ausente no contrato
- **WHEN** uma resposta não inclui `capa_url` ou contém seu valor nulo/vazio
- **THEN** a interface continua exibindo o título com a capa CSS de fallback e não trata a ausência do campo como erro

### Requirement: Cartão de catálogo evita metadado repetido
Cada cartão MUST apresentar a categoria uma única vez como etiqueta e manter capa, título, autoria, disponibilidade e ação de detalhe legíveis.

#### Scenario: Categorias exibidas no cartão
- **WHEN** cartão de título possui uma ou mais categorias
- **THEN** as categorias aparecem na etiqueta sem uma segunda linha repetindo “Categorias:”

#### Scenario: Capa remota disponível ou ausente
- **WHEN** cartão possui `capa_url` HTTPS ou não possui capa
- **THEN** a imagem usa texto alternativo acessível quando presente e, na ausência, é exibida a capa CSS derivada de categoria e título

### Requirement: Ação no detalhe respeita o perfil efetivo
O detalhe MUST oferecer a ação de reserva ao estudante autenticado, orientar visitantes ao login e ocultar a ação de estudante para bibliotecário e admin.

#### Scenario: Estudante autenticado abre o detalhe
- **WHEN** estudante autenticado consulta um título
- **THEN** vê “Reservar” e a operação usa o fluxo autenticado existente, que deixa elegibilidade e resultado final sob validação do backend

#### Scenario: Visitante abre o detalhe
- **WHEN** visitante consulta um título
- **THEN** vê “Entrar para reservar” com destino de login

#### Scenario: Perfil não estudante abre o detalhe
- **WHEN** bibliotecário, admin ou admin em visão simulada consulta um título
- **THEN** não vê nem pode acionar a ação exclusiva de estudante
### Requirement: Busca, filtros e ordenação do catálogo são aplicados em memória
A interface MUST permitir refinar os títulos carregados sem enviar filtros ou ordenações adicionais ao backend.

#### Scenario: Buscar por texto
- **WHEN** pessoa informa um texto no campo de busca
- **THEN** a lista em memória é filtrada pelos campos de título e autoria retornados pelo catálogo

#### Scenario: Filtrar por categoria e disponibilidade
- **WHEN** pessoa seleciona uma categoria ou ativa "Somente disponíveis"
- **THEN** a lista em memória contém somente títulos associados à categoria selecionada e, quando aplicável, com quantidade disponível maior que zero

#### Scenario: Ordenar alfabeticamente
- **WHEN** pessoa seleciona A-Z ou Z-A
- **THEN** os títulos visíveis são ordenados em memória pelo título, respeitando a direção selecionada

#### Scenario: Catálogo sem resultados
- **WHEN** a busca ou os filtros não correspondem a nenhum título
- **THEN** a interface informa claramente que nenhum título corresponde aos critérios atuais

#### Scenario: Filtros combinados
- **WHEN** pessoa informa texto, seleciona uma categoria, ativa somente disponíveis e escolhe ordenação A-Z ou Z-A
- **THEN** a lista em memória contém somente títulos que atendem simultaneamente aos filtros e os ordena pelo título

#### Scenario: Categoria sem títulos correspondentes
- **WHEN** visitante seleciona uma categoria existente sem títulos correspondentes
- **THEN** a interface não exibe títulos, mantém os outros filtros utilizáveis e informa que nenhum título corresponde aos critérios atuais

#### Scenario: Remover filtro de categoria
- **WHEN** visitante seleciona novamente todas as categorias
- **THEN** a interface remove apenas o filtro de categoria e preserva busca, disponibilidade e ordenação
### Requirement: Estudante inicia solicitação a partir do catálogo
A interface MUST permitir que estudante autenticado inicie o fluxo de empréstimo ou reserva de um título do catálogo, submetendo a decisão final de disponibilidade e elegibilidade ao backend.

#### Scenario: Há exemplar disponível no catálogo
- **WHEN** estudante autenticado abre o detalhe de título que informa exemplares disponíveis
- **THEN** a interface oferece solicitar empréstimo e envia a solicitação autenticada ao backend

#### Scenario: Não há exemplar disponível no catálogo
- **WHEN** estudante autenticado abre o detalhe de título sem exemplares disponíveis
- **THEN** a interface oferece entrar na fila de reserva pelo fluxo de solicitação autenticado

#### Scenario: Disponibilidade muda antes do envio
- **WHEN** disponibilidade ou elegibilidade muda entre a consulta do catálogo e o envio
- **THEN** a interface apresenta o resultado retornado pelo backend e não presume que a contagem previamente exibida ainda seja válida

#### Scenario: Visitante ou bibliotecário tenta iniciar o fluxo de estudante
- **WHEN** pessoa sem perfil estudante tenta enviar uma solicitação pelo catálogo
- **THEN** a interface bloqueia a ação e o backend continua responsável por recusar a operação não autorizada
### Requirement: Bibliotecário consulta o acervo administrativo completo

O sistema MUST permitir a bibliotecários e admins autenticados consultar todos os títulos, exemplares e estados operacionais, inclusive itens indisponíveis e títulos desativados.

#### Scenario: Consultar acervo completo
- **WHEN** bibliotecário ou admin abre a área administrativa do acervo
- **THEN** recebe todos os títulos e seus exemplares com os estados necessários à gestão, sem expor dados pessoais de estudantes

#### Scenario: Consultar título desativado
- **WHEN** bibliotecário ou admin consulta o acervo que contém título desativado
- **THEN** o título permanece visível e identificado como desativado, com seu histórico preservado

#### Scenario: Perfil sem privilégio tenta consultar acervo completo
- **WHEN** visitante ou estudante tenta consultar a listagem administrativa
- **THEN** o backend recusa a consulta e não revela os dados administrativos
### Requirement: Bibliotecário edita metadados de título existente

O sistema MUST permitir a bibliotecários e admins autenticados editar os metadados permitidos de um título existente sem alterar seu identificador, exemplares ou histórico.

#### Scenario: Atualização válida
- **WHEN** bibliotecário ou admin envia metadados válidos para título existente
- **THEN** os metadados são atualizados e o identificador e os registros relacionados permanecem preservados

#### Scenario: Título inexistente
- **WHEN** operação de edição referencia título inexistente
- **THEN** o backend recusa a atualização sem criar outro título

#### Scenario: Perfil sem privilégio tenta editar título
- **WHEN** estudante ou visitante tenta editar metadados de título
- **THEN** o backend recusa a alteração sem modificar o acervo
### Requirement: Título é desativado logicamente e reativado com histórico preservado

O sistema MUST usar o estado `ativo` do título para remoção lógica e reativação, sem excluir fisicamente título ou histórico, e deve revalidar empréstimos e reservas no backend antes da desativação.

#### Scenario: Desativar título sem empréstimo ou reserva ativa
- **WHEN** bibliotecário ou admin solicita desativar título sem empréstimo ativo e sem reserva ativa associada ao título ou a seus exemplares
- **THEN** o backend marca o título como inativo, preserva os registros relacionados e remove o título do catálogo público

#### Scenario: Bloquear desativação com empréstimo ativo
- **WHEN** título ou exemplar associado possui empréstimo não devolvido, considerando `devolvido_em` nulo ou zero como não devolvido
- **THEN** o backend recusa a desativação e mantém o título ativo e os registros inalterados

#### Scenario: Bloquear desativação com reserva ativa
- **WHEN** título ou exemplar associado possui reserva ativa segundo os estados definidos pelo contrato de reservas
- **THEN** o backend recusa a desativação e mantém o título ativo e a fila inalterada

#### Scenario: Reativar título
- **WHEN** bibliotecário ou admin reativa título desativado
- **THEN** o título volta a ser elegível para consulta pública, sem recriar o registro nem alterar o histórico existente

#### Scenario: Perfil sem privilégio tenta desativar ou reativar
- **WHEN** estudante ou visitante solicita desativação ou reativação
- **THEN** o backend recusa a operação sem alterar o título
### Requirement: Dados de demonstração são idempotentes

A API simulada MUST oferecer um catálogo de demonstração com metadados bibliográficos, categorias, exemplares e contas de teste, sem texto de obras, e repetir o seed não pode duplicar registros.

#### Scenario: Inicializar catálogo de demonstração
- **WHEN** a API simulada é inicializada ou o seed local é chamado
- **THEN** existem cerca de 30 títulos reais com título, autor e pelo menos uma categoria, quantidades variadas de exemplares, pelo menos seis categorias e contas de teste de estudante, bibliotecário e admin com e-mails `@example.invalid`

#### Scenario: Repetir seed local
- **WHEN** o seed da API simulada é executado mais de uma vez
- **THEN** títulos, categorias, vínculos, exemplares e contas existentes não são duplicados nem sobrescritos

#### Scenario: Preparar seed Xano
- **WHEN** o script de seed Xano é preparado para execução futura
- **THEN** ele usa contratos existentes de catálogo, lê endereço/token do ambiente de execução, inicia sem escritas e não é executado durante esta Change

### Requirement: Catálogo usa capas SVG geradas
O sistema MUST usar uma capa SVG determinística antes do fallback CSS quando não há `capa_url` HTTPS válido, mantendo contraste legível no título sem depender do tema da interface.

#### Scenario: Capa gerada para título sem imagem remota
- **WHEN** título não possui `capa_url` válido
- **THEN** a interface apresenta capa determinística baseada em título, autoria e categoria, com proporção 2:3 e texto alternativo

#### Scenario: Mesma capa em todas as apresentações
- **WHEN** título aparece na home, catálogo, detalhe ou Acervo
- **THEN** usa a prioridade URL HTTPS, capa gerada e fallback CSS

#### Scenario: Contraste do título na capa
- **WHEN** uma capa gerada exibe o título sobre a faixa colorida
- **THEN** escolhe texto claro ou escuro para obter contraste mínimo de 4,5:1 sobre a cor efetiva da faixa, sem variar por tema

### Requirement: Acervo usa lista compacta e edição única
A interface MUST apresentar o Acervo em lista vertical responsiva, com busca e apenas os painéis de edição ou exemplares selecionados abertos.

#### Scenario: Acervo abre com lista compacta
- **WHEN** bibliotecário ou admin abre o Acervo
- **THEN** vê busca no topo, cadastro fechado e uma linha por título com miniatura de 72 por 108 px, dados bibliográficos e operacionais e ações por título

#### Scenario: Dados e ações da linha
- **WHEN** linha de título está visível
- **THEN** apresenta título, autoria, categorias, estado, exemplares disponíveis sobre o total e ações Editar, Exemplares e Desativar ou Reativar

#### Scenario: Layout móvel do Acervo
- **WHEN** pessoa consulta o Acervo em tela estreita
- **THEN** capa fica à esquerda, dados à direita e ações aparecem abaixo em uma linha utilizável

#### Scenario: Novo título e edição única
- **WHEN** pessoa ativa Novo título ou Editar
- **THEN** cadastro começa fechado e somente o painel de edição do título selecionado pode estar aberto

#### Scenario: Painel único de exemplares
- **WHEN** pessoa abre Exemplares para um título
- **THEN** somente o painel de exemplares desse título fica aberto, sem manter aberto outro painel de edição ou exemplares

#### Scenario: Busca normalizada do Acervo
- **WHEN** pessoa busca por título, autoria ou ISBN
- **THEN** o filtro ignora caixa e acentos e apresenta “Nenhum título encontrado” para resultado vazio

#### Scenario: Paginação do Acervo
- **WHEN** há mais de dez títulos correspondentes
- **THEN** exibe dez por vez e permite revelar os próximos por Mostrar mais

#### Scenario: Títulos desativados ocultos por padrão
- **WHEN** bibliotecário ou admin abre o Acervo sem habilitar Mostrar desativados
- **THEN** títulos inativos não aparecem

#### Scenario: Exibir títulos desativados
- **WHEN** bibliotecário ou admin habilita Mostrar desativados
- **THEN** títulos inativos aparecem identificados como desativados

#### Scenario: Catálogo público nunca mostra título desativado
- **WHEN** visitante ou estudante consulta catálogo ou detalhe
- **THEN** títulos desativados não são apresentados, mesmo que a opção administrativa Mostrar desativados esteja ligada

#### Scenario: Staff edita pelo catálogo e detalhe
- **WHEN** staff consulta catálogo ou detalhe
- **THEN** vê “Editar este título” e é direcionado ao Acervo com o título selecionado

### Requirement: Ações administrativas têm confirmação e feedback
Ações destrutivas e assíncronas MUST informar processamento, pedir confirmação e mostrar o resultado confirmado pelo serviço junto ao recurso.

#### Scenario: Confirmação de desativação
- **WHEN** staff seleciona Desativar
- **THEN** a interface exige confirmar em dois passos antes da chamada

#### Scenario: Processamento visível
- **WHEN** ação administrativa está em andamento
- **THEN** o controle mostra “Processando...” e fica desabilitado

#### Scenario: Resultado seguro visível
- **WHEN** operação retorna sucesso, 404, 403 ou falha de conexão
- **THEN** a interface mostra mensagem simples próxima ao cartão, recarrega o estado e atualiza somente conforme o valor `ativo` confirmado pelo servidor

#### Scenario: Sucesso aparente na desativação
- **WHEN** chamada de desativação retorna sucesso mas a leitura posterior informa que o título continua ativo
- **THEN** o título permanece marcado como Ativo e a interface mostra “O servidor respondeu, mas o título continua ativo. A atualização do servidor pode não estar publicada”

#### Scenario: Erro na leitura posterior
- **WHEN** não é possível recarregar o título após uma tentativa de desativação
- **THEN** a interface informa a falha de confirmação e não apresenta o título como desativado

### Requirement: Seed de catálogo é seguro e idempotente
O script de seed MUST operar em dry-run por padrão, exigir `XANO_SEED_EMAIL` e `XANO_SEED_PASSWORD` para `--apply`, comparar títulos sem caixa e acentos e nunca criar categorias.

#### Scenario: Dry-run do seed
- **WHEN** script roda sem `--apply`
- **THEN** imprime primeiro “alvo: demonstração local”, apresenta somente o plano e não realiza chamadas de escrita

#### Scenario: Aplicação explícita do seed
- **WHEN** operador executa o script com `--apply` e credenciais presentes
- **THEN** a saída começa com “alvo: Xano remoto” e a execução usa as credenciais do ambiente sem imprimi-las

#### Scenario: Credenciais obrigatórias
- **WHEN** `--apply` é usado sem variáveis de ambiente válidas
- **THEN** o script aborta sem imprimir senha

#### Scenario: Seed idempotente
- **WHEN** título já existe normalizado ou categoria não existe
- **THEN** o script pula o título ou registra categoria inexistente sem criá-la

#### Scenario: Catálogo de demonstração planejado
- **WHEN** o plano padrão é preparado
- **THEN** inclui cerca de 30 títulos com descrições próprias e dois ou três exemplares por título

#### Scenario: Desativação de títulos de teste existentes
- **WHEN** `Jack Sparrow` ou `Something` existe no destino remoto
- **THEN** o plano identifica o título pelo nome exato normalizado para desativação sem adicioná-lo ao conjunto de títulos novos

#### Scenario: Seed remoto não executado durante validação
- **WHEN** testes locais verificam o script
- **THEN** não usam `--apply` nem gravam dados no Xano
