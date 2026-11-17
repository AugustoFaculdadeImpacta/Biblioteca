# Tasks

## 1. Tokens e tema global

- [B] 1.1 Implementar tokens creme/grafite/azul-petróleo/verde/âmbar, tipografia local, movimento reduzido e estados de foco; adicionar `test_visual_tokens_keep_accessible_contrast_and_reduced_motion` em `tests/test_frontend_foundation.py`, validar combinações WCAG AA e `:focus-visible`, executar `.venv\Scripts\python.exe -m reflex compile --dry` e `.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`, medir DOM em 360 px e 1366 px, registrar hash/teste/métricas e se a inspeção visual foi feita, então criar commit pequeno em português. Motivo: commit `322102e03038dfa0ffd856858a230666bd9f32c0`; compilação aprovada e 205 testes aprovados. O teste citado foi adicionado. As capturas atuais `home-tema-360.png` e `home-tema-1366.png` antecedem a correção final do escopo dos tokens e não são evidência válida; inspeção DOM/captura atual: não verificada, visual não visto após erro de conexão do navegador integrado.

## 2. Cabeçalho e rodapé

- [B] 2.1 Adicionar slogan, simplificar navegação sem alterar permissões por perfil, padronizar o rodapé com links apenas para destinos oficiais; adicionar `test_site_header_brand_and_footer_links_preserve_profile_access` em `tests/test_navigation.py`, executar compilação e suíte pytest completas, medir DOM nos dois viewports e perfis visitante/estudante/bibliotecário/admin, registrar hash/teste/métricas e se a inspeção visual foi feita, então criar commit pequeno em português. Motivo: commit `3b09ff6e7d64de63c697be717e00fbc4e4d5273f`; compilação aprovada e 206 testes aprovados. O teste citado foi adicionado. Não há captura ou métrica DOM pós-alteração; inspeção visual por perfil não verificada após erro de conexão do navegador.

## 3. Página inicial e seções

- [B] 3.1 Implementar hero e seções de catálogo com “Ver mais”, dados públicos existentes e estados explícitos sem números ou novidades inventados; adicionar `test_home_sections_use_catalog_data_and_explicit_empty_error_states` em `tests/test_primary_journeys.py`, preservar o redirecionamento de sessões autenticadas, executar compilação e suíte pytest completas, medir DOM a 360 px e 1366 px, registrar hash/teste/métricas e se a inspeção visual foi feita, então criar commit pequeno em português. Motivo: commit `67b041a58d8a1c353b1c4d42cbe2ece250c6961b`; compilação aprovada e 207 testes aprovados. O teste citado foi adicionado. Não há captura ou métrica DOM pós-alteração; inspeção visual não verificada porque o navegador integrado falhou no handshake do Reflex.

## 4. Cartões e catálogo

- [B] 4.1 Melhorar capa CSS determinística, autoria, disponibilidade, ações, busca e filtros; adicionar `test_catalog_card_derives_cover_fallback_from_category_and_title` e `test_catalog_controls_and_card_states_are_responsive` em `tests/test_catalog.py`, sem ampliar o contrato Xano, executar compilação e suíte pytest completas, medir grade/overflow/alvos em 360 px e 1366 px, registrar hash/testes/métricas e se a inspeção visual foi feita, então criar commit pequeno em português. Motivo: commit `1a98366f621c252b2779a5a784dcb5dc8698ace6`; compilação aprovada e 209 testes aprovados com a compilação automática desabilitada após erro de lockfile congelado. Os dois testes citados foram adicionados. Sem captura nem métrica DOM pós-alteração; navegador não hidrata a página e a inspeção visual não foi verificada.

## 5. Formulários, painéis e estados

- [B] 5.1 Aplicar o tema a formulários, listas e estados vazio/carregando/erro/sucesso, preservando semântica e autorização; adicionar `test_forms_and_admin_panels_use_shared_visual_states` e `test_touch_targets_and_keyboard_accessibility_at_mobile_viewport` em `tests/test_frontend_foundation.py`, executar compilação e suíte pytest completas, medir DOM para as telas e perfis documentados em 360 px e 1366 px, registrar hash/testes/métricas e se a inspeção visual foi feita, então criar commit pequeno em português. Código/testes no commit `c17da0530aeeeee2f8f4e838607279c4be8672f5`; compilação `python -m reflex compile --dry` aprovada e suíte executada com o `_compile` automático desabilitado: 211 aprovados, incluindo os dois testes citados e `test_site_header_brand_and_footer_links_preserve_profile_access` atualizado. Bloqueio: `openBrowserPage` para `http://127.0.0.1:3010/` expirou; `readPage` exibiu somente “Connection Error:”. Sem captura ou métrica DOM pós-alteração em 360 px/1366 px; visual não visto, portanto tarefa não concluída.

## 6. Relatório e fechamento

- [B] 6.1 Relatório atualizado em `docs/relatorio-noite.md` com telas/rotas/perfis, caminhos das capturas existentes e ausência das posteriores, hashes e nomes de testes dos cinco blocos, resultados de pytest/compile/OpenSpec, seletor admin e lista OpenSpec final. Validações OpenSpec: specs 7/7 e Change válida. Motivo do bloqueio: não foi possível obter DOM atual nem capturas 360 px/1366 px; o navegador expirou e `readPage` exibiu apenas “Connection Error:”. A Change permanece ativa e não foi arquivada; o commit documental português contém somente relatório e tarefas OpenSpec.

## Verificação do navegador

- Para métricas locais, usar somente a API demo em `8765`, Reflex frontend em `8020` e backend em `8021`, após confirmar que as portas escolhidas estão livres. Não encerrar listeners preexistentes e nunca parar processos nas portas protegidas.
- Registrar largura do viewport, largura total de rolagem, dimensões dos alvos acionáveis e colunas visíveis da grade em ambas as larguras. Métricas DOM não equivalem a inspeção visual; escrever “visual não visto” no relatório se não houver captura inspecionada.
- Fazer cada commit de bloco após sua compilação, suíte completa, testes nomeados e evidência DOM. Não stagear arquivos preexistentes ou fora do bloco; atualizar o relatório com os hashes conhecidos no fechamento.

## Workflow follow-up

- Aguardar revisão/aprovação humana desta Change antes de iniciar Apply.
- Arquivar somente após implementação aprovada, verificação de todos os requisitos e validação OpenSpec estrita.
