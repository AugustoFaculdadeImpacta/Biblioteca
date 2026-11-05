# Tasks

## 1. Tema e formulários acessíveis

- [x] 1.1 Definir tokens e aparência clara/escura do app, com cores explícitas para texto, fundo, placeholder, borda, seleção e foco de input, senha, textarea e select; verificar contraste WCAG AA e `:focus-visible` por testes no navegador em 360px e 1366px.
- [x] 1.2 Padronizar cartões, espaçamento, largura responsiva, botões e mensagens de formulário; verificar teclado, labels, ausência de overflow horizontal a 360px e legibilidade nos dois temas por teste visual no navegador.

## 2. Navegação e transições de autenticação

- [x] 2.1 Implementar cabeçalho compartilhado e links entre login/cadastro conforme sessão e perfil; adicionar testes com estados visitante, estudante, bibliotecário e logout usando sessão mockada.
- [x] 2.2 Tornar a página inicial útil e apresentar boas-vindas, links e confirmação pós-cadastro; testar a sessão privada e o consumo da mensagem após redirect com resposta de API mockada.
- [x] 2.3 Corrigir o retorno de navegação dos handlers de login/cadastro para que estudantes cheguem a `/`, bibliotecários a `/admin/acervo` e cadastro bem-sucedido a `/` com mensagem; testar respostas mockadas e preservar os erros na tela de origem.
- [x] 2.4 Verificar bloqueio de `/admin/acervo` para visitante e estudante, acesso de bibliotecário e ausência de token/perfil privado no estado enviado ao cliente ou logs, usando testes automatizados sem chamadas de escrita ao Xano live.

## 3. Verificação integrada

- [x] 3.1 Executar `pytest` completo e `openspec validate --strict` para a Change e para as specs; registrar os resultados sem executar escrita remota.
- [x] 3.2 Executar `reflex compile --dry` e validar no Playwright real os campos, contraste calculado, foco por teclado, navegação, redirects e bloqueio administrativo em 360px/1366px e nos modos claro/escuro.
- [x] 3.3 Revisar `git status` e `git diff` para confirmar que as alterações estão limitadas à Change e aos arquivos de implementação/teste autorizados, sem segredo versionado, alterações em `xano/`, `evaluation/` ou `verificacao-avancada-circulacao`; registrar OK/FALHOU por gate.

## Workflow follow-up

- Arquivar a Change somente depois da revisão humana dos artefatos, da implementação e da verificação completa; sincronizar as deltas `frontend-foundation` e `identity-session` durante o archive.
