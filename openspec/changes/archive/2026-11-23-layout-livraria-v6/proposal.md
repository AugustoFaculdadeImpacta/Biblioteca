# Proposal

## Why

A interface atual já contém parte da estrutura estável da versão v5, mas ainda não atende integralmente à hierarquia da referência da livraria pública em todas as rotas e larguras. Esta Change conclui o layout de livraria virtual, reforça a confirmação visual dos 30 livros reais e torna a verificação navegável pelos perfis.

## What Changes

- Reescrever o cabeçalho para uma única composição responsiva, sem menu hambúrguer e sem links estilizados como botões.
- Aplicar a hierarquia de home, catálogo, detalhe, reservas, Acervo e Contas no estilo da referência.
- Completar a resolução de capas por capa HTTPS do título, Open Library pelo ISBN ou capa gerada local.
- Preservar os 30 títulos reais das oito categorias aprovadas e registrar o seed sem escrita real por padrão.
- Adicionar robô local de layout e fluxos, testes CSS focados e relatório verificável.
- Fechar as verificações pendentes de ambiente Windows e preparar o checklist operacional do Xano sem publicar nada.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `frontend-foundation`: cabeçalho único, hierarquia visual e layout responsivo por tema e perfil.
- `catalog`: catálogo público, grade, detalhe e apresentação das oito categorias.
- `cover-isbn`: prioridade de capas HTTPS, Open Library por ISBN e fallback gerado.
- `primary-journeys`: home, busca, reserva e navegação por perfil.
- `reservations`: abas e contadores consistentes para acompanhamento pelo estudante.

## Impact

- Frontend Reflex em `biblioteca_mais_nova/`.
- Scripts de seed e verificação em `scripts/`.
- Testes em `tests/`.
- Evidências em `docs/`.
- Nenhuma publicação ou alteração remota no Xano nesta Change.

## Nota de arquivamento

substituída por restaura-visual-v7
