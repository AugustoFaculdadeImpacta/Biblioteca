# Relatório de execução noturna

## Fechamento — regras-e-visao-admin-v10, 2026-11-26

- A implementação local da v10 foi validada anteriormente nesta execução:
  `reflex compile --dry` passou e `pytest --ignore=evaluation -q` aprovou
  472 testes. Nenhuma escrita ou consulta nova ao Xano foi feita.
- A validação estrita da Change passou; a validação estrita das specs
  consolidadas aprovou 11 specs. As tarefas estão completas (8/8).
- Os seis deltas foram sincronizados nas specs principais e commitados em
  `39e3bc6` (`Sincronizar specs das regras de biblioteca`).
- A Change foi arquivada em
  `openspec/changes/archive/2026-11-26-regras-e-visao-admin-v10/`.
- A conferência visual renderizada do cabeçalho continua **aguardando
  conferência do usuário**; os testes de contraste calculado passaram, mas não
  foi executada verificação visual em navegador.

## Atualização — fechamento da retomada H–N, 2026-11-26

- Branch: `trabalho-autopilot`. Nenhuma chamada remota, pull, sincronização,
  publicação ou alteração no Xano foi feita nesta retomada.
- H: payloads reais de solicitação passaram a aceitar `reserva_id=0`,
  `atendida_em=0`, datas em segundos/milissegundos e estados textuais
  desconhecidos sem rejeitar o registro.
- I: o POST confirmável por `id` e `titulo_id` acrescenta o pedido ao estado
  local e não relê listas; corpo incerto mantém no máximo duas releituras.
- J: GETs pessoais idênticos usam single-flight e cache de 20 segundos por
  sessão. A escrita invalida o cache e respostas 2xx incompatíveis não repetem.
- K: o host Xano usa janela deslizante compartilhada de oito chamadas por
  20 segundos por padrão, fila assíncrona e pausa global após 429. Escritas não
  são repetidas.
- L e M: pedidos já carregados bloqueiam o POST; “Tentar de novo” continua
  sendo uma releitura única. O procedimento manual de limpeza está em
  `docs/xano-limpeza-pedidos.md`.
- Evidência local: `.\\.venv\\Scripts\\python.exe -m reflex compile --dry`
  passou; `.\\.venv\\Scripts\\python.exe -m pytest --ignore=evaluation -q`
  aprovou `420 passed` em 652,25 s.
- OpenSpec: a Change `xano-funciona-v9` passou em `--strict`; as 10 specs
  consolidadas passaram em `--strict`.
- Permanecem explicitamente bloqueadas as tarefas remotas 5.3 e 5.4:
  validação/push não concluídos por MCP e `allow_push=false`. Não há
  sincronização nem archive nesta execução.

## Atualização — diagnóstico no Perfil e verificação v9, 2026-11-25

- Tarefas locais 3.1 e 4.1 concluídas. O resumo da home mantém carregamento e retry independentes; o Perfil oferece diagnóstico somente leitura restrito ao perfil, com relatório copiável sem valores pessoais. A comparação de contratos de 5.2 já está documentada em `docs/xano-diferencas.md`.
- Commit do diagnóstico: `5d27808` (`Adiciona diagnóstico Xano no Perfil`). `.\.venv\Scripts\python.exe -m reflex compile --dry` passou; `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q` — `404 passed`.
- A suíte encontrou e motivou duas correções de teste sem reduzir suas verificações: referências hexadecimais podem ser compostas só por dígitos, e o teste de confirmação de reserva precisava recuperar sua fixture de releitura atrasada.
- `openspec validate xano-funciona-v9 --strict` considerou a Change válida; `openspec validate --specs --strict` aprovou 10 specs. O delta do contraste foi classificado como requisito novo (`ADDED`), pois não existe ainda na spec consolidada, e não há aviso de arquivamento na validação.
- 5.3 continua bloqueada: a tentativa anterior de validação XanoScript pelo MCP expirou na negociação. 5.4 continua bloqueada por `allow_push=false`. Nenhum acesso de escrita ao Xano ou novo pull foi feito nesta retomada; não sincronizei nem arquivei a Change.

## Atualização — confirmação de solicitação de reserva, 2026-11-24

- O Reflex agora mantém a escrita POST única e, quando seu 2xx não tem corpo interpretável, repete apenas as leituras pessoais de solicitações/reservas: uma leitura inicial e até duas releituras com intervalos curtos. A solicitação continua bloqueada se nenhum registro correspondente aparecer; o teste cobre registro tardio e ausência persistente até atualização manual.
- A comparação estática confirmou que o Reflex envia `titulo_id` e chama os caminhos de leitura publicados. O endpoint live `POST /solicitacoes-emprestimo` ainda diverge da fonte local por não verificar solicitação/reserva ativa duplicada.
- Xano CLI confirmou workspace `151966`, branch `v1` live e `allow_push=false`. Nenhum push, alteração de preferência, leitura de registros reais ou escrita remota foi feito. A publicação do endpoint divergente depende de atualização e publicação manual no painel.
- Validação local: `reflex compile --dry` passou; `pytest --ignore=evaluation -q` aprovou 377 testes; `openspec validate xano-funciona-v9 --strict` passou e `openspec validate --specs --strict` aprovou 10 specs. A tentativa de pytest sem exclusão não coletou `evaluation/reflex-poc/tests/test_mock_api.py` porque `fastapi` não está instalado; essa pasta é excluída pelo script oficial.
- O Xano Developer MCP não concluiu a negociação para validar os oito XanoScript; portanto, essa validação e a confirmação de runtime permanecem pendentes. Não foi executado build de produção nem robô visual.
- O teste anterior foi refeito porque o bloqueio agora precisa durar até o fim da releitura após um POST incerto, e não apenas durante o POST; a nova regressão tenta uma segunda chamada enquanto a releitura está suspensa e confirma que não há segundo POST.

## Atualização — estabiliza-xano-v8, 2026-11-24

### Integração e validação local

- Branch: `trabalho-autopilot`.
- `scripts/verificar.ps1` passou: `reflex compile --dry` compilou e
  `pytest --ignore=evaluation` aprovou 354 testes.
- OpenSpec: Change `estabiliza-xano-v8` válida com `--strict`; deltas
  sincronizados e 10 specs consolidadas válidas com `--strict`. A Change foi
  arquivada em `openspec/changes/archive/2026-11-24-estabiliza-xano-v8/`.
- Commits de implementação e evidência foram feitos em lotes pequenos em
  português. Nenhuma operação de escrita, sincronização ou seed foi enviada ao
  Xano.

### Robô visual — última execução

| Rota | Perfil | Largura | Tema | Resultado |
|---|---|---:|---|---|
| `/` | visitante | 360 | claro | FALHOU: cabeçalho ausente no erro do navegador |
| `/` | visitante | 360 | escuro | FALHOU: cabeçalho ausente no erro do navegador |
| `/` | visitante | 1366 | claro | FALHOU: cabeçalho ausente no erro do navegador |
| `/` | visitante | 1366 | escuro | FALHOU: cabeçalho ausente no erro do navegador |
| `/catalogo` | visitante | 360 | claro | FALHOU: redirecionado para `/` no erro |
| `/catalogo` | visitante | 360 | escuro | FALHOU: redirecionado para `/` no erro |
| `/catalogo` | visitante | 1366 | claro | FALHOU: redirecionado para `/` no erro |
| `/catalogo` | visitante | 1366 | escuro | FALHOU: redirecionado para `/` no erro |
| `/login` | visitante | 360 | claro | FALHOU: redirecionado para `/` no erro |
| `/login` | visitante | 360 | escuro | FALHOU: redirecionado para `/` no erro |
| `/login` | visitante | 1366 | claro | FALHOU: redirecionado para `/` no erro |
| `/login` | visitante | 1366 | escuro | FALHOU: redirecionado para `/` no erro |

O build de produção do Reflex terminou antes da abertura do frontend: o
prerender de `/` excedeu o timeout. O frontend em `localhost:3000` não ficou
disponível e o robô não confirmou PASSOU em nenhuma combinação. Capturas e
linhas detalhadas da última rodada estão em
`docs/verificacao-layout.md` (rodada `2026-11-24T16:27:51.968Z`).

A aparência implementada está **aguardando conferência do usuário**. A rodada
não verificou visualmente o aplicativo; a falha no prerender impediu iniciar o
frontend que seria inspecionado.

Não verificado visualmente nesta execução: contraste renderizado, composição
final da página, menus, perfis autenticados, fluxos de reserva/acervo/admin e
continuidade da importação em navegador real. Essas lacunas não foram convertidas
em PASSOU.

## Fase 0 — preflight

- Branch local: `trabalho-autopilot`.
- Tag de segurança `ponto-seguro-antes-da-noite`: presente.
- Antes da execução, `git status --short` mostrou somente alterações preexistentes em `.gitignore` e `.mcp.json`; esses arquivos ficam fora do escopo e de qualquer commit.
- Destino Xano confirmado pelo CLI: workspace `151966`, branch `v1` live. O pull somente de definições desta execução trouxe 67 documentos. O campo `allow_push` não veio no objeto consultado e não foi alterado.
- Linha de base HTTP: `GET /catalogo/titulos` = 200, JSON válido com 2 itens; `GET /catalogo/categorias` = 200, 8 itens; GET sem token em `/minhas/emprestimos`, `/minhas/solicitacoes` e `/minhas/reservas` = 401.
- Ambiente local: Reflex 0.10.0 instalado e fixado; portas 3000, 8000 e 8765 livres.
- OpenSpec: raiz local confirmada. Progresso inicial: `acervo-bibliotecario` 24/25, `perfil-admin-xano` 11/15 e `reserva-pelo-bibliotecario` 10/12. Nenhuma delas estava completa para archive.
- Nenhuma escrita remota foi realizada nesta fase.

## Acompanhamento

As fases funcionais avançaram parcialmente. A tentativa de seed remoto foi interrompida após limitação HTTP; os fluxos de escrita do estudante, a verificação integrada e o polimento visual permanecem pendentes. A validação local, a simulada e a remota são identificadas separadamente.

## Fase 1 — cadastro e autenticação

- Criada uma conta sintética de estudante pelo endpoint de cadastro autorizado; o ID numérico foi guardado somente no estado desta sessão para limpeza manual posterior. Credenciais não foram impressas nem gravadas.
- Resultados remotos: cadastro 200; login correto 200 com perfil `estudante`; senha incorreta 403; e-mail inexistente 403.
- Smoke autenticado do estudante: `/auth/me` 200 (1 registro); `/minhas/emprestimos`, `/minhas/solicitacoes` e `/minhas/reservas` 200 (0 registros cada).
- `python -m reflex compile --dry` passou. A tentativa de iniciar em produção falhou durante a exportação do frontend via Bun; não foi usado modo de desenvolvimento. O processo e o serviço local efêmero foram encerrados, e as portas 3000, 8000 e 8765 foram confirmadas livres.
- Smoke de bibliotecário/admin e seed ainda não executados; não havia credenciais desses perfis no ambiente.

## Fase 2 — fluxos do estudante

- Smoke de leitura autenticado concluído com a conta sintética da fase 1: todas as rotas pessoais responderam 200 e não havia registros.
- Os 2 títulos atuais não correspondem a nenhum título do conjunto de seed. Nenhum empréstimo ou reserva foi criado sobre esses títulos; os fluxos de escrita do estudante aguardam a preparação autorizada do catálogo na fase 5.

## Fase 3 — operações bibliotecárias

- Criada uma conta sintética e promovida a `bibliotecario` por atualização individual documentada da Metadata API, enviando somente o campo `perfil`. A leitura antes/depois confirmou que os demais campos permaneceram iguais.
- Login autenticado: 200 com perfil `bibliotecario`. Smoke: `/auth/me`, `/admin/acervo`, `/admin/solicitacoes`, `/admin/reservas` e `/admin/emprestimos` responderam 200; as quatro listagens administrativas estavam vazias, exceto o acervo, que continha 2 títulos.
- O ID dessa conta foi guardado somente no estado desta sessão. Credenciais e host não foram impressos nem gravados.
- Criada a conta sintética admin ID 78 e promovida pelo mesmo método, enviando somente `perfil`; a leitura antes/depois confirmou que os demais campos permaneceram iguais. Login 200 com perfil `admin`; `GET /admin/usuarios` respondeu 200 com 2 itens e sem campos de credencial.
- Com essa conta, a desativação e a reativação da conta bibliotecária ID 76 responderam 200. A leitura posterior confirmou `ativo=true`; nenhum outro usuário foi alterado.
- Smoke admin: `/auth/me`, `/admin/acervo`, `/admin/solicitacoes` e `/admin/reservas` responderam 200. `/admin/emprestimos` e uma chamada posterior a `/admin/usuarios` responderam 429 durante limitação da API; o GET direto de `/admin/usuarios` feito antes do limite respondeu 200.

