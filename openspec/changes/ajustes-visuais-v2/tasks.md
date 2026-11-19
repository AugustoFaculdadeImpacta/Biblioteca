# Tasks

## 1. Corrigir bordas e foco dos campos

- [x] 1.1 Unificar a demarcação visual de inputs, selects, textareas e busca no controle externo, mantendo semântica e alvos de 44 px. Commits `55e68a6` e `5ef59fe` (correção do seletor no teste móvel). Testes novos: `test_text_fields_have_single_container_border_and_visible_container_focus`, `test_form_controls_keep_keyboard_focus_visible`; atualizados: `test_text_controls_have_explicit_theme_aware_colors_and_focus`, `test_touch_targets_and_keyboard_accessibility_at_mobile_viewport`. Verificação: `reflex compile --dry` aprovado; `pytest --ignore=evaluation -q`: 245 passed. Visual: feito, aguarda conferência do usuário.

## 2. Compartilhar acessibilidade com visitantes

- [ ] 2.1 Reutilizar no Perfil visitante os controles de fonte, alto contraste, redução de movimento e modo escuro; adicionar `test_visitor_profile_menu_exposes_shared_accessibility_controls`; criar commit em português e, após ele, executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`.

## 3. Persistir somente preferências de aparência

- [ ] 3.1 Persistir tema, escala, contraste e movimento na chave local `biblioteca-aparencia`, migrando apenas as três preferências legadas, aplicando o tema antes da pintura em todas as rotas e preservando valores ao sair; adicionar `test_appearance_preferences_bootstrap_on_every_route`, `test_appearance_storage_contains_only_four_preferences`, `test_appearance_storage_never_contains_session_data` e `test_legacy_accessibility_preferences_migrate`; criar commit em português e, após ele, executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`.

## 4. Completar e verificar o tema escuro

- [ ] 4.1 Auditar cores fixas e tokens, ajustar componentes e capas CSS para o tema escuro e calcular WCAG AA nos pares texto/fundo e limites de controles; atualizar `test_dark_and_high_contrast_tokens_meet_wcag_aa` e adicionar `test_dark_theme_tokens_cover_operational_components` e `test_dark_cover_fallbacks_use_saturated_palette`; criar commit em português e, após ele, executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`.

## 5. Simplificar o hero da home

- [ ] 5.1 Remover do hero busca, ações e atalhos para todos os perfis, eliminar estado/evento/estilos exclusivos da busca da home, manter destaques e “Sobre a biblioteca” e renomear o título do rodapé; atualizar `test_home_has_no_login_or_signup_form_and_keeps_profile_shortcuts` e adicionar `test_home_hero_omits_search_and_actions_for_all_profiles` e `test_footer_uses_library_name_without_repeating_home_about`; criar commit em português e, após ele, executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`.

## 6. Revisar jornadas de bibliotecário e admin

- [ ] 6.1 Auditar Perfil/visão, acervo, reservas/circulação e contas ponta a ponta; corrigir somente problemas reproduzidos de feedback, estados vazios, ações destrutivas, alvos e rolagem móvel, sem alterar contratos Xano; para cada correção, adicionar teste focado, incluindo `test_staff_admin_workflows_have_visible_feedback_and_empty_states`, `test_destructive_operations_are_visually_distinct` e `test_operational_lists_keep_horizontal_scroll_inside_container`; registrar no relatório o que foi encontrado e dependências reais de Xano; criar commit em português e, após ele, executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`.

## 7. Registrar evidências e fechar a Change

- [ ] 7.1 Atualizar `docs/relatorio-noite.md` com item, commit, testes e status visual “feito, aguarda conferência do usuário” ou pendência Xano; validar a Change e as specs com `openspec.cmd validate ajustes-visuais-v2 --strict` e `openspec.cmd validate --specs --strict`, sincronizar `frontend-foundation`, arquivar usando o fluxo OpenSpec, validar novamente, criar commit final em português e fazer push sem `--force`.

## Workflow follow-up

- Arquivar somente após os seis itens de implementação e suas verificações estarem completos.
- Não abrir navegador nem produzir capturas; registrar que a inspeção visual aguarda o usuário.
- Não acessar nem escrever no Xano real; manter pendentes somente contratos ou dados cuja ausência seja reproduzida no cliente atual.
