# primary-journeys Specification

## Purpose

Descrever os percursos integrados que conectam identidade, catálogo, circulação e acervo para que estudante e bibliotecário consigam concluir as tarefas prioritárias com resultados claros e sem alterar regras de domínio existentes.

## Requirements

### Requirement: Estudante percorre cadastro, catálogo e solicitação
A interface MUST permitir que estudante conclua o percurso de entrada, descubra um título e acompanhe uma solicitação ou reserva usando os resultados confirmados pelos serviços.

#### Scenario: Estudante solicita título disponível
- **WHEN** visitante conclui o cadastro ou estudante entra, abre um título disponível e solicita empréstimo
- **THEN** a interface mantém a sessão conforme o perfil retornado, mostra a confirmação somente após resposta de sucesso e permite consultar o estado na área pessoal

#### Scenario: Estudante solicita título indisponível
- **WHEN** estudante autenticado abre título sem exemplar disponível e escolhe solicitar reserva
- **THEN** a interface apresenta o resultado confirmado da solicitação e permite acompanhar a reserva sem inventar posição ou prazo

### Requirement: Bibliotecário percorre cadastro e circulação
A interface MUST permitir que bibliotecário percorra as tarefas operacionais existentes sem perder o resultado confirmado de cada etapa.

#### Scenario: Bibliotecário cadastra título e exemplares
- **WHEN** bibliotecário autenticado informa os dados obrigatórios, associa categorias existentes e cria exemplares
- **THEN** a interface apresenta identificadores e códigos de tombo retornados e permite conferir o título no acervo

#### Scenario: Bibliotecário processa circulação
- **WHEN** bibliotecário autenticado confirma retirada ou devolução por uma ação disponível no painel
- **THEN** a interface atualiza a lista com o estado retornado e não apresenta como concluída uma ação recusada

### Requirement: Jornadas apresentam erros de integração com segurança
A interface MUST distinguir falhas de entrada, autenticação/autorização, conflito, servidor e comunicação sem expor conteúdo interno nem simular sucesso.

#### Scenario: Sessão expirada ou perfil sem permissão
- **WHEN** uma operação da jornada recebe recusa de autenticação ou autorização
- **THEN** a interface orienta a pessoa em português, não apresenta sucesso e não expõe corpo técnico da resposta

#### Scenario: Falha de comunicação após uma escrita
- **WHEN** o resultado de uma escrita fica incerto por falha de transporte
- **THEN** a interface informa que é necessário conferir o estado antes de repetir e não repete a escrita automaticamente

#### Scenario: Dados inválidos ou resposta incompatível
- **WHEN** formulário contém dados inválidos ou o serviço retorna uma resposta incompatível com o contrato
- **THEN** a interface informa o problema com segurança e não avança a jornada como se a operação tivesse sido concluída

### Requirement: Home resume o catálogo com dados disponíveis
A página inicial MUST apresentar estatísticas calculadas exclusivamente dos dados públicos carregados, títulos em destaque, uma apresentação da biblioteca e atalhos correspondentes à identidade e visão ativa.

#### Scenario: Estatísticas com catálogo carregado
- **WHEN** o catálogo público e as categorias são carregados com sucesso
- **THEN** a home apresenta total de títulos ativos, total de exemplares disponíveis e total de categorias a partir desses resultados

#### Scenario: Carregamento independente dos indicadores
- **WHEN** a home inicia o carregamento do resumo
- **THEN** cada indicador é carregado e atualizado independentemente, sem aguardar o sucesso dos demais

#### Scenario: Falha isolada de indicador
- **WHEN** a leitura de um indicador falha
- **THEN** somente aquele indicador apresenta “—” e um link “Tentar de novo”, enquanto os demais resultados válidos permanecem visíveis

#### Scenario: Catálogo vazio ou em erro
- **WHEN** o catálogo está carregando, vazio ou indisponível
- **THEN** a home apresenta o estado correspondente sem fabricar contagens; falha de leitura afeta somente os indicadores dependentes e mantém resultados independentes

#### Scenario: Visitante na home
- **WHEN** visitante abre a página inicial
- **THEN** vê boas-vindas, busca, acesso ao catálogo, destaques reais, apresentação da biblioteca e ações Entrar e Cadastrar-se

