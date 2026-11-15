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
- Naquele diagnóstico, o código e as specs vigentes registravam um empréstimo
  ativo. A decisão foi substituída posteriormente pela regra explícita do usuário
  descrita em “Retificação da regra de empréstimos” abaixo.
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

## P4.1 — Detalhes do título na área pessoal

**Status: concluído localmente.**

- Títulos exibidos nas solicitações e reservas do estudante agora são links
  para `/catalogo/{titulo_id}`. O estado da solicitação/reserva e o prazo
  continuam visíveis e os dados permanecem limitados à sessão autenticada.
- Verificação: `.\.venv\Scripts\python.exe -m pytest
  tests\test_student_area.py -q` — **24 passaram**;
  `openspec validate acervo-bibliotecario --strict` — válida.
- Nenhum endpoint ou dado remoto foi alterado.

### Decisões tomadas

- Reutilizar a rota pública existente de detalhes e o `titulo_id` retornado
  pelos endpoints pessoais; não adicionar dados nem permissões ao backend.
- Manter o nome do título apresentado caso o catálogo público não exponha mais
  o detalhe (por exemplo, título desativado); o link continua sujeito à
  política pública vigente.

### Como verificar

- `.\.venv\Scripts\python.exe -m pytest tests\test_student_area.py -q`
- `openspec validate acervo-bibliotecario --strict`

### Próximos itens

P4.2 está registrado abaixo. P4.3: implementar a alternância de visualização
somente na interface para admin, sem alterar permissões do servidor.

## Retificação da regra de empréstimos

**Decisão vigente:** a regra definida pelo usuário nesta continuação substitui a
menção anterior a um empréstimo ativo. Um estudante pode ter até três
empréstimos ativos; atraso bloqueia novas operações; abaixo do limite,
empréstimos de outros títulos não bloqueiam. Um empréstimo ativo do mesmo título
impede nova solicitação, reserva, oferta ou retirada daquele título. Renovação
continua não implementada.

O XanoScript local aplica a regra por contagem dos empréstimos ativos e por
consulta dos IDs de exemplares do título, sem `join` nos fluxos alterados. A API
simulada aplica as mesmas condições. O Xano Developer MCP validou oito arquivos
XanoScript; essa validação é local e não comprova publicação, execução ou
concorrência no Xano real.

## P4.2 — Painel e regras de circulação

**Status: concluído localmente e verificado; sem publicação remota.** O painel Reflex e seus clientes tipados cobrem
solicitações, fila FIFO, ofertas, retiradas, devoluções e indicadores de
empréstimos ativos/atrasados. A API simulada foi ampliada para os fluxos
pessoais e administrativos.

- A suíte focada `tests/test_circulation.py` e
  `tests/test_demo_api_circulation.py` passou (**14 testes**), incluindo o caso
  de estudante com um empréstimo de outro título recebendo oferta, o limite
  máximo de três empréstimos ativos e o bloqueio por empréstimo do mesmo título.
- `xano.tests.test_candidates` passou (**13 testes**) após corrigir a contagem
  das 38 operações OpenAPI e os contratos dos novos endpoints.
- O Xano Developer MCP validou **8 arquivos `.xs` (8 válidos)**. Nenhuma
  publicação, comando Xano CLI ou chamada remota foi realizada.
- `python -m reflex compile --dry` concluiu com sucesso; nenhum servidor Reflex
  foi iniciado.
- Verificação integrada final: `.\\.venv\\Scripts\\python.exe -m pytest
  --ignore=evaluation` — **174 passaram**; `unittest discover -s xano\\tests`
  — **13 passaram**; `openspec validate --specs --strict` e as três Changes
  (`acervo-bibliotecario`, `perfil-admin-xano`,
  `reserva-pelo-bibliotecario`) — válidas.

### Decisões tomadas

- Aplicar o limite global de três empréstimos, sem bloquear por empréstimos de
  outros títulos abaixo do limite.
- Bloquear somente por atraso, limite atingido ou empréstimo ativo do título
  operado; manter a validação no servidor e na API simulada.
- Não usar `join` nos guards de título: listar IDs dos exemplares e filtrar os
  empréstimos ativos por esses IDs.
- Manter os contratos e XanoScript apenas locais, pendentes de validação e
  publicação remotas autorizadas.

### Como verificar

- `.\.venv\Scripts\python.exe -m pytest tests\test_circulation.py tests\test_demo_api_circulation.py -q`
- `.\.venv\Scripts\python.exe -m unittest xano.tests.test_candidates -v`
- `.\.venv\Scripts\python.exe -m reflex compile --dry`
- `openspec validate acervo-bibliotecario --strict`
- `openspec validate perfil-admin-xano --strict`
- `openspec validate reserva-pelo-bibliotecario --strict`
- `openspec validate --specs --strict`

### Próximos itens

P4.3: alternância de visualização somente na interface para admin. As tarefas
remotas continuam pendentes; não arquivar as Changes enquanto houver qualquer
publicação, prova ou limpeza remota por executar.

