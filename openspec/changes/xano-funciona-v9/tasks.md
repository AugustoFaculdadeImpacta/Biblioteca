# Tasks

## 1. Leitura tolerante

- [x] 1.1 Implementar extração dos envelopes, conversões escalares e validação por registro nos leitores autenticados de empréstimos, pedidos, reservas, equipe, bibliotecários, acervo e categorias; cobrir lista simples/embrulhada, ms/s, nulos, campos extras, registro ilegível e topo inválido com fixtures simuladas.
  - Evidência: commit `48bef7e`; `pytest tests\test_student_area.py tests\test_circulation.py tests\test_catalog.py tests\test_admin_catalog.py tests\test_user_admin.py tests\test_staff_reservations.py -q` — 160 passed; `reflex compile --dry` concluído com sucesso.

## 2. Escritas sem repetição

- [x] 2.1 Tratar respostas POST/PATCH 2xx ilegíveis sem repetir a escrita, atualizar as listas e só confirmar a reserva após encontrar o registro; para visibilidade atrasada, fazer até duas releituras GET limitadas e manter o bloqueio se não houver confirmação. Testar sucesso imediato/atrasado, ausência de confirmação, erro, transporte e ausência de retry do POST.
  - Evidência: `pytest tests\test_student_area.py tests\test_primary_journeys.py -q` — 70 passed; `pytest --ignore=evaluation -q` — 377 passed; `reflex compile --dry` — sucesso. Cobertos registro visível na segunda leitura e bloqueio após duas releituras sem confirmação.
- [x] 2.2 Bloquear nova submissão em Reservar durante a tentativa e até a confirmação pela releitura; manter o bloqueio quando a escrita for incerta e testar liberação somente após confirmação.
  - Evidência: commit `26e7601`; testes de confirmação e bloqueio incluídos na suíte focada — 231 passed; `reflex compile --dry` — sucesso.

## 3. Resumo da home

- [x] 3.1 Tornar independentes o carregamento, erro, valor “—” e retry de cada indicador; testar falha isolada e preservação dos demais resultados.
  - Evidência: commit `dcc06a6`; `pytest tests\test_primary_journeys.py -q` — `17 passed` (inclui início concorrente e retry independente); `pytest tests\test_xano_client.py -q` — `32 passed` (detalhe interno não exposto).

## 4. Diagnóstico pelo Perfil

- [x] 4.1 Adicionar diagnóstico somente leitura para usuários autenticados, com chamadas autorizadas pelo perfil, validação estrutural e relatório copiável sem valores sensíveis; documentar em `docs/diagnostico-xano.md` e testar 200 válido/inválido, 403, 404, 429, não JSON e sanitização.
  - Evidência: commit `5d27808`; `pytest --ignore=evaluation -q` — `404 passed`, incluindo validação por perfil, 200 válido/inválido, 403/404/429, não JSON e sanitização; `.\.venv\Scripts\python.exe -m reflex compile --dry` — sucesso.

## 5. Comparação de contratos Xano