#### Scenario: Atalhos pessoais e operacionais
- **WHEN** estudante, bibliotecário ou admin abre a home
- **THEN** vê atalhos pertinentes ao perfil e à visão ativa, sem ações que o perfil não pode executar

#### Scenario: Atalhos de estudante
- **WHEN** estudante autenticado abre a home
- **THEN** vê um atalho para Reservas

#### Scenario: Atalhos de bibliotecário
- **WHEN** bibliotecário autenticado abre a home
- **THEN** vê atalhos para Acervo e Reservas

#### Scenario: Atalho de admin
- **WHEN** admin está na visão Administrador e abre a home
- **THEN** vê um atalho para Contas

#### Scenario: Atalhos de visão simulada
- **WHEN** admin abre a home em visão Bibliotecário ou Estudante
- **THEN** vê os atalhos da visão ativa sem receber permissões ou consultas de dados do perfil simulado

#### Scenario: Popularidade sem contagem disponível
- **WHEN** a API ou os dados já carregados não fornecem contagens de empréstimos por título
- **THEN** a home não exibe uma seção “Livros que mais saem” nem infere popularidade a partir de disponibilidade

### Requirement: Jornadas operacionais agrupam ações já disponíveis
A interface MUST oferecer entradas concisas para as operações existentes de bibliotecário e admin, sem ampliar autorização nem simular operações não suportadas pelo cliente ou backend.

#### Scenario: Bibliotecário abre Reservas
- **WHEN** bibliotecário autenticado abre Reservas
- **THEN** encontra abas acessíveis para Pedidos e Empréstimos e devoluções que reutilizam as operações atuais de reservas e circulação

#### Scenario: Admin abre Contas
- **WHEN** admin autenticado abre Contas
- **THEN** pode pesquisar e gerir as contas e situações que os contratos atuais suportam, sem expor senhas ou oferecer alteração genérica de perfil sem operação aprovada

#### Scenario: Ação de conta fora do contrato atual
- **WHEN** a API atual não oferece operação para promover ou rebaixar perfil de uma conta
- **THEN** a interface não simula nem envia essa alteração e a limitação é registrada como dependência de validação do contrato

#### Scenario: Indicadores operacionais incompletos
- **WHEN** os dados carregados não permitem contar pedidos pendentes ou devoluções do dia
- **THEN** a interface omite esses contadores em vez de estimá-los

#### Scenario: Contadores operacionais deriváveis
- **WHEN** bibliotecário abre a área operacional e as listas existentes foram carregadas
- **THEN** pode ver pedidos pendentes, empréstimos em atraso e devoluções previstas para hoje calculados dessas listas, sem nova consulta ou inferência de devolução já concluída

#### Scenario: Ferramentas administrativas adiadas
- **WHEN** pessoa usa as áreas de bibliotecário ou admin nesta Change
- **THEN** indicadores avançados, regras de empréstimo, auditoria, exportação CSV e aviso geral não aparecem como funcionalidades implementadas

### Requirement: Jornada principal usa navegação estável
O sistema MUST adaptar home, catálogo, detalhe, reservas, login e cadastro ao padrão visual consistente de app de delivery.

#### Scenario: Home compacta
- **WHEN** pessoa abre a home
- **THEN** vê boas-vindas compacta, pílulas de categoria e fileiras roláveis por categoria usando dados reais

#### Scenario: Detalhe como produto
- **WHEN** pessoa abre detalhe de livro
- **THEN** vê capa à esquerda, dados à direita e um único botão principal de reserva ou entrada

#### Scenario: Reservas por abas
- **WHEN** estudante abre reservas
- **THEN** vê abas de acompanhamento com contadores e somente uma aba ativa por vez

#### Scenario: Login e cadastro sem navegação extra
- **WHEN** visitante abre login ou cadastro
- **THEN** vê um cartão central estreito com abas Entrar/Criar conta e somente campos e mensagens do fluxo

### Requirement: Controles do cabeçalho mantêm contraste acessível
O texto dos controles “Perfil” e “Acessibilidade” MUST manter contraste mínimo de 4,5:1 contra o fundo nos temas claro e escuro, em repouso, hover e foco, usando tokens de tema sem alterar a geometria aprovada.

#### Scenario: Contraste do cabeçalho
- **WHEN** o cabeçalho é renderizado em tema claro ou escuro
- **THEN** os rótulos dos dois controles atingem pelo menos 4,5:1 em repouso, hover e foco
