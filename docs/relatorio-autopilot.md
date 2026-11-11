# Relatório de execução autônoma

## P0 — Diagnóstico de autenticação e domínio

**Status: concluído (diagnóstico local).** Nenhuma credencial, URL ou arquivo
`.env` foi lido ou registrado. Não houve chamada à API do Xano nesta etapa.

### Login, cadastro e token

- O login Reflex chama `submit_login` (`authenticate` é apenas um alias) e o
  cadastro chama `submit_student_signup`. Ambos usam `XanoClient.from_environment`
  e as rotas locais `POST /auth/login` e `POST /auth/signup`.
- O login Xano retorna `authToken` e perfil da conta; o cadastro público define
  `perfil=estudante` no servidor e também retorna `authToken`.
- A sessão guarda token, perfil e nome no estado privado Reflex (`_session_token`,
  `_session_profile`, `_session_name`). Não há persistência explícita do token
  em `rx.LocalStorage`.
- Chamadas pessoais são sequenciais: `/minhas/emprestimos`,
  `/minhas/solicitacoes`, `/minhas/reservas`, seguidas pelo catálogo público.
  `XanoClient.request` envia `Authorization: Bearer <token>` quando recebe token.
  Os três endpoints locais declaram `auth = "usuario"` e validam perfil
  `estudante`, compatível com esse header e com o perfil enviado pelo login.
- Sem token, `load_student_library` redireciona ao login; com token mas perfil
  diferente de estudante, redireciona à página inicial. Portanto, a mensagem
  genérica observada pressupõe que a sessão Reflex tinha token, mas o Xano
  rejeitou alguma chamada ou houve outra falha durante a carga.
- O código não faz fallback automático para `scripts/demo_api.py`. Essa API é
  um servidor local independente, com credenciais fixas de demonstração; o
  cliente da aplicação continua usando somente `XANO_API_BASE_URL`.
- A causa de eventual 401 após login não pode ser confirmada sem a sessão real.
  Possibilidades compatíveis com o código incluem token expirado/inválido ou
  login feito contra outro serviço/configuração. Não há evidência local de que
  o header Bearer esteja ausente nas chamadas atuais.

### Erros e mensagem da tela

- `XanoClient` preserva o status HTTP em `XanoResponseError`, mas converte
  falhas de transporte (incluindo timeout) em `XanoRequestError`.
- JSON ou payload inválido também resulta em `XanoRequestError`, sem distinção
  tipada de falha de transporte.
- `load_student_library` encaminha todas essas exceções a
  `catalog_error_message`. Fora detalhes de negócio previamente mapeados, a
  função retorna a mensagem genérica “Não foi possível concluir a operação no
  acervo...”; 401, 403, 404, 5xx, timeout e resposta inválida ainda não recebem
  mensagens específicas.
- Os cenários informados pelo usuário — catálogo público 200 e rotas pessoais
  401 sem token — são evidências fornecidas pelo usuário, não foram repetidos
  nesta sessão. Não foi feita chamada autenticada nem tentativa de validar o
  token real.
- A primeira tentativa de executar pytest pelo Python global 3.12 não encontrou
  o módulo pytest; o ambiente `.venv` existente foi usado sem instalar pacotes.
- O primeiro commit do relatório falhou porque não havia identidade Git
  configurada. O commit foi feito com identidade apenas na invocação, sem mudar
  a configuração do repositório ou do usuário.

### Regras de domínio encontradas

- O prazo do empréstimo é de 14 dias corridos a partir da retirada física; os
  endpoints locais calculam `vence_em` somando 1.209.600 segundos.
- O limite documentado e especificado é **um empréstimo ativo por estudante**,
  não três. O endpoint de retirada verifica empréstimos ativos antes de criar
  outro. Atrasos também bloqueiam solicitações/reservas.
- Renovação não está implementada como endpoint e permanece uma questão aberta
  na documentação. Não foi criada regra nova.
