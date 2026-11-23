# Spec Delta

## ADDED Requirements

### Requirement: Jornada principal usa navegação estável
O sistema MUST adaptar home, catálogo, detalhe, reservas, login e cadastro ao padrão visual consistente de app de delivery.

#### Scenario: Home compacta
- **WHEN** pessoa abre a home
- **THEN** vê boas-vindas compacta, pílulas de categoria e fileiras roláveis por categoria usando dados reais

#### Scenario: Detalhe como produto
- **WHEN** pessoa abre detalhe de livro
- **THEN** vê capa à esquerda, dados à direita e um único botão principal de reserva ou entrada

#### Scenario: Reservas por abas
- **WHEN** estudante abre reservas
- **THEN** vê abas de acompanhamento com contadores e somente uma aba ativa por vez

#### Scenario: Login e cadastro sem navegação extra
- **WHEN** visitante abre login ou cadastro
- **THEN** vê um cartão central estreito com abas Entrar/Criar conta e somente campos e mensagens do fluxo
