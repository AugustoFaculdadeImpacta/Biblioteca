# Tasks

## 0. README prioritário

- [x] 0.1 Substituir README.md por instruções concisas (máximo 40 linhas), conferir URL e comandos e validar a contagem de linhas; 40 linhas e `git diff --check` aprovados, commit `7314ab7`, push imediato concluído.

## 1. Parser das regras

- [x] 1.1 Reproduzir o corpo Xano exato em teste, aceitar metadados opcionais e formatos de data solicitados, manter validação dos sete campos e testar que o diagnóstico identifica campo inválido; `pytest tests/test_library_rules.py -q` — 20 passed, commit `93b586b`.

## 2. Cópia pública e pré-carga

- [x] 2.1 Implementar cache em memória e JSON temporário com validade de 24 horas, gravação segura e testes de relógio falso e caminho fora do repositório; `pytest tests/test_public_data_cache.py -q` — 3 passed, commit `98cb56d`.
- [x] 2.2 Integrar cópia imediata/atualização em segundo plano às telas públicas e fazer pré-carga idempotente; `pytest tests/test_public_cache_ui.py -q` — 6 passed; commit `fcfca63`.

## 3. Listas autenticadas

- [x] 3.1 Mostrar a cópia autenticada de até 20 segundos imediatamente e reler em segundo plano nas listas pessoais e da equipe, sem ocultar escritas próprias; `pytest tests\test_authenticated_snapshot_ui.py tests\test_student_area.py tests\test_circulation.py tests\test_admin_catalog.py -q` — 132 passaram; commit `b4bec42`.

## 4. Escritas otimistas

- [ ] 4.1 Implementar estados otimistas reversíveis para pedido, ações da equipe e desativação, fila sequencial sem retry e releitura agrupada em 1,5 segundo; os estados de pedido/equipe, rollback de desativação e fila sequencial estão implementados em `24b626a` e cobertos por 176 testes e 10 casos focados; a releitura agrupada/debounce ainda está pendente.

## 5. Demonstração e desempenho

- [x] 5.1 Adicionar latência configurável à API demo e registrar medições locais simuladas com 1000 ms; `pytest tests/test_demo_api_library_rules.py tests/test_xano_client.py -q` — 63 passed; medição e 3 chamadas por página em `docs/desempenho.md`; commit `4e0fcff`.

## 6. Changes preexistentes e relatório

- [x] 6.1 Arquivar `execucao-reflex-windows` e `validacao-remota-xano` sem alterar o Xano; tarefas remotas/visuais ficaram transferidas ou aguardando conferência, e o relatório registra ações do usuário. Evidências finais: 501 testes pytest, 17 testes unittest, 11 specs em validação estrita; commits `b4bec42` e `d8f4bf3`.

## 7. Fechamento v11

- [ ] 7.1 Executar compile --dry e pytest em sequência, validar specs estritamente, sincronizar e arquivar esta Change, atualizar o relatório, commitar e fazer push sem force.
