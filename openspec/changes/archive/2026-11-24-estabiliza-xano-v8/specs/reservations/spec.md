# Spec Delta

## ADDED Requirements

### Requirement: Falhas de carregamento de reservas são recuperáveis
As telas de reservas MUST encerrar o estado de carregamento em qualquer resultado e oferecer recuperação explícita quando uma leitura falhar.

#### Scenario: Leitura concluída
- **WHEN** a leitura de reservas termina com sucesso
- **THEN** o indicador de carregamento é encerrado e os dados ou estado vazio são apresentados

#### Scenario: Leitura falha após retries
- **WHEN** a leitura não pode ser concluída após as tentativas permitidas
- **THEN** o indicador é encerrado, a tela apresenta mensagem clara e botão “Tentar de novo”

#### Scenario: Nova tentativa manual
- **WHEN** pessoa ativa “Tentar de novo”
- **THEN** somente a leitura correspondente é refeita e o estado de carregamento é restaurado durante a operação
