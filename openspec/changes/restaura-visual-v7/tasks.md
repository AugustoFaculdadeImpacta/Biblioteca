# Tasks

## 1. Cabeçalho e aparência compartilhada

- [x] 1.1 Restaurar os tokens, tipografia, cabeçalho, faixa de visão do admin, Perfil, Acessibilidade e rodapé; manter busca, navegação e preferências existentes. Evidências: commit `221beb8`; `.\.venv\Scripts\python.exe -m pytest tests/test_navigation.py tests/test_frontend_foundation.py` (66 aprovados). Aparência implementada, aguarda conferência do usuário; matriz visual será registrada em 5.1.

## 2. Home e cartões

- [x] 2.1 Restaurar o hero e as seções da home sem perder dados dinâmicos, resumo por perfil, novidades, categorias ou passos de reserva; reintroduzir Sobre, corrigir contagens das pílulas e atualizar os contratos CSS antigos. Evidências: commit `d70d812`; `.\.venv\Scripts\python.exe -m pytest tests/test_layout_v5.py tests/test_primary_journeys.py tests/test_catalog.py tests/test_navigation.py tests/test_frontend_foundation.py tests/test_icons.py` (124 aprovados). Aparência implementada, aguarda conferência do usuário; matriz visual será registrada em 5.1.

## 3. Dados compartilhados de exemplo

- [x] 3.1 Mover os 30 livros para `biblioteca_mais_nova/seed_data.py` e manter `scripts/seed_catalogo_real.py` como alternativa baseada na mesma fonte. Evidências: commit `5f83036`; `.\.venv\Scripts\python.exe -m pytest tests/test_seed_catalogo.py tests/test_covers.py` (14 aprovados).

## 4. Importação pelo Acervo

- [ ] 4.1 Implementar seção admin recolhida, prévia somente leitura, confirmação inline e importação sequencial idempotente por título/autoria, com mapeamento de categorias e interrupção segura. Cobrir com cliente simulado a prévia sem escrita, criação, segunda execução, categoria ausente, falha, visibilidade e ausência de segredos; verificar com os testes de importação.

## 5. Integração e evidências

- [ ] 5.1 Executar verificações locais sem paralelizar compile e pytest; rodar uma única vez a matriz visual visitante em `/`, `/catalogo` e `/login`, 1366/360 px e temas claro/escuro, limitada a 15 minutos; registrar resultados e lacunas em `docs/relatorio-noite.md`. Validar os deltas e specs com `openspec.cmd validate --strict`.

## Workflow follow-up

- Arquivar `layout-livraria-v6` como substituída, usando `--skip-specs` e a nota `substituída por restaura-visual-v7`.
- Sincronizar os deltas e arquivar `restaura-visual-v7` somente após concluir a verificação local.
- Fazer push sem `--force` após os commits da Change.
