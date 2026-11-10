# Proposal

## Why

A biblioteca precisa de uma conta administradora capaz de exercer as permissões bibliotecárias e provisionar outras contas privilegiadas. Hoje o Xano aceita somente estudante e bibliotecário, e os endpoints administrativos autorizam exclusivamente o perfil bibliotecário.

## What Changes

- Adicionar `admin` ao enum `usuario.perfil`, preservando `estudante` e `bibliotecario`.
- Permitir que administradores autenticados exerçam as mesmas operações administrativas que bibliotecários, sem ampliar operações pessoais exclusivas de estudantes.
- Criar uma operação administrativa autenticada para provisionar contas de bibliotecário ou admin; o autocadastro público continuará criando somente estudantes.
- Permitir que o frontend reconheça sessões admin sem expor token e reutilize as permissões administrativas já disponíveis ao bibliotecário.
- Registrar um roteiro sem credenciais para provisionar manualmente a primeira conta admin.
- Não alterar `auth=false`, apagar registros, alterar `allow_push` ou executar escrita real no Xano sem passar pelos gates de destino, pull, rollback, dry-run e push unitário.

## Capabilities

### New Capabilities

### Modified Capabilities
- `identity-session`: adicionar o perfil admin e provisionamento restrito de contas privilegiadas.
- `frontend-foundation`: reconhecer sessão admin nas permissões equivalentes às do bibliotecário.
- `catalog`: autorizar bibliotecário e admin nas operações administrativas de acervo.
- `copy-condition`: permitir que admin registre e consulte condições como bibliotecário.
- `loan-circulation`: permitir que admin opere retiradas, devoluções e consultas administrativas como bibliotecário.
- `reservations`: permitir que admin consulte e opere filas como bibliotecário.

## Impact

- Xano: enum `usuario.perfil`, precondições dos endpoints administrativos do grupo Biblioteca e novo endpoint de provisionamento administrativo.
- Reflex: reconhecimento do perfil admin na sessão privada e nas verificações equivalentes ao bibliotecário.
- OpenAPI e specs das capacidades listadas; roteiro operacional sem segredos em `docs/`.
- Alvo pretendido já indicado pelo usuário: workspace `151966`, branch `v1`, grupo Biblioteca. A confirmação pelo CLI e a possibilidade de push unitário devem ser refeitas em Apply; a documentação local registra `allow_push=false` e informa que sandbox push não oferece filtro `-i`, portanto a execução pode ser bloqueada antes de qualquer escrita.
