# Proposal

## Why

A avaliação documentada da prova Reflex recomenda sua adoção, mas os documentos globais ainda tratam o framework como candidato. A decisão precisa ser registrada de forma consistente, preservando as condições da avaliação antes de iniciar funcionalidades de produto ou qualquer deploy.

## What Changes

- Registrar Reflex como tecnologia adotada e exclusiva para o frontend, sem introduzir outra tecnologia de frontend sem mudança arquitetural aprovada.
- Atualizar `docs/project-overview.md`, `openspec/config.yaml` e `AGENTS.md` para refletir a decisão.
- Manter explícito que a adoção não autoriza implementar funcionalidades nem fazer deploy antes de cumprir as duas mitigações: indicador visual `:focus-visible` na busca e escolha/validação do ambiente acadêmico, com segredos somente no backend e inspeção de logs.
- Não criar interface, ambiente virtual ou integração com Xano nesta Change.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. Esta Change altera somente contexto e documentação; não muda requisitos comportamentais do sistema. O arquivo `.openspec.yaml` desta Change declara `skip_specs: true`.

## Impact

- Documentação/contexto: `docs/project-overview.md`, `openspec/config.yaml` e `AGENTS.md`.
- Nenhuma alteração em código de produto, dependências, API, Xano ou na Change ativa `verificacao-avancada-circulacao`.
