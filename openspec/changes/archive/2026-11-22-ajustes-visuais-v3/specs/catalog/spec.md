# Spec Delta

## ADDED Requirements

### Requirement: Catálogo usa capas SVG geradas
O sistema MUST usar uma capa SVG determinística antes do fallback CSS quando não há `capa_url` HTTPS válido.

#### Scenario: Capa gerada para título sem imagem remota
- **WHEN** título não possui `capa_url` válido
- **THEN** a interface apresenta capa determinística baseada em título, autoria e categoria, com proporção 2:3 e texto alternativo

#### Scenario: Mesma capa em todas as apresentações
- **WHEN** título aparece na home, catálogo, detalhe ou Acervo
- **THEN** usa a prioridade URL HTTPS, capa gerada e fallback CSS

### Requirement: Acervo usa lista compacta e edição única
A interface MUST apresentar o Acervo em lista compacta buscável e abrir somente um painel de edição por vez.

#### Scenario: Acervo abre com lista compacta
- **WHEN** staff abre o Acervo
- **THEN** vê busca no topo, cadastro fechado, miniaturas e ações por título

#### Scenario: Novo título e edição única
- **WHEN** pessoa ativa Novo título ou Editar
- **THEN** cadastro começa fechado e somente o título selecionado pode estar em edição

#### Scenario: Busca normalizada do Acervo
- **WHEN** pessoa busca por título, autoria ou ISBN
- **THEN** o filtro ignora caixa e acentos e apresenta “Nenhum título encontrado” para resultado vazio

#### Scenario: Staff edita pelo catálogo e detalhe
- **WHEN** staff consulta catálogo ou detalhe
- **THEN** vê “Editar este título” e é direcionado ao Acervo com o título selecionado

### Requirement: Ações administrativas têm confirmação e feedback
Ações destrutivas e assíncronas MUST informar processamento, pedir confirmação e mostrar resultado seguro junto ao recurso.

#### Scenario: Confirmação de desativação
- **WHEN** staff seleciona Desativar
- **THEN** a interface exige confirmar em dois passos antes da chamada

#### Scenario: Processamento visível
- **WHEN** ação administrativa está em andamento
- **THEN** o controle mostra “Processando...” e fica desabilitado

#### Scenario: Resultado seguro visível
- **WHEN** operação retorna sucesso, 404, 403 ou falha de conexão
- **THEN** a interface mostra mensagem simples próxima ao cartão e atualiza o estado somente após sucesso

### Requirement: Seed de catálogo é seguro e idempotente
O script de seed MUST operar em dry-run por padrão, exigir credenciais para `--apply` e comparar títulos e categorias sem criar categorias.

#### Scenario: Dry-run do seed
- **WHEN** script roda sem `--apply`
- **THEN** imprime somente o plano e não realiza chamadas de escrita

#### Scenario: Credenciais obrigatórias
- **WHEN** `--apply` é usado sem variáveis de ambiente válidas
- **THEN** o script aborta sem imprimir senha

#### Scenario: Seed idempotente
- **WHEN** título já existe normalizado ou categoria não existe
- **THEN** o script pula o título ou registra categoria inexistente sem criá-la
