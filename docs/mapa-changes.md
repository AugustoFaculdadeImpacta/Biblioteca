# Mapa das Changes

Este documento resume o estado atual das Changes e separa o trabalho local das pendências que dependem do Xano real ou do operador.

## Status geral

- Changes ativas: `validacao-remota-xano` e `execucao-reflex-windows`.
- Changes arquivadas nesta rodada: `acervo-bibliotecario`, `reserva-pelo-bibliotecario`, `perfil-admin-xano` e `devolvido-em-nulavel`.
- As tarefas remotas de acervo, reservas e perfil foram transferidas, sem serem marcadas como concluídas, para `validacao-remota-xano`.

## Change: validacao-remota-xano

| Item | Observação |
|---|---|
| Finalidade | Consolidar validações e operações que dependem do Xano real, do painel do operador ou de dados de teste remotos. |
| Evidência local | A lista `tasks.md` reúne as tarefas remotas originais e sete tarefas transferidas de acervo, reservas e perfil. |
| Tarefas abertas | 22/22; nenhuma foi marcada como concluída. |
| Dono | Operador do Xano para ações no painel e validações remotas; Copilot local para suporte seguro e evidências. |
| Status | Ativa. |

## Change: execucao-reflex-windows

| Item | Observação |
|---|---|
| Finalidade | Garantir a execução do `reflex run` no Windows sem editar arquivos gerados ou `site-packages`. |
| Evidência local | README, testes de configuração e compilação com `reflex compile --dry`. |
| Tarefas abertas | 1.3, corrida `psutil.NoSuchProcess`; não foi identificada correção segura no código do projeto. |
| Dono | Copilot local, condicionado a uma solução segura e reproduzível no código do projeto. |
| Status | Ativa, 6/7 tarefas concluídas. |

## Changes arquivadas

### acervo-bibliotecario

Implementação local concluída; as tarefas remotas pendentes foram transferidas para `validacao-remota-xano`. Os deltas foram comparados com as specs consolidadas (32 requisitos verificados no conjunto das Changes; nenhuma divergência) e as specs estritas passaram após o archive.

### reserva-pelo-bibliotecario

Implementação local concluída; as tarefas remotas pendentes foram transferidas para `validacao-remota-xano`. Os deltas foram comparados com as specs consolidadas e a validação estrita passou após o archive.

### perfil-admin-xano

Implementação local concluída; as tarefas remotas pendentes foram transferidas para `validacao-remota-xano`. Os deltas foram comparados com as specs consolidadas e a validação estrita passou após o archive.

### devolvido-em-nulavel

Arquivada sem sincronização de specs. O pull somente de definições do Xano mostrou `devolvido_em` como nullable, igual ao schema local; o código consumidor já aceita `None` e `0`. Não foram lidos registros, portanto o resultado não afirma nada sobre valores armazenados. A proposta não precisava de mudança de comportamento; as 20 tarefas originais permanecem desmarcadas e a razão está registrada na Change arquivada.

## Referências

1. Consulte [README.md](../README.md) para a visão geral e instruções de execução.
2. Use `openspec/changes/` para as duas Changes ativas.
3. Use `openspec/specs/` como fonte de verdade do comportamento consolidado.
4. Não considere uma tarefa remota concluída sem evidência do ambiente Xano correspondente.
