# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de [catalog](./specs/catalog/spec.md), [loan-circulation](./specs/loan-circulation/spec.md) e [reservations](./specs/reservations/spec.md).

O Xano local confirma criação de título, associação a categoria, criação de exemplar e `PATCH /catalogo/titulos/{tituloId}`. A tabela `titulo` não contém `ativo`; o catálogo público não lista exemplares individualmente; não há contrato local para listar o acervo administrativo completo, desativar ou reativar título. A tela Reflex atual cadastra títulos e exemplares, mas não consulta nem edita o acervo completo.

## Goals / Non-Goals

**Goals:**
- Evoluir o título e seus fluxos de maneira vertical, preservando histórico e as regras existentes de circulação.
- Fazer da API Xano a autoridade para filtros de autorização, estado ativo e impedimentos por empréstimo/reserva.
- Reutilizar os contratos existentes de criação, edição, categoria e exemplar quando compatíveis.
- Tornar falhas de carregamento da área pessoal compreensíveis e recuperáveis sem expor detalhes internos do serviço.

**Non-Goals:**
- Criar ou alterar qualquer dado de empréstimo/reserva fora da validação necessária à desativação.
- Remover fisicamente registros ou alterar estados operacionais dos exemplares por uma ação de acervo.
- Inventar endpoints Xano ou sincronizar arquivos sem validar seu contrato e o dry-run unitário.

## Decisions

### Estado ativo do título

Usar o campo conceitual `ativo` no título para desativação lógica. Títulos existentes e novos devem iniciar ativos para preservar o comportamento público atual. A desativação nunca apaga o título nem seus exemplares/histórico; a reativação altera somente esse estado.

**Alternativa considerada:** apagar o título ou exemplares; rejeitada porque destrói referências históricas e não atende à remoção lógica aprovada.

### Bloqueios de desativação

O backend deve revalidar empréstimos e reservas associados ao título e a todos os exemplares imediatamente antes da mudança de estado. Empréstimo sem devolução inclui `devolvido_em` nulo ou zero. Reserva ativa é determinada pelos estados ativos do contrato de reservas existente; não criar novos estados nesta Change. Uma verificação apenas na interface não é suficiente. Se o Xano não permitir uma operação consistente contra condições concorrentes, a desativação não deve ser habilitada até essa garantia ser validada.

**Alternativa considerada:** consultar bloqueios no cliente e depois enviar a desativação; rejeitada porque o estado pode mudar entre consulta e gravação.

### Contratos administrativos locais

O OpenAPI local confirma `PATCH /catalogo/titulos/{tituloId}`, mas não oferece listagem de todos os títulos com exemplares/estados. Por decisão delegada, `GET /admin/acervo` é um candidato aprovado para implementação local e o PATCH existente aceitará a alteração opcional de `ativo`. Esses contratos não foram encontrados no pull remoto e não serão sincronizados nesta sessão. A listagem completa deve permanecer autenticada e autorizada no servidor.

**Alternativa considerada:** reutilizar a listagem pública para a interface administrativa; rejeitada porque ela omite exemplares individuais e não pode incluir títulos desativados.

### Perfis e autorização

Todas as consultas e mutações administrativas exigem autenticação e validação no servidor para bibliotecário/admin. A paridade de `admin` depende da Change `perfil-admin-xano`; até o Xano aceitar e autorizar esse perfil, não afirmar que as operações administrativas reais estão disponíveis a admin. Visitantes e estudantes não recebem consultas ou mutações administrativas.

**Alternativa considerada:** ocultar ações apenas no Reflex; rejeitada porque a interface não é uma fronteira de autorização.

### Falhas ao carregar Minha biblioteca

As chamadas pessoais preservam o token em estado privado e o enviam como `Authorization: Bearer`. A interface não deve presumir que o token foi enviado incorretamente: a causa de um 401 depende da sessão real. O cliente distingue 401 (sessão inválida, limpar a sessão e oferecer link para entrar novamente), 403 (sem permissão), 404 (recurso/rota indisponível), 5xx ou timeout (serviço temporariamente indisponível) e payload inválido. Mensagens não incluem corpo de resposta, token ou URL. O alerta continua acessível e os estados vazios atuais permanecem intactos.