## P4.3 — Alternância de visualização do admin

**Status: concluído localmente; sem mudança remota.**

- O cabeçalho agora oferece a admin os modos “Bibliotecária” e “Estudante”,
  com faixa visível “Modo de visualização: ...”, botões operáveis por teclado
  e estado `aria-pressed`. O modo altera somente as opções de navegação.
- O perfil efetivo continua `admin`, com permissões administrativas intactas;
  a interface não altera token, perfil ou autorização no servidor.
- Em visualização de estudante, Minha biblioteca usa o token da própria
  sessão admin. Quando o backend mockado recusa a chamada com 403, a tela
  preserva a sessão, mostra a mensagem de permissão e não inventa registros.
  A tela pessoal continua protegida para bibliotecários e visitantes.
- Testes locais: `.\.venv\Scripts\python.exe -m pytest
  tests\test_navigation.py tests\test_student_area.py -q` — **34 passaram**;
  `.\.venv\Scripts\python.exe -m reflex compile --dry` — compilação concluída.
  A primeira execução focada teve um teste que esperava acentos literais na
  representação serializada do Reflex; o teste foi ajustado aos escapes reais
  e a repetição passou. Nenhum servidor foi iniciado.
- A validação estrita `openspec validate perfil-admin-xano --strict` passou.
  Esta etapa não alterou XanoScript; validação MCP de sintaxe não se aplica.
  Nenhuma chamada remota, Xano CLI ou publicação foi executada.

### Decisões tomadas

- Manter a visualização de estudante como modo visual, não como impersonação:
  o token enviado é o do admin autenticado e o backend continua decidindo se a
  rota pessoal pode ser consultada.
- Não exibir dados simulados nem conceder ações exclusivas de estudante ao
  admin; uma recusa do backend permanece explícita.
- A alternância é reiniciada para “Bibliotecária” ao estabelecer ou limpar uma
  sessão, e o estado interno do modo não é usado para autorização.

### Como verificar

- `.\.venv\Scripts\python.exe -m pytest tests\test_navigation.py tests\test_student_area.py -q`
- `.\.venv\Scripts\python.exe -m reflex compile --dry`
- `openspec validate perfil-admin-xano --strict`

### Próximos itens

As tarefas locais pendentes de implementação das três Changes foram
concluídas. P5: validar todas as Changes e specs; não arquivar enquanto houver
tarefas remotas pendentes. Nenhuma operação remota será executada nesta sessão.

## Continuação — login legado, smoke e pendências OpenSpec (2026-11-14)

### Login e campo `ativo`

- Um pull sem registros da branch `v1` confirmou que o login remoto contém
  `precondition ($usuario.ativo != false)`. A mesma regra já estava no arquivo
  local e nos guards de perfil, nas rotas administrativas e nas consultas de
  estudantes/títulos. Não há uma condição `ativo == true` que rejeite nulos.
- Portanto, pelo código, `ativo` nulo não é tratado como explicitamente falso.
  A hipótese é plausível apenas se o runtime do Xano avaliar essa comparação de
  forma diferente; não foi possível testá-la com conta existente sem
  credenciais. A regra foi mantida conforme o contrato `!= false`.
- A checagem de conta ativa foi movida para depois da validação da senha e agora
  responde `Conta desativada.`. Isso evita revelar que um e-mail pertence a
  uma conta desativada quando a senha está errada. O app traduz esse detalhe
  somente quando o cliente o reconhece na lista de mensagens seguras. Respostas
  401 e 403 sem esse detalhe continuam com mensagem genérica de credenciais.
- O Xano usa `accessdenied` para credenciais inválidas e para conta desativada,
  então ambas podem retornar 403; a sonda de credenciais falsas confirmou 403.
  Não foi afirmado que o código HTTP sozinho diferencie os casos.
- A validação MCP de XanoScript foi tentada repetidamente, mas o MCP não
  inicializou (negociação de lifecycle excedeu 60 segundos). O pull confirmou
  a regra remota anterior; o CLI executou dry-run somente de `login_POST.xs`
  com exatamente um UPDATE e aceitou o push parcial do mesmo arquivo. O push
  terminou com código 0, com aviso do CLI sobre referência à tabela `usuario`.
- Verificação remota sem credenciais reais: títulos 200 com JSON válido e
  contagem 2; categorias 200; `/minhas/emprestimos`,
  `/minhas/solicitacoes` e `/minhas/reservas` 401; login com endereço e senha
  falsos 403. Nenhuma conta real foi usada.

### Smoke autenticado somente de leitura

- Criados `scripts/smoke_xano.py` e testes com `httpx.MockTransport`. O script
  lê `XANO_API_BASE_URL` da configuração local, captura credenciais somente do
  ambiente do terminal antes de carregar `.env`, faz login e executa apenas as
  consultas GET previstas por perfil. Não imprime e-mail, senha, token, corpo
  de resposta nem URL. Perfis sem ambos os valores são ignorados.
