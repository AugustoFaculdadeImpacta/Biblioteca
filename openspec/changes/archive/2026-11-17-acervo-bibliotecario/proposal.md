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
- Na área pessoal, distinguir falhas de sessão, permissão, rota, serviço e resposta inválida, com ação para entrar novamente quando a sessão expirar.
- Preparar dados idempotentes de demonstração na API simulada e um script local de seed do catálogo Xano, sem executá-lo.
- Facilitar a abertura dos detalhes públicos do título a partir das solicitações e reservas da área pessoal do estudante.
- Permitir que bibliotecário/admin acompanhe solicitações e reservas em fila, confirme retiradas, recuse pedidos ainda pendentes, registre devoluções e consulte empréstimos ativos/atrasados.
- Aplicar o limite de três empréstimos ativos por estudante, permitindo títulos diferentes abaixo do limite e impedindo novo exemplar do mesmo título.

## Capabilities

### New Capabilities

### Modified Capabilities
- `catalog`: ampliar consulta e manutenção administrativa do acervo e definir desativação/reativação lógica.
- `loan-circulation`: recusar nova solicitação quando o título estiver desativado.
- `reservations`: recusar nova reserva quando o título estiver desativado.

## Impact

- Reflex: área administrativa para listar, cadastrar, editar, adicionar exemplares, desativar e reativar títulos.
- Reflex: vincular os títulos das solicitações e reservas pessoais à página pública de detalhes, preservando estados e prazos exibidos.
- Reflex: criar painel de circulação com solicitações, fila FIFO, retiradas, devoluções e resumo de empréstimos ativos/atrasados.
- API simulada: cerca de 30 títulos reais com autor, categoria e quantidades variadas, pelo menos seis categorias e contas de teste `@example.invalid`; o seed Xano cobre somente catálogo e exemplares, sem provisionar contas.
- Script Xano: usar contratos locais existentes, obter endereço e token do ambiente de execução, iniciar em modo de prévia e exigir opção explícita para escritas; não executar nesta Change.
- Xano: schema do título e operações de leitura/escrita necessárias; o contrato existente confirma `PATCH /catalogo/titulos/{tituloId}`, `POST /catalogo/titulos`, associações de categoria e criação de exemplares. `GET /admin/acervo` é um endpoint candidato aprovado para implementação local, ainda não confirmado no workspace remoto. Não haverá sincronização remota nesta Change local.
- Xano: preparar localmente listagem de empréstimos ativos, reservas administrativas e recusa de solicitações/reservas pendentes; não publicar durante esta Change.
- Testes pytest com transportes mockados, validação OpenSpec estrita e compilação Reflex.
- A alteração de autorização para admin depende da conclusão da Change `perfil-admin-xano`; até lá, somente a autorização de bibliotecário existente pode ser considerada confirmada.