## Fase 4 — seed e catálogo

- Prévia local do seed: 7 categorias e 30 títulos; nenhuma chamada remota.
- A execução autorizada de `--apply --confirm-destination` terminou com código de saída 1. A saída detalhada foi capturada pelo processo e não foi preservada; portanto, a causa exata não está confirmada. Leituras públicas imediatamente antes/depois retornaram 429 e, após a janela de limite, voltaram a 200.
- Verificação posterior: `/catalogo/categorias` 200 com 8 itens e `/catalogo/titulos` 200 com 2 itens, iguais à linha de base. Não há criação de categoria ou título observável. Não repeti a escrita: o token admin existiu somente em memória, e as três promoções sintéticas autorizadas já foram usadas.
- O seed não pode ser considerado concluído. Não foram criados empréstimos ou reservas; as escritas do estudante continuam pendentes.

## Fase 5 — OpenSpec, testes e interface

- `python -m pytest --ignore=evaluation`: 184 testes aprovados. `python -m unittest discover -s xano\tests`: 16 testes aprovados.
- `openspec validate --specs --strict`: 6 specs válidas; as Changes `acervo-bibliotecario`, `perfil-admin-xano` e `reserva-pelo-bibliotecario` também passaram na validação estrita. Nenhuma foi arquivada: continuam pendentes, respectivamente, prova/integração remota; publicação e limpeza de fixtures; e execução/limpeza remota e prova de atomicidade FIFO.
- `python -m reflex compile --dry` havia passado. A execução Reflex de produção falhou durante a exportação frontend via Bun, sem servidor mantido; nenhuma verificação visual em navegador foi concluída. As portas 3000, 8000 e 8765 estão livres.
- As contas sintéticas IDs 75, 76, 77 e 78 permanecem no Xano para remoção manual autorizada posterior. Nenhuma conta ou registro foi apagado.

## Atualização — runtime Reflex no Windows, 2026-11-15

- Pull somente de definições do workspace `151966`, branch `v1`, em pasta
  temporária, sem `--records`: 67 documentos. A estrutura inclui os endpoints
  esperados sob `api/biblioteca` (autenticação, catálogo, administração e área
  pessoal), confirmando o destino da Biblioteca. Nenhuma escrita remota foi
  feita; a negociação do MCP de documentação excedeu o tempo limite.
- Duas execuções do comando `.\.venv\Scripts\python.exe -m reflex run`
  iniciaram frontend e backend juntos nas portas padrão 3000 e 8000. Em ambas,
  o processo permaneceu ativo até a verificação e não houve erro de inicialização.
- No navegador integrado, a rota pública inicial carregou título, formulário,
  estilos e recursos. A conexão de eventos Reflex recebeu quadros; o controle
  de alto contraste mudou de desligado para ligado e foi restaurado. Não havia
  mensagem de erro de conexão visível durante a verificação ativa.
- `python -m reflex compile --dry`: sucesso. Depois dos testes, todos os
  processos descendentes identificados foram encerrados e as portas 3000,
  5173, 8000, 8765 e 9000 estavam sem listeners.
- A falha histórica de frontend/`psutil.NoSuchProcess` não se repetiu. O código
  Reflex 0.10.0 instalado ainda tem uma janela de corrida na limpeza quando o
  processo frontend já desapareceu; a tarefa 1.3 continua pendente porque
  corrigir o pacote exigiria alterar `.venv`/dependências, proibido nesta
  execução. Não houve edição manual de `.web/`, `.venv/` ou `requirements.txt`.
- Revalidação local: pytest 184/184; unittest Xano 16/16.

## Continuação — 2026-11-16

### Fase 0 — estado e testes

- Branch: `trabalho-autopilot`; alterações preexistentes em `.gitignore` e
  `.mcp.json` foram preservadas.
- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation`: 193 passaram.
- `.\.venv\Scripts\python.exe -m unittest discover -s xano\tests`: 16 passaram.
- Depois da correção de mensagem descrita abaixo, os testes focados de cadastro
  e jornadas passaram: 31 testes. A suíte completa será repetida no fechamento.

### Fase 1 — runtime Reflex no Windows

- A API demonstrativa respondeu HTTP 200. A página inicial Reflex carregou com
  HTTP 200 e título esperado; uma espera curta inicial expirou, mas a navegação
  seguinte, com timeout longo, carregou normalmente.
- No navegador, um controle de acessibilidade alterou e restaurou o estado
  Reflex. Login com entrada claramente fictícia recebeu feedback em português
  esperado pelo app; a mensagem não incluiu dados da entrada. O elemento
  “Connection Error” não estava visível.
- `/_health` e `/ping` do backend responderam 200. `reflex.log` registrou
  compilação concluída e frontend/backend iniciados.
- Os processos do app/API identificados como desta execução foram encerrados.
  Depois, o PID que o netstat associa à porta 8000 não estava visível no CIM;
  não foi encerrado por não ser possível confirmar propriedade. Nenhuma
  tentativa foi iniciada sobre essa porta ocupada.
- A tarefa OpenSpec 1.3 continua pendente: a falha histórica
  `psutil.NoSuchProcess` não se repetiu, mas corrigir/testar a limpeza exigiria
  alterar `site-packages`/`.venv` ou introduzir um monkeypatch não aprovado.
  O runtime integrado foi confirmado; a Change não está completa por causa
  desse item.

### Fase 2 — cadastro e autenticação Xano

- O perfil do Xano CLI confirmou workspace `151966`. Um pull somente de
  definições na branch `v1` retornou 67 arquivos e confirmou os endpoints de
  login e cadastro; nenhum registro foi puxado e nenhum código foi publicado.
- Criada a conta sintética `79` pelo endpoint público: cadastro 200; contrato
  da sessão e login correto 200 com perfil `estudante`; senha incorreta e
  conta inexistente 403. O erro do login foi mapeado para mensagem segura em
  português.
- Catálogo: títulos 200 (2 itens), categorias 200 (8 itens). Sem token,
  `/minhas/emprestimos`, `/minhas/solicitacoes` e `/minhas/reservas` retornaram
  401. Com a sessão sintética, `/auth/me` e duas rotas pessoais retornaram 200;
  reservas atingiu 429. Tentativas de leitura das cinco rotas administrativas
  também foram limitadas a 429; isso não comprova nem refuta as guards.
- A repetição de cadastro com o mesmo endereço de teste retornou 403, embora
  `signup_POST.xs` use o erro de negócio “Este e-mail já está cadastrado.”.
  Antes da correção, o app apresentava mensagem genérica. Foi acrescentado
  tratamento por allowlist no cliente e um teste mockado de regressão.
- Não houve repetição da escrita de cadastro nem nova tentativa de login:
  credenciais e token existiram somente em memória e não foram conservados.
  O ID `79` fica para limpeza manual; nenhuma conta ou registro foi apagado.

### Fases 3 a 6 — pendências atuais

- As guards administrativas para estudante aguardam a janela do limite HTTP;
  serão tentadas novamente somente após cooldown, com resposta HTTP registrada.
- A documentação oficial confirma que atualizar um único registro pelo
  Metadata API usa `PUT` em um caminho por workspace/tabela/registro, body
  definido pelo schema e escopo “Workspace Content: Update”. Nenhuma promoção
  nova foi feita: o limite autorizado pode já estar esgotado pelas promoções
  anteriores e não há credenciais preservadas para as contas antigas.
- A prévia/execução anterior do seed terminou sem evidência suficiente e deixou
  as contagens em 8 categorias e 2 títulos. Não foi repetida porque não há
  sessão admin sintética disponível em memória; nenhuma tabela, conta ou dado
  foi apagado.

## Demonstração integrada local — 2026-11-16

- Reflex e a API demonstrativa foram iniciados e verificados: frontend na porta
  3000, backend na 8001 e API demo na 8765. A porta 8000 já tinha um listener
  de processo não identificado; ele foi preservado.
- As jornadas foram percorridas pela interface com dados locais e em memória:
  cadastro e login de estudante, solicitação de título e consulta na área
  pessoal; login de bibliotecário, criação de título, categoria e exemplar, e
  processamento de solicitação na circulação.
- A API demo agora aceita cadastro em memória, autentica a senha cadastrada,
  recusa e-mail duplicado e inicia sessão de estudante. Contas e operações
  somem ao reiniciar a API; isso não comprova o comportamento do Xano.
- Nas telas verificadas em 360 px e 1366 px, não houve rolagem horizontal; o
  foco de teclado permaneceu visível.
- Validação local: `pytest --ignore=evaluation` — 198 aprovados;
  `unittest discover -s xano\tests` — 16 aprovados; 12 testes da API demo
  (cadastro, seed e circulação) aprovados; `reflex compile --dry` — sucesso.
- OpenSpec: specs estritas — 7 válidas; Changes arquivadas estritas — 17
  válidas. `jornadas-principais-biblioteca` foi sincronizada e arquivada com
  7/7 tarefas.
- A Change `execucao-reflex-windows` permanece em 6/7: falta corrigir a corrida
  `psutil.NoSuchProcess` no encerramento do frontend. A execução observada foi
  bem-sucedida, mas não elimina essa pendência.
- Não houve chamada nem escrita no Xano nesta demonstração. O runtime local
  foi deixado ativo para consulta; dados de demonstração são voláteis.

## Checklist final — continuação autônoma, 2026-11-16

- [x] **Passo 1 — commits e push:** os lotes iniciais foram enviados na branch
  `trabalho-autopilot`; o commit de documentação `d3c37f6` também foi enviado.
  Este registro e a atualização do relatório Xano serão incluídos no push de
  fechamento.
- [B] **Passo 2 — jornada real de estudante:** linha de base: títulos 200 (2),
  categorias 200 (8) e rotas pessoais sem token 401. A conta sintética 82 teve
  cadastro e login correto 200; duplicidade, senha errada e conta inexistente
  403; token adulterado 401. Com sessão, `/auth/me` e rotas pessoais 200, sem
  registros. O detalhe do título retornou 429 após o catálogo indicar um item
  disponível. As rotas administrativas e operações de circulação não foram
  chamadas após o limite; nenhum registro foi criado.
- [B] **Passo 3 — promoção de perfil:** a atualização por Metadata API exige
  credencial com escopo de edição do workspace. Não foi lida nem extraída
  credencial armazenada; nenhuma promoção foi feita. O roteiro manual está em
  [docs/passos-manuais-xano.md](./passos-manuais-xano.md).
- [x] **Passo 4 — execução:** o README documenta o modo Xano e a demonstração
  local, incluindo as portas e o diagnóstico do listener. `rxconfig.py` não
  foi alterado.
- [B] **Passo 5 — visual:** o login foi capturado em viewport de 360 px e
  1366 px; em 360 px, a largura do documento permaneceu 360 px. Um login
  claramente fictício pela interface demo mostrou a mensagem segura em
  português e não exibiu erro visível de conexão. Nenhum bloco visual novo foi
  alterado; as telas administrativas e pessoais não foram recapturadas nesta
  continuação.
- [B] **Passo 6 — fechamento:** pytest 198/198, unittest Xano 16/16 e
  `reflex compile --dry` passaram. A validação OpenSpec estrita desta rodada
  foi bloqueada pela política de execução do `openspec.ps1`; não houve
  tentativa de contornar Device Guard. A validação anterior havia confirmado
  7 specs e 17 Changes arquivadas. O frontend Reflex próprio foi encerrado e a
  porta 3000 ficou livre. As portas 8000 e 8001 permaneceram ocupadas por
  listeners sem processo identificável no CIM; a porta 8002 ainda apontava
  para um PID cujo processo deixou de ser consultável após o encerramento. A
  porta 8765 pertence a um processo Python cuja linha de comando não confirma
  o caminho do projeto. Esses listeners foram preservados; nenhuma porta
  desconhecida foi encerrada.

### Contas sintéticas e decisões

- IDs sintéticos documentados para remoção manual: 71 a 82. Nesta rodada foi
  criada somente a conta 82; as senhas e tokens foram descartados da memória.
  Nenhuma conta ou registro de circulação foi apagado.
- Depois da resposta 429, não houve repetição de chamadas remotas nem criação
  de registros. Nenhum código Xano foi alterado ou publicado.
- O runtime Reflex foi iniciado com o backend na porta alternativa 8002, pois
  a 8000 estava ocupada e a 8001 já tinha listener não identificável. O
  frontend e a interação de login demo foram verificados antes de encerrar os
  processos Reflex próprios.

## Atualização v6 — 2026-11-23

### Estado inicial

- Branch novo: `trabalho-autopilot-layout-livraria-v6`.
- A Change `layout-estavel-v5` já estava arquivada e foi usada como base.
- Antes desta rodada havia duas Changes abertas: `execucao-reflex-windows` e
  `validacao-remota-xano`.

### Evidências concluídas

- [x] Dry-run do seed: 30 títulos planejados, nenhuma escrita.
- [x] Testes locais de seed, ISBN/checksum, capas e layout.
- [x] Cabeçalho único sem hambúrguer, com grid desktop e três linhas móveis.
- [x] `reflex compile --dry`: passou.
- [x] `pytest --ignore=evaluation`: 310 testes passaram.
- [x] Script `scripts/verificar.ps1` executa compile dry e pytest em sequência.
- [x] Xano CLI confirmou workspace `151966`, branch `v1` e `allow_push=false`.
- [x] Pull somente de definições realizado para pasta temporária fora do
  repositório; nenhum `--records`, `--sync`, `--delete` ou `--truncate`.

### Seed

- Variáveis `XANO_SEED_EMAIL` e `XANO_SEED_PASSWORD` ausentes: nenhuma
  aplicação remota realizada.
- As 30 entradas usam oito categorias aprovadas, descrições próprias,
  editora, edição e ISBN-13 com checksum válido.
- Open Library não confirmou os ISBN/capas nesta máquina por 404 ou falha de
  rede; a lista continua marcada como não verificada externamente.

### Robô de layout

- Edge foi encontrado e lançado em headless na porta 9333.
- API demo e Reflex foram iniciados, aquecidos e encerrados.
- O robô excedeu o prazo sem produzir tabela completa ou capturas PNG.
- Resultado: não verificado visualmente.
- Nenhuma violação visual foi ocultada ou convertida em PASSOU.

### Fluxos funcionais

- Visitante buscando e entrando no login: não coberto pelo passe incompleto.
- Estudante reservando e acompanhando pedido: não coberto.
- Bibliotecário aceitando pedido: não coberto.
- Bibliotecário cadastrando/desativando livro: não coberto.
- Admin alternando visões e criando bibliotecário: não coberto.

### OpenSpec

- `execucao-reflex-windows` arquivada em
  `openspec/changes/archive/2026-11-23-execucao-reflex-windows`.
- `validacao-remota-xano` arquivada em
  `openspec/changes/archive/2026-11-23-validacao-remota-xano` com
  `--skip-specs`; tarefas operacionais ficaram em
  `docs/checklist-publicacao-xano.md`.
- A Change `layout-livraria-v6` permanece em andamento até a conclusão da
  verificação visual e dos fluxos.

### Usuário ainda precisa fazer

- Configurar credenciais somente no processo do seed, se houver autorização
  para aplicação remota.
- Confirmar o workspace, o ambiente, o backup e a publicação no painel Xano.
- Executar novamente o robô até produzir relatório completo ou a plataforma
  integrada confirmar a falha visual.

## Continuação autônoma — 2026-11-16, rodada seguinte

### Passo A — jornada real de estudante

- Criada uma conta sintética nova (ID 83), sem imprimir ou registrar e-mail,
  senha ou token. Cadastro e login retornaram HTTP 200.
- Catálogo retornou 200; o detalhe de um título existente retornou 200. Um
  exemplar estava disponível.
- O pedido de empréstimo retornou 200. Repetir o pedido para a mesma conta e
  título também retornou 200, e `/minhas/solicitacoes` retornou 2 itens. A API
  aceitou uma duplicata em vez de recusá-la; duas solicitações sintéticas
  permanecem no remoto, sem exclusão.
- Pedido para título inexistente retornou 404. Antes do ajuste local, a
  interface mostraria uma mensagem genérica; foram adicionados mapeamento
  seguro do erro e teste com `httpx.MockTransport`.
- Token adulterado em POST de circulação retornou 401. Rotas de acervo,
  solicitações, reservas, empréstimos e usuários retornaram 403 para
  estudante. `/admin/estudantes` sem o parâmetro obrigatório de e-mail
  retornou 400; o teste correto de autorização nessa rota permanece pendente.
- O candidato local de `solicitacoes_POST.xs` agora verifica solicitação
  pendente/em reserva e reserva aguardando/ofertada do mesmo estudante e
  título antes de inserir. Foi adicionada validação estrutural local. O
  Xano Developer MCP não inicializou (timeout de 60 s); não houve dry-run ou
  publicação. O remoto continua aceitando duplicatas até validação e
  publicação controlada.

### Passo B — Changes e próxima ação

- A revisão das cinco listas de tarefas confirmou que `acervo-bibliotecario`,
  `reserva-pelo-bibliotecario` e `perfil-admin-xano` mantêm dependências de
  verificação/publicação remota. `devolvido-em-nulavel` ainda depende da prova
  descartável obrigatória antes de qualquer migração produtiva. Não marcar
  essas tarefas remotas como concluídas nem arquivar Changes incompletas.
- `execucao-reflex-windows` continua em 6/7; a falha histórica
  `psutil.NoSuchProcess` não se reproduziu, e não há correção segura que
  dispense alterar `.venv`/site-packages.
- Próxima ação: validar o XanoScript e tentar confirmar pelo CLI se o dry-run
  filtrado é possível sem mudar `allow_push`; se o MCP/CLI ou a proteção
  impedir a prova, registrar bloqueio e seguir para a revisão visual local.

### Testes do Passo A

- `pytest tests\test_student_area.py -q`: 27 aprovados, incluindo as
  mensagens mockadas de duplicidade e título inexistente.
- `unittest discover -s xano\tests`: 17 aprovados, incluindo a guarda
  estrutural candidata contra solicitação duplicada.
- A suíte completa e as validações estritas são executadas no Passo D.

### Passo B — inventário OpenSpec e dependências

- [x] Inventário das tarefas pendentes e validação estrita das Changes.
  `openspec.cmd validate --specs --strict`: 7 passaram; `--changes --strict`:
  5 passaram; `--archived --strict`: 17 passaram. A validação estrutural não
  significa que as tarefas remotas foram executadas.
- Nenhuma Change está 100% concluída; não houve archive.
- `execucao-reflex-windows` (6/7): **1.3** — falta reproduzir a condição em
  que o frontend desaparece antes da limpeza e provar ausência de processo
  residual. Responsável: agente, somente se surgir uma solução segura no
  código do projeto; a falha histórica não se reproduziu e o ponto conhecido
  fica no Reflex instalado, cuja `.venv`/site-packages não pode ser editada.
- `acervo-bibliotecario` (24/25): **2.5** — falta sincronização/verificação de
  concorrência, conferência remota e limpeza. Responsável: agente para os
  testes e publicação sob escopo aprovado; limpeza permanece bloqueada pela
  proibição absoluta de apagar dados. A solicitação duplicada foi observada
  ao vivo; o fix local não foi publicado.
- `reserva-pelo-bibliotecario` (10/12): **2.3** — falta prova remota de
  execução/atomicidade FIFO; responsável: agente quando houver prévia e
  publicação seguras. **2.4** — faltam fixtures, limpeza individual e
  conferência; responsável: operador Xano com autorização futura para limpeza.
- `perfil-admin-xano` (11/15): **1.3** — prova de schema em tabela descartável
  e exclusão/GET 404; responsável: agente, bloqueado por não apagar dados.
  **2.2** — publicar `usuario.xs`; **2.4** — publicar guards; responsáveis:
  agente após gate de destino/prévia e autorização específica para esses
  arquivos, que não faz parte da correção isolada de duplicidade.
  **2.6** — fixtures e limpeza com contagens finais; responsável: operador
  Xano após autorização de limpeza. As quatro tarefas continuam sem execução.
- `devolvido-em-nulavel` (0/20): **1.1** — confirmação/consulta oficial e
  registro do destino, responsável: agente após disponibilidade da ferramenta
  oficial. **1.2–1.3** — sentinel, registro null, rollback e exclusões,
  bloqueados por exigirem criação e posterior exclusão. **2.1–2.3** — prova,
  schema produtivo, publicação e fixture, dependem do passo 1 e incluem
  exclusões. **3.1–3.8** — updates/pull dos sete endpoints e conferência do
  oitavo, dependem do schema nullable comprovado; responsável: agente após
  gates e aprovação, sem executar agora. **4.1** — testes estruturais depende
  dos arquivos-alvo atualizados; **4.2–4.4** — cenários exigem limpeza, vedada;
  **4.5** — documentação final depende da prova/migração; **5.1** — verify
  final depende de todos os gates. Responsável: agente após desbloqueio do
  sentinel e autorização de exclusões.
- Nenhuma tarefa pendente foi marcada como concluída por inferência. A Change
  de nulabilidade não foi aplicada, publicada ou arquivada.

## Passo C — bloco visual 1, 2026-11-16

- [x] Paleta, tipografia e espaçamento base ajustados em
  `biblioteca_mais_nova/biblioteca_mais_nova.py`, mantendo foco visível e os
  modos de acessibilidade.
- `python -m reflex compile --dry`: aprovado.
- `python -m pytest --ignore=evaluation -q`: 201 aprovados.
- Catálogo visto em captura nos viewports de 360 px e 1366 px; sem rolagem
  horizontal e com títulos e filtros presentes. As capturas foram realizadas
  pelo navegador local contra a API demonstrativa.
- A indicação acessível “Connection Error:” é o `title` permanente da camada
  do Reflex; o ícone de falha só aparece com erros de conexão. A conexão
  Socket.IO com o backend alternativo 8011 abriu e o catálogo carregou.
- Próximo: bloco 2, hierarquia do cabeçalho e navegação por perfil.

## Passo C — bloco visual 2, 2026-11-16

- [x] Cabeçalho e navegação receberam hierarquia visual, estados de hover e
  alvos de navegação com altura mínima de 2,5 rem; os destinos por perfil
  continuam condicionados às permissões existentes.
- `python -m reflex compile --dry`: aprovado.
- `python -m pytest --ignore=evaluation -q`: 201 aprovados. A expectativa de
  cor do link no teste de navegação foi atualizada para a nova paleta.
- Catálogo visto em captura nos viewports de 360 px e 1366 px; sem rolagem
  horizontal em ambos.
- Próximo: bloco 3, cartões e filtros do catálogo.

## Passo C — bloco visual 3, 2026-11-16

- [x] Cartões, campos de filtro e ações do catálogo receberam contraste,
  hierarquia e estados de interação discretos, sem animações pesadas.
- `python -m reflex compile --dry`: aprovado.
- `python -m pytest --ignore=evaluation -q`: 201 aprovados.
- Catálogo visto em captura nos viewports de 360 px e 1366 px; sem rolagem
  horizontal. No navegador local, a busca por título filtrou para 1 cartão e
  a categoria Literatura filtrou para 18.
- Próximo: bloco 4, formulários e tabelas da bibliotecária.

## Passo C — bloco visual 4, 2026-11-16

- [x] Formulários, cartões de título, exemplares e painéis de circulação
  receberam superfícies, bordas, espaçamento e estados desabilitados coerentes.
- `python -m reflex compile --dry`: aprovado.
- `python -m pytest --ignore=evaluation -q`: 201 aprovados.
- [B] As telas administrativas não puderam ser vistas na captura: abrir
  `/admin/acervo` sem sessão redireciona corretamente para `/login`, em 360 px
  e 1366 px. Não há sessão bibliotecária/admin autenticada no navegador. A
  verificação DOM confirmou ausência de rolagem horizontal na tela de login;
  os componentes administrativos foram compilados, mas não inspecionados
  visualmente no navegador.
- Próximo: bloco 5, Minha biblioteca.

## Passo C — bloco visual 5, 2026-11-16

- [x] A área Minha biblioteca recebeu painéis consistentes e estados vazios
  claramente delimitados, preservando as três seções de empréstimos,
  solicitações e reservas.
- `python -m reflex compile --dry`: aprovado.
- `python -m pytest --ignore=evaluation -q`: 201 aprovados.
- Na API demo local, o cadastro pela interface redirecionou ao catálogo e a
  sessão assumiu perfil estudante. Uma solicitação de um título existente foi
  confirmada pela interface e apareceu em Minha biblioteca após o carregamento
  dos dados. Nenhuma escrita foi feita no Xano real.
- Minha biblioteca foi vista em captura nos viewports de 360 px e 1366 px,
  com uma solicitação, estados vazios de empréstimos/reservas e sem rolagem
  horizontal; nenhum e-mail ou credencial apareceu no conteúdo.
- Próximo: bloco 6, estados de carregamento, vazio, erro e sucesso.

## Passo C — bloco visual 6, 2026-11-16

- [x] Estados de carregamento, vazio, erro e sucesso receberam largura,
  contraste, espaçamento e distinção visual sem alterar os rótulos acessíveis.
- [x] Durante o teste local, a duplicidade recebeu inicialmente uma mensagem
  genérica porque o texto da API demo não constava na lista segura. O cliente
  agora mapeia as mensagens exatas de solicitação/reserva duplicada para
  instruções claras; a regressão usa `httpx.MockTransport`.
- `python -m reflex compile --dry`: aprovado.
- `python -m pytest --ignore=evaluation -q`: 203 aprovados.
- No fluxo da API demo local, a solicitação repetida não criou novo registro e
  agora mostra “Você já tem uma solicitação ativa para este título. Consulte
  Minha biblioteca.”. A busca sem resultados mostra o estado vazio esperado.
- A mensagem de erro foi vista em captura nos viewports de 360 px e 1366 px;
  métricas DOM em ambos indicaram ausência de rolagem horizontal.

## Retentativa do bloqueio Xano — 2026-11-16

- [B] Após concluir os blocos locais, a validação do XanoScript, a consulta de
  versão do Xano Developer MCP e a consulta de documentação do CLI foram
  tentadas novamente. As três falharam na inicialização com timeout de
  negociação do MCP de 60 segundos.
- Não houve comando Xano CLI, dry-run, sincronização ou publicação nesta
  retentativa. O candidato de guarda de duplicidade permanece local e não
  validado oficialmente; não foi arquivado como Change concluída.

## Fechamento final — 2026-11-16

- [x] Suíte final: `pytest --ignore=evaluation -q`: 203 aprovados;
  `unittest discover -s xano\tests`: 17 aprovados; `reflex compile --dry`:
  compilação aprovada.
- [x] OpenSpec estrito: 7 specs, 5 Changes ativas e 17 Changes arquivadas
  validadas, sem falhas.
- [B] A validação oficial do XanoScript e a consulta de versão/documentação
  continuam bloqueadas pelo timeout de inicialização do Xano Developer MCP.
  Nenhum comando do Xano CLI, chamada ao Xano real ou publicação foi feita
  neste fechamento.
- [B] O shell Reflex próprio (PID 8872) foi encerrado. As portas 3000 e 8765
  estão livres. Permanecem listeners em 8000 (PID 3860), 8001 (PID 6296),
  8002 (PID 3516), 8010 (PID 9788) e 8011 (PID 9240); a consulta de processo
  não conseguiu identificar os respectivos proprietários/linhas de comando.
  Nenhum desses listeners foi encerrado por não ser possível confirmar sua
  identidade.
- O candidato Xano local contra solicitações duplicadas não foi publicado.
  No Xano real, a duplicidade observada na solicitação ID 83 continua pendente
  de correção/publicação; as contas sintéticas e solicitações já registradas
  não foram apagadas.
- Branch `trabalho-autopilot`. As alterações preexistentes em `.gitignore` e
  `.mcp.json` foram preservadas e não fazem parte deste fechamento.

## Checklist final A–D

- [B] **A — estudante no Xano real:** conta sintética ID 83: cadastro/login
  200; pedido inicial 200; pedido duplicado também 200 e duas solicitações
  apareceram na lista; título inexistente 404; token adulterado 401; rotas
  administrativas testadas responderam 403, exceto `/admin/estudantes`, que
  respondeu 400 sem o parâmetro obrigatório. O detalhe do título respondeu
  429 em uma tentativa. A API remota ainda aceita duplicidade e o guard local
  não foi publicado, pois o MCP oficial falhou por timeout; não foi possível
  cumprir o critério remoto de rejeição.
- [x] **B — inventário OpenSpec local:** tarefas e responsáveis pendentes
  registrados acima; contagens conferidas diretamente nos `tasks.md`:
  `execucao-reflex-windows` 6/7, `acervo-bibliotecario` 24/25,
  `reserva-pelo-bibliotecario` 10/12, `perfil-admin-xano` 11/15 e
  `devolvido-em-nulavel` 0/20. Nenhuma está completa; nenhuma foi arquivada.
- [x] **C — interface local:** seis blocos visuais implementados e verificados
  contra a API demo; capturas de telas de estudante em 360 px e 1366 px.
  [B] A tela administrativa não foi vista por falta de sessão administrativa.
- [B] **D — fechamento:** pytest 203/203, unittest Xano 17/17, compilação
  Reflex e validações estritas passaram; relatórios foram atualizados. O shell
  próprio foi encerrado, mas não foi seguro encerrar os listeners sem processo
  identificável: 8000/PID 3860, 8001/PID 6296, 8002/PID 3516, 8010/PID 9788
  e 8011/PID 9240. As portas 3000 e 8765 estão livres. O commit do relatório
  foi enviado pela branch autorizada; `.gitignore` e `.mcp.json` seguem fora
  do commit.

## Continuação — redução das Changes, 2026-11-17

### Inventário antes dos archives

`openspec.cmd list --json` antes desta rodada:

```json
{
  "changes": [
    {"name": "devolvido-em-nulavel", "completedTasks": 0, "totalTasks": 20, "status": "in-progress"},
    {"name": "validacao-remota-xano", "completedTasks": 0, "totalTasks": 15, "status": "in-progress"},
    {"name": "execucao-reflex-windows", "completedTasks": 6, "totalTasks": 7, "status": "in-progress"},
    {"name": "perfil-admin-xano", "completedTasks": 11, "totalTasks": 15, "status": "in-progress"},
    {"name": "acervo-bibliotecario", "completedTasks": 24, "totalTasks": 25, "status": "in-progress"},
    {"name": "reserva-pelo-bibliotecario", "completedTasks": 10, "totalTasks": 12, "status": "in-progress"}
  ],
  "root": {"path": "C:\\Users\\User\\Biblioteca\\Biblioteca\\Biblioteca", "source": "nearest"}
}
```

## Continuação — Change ajustes-visuais-v3

### Evidências dos itens concluídos

| Item | Commit | Testes novos/alterados | Status |
|---|---|---|---|
| 1 — primários escuros | `f5f2818`, `ded0dc0` | `test_primary_actions_meet_wcag_contrast` e correção de `test_dark_cover_fallbacks_use_saturated_palette` | Feito, aguarda conferência visual |
| 2 — campos e autofill | `ad51bd2` | `test_text_fields_align_and_autofill_safely`, `test_editing_controls_keep_external_border_only`, `test_category_checkboxes_share_44px_row` | Feito, aguarda conferência visual |
| 3 — destino do tema | `eb9485e` | `test_theme_switch_reports_effective_destination` | Feito, aguarda conferência visual |
| 4 — emojis decorativos | `24b955f` | `test_decorative_emojis_are_aria_hidden` | Feito, aguarda conferência visual |
| 5 — animações leves | `012b03a`, `fea2456` | `test_motion_rules_have_reduced_motion_override` | Feito, aguarda conferência visual |
| 6 — capas únicas | `8d987cf`, `cfc1792`, `9d569dc` | `test_generated_cover_is_deterministic`, `test_generated_cover_is_distinct_across_seed_titles`, `test_generated_cover_has_no_external_scripts`, `test_generated_cover_handles_invalid_data`, `test_catalog_cover_grid_has_bounded_card_size` | Feito, aguarda conferência visual |
| 7 — desativar título | `92fa83d`, `edbcd6b`, `c90f08d` | `test_admin_actions_handle_success_404_403_and_connection` e regressões do Acervo | Feito localmente; validação remota pendente |
| 8 — Acervo compacto | `e0b6110`, `17a4c22` | `test_acervo_search_normalizes_text_and_empty_state`, `test_acervo_has_one_edit_panel`, `test_acervo_paginates_in_groups_of_ten`, `test_staff_can_edit_from_catalog_and_detail` | Feito, aguarda conferência visual |
| 9 — seed seguro | `a9a323a`, `4bcd52f` | `test_dry_run_makes_no_write`, `test_apply_without_credentials_aborts`, `test_seed_mapping_categories_and_idempotency`, `test_seed_never_prints_password` | Pronto; não aplicado ao Xano |
| 10 — limpeza da Change | `829dc3c`, `317aee7` | Nenhum teste novo; `openspec.cmd validate --specs --strict` aprovou 7 specs | Arquivada sem sincronizar specs |
| 11 — relatório e fechamento | `bc8dd28` | Nenhum teste novo; validação da Change, specs e compilação final | Arquivada em `2026-11-22-ajustes-visuais-v3`; push pendente até este commit |

### Verificações locais

- `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado após as implementações.
- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: regressão final 277 testes aprovados nesta retomada; o Acervo compacto foi confirmado em suíte completa anterior com 273.
- Seed dry-run: 30 títulos planejados, nenhuma escrita.
- Não houve navegador, capturas ou operações remotas de escrita.