- Os testes cobrem rotas por perfil, bearer token no transporte simulado,
  contagens, credenciais omitidas do output e ajuda com exemplos PowerShell.
  O script não foi executado com credenciais reais; smoke autenticado real
  permanece pendente para o usuário.

### Verificações e Changes

- `python -m pytest --ignore=evaluation`: 183 passaram.
- `python -m unittest discover -s xano\tests`: 15 passaram.
- `openspec validate --specs --strict`: 6 válidas, 0 inválidas.
- `openspec validate acervo-bibliotecario --strict`: válida.
- `openspec validate perfil-admin-xano --strict`: válida.
- `openspec validate reserva-pelo-bibliotecario --strict`: válida.
- Contagem do OpenSpec: acervo-bibliotecario 24/25; perfil-admin-xano
  11/15; reserva-pelo-bibliotecario 10/12. Nenhuma tarefa adicional foi
  marcada como concluída: os itens restantes exigem confirmação/execução
  remota completa, não apenas os testes e sondagens desta sessão.
- Não houve Change 100% concluída; nenhuma foi arquivada. As validações foram
  repetidas após as alterações e permaneceram verdes.

#### Tarefas ainda abertas e responsável

| Change | Tarefa(s) `[ ]` | Falta | Responsável |
|---|---|---|---|
| acervo-bibliotecario | 2.5 | Testes autenticados/sintéticos das rotas, prova de concorrência, pull de conferência da funcionalidade e limpeza remota; a publicação parcial e sondagens sem token não provam esses itens | Usuário: fornecer contas de teste e autorizar operações remotas fora do escopo atual; Copilot pode executar depois de autorização específica |
| perfil-admin-xano | 1.3 | Prova do enum/perfis em tabela descartável e limpeza confirmada | Usuário/Xano admin: autorizar e executar a prova remota; não permitida nesta sessão |
| perfil-admin-xano | 2.2 | Dry-run unitário de `usuario.xs` e pull de conferência que satisfaçam o critério exato da tarefa | Usuário: autorização específica para publicar/verificar schema; Copilot pode fazê-lo em sessão autorizada |
| perfil-admin-xano | 2.4 | Dry-run, publicação e pull individual de cada endpoint de autorização | Usuário: autorização específica para operações remotas; Copilot pode fazê-lo em sessão autorizada |
| perfil-admin-xano | 2.6 | Fixtures de contas sintéticas, testes autenticados, limpeza individual e conferência de contagens | Usuário: autorizar escrita/limpeza e fornecer contas/ambiente de teste; Copilot pode executar depois |
| reserva-pelo-bibliotecario | 2.3 | Confirmar atomicidade FIFO e execução da reserva no Xano real | Usuário: autorizar teste autenticado no workspace; Copilot pode executar depois |
| reserva-pelo-bibliotecario | 2.4 | Fixtures, testes autenticados, limpeza individual e pull/verificação remotos | Usuário: autorizar escrita/limpeza e fornecer ambiente de teste; Copilot pode executar depois |

Nenhum item local independente permaneceu em `[ ]`. O script de smoke é uma
ferramenta de verificação, não cria contas nem substitui seed/fixtures ou
operações de limpeza. As três Changes permanecem ativas porque ainda têm
tarefas remotas pendentes.

### Diagnóstico de login sintético — 2026-11-14

- O destino foi confirmado como workspace `151966` (“Augusto's Workspace”),
  branch `v1` live. A linha de base permaneceu: catálogo de títulos e categorias
  200; as três consultas `/minhas/*` sem token 401.
- Foram criadas, por autorização específica, três contas sintéticas: IDs
  `71`, `72` e `73`. Os três cadastros retornaram 200, token e perfil estudante;
  os três logins retornaram 403. Nenhuma credencial foi gravada ou registrada.
  A mensagem do login não correspondeu à lista de mensagens seguras conhecida e
  foi omitida, sem imprimir o corpo.
- Os testes cobriram e-mail minúsculo no cadastro/login, e-mail maiúsculo no
  cadastro e minúsculo no login, e maiúsculo em ambos. O resultado igual nos
  três casos descarta a normalização como causa provável. O payload do app usa
  `nome`, `email` e `senha` no cadastro e `email` e `senha` no login, em acordo
  com os endpoints.
- A correção local mudou o tipo de entrada `senha` de `password` para `text`
  em signup/login; o campo da tabela continua `password`, e não foi adicionado
  hash explícito. Isso segue o contrato documentado de `check_password` (texto
  contra hash) e o exemplo Xano de input de senha como texto.
- `pytest --ignore=evaluation`: 184 passaram; `unittest discover -s xano\tests`:
  16 passaram. A validação pelo Xano Developer MCP não foi concluída porque o
  servidor expirou durante a inicialização. O dry-run filtrado mostrou somente
  UPDATE dos dois endpoints. Não houve push: as três contas autorizadas já
  foram usadas, então não é possível fazer a verificação pós-correção com uma
  conta nova sem ultrapassar o limite aprovado. A correção remota e o teste
  autenticado pós-publicação permanecem pendentes.
