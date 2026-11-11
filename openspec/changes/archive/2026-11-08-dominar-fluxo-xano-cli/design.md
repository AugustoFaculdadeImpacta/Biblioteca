# Design

## Context

A CLI instalada é `@xano/cli 1.3.4`. O workspace confirmado é `151966`, branch `v1` live. O pull de referência reportou 57 documentos remotos contra 41 arquivos locais; havia 11 tabelas e 36 endpoints remotos contra 9 tabelas e 28 endpoints locais, com diferenças de conteúdo. Essas divergências existentes não fazem parte desta Change.

A preferência consultada pelo CLI retornou `allow_push = false`. Por decisão do usuário, não foi alterada. O escopo final limita-se à prova já realizada de criação, alteração e remoção da tabela descartável `zz_teste_nota`, à documentação do fluxo e à limpeza local correspondente. O arquivo `xano/table/zz_teste_nota.xs` estava rastreado antes da prova, portanto sua remoção aparece como `D` no Git e não será ocultada por commit.

## Goals / Non-Goals

**Goals:**

- Documentar comandos reais de pull/push e os limites das operações destrutivas.
- Confirmar criação e alteração delimitada da tabela descartável e registrar sua exclusão individual pela Metadata API oficial.
- Confirmar a limpeza remota por GET/pull sem alterar os recursos existentes.
- Registrar evidências sanitizadas e validar estritamente os artefatos OpenSpec.

**Non-Goals:**

- Criar ou testar endpoints temporários, por HTTP real ou por qualquer outro transporte.
- Adicionar ou executar testes Reflex/pytest com `httpx.MockTransport`.
- Alterar `allow_push`, reconciliar divergências do workspace, fazer commit ou deploy.

## Decisions

### Limitar operações remotas

Usar somente workspace `151966`, branch `v1`, credencial local fora do repositório, e operações delimitadas. Não usar `push --delete --sync`; não modificar nenhuma das tabelas ou APIs preexistentes.

### Remover a tabela por ID confirmado

Consultar nome e ID pela Metadata API oficial antes do DELETE individual da tabela. A tabela foi identificada como `zz_teste_nota`, ID `912722`; confirmar sua ausência com GET 404 após a remoção e fazer pull somente de definições para verificar que não restaram recursos `zz_teste_*`.

### Não executar o ciclo de endpoints

Embora o plano inicial previsse endpoints públicos temporários, `allow_push = false` foi confirmado e o usuário decidiu encerrar a Change sem esse ciclo. Não alterar a preferência nem tentar uma alternativa não aprovada. Documentar como não executados a criação/chamada de endpoints, a validação de texto vazio, o teste pytest/MockTransport e o consumo pelo cliente Reflex.

## Risks / Trade-offs

- O ciclo de endpoints e cliente fica sem evidência; isso é uma limitação explícita, não uma validação simulada nem sucesso presumido.
- O arquivo de tabela de teste estava rastreado; removê-lo deixa uma exclusão no Git. Preservar essa evidência e não criar commit.
- Divergências preexistentes entre workspace remoto e Git permanecem fora desta Change.

## Verification

Evidências remotas registradas: GET da tabela `912722` confirmou nome/ID; DELETE individual retornou 200; GET posterior retornou 404. A busca GET de grupos não encontrou `zz_teste_*`; o pull de definições trouxe 57 documentos sem arquivos `zz_teste_*`. Localmente, o arquivo de teste foi removido; o único estado Git em `xano/` é a exclusão intencional desse arquivo.

## Migration Plan

Não há migração de produto. Validar `openspec validate --strict` e arquivar somente após registrar as evidências acima. Não fazer commit.