### O que o usuário precisa publicar no Xano

- Confirmar em runtime `PATCH /catalogo/titulos/{titulo_id}` no workspace selecionado.
- Publicar ou confirmar a rota com perfil bibliotecário/admin, bloqueios de empréstimo ativo e reserva ativa e resposta segura para sucesso, 404 e 403.
- Arquivos de origem: `xano/api/default/catalogo/titulos_id_PATCH.xs` e `api/biblioteca/catalogo/titulos/titulo_id_PATCH.xs`.
- Um pull somente de definições trouxe 67 documentos para pasta temporária e mostrou a rota remota correspondente. A rota não foi alterada nem publicada nesta sessão.

### Estado OpenSpec

```json
{
  "changes": [
    {"name": "ajustes-visuais-v3", "completedTasks": 10, "totalTasks": 11, "status": "in-progress"},
    {"name": "validacao-remota-xano", "completedTasks": 0, "totalTasks": 29, "status": "in-progress"},
    {"name": "execucao-reflex-windows", "completedTasks": 6, "totalTasks": 7, "status": "in-progress"}
  ]
}
```

## Atualização final — navegação e rotas

### Estado e evidência

- Branch: `trabalho-autopilot`.
- Código da navegação entregue em commits pequenos: `e934ad83f1d5448a1d880cb9ffa5a5a8b03055d3` (cabeçalho/menu), `8bf937f6a1b46f8fd9ec5ac909caa9adf98bd27b` (home), `490a0f183d927b9d6a3d1b896b969da9216e2b10` (formulários), `1bb4a6307a44db628e0ade66ca5af28860421125` (redirecionamentos), `8d263cec87bdff0125d9492be4a172bcd661510e` (perfil/acessibilidade), `96bdfbb980e459d42580d9c13cab92e0f6ef862d` (rodapé) e `7cdf51a3e576a03e79df7408f15c554ce97654ba` (gatilho do menu).
- `.\.venv\Scripts\python.exe -m reflex compile --dry`: sucesso, compilação concluída.
- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: `223 passed`, 0 falhas.
- `openspec.cmd validate --specs --strict`: 7 passaram, 0 falharam. `openspec.cmd validate refino-visual-biblioteca --strict`: Change válida.
- Status OpenSpec: 1/13 tarefas concluída; as demais continuam bloqueadas por evidência visual/DOM pendente. Não arquivada.
- Xano real: nenhuma escrita foi feita.
- Inspeção atual: `openBrowserPage` em `http://127.0.0.1:3010/` retornou somente “Connection Error:”. Não houve hidratação, captura posterior, DOM mensurável ou inspeção visual das telas. O HTTP 200 anteriormente observado no frontend não prova que o navegador renderizou a aplicação.

### Rotas solicitadas

“Implementado/testado” abaixo significa que o componente/rota está no código e os testes automatizados correspondentes passaram; não significa que a tela atual foi vista no navegador. Nenhuma rota possui captura “depois” válida.

