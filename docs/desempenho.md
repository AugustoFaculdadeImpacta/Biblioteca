# Desempenho

Medição local simulada com `BIBLIOTECA_DEMO_LATENCIA_MS=1000` e
`BIBLIOTECA_DIAGNOSTICO=1`. O servidor de demonstração recebeu três leituras
paralelas por abertura: títulos, categorias e configurações. A resposta de
configurações foi habilitada pelo adaptador local do ensaio; não houve chamada
ao Xano real.

| Cenário | Até os livros aparecerem | Atualização em segundo plano | Chamadas |
|---|---:|---:|---:|
| Antes, sem cópia salva | 1451,3 ms | 1451,3 ms | 3 |
| Depois, com cópia salva | 3,5 ms | 1264,4 ms | 3 |

O diagnóstico terminal registrou 3 chamadas sem falhas; a duração do evento de
atualização foi 1448 ms com cópia e 1581 ms sem cópia. A diferença inclui a
latência do servidor local, o limitador e a instrumentação; não representa
desempenho do Xano de produção.

Para repetir no servidor local, defina `BIBLIOTECA_DEMO_LATENCIA_MS=1000`.
Use `0` ou remova a variável para desativar a espera artificial.
