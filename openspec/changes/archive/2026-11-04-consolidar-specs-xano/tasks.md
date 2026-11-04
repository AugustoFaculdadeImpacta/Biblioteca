# Tasks

## 1. Confirmar fidelidade das fontes

- [x] 1.1 Comparar byte a byte cada uma das cinco specs desta Change com sua delta arquivada correspondente e confirmar que os 18 requisitos e seus cenários foram preservados.
- [x] 1.2 Conferir que `docs/`, `xano/` e `openspec/changes/verificacao-avancada-circulacao/` não foram alterados por esta Change, usando `git status` e diff dos caminhos.

## 2. Validar preparação para consolidação

- [x] 2.1 Executar `openspec validate "consolidar-specs-xano" --strict` e corrigir somente problemas estruturais nos artefatos desta Change, sem reescrever requisitos.
- [x] 2.2 Conferir `openspec status --change "consolidar-specs-xano"` e confirmar que proposal, specs, design e tasks estão completos antes de Review.

## Workflow follow-up

- Arquivar somente após Apply e Verify aprovados explicitamente; no Archive, escolher sincronizar agora para criar as cinco specs principais.
- Após a sincronização, comparar os 18 requisitos e cenários em `openspec/specs/` com as deltas arquivadas e registrar qualquer divergência antes de concluir o Archive.