- [x] 5.1 Confirmar pelo Xano CLI workspace `151966`, branch `v1` marcada como live e ambiente selecionado; registrar identificação e evidência sem segredos na Change. Comparar host/grupo do `.env` com `docs/xano-workflow.md` sem expor a URL. Interromper se qualquer elemento não corresponder.
  - Evidência (2026-11-24): Xano CLI 1.3.4 confirmou workspace `151966` (“Augusto's Workspace”); `branch list` retornou somente `v1` com `live=true`. Host/grupo configurados no `.env` correspondem à documentação local. `allow_push=false`; nenhuma preferência foi alterada. Nenhuma URL, credencial ou token foi registrado.
- [x] 5.2 Fazer pull somente leitura das definições para diretório temporário fora do repositório, sem registros ou variáveis; comparar com os oito arquivos aprovados (`titulo.xs`, `reserva.xs`, `titulos_id_PATCH.xs`, `admin/acervo_GET.xs`, `solicitacoes_POST.xs`, `minhas_solicitacoes_GET.xs`, `minhas_GET.xs`, `reservas_POST.xs`) e documentar os contratos, diferenças e recomendação em `docs/xano-diferencas.md`. Revisar `git status` e os diffs antes do push.
  - Evidência (2026-11-24): pull de definições do workspace `151966`/branch `v1` e comparação dos oito objetos concluídos; relatório em `docs/xano-diferencas.md`. Worktree tinha alterações preexistentes fora de `xano/` e desta Change; foram preservadas.
- [ ] 5.3 Validar os oito XanoScript com Xano Developer MCP e executar `xano workspace push --dry-run` a partir de uma pasta temporária que contenha somente os oito arquivos, com workspace/branch explícitos; inspecionar e mostrar o resultado antes de publicar. Não usar `--sync`, `--delete`, `--records`, `--env`, `--truncate` ou `--force` no push; não alterar `allow_push`. Se o push direto for recusado por essa preferência, parar sem trocar para sandbox.
  - Bloqueio (2026-11-24): nova validação em lote pelo Xano Developer MCP falhou após 60 s porque a negociação do cliente não terminou. Os dry-runs anteriores em staging com os oito caminhos remotos `api/biblioteca/...` mostraram somente atualizações de `admin/acervo GET` e `solicitacoes-emprestimo POST`. `workspace get` confirmou `allow_push=false` e `branch list` confirmou `v1` como live; nenhum push ou alteração dessa preferência foi feito.
- [ ] 5.4 Publicar os oito arquivos delimitados somente após dry-run sem objetos adicionais; fazer pull posterior para diretório temporário e comparar as definições publicadas com as fontes locais. Conferir os fluxos PATCH/GET de desativação e POST/GET de solicitação/reserva por contrato publicado. Não executar escritas de teste contra registros reais; qualquer teste HTTP com escrita exige fixtures e conta de teste autorizadas.
  - Bloqueio (2026-11-24): a publicação permanece impedida por `allow_push=false`. Não foi tentado push, nem alterada a preferência ou usado outro workspace. Para alinhar a regra anti-duplicidade, aplicar e publicar manualmente no painel a versão local de `POST /solicitacoes-emprestimo`; os contratos de confirmação GET e POST/GET de reservas correspondem estaticamente ao Reflex. A confirmação de runtime continua pendente.

## 6. Verificação local

- [x] 6.1 Atualizar `docs/relatorio-noite.md`, validar Change e specs com `--strict`, executar `reflex compile --dry` e pytest em sequência e revisar as evidências; registrar sucesso/falha sem executar build de produção ou robô visual.
  - Evidência (2026-11-24): `reflex compile --dry` passou; `pytest --ignore=evaluation -q` — 377 passed; Change validada com `openspec validate xano-funciona-v9 --strict` e 10 specs com `openspec validate --specs --strict`. A tentativa de pytest sem exclusão não coletou `evaluation/reflex-poc/tests/test_mock_api.py` por falta de `fastapi`; o próprio script oficial exclui `evaluation`. Nenhum build de produção ou robô visual foi executado.

## Workflow follow-up

- Revisar e aprovar os artefatos antes de iniciar Apply.
- Depois de Apply e Verify aprovados, sincronizar specs, arquivar a Change e enviar commits sem force.

## 7. Diagnóstico de falhas em chamadas Xano

- [x] A. Emitir sempre no stderr um bloco de erro sanitizado e correlacionável para falhas HTTP, transporte, timeout, 2xx ilegível e resultado inesperado; incluir ação, perfil, metadados, chaves enviadas e resposta limitada; integrar o handler de exceções do backend Reflex; permitir desligamento por `BIBLIOTECA_LOG_ERROS=0` e manter sucessos sob `BIBLIOTECA_DIAGNOSTICO=1`. Testar cada classe e provar que tokens, e-mails e senhas não aparecem.
  - Evidência: commit `c4ba801`; `pytest tests\test_xano_client.py tests\test_frontend_foundation.py -q` — 51 passed. Saídas verificadas: falha HTTP, conexão, timeout, 2xx inválido/incompatível, sanitização, opção desligada e traceback do hook.
- [x] B. Acrescentar a referência do terminal a mensagens de erro de botão e mostrar mensagens curtas e seguras dos 4xx do Xano. Testar vínculo da referência e filtragem de mensagens.
  - Evidência: commit `27edb4f`; suíte focada de cliente, reservas, autenticação e acervo — `175 passed`; as mensagens de estado e do hook Reflex incluem referência correlacionada, e detalhes ingleses, e-mails e números longos ficam ocultos.
- [x] C. Em POST 2xx ilegível de solicitação, reler imediatamente, +1,5 s e +3 s; confirmar somente se encontrar o título, jamais repetir POST, manter o botão bloqueado até terminar e fazer “Tentar de novo” apenas reler listas. Testar segunda releitura com pedido, ausência, JSON incompatível, 429, 5xx e timeout.
  - Evidência: commit `6c037a6`; `pytest tests\test_student_area.py -q` — `58 passed`; inclui confirmação na releitura seguinte, ausência com log/ref correlacionados, intervalos `1,5 s`, retry manual somente GET e erros 429/5xx/timeout sem repetir POST.
- [x] D. Testar que desativação envia `ativo` como booleano `false`; comparar linha a linha o PATCH local com `api\biblioteca\catalogo\titulos\titulo_id_PATCH.xs` da cópia existente e documentar exatamente o comportamento de `$input.ativo` até `db.patch`, qualquer descarte de `false`, correção local e passos manuais de aplicação/teste sem publicar.
  - Evidência: commit `6a08fe9`; `pytest tests\test_admin_catalog.py tests\test_catalog.py tests\test_xano_client.py -q` — `100 passed`; teste confirma `ativo is False`, e log de divergência registra enviado/resposta/releitura. Comparação local/remota encontrou somente formatação; nenhum XanoScript foi alterado.
- [x] E. Recriar teste equivalente que impede uma segunda solicitação durante a escrita e até o fim da releitura, verificando que nenhum segundo POST é enviado; registrar em uma linha do relatório por que o teste antigo foi substituído.
  - Evidência: commit `75854db`; `pytest tests\test_student_area.py::test_student_request_cannot_be_submitted_again_while_pending -q` — `1 passed`; a segunda ativação foi tentada enquanto a releitura GET estava suspensa, sem POST adicional.
- [x] F. Ajustar somente tokens de cor de “Acessibilidade” para preservar posição, tamanho e formato; calcular e testar contraste >=4,5:1 para Perfil e Acessibilidade em temas claro/escuro, repouso/hover/foco.
  - Evidência: commit `9421d01`; `pytest tests\test_layout_v5.py tests\test_frontend_foundation.py -q` — `29 passed`; contraste calculado (repouso/foco; hover): Perfil claro 11,85/10,78:1 e escuro 9,17/7,84:1; Acessibilidade claro 14,00/12,73:1 e escuro 13,34/11,40:1.
- [ ] G. Concluir tarefas pendentes locais da v9 para resumo independente da home, “Testar conexão” para usuário logado e documentação comparativa com a cópia remota existente; atualizar `docs/relatorio-noite.md`, validar specs com `--strict`, executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e pytest em sequência. Não escrever no Xano nem fazer novo pull; validar e arquivar somente se todas as tarefas puderem ser concluídas, caso contrário deixar Change aberta com bloqueio explícito.
  - Evidência parcial (2026-11-25): tarefas locais 3.1, 4.1 e 5.2 concluídas; compile dry passou; `pytest --ignore=evaluation -q` — `404 passed`; Change válida com `--strict` e 10 specs aprovadas. O requisito de contraste foi classificado como `ADDED`, pois ainda não existe na spec consolidada.
  - Bloqueio: 5.3 permanece sem validação XanoScript bem-sucedida pelo MCP (a tentativa anterior expirou na negociação); 5.4 está impedida por `allow_push=false`. Não houve escrita no Xano nem novo pull; a Change fica aberta e não será arquivada.

## 8. Correção dos retornos e tráfego Xano

- [x] H. Reproduzir com payloads exatos a resposta individual e a lista de solicitações reais; identificar campo/parsers que rejeitam `reserva_id=0`, tratar zero/null como ausência em IDs/datas opcionais sem relaxar IDs obrigatórios, preservar estados desconhecidos como texto, emitir uma única falha detalhada por chamada com campo/motivo, duração real e ação/perfil de sessão. Testar também campos opcionais equivalentes de empréstimos e reservas.
  - Evidência: commit `91e9a01`; `pytest tests\test_student_area.py tests\test_circulation.py tests\test_xano_client.py -q` — 108 passed. Identificado `parse_optional_xano_id` como rejeição de `reserva_id=0`; payloads reais e campos opcionais de solicitação, reserva e empréstimo cobertos.
- [x] I. Confirmar imediatamente o POST 2xx cujo objeto tem ID válido e `titulo_id` solicitado; acrescentar o registro ao estado local e manter o botão bloqueado até atualização. Somente se corpo/resposta não confirmar, fazer no máximo duas releituras GET após 1,5 s e 4 s. Testar sucesso direto, escrita incerta e nenhuma repetição do POST.
  - Evidência: commit `ae56041`; `pytest tests\test_student_area.py tests\test_circulation.py -q` — 78 passed. O POST mínimo com `id` e `titulo_id` confirma sem GET; o registro é inserido no estado local, e resposta ilegível mantém releituras limitadas e não repete o POST.
- [x] J. Remover repetições GET por resposta 2xx incompatível; localizar e eliminar carregamentos duplicados/retentativas aninhadas; implementar single-flight para GET idêntico simultâneo e cache autenticado de 20 s com chave não reversível por sessão, invalidado por qualquer escrita do usuário. Documentar em `docs/diagnostico-xano.md` o máximo esperado de chamadas na abertura (4). Testar concorrência, cache, invalidação e 2xx inválido sem retry.
  - Evidência: commit `b6680b6`; `pytest tests\test_xano_client.py tests\test_student_area.py tests\test_primary_journeys.py -q` — 120 passed. A home deixou de carregar dados pessoais/administrativos automaticamente, GETs pessoais simultâneos compartilham uma chamada, o cache expira em 20 s e escritas invalidam as listas da sessão.
- [x] K. Implementar limitador global assíncrono de janela deslizante por host, configurável por `BIBLIOTECA_XANO_LIMITE_REQ` e `BIBLIOTECA_XANO_JANELA_S`, fila com prioridade para escritas e leituras acionadas pelo usuário, limite de espera de 25 s e pausa global após 429 até janela + 1 s. Repetir somente GET uma vez após 429; jamais repetir escrita. Exibir mensagem de limite com espera e referência. Testar janela com relógio falso, pausa, retomada, prioridade e não repetição de escrita.
  - Evidência: commit `81322df`; `pytest tests\test_xano_client.py -q` — 38 passed. Cobertos janela deslizante de 8/20 com relógio falso, pausa e retomada após 429, retry único de GET e não repetição de POST.
- [x] L. Antes do POST, impedir pedido duplicado quando as listas carregadas já mostrarem pedido pendente/aprovado ou reserva ativa para o título. Exibir a orientação sem referência; criar `docs/xano-limpeza-pedidos.md` com identificação por usuário/título, backup e procedimento manual de remoção, sem executar operações; registrar que a regra remota não foi publicada. Testar bloqueio e envio quando não há duplicidade.
  - Evidência: commit `cee735b`; teste focado `test_student_request_blocks_duplicate_from_loaded_lists` — 1 passed. O POST não é chamado e a mensagem é orientativa sem referência; `docs/xano-limpeza-pedidos.md` registra identificador, backup e procedimento manual sem operações.
- [x] M. Garantir no detalhe e em Reservas que “Tentar de novo” faça somente uma releitura, passando pelo limitador, sem POST; testar ambos os caminhos sem duplicação de chamadas.
  - Evidência: commit `cee735b`; testes focados de releitura manual e bloqueio até recuperação — 2 passed em `test_student_area.py`. Reservas chama somente listas; o detalhe não envia solicitação em retry.
- [ ] N. Executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e pytest em sequência, atualizar `docs/relatorio-noite.md`, validar Change/specs com `--strict`, manter abertos os bloqueios 5.3/5.4, criar commit por tarefa e fazer push sem force. Não sincronizar nem arquivar.
