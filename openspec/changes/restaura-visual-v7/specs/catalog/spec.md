# Spec Delta

## ADDED Requirements

### Requirement: Pílulas de categoria exibem contagens reais
As pílulas de categoria do catálogo MUST usar contagens calculadas a partir dos títulos ativos ou omitir a contagem quando ela não estiver disponível.

#### Scenario: Categoria com títulos
- **WHEN** categoria tem títulos ativos no catálogo
- **THEN** a pílula mostra a quantidade real de títulos associados

#### Scenario: Categoria sem títulos
- **WHEN** categoria não tem títulos ativos
- **THEN** a pílula mostra zero, sem parênteses vazios

#### Scenario: Contagem ausente
- **WHEN** a interface recebe uma categoria sem valor de contagem
- **THEN** mostra somente o nome da categoria, sem `()`

### Requirement: Cartões públicos de livros mantêm proporção e largura
A grade pública de livros MUST manter cartões compactos de 190 px a 220 px e capas na proporção 2:3, sem ampliar cartões para preencher espaços vazios.

#### Scenario: Poucos títulos
- **WHEN** a grade contém poucos títulos
- **THEN** as colunas começam em 190 px, não excedem 220 px e ficam alinhadas ao início

#### Scenario: Muitos títulos
- **WHEN** a largura disponível permite várias colunas
- **THEN** a grade preenche a linha com colunas de até 220 px, preservando o espaçamento entre cartões

#### Scenario: Capa de livro
- **WHEN** cartão apresenta capa remota, gerada ou fallback
- **THEN** sua caixa visual preserva a proporção 2:3

### Requirement: Livros de exemplo têm metadados consistentes
O conjunto de livros de exemplo MUST conter 30 títulos distintos com autoria, ISBN-13 válido, ano, editora, descrição curta própria, categoria e quantidade de exemplares entre dois e três.

#### Scenario: Validar o conjunto de exemplo
- **WHEN** testes locais validam os dados de exemplo
- **THEN** encontram 30 títulos distintos, ISBN-13 com dígito verificador válido e todos os campos definidos

#### Scenario: Quantidade de exemplares
- **WHEN** um livro de exemplo é importado
- **THEN** são solicitados os dois ou três exemplares definidos para aquele título

### Requirement: Admin importa livros de exemplo pelo Acervo
A interface MUST oferecer ao admin real uma prévia somente leitura e uma importação confirmada dos livros de exemplo, usando apenas categorias existentes e preservando os registros atuais.

#### Scenario: Acesso restrito
- **WHEN** visitante, estudante ou bibliotecário abre o Acervo
- **THEN** a seção “📥 Livros de exemplo” não é exibida nem inicia chamadas de importação

#### Scenario: Seção recolhida
- **WHEN** admin real abre o Acervo
- **THEN** encontra a seção recolhida com a descrição “Adiciona 30 livros reais ao acervo, com 2 ou 3 exemplares cada. Livros que já existem são ignorados.”

#### Scenario: Prévia sem escrita
- **WHEN** admin real ativa “Ver o que será adicionado”
- **THEN** a interface lê o catálogo e as categorias do servidor e mostra quantos títulos serão criados, quantos já existem e quais categorias não existem, sem enviar chamadas de escrita

#### Scenario: Categoria inexistente
- **WHEN** a categoria de um livro de exemplo não existe no servidor
- **THEN** a interface a identifica na prévia e não cria a categoria nem um título sem o vínculo necessário

#### Scenario: Confirmação e importação sequencial
- **WHEN** admin real confirma “Adicionar agora”
- **THEN** a interface cria cada título, associação e exemplar sequencialmente com a sessão do admin, mostra o progresso de 1 a 30 e recarrega o catálogo ao terminar

#### Scenario: Repetir importação
- **WHEN** admin real executa novamente a importação após os títulos terem sido criados
- **THEN** pares de título e autoria que já existem, ignorando caixa e acentos, não são criados novamente

#### Scenario: Interromper em erro inesperado
- **WHEN** uma operação retorna 401, 403, 5xx, resposta inválida ou tempo esgotado
- **THEN** a importação para no primeiro erro, informa os totais criados, ignorados e com erro e não repete automaticamente escritas confirmadas

#### Scenario: Segredos permanecem privados
- **WHEN** a prévia ou importação falha
- **THEN** mensagens e logs não mostram token, senha, e-mail ou cabeçalho de autorização
