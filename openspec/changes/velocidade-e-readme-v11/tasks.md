# Tasks

## 0. README prioritário

- [x] 0.1 Substituir README.md por instruções concisas (máximo 40 linhas), conferir URL e comandos e validar a contagem de linhas; 40 linhas e `git diff --check` aprovados, commit `7314ab7`, push imediato concluído.

## 1. Parser das regras

- [x] 1.1 Reproduzir o corpo Xano exato em teste, aceitar metadados opcionais e formatos de data solicitados, manter validação dos sete campos e testar que o diagnóstico identifica campo inválido; `pytest tests/test_library_rules.py -q` — 20 passed, commit `93b586b`.

## 2. Cópia pública e pré-carga

- [x] 2.1 Implementar cache em memória e JSON temporário com validade de 24 horas, gravação segura e testes de relógio falso e caminho fora do repositório; `pytest tests/test_public_data_cache.py -q` — 3 passed, commit `98cb56d`.
- [ ] 2.2 Integrar cópia imediata/atualização em segundo plano às telas públicas e fazer pré-carga idempotente; testar cópia antes da resposta, atualização, 429 e chamada única.

## 3. Listas autenticadas

- [ ] 3.1 Servir cópia autenticada de até 20 segundos antes da releitura em segundo plano, sem ocultar escritas próprias; cobrir as rotas pessoais e de acervo com relógio falso.

## 4. Escritas otimistas

- [ ] 4.1 Implementar estados otimistas reversíveis para pedido, ações da equipe e desativação, fila sequencial sem retry e releitura agrupada em 1,5 segundo; testar confirmação, falha, ordem e lote.

## 5. Demonstração e desempenho

- [ ] 5.1 Adicionar latência configurável à API demo e registrar medições reais com 1000 ms, com e sem cópia, além de chamadas por página em docs/desempenho.md.

## 6. Changes preexistentes e relatório

- [ ] 6.1 Resolver tarefas locais das Changes ativas preexistentes, transferir bloqueios Xano/visuais com evidência, arquivar as concluídas ou obsoletas segundo suas regras e registrar o que falta ao usuário em docs/relatorio-noite.md.

## 7. Fechamento v11

- [ ] 7.1 Executar compile --dry e pytest em sequência, validar specs estritamente, sincronizar e arquivar esta Change, atualizar o relatório, commitar e fazer push sem force.
