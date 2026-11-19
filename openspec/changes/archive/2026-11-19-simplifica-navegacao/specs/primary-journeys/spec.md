# Spec Delta

## ADDED Requirements

### Requirement: Home resume o catálogo com dados disponíveis
A página inicial MUST apresentar estatísticas calculadas exclusivamente dos dados públicos carregados, títulos em destaque, uma apresentação da biblioteca e atalhos correspondentes à identidade e visão ativa.

#### Scenario: Estatísticas com catálogo carregado
- **WHEN** o catálogo público e as categorias são carregados com sucesso
- **THEN** a home apresenta total de títulos ativos, total de exemplares disponíveis e total de categorias a partir desses resultados

#### Scenario: Catálogo vazio ou em erro
- **WHEN** o catálogo está carregando, vazio ou indisponível
- **THEN** a home apresenta o estado correspondente sem fabricar contagens ou indicar sucesso

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
