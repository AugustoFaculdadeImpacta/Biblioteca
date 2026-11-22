# Design

## Context

O frontend concentra tema, navegação, cards e estilos em `biblioteca_mais_nova/biblioteca_mais_nova.py`, com testes em `tests/`. O Acervo hoje monta formulários para os títulos carregados e usa ações administrativas ligadas a chamadas existentes. O catálogo já possui endpoints locais e tipos TypedDict que podem receber um campo extra de capa gerada sem ampliar o contrato Xano.

## Goals / Non-Goals

**Goals:**
- Separar gerações de aparência compartilhada em estilos, componentes e utilitário puro.
- Tornar estados assíncronos visíveis e impedir repetição de escrita.
- Gerar capas determinísticas e usar o mesmo campo derivado em todas as apresentações.
- Tornar o Acervo compacto, com somente um painel de edição aberto.
- Preparar seed seguro e documentar a publicação necessária no Xano.

**Non-Goals:**
- Não alterar endpoints ou payload Xano existentes.
- Não executar operações remotas nem escrever no Xano real.
- Não baixar fontes, ícones ou imagens.
- Não usar navegador ou capturas.

## Decisions

- Usar tokens CSS existentes para primários, campos, texto e fundo; o modo escuro terá primários claros com texto escuro.
- Implementar o tema efetivo em uma única leitura do localStorage mais `matchMedia`, mantendo o script atual antes da pintura.
- Criar `covers.py` com hash estável, SVG URL-encoded e sem referências externas; adicionar `capa_gerada` aos itens de exibição derivados, nunca ao payload enviado ao Xano.
- Transformar o Acervo em rows reativas com busca em memória e edição por `titulo_id` selecionado; manter o formulário fechado até novo título ou edição.
- Centralizar mensagens administrativas no cliente em estados por operação; mapear 404, 403 e erros de transporte para texto simples.
- Preparar `scripts/seed_catalogo_real.py` como CLI com dry-run, `--apply`, variáveis de ambiente e clientes existentes.
- Usar pull temporário do Xano somente para comparar definições, sem registros ou escrita.

## Risks / Trade-offs

- [Endpoints administrativos não publicados] → registrar método, caminho e arquivo Xano pendente, sem marcar concluído.
- [Falha remota deixa estado incerto] → não assumir sucesso e pedir conferência antes de repetir.
- [Animações atrapalham leitura] → apenas transições curtas, reduções por mídia/classe e sem loop rápido.
- [Hash não gera todos os motivos igualmente] → usar pelo menos oito motivos e teste por lista de 30 títulos.

## Migration Plan

Aplicar alterações em lote por tarefa com commit, repetir compilação e testes após cada commit, registrar hashes nos tasks e no relatório, sincronizar a spec consolidada e arquivar a Change após todas as tarefas.
