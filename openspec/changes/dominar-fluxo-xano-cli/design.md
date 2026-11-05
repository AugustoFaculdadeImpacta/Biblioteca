# Design

## Context

Veja `proposal.md` para a motivação e o escopo. A CLI local é `@xano/cli 1.3.4`; `workspace pull` exporta documentos, `workspace push` aceita filtros `--include` (`-i`) e `--dry-run`, e `--delete` exige `--sync`, podendo remover objetos remotos omitidos do conjunto enviado. A credencial padrão `~/.xano/credentials.yaml` fica fora do repositório. A branch `v1` do workspace `151966` foi confirmada como live.

O pull de 2026-11-05 mostrou uma divergência preexistente: 11 tabelas e 36 endpoints remotos contra 9 tabelas e 28 endpoints locais; as nove tabelas correspondentes diferem em conteúdo, incluindo `auth = false` remoto em `titulo`; há recursos remotos de `Authentication` e `Event Logs` ausentes da árvore local. Esta Change não reconcilia esses estados nem inclui recursos existentes em pushes.

## Goals / Non-Goals

**Goals:**

- Fazer a prova ser auditável e repetível, preservando a cópia e o diff das definições antes de alterar o destino remoto.
- Limitar criação, atualização e exclusão a recursos temporários com prefixo `zz_teste_`.
- Validar a chamada da aplicação somente com transporte HTTP simulado.

**Non-Goals:**

- Recriar ou limpar o workspace, importar registros/env ou modificar qualquer recurso existente.
- Adicionar funcionalidade de produto ou interface Reflex, criar usuário de teste em qualquer tabela existente, fazer deploy ou commit.

## Decisions

### Não usar a exclusão global da CLI

`xano workspace push --sync --delete` não é uma remoção pontual: os objetos remotos ausentes do conjunto sincronizado podem ser apagados. O fluxo nunca usa essa combinação. A exclusão individual só será executada por uma operação oficial da Metadata API cuja rota e semântica tenham sido verificadas antes da escrita; se não houver alternativa segura compatível com o token no `.env`, a prova remota para sem alterações.

### Usar credenciais CLI fora do repositório

Usar a credencial padrão já existente em `~/.xano/credentials.yaml`, confirmada fora da raiz do projeto. Não imprimir seu conteúdo nem inseri-lo em arquivos, logs, documentação ou Git. O `.env` não precisa conter o token Metadata API. A CLI local é preferível a uma chamada HTTP manual para pull/push; exclusão individual só ocorre por um comando ou rota oficial cuja semântica pontual tenha sido comprovada.

### Revalidar destino e preservar estado antes de escrever

Antes do primeiro push, conferir `git status`, o perfil/destino que a CLI consegue expor sem revelar credenciais e a identidade do workspace/branch/ambiente por consulta oficial. O README local é apenas uma referência anterior, não prova do destino atual. Fazer pull/export apenas de definições (sem registros, variáveis ou segredos), guardar a referência fora de `xano/` e revisar `git diff -- xano/`; relatar divergências antes de qualquer push. Cada push deve usar inclusões explícitas `-i` restritas aos arquivos `zz_teste_*`, precedido por `--dry-run`. Se a prévia listar qualquer outro recurso, parar sem aplicar.

### Manter a reconciliação do workspace fora desta Change

A divergência entre Xano e Git é um achado, não uma autorização para importar ou sincronizar objetos existentes. Uma Change separada `reconciliar-xano-com-git` deverá comparar os arquivos e IDs de recursos, propor decisões para cada divergência e pedir revisão antes de qualquer sincronização do estado existente.

### Isolar endpoints públicos da prova

Por decisão explícita do usuário, os endpoints temporários GET e POST serão públicos, sem autenticação, apenas no grupo `zz_teste_*` e com operações limitadas à tabela descartável `zz_teste_nota`. O POST valida texto e grava somente nessa tabela; o GET lê somente dela. Não criar usuário em tabela existente, nem apontar endpoints a recursos da biblioteca. Fazer as chamadas reais assim que os endpoints forem publicados e remover endpoints, grupo e tabela no mesmo ciclo de trabalho. Como endpoints públicos podem receber chamadas de terceiros enquanto existirem, não deixar a prova pausada com esses recursos publicados: se um push, teste ou remoção falhar, interromper novas mudanças e priorizar a limpeza individual pela Metadata API, relatando recursos/IDs restantes.

### Isolar o teste Reflex

O teste pytest usa `httpx.MockTransport` com resposta determinística para a rota GET e verifica método, caminho e payload retornado. Ele não usa servidor Xano, token real ou POST de escrita. A produção não recebe um fluxo de gravação de teste.

## Risks / Trade-offs

- [A exclusão individual não está disponível por comando ou API oficial comprovada] → não usar `push --delete --sync`; parar antes da criação remota se a estratégia de limpeza não estiver estabelecida.
- [Perfil, branch ou ambiente não correspondem à biblioteca live autorizada] → não executar pull/push; confirmar o alvo com o usuário.
- [Endpoint público pode receber tráfego não previsto] → restringir grupo, métodos e consultas à tabela temporária, validar entradas no servidor, executar chamadas imediatamente e remover endpoints/grupo/tabela sem demora.
- [Falha ou incerteza em push/teste/remoção deixa recurso público ativo] → parar de ampliar o escopo e priorizar DELETE pontual por IDs obtidos por GET; não usar exclusão global e relatar qualquer recurso não removido.
- [Falha ou incerteza na limpeza] → não arquivar; parar imediatamente e relatar nomes/IDs ainda presentes.
- [Push inclui mais arquivos do que o esperado] → apresentar a prévia e revisar a lista antes de enviar; se qualquer recurso fora de `zz_teste_*` aparecer, parar; nunca usar `--sync`, `--delete`, `--records`, `--env` ou truncamento. `--force` só é permitido para o push delimitado cuja prévia exata foi revisada e contém exclusivamente recursos `zz_teste_*`.

## Migration Plan

Não há migração de produto. Após aprovação, validar a rota oficial de Metadata API, confirmar destino e guardar a referência de definições; criar e exercitar os recursos temporários; remover endpoints e tabela por operações pontuais; confirmar ausência por GET/404 e comparar `xano/` com o estado Git inicial. Só então concluir Verify e considerar Archive.
