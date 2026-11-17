# Spec Delta

## ADDED Requirements

### Requirement: Navegação administrativa oferece acesso às reservas por estudante
A interface MUST oferecer acesso à tela de reservas administrativas somente a bibliotecários e admins autenticados, mantendo a autorização do backend para qualquer busca ou criação.

#### Scenario: Bibliotecário abre a navegação
- **WHEN** bibliotecário autenticado abre o cabeçalho compartilhado
- **THEN** vê um link para a área de reservas administrativas em `/admin/reservas`

#### Scenario: Admin abre a navegação
- **WHEN** admin autenticado abre o cabeçalho compartilhado
- **THEN** vê o mesmo link de reservas administrativas disponível ao bibliotecário

#### Scenario: Visitante ou estudante abre a navegação
- **WHEN** visitante ou estudante abre o cabeçalho compartilhado
- **THEN** não vê o link de reservas administrativas

#### Scenario: Perfil sem privilégio tenta acessar a tela
- **WHEN** visitante ou estudante acessa diretamente `/admin/reservas`
- **THEN** a interface bloqueia ou redireciona e não envia busca de estudante nem criação de reserva
