# Tasks

## 1. Jornadas e falhas de integração

- [x] 1.1 Criar testes integrados de estado/cliente para cadastro ou login de estudante, catálogo, solicitação de empréstimo ou reserva e consulta do resultado; usar somente `httpx.MockTransport` e validar os resultados contra `identity-session`, `catalog`, `loan-circulation` e `reservations`.
- [x] 1.2 Cobrir por transporte simulado entradas inválidas, respostas 401/403/404/409/5xx, falha de transporte e resposta de sucesso incompatível; verificar mensagens em português, privacidade de token/senha/corpo técnico, ausência de falso sucesso e ausência de repetição automática de escrita.
- [x] 1.3 Criar testes integrados de bibliotecário autenticado para cadastro de título, associação de categoria, criação de exemplar e ação de circulação; corrigir somente lacunas observadas e atualizar a documentação de uso diretamente afetada, validando testes focados de cada fluxo.

## 2. Consistência visual e acessibilidade

- [x] 2.1 Revisar telas de login, cadastro, catálogo/detalhe, área pessoal, acervo e circulação e aplicar ajustes visuais reutilizando tema e componentes existentes; verificar consistência, português, foco visível, contraste, labels e navegação por teclado com testes focados.
- [x] 2.2 Validar os layouts das telas alteradas em 360px e 1366px, sem rolagem horizontal e sem regressão de leitura/acessibilidade; registrar a verificação em teste automatizado ou evidência Playwright.

## 3. Verificação local integrada

- [x] 3.1 Executar as suítes focadas e a suíte Python do projeto, além de `reflex compile --dry`; registrar contagens e confirmar que os testes não acessam o Xano real nem usam credenciais.
- [x] 3.2 Com o runtime Reflex local funcional, percorrer no navegador uma jornada de estudante e uma de bibliotecário usando somente a API demonstrativa local; verificar feedback, navegação por teclado e layouts em 360px/1366px, inspecionando que nenhum processo de teste permaneça ativo ao final.

## Workflow follow-up

- Arquivar somente após revisão humana, tarefas concluídas, evidências locais registradas e validação OpenSpec estrita aprovada. Não considerar mocks ou a API demonstrativa como teste do Xano remoto.
