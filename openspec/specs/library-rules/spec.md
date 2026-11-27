# library-rules Specification

## Purpose

Permite que admins consultem e configurem regras de circulação da biblioteca, enquanto estudantes veem os limites relevantes sem substituir a validação autoritativa do servidor.

## Requirements

### Requirement: Admin consulta e edita regras da biblioteca
A interface MUST oferecer a admins reais a página `/regras` com leitura e edição das regras vigentes.

#### Scenario: Acesso administrativo em qualquer visão
- **WHEN** admin real abre `/regras` em qualquer visão
- **THEN** acessa a página de regras; usuários que não sejam admin real não podem acessá-la

#### Scenario: Campos e padrões das regras
- **WHEN** admin abre a página sem configuração publicada
- **THEN** são apresentados `limite_emprestimos_ativos` (1–20, padrão 3), `limite_pedidos_em_aberto` (1–20, padrão 3), `permitir_pedido_com_reserva_ativa` (sim, padrão), `bloquear_com_atraso` (sim, padrão), `exigir_autorizacao_bibliotecaria` (sim, padrão), `prazo_emprestimo_dias` (1–60, padrão 14) e `prazo_retirada_horas` (1–168, padrão 48), cada qual com rótulo e ajuda em português simples

#### Scenario: Controles nativos e ações
- **WHEN** admin altera uma regra
- **THEN** números usam campos HTML numéricos, opções booleanas usam caixas de seleção, e a página oferece “Salvar regras” e “Descartar mudanças”

#### Scenario: Atualização da configuração
- **WHEN** existe metadado de atualização retornado pelo serviço
- **THEN** a interface mostra “Atualizado em … por …”

### Requirement: Regras são lidas e gravadas pelo contrato publicado
A aplicação MUST ler as regras por `GET /configuracoes` e gravá-las por `PUT /admin/configuracoes`, usando somente os sete campos do contrato no corpo da gravação.

#### Scenario: Leitura de regras
- **WHEN** a página solicita regras
- **THEN** o cliente chama `GET /configuracoes` pelo cliente Xano compartilhado

#### Scenario: Gravação de regras
- **WHEN** admin salva alterações válidas
- **THEN** o cliente envia `PUT /admin/configuracoes` com somente os sete campos da configuração

#### Scenario: Regras publicadas localmente para demonstração
- **WHEN** a API de demonstração recebe leitura ou gravação de configuração
- **THEN** implementa os mesmos endpoints, validações e restrições de circulação definidas neste contrato

### Requirement: Regras inválidas são rejeitadas e apresentadas
A interface MUST validar limites numéricos antes de salvar e apresentar erros retornados pelo servidor sem ocultá-los.

#### Scenario: Valores numéricos fora dos limites
- **WHEN** um campo numérico está fora de sua faixa permitida ou não é inteiro
- **THEN** a gravação não é enviada e a interface identifica o campo inválido

#### Scenario: Erro de validação do servidor
- **WHEN** o servidor rejeita a configuração
- **THEN** a interface apresenta a mensagem retornada em português seguro e preserva as alterações locais para correção

### Requirement: Regras ausentes no Xano ficam somente para consulta
A página MUST apresentar padrões somente leitura quando o endpoint de configuração responder 404 ou 403.

#### Scenario: Endpoint não publicado
- **WHEN** `GET /configuracoes` responde 404 ou 403
- **THEN** a página mostra “As regras ainda não foram publicadas no Xano. Veja docs/publicacao-xano-regras.md.” e exibe os padrões sem permitir gravação

### Requirement: Configuração em cache é atualizada após gravação
O cliente MUST reutilizar a configuração por até 60 segundos e invalidar o cache após gravação bem-sucedida.

#### Scenario: Leitura dentro do prazo de cache
- **WHEN** outra tela solicita a configuração dentro de 60 segundos
- **THEN** o cliente reutiliza o valor em cache

#### Scenario: Gravação invalida cache
- **WHEN** PUT de configuração termina com sucesso
- **THEN** o cache da configuração é invalidado e a nova configuração passa a ser usada

### Requirement: Detalhe informa limites vigentes ao estudante
O detalhe público do livro MUST apresentar os limites de pedidos vigentes em cache sem tratar essa informação como autorização da operação.

#### Scenario: Limite de pedidos visível
- **WHEN** estudante autenticado abre o detalhe de um livro e há configuração disponível
- **THEN** vê uma frase curta como “Você pode ter até N pedidos em aberto”

#### Scenario: Validação continua no servidor
- **WHEN** estudante solicita empréstimo ou reserva
- **THEN** o servidor revalida limites, atraso e elegibilidade mesmo que a interface tenha mostrado a configuração
