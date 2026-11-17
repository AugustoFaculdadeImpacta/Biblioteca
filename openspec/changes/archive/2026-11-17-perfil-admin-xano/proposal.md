# Proposal

## Why

A biblioteca precisa de uma conta administradora capaz de exercer as permissões bibliotecárias e provisionar outras contas privilegiadas. Hoje o Xano aceita somente estudante e bibliotecário, e os endpoints administrativos autorizam exclusivamente o perfil bibliotecário.

## What Changes

- Adicionar `admin` ao enum `usuario.perfil`, preservando `estudante` e `bibliotecario`.
- Permitir que administradores autenticados exerçam as mesmas operações administrativas que bibliotecários, sem ampliar operações pessoais exclusivas de estudantes.
- Permitir que admin crie e desative bibliotecários pela área de gestão, com autorização validada no backend; o autocadastro público continuará criando somente estudantes.
- Permitir que o frontend reconheça sessões admin sem expor token e reutilize as permissões administrativas já disponíveis ao bibliotecário.
- Permitir que admin alterne entre visualizações de bibliotecário e estudante, com indicação visível, sem mudar o perfil da sessão ou as permissões do backend.
- Registrar em `docs/xano-workflow.md` um roteiro sem credenciais para provisionar manualmente a primeira conta admin pelo dono do workspace.
- Não remover fisicamente contas de bibliotecário nem títulos que tenham histórico.
- Não alterar `auth=false`, apagar registros, alterar `allow_push` ou executar escrita real no Xano sem passar pelos gates de destino, pull, rollback, dry-run e push unitário.

## Capabilities

### New Capabilities

### Modified Capabilities
- `identity-session`: adicionar o perfil admin e provisionamento restrito de contas privilegiadas.
- `frontend-foundation`: reconhecer sessão admin nas permissões equivalentes às do bibliotecário e oferecer gestão de bibliotecários somente a admin.
- `catalog`: autorizar bibliotecário e admin nas operações administrativas de acervo.
- `copy-condition`: permitir que admin registre e consulte condições como bibliotecário.
- `loan-circulation`: permitir que admin opere retiradas, devoluções e consultas administrativas como bibliotecário.
- `reservations`: permitir que admin consulte e opere filas como bibliotecário.

## Impact

- Xano: enum `usuario.perfil`, precondições dos endpoints administrativos do grupo Biblioteca e operações administrativas para criar e desativar bibliotecários.
- Reflex: reconhecimento do perfil admin na sessão privada, nas verificações equivalentes ao bibliotecário, na área de gestão exclusiva de admin e na alternância de visualização sem impersonação.
- OpenAPI e specs das capacidades listadas; roteiro operacional sem segredos em `docs/`.
- Alvo pretendido e confirmado pelo CLI: workspace `151966`, branch `v1` (live), grupo Biblioteca. `allow_push=false` e o sandbox não oferece filtro `-i`; nenhum push Xano será feito nesta Change.
