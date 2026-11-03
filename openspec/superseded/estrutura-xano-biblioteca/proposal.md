# Proposal

## Why

A biblioteca precisa iniciar a integração Xano–Reflex a partir do domínio aprovado, sem tratar definições existentes no workspace como modelo ou fonte de verdade. A primeira entrega será uma fatia vertical de identidade e sessão; catálogo, circulação e demais capacidades evoluirão com suas próprias Changes.

## What Changes

- Definir e implementar, após revisão humana, o contrato de identidade da biblioteca com autenticação nativa Xano: cadastro por e-mail e senha sem confirmação, sessão imediata de estudante, login e consulta do perfil confiável.
- Integrar esses fluxos a uma aplicação Reflex, aprovada na avaliação do projeto, mantendo o token exclusivamente no estado privado do backend e oferecendo logout local sem presumir revogação remota.
- Delimitar a identidade a uma conta autenticável e seu perfil (`estudante` ou `bibliotecario`); autocadastro não aceita papel escolhido pelo cliente, e não haverá endpoint público de promoção. O primeiro bibliotecário será provisionado manualmente por operador após confirmação do destino autorizado.
- **Não usar, reconstruir, excluir ou adaptar** definições atualmente encontradas no Xano. A leitura atual encontrou 35 documentos de definição; a Change deve parar antes de qualquer escrita se recursos ainda estiverem presentes no destino ou se não houver uma autorização e um destino limpo claramente confirmados.
- Manter fora desta Change os schemas e comportamentos de catálogo, empréstimos, reservas e danos/perdas. Eles serão especificados verticalmente em Changes posteriores, conforme as regras já aprovadas.
- Registrar as dependências entre a conta autenticável, o contrato de sessão Xano e a mediação Reflex, bem como testes locais e integrados que comprovem o isolamento da sessão.

## Capabilities

### New Capabilities

- `identity-session`: cadastro, login, sessão mediada pelo backend Reflex, logout local e perfil confiável de estudante ou bibliotecário.

### Modified Capabilities

Nenhuma. Não existem specs consolidadas do produto.

## Impact

- Xano: uma nova estrutura de identidade autenticável e os contratos necessários à identidade; nenhuma alteração em recursos encontrados será permitida por esta proposta.
- Reflex: fluxos de cadastro, login, sessão e logout local; chamadas Xano sempre intermediadas pelo backend.
- Estado lido em 2026-10-27: workspace `151966` (`Augusto's Workspace`), host `x8ki-letl-twmt.n7.xano.io`, branch `v1` marcada live, `allow_push: false`. Pull somente de definições retornou 35 documentos: 4 de tabela, 24 de API, 3 de função, 1 addon, 2 objetos de IA e 1 definição de workspace. Não foram incluídos registros nem variáveis de ambiente. Esse levantamento é apenas o estado encontrado; não é fonte para o modelo greenfield.
- Apply depende de o operador confirmar previamente um destino autorizado e sem recursos preexistentes a alterar. Se o estado atual persistir, ou o push continuar bloqueado, não escrever no workspace, não habilitar push, não excluir recursos e não contornar a restrição.
- A Change incompleta `identidade-sessao-estudante` será preservada, identificada como substituída e movida para `openspec/superseded/`; não será apagada nem arquivada como concluída. A nova Change será a única ativa.