**Alternativa considerada:** trocar o token ou usar a API demo automaticamente após erro; rejeitada porque não há evidência da causa e isso ocultaria falhas de configuração/autorização.

### Operação e validação Xano

O CLI confirmou workspace `151966`, branch `v1` live, grupo Biblioteca e `allow_push=false`; sandbox push não oferece filtro unitário `-i`. O pull somente de definições desta sessão contém 57 documentos em uma pasta temporária fora do repositório. Nenhuma escrita será enviada ao Xano. Não alterar `allow_push`, não usar sandbox push nem sincronizar `xano/`. O Xano Developer MCP valida sintaxe local e informa documentação, mas não garante execução, concorrência ou publicação no workspace; contratos não encontrados no pull permanecem candidatos locais. Antes de qualquer operação remota futura, repetir a identificação do destino, obter pull isolado e rollback fora do repositório, e exigir dry-run unitário de um único CREATE/UPDATE para cada arquivo.

Enquanto o backend estiver bloqueado, os testes de interface/clientes usam respostas mockadas. Nenhum teste mockado será descrito como verificação contra Xano real.

## Risks / Trade-offs

- [O campo `ativo` exige migração de schema] → preservar todos os registros; a migração remota continua pendente e não será feita nesta sessão.
- [A lista administrativa pode expor dados operacionais] → autenticação e perfil verificados no backend; nunca usar o GET público como substituto.
- [Corrida entre verificação de empréstimos/reservas e desativação] → revalidar no servidor com garantia de consistência; bloquear a ação se essa garantia não puder ser comprovada.
- [A Change `perfil-admin-xano` está incompleta] → manter o acesso de admin pendente até conclusão backend daquela Change.
- [Destino Xano recusa push filtrado] → manter tarefas remotas pendentes; não alterar preferências ou contornar o gate.

## Migration Plan

1. Para este Apply, manter todas as mudanças Xano somente em arquivos locais e validar cada arquivo com o Xano Developer MCP.
2. Não alterar dados remotos: push, sandbox, fixtures sintéticas, prova de concorrência e limpeza ficam NÃO EXECUTADOS.
3. Antes de uma publicação futura, reidentificar o destino, obter pull isolado e cópia de rollback fora do repositório, e enviar apenas após dry-run unitário revisado.

## Decisões tomadas por delegação (revisar)

- `titulo.ativo` é booleano com padrão verdadeiro; `ativo` ausente ou nulo em título legado significa ativo.
- A desativação é lógica; títulos inativos somem de todas as rotas públicas, mas permanecem na listagem completa do acervo com o estado visível e podem ser reativados.
- Título inativo não aceita novas solicitações de empréstimo ou reservas; filas existentes não são alteradas.
- Bloquear remoção lógica se existir qualquer empréstimo ainda não devolvido (`devolvido_em` nulo ou zero) ou reserva ativa (`aguardando`/`ofertada`) associada ao título ou a seus exemplares.
- Não remover fisicamente títulos com histórico nem seus exemplares.
- A interface usa o candidato local `GET /admin/acervo` para listar títulos, exemplares e estados; a consulta é restrita no backend.
- `PATCH /catalogo/titulos/{titulo_id}` será reutilizado para edição e alteração de `ativo`; o contrato `ativo` é candidato local e não foi confirmado no Xano remoto.
- As operações de acervo são para bibliotecário/admin e são verificadas no servidor. Nenhuma verificação mockada equivale à validação remota ou garante atomicidade concorrente.
- A autorização de admin está preparada localmente pela Change `perfil-admin-xano`; ainda depende de publicação e testes remotos.
- O destino continua workspace `151966`, branch `v1`, grupo Biblioteca; `allow_push` não será alterado.
