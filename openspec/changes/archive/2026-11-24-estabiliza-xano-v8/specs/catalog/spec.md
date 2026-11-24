# Spec Delta

## MODIFIED Requirements

### Requirement: Cartão de catálogo evita metadado repetido
Cada cartão MUST apresentar a categoria uma única vez como etiqueta e manter capa, título, autoria, disponibilidade e ação de detalhe legíveis.

#### Scenario: Categorias exibidas no cartão
- **WHEN** cartão de título possui uma ou mais categorias
- **THEN** as categorias aparecem na etiqueta sem uma segunda linha repetindo “Categorias:”

#### Scenario: Capa remota disponível ou ausente
- **WHEN** um cartão possui `capa_url` HTTPS ou não possui capa real
- **THEN** um contêiner com papel de imagem anuncia “Capa de «título»”, a imagem interna não repete o texto alternativo e uma falha da imagem real nunca mostra ícone quebrado

### Requirement: Catálogo usa capas SVG geradas
O sistema MUST manter a capa SVG determinística como base sempre visível sob fontes reais, respeitando a ordem de prioridade e o contraste legível sem depender do tema.

#### Scenario: Capa gerada para título sem imagem remota
- **WHEN** título não possui `capa_url`, capa resolvida ou ISBN informado utilizável
- **THEN** a interface apresenta a capa determinística baseada em título, autoria e categoria, com proporção 2:3

#### Scenario: Mesma capa em todas as apresentações
- **WHEN** título aparece na home, catálogo, detalhe ou Acervo
- **THEN** a capa gerada permanece por baixo da imagem real e o fallback visual é consistente

#### Scenario: Contraste do título na capa
- **WHEN** uma capa gerada exibe o título sobre a faixa colorida
- **THEN** escolhe texto claro ou escuro para obter contraste mínimo de 4,5:1 sobre a cor efetiva da faixa, sem variar por tema

#### Scenario: ISBN normalizado
- **WHEN** título possui ISBN-13 válido e a busca por título/autoria não resolve capa
- **THEN** usa ISBN normalizado como fonte alternativa da imagem real mantendo a capa gerada por baixo

#### Scenario: Falha da imagem real
- **WHEN** a imagem externa não carrega
- **THEN** ela desaparece sem texto alternativo visível e a capa gerada permanece visível

#### Scenario: Falha da imagem real
- **WHEN** a imagem externa não carrega
- **THEN** ela desaparece sem ícone quebrado ou texto alternativo visível, e a capa gerada permanece visível

#### Scenario: ISBN normalizado
- **WHEN** título possui ISBN-13 válido
- **THEN** o fallback usa somente o ISBN do registro, sem consultar um índice local de ISBN

### Requirement: Admin importa livros de exemplo pelo Acervo
A interface MUST oferecer ao admin real prévia somente leitura e importação confirmada dos livros de exemplo, preservando registros e permitindo retomar após falhas transitórias.

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
- **THEN** a operação ocorre em segundo plano, informa o progresso de 1 a 30, espera 1,5 s entre gravações e mantém a página interativa

#### Scenario: Repetir etapa após resultado incerto
- **WHEN** uma etapa de gravação falha por 429, 5xx, timeout ou conexão
- **THEN** a interface relê o catálogo antes de tentar novamente a mesma etapa, evita duplicatas e limita a três repetições

#### Scenario: Retomar importação
- **WHEN** importação parou após falha transitória
- **THEN** admin real pode selecionar “Continuar importação” e a execução relê o catálogo para pular gravações concluídas e prosseguir com as pendentes

#### Scenario: Parada após falhas repetidas
- **WHEN** a etapa continua falhando após três repetições
- **THEN** a operação para, exibe resumo de criados, ignorados e erros e oferece retomada sem reiniciar gravações já confirmadas

#### Scenario: Repetir importação
- **WHEN** admin real executa novamente a importação
- **THEN** pares de título e autoria existentes, ignorando caixa e acentos, não são criados novamente

#### Scenario: Interromper em erro inesperado
- **WHEN** uma etapa continua falhando após três repetições limitadas ou encontra erro permanente
- **THEN** a operação para, exibe resumo de criados, ignorados e erros e oferece “Continuar importação” sem repetir gravações já confirmadas

#### Scenario: Segredos permanecem privados
- **WHEN** a prévia ou importação falha
- **THEN** mensagens e logs não mostram token, senha, e-mail ou cabeçalho de autorização

## ADDED Requirements

### Requirement: Admin real testa a comunicação pública do Acervo
O Acervo MUST oferecer ao admin real uma ação somente de leitura para medir cinco chamadas públicas ao Xano em sequência.

#### Scenario: Teste autorizado
- **WHEN** admin real seleciona “🩺 Testar conexão”
- **THEN** o sistema executa cinco leituras públicas sequenciais e mostra quantas passaram, a mais lenta em milissegundos e o primeiro código de erro

#### Scenario: Dica para limite de chamadas
- **WHEN** uma das leituras recebe HTTP 429
- **THEN** o resultado inclui “se aparecer 429, o plano do Xano está limitando as chamadas”

#### Scenario: Acesso sem privilégio
- **WHEN** visitante, estudante ou bibliotecário abre o Acervo
- **THEN** a ação de teste não é exibida e nenhuma leitura de diagnóstico é iniciada

### Requirement: Lista de exemplo mantém os títulos literários requeridos
Os dados compartilhados dos livros de exemplo MUST preservar a lista existente sem alteração nesta Change.

#### Scenario: Obras brasileiras permanecem no seed
- **WHEN** os dados de exemplo são validados
- **THEN** continuam presentes “Dom Casmurro” e “Memórias Póstumas de Brás Cubas”
