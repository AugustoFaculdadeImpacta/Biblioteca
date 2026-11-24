# Design

## Context

Ver [proposal.md](./proposal.md) e os contratos em `specs/`. O cliente compartilha transporte Xano, mas as telas autenticadas convertem listas para modelos próprios. O diagnóstico deve respeitar as permissões já validadas no backend e não persistir resultados.

## Goals / Non-Goals

**Goals:**
- Aceitar variações compatíveis de envelope e valores sem enfraquecer as permissões nem os campos identificadores necessários.
- Separar a confirmação HTTP de uma escrita da leitura opcional de seu corpo.
- Produzir um relatório útil para comparar contratos sem copiar valores pessoais.

**Non-Goals:**
- Alterar endpoints, permissões, modelos de dados ou contratos remotos.
- Escrever no Xano, sincronizar definições de volta ou mudar o layout aprovado.

## Decisions

- Fazer a extração do envelope e as conversões escalares na fronteira comum de leitura; manter a validação de campos por modelo e isolar a rejeição a cada registro, agregando a contagem para a interface.
- Tratar status 2xx como resultado da escrita independentemente da legibilidade do corpo. A rotina chamadora apresenta aviso e atualiza suas listas; a política global continua sem retry automático de POST/PATCH.
- Gerar o diagnóstico a partir das operações GET já existentes, com seleção por perfil no servidor. Usar a sessão corrente; a lista de contas bibliotecárias fica restrita ao admin. Remover valores antes de montar linhas e texto copiável.
- No Apply, confirmar com Xano CLI o workspace, branch e ambiente selecionados antes de qualquer operação remota e registrar a identificação aprovada na Change. Fazer pull de definições somente para diretório temporário fora do repositório, nunca sincronizar de volta. Se o destino não for inequívoco, parar.
- Comparar as chamadas descobertas no código com as definições puxadas e registrar diferenças, autenticação/perfil, entradas, campos exigidos e decisão de publicação em `docs/xano-diferencas.md`.

## Risks / Trade-offs

- [Conversão permissiva mascara incompatibilidades] → campos identificadores permanecem obrigatórios; outros registros inválidos são contados e o relatório diagnóstico mantém os nomes dos campos problemáticos.
- [Resposta ilegível após escrita confirmada] → não repetir a escrita; mostrar aviso e atualizar a lista antes de liberar nova tentativa.
- [Relatório expõe dados pessoais] → coletar e exibir somente status, tempos, nomes de chaves, tipos e motivos de validação; não registrar valores nem persistir o relatório.
- [Destino Xano ambíguo] → não executar pull até confirmar workspace, branch e ambiente pelo CLI.

## Migration Plan

Não há migração de dados. Após revisão e Apply, validar localmente com testes simulados, `reflex compile --dry` e pytest em sequência. O pull remoto é somente leitura; não há publicação ou deploy nesta Change.
