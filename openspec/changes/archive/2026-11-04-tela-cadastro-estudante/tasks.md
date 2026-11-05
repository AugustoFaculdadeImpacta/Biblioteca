# Tasks

## 1. Construir a tela de cadastro

- [x] 1.1 Criar a rota e o formulário Reflex com nome, e-mail e senha, sem campo de perfil; manter navegação e indicador `:focus-visible`. Verificar com testes de componentes que os rótulos, tipos de campo, ordem por teclado e foco visível estão presentes.
- [x] 1.2 Implementar validação do formulário antes do envio: obrigatoriedade, formato de e-mail, normalização de espaços externos e minúsculas, rejeição de espaços internos e preservação da senha. Verificar os casos válidos e inválidos com testes sem transporte HTTP e confirmar que entradas inválidas não chamam a API.

## 2. Integrar autocadastro e sessão

- [x] 2.1 Enviar somente `nome`, e-mail normalizado e `senha` para `POST /auth/signup` por meio do cliente backend e transporte injetável. Verificar método, caminho e payload com `httpx.MockTransport`, sem tráfego de rede live.
- [x] 2.2 Tratar sucesso `200`, conflito `409`, entrada inválida `400` e falhas de configuração/transporte com mensagens em português; em sucesso guardar `authToken` apenas no estado privado da sessão e confirmar acesso imediato. Testes devem verificar ausência de token, senha, URL e cabeçalho em deltas, estado público e logs, além de isolamento entre sessões.

## 3. Documentar teste manual e integrar

- [x] 3.1 Criar roteiro em português para o usuário testar cadastro válido e duplicado usando identidade de teste exclusiva num ambiente acadêmico não produtivo, após confirmar o destino de `XANO_API_BASE_URL`; deixar explícito que nenhum teste automatizado grava no Xano live e que o roteiro não presume endpoint de exclusão.
- [x] 3.2 Executar `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q`, `openspec validate "tela-cadastro-estudante" --strict` e `reflex compile --dry`; verificar a tela no navegador local e confirmar no `git status` que `xano/`, `evaluation/` e `openspec/changes/verificacao-avancada-circulacao` não foram alterados.

## Workflow follow-up

- Arquivar somente após Review/aprovação e Verify aprovado, sincronizando a delta `identity-session` com as specs consolidadas.
