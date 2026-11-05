# Design

## Context

Consulte [proposal.md](./proposal.md) para a motivação. O pull de referência anterior foi feito na branch live `v1` do workspace `151966` com a CLI Xano 1.3.4 e continha apenas definições publicadas. O checkout tem 9 tabelas e 28 endpoints; o pull observado tinha 11 tabelas e 36 endpoints, incluindo recursos adicionais de `Authentication` e `Event Logs`. As nove tabelas correspondentes divergiam, inclusive `titulo` (`auth = false` no remoto).

## Goals / Non-Goals

**Goals:**

- Fazer um inventário reproduzível das diferenças remotas/locais por recurso.
- Versionar as definições aprovadas do Xano remoto sem misturar dados, variáveis, drafts ou segredos.
- Manter o Xano remoto inalterado durante toda a Change.

**Non-Goals:**

- Enviar arquivos ao Xano, alterar permissões, dados, variáveis ou branch.
- Presumir que diferenças locais devem ser descartadas sem revisão.
- Decidir regras de domínio ou alterar requisitos de produto.

## Decisions

### Usar o pull de definições do CLI para uma pasta temporária

Confirmar novamente workspace, branch e ambiente pela CLI antes do pull. Usar `workspace pull` sem `--records`, `--env`, `--draft` ou `--sync-state`, com destino fora de `xano/` e fora da árvore versionada. O pull do CLI é preferível a reconstruir definições por chamadas Metadata API porque fornece uma cópia consistente dos documentos XanoScript; a Metadata API continua útil apenas para consultas pontuais de metadados.

### Comparar por recurso e preservar todas as versões até a decisão

Gerar inventário dos arquivos locais e do pull, revisar diffs por tabela, grupo e endpoint e separar três casos: divergências de recursos correspondentes, recursos somente remotos e recursos somente locais. Não copiar o pull inteiro por cima de `xano/`. Para cada diferença, incorporar a definição remota ao Git somente após inspecionar seu conteúdo e confirmar que não contém dados ou segredos; preservar a versão local em Git para que as mudanças sejam revisáveis. Se o conteúdo indicar comportamento inesperado ou não for seguro versionar, pausar para decisão em vez de omitir ou normalizar silenciosamente.

Alternativas consideradas: confiar integralmente no checkout local manteria o drift; substituir a árvore local pelo pull integral poderia apagar definições locais ou introduzir conteúdo não revisado. A comparação por recurso reduz ambos os riscos.

### Tornar a sincronização unidirecional e local

O fluxo é exclusivamente Xano → pasta temporária → revisão → Git local. Não executar `workspace push`, `--sync`, `--delete`, nem qualquer operação de escrita remota. Não fazer commit automático. Isso evita que a Change de alinhamento local cause alterações involuntárias no workspace live.

### Não criar specs de produto

Esta Change modifica somente arquivos de infraestrutura versionados, sem alterar comportamento do catálogo, autenticação ou circulação; portanto `.openspec.yaml` declara `skip_specs: true`.

## Risks / Trade-offs

- [O workspace ou branch pode ter mudado desde a leitura anterior] → confirmar destino e branch novamente e registrar o novo resultado antes de comparar.
- [Definições remotas podem conter valores sensíveis ou implementação ainda não revisada] → inspecionar o diff antes de copiar; nunca versionar registros, variáveis, tokens ou segredos; interromper em caso de dúvida.
- [Diferenças locais podem conter trabalho válido não existente no remoto] → manter o checkout intacto até revisão por recurso e não substituir arquivos em lote.
- [O conjunto remoto pode mudar entre pull e revisão] → tratar o pull salvo como snapshot desta Change e não aplicar uma segunda cópia sem registrar e revisar as diferenças.

## Migration Plan

Não há migração ou escrita remota. Fazer o pull para fora de `xano/`, inventariar e revisar os diffs, incorporar ao Git apenas as definições explicitamente aprovadas, executar as verificações locais disponíveis e validar que nenhum comando de push foi usado. Se a reconciliação local precisar ser desfeita, restaurar somente os arquivos adicionados ou alterados por esta Change usando o diff revisado; não reverter alterações preexistentes.
