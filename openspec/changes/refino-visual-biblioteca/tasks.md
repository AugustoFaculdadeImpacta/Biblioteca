# Tasks

## 1. Tokens e tema global

- [B] 1.1 Implementar tokens creme/grafite/azul-petróleo/verde/âmbar, tipografia local, movimento reduzido e estados de foco; adicionar `test_visual_tokens_keep_accessible_contrast_and_reduced_motion` em `tests/test_frontend_foundation.py`, validar combinações WCAG AA e `:focus-visible`, executar `.venv\Scripts\python.exe -m reflex compile --dry` e `.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`, medir DOM em 360 px e 1366 px, registrar hash/teste/métricas e se a inspeção visual foi feita, então criar commit pequeno em português. Motivo: compilação e testes passaram (205); métricas DOM foram lidas antes da correção final do seletor, mas o navegador integrado passou a retornar DOM vazio após o reinício do Reflex, impedindo capturas válidas pós-alteração.

## 2. Cabeçalho e rodapé

- [B] 2.1 Adicionar slogan, simplificar navegação sem alterar permissões por perfil, padronizar o rodapé com links apenas para destinos oficiais; adicionar `test_site_header_brand_and_footer_links_preserve_profile_access` em `tests/test_navigation.py`, executar compilação e suíte pytest completas, medir DOM nos dois viewports e perfis visitante/estudante/bibliotecário/admin, registrar hash/teste/métricas e se a inspeção visual foi feita, então criar commit pequeno em português. Motivo: compilação e testes passaram (206); a sessão Playwright do navegador expirou e a recarga anterior retornou DOM vazio após erro de conexão do Reflex, impedindo métricas por perfil e capturas pós-alteração.

## 3. Página inicial e seções

- [ ] 3.1 Implementar hero e seções de catálogo com “Ver mais”, dados públicos existentes e estados explícitos sem números ou novidades inventados; adicionar `test_home_sections_use_catalog_data_and_explicit_empty_error_states` em `tests/test_primary_journeys.py`, preservar o redirecionamento de sessões autenticadas, executar compilação e suíte pytest completas, medir DOM a 360 px e 1366 px, registrar hash/teste/métricas e se a inspeção visual foi feita, então criar commit pequeno em português.

## 4. Cartões e catálogo

- [ ] 4.1 Melhorar capa CSS determinística, autoria, disponibilidade, ações, busca e filtros; adicionar `test_catalog_card_derives_cover_fallback_from_category_and_title` e `test_catalog_controls_and_card_states_are_responsive` em `tests/test_catalog.py`, sem ampliar o contrato Xano, executar compilação e suíte pytest completas, medir grade/overflow/alvos em 360 px e 1366 px, registrar hash/testes/métricas e se a inspeção visual foi feita, então criar commit pequeno em português.

## 5. Formulários, painéis e estados

- [ ] 5.1 Aplicar o tema a formulários, listas e estados vazio/carregando/erro/sucesso, preservando semântica e autorização; adicionar `test_forms_and_admin_panels_use_shared_visual_states` e `test_touch_targets_and_keyboard_accessibility_at_mobile_viewport` em `tests/test_frontend_foundation.py`, executar compilação e suíte pytest completas, medir DOM para as telas e perfis documentados em 360 px e 1366 px, registrar hash/testes/métricas e se a inspeção visual foi feita, então criar commit pequeno em português.

## 6. Relatório e fechamento

- [ ] 6.1 Atualizar `docs/relatorio-noite.md` com uma linha por tela/perfil e colunas 360 px e 1366 px, incluir os hashes e nomes de testes dos cinco commits, métricas DOM e a declaração “visual não visto” quando não houver inspeção; verificar que nenhuma pendência foi marcada por suposição e criar commit documental em português contendo somente relatório e tarefas OpenSpec.

## Verificação do navegador

- Para métricas locais, usar somente a API demo em `8765`, Reflex frontend em `8020` e backend em `8021`, após confirmar que as portas escolhidas estão livres. Não encerrar listeners preexistentes e nunca parar processos nas portas protegidas.
- Registrar largura do viewport, largura total de rolagem, dimensões dos alvos acionáveis e colunas visíveis da grade em ambas as larguras. Métricas DOM não equivalem a inspeção visual; escrever “visual não visto” no relatório se não houver captura inspecionada.
- Fazer cada commit de bloco após sua compilação, suíte completa, testes nomeados e evidência DOM. Não stagear arquivos preexistentes ou fora do bloco; atualizar o relatório com os hashes conhecidos no fechamento.

## Workflow follow-up

- Aguardar revisão/aprovação humana desta Change antes de iniciar Apply.
- Arquivar somente após implementação aprovada, verificação de todos os requisitos e validação OpenSpec estrita.
