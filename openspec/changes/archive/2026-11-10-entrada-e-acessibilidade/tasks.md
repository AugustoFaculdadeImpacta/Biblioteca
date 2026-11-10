# Tasks

## 1. Entrada, navegação e identidade

- [x] 1.1 Fazer `/` reutilizar a tela de login, remover “Início” como destino separado e manter `/catalogo` público; atualizar testes estruturais para confirmar o formulário raiz e o link “Ver catálogo sem entrar”. Verificado em `tests/test_frontend_foundation.py` (parte da execução com 49 testes aprovados).
- [x] 1.2 Manter o redirecionamento de sessão autenticada de `/` para `/catalogo` e cobrir visitante/logado em testes de estado Reflex. Verificado em `tests/test_navigation.py`.
- [x] 1.3 Guardar o nome retornado na sessão somente em estado privado, exibir “Olá, <nome>” no cabeçalho, mostrar “Entrar” para visitante e limpar a saudação no logout; testar nome, ausência de e-mail/token no estado público e os links por perfil. Verificado com estado Reflex isolado em `tests/test_navigation.py`.

## 2. Preferências globais de acessibilidade

- [x] 2.1 Implementar controles de fonte com escala limitada a 100%–150%, ação restaurar e persistência local; cobrir limites, restauração e valores persistidos inválidos em pytest. Verificado em `tests/test_navigation.py`; armazenamento `rx.LocalStorage` sincronizado.
- [x] 2.2 Implementar alternância persistente de alto contraste e redução de animações em todas as telas; testar estado inicial, alternância, persistência e foco visível. Verificado em `tests/test_navigation.py` e regras globais em `biblioteca_mais_nova/biblioteca_mais_nova.py`.
- [x] 2.3 Auditar os estados de alto contraste e validar contraste de texto >=4.5:1 e rótulos/estados acessíveis por teclado em teste ou verificação automatizada documentada. Playwright mediu contraste mínimo 15.30:1 em 26 elementos visíveis no catálogo, sem nenhum abaixo de 4.5:1; o primeiro controle teve foco visível de 3px após Tab.

## 3. Verificação integrada no navegador

- [x] 3.1 Rodar `reflex run` sem flags e verificar com Playwright login raiz, link e carregamento do catálogo público, saudação simulada, logout e persistência dos controles após navegação/recarga. Verificado em modo padrão contra API simulada `127.0.0.1:8765`; login simulado direcionou ao catálogo, saudação “Olá, Ana Simulada” e logout retornou ao login. O frontend abriu em `localhost:3000`; como a porta 8000 estava ocupada (`WinError 10048`), Reflex iniciou o backend em 8001.
- [x] 3.2 Verificar por Playwright ausência de rolagem horizontal em 360px e 1366px e foco visível nos controles de acessibilidade; registrar explicitamente o que não puder ser verificado, inclusive autenticação real sem credenciais autorizadas. Em 360px `scrollWidth=345/clientWidth=345`; em 1366px `1366/1366`; foco de 3px confirmado. Login real contra Xano não foi executado.
- [x] 3.3 Executar a suíte completa e `reflex compile --dry`; registrar saídas e corrigir falhas antes de concluir Verify. `.\.venv\Scripts\python.exe -m pytest tests -q`: 133 passed; `.\.venv\Scripts\python.exe -m reflex compile --dry`: Success, app compiled successfully; `openspec validate entrada-e-acessibilidade --strict`: válida.
