# Tasks

## 1. Leitura tolerante

- [x] 1.1 Implementar extração dos envelopes, conversões escalares e validação por registro nos leitores autenticados de empréstimos, pedidos, reservas, equipe, bibliotecários, acervo e categorias; cobrir lista simples/embrulhada, ms/s, nulos, campos extras, registro ilegível e topo inválido com fixtures simuladas.
  - Evidência: commit `48bef7e`; `pytest tests\test_student_area.py tests\test_circulation.py tests\test_catalog.py tests\test_admin_catalog.py tests\test_user_admin.py tests\test_staff_reservations.py -q` — 160 passed; `reflex compile --dry` concluído com sucesso.

## 2. Escritas sem repetição

- [x] 2.1 Tratar respostas POST/PATCH 2xx ilegíveis sem repetir a escrita, atualizar as listas e só confirmar a reserva após a releitura encontrá-la; testar sucesso, ausência de confirmação, erro, transporte e ausência de retry.
  - Evidência: commit `26e7601`; `pytest tests\test_student_area.py tests\test_circulation.py tests\test_catalog.py tests\test_admin_catalog.py tests\test_user_admin.py tests\test_staff_reservations.py tests\test_signup.py tests\test_xano_client.py tests\test_frontend_foundation.py -q` — 231 passed; `reflex compile --dry` — sucesso.
- [x] 2.2 Bloquear nova submissão em Reservar durante a tentativa e até a confirmação pela releitura; manter o bloqueio quando a escrita for incerta e testar liberação somente após confirmação.
  - Evidência: commit `26e7601`; testes de confirmação e bloqueio incluídos na suíte focada — 231 passed; `reflex compile --dry` — sucesso.

## 3. Resumo da home

- [ ] 3.1 Tornar independentes o carregamento, erro, valor “—” e retry de cada indicador; testar falha isolada e preservação dos demais resultados.

## 4. Diagnóstico pelo Perfil

- [ ] 4.1 Adicionar diagnóstico somente leitura para usuários autenticados, com chamadas autorizadas pelo perfil, validação estrutural e relatório copiável sem valores sensíveis; documentar em `docs/diagnostico-xano.md` e testar 200 válido/inválido, 403, 404, 429, não JSON e sanitização.

## 5. Comparação de contratos Xano

- [ ] 5.1 Antes do pull, confirmar via Xano CLI o workspace, branch e ambiente selecionados e registrar a identificação na Change; puxar somente definições para pasta temporária fora do repositório, inventariar todas as chamadas do app e documentar em `docs/xano-diferencas.md` existência, autorização, entradas, resposta esperada, diferença local e recomendação “Publicar: sim/não”; conferir que não houve escrita remota nem segredo/URL no relatório.
  - Bloqueio: o perfil padrão informa somente um ID de workspace e a listagem de workspaces pelo CLI falha; não foi possível confirmar que o destino é a biblioteca nem confirmar branch/ambiente. Nenhuma definição foi puxada e nenhuma escrita foi feita no Xano.

## 6. Verificação local

- [ ] 6.1 Atualizar `docs/relatorio-noite.md`, validar Change e specs com `--strict`, executar `reflex compile --dry` e pytest em sequência e revisar as evidências; registrar sucesso/falha sem executar build de produção ou robô visual.

## Workflow follow-up

- Revisar e aprovar os artefatos antes de iniciar Apply.
- Depois de Apply e Verify aprovados, sincronizar specs, arquivar a Change e enviar commits sem force.
