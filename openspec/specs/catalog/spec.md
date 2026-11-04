# catalog Specification

## Purpose

Define consulta pública e administração autorizada do acervo, preservando a distinção entre obra bibliográfica, categorias e exemplares físicos.

## Requirements

### Requirement: Catálogo é consultável publicamente
O sistema MUST permitir a visitantes consultar títulos e disponibilidade agregada sem autenticação, derivando disponibilidade dos exemplares elegíveis.

#### Scenario: Consulta pública
- **WHEN** visitante solicita o catálogo ou um título
- **THEN** o sistema retorna metadados bibliográficos publicados e disponibilidade agregada, sem dados pessoais de estudantes

#### Scenario: Disponibilidade por exemplares
- **WHEN** o sistema informa disponibilidade de um título
- **THEN** o resultado deriva dos exemplares físicos elegíveis e não de uma quantidade independente mantida no título

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
O sistema MUST autorizar no backend a criação/atualização de títulos, categorias e associações e a criação de exemplares somente para bibliotecários autenticados. Estados operacionais de exemplares são alterados somente pelos fluxos de empréstimo, reserva e condição.

#### Scenario: Bibliotecário mantém metadados do acervo
- **WHEN** bibliotecário autenticado cria ou atualiza título/categoria, associa título e categoria ou cria exemplar
- **THEN** o sistema aplica a alteração solicitada e a consulta posterior reflete o resultado

#### Scenario: Estudante ou visitante tenta administrar acervo
- **WHEN** estudante autenticado ou visitante tenta criar ou atualizar metadados, associar categorias ou criar exemplar
- **THEN** o backend recusa a operação sem alterar dados

#### Scenario: Remoção sem política aprovada
- **WHEN** uma operação tenta remover título, categoria, associação ou exemplar sem política de exclusão/arquivamento aprovada
- **THEN** o contrato não oferece a remoção e o estado persistido permanece inalterado

### Requirement: API de catálogo valida relações
O sistema MUST validar existência e compatibilidade das relações de título, categoria e exemplar antes de persistir alterações administrativas.

#### Scenario: Referência inválida
- **WHEN** pedido administrativo referencia título, categoria ou exemplar inexistente ou incompatível
- **THEN** o sistema recusa a alteração e preserva o estado anterior
