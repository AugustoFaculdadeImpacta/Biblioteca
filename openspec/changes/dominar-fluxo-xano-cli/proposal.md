# Proposal

## Why

Precisamos comprovar um fluxo reproduzível para inspecionar, criar, alterar e remover recursos Xano sem afetar as nove tabelas e os 28 endpoints já versionados. A prova deve usar as credenciais padrão locais da CLI fora do repositório, apresentar a prévia delimitada antes de cada push e deixar o workspace e o Git sem recursos de teste ao final.

## What Changes

- Documentar em `docs/xano-workflow.md` a ajuda real da CLI instalada, os comandos de pull/push e seus limites, a comparação com o estado Git e o procedimento seguro para criar uma tabela e endpoints e consumi-los no Reflex.
- Antes da primeira operação remota, confirmar que o destino é o workspace `151966` da biblioteca e identificar branch e ambiente; fazer pull somente de definições e comparar com Git, sem importar registros, variáveis ou segredos.
- Criar, modificar, chamar e remover apenas os recursos descartáveis `zz_teste_*`. A exclusão será pontual; `push --sync --delete` e qualquer operação que possa remover recursos fora desse prefixo ficam proibidos.
- Adicionar um teste pytest de leitura com `httpx.MockTransport`, usando o padrão de `xano_client.py`; o teste do app não fará escrita real.
- Usar a credencial padrão da CLI em `~/.xano/credentials.yaml`, fora do repositório; não exibir nem copiar o conteúdo para Git, logs ou documentação. O `.env` não precisa conter token Metadata API.
- Antes do primeiro push, fazer pull e revisar `git diff` em `xano/`; relatar divergências. Fazer push somente com `-i` para os arquivos temporários `zz_teste_*`, sempre após `--dry-run`; se a prévia de qualquer push listar algo fora do prefixo, parar.
- Remover somente recursos `zz_teste_*` por operações pontuais. Nunca usar `push --delete --sync`; qualquer outro método de exclusão precisa estar documentado oficialmente e comprovar escopo individual antes da execução.
- Não modificar as nove tabelas ou 28 APIs existentes, não fazer commit ou deploy e não arquivar até confirmar que os recursos descartáveis sumiram e que `xano/` voltou ao estado Git inicial. A divergência preexistente do restante do workspace será tratada em Change separada, com revisão própria antes de sincronizar.

## Capabilities

### New Capabilities

Nenhuma. A Change trata de documentação e validação de fluxo de desenvolvimento com recursos temporários, sem introduzir comportamento durável no produto. `skip_specs: true` está declarado em `.openspec.yaml`.

### Modified Capabilities

Nenhuma.

## Impact

- Xano live: somente recursos com prefixo `zz_teste_` no workspace `151966`, após confirmação do destino e das operações delimitadas.
- Repositório: `docs/xano-workflow.md`, `.env.example`, arquivos temporários sob `xano/`, um módulo de teste do Reflex e testes pytest.
- Segurança: nenhum token, registro ou dado de teste em logs, arquivos versionados, resultados ou commits.
