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

- [ ] 3.1 Tornar independentes o carregamento, erro, valor “—” e retry de cada indicador; testar falha isolada e preservação dos demais resultados.

## 4. Diagnóstico pelo Perfil

- [ ] 4.1 Adicionar diagnóstico somente leitura para usuários autenticados, com chamadas autorizadas pelo perfil, validação estrutural e relatório copiável sem valores sensíveis; documentar em `docs/diagnostico-xano.md` e testar 200 válido/inválido, 403, 404, 429, não JSON e sanitização.

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
- [ ] C. Em POST 2xx ilegível de solicitação, reler imediatamente, +1,5 s e +3 s; confirmar somente se encontrar o título, jamais repetir POST, manter o botão bloqueado até terminar e fazer “Tentar de novo” apenas reler listas. Testar segunda releitura com pedido, ausência, JSON incompatível, 429, 5xx e timeout.
- [ ] D. Testar que desativação envia `ativo` como booleano `false`; comparar linha a linha o PATCH local com `api\biblioteca\catalogo\titulos\titulo_id_PATCH.xs` da cópia existente e documentar exatamente o comportamento de `$input.ativo` até `db.patch`, qualquer descarte de `false`, correção local e passos manuais de aplicação/teste sem publicar.
- [ ] E. Recriar teste equivalente que impede uma segunda solicitação durante a escrita e até o fim da releitura, verificando que nenhum segundo POST é enviado; registrar em uma linha do relatório por que o teste antigo foi substituído.
- [ ] F. Ajustar somente tokens de cor de “Acessibilidade” para preservar posição, tamanho e formato; calcular e testar contraste >=4,5:1 para Perfil e Acessibilidade em temas claro/escuro, repouso/hover/foco.
- [ ] G. Concluir tarefas pendentes locais da v9 para resumo independente da home, “Testar conexão” para usuário logado e documentação comparativa com a cópia remota existente; atualizar `docs/relatorio-noite.md`, validar specs com `--strict`, executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e pytest em sequência. Não escrever no Xano nem fazer novo pull; validar e arquivar somente se todas as tarefas puderem ser concluídas, caso contrário deixar Change aberta com bloqueio explícito.
