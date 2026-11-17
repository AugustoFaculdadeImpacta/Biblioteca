# Mapa das Changes

Este documento resume o que cada Change entrega hoje, quais partes já têm evidência no código ou nos testes e quais itens ainda dependem do uso do Xano real ou do painel do usuário.

## Status geral

- Changes ativas: `validacao-remota-xano` e, quando necessário, `execucao-reflex-windows` para a correção local de execução.
- Changes arquivadas: as demais que já têm código local validado e com tarefas migradas para a validação remota.
- Regra: uma Change só é arquivada quando a parte local está entregue e a etapa remota foi movida para a validação consolidada.

## Change: execucao-reflex-windows

| Item | Observação |
|---|---|
| Finalidade | Garantir que `reflex run` funcione no Windows sem editar arquivos gerados ou `site-packages`. |
| Evidência local | `README.md`, `tasks.md` da Change, testes de configuração e compilação com `reflex compile --dry`. |
| Tarefas abertas | 1.3: corrigir a corrida `psutil.NoSuchProcess` somente no código do projeto, sem tocar em `.venv`. |
| Dono | Copilot local; o restante depende de um ambiente Windows estável. |
| Status | Ativa, sem solução segura confirmada no código do projeto. |

## Change: acervo-bibliotecario

| Item | Observação |
|---|---|
| Finalidade | Gerenciar acervo, títulos, categorias, exemplares e ações administrativas do bibliotecário. |
| Evidência local | `biblioteca_mais_nova/catalog.py`, `biblioteca_mais_nova/biblioteca_mais_nova.py`, testes de catálogo e administração. |
| Tarefas abertas | Conciliação remota, publicação, validação de concorrência e limpeza de dados sintéticos. |
| Dono | Copilot local para código; usuário para a operação remota com painel do Xano. |
| Status | Entregue localmente, com validação remota transferida para `validacao-remota-xano`. |

## Change: reserva-pelo-bibliotecario

| Item | Observação |
|---|---|
| Finalidade | Processar reservas, fila, retirada e recusa, validando regras de elegibilidade e FIFO. |
| Evidência local | `biblioteca_mais_nova/staff_reservations.py`, `biblioteca_mais_nova/circulation.py`, testes administrativos e de circulação. |
| Tarefas abertas | Publicação remota, prova de atomicidade FIFO, limpeza das contas sintéticas e revisão de regressões. |
| Dono | Copilot local para implementações; usuário Xano para publicação e limpeza. |
| Status | Entregue localmente, com validação remota transferida para `validacao-remota-xano`. |

## Change: perfil-admin-xano

| Item | Observação |
|---|---|
| Finalidade | Definir perfis de admin/bibliotecário, regras de autenticação e acesso administrativo. |
| Evidência local | `biblioteca_mais_nova/user_admin.py`, `biblioteca_mais_nova/biblioteca_mais_nova.py`, testes de perfil e sessão. |
| Tarefas abertas | Publicação do schema/perfil, validação de acesso e confirmação do destino do Xano. |
| Dono | Copilot local para código; usuário para ajuste final e limpeza do painel. |
| Status | Entregue localmente, com validação remota transferida para `validacao-remota-xano`. |

## Change: devolvido-em-nulavel

| Item | Observação |
|---|---|
| Finalidade | Confirmar se o campo `devolvido_em` em empréstimos deve aceitar nulo, zero ou datas. |
| Evidência local | Cadastro e regras de empréstimo em `biblioteca_mais_nova/circulation.py`; ausência de prova remota. |
| Tarefas abertas | Validar schema do Xano real, confirmar modelo de dados e publicar/dry-run só quando o destino estiver claro. |
| Dono | Copilot local para a análise e comparação; usuário do Xano para a mudança e possíveis exclusões. |
| Status | Bloqueada, sem mudança remota aprovada nem autorização para apagar dados. |

## Change: validacao-remota-xano

| Item | Observação |
|---|---|
| Finalidade | Consolidar somente as tarefas remotas que dependem do Xano live, do painel do usuário ou da limpeza de registros sintéticos. |
| Evidência local | Esta Change contém apenas a proposta e a lista de tarefas remotas; não duplica specs já consolidadas. |
| Tarefas abertas | Destino, dry-run filtrado, seed controlado, promoção de perfil, limpeza manual e verificação final. |
| Dono | Usuário no painel Xano e Copilot local para documentação e validação. |
| Status | Ativa e consolidada como fila de trabalho remota. |

## Como ler a árvore de trabalho

1. Comece por [README.md](../README.md) para a visão geral do projeto.
2. Consulte este arquivo para saber o que já está entregue localmente e o que ainda depende do Xano real.
3. Entre em `openspec/changes/` para revisar a proposta e as tarefas de uma mudança específica.
4. Só use `openspec/specs/` como fonte de verdade do comportamento já validado e consolidado.
5. O passo remoto nunca deve ser inferido como concluído sem login/painel confirmado e verificação HTTP real.