| Rota / tela | Perfil | Antes | Depois | 360 px | 1366 px | Estado visual |
|---|---|---|---|---|---|---|
| `/` — vitrine, busca e seções públicas | Visitante; atalhos conforme sessão | [home-antes-360.png](./capturas/home-antes-360.png), [home-antes-1366.png](./capturas/home-antes-1366.png); também há [home-tokens-360.png](./capturas/home-tokens-360.png) e [home-before-nav-1366.png](./capturas/home-before-nav-1366.png) de estados anteriores | Não capturada | A imagem `home-tokens-360.png` é 360×900, mas anterior à navegação final; DOM atual não medido | `home-before-nav-1366.png` é 1366×900, mas anterior à navegação final; DOM atual não medido | Só alterado; versão atual não vista |
| `/login` — somente formulário de login | Visitante; sessão autenticada redireciona | [login-antes-360.png](./capturas/login-antes-360.png) | Não capturada | A imagem existente é 450×1125, não prova viewport de 360 px; DOM atual não medido | Não capturada; DOM atual não medido | Só alterado; não visto |
| `/cadastro` — somente formulário de cadastro | Visitante; sessão autenticada redireciona | Não capturada | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Só alterado; não visto |
| `/catalogo` — busca, filtros e cartões | Visitante | [catalogo-antes-1366.png](./capturas/catalogo-antes-1366.png) | Não capturada | Não capturada; DOM não medido | A imagem existente é 1280×960, não prova viewport de 1366 px; DOM atual não medido | Só alterado; não visto |
| `/catalogo/[titulo_id]` — detalhe do título | Visitante | Não capturada | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Só alterado; não visto |
| `/minha-biblioteca` — empréstimos e reservas | Estudante | Não capturada | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Só alterado; não visto |
| `/admin/acervo` — acervo | Bibliotecária/admin; menu segue visão ativa | Não capturada | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Só alterado; não visto |
| `/admin/reservas` — reservas | Bibliotecária/admin; menu segue visão ativa | Não capturada | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Só alterado; não visto |
| `/admin/circulacao` — circulação | Bibliotecária/admin; menu segue visão ativa | Não capturada | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Só alterado; não visto |
| `/admin/bibliotecarios` — gestão de bibliotecários | Admin | Não capturada | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Só alterado; não visto |
| `/perfil` — identidade somente leitura da sessão | Usuário autenticado | Não existia nesta Change | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Implementado/testado; não visto |
| `/acessibilidade` — controles locais | Visitante e usuários autenticados | Não existia nesta Change | Não capturada | Não capturada; DOM não medido | Não capturada; DOM não medido | Implementado/testado; não visto |
| Menu “Perfil” aberto por visitante/estudante/bibliotecária/admin | Todos os perfis conforme sessão/visão | Não capturada | Não capturada | Não capturada; interação/DOM não medidos | Não capturada; interação/DOM não medidos | Estrutura/state testados; interação visual não vista |

As capturas antigas com “360” ou “1366” no nome nem sempre têm exatamente essas dimensões ou representam a versão atual. Não foram reaproveitadas como capturas “depois”. Caminhos de capturas posteriores: **nenhum**.

### Cabeçalho, menu Perfil e retorno à visão admin