- Solicitações: `pendente`, `em_reserva`, `atendida`, `recusada`.
- Reservas: `aguardando`, `ofertada`, `retirada`, `expirada`; a oferta expira em
  48 horas e as rotas locais ordenam a fila por criação/ID.
- Perfis no schema: `estudante`, `bibliotecario`, `admin`. O login devolve o
  perfil armazenado; o cadastro público fixa estudante.
- Não há atualmente campo de motivo de recusa no schema local da solicitação.

### Inspeção MCP/Xano

- O Xano Developer MCP respondeu a versão `2.2.6`.
- A validação de sintaxe MCP dos três arquivos pessoais (`minhas_GET.xs` de
  empréstimos e reservas, e `minhas_solicitacoes_GET.xs`) passou: 3 válidos,
  0 inválidos.
- As ferramentas MCP disponíveis nesta sessão não oferecem listagem de
  workspace/branch/tabelas ativos. Nenhum comando Xano CLI foi executado.
- O estado remoto relatado (rotas publicadas) não foi revalidado por API.

### Decisões tomadas

- Tratar o 401 observado após login como problema de sessão/token ainda não
  confirmado; corrigir mensagens e tratamento no cliente sem inventar uma causa.
- Preservar o limite de um empréstimo ativo, pois já está definido no domínio e
  nas specs; não substituir por três.
- Manter renovação como não implementada e sem regra nova.
- Não usar a API demo como fallback silencioso para o Xano configurado.
- Não inspecionar `.env`; não expor URL, tokens, senhas ou dados pessoais.

### Como verificar

- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation`
- `openspec validate acervo-bibliotecario --strict`
- `openspec validate perfil-admin-xano --strict`
- `openspec validate reserva-pelo-bibliotecario --strict`

## P1 — Correção de Minha biblioteca

**Status: concluído localmente; causa da sessão real ainda não confirmada.**

- Confirmado no código: chamadas `GET /minhas/*` já recebem
  `Authorization: Bearer <token>` e exigem perfil estudante no XanoScript.
  Portanto, não foi alterado o header nem criado fallback para a API demo.
- O tratamento agora diferencia HTTP 401, 403, 404, 5xx, timeout, falha de
  comunicação e resposta/payload inválido, sempre sem expor corpo, URL ou token.
  Mensagens de negócio previamente permitidas continuam preservadas.
- Em 401, o cliente limpa a sessão local, mantém um alerta acessível com link
  para login e não apresenta estados vazios como se a consulta tivesse sucesso.
  Estados vazios amigáveis permanecem para consultas válidas sem registros.
- Verificação local/simulada: `.\.venv\Scripts\python.exe -m pytest
  --ignore=evaluation` — **156 passaram**; `openspec validate
  acervo-bibliotecario --strict` — **válida**. Cobertura usa transporte mockado;
  não valida o token nem o comportamento autenticado no Xano real.
- Uma expectativa inicial do teste de mensagem de negócio usou o texto Xano
  não traduzido; foi corrigida para conferir a mensagem permitida sanitizada.
  A suíte direcionada e a suíte completa passaram depois do ajuste.
- Não há tarefa de publicação de Xano decorrente de P1: a mudança é somente no
  cliente Reflex e no parser. A causa remota provável continua sendo sessão/
  token rejeitado, mas não foi afirmada como confirmada.

## P2 — Validação estrita de perfil-admin-xano

**Status: concluído localmente.**

- A validação estrita apontava que a delta da Change havia omitido dois
  cenários ainda vigentes do requisito consolidado de navegação:
  “Usuário autenticado navega na aplicação” e
  “Administrador autenticado navega na aplicação”.
- A correção mínima restaurou esses dois cenários em
  `openspec/changes/perfil-admin-xano/specs/frontend-foundation/spec.md`,
  preservando os cenários novos da Change.
- Verificação: `openspec validate perfil-admin-xano --strict` válida;
  `openspec validate acervo-bibliotecario --strict` válida;
  `openspec validate reserva-pelo-bibliotecario --strict` válida;
  `openspec validate --specs --strict` — 6 válidas, 0 inválidas.
- Suíte local: `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation` —
  **156 passaram**. Nenhum pacote foi instalado e nenhuma operação remota foi
  executada.

### Decisões tomadas

- Manter os dois cenários preexistentes com seus nomes e comportamentos
  consolidados, sem remover nem reescrever os cenários novos da Change.
- Não alterar código nem contratos Xano: P2 era uma correção de consistência
  dos artefatos OpenSpec.
- Manter `docs/publicacao-xano-pendente.md` sem alteração; P2 não adicionou
  trabalho que precise ser publicado no Xano real.

### Como verificar

- `openspec validate perfil-admin-xano --strict`
- `openspec validate --specs --strict`
- `openspec validate acervo-bibliotecario --strict`
- `openspec validate reserva-pelo-bibliotecario --strict`
- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation`

### Próximos itens

P3 foi executado e está registrado na seção seguinte. P4 é a próxima etapa;
P5–P6 serão registrados após cada item.

## P3 — Povoamento idempotente

**Status: concluído localmente; seed remoto não executado.**

- A API simulada agora inicia com **30 títulos reais**, usando somente título,
  autor e categorias; possui sete categorias, exemplares em quantidades
  variadas e contas de bibliotecário, estudante e admin com e-mails
  `@example.invalid`.
- O seed local reutiliza categorias, títulos, vínculos e contas existentes por
  chaves naturais normalizadas e completa exemplares faltantes sem apagar ou
  sobrescrever registros. Duas chamadas consecutivas foram testadas sem
  duplicações.
- Foi criado `scripts/seed_xano_demo.py` para categorias, títulos,
  associações e exemplares. O script usa `XANO_BASE_URL` e `XANO_ADMIN_TOKEN`
  somente do ambiente de execução, inicia em prévia sem chamadas e exige
  `--apply` e confirmação explícita do destino. Sua idempotência foi testada
  com transporte simulado; o modo de prévia foi executado localmente.
- O script Xano não provisiona contas. O contrato disponível não oferece uma
  operação aprovada para criar uma conta admin de teste, e a necessidade de
  contas de teste desta tarefa é atendida pela API simulada. A execução futura
  do seed de catálogo depende de confirmar/publicar `GET /admin/acervo`, que
  permanece candidato local.
- Nenhum comando Xano, chamada remota ou escrita foi realizada. O artefato é
  Python, não XanoScript; validação de sintaxe pelo Xano Developer MCP não se
  aplica.
- Testes locais: `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation` —
  **160 passaram**; `openspec validate` de cada uma das três Changes — todas
  válidas; `openspec validate --specs --strict` — **6 válidas, 0 inválidas**.

### Decisões tomadas

- Manter exatamente 30 títulos na massa simulada, preservar o empréstimo e os
  estados demonstrativos iniciais e usar sete categorias.
- Limitar o script Xano ao catálogo porque a criação de conta admin não tem
  contrato aprovado; não inventar um endpoint de provisionamento.
- Não executar nem conectar o script ao Xano; registrar `/admin/acervo` como
  dependência remota pendente.

### Como verificar

- `.\.venv\Scripts\python.exe -m pytest tests\test_demo_api_seed.py -q`
- `.\.venv\Scripts\python.exe -m scripts.seed_xano_demo`
- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation`
- `openspec validate acervo-bibliotecario --strict`
- `openspec validate perfil-admin-xano --strict`
- `openspec validate reserva-pelo-bibliotecario --strict`
- `openspec validate --specs --strict`

### Próximos itens

P4: revisar e concluir as tarefas locais ainda pendentes das três Changes.
Tarefas remotas continuam abertas e não serão marcadas como concluídas.
