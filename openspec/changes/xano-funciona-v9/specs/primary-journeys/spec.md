# Spec Delta

## MODIFIED Requirements

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