O código usa `rx.menu` em [profile_menu](../biblioteca_mais_nova/biblioteca_mais_nova.py#L1944). Visitante recebe “Entrar” e “Cadastrar-se”; usuário autenticado recebe identidade somente leitura, “Meu perfil”, “Acessibilidade” e “Sair”. O menu admin inclui as opções de visão com `aria_checked` e ações de seleção. A navegação principal é condicional ao perfil/visão em [site_primary_nav](../biblioteca_mais_nova/biblioteca_mais_nova.py#L1879).

Sim: o código mantém o seletor disponível ao admin nas visões simuladas e permite retornar à visão de admin. A faixa e o botão “Voltar à visão de admin” são renderizados fora do conteúdo suspenso do menu, no cabeçalho, em [admin_view_status](../biblioteca_mais_nova/biblioteca_mais_nova.py#L1907). Isso é confirmado estruturalmente por `test_navigation_items_follow_profile_and_active_view`, `test_admin_view_mode_controls_are_visible_and_accessible`, `test_admin_view_mode_can_reset_and_is_hidden_for_non_admin` e `test_admin_view_mode_changes_navigation_without_changing_session`, em [test_navigation.py](../tests/test_navigation.py#L239). O cabeçalho por rota também é coberto por `test_header_has_catalog_and_profile_on_every_route` e `test_all_routes_use_one_shared_header_and_footer`. Não foi possível confirmar por interação real no navegador que Esc fecha o menu e devolve foco ao gatilho.

### Testes específicos de navegação

Passaram na suíte final: `test_home_has_no_login_or_signup_form_and_keeps_profile_shortcuts`, `test_login_page_contains_only_login_form`, `test_signup_page_contains_only_signup_form`, `test_authenticated_users_redirect_from_auth_pages_to_profile_home`, `test_profile_page_shows_session_identity_read_only`, `test_accessibility_page_reuses_existing_controls`, `test_profile_menu_for_visitor_has_login_and_signup`, `test_profile_menu_for_authenticated_user_has_profile_accessibility_and_logout`, `test_navigation_items_follow_profile_and_active_view`, `test_all_routes_use_one_shared_header_and_footer` e `test_page_bodies_do_not_duplicate_global_navigation`. Os testes são automatizados de estrutura/estado e não substituem a inspeção visual/teclado no navegador.

### Saída final de `openspec.cmd list --json`

```json
{
  "changes": [
    {
      "name": "refino-visual-biblioteca",
      "completedTasks": 1,
      "totalTasks": 13,
      "lastModified": "2026-11-18T19:29:45.836Z",
      "status": "in-progress"
    },
    {
      "name": "validacao-remota-xano",
      "completedTasks": 0,
      "totalTasks": 22,
      "lastModified": "2026-11-17T05:16:18.677Z",
      "status": "in-progress"
    },
    {
      "name": "execucao-reflex-windows",
      "completedTasks": 6,
      "totalTasks": 7,
      "lastModified": "2026-11-15T17:36:02.160Z",
      "status": "in-progress"
    }
  ],
  "root": {
    "path": "C:\\Users\\User\\Biblioteca\\Biblioteca\\Biblioteca",
    "source": "nearest"
  }
}
```

### Resultado

- [x] Os deltas de acervo, reservas, perfil e execução Reflex estão alinhados às specs principais. Comparação dos requisitos delta: 32 verificados, 0 divergências. `openspec.cmd validate --specs --strict` passou com 7 specs e 0 falhas antes do archive.
- [x] `acervo-bibliotecario`, `reserva-pelo-bibliotecario` e `perfil-admin-xano` arquivadas após confirmar seus artefatos e tarefas locais completos; as tarefas remotas pendentes foram transferidas, sem serem marcadas como feitas, para `validacao-remota-xano`. A validação estrita passou depois de cada archive.
- [x] `devolvido-em-nulavel` arquivada sem sincronizar specs: o status OpenSpec não lista delta specs; a inspeção anterior via pull somente de definições trouxe 67 documentos. O campo remoto e `xano/table/emprestimo.xs` são nullable e o cliente local aceita `None` e `0`. Não foram consultados registros remotos. As 20 tarefas permanecem não concluídas; a conclusão é que a alteração proposta é desnecessária diante das evidências de schema e código, não que os testes de migração foram executados.
- [B] `execucao-reflex-windows` permanece ativa em 6/7. A tarefa 1.3 continua aberta porque a corrida conhecida está no Reflex instalado e não há correção segura confirmada no código do projeto; nenhum arquivo de `.venv`/`site-packages` foi alterado.
- [B] `openspec.cmd validate --archived --strict` encontrou 20 Changes arquivadas válidas e uma inválida: `2026-11-17-devolvido-em-nulavel`, por manter honestamente 20/20 tarefas não realizadas. Não foram marcadas como concluídas nem removidas para mascarar a pendência. As specs estritas passaram após cada archive.
- [x] `docs/mapa-changes.md` atualizado para refletir as duas Changes ativas e as quatro arquivadas.

Lista final capturada por `openspec.cmd list --json`:

```json
{
  "changes": [
    {"name": "validacao-remota-xano", "completedTasks": 0, "totalTasks": 22, "status": "in-progress"},
    {"name": "execucao-reflex-windows", "completedTasks": 6, "totalTasks": 7, "status": "in-progress"}
  ],
  "root": {"path": "C:\\Users\\User\\Biblioteca\\Biblioteca\\Biblioteca", "source": "nearest"}
}
```

Resultado final: 2 Changes ativas; quatro Changes arquivadas; as 7 tarefas transferidas para `validacao-remota-xano` continuam abertas. Os `tasks.md` arquivados mantêm sem conclusão tarefas que não foram realizadas. Validação estrita repetida após cada archive: 7 specs, 0 falhas.

## Continuação — Change refino-visual-biblioteca, bloco 5

### Verificações desta retomada

- Bloco 5 implementado no commit `c17da0530aeeeee2f8f4e838607279c4be8672f5`.
- `.venv\Scripts\python.exe -m reflex compile --dry`: `Success: App compiled successfully in 14.248 seconds.`
- Suíte completa: `211 passed, 1 warning in 35.66s`. O runner desabilitou somente `app._compile` automático durante `pytest`; a compilação Reflex foi executada separadamente. Isso evitou que o teste de privacidade tentasse instalar pacotes com lockfile congelado divergente.
- Testes novos: `test_forms_and_admin_panels_use_shared_visual_states` e `test_touch_targets_and_keyboard_accessibility_at_mobile_viewport`, em `tests/test_frontend_foundation.py`. Também foi atualizada a expectativa de `test_site_header_brand_and_footer_links_preserve_profile_access`, em `tests/test_navigation.py`.
- Navegador: abrir `http://127.0.0.1:3010/` expirou após 30 s; `readPage` exibiu apenas “Connection Error:”. Não foi obtida captura posterior nem DOM hidratado. Inspeção visual e métricas DOM atuais: **não verificadas; visual não visto**.
- Nenhuma operação de escrita no Xano foi feita.

### Telas, perfis e evidência visual

“Antes” indica apenas o caminho de uma captura existente; não implica que a tela atual foi vista. “Depois” e as métricas DOM ficam não verificados quando não há uma captura posterior válida.

| Tela / rota | Perfil | 360 px (antes / depois) | 1366 px (antes / depois) | Situação |
|---|---|---|---|---|
| Início `/` | Visitante | Antes: [home-antes-360.png](./capturas/home-antes-360.png); depois: não capturada; DOM: não medido | Antes: [home-antes-1366.png](./capturas/home-antes-1366.png); depois: não capturada; DOM: não medido | Captura antes de 360 px vista e mostra os defeitos originais; versão atual só alterada, visual não visto |
| Catálogo `/catalogo` | Visitante | Antes/depois: não capturadas; DOM: não medido | Antes: [catalogo-antes-1366.png](./capturas/catalogo-antes-1366.png); depois: não capturada; DOM: não medido | Só alterado, visual não visto |
| Detalhe `/catalogo/[titulo_id]` | Visitante | Antes/depois: não capturadas; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Só alterado, visual não visto |
| Login `/login` | Visitante | Antes: [login-antes-360.png](./capturas/login-antes-360.png); depois: não capturada; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Só alterado, visual não visto |
| Cadastro `/cadastro` | Visitante | Antes/depois: não capturadas; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Só alterado, visual não visto |
| Minha biblioteca `/minha-biblioteca` | Estudante | Antes/depois: não capturadas; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Só alterado, visual não visto nesta retomada |
| Acervo `/admin/acervo` | Bibliotecária/admin | Antes/depois: não capturadas; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Só alterado; visual não visto |
| Circulação `/admin/circulacao` | Bibliotecária/admin | Antes/depois: não capturadas; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Só alterado; visual não visto |
| Reservas `/admin/reservas` | Bibliotecária/admin | Antes/depois: não capturadas; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Só alterado; visual não visto |
| Gestão de bibliotecários `/admin/bibliotecarios` | Admin | Antes/depois: não capturadas; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Só alterado; visual não visto |
| Cabeçalho e seletor de visão (todas as rotas) | Admin; modos simulados de bibliotecária/estudante | Antes/depois: não capturadas; DOM: não medido | Antes/depois: não capturadas; DOM: não medido | Evidência automatizada abaixo; aparência visual não vista |

As imagens `home-tema-360.png`, `home-tema-1366.png` e `home-tokens-360.png` são anteriores ao ajuste final de escopo dos tokens; não servem como capturas “depois”. As métricas antigas também antecedem essa correção e não são métricas do estado atual.

### Seletor de visão do admin

Correção do trecho registrado anteriormente: o seletor atual fica dentro do menu `rx.menu` “Perfil”. A faixa “Modo de visualização” e o botão “Voltar à visão de admin” ficam fora do conteúdo suspenso do menu, no cabeçalho. Ambos são renderizados quando `State.can_manage_librarians` é verdadeiro; o botão de retorno aparece enquanto `State.admin_view_mode != ""`. A lógica está em [biblioteca_mais_nova.py](../biblioteca_mais_nova.py#L1907) e [biblioteca_mais_nova.py](../biblioteca_mais_nova.py#L1944).

```python
rx.cond(
    State.admin_view_mode != "",
    rx.button(
        "Voltar à visão de admin",
        type="button",
        on_click=State.reset_admin_view_mode,
        class_name="admin-view-reset",
    ),
    rx.fragment(),
)
```

O menu mantém as opções Admin, Bibliotecária e Estudante marcadas com `aria_checked` e seus `on_select` mudam/restauram a visão. Os testes `test_navigation_items_follow_profile_and_active_view`, `test_admin_view_mode_controls_are_visible_and_accessible`, `test_admin_view_mode_can_reset_and_is_hidden_for_non_admin` e `test_admin_view_mode_changes_navigation_without_changing_session`, em [test_navigation.py](../tests/test_navigation.py#L239), passam na suíte final. Isso demonstra o estado e a estrutura em testes, não a interação real de teclado/Esc/foco nem a aparência visual, que não foram vistas no navegador.

### Commits dos cinco blocos visuais

| Bloco | Commit | Teste(s) que dão evidência |
|---|---|---|
| 1 — tokens/tema | `322102e03038dfa0ffd856858a230666bd9f32c0` | `test_visual_tokens_keep_accessible_contrast_and_reduced_motion` |
| 2 — cabeçalho/rodapé | `3b09ff6e7d64de63c697be717e00fbc4e4d5273f` | `test_site_header_brand_and_footer_links_preserve_profile_access` |
| 3 — início | `67b041a58d8a1c353b1c4d42cbe2ece250c6961b` | `test_home_sections_use_catalog_data_and_explicit_empty_error_states` |
| 4 — cartões/catálogo | `1a98366f621c252b2779a5a784dcb5dc8698ace6` | `test_catalog_card_derives_cover_fallback_from_category_and_title`; `test_catalog_controls_and_card_states_are_responsive` |
| 5 — formulários/estados/alvos | `c17da0530aeeeee2f8f4e838607279c4be8672f5` | `test_forms_and_admin_panels_use_shared_visual_states`; `test_touch_targets_and_keyboard_accessibility_at_mobile_viewport` |

### OpenSpec — estado final desta retomada

`openspec.cmd validate --specs --strict`: 7 passaram, 0 falharam. `openspec.cmd validate refino-visual-biblioteca --strict`: Change válida. A Change continua ativa, com 1/13 tarefas concluída; não foi arquivada porque a inspeção visual/DOM permanece bloqueada. A tentativa mais recente do navegador retornou “Connection Error:”.

Saída final de `openspec.cmd list --json`:

```json
{
  "changes": [
    {
      "name": "refino-visual-biblioteca",
      "completedTasks": 1,
      "totalTasks": 13,
      "lastModified": "2026-11-18T19:29:45.836Z",
      "status": "in-progress"
    },
    {
      "name": "validacao-remota-xano",
      "completedTasks": 0,
      "totalTasks": 22,
      "lastModified": "2026-11-17T05:16:18.677Z",
      "status": "in-progress"
    },
    {
      "name": "execucao-reflex-windows",
      "completedTasks": 6,
      "totalTasks": 7,
      "lastModified": "2026-11-15T17:36:02.160Z",
      "status": "in-progress"
    }
  ],
  "root": {
    "path": "C:\\Users\\User\\Biblioteca\\Biblioteca\\Biblioteca",
    "source": "nearest"
  }
}
```

## Continuação — Change simplifica-navegacao, 2026-11-19

### Evidências dos itens concluídos nesta rodada

| Item | Commit | Testes novos/alterados ou regressões | Status |
|---|---|---|---|
| Área pessoal `/reservas` e redirecionamento de `/minha-biblioteca` | `e370506` | `test_student_reservations_has_four_sections_and_empty_states`; `test_my_library_redirects_to_reservations_without_personal_gets`; `test_student_reservation_groups_order_overdue_and_show_neutral_missing_data`; `test_student_library_page_and_navigation_are_profile_gated` | Feito, aguarda conferência visual do usuário |
| Abas de pedidos/circulação e busca de contas | `6abd99b`, `64f44a7` | `test_staff_reservations_tabs_reuse_current_operations`; `test_admin_accounts_search_and_supported_actions`; `test_staff_operational_counts_use_loaded_records` (inclui devoluções previstas para hoje); atualizado `test_circulation_page_has_accessible_actions_and_focus_style` | Feito, aguarda conferência visual do usuário |
| Pendências do contrato Xano | `ca1cf27` | Nenhum teste foi criado ou alterado; regressões incluídas na suíte: `test_cover_url_is_optional_and_validated_as_https`, `test_title_payload_omits_empty_optional_cover`, `test_student_reservation_groups_order_overdue_and_show_neutral_missing_data` | Pendente de validação Xano; nenhuma operação remota executada |

### Verificações locais

- `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado após as alterações.
- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 243 passaram. Uma execução concorrente com a compilação falhou durante coleta por corrida nos arquivos temporários do Reflex; a repetição isolada passou.
- `openspec.cmd validate --specs --strict`: 7 specs aprovadas, 0 falhas.
- `openspec.cmd validate simplifica-navegacao --strict`: Change válida.
- Navegador e capturas não foram usados, conforme solicitado. A aparência das telas desta rodada não foi vista; itens visuais ficam “feito, aguarda conferência do usuário”.

### Pendências sem escrita no Xano

O backlog em `openspec/changes/validacao-remota-xano/tasks.md` agora mantém abertas as validações de `capa_url` e `descricao` em `titulo`, título/`titulo_id` nos empréstimos pessoais, `solicitada_em` quando exigida, contagem de empréstimos por título e endpoint para mudança genérica de perfil. Não houve consulta nem escrita no Xano real.

### Archive e validação final

`simplifica-navegacao` foi arquivada em `openspec/changes/archive/2026-11-19-simplifica-navegacao/`, com 10/10 tarefas concluídas. Deltas sincronizados em `catalog`, `frontend-foundation`, `loan-circulation`, `primary-journeys` e `reservations`. `openspec.cmd validate --specs --strict` após o archive: 7 aprovadas, 0 falhas. As pendências de contrato Xano seguem abertas em `validacao-remota-xano`.

### Saída final de `openspec.cmd list --json`

```json
{
  "changes": [
    {
      "name": "validacao-remota-xano",
      "completedTasks": 0,
      "totalTasks": 28,
      "lastModified": "2026-11-19T04:39:37.673Z",
      "status": "in-progress"
    },
    {
      "name": "refino-visual-biblioteca",
      "completedTasks": 1,
      "totalTasks": 13,
      "lastModified": "2026-11-18T19:29:45.836Z",
      "status": "in-progress"
    },
    {
      "name": "execucao-reflex-windows",
      "completedTasks": 6,
      "totalTasks": 7,
      "lastModified": "2026-11-15T17:36:02.160Z",
      "status": "in-progress"
    }
  ],
  "root": {
    "path": "C:\\Users\\User\\Biblioteca\\Biblioteca\\Biblioteca",
    "source": "nearest"
  }
}
```

## Continuação — Change ajustes-visuais-v2

### Evidências dos itens concluídos nesta retomada

| Item | Commit | Testes novos/alterados ou regressões | Status |
|---|---|---|---|
| 6 — Jornadas de bibliotecário e admin | `e254525` | Novos: `test_staff_admin_workflows_have_visible_feedback_and_empty_states`, `test_destructive_operations_are_visually_distinct`, `test_operational_lists_keep_horizontal_scroll_inside_container`. Regressões: `test_staff_reservations_tabs_reuse_current_operations`, `test_admin_accounts_search_and_supported_actions`, `test_header_navigation_by_profile_and_view`. Suíte: 256 passaram. | Feito, aguarda conferência do usuário |
| 7 — Sincronização e arquivamento | `e16ec8e` | Sem testes de código novos/alterados; regressões: `test_staff_admin_workflows_have_visible_feedback_and_empty_states`, `test_destructive_operations_are_visually_distinct`, `test_operational_lists_keep_horizontal_scroll_inside_container` (256 passaram). Validações estritas da Change e das specs aprovadas. | Arquivada em `2026-11-22-ajustes-visuais-v2`; Xano não tocado |

### Achados e dependências Xano

- Feedback de carregamento, vazio, sucesso e erro já estava presente nas páginas auditadas. As abas de reservas/circulação, a busca de contas e o seletor de visão mantêm as operações existentes; os testes de regressão indicados acima cobrem esses fluxos.
- As ações de desativar título, desativar bibliotecário e recusar solicitação/reserva usavam o estilo visual de saída da sessão. O commit `e254525` as diferencia com o estilo de ação destrutiva.
- As listas `.admin-catalog-grid` e `.librarian-list` não limitavam explicitamente largura nem continham a rolagem horizontal. O mesmo commit limita a largura e mantém a rolagem dentro dos contêineres.
- Dependências observadas no cliente local: acervo administrativo em `GET /admin/acervo` e atualização de título em `PATCH /catalogo/titulos/{id}`; contas bibliotecárias em `GET/PATCH /admin/usuarios`; circulação lê `GET /admin/solicitacoes`, `/admin/reservas` e `/admin/emprestimos`, e usa as operações administrativas existentes de retirada/recusa/oferta/devolução. Essas rotas são contratos codificados no cliente, não confirmação de disponibilidade ou compatibilidade no Xano real.
- Nenhum endpoint, payload ou regra de domínio foi alterado. Não houve acesso ou escrita no Xano; a confirmação remota dos contratos permanece fora desta Change. Não foram usadas capturas nem navegador; a revisão visual aguarda conferência do usuário.

### Verificações locais

- Após o commit `e254525`, `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado.
- Após o commit `e254525`, `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 256 passaram.
- Após o commit `e16ec8e`, `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado; a suíte foi repetida isoladamente após uma corrida de coleta observada ao executá-la em paralelo com o compile, com 256 testes aprovados.
- As validações globais também encontraram pendências preexistentes fora desta Change: `openspec.cmd validate --archived --strict` marcou somente `2026-11-17-devolvido-em-nulavel` (20 tarefas ainda abertas; a Change desta execução passou); `openspec.cmd validate --changes --strict` apontou `refino-visual-biblioteca` por cenários omitidos no delta e uma informação de requisito já existente em `execucao-reflex-windows`. Essas Changes não foram alteradas.

## Continuação — Change ajustes-interface-acervo-v4

### Evidências

| Item | Commit | Testes novos/alterados | Status |
|---|---|---|---|
| 1.1 — Campos HTML nativos e IDs ocultos | `90aa22114381e792e68cd413c7a176bf37bde3aa` | `test_form_routes_use_native_fields_and_hidden_ids_are_invisible`, `test_native_fields_have_single_border_and_visible_focus`, `test_catalog_form_has_only_defined_fields_and_category_selection`, `test_login_page_has_only_labeled_email_and_password_fields`, `test_signup_route_has_labeled_fields_in_keyboard_order_and_visible_focus`, `test_librarian_management_page_has_labeled_fields_and_responsive_styles`; suíte completa: 277 passaram | Feito, aguarda conferência do usuário |
| 1.2 — Contraste de botões e capas | `f093328fe8500907e2647ee471c54e9774799c95` (implementação), `1319d1e74843275f505b6fd5ccdffd97f26de19d` (teste de regressão) | `test_button_variants_meet_wcag_aa_in_both_themes`, `test_seed_cover_title_bands_meet_wcag_aa`, `test_destructive_operations_are_visually_distinct`; compilação Reflex aprovada; suíte completa: 278 passaram | Feito, aguarda conferência do usuário |
| 2.1 — Menus independentes de Perfil e Acessibilidade | `703331d3bd039b50162156537525a7bf72d50062` (implementação), `30599ea0878a27af726a391b1022c1fd6c2dbf91` (testes de regressão) | `test_visitor_accessibility_menu_exposes_shared_appearance_controls`, `test_profile_menu_never_contains_accessibility_controls`, `test_header_separates_profile_and_accessibility_on_mobile`, `test_profile_disclosure_uses_details_without_rx_menu`, `test_profile_disclosure_escape_and_outside_click_script`, `test_profile_disclosure_for_visitor_and_authenticated_users`, `test_admin_view_mode_controls_are_visible_and_accessible`, `test_student_navigation_has_accessible_labels_focus_and_mobile_layout`, `test_site_header_brand_and_footer_links_preserve_profile_access`, `test_header_has_catalog_and_profile_on_every_route`, `test_header_navigation_by_profile_and_view`, `test_dark_mode_toggles_scoped_theme_tokens`, `test_decorative_emojis_are_aria_hidden`, `test_theme_switch_reports_effective_destination`, `test_motion_rules_have_reduced_motion_override`, `test_touch_targets_and_keyboard_accessibility_at_mobile_viewport`, `test_shared_navigation_is_conditioned_on_private_session_profile`; compilação Reflex aprovada; suíte completa: 280 passaram | Feito, aguarda conferência do usuário |
| 2.2 — Dicionário de ícones e confirmação destrutiva | `cf4a4363d43cb3726663fafb72ddd1605c52c26f` | `tests/test_icons.py`: `test_action_emojis_are_unique_and_have_visual_categories`, `test_action_helpers_include_accessible_icon_and_button_metadata`, `test_theme_action_marks_its_dynamic_emoji_and_label`, `test_status_seals_render_an_aria_hidden_emoji`, `test_every_button_and_link_uses_the_shared_action_helpers`, `test_title_deactivation_keeps_inline_confirmation_actions`, `test_librarian_deactivation_requires_inline_confirmation`; testes atualizados: `test_title_detail_actions_follow_effective_role`, `test_circulation_page_has_accessible_actions_and_focus_style`, `test_staff_reservations_tabs_reuse_current_operations`, `test_login_page_has_only_labeled_email_and_password_fields`, `test_home_keeps_featured_and_about_without_hero_shortcuts`, `test_login_page_contains_only_login_form`, `test_signup_page_contains_only_signup_form`, `test_student_navigation_has_accessible_labels_focus_and_mobile_layout`, `test_page_bodies_do_not_duplicate_global_navigation`, `test_visitor_accessibility_menu_exposes_shared_appearance_controls`, `test_profile_menu_never_contains_accessibility_controls`, `test_profile_disclosure_for_visitor_and_authenticated_users`, `test_accessibility_page_reuses_existing_controls`, `test_header_navigation_by_profile_and_view`, `test_destructive_operations_are_visually_distinct`, `test_decorative_emojis_are_aria_hidden`, `test_home_sections_use_catalog_data_and_explicit_empty_error_states`, `test_signup_route_has_labeled_fields_in_keyboard_order_and_visible_focus`, `test_reservation_page_exposes_accessible_controls_and_visible_focus`, `test_student_library_401_clears_session_and_offers_login`; compilação Reflex aprovada; suíte completa: 287 passaram | Feito, aguarda conferência do usuário |
| 3.1 — Acervo em lista vertical | `e242de459f5a5ee68357aeb7f3266e0ab178862b` | `test_acervo_search_normalizes_text_and_empty_state`, `test_acervo_has_one_edit_panel`, `test_acervo_hides_inactive_by_default_and_keeps_one_panel_open`, `test_acervo_vertical_layout_is_responsive_and_covers_are_fixed`, `test_acervo_paginates_in_groups_of_ten`, `test_public_catalog_never_returns_inactive_titles`, `test_catalog_cover_grid_has_bounded_card_size`; compilação Reflex aprovada; suíte completa: 289 passaram | Feito, aguarda conferência do usuário |
| 3.2 — Confirmação da desativação pelo servidor | `655ae877029ff4ce118cb941b6d761f089badf7e` | `test_title_deactivation_reports_http_and_connection_errors`, `test_title_deactivation_detects_apparent_success`, `test_title_deactivation_reports_refresh_connection_failure`, além de `test_admin_catalog_edits_titles_and_adds_copies_without_repeating_writes`; compilação Reflex aprovada; suíte completa: 294 passaram | Feito, aguarda conferência do usuário |
| 4.1 — Mensagens de falha ao reservar | `60bf09a200650ac9cfdee163d3a8063994f7e1d2` | `test_reservation_request_error_codes`, `test_student_request_does_not_retry_uncertain_result`, `test_student_request_shows_allowlisted_business_error`, `test_student_request_http_error_matrix_is_safe_and_not_retried`, `test_student_request_uncertain_result_is_not_reported_or_retried`; compilação Reflex aprovada; suíte completa: 300 passaram | Feito, aguarda conferência do usuário |
| 4.2 — Auditoria do seed seguro | `abf0a3ef0b5cfbf616e9c6d32912a2e43d124160` | `test_dry_run_makes_no_write`, `test_apply_without_credentials_aborts`, `test_seed_mapping_categories_and_idempotency`, `test_seed_never_prints_password`, `test_seed_identifies_existing_test_titles_for_deactivation`; execução local sem `--apply` mostrou `alvo: demonstração local`; compilação Reflex aprovada; suíte completa: 301 passaram | Feito, aguarda conferência do usuário |

### Verificações locais

- Após `90aa22114381e792e68cd413c7a176bf37bde3aa`, `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado.
- Após `90aa22114381e792e68cd413c7a176bf37bde3aa`, `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation`: 277 passaram.
- A aplicação usa controles HTML nativos nos formulários; nenhum acesso ao Xano foi realizado nesta tarefa.
- Após `cf4a4363d43cb3726663fafb72ddd1605c52c26f`, `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado.
- Após `cf4a4363d43cb3726663fafb72ddd1605c52c26f`, `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 287 passaram.
- A conferência visual continua pendente com o usuário; não foram usados navegador nem capturas de tela.
- ## Continuação — Change layout-estavel-v5
- | 1.1 — Barra superior estável | `03a15e33b0517876090cb6a2120b2ad26d61c86c` | `test_header_contract_is_stable_without_action_classes`, `test_header_nav_and_footer_tokens_meet_text_contrast`, testes atualizados em `test_navigation.py` e testes dos breakpoints para 48 rem; compilação Reflex aprovada; suíte completa: 303 passaram | Feito, aguarda conferência do usuário |
- | 2.1 — Contêineres estáveis | `71cb4eab39f6b0f7da4925649984ab16955da168` | `test_page_container_layout_is_stable`, testes de grades e listas atualizados em `test_layout_v5.py`, `test_catalog.py`, `test_frontend_foundation.py` e `test_user_admin.py`; compilação Reflex aprovada; suíte completa: 304 passaram | Feito, aguarda conferência do usuário |
- | 3.1 — Jornadas app de delivery | `dfb71ad2e78b965898ebc359da99efc5c2d9c405` | `test_delivery_layout_has_category_rails_and_product_detail`, testes de reservas por abas em `test_student_area.py` e atualizações de jornada em `test_primary_journeys.py`; compilação Reflex aprovada; suíte completa: 305 passaram | Feito, aguarda conferência do usuário |
- | 4.1 — Login e cadastro só para acesso | `b1e7d71803718abc7ff3201870133f2da8e50c65` | `test_login_page_contains_only_login_form`, `test_signup_route_has_labeled_fields_in_keyboard_order_and_visible_focus`, `test_login_payload_normalizes_email_and_preserves_password`; compilação Reflex aprovada; suíte completa: 305 passaram | Feito, aguarda conferência do usuário |
- | 5.1 — Emojis semânticos | `ae5f040` | `test_icon_guide_restricts_decorative_emojis_to_semantic_places`, `test_action_emojis_are_unique_and_have_visual_categories`; compilação Reflex aprovada; suíte completa: 306 passaram | Feito, aguarda conferência do usuário |
- | 6.1 — Capas reais por ISBN | `2e67528` | `test_isbn_cover_priority_and_normalization`, `test_local_isbn_index_falls_back_by_normalized_title_and_author`; compilação Reflex aprovada; suíte completa: 308 passaram | Feito, aguarda conferência do usuário |
- | 7.1 — Seed de 30 livros reais | `f36d67d` | `test_real_seed_has_unique_titles_valid_isbns_and_approved_categories`, `test_seed_catalogo`, dry-run sem `--apply`; compilação Reflex aprovada; suíte completa: 309 passaram | Feito, aguarda conferência do usuário |
- | 8.1 — Diagnóstico da desativação | `3fef4bb` | `test_deactivation_diagnostic_is_opt_in_and_never_prints_secrets`; compilação Reflex aprovada; suíte completa: 310 passaram | Feito, aguarda conferência do usuário |
- Após `e242de459f5a5ee68357aeb7f3266e0ab178862b`, `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado.
- Após `e242de459f5a5ee68357aeb7f3266e0ab178862b`, `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 289 passaram.
- Após `655ae877029ff4ce118cb941b6d761f089badf7e`, `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado.
- Após `655ae877029ff4ce118cb941b6d761f089badf7e`, `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 294 passaram.
- Destino Xano confirmado pelo CLI: workspace `151966`, branch live `v1`, `allow_push=false`; pull de 67 definições realizado somente para pasta temporária fora do repositório. A definição local de `titulos_id_PATCH.xs` coincide com a remota no contrato e nas regras de perfil, ativo, empréstimos e reservas; somente diferenças de formatação foram observadas. Nenhuma publicação ou alteração remota foi feita.
- Após `60bf09a200650ac9cfdee163d3a8063994f7e1d2`, `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado.
- Após `60bf09a200650ac9cfdee163d3a8063994f7e1d2`, `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 300 passaram.
- Comparação local/remota do endpoint público de reservas confirmou que o perfil exigido é estudante; não houve alteração remota ou publicação.
- Após `abf0a3ef0b5cfbf616e9c6d32912a2e43d124160`, `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado.
- Após `abf0a3ef0b5cfbf616e9c6d32912a2e43d124160`, `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 301 passaram.
- O seed foi executado somente em dry-run; nenhuma senha foi usada ou impresa e não houve `--apply`.

## Continuação — Change layout-livraria-v6, validação final (2026-11-23)

### Verificações locais

- `.\.venv\Scripts\python.exe -m reflex compile --dry`: aprovado.
- Em seguida, `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation`:
  314 aprovados em 276,39 s.
- `node --check scripts/verificar_layout.mjs` e `git diff --check`: aprovados.
- `scripts/verificar.ps1` foi bloqueado pela política de execução antes de
  iniciar; a política não foi contornada. Os dois comandos foram executados
  manualmente, em sequência.
- Nenhuma escrita no Xano foi realizada.

### Última matriz visual — rodada 4/4

A rodada começou em `2026-11-23T09:05:48.605Z`, registrou 28 combinações e
durou 992 s. Resultado: 11 `PASSOU`, 17 `FALHOU`; a matriz não terminou sem
violações. As capturas PNG estão em `docs/capturas/verificacao/` e o registro
incremental completo está em `docs/verificacao-layout.md`.

| Rota | Perfil | Largura | Tema | Resultado | Achados |
|---|---|---:|---|---|---|
| `/` | visitante | 360 | claro | FALHOU | hidratação |
| `/` | visitante | 360 | escuro | PASSOU | nenhum |
| `/` | visitante | 1366 | claro | FALHOU | hidratação |
| `/` | visitante | 1366 | escuro | PASSOU | nenhum |
| `/catalogo` | visitante | 360 | claro | PASSOU | nenhum |
| `/catalogo` | visitante | 360 | escuro | PASSOU | nenhum |
| `/catalogo` | visitante | 1366 | claro | PASSOU | nenhum |
| `/catalogo` | visitante | 1366 | escuro | PASSOU | nenhum |
| `/catalogo/1` | visitante | 360 | claro | FALHOU | conexão/renderização; `svg` fora do contêiner; botão abaixo de 44 px; contraste insuficiente |
| `/catalogo/1` | visitante | 360 | escuro | FALHOU | conexão/renderização; `svg` fora do contêiner; botão abaixo de 44 px |
| `/catalogo/1` | visitante | 1366 | claro | FALHOU | conexão/renderização; `svg` fora do contêiner; botão abaixo de 44 px; contraste insuficiente |
| `/catalogo/1` | visitante | 1366 | escuro | FALHOU | conexão/renderização; `svg` fora do contêiner; botão abaixo de 44 px |
| `/login` | visitante | 360 | claro | FALHOU | conexão/renderização; `svg` fora do contêiner; botão abaixo de 44 px; contraste insuficiente |
| `/login` | visitante | 360 | escuro | FALHOU | conexão/renderização; `svg` fora do contêiner; botão abaixo de 44 px |
| `/login` | visitante | 1366 | claro | FALHOU | hidratação |
| `/login` | visitante | 1366 | escuro | PASSOU | nenhum |
| `/cadastro` | visitante | 360 | claro | PASSOU | nenhum |
| `/cadastro` | visitante | 360 | escuro | PASSOU | nenhum |
| `/cadastro` | visitante | 1366 | claro | PASSOU | nenhum |
| `/cadastro` | visitante | 1366 | escuro | PASSOU | nenhum |
| `/reservas` | estudante | 1366 | escuro | FALHOU | conta de demonstração indisponível |
| `/reservas` | estudante | 360 | escuro | FALHOU | conta de demonstração indisponível |
| `/admin/acervo` | bibliotecário | 1366 | escuro | FALHOU | conta de demonstração indisponível |
| `/admin/acervo` | bibliotecário | 360 | escuro | FALHOU | conta de demonstração indisponível |
| `/admin/reservas` | bibliotecário | 1366 | escuro | FALHOU | conta de demonstração indisponível |
| `/admin/reservas` | bibliotecário | 360 | escuro | FALHOU | conta de demonstração indisponível |
| `/admin/bibliotecarios` | admin | 1366 | escuro | FALHOU | conta de demonstração indisponível |
| `/admin/bibliotecarios` | admin | 360 | escuro | FALHOU | conta de demonstração indisponível |

Embora o robô tenha registrado `PASSOU` nas duas larguras da home escura e
nas quatro combinações do catálogo, as capturas ainda mostram conteúdo
`Carregando`. Esses seis resultados não confirmam o conteúdo visual carregado.
O critério foi ajustado para detectar o placeholder; não houve quinta rodada.

### Pendências e decisão de fechamento

- A tentativa anterior do navegador integrado também encontrou erro de
  conexão; portanto, a interface continua não verificada visualmente nas
  combinações que falharam.
- A limpeza do Edge falhou na rodada por timeout da consulta WMI. O perfil
  temporário exclusivo foi removido após o processo terminar. O robô foi
  revisado após `71cb6dc` para encerrar o processo próprio pelo PID e detectar
  estados `Carregando`, mas essas revisões não foram executadas por uma quinta
  rodada.
- Naquele momento, a validação estrita das specs e o push ainda precisavam ser
  concluídos. A recomendação de manter `layout-livraria-v6` aberta foi
  posteriormente substituída pela instrução de arquivá-la como superada por
  `restaura-visual-v7`, mesmo com a matriz incompleta.

## Restauração visual v7 — verificação final

### Verificações locais

- `scripts/verificar.ps1` foi bloqueado pela política de execução do PowerShell;
  não houve tentativa de contornar a política. Os passos equivalentes foram
  executados em sequência: `.\.venv\Scripts\python.exe -m reflex compile --dry`
  passou e `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation` passou
  com 322 testes.
- A API demo respondeu HTTP 200 e as rotas `/`, `/catalogo` e `/login`
  responderam HTTP 200 ao aquecimento com `Invoke-WebRequest -TimeoutSec 300`.
- A porta 8000 estava ocupada por processo não identificável e não foi
  encerrada. O Reflex foi iniciado na porta 8001; frontend em 3000. Os serviços
  iniciados para a verificação foram encerrados ao final. Nenhuma escrita no
  Xano foi realizada.
- O robô foi executado uma única vez, somente para visitante, em 12 combinações
  das três rotas, duas larguras e dois temas. Início registrado em
  `2026-11-23T21:17:58.468Z`; duração 287 s; limite 900 s.

### Última matriz visual

| Rota | Perfil | Largura | Tema | Resultado | Achados | Captura |
|---|---|---:|---|---|---|---|
| `/` | visitante | 360 | claro | PASSOU | nenhum | [PNG](./capturas/verificacao/home-visitante-360-claro.png) |
| `/` | visitante | 360 | escuro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-360-escuro.png) |
| `/` | visitante | 1366 | claro | PASSOU | nenhum | [PNG](./capturas/verificacao/home-visitante-1366-claro.png) |
| `/` | visitante | 1366 | escuro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-1366-escuro.png) |
| `/catalogo` | visitante | 360 | claro | PASSOU | nenhum | [PNG](./capturas/verificacao/catalogo-visitante-360-claro.png) |
| `/catalogo` | visitante | 360 | escuro | PASSOU | nenhum | [PNG](./capturas/verificacao/catalogo-visitante-360-escuro.png) |
| `/catalogo` | visitante | 1366 | claro | PASSOU | nenhum | [PNG](./capturas/verificacao/catalogo-visitante-1366-claro.png) |
| `/catalogo` | visitante | 1366 | escuro | PASSOU | nenhum | [PNG](./capturas/verificacao/catalogo-visitante-1366-escuro.png) |
| `/login` | visitante | 360 | claro | PASSOU | nenhum | [PNG](./capturas/verificacao/login-visitante-360-claro.png) |
| `/login` | visitante | 360 | escuro | PASSOU | nenhum | [PNG](./capturas/verificacao/login-visitante-360-escuro.png) |
| `/login` | visitante | 1366 | claro | PASSOU | nenhum | [PNG](./capturas/verificacao/login-visitante-1366-claro.png) |
| `/login` | visitante | 1366 | escuro | PASSOU | nenhum | [PNG](./capturas/verificacao/login-visitante-1366-escuro.png) |

### O que não foi verificado

- A home no tema escuro não hidratou em nenhuma largura; as capturas mostram
  conteúdo ainda carregando em 360 px e uma página sem conteúdo visível em
  1366 px. Esses estados não foram tratados como aprovação visual. A saída do
  robô também informou falha ao observar o encerramento do Edge pelo processo
  iniciado; uma consulta posterior não encontrou Edge associado ao perfil
  temporário `biblioteca-layout-`.
- A rodada não cobriu rotas de detalhe, cadastro, reservas ou administração,
  contas autenticadas, menus abertos nem interações. Não houve uma segunda
  rodada nem verificação visual dessas áreas.
- A aparência implementada aguarda conferência do usuário; os dois resultados
  da home escura permanecem falhos e devem ser tratados antes de afirmar
  hidratação visual completa.

### Fechamento OpenSpec

- Os deltas de `frontend-foundation` e `catalog` foram mesclados nas specs
  principais; `openspec.cmd validate --specs --strict` aprovou as 9 specs.
  `openspec.cmd validate "restaura-visual-v7" --strict` também passou antes
  do arquivo.
- `layout-livraria-v6` foi arquivada sem sincronizar specs em
  `openspec/changes/archive/2026-11-23-layout-livraria-v6/`, com a nota de
  substituição por `restaura-visual-v7`; ela estava incompleta (20/32 tarefas).
- `restaura-visual-v7` foi arquivada em
  `openspec/changes/archive/2026-11-23-restaura-visual-v7/` após 5/5 tarefas.
  Os deltas já estavam sincronizados, portanto o arquivo não alterou specs.
- Commits das evidências finais: `a9075dd` (relatório, matriz, capturas e
  sync) e `baef058` (hash e evidências da tarefa 5.1).

## Continuação — Change regras-e-visao-admin-v10 (2026-11-26)

### Implementação e evidências

| Tarefa | Alteração | Evidência local |
|---|---|---|
| 1.1 | Visão efetiva do admin, guards, menu e identidade real | 191 testes; `247387c` |
| 2.1 | Regras e validações da API de demonstração | 25 testes; `e4bd46f` |
| 2.2 | Cliente Xano, cache de 60 s e invalidação | 50 testes; `2a04cc7` |
| 3.1 | Página `/regras`, validação, descarte e leitura somente para consulta | 65 testes; `6b652bf` |
| 3.2 | Limite de pedidos no detalhe do livro | 48 testes; `0a6e701` |
| 4.1 | Ações simuladas, mensagens de regra e releitura após estado obsoleto | 149 testes; `0a8d1ae` |
| 5.1 | Contraste do cabeçalho, sem alterar geometria | 2 testes de estilo/contraste; `bd2a115` |
| Correção integrada | Ações de fechar aviso e botões de regras usam helpers comuns; os rótulos existentes foram preservados | `tests/test_icons.py tests/test_library_rules_state.py`: 15 testes; `c24a219` |

A inspeção da árvore Reflex confirmou o `summary` nativo de Acessibilidade e
seus spans de emoji/rótulo. A regra vencedora anterior usava
`--button-subtle-text`, diferente de Perfil (`--brand-text`). Os spans herdavam
a cor; as regras Radix `.rt-Button`, `.subtle-action` e `.a11y-controls button`
não selecionam esse `summary`. A stylesheet global não contém seletores do
cabeçalho; os estilos do app terminam com os overrides específicos verificados
pelos testes. A verificação visual no navegador não foi realizada; o controle
aguarda conferência do usuário.

### Verificação final local

- `.\.venv\Scripts\python.exe -m reflex compile --dry`: sucesso após a última
  alteração de código.
- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 472 passaram.
  Uma execução anterior sofreu uma falha de transporte local (`WinError 10053`);
  o teste isolado passou e a repetição completa terminou sem falhas.
- Nenhuma chamada ou escrita foi realizada no Xano. A publicação das regras e
  permissões continua manual, conforme [publicacao-xano-regras.md](./publicacao-xano-regras.md).

## Continuação — velocidade-e-readme-v11 (2026-11-27)

### Implementação e evidências

- README conciso: commit `7314ab7`.
- Parser de regras com os metadados reais informados e cache público em arquivo
  temporário: commits `93b586b`, `98cb56d`, `1454e01`, `fcfca63` e `248db27`.
- Cache HTTP autenticado e fila sequencial de escritas: commits `dd640e3`,
  `103e948` e `24b626a`.
- Cópias autenticadas de até 20 s agora aparecem imediatamente nas telas
  pessoais, circulação e acervo, com atualização em segundo plano; 132 testes
  focados passaram, commit `b4bec42`.
- Latência configurável da API demo e medição local simulada: commit `4e0fcff`.
  A 1000 ms, a home mostrou livros em 1451,3 ms sem cópia e em 3,5 ms com cópia;
  a atualização em segundo plano levou 1264,4 ms. Foram 3 chamadas por abertura.
  Essa medição foi local, não contra o Xano real.
- O mock do smoke test passou a fornecer um token distinto para cada perfil,
  evitando que o cache correto de mesmo token reutilizasse respostas entre
  logins simulados: commit `d8f4bf3`.

### Verificação final local

- `.\.venv\Scripts\python.exe -m reflex compile --dry`: sucesso.
- `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`: 501 passaram.
- `.\.venv\Scripts\python.exe -m unittest discover -s xano\tests`: 17 passaram.
- `openspec.cmd validate --specs --strict`: 11 specs passaram; a v11 passou na
  validação estrita.
- `validacao-remota-xano` foi arquivada como
  `openspec/changes/archive/2026-11-27-validacao-remota-xano/`, sem sync porque
  é somente operacional. `execucao-reflex-windows` já está em `archive/`.
- `velocidade-e-readme-v11` foi arquivada em
  `openspec/changes/archive/2026-11-27-velocidade-e-readme-v11/`; após a
  evidência final de 7.1, ficou com 8/9 tarefas concluídas. A releitura
  agrupada de 1,5 s permanece explicitamente pendente, sem ser tratada como
  concluída. Commit e push sem force: `580e7bc`.
- Não houve chamada, pull, escrita ou publicação no Xano nesta continuação.

### Pendências e conferências

- A releitura agrupada/debounce em 1,5 s após escritas da tarefa 4.1 permanece
  incompleta; não foi marcada como concluída. A sequência atual ainda não prova
  que várias escritas concorrentes gerem uma única releitura.
- A aparência visual continua aguardando conferência do usuário; os achados de
  hidratação escura da home registrados acima permanecem sem nova inspeção.

### O que o usuário precisa conferir ou fazer

1. Publicar manualmente as mudanças de regras e permissões no workspace correto
   do Xano, conforme [publicacao-xano-regras.md](./publicacao-xano-regras.md), e
   validar os endpoints no painel antes de testar as ações no site.
2. Conferir visualmente a home no tema escuro e o cabeçalho de Acessibilidade.
3. Decidir se a releitura agrupada de 1,5 s ainda deve ser concluída em uma
   Change posterior.

## Inventário de branches antes da limpeza (2026-11-27)

- `main` — `8d901eb`
- `trabalho-autopilot` — `888f94b`
- `trabalho-autopilot-layout-livraria-v6` — `accd3ef`
- `origin/feat/frontend-cadastros` — `7b88761`
- `origin/main` — `8d901eb`
- `origin/trabalho-autopilot` — `888f94b`
- `origin/trabalho-autopilot-layout-livraria-v6` — `accd3ef`
- `origin/trabalho-noturno` — `798e9b0`

Branches removidas: remotas `feat/frontend-cadastros`, `trabalho-autopilot`, `trabalho-autopilot-layout-livraria-v6`, `trabalho-noturno`; local `trabalho-autopilot-layout-livraria-v6`.
Backup verificado: `C:\Users\User\Desktop\biblioteca-backup-antes-da-limpeza.bundle`.
Branches restantes: `main` é a única branch local e remota; `origin/HEAD` aponta para `origin/main`.
