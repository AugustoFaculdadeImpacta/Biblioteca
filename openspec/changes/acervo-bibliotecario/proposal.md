# Proposal

## Why

Bibliotecários precisam consultar e manter o acervo completo, inclusive exemplares indisponíveis, sem perder o histórico quando um título deixa de ser oferecido. A operação de remoção deve preservar registros e impedir desativação enquanto houver empréstimo ou reserva ativa.

## What Changes

- Disponibilizar uma área administrativa para consultar todos os títulos, exemplares e estados operacionais, identificando títulos desativados.
- Permitir cadastrar título com categorias e exemplares, adicionar exemplares a título existente e editar metadados.
- Remover títulos somente por desativação lógica; bloquear a ação quando houver empréstimo ou reserva ativa e permitir reativação.
- Ocultar títulos desativados do catálogo público e recusar novas solicitações e reservas para eles no backend.
- Exigir autenticação e autorização de bibliotecário ou admin no backend para operações administrativas; a interface não substitui essa validação.
- Preservar histórico e nunca excluir fisicamente título, exemplar, empréstimo ou reserva por esta capability.

## Capabilities

### New Capabilities

### Modified Capabilities
- `catalog`: ampliar consulta e manutenção administrativa do acervo e definir desativação/reativação lógica.
- `loan-circulation`: recusar nova solicitação quando o título estiver desativado.
- `reservations`: recusar nova reserva quando o título estiver desativado.

## Impact

- Reflex: área administrativa para listar, cadastrar, editar, adicionar exemplares, desativar e reativar títulos.
- Xano: schema do título e operações de leitura/escrita necessárias; o contrato existente confirma `PATCH /catalogo/titulos/{tituloId}`, `POST /catalogo/titulos`, associações de categoria e criação de exemplares. Não há hoje campo de ativação nem consulta administrativa completa; nenhum endpoint novo será presumido sem validação do contrato.
- Testes pytest com transportes mockados, validação OpenSpec estrita e compilação Reflex.
- A alteração de autorização para admin depende da conclusão da Change `perfil-admin-xano`; até lá, somente a autorização de bibliotecário existente pode ser considerada confirmada.
