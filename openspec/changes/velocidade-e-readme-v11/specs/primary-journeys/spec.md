# Spec Delta

## ADDED Requirements

### Requirement: Ações de escrita mostram estado otimista
A interface MUST refletir imediatamente uma ação iniciada pelo usuário e reconciliá-la com o resultado confirmado.

#### Scenario: Pedido de estudante enviado
- **WHEN** estudante solicita título elegível
- **THEN** a lista mostra “Enviando…”, o botão fica bloqueado e o pedido é substituído pelo registro real após confirmação

#### Scenario: Ação de equipe pendente
- **WHEN** equipe aceita ou recusa pedido, registra retirada ou devolução, ou desativa título
- **THEN** a interface mostra estado pendente e só confirma a ação após resposta e releitura exigida pelo fluxo

#### Scenario: Escrita falha
- **WHEN** uma escrita falha
- **THEN** a marca otimista é removida e a mensagem de erro com referência é apresentada sem repetir a escrita

### Requirement: Escritas sequenciais agrupam a atualização das listas
O cliente MUST serializar escritas no limitador e agrupar releituras das listas afetadas.

#### Scenario: Escritas concorrentes
- **WHEN** várias escritas são iniciadas próximas entre si
- **THEN** são executadas em sequência, com prioridade sobre leituras de fundo e sem retry automático de escrita

#### Scenario: Ações na janela de agrupamento
- **WHEN** uma ou mais escritas concluem dentro da janela de 1,5 segundo
- **THEN** uma única releitura atualiza as listas afetadas
