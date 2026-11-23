# Proposal

## Why

O código local e os testes simulados já validam a maior parte do comportamento da biblioteca, mas as tarefas finais que dependem do Xano real, do painel do usuário e da limpeza de registros sintéticos continuam dispersas entre diversas Changes. Essa dispersão dificulta a revisão, porque combina responsabilidades diferentes: código local, publicação remota e operação manual em ambiente do usuário.

## What Changes

- Consolidar em uma única Change as tarefas ainda abertas que dependem do Xano real ou do usuário.
- manter o escopo restrito a validações remotas, promoção de perfil, limpeza de contas sintéticas, seed autorizado e publicação filtrada do arquivo Xano relevante.
- preservar a rastreabilidade para as tarefas originais, citando a Change de origem e o responsável de cada item.

## Capabilities

### New Capabilities

Nenhuma funcionalidade de produto nova. Este é um ajuste operacional de validação remota.

### Modified Capabilities

- `catalog`: validação e publicação remota do catálogo e da integração com os dados de produção.
- `loan-circulation`: verificação remota da elegibilidade, fila, devolução e rejeição de pedidos duplicados.
- `identity-session`: validação final de perfis `bibliotecario` e `admin` e da sessão autenticada.

## Impact

- Não altera a API local usada pela aplicação Reflex.
- Não exige alterações em `requirements.txt`, `.env`, `.mcp.json` ou `site-packages`.
- Reúne, em uma área explícita, o trabalho operacional ainda pendente no Xano real.
