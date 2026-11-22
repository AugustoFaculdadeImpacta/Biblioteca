# Tasks

## 1. Primários e contraste no tema escuro

- [x] 1.1 Ajustar tokens e classes dos botões primários nos temas claro/escuro, incluindo Entrar, Criar conta, Cadastrar título, Salvar, Adicionar exemplar e Buscar; verificar contraste contra texto e painel com testes novos de `test_primary_actions_meet_wcag_contrast`. Commits `f5f2818` e `ded0dc0`. Verificação: `reflex compile --dry` aprovado; `pytest --ignore=evaluation -q`: 257 passed. Visual: feito, aguarda conferência do usuário.

## 2. Campos, autofill e formulários

- [x] 2.1 Centralizar inputs verticalmente, aplicar autofill/autofill webkit com tokens e remover caixas internas de textarea/select; verificar cada correção com testes novos de `test_text_fields_align_and_autofill_safely`, `test_editing_controls_keep_external_border_only` e `test_category_checkboxes_share_44px_row`. Commit `ad51bd2`. Verificação: `reflex compile --dry` aprovado; `pytest --ignore=evaluation -q`: 260 passed. Visual: feito, aguarda conferência do usuário.

## 3. Interruptor efetivo de tema

- [x] 3.1 Fazer o interruptor refletir o tema explícito ou herdado e mostrar emoji/texto/aria-checked correspondentes em todas as páginas após recarga; verificar com `test_theme_switch_reports_effective_destination`. Commit `eb9485e`. Verificação: `reflex compile --dry` aprovado; `pytest --ignore=evaluation -q`: 261 passed. Visual: feito, aguarda conferência do usuário.

## 4. Emojis decorativos e identificação

- [x] 4.1 Acrescentar emojis em spans decorativos antes da marca, menu, perfil, seções, selos e botões solicitados; verificar com `test_decorative_emojis_are_aria_hidden` e atualizar os testes relacionados a rótulos. Commit `24b955f`. Verificação: `reflex compile --dry` aprovado; `pytest --ignore=evaluation -q`: 262 passed. Visual: feito, aguarda conferência do usuário.

## 5. Animações leves e reduzidas

- [x] 5.1 Adicionar entrada de página, cascata limitada, elevação, zoom de capa, abertura do menu, gradiente flutuante do hero, transição de tema e pulso único dos selos; verificar todas as regras com `test_motion_rules_have_reduced_motion_override`. Commit `012b03a`. Verificação: `reflex compile --dry` aprovado; `pytest --ignore=evaluation -q`: 263 passed. Visual: feito, aguarda conferência do usuário.

## 6. Capas únicas

- [x] 6.1 Criar `biblioteca_mais_nova/covers.py`, derivar `capa_gerada` nas entradas e usá-la em home, catálogo, detalhe e Acervo; verificar com `test_generated_cover_is_deterministic`, `test_generated_cover_is_distinct_across_seed_titles`, `test_generated_cover_has_no_external_scripts`, `test_generated_cover_handles_invalid_data` e limites do grid. Commits `8d987cf` e `cfc1792`. Verificação: `reflex compile --dry` aprovado; `pytest --ignore=evaluation -q`: 268 passed. Visual: feito, aguarda conferência do usuário.

## 7. Diagnóstico e ações operacionais

- [ ] 7.1 Investigar evento, cliente e endpoints de desativação comparando código, documentação e pull temporário de definições; corrigir processamento, confirmação, mensagens e atualização da linha; testar sucesso, 404, 403 e conexão com `test_admin_actions_handle_success_404_403_and_connection`, registrar pendências exatas sem marcar concluída.

## 8. Acervo compacta

- [ ] 8.1 Implementar busca normalizada, cadastro fechado, uma edição aberta por vez, “Mostrar mais”, lista compacta e edição staff no catálogo/detalhe; verificar com `test_acervo_search_normalizes_text_and_empty_state`, `test_acervo_has_one_edit_panel`, `test_acervo_paginates_in_groups_of_ten`, `test_staff_can_edit_from_catalog_and_detail`.

## 9. Seed seguro

- [ ] 9.1 Criar `scripts/seed_catalogo_real.py`, documentação `docs/seed-catalogo.md` e testes simulados de dry-run, credenciais, idempotência e categorias; verificar que a senha nunca aparece e que nenhuma escrita ocorre no modo padrão.

## 10. Limpeza da Change refino-visual-biblioteca

- [ ] 10.1 Arquivar `refino-visual-biblioteca` sem sincronizar specs, registrar o motivo no relatório e confirmar as specs consolidadas com `openspec.cmd validate --specs --strict`.

## 11. Evidências e fechamento

- [ ] 11.1 Atualizar `docs/relatorio-noite.md` com item, commit, testes e status visual ou pendência Xano, incluir `openspec.cmd list --json` e o bloco “O que o usuário precisa publicar no Xano”; validar a Change, sincronizar specs, arquivar e fazer push sem `--force`.

## Workflow follow-up

- Não executar o seed com `--apply`, publicar Xano ou alterar tabelas/endpoints nesta Change.
- Não usar navegador ou capturas.
