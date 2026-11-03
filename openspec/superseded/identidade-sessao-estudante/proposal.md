# Proposal

## Why

A biblioteca precisa de uma estrutura inicial Xano coerente com a identidade escolar e de fluxos de identidade confiáveis para estudantes. Esta Change reconstrói somente os recursos Xano aprovados para identidade, remove o legado explicitamente autorizado e integra cadastro, login, sessão e logout local pelo backend Reflex, sem implementar capacidades de catálogo ou operações administrativas.

## What Changes

- Introduzir cadastro e login com e-mail e senha, sem confirmação de e-mail; um cadastro bem-sucedido inicia imediatamente uma sessão de estudante.
- Estabelecer sessão autenticada e logout, com Reflex intermediando as chamadas e mantendo o token exclusivamente no estado privado do backend.
- Atribuir perfil confiável no backend: autocadastro sempre cria estudante e tentativas de autoelevação não alteram o perfil. A autorização de ações administrativas reais será implementada e verificada na Change futura que introduzir a primeira dessas ações.
- Não provisionar uma conta bibliotecária nesta Change; o bootstrap fica para uma Change futura. O autocadastro continua criando somente estudantes, não há endpoint público de promoção, e a única limpeza de registros autorizada é a exclusão dos registros fake de `usuario`.
- Verificar a integração com autenticação nativa do Xano e seu contrato durante Apply, sem presumir endpoints, formatos de token, renovação ou revogação que ainda não tenham sido confirmados.
- **BREAKING:** excluir as tabelas legadas `livro`, `categorias` e `emprestimo`; a exclusão apaga todos os registros nelas, cuja quantidade não foi consultada. Remover as 18 rotas legadas de catálogo, categorias e empréstimo, enumeradas no design.
- Atualizar in-place a tabela autenticável `usuario` e suas rotas existentes `POST /auth/signup`, `POST /auth/login` e `GET /auth/me`, acrescentando o perfil controlado de estudante/bibliotecário sem recriar esses recursos. Excluir os registros fake atualmente existentes em `usuario`, conforme autorização do usuário; não alterar outros registros. Confirmar no Apply o diff e que a exclusão de registros se limita a essa tabela.
- Atualizar também `GET /logs/user/my_events`, uma atualização incidental do Xano CLI explicitamente autorizada pelo usuário. A definição atual tem referência de tabela vazia; não criar tabela de eventos nem implementar seu comportamento nesta Change.
- Implementar logout no contexto privado da aplicação Reflex; não adicionar rota Xano de logout, a menos que a documentação nativa confirmada exija uma para cumprir o comportamento aprovado e a Change seja revisada.
- Limitar operações remotas nesta Change a atualizar a tabela `usuario` e os três endpoints de identidade existentes, excluir os registros fake de `usuario`, excluir as tabelas `livro`, `categorias`, `emprestimo` e suas 18 rotas, e atualizar `GET /logs/user/my_events`. Não alterar variáveis de ambiente, configurações do workspace, addon `user`, funções Quick Start ou outros recursos.
- **BREAKING:** as três tabelas de catálogo/categorias/empréstimo e 18 rotas legadas serão removidas; suas rotas deixarão de existir e seus registros serão perdidos. Os registros fake existentes em `usuario` também serão excluídos; nenhuma contagem foi obtida. As três rotas de identidade continuam nos mesmos caminhos e serão atualizadas in-place.
- O dry-run do snapshot sem alterações também aponta referências de tabela vazias no addon `user`, nas funções Quick Start e no endpoint de logs, e indica que `GET /logs/user/my_events` seria atualizado. A atualização do endpoint de logs foi autorizada; addon e funções permanecem fora do escopo. Parar sem push se um dry-run indicar alteração neles ou em qualquer outro recurso não enumerado.
- A definição Xano candidata de `usuario` preserva os campos existentes `id`, `created_at`, `nome` e `telefone`, exige e-mail e senha, adiciona `perfil` e índice único de e-mail. A prévia deve identificar os campos alterados e qualquer efeito de schema antes de ser considerada para aprovação; não pressupor expiração de token além do contrato nativo confirmado.
- O Xano CLI disponível identificou `allow_push: false` no workspace. Nenhuma escrita pode ocorrer enquanto essa restrição persistir; não alterar configuração ou buscar outro caminho para contorná-la. `--sync --delete` só pode ser considerado a partir de um snapshot completo de referência, com a prévia integral limitada às operações explicitamente aprovadas.
- Manter fora do escopo recuperação de conta, SSO, confirmação de matrícula, promoção de outros bibliotecários e operações de empréstimo, reserva e administração do catálogo.

## Capabilities

### New Capabilities

- `identity-session`: cadastro, login, sessão, logout e determinação confiável do perfil de estudante ou bibliotecário, incluindo proteção contra autoelevação.

### Modified Capabilities

Nenhuma. O projeto ainda não possui specs consolidadas; esta será a primeira capacidade especificada.

## Impact

- Evoluir verticalmente apenas os dados de identidade necessários, regras e endpoints autenticados no Xano e a interface de cadastro/login/sessão em Reflex.
- O workspace aprovado é `151966` (`x8ki-letl-twmt.n7.xano.io`), branch `v1`, marcada `live`; o usuário autorizou explicitamente operações delimitadas nessa branch. O CLI retornou `allow_push: false`; isso bloqueia escrita até que o próprio destino permita push. Reconfirmar workspace, branch e permissão pelo CLI imediatamente antes de qualquer escrita e parar se divergirem ou a permissão continuar desabilitada.
- O inventário das quatro tabelas e 21 rotas legadas está em `design.md`. Excluir `livro`, `categorias` e `emprestimo` apaga seus registros, cujas quantidades/conteúdo são desconhecidos. Excluir os registros fake de `usuario` foi autorizado explicitamente.
- Aplicar somente as exclusões e atualizações explicitamente enumeradas nesta Change: atualizar `usuario`, as três rotas de identidade e `GET /logs/user/my_events`; remover três tabelas e 18 rotas; limpar apenas os registros de `usuario`. Não alterar variáveis de ambiente, configurações, addon `user`, funções Quick Start ou outros recursos.
- As rotas legadas de catálogo, categorias e empréstimo deixarão de existir nesta Change. Changes futuras deverão especificar e implementar essas capacidades sem assumir que as tabelas antigas são o modelo final.
- O bootstrap da conta de bibliotecário fica adiado para Change futura; a exclusão autorizada dos registros fake de `usuario` não cria nem promove contas.
- Confirmar a auth nativa do Xano e o esquema técnico no Apply. Se não cumprir os requisitos, interromper antes de escrita e retornar à revisão; não contornar nem presumir contratos.
- Consultar a documentação oficial do Xano e verificar no workspace escolhido se a autenticação nativa atende ao fluxo aprovado. Se detalhes técnicos não puderem ser confirmados antes da revisão, registrá-los como premissas/risco e interromper Apply antes de depender de um contrato inventado.
- Manter tokens fora do bundle e do estado acessível ao cliente. Esta Change não cria ação administrativa; cada Change futura que introduzir uma ação dessas deverá implementar e verificar autorização no backend pelo perfil confiável, não apenas ocultar controles na interface.
- Criar somente os dados, regras e endpoints da capacidade de identidade e sessão; não criar antecipadamente tabelas de catálogo, empréstimo, reserva ou outras funcionalidades futuras.
