# Proposal

## Why

O perfil admin precisa validar as jornadas completas de estudante e bibliotecário sem trocar de conta, e ainda não dispõe de uma interface para consultar ou editar as regras da biblioteca. Também é necessário corrigir o contraste real do controle de acessibilidade no cabeçalho, preservando o layout aprovado.

## What Changes

- Permitir ao admin alternar entre visões Estudante, Bibliotecário e Administrador, aplicando guardas de rota à visão efetiva e mantendo todas as ações próprias da visão usando a sessão real do admin.
- Criar a página administrativa `/regras`, com leitura e gravação das sete configurações do contrato, validação, padrões somente leitura quando o endpoint não estiver disponível e cache invalidável.
- Implementar no servidor local de demonstração as mesmas rotas e regras para facilitar testes sem acesso remoto ao Xano.
- Documentar o contrato e os passos para publicação manual dos endpoints e permissões no Xano; esta Change não fará escrita nem leitura remota do Xano.
- Traduzir mensagens de regra e atualizar uma vez as listas após conflito de estado 403.
- Corrigir o estilo efetivamente renderizado do botão de acessibilidade para igualar Perfil, mantendo geometria e contraste mínimo de 4,5:1 nos dois temas e estados.

## Capabilities

### New Capabilities
- `library-rules`: Consulta, edição e aplicação local das regras configuráveis da biblioteca.

### Modified Capabilities
- `primary-journeys`: A navegação e as jornadas do admin seguem a visão efetiva, inclusive ações de estudante e bibliotecário.
- `identity-session`: A sessão real de admin permanece a identidade usada ao alternar a visão; a UI não substitui nem falsifica o perfil autenticado.
- `reservations`: Admin pode executar as ações de estudante e de equipe na visão correspondente, usando sua própria conta e sessão.
- `loan-circulation`: Limites e prazos configuráveis passam a determinar operações de empréstimo e retirada.
- `xano-communication`: Chamadas das regras usam o cliente comum, limitador, cache e tratamento seguro de erros já adotados.

## Impact

- Afeta rotas, estado de sessão/visão, menus do perfil, detalhe de livro, telas de reservas e acervo, estilos do cabeçalho e testes Reflex.
- Adiciona `GET /configuracoes` e `PUT /admin/configuracoes` ao contrato esperado e à API local de demonstração, além de uma página administrativa.
- Requer publicação manual no Xano para que os endpoints aceitem admin; nenhuma operação remota será executada nesta Change.
- Adiciona `docs/publicacao-xano-regras.md` e atualiza `docs/relatorio-noite.md`.
