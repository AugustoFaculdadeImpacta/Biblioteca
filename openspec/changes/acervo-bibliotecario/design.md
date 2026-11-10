# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de [catalog](./specs/catalog/spec.md), [loan-circulation](./specs/loan-circulation/spec.md) e [reservations](./specs/reservations/spec.md).

O Xano local confirma criação de título, associação a categoria, criação de exemplar e `PATCH /catalogo/titulos/{tituloId}`. A tabela `titulo` não contém `ativo`; o catálogo público não lista exemplares individualmente; não há contrato local para listar o acervo administrativo completo, desativar ou reativar título. A tela Reflex atual cadastra títulos e exemplares, mas não consulta nem edita o acervo completo.

## Goals / Non-Goals

**Goals:**
- Evoluir o título e seus fluxos de maneira vertical, preservando histórico e as regras existentes de circulação.
- Fazer da API Xano a autoridade para filtros de autorização, estado ativo e impedimentos por empréstimo/reserva.
- Reutilizar os contratos existentes de criação, edição, categoria e exemplar quando compatíveis.

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

### Contratos administrativos ausentes

O OpenAPI local confirma `PATCH /catalogo/titulos/{tituloId}`, mas não oferece listagem de todos os títulos com exemplares/estados, desativação ou reativação. Não escolher caminhos, verbos ou schemas para essas operações por convenção. Consultar documentação atual do Xano Developer antes de definir os contratos; se não for possível validá-los, manter as tarefas correspondentes como NÃO EXECUTADAS e não apresentar funcionalidade parcial como concluída. A listagem completa deve permanecer autenticada e autorizada no servidor.

**Alternativa considerada:** reutilizar a listagem pública para a interface administrativa; rejeitada porque ela omite exemplares individuais e não pode incluir títulos desativados.

### Perfis e autorização

Todas as consultas e mutações administrativas exigem autenticação e validação no servidor para bibliotecário/admin. A paridade de `admin` depende da Change `perfil-admin-xano`; até o Xano aceitar e autorizar esse perfil, não afirmar que as operações administrativas reais estão disponíveis a admin. Visitantes e estudantes não recebem consultas ou mutações administrativas.

**Alternativa considerada:** ocultar ações apenas no Reflex; rejeitada porque a interface não é uma fronteira de autorização.

### Operação e validação Xano

O CLI confirmou workspace `151966`, branch `v1` live, grupo Biblioteca e `allow_push=false`; sandbox push não oferece filtro unitário `-i`. O pull isolado de referência contém 57 arquivos fora do repositório e `xano/` local permanece sem alterações. Nenhuma escrita foi enviada ao Xano. Não alterar `allow_push`, não usar sincronização ampla e não editar/sincronizar `xano/` se não houver uma via unitária permitida. A ferramenta Xano Developer MCP para consultar documentação/validar XanoScript não está disponível nesta sessão; portanto, os contratos ausentes não serão inferidos. Antes de qualquer operação remota futura, repetir a identificação do destino, obter pull isolado e rollback fora do repositório, e exigir dry-run de um único CREATE/UPDATE para cada arquivo.

Enquanto o backend estiver bloqueado, os testes de interface/clientes usam respostas mockadas. Nenhum teste mockado será descrito como verificação contra Xano real.

## Risks / Trade-offs

- [O campo `ativo` exige migração de schema] → preservar todos os registros, default ativo e atualizar somente após prova reversível e dry-run unitário.
- [A lista administrativa pode expor dados operacionais] → autenticação e perfil verificados no backend; nunca usar o GET público como substituto.
- [Corrida entre verificação de empréstimos/reservas e desativação] → revalidar no servidor com garantia de consistência; bloquear a ação se essa garantia não puder ser comprovada.
- [A Change `perfil-admin-xano` está incompleta] → manter o acesso de admin pendente até conclusão backend daquela Change.
- [Destino Xano recusa push filtrado] → manter tarefas remotas pendentes; não alterar preferências ou contornar o gate.

## Migration Plan

1. Reconfirmar workspace, branch, ambiente e permissões do CLI; obter pull isolado e cópia de rollback fora do repositório.
2. Validar o campo `ativo` e suas consultas com documentação Xano e teste reversível; não alterar dados de produção sem mecanismo unitário aprovado.
3. Implementar cada alteração em arquivo Xano separado, validando dry-run de um único CREATE/UPDATE e pull de conferência após cada operação autorizada.
4. Testar com dados sintéticos e limpar individualmente; verificar GET 404 e contagens finais exigidas antes de considerar o backend verificado.
5. Se o gate de push ou a validação de consistência falhar, não sincronizar e manter esta Change ativa.

## Decisões tomadas por delegação (revisar)

- A desativação é lógica, usando `ativo`; novos e existentes começam ativos para preservar o catálogo atual.
- Bloquear remoção lógica se existir qualquer empréstimo ainda não devolvido (`devolvido_em` nulo ou zero) ou reserva ativa associada ao título/exemplar.
- Não remover fisicamente títulos com histórico nem seus exemplares.
- Título inativo desaparece do catálogo público e não aceita nova solicitação ou reserva; bibliotecário continua vendo-o na área administrativa.
- Não inventar endpoint para listagem completa, desativação ou reativação. Se a documentação Xano não permitir validar o contrato, deixar essas tarefas pendentes.
- Admin deve ter as mesmas permissões do bibliotecário, mas essa parte depende do backend da Change `perfil-admin-xano`.
- O destino continua workspace `151966`, branch `v1`, grupo Biblioteca; `allow_push` não será alterado.
