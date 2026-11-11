# Tasks

## 1. Preparar o ambiente e a estrutura mínima

- [x] 1.1 Antes de instalar ou executar código Reflex, localizar e conferir o Apêndice B do curso, a versão do Python e Node já instalados e as instruções oficiais/skills necessárias; registrar a evidência localmente na Change e parar se o Apêndice B estiver indisponível ou divergir materialmente da estratégia `venv + pip`. Evidência: Apêndice B em `docs/apendices/apendice_B_reflex.md`; Python 3.14.7; Node 24.20.0; sem `.venv` preexistente; as três skills Reflex estão disponíveis; sequência B.5–B.12 incorporada ao design.
- [x] 1.2 Com o gate de 1.1 satisfeito, criar/ativar `.venv` conforme Apêndice B, atualizar pip, instalar Reflex e dependências justificadas somente nesse ambiente; executar `reflex init` com app em branco e `pip freeze > requirements.txt`; verificar versões do Reflex/HTTPX, `pytest`, `pip check` e que a instalação global preexistente não foi alterada. Evidência: Reflex 0.10.0, HTTPX 0.28.1, pytest 9.2.0, python-dotenv 1.2.4; `pip check` sem conflitos; Reflex global 0.9.11 preservado.
- [x] 1.3 Criar `.gitignore`, `.env.example` sem valores, `rxconfig.py`, o esqueleto mínimo da aplicação e README com setup, configuração local e comando de execução; confirmar que `.env`, `.venv/`, `.web/`, `.states/` e `__pycache__/` são ignorados e que os comandos documentados apontam ao ambiente local.

## 2. Implementar a estrutura acessível

- [x] 2.1 Implementar layout base e navegação simples sem telas, formulários ou operações de negócio; criar testes `pytest` para a renderização e navegação por teclado da estrutura.
- [x] 2.2 Aplicar estilo `:focus-visible` perceptível a campos e botões sem criar fluxo funcional; validar com teste automatizado e walkthrough por teclado no navegador em 360×800 e 1366×768.

## 3. Implementar e verificar a fronteira HTTP

- [x] 3.1 Implementar cliente HTTP server-side que carrega `XANO_API_BASE_URL` do ambiente/`.env`, falha antes de enviar se ausente ou inválida e aceita transporte injetável; manter token em estado backend privado e isolado por sessão, sem registrar URL sensível, token ou cabeçalho; cobrir configuração, autorização, erros sanitizados e isolamento com `pytest` e mock/stub, sem tráfego de rede.
- [x] 3.2 Executar `pytest`, `openspec validate "fundacao-frontend-reflex" --strict` e build Reflex; iniciar `reflex run` em loopback e abrir a página local. Inspecionar foco, logs, eventos/estado e bundle compilado para confirmar que não há token nem valor de URL exposto e que nenhum teste ou fluxo emite escrita ao Xano live. Evidências locais: 12 testes passaram com bytecode Python desativado; `reflex compile --dry` e `reflex export --frontend-only` passaram; app de produção abriu e conectou em `http://127.0.0.1:3000/`; walkthrough Tab em 360×800 confirmou foco 3px na busca, links e botão sem overflow, 1366×768 sem overflow; delta real contém só o booleano público e não o token; bundle/logs sem token ou exceção; cliente Xano testado somente com `httpx.MockTransport`; `git status` final sem alterações em `xano/`, `evaluation/` ou `openspec/changes/verificacao-avancada-circulacao`.

## Workflow follow-up

- Após Review/aprovação e Apply, só arquivar depois de Verify aprovado e todas as tarefas concluídas.
- Não iniciar a Change de cadastro de estudante antes de concluir e arquivar esta fundação.
