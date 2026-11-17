# Proposal

## Why

Bibliotecários precisam registrar uma reserva solicitada presencialmente por um estudante sem usar a conta ou credenciais do estudante. A criação deve seguir exatamente a elegibilidade e a ordem FIFO existentes, sem permitir que a operação administrativa favoreça alguém na fila.

## What Changes

- Permitir que bibliotecário autenticado encontre um estudante por e-mail exato normalizado, com retorno mínimo de identidade.
- Permitir registrar reserva em nome do estudante selecionado, com autenticação e autorização verificadas no backend.
- Revalidar atraso, empréstimo ativo do título, reserva ativa duplicada e situação do título; inserir a nova reserva no fim da fila FIFO.
- Não emitir sessão de estudante, não aceitar credenciais do estudante e não oferecer exceção para furar a fila.
- Exibir busca e confirmação em uma área administrativa acessível somente a bibliotecário/admin.

## Capabilities

### New Capabilities

### Modified Capabilities
- `reservations`: permitir busca restrita de estudante e inclusão administrativa de reserva, preservando as regras de elegibilidade e FIFO.
- `frontend-foundation`: incluir navegação à área de reservas administrativas para perfis autorizados.

## Impact

- Reflex: tela de busca de estudante e criação de reserva para bibliotecário/admin, com mensagens seguras e sem armazenar credenciais estudantis.
- Xano: operações autenticadas de busca mínima de estudante e criação de reserva por estudante informado. `GET /admin/estudantes?email=` e `POST /admin/reservas` são contratos candidatos aprovados para implementação local, ainda não encontrados no pull remoto.
- Testes pytest com transportes mockados, validação OpenSpec estrita e compilação Reflex.
- A criação para título inativo depende da conclusão de `acervo-bibliotecario`; a autorização de admin depende de `perfil-admin-xano`. Nenhuma dessas permissões será presumida enquanto o backend não as confirmar.
