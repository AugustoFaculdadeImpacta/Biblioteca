# Proposal

## Why

O workspace live trata `emprestimo.devolvido_em` como `nullable=false` e retorna `0` para empréstimos ainda ativos, embora o contrato local o declare opcional. O sentinel `null || 0` corrigiu os bloqueios de circulação, mas mantém uma diferença entre o modelo desejado e o schema efetivo; esta Change primeiro provará a nulabilidade em uma tabela descartável e só então migrará a tabela produtiva.

## What Changes

- Provar em `zz_teste_nota`, por push delimitado, leitura do schema e POST/GET de registro, que um campo timestamp nulável mantém `null`; remover a fixture e confirmar GET 404.
- Somente se a prova passar, atualizar `emprestimo.devolvido_em` para nullable e verificar o schema e um registro com valor null, limpando todas as fixtures.
- Substituir comparações `devolvido_em == null || devolvido_em == 0` por `devolvido_em == null` nos sete endpoints que atualmente contêm o sentinel.
- Verificar `fila_GET` como o oitavo endpoint relacionado da Change anterior; ele não consulta `devolvido_em` e não precisa de alteração por sentinel.
- Reexecutar, um cenário de cada vez, atraso, limite e FIFO, com limpeza confirmada por GET 404 e contagens finais `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0`, `usuario=2`.
- Atualizar `xano/README.md` e registrar evidências sanitizadas.
- Se a prova descartável não demonstrar nulabilidade persistente, não alterar `emprestimo` nem os endpoints; manter o sentinel como solução atual, documentar o limite e parar para reporte, sem arquivar como concluída.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A Change corrige a representação persistida de uma devolução não registrada para corresponder ao significado já definido nas specs; não altera comportamento observável. `.openspec.yaml` declara `skip_specs: true`.

## Impact

- Xano: definição da tabela `emprestimo` e sete endpoints de circulação; o endpoint de consulta da fila não contém o sentinel.
- A tabela e o registro de prova `zz_teste_nota` são descartáveis e devem ser removidos antes de tocar na tabela produtiva.
- Workspace de Apply esperado: `151966`, branch live `v1`, sujeito a confirmação pelo Xano CLI antes da primeira operação remota.
- Verificação: schema Metadata API, persistência de null, testes estruturais e cenários de circulação.
- Nenhum endpoint ou contrato HTTP novo; sem alteração no frontend, sem push amplo, sem segredo em arquivos/saídas e sem commit Git.
