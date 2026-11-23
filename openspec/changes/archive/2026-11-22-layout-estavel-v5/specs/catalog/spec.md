# Spec Delta

## MODIFIED Requirements

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

#### Scenario: ISBN normalizado
- **WHEN** título possui ISBN
- **THEN** a URL usa ISBN-13 sem pontuação e solicita a capa grande da Open Library

#### Scenario: Falha da imagem real
- **WHEN** a imagem externa não carrega
- **THEN** o elemento real some e a capa gerada permanece visível

#### Scenario: ISBN normalizado
- **WHEN** título possui ISBN
- **THEN** a URL usa ISBN-13 sem pontuação e solicita a capa grande da Open Library

#### Scenario: Falha da imagem real
- **WHEN** a imagem externa não carrega
- **THEN** o elemento real some e a capa gerada permanece visível

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

#### Scenario: Linha do Acervo
- **WHEN** bibliotecário ou admin consulta o Acervo
- **THEN** cada título ocupa uma linha com capa pequena, dados e ações de editar, exemplares e desativar ou reativar

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

#### Scenario: Categorias aprovadas
- **WHEN** o plano é preparado
- **THEN** usa somente Literatura, Ciências, História, Geografia, Matemática, Infantil, Didáticos e Biografias

#### Scenario: Dry-run sem escrita
- **WHEN** script é executado sem `--apply`
- **THEN** imprime o alvo local e não autentica nem escreve no Xano

#### Scenario: Categorias aprovadas
- **WHEN** o plano é preparado
- **THEN** usa somente Literatura, Ciências, História, Geografia, Matemática, Infantil, Didáticos e Biografias
