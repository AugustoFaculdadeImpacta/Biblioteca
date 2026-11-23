# Proposal

## Why

A barra superior e a hierarquia visual atual quebram em perfis e telas diferentes, com estilos de ação vazando para links de navegação e o rodapé. Esta Change estabiliza o layout completo e atualiza a experiência do acervo, das reservas, do login e do seed sem alterar contratos Xano remotos.

## What Changes

- Refazer o cabeçalho e a navegação com contratos CSS explícitos por tema, comportamento móvel isolado e links simples no rodapé.
- Padronizar contêineres, larguras, grades e estados vazios das páginas operacionais e de autenticação.
- Reorganizar home, catálogo, detalhe, reservas, Acervo e Contas no padrão visual de app de delivery.
- Remover emojis decorativos irrelevantes, preservando emojis exclusivos nas ações e selos.
- Resolver capas por prioridade HTTPS do Xano, Open Library pelo ISBN normalizado e capa gerada local.
- Substituir o catálogo de demonstração por 30 livros reais das oito categorias existentes, com ISBN-13 validável.
- Adicionar diagnóstico opt-in da desativação, sem dados pessoais ou valores sensíveis.

## Capabilities

### New Capabilities

- `cover-isbn`: resolução de capas reais por ISBN, fallback determinístico e ausência de requisições externas no servidor.
- `deactivation-diagnostics`: registro terminal opt-in do PATCH de desativação e da releitura, sem dados pessoais.

### Modified Capabilities

- `frontend-foundation`: barra, navegação, layout estável, login/cadastro, padrões de páginas e tokens responsivos.
- `catalog`: catálogo por categorias, detalhes de produto, capas, Acervo e seed de 30 títulos reais.
- `primary-journeys`: jornadas visuais da home, reserva, acompanhamento e navegação por perfil.

## Impact

- Frontend Reflex em `biblioteca_mais_nova/biblioteca_mais_nova.py`.
- Novo índice local `biblioteca_mais_nova/capas_isbn.py`.
- Reescrita controlada de `scripts/seed_catalogo_real.py` e documentação do seed.
- Novo diagnóstico em `docs/diagnostico-desativacao.md` e registro em `docs/relatorio-noite.md`.
- Testes pytest focados em CSS, estrutura das páginas, capas, seed e logs.
- Nenhuma escrita no Xano real e nenhuma captura obrigatória em caso de falha do Edge headless.
