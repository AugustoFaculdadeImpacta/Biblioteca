# Instruções para agentes de IA

## Idioma e decisões

- Toda a documentação, interface, mensagens e comentários do projeto devem usar português do Brasil.
- Trate `docs/project-overview.md` como visão global e `docs/domain-model.md` como modelo conceitual. Não os transforme em especificações de telas, endpoints ou tabelas.
- O projeto está sendo reconstruído do zero em `biblioteca-mais-nova`. `biblioteca-nova` é somente referência; não copie seu modelo de dados ou seus contratos Xano sem nova verificação.
- O backend será Xano. Reflex é a tecnologia adotada e exclusiva do frontend; qualquer outra tecnologia de frontend exige mudança arquitetural aprovada.
- Mitigação 1 cumprida: `:focus-visible` está implementado na busca e coberto por `tests/test_catalog.py`; a verificação Playwright está registrada em `openspec/changes/archive/2026-11-10-catalogo-publico/tasks.md`. A adoção do Reflex não autoriza deploy até que o ambiente acadêmico seja escolhido e validado, segredos permaneçam somente no backend e os logs sejam inspecionados.
- Não introduza estrutura de banco separada da funcionalidade. Em cada Change vertical, especifique e implemente somente os dados, regras de servidor, API e interface necessários àquela capability.

## Fluxo obrigatório de trabalho

1. **Explore:** investigar e discutir. Não escrever código, não criar ou alterar arquivos, não criar Changes e não executar operações no Xano.
2. **Propose:** após o usuário pedir explicitamente, gerar os artefatos OpenSpec para uma Change delimitada: `proposal.md`, `specs/<capability>/spec.md`, `design.md` quando necessário e `tasks.md`. Não implementar.
3. **Review:** parar e aguardar a revisão/aprovação humana dos artefatos antes de Apply. Não inferir aprovação pelo silêncio ou por respostas a perguntas de domínio.
4. **Apply:** implementar somente as tarefas aprovadas da Change atual. Se o escopo ou uma regra mudar, atualizar a Change e voltar à revisão antes de continuar.
5. **Verify:** comparar a implementação com todos os cenários e tarefas, executar as verificações locais adequadas e registrar evidências reais. Diferenciar validação local, simulada e sandbox; nunca alegar que uma verificação ocorreu se não ocorreu.
6. **Archive:** somente depois de todas as tarefas concluídas e Verify aprovado, arquivar a Change usando o OpenSpec. O Archive consolida os deltas em `openspec/specs/` e move a Change para `openspec/changes/archive/`. Não deixe Changes concluídas na pasta ativa `openspec/changes/`; não arquive trabalho incompleto.

Mantenha `openspec/changes/` apenas para trabalho em andamento. As specs consolidadas em `openspec/specs/` são a fonte de verdade do comportamento já implementado.

## Xano: autorização e cuidados operacionais

O usuário autorizou reconstruir integralmente o workspace Xano do projeto, inclusive excluir tabelas existentes e recriá-las. Considere os dados e schemas anteriores descartáveis **dentro do workspace selecionado para esta reconstrução**. Essa autorização não deve ser confundida com autorização para operar em qualquer workspace da conta.

- Não acesse nem altere o Xano em Explore ou Propose.
- Antes da primeira operação remota em Apply, identifique pelo Xano CLI o workspace, branch e ambiente selecionados e registre essa identificação na Change. Se houver mais de um destino plausível, ou se não for possível confirmar que é o workspace da biblioteca escolar, pare e peça esclarecimento.
- O escopo da Change aprovada deve mencionar claramente o reset/recriação Xano. Não solicite nova aprovação para apagar as tabelas antigas quando o alvo correto e a operação estiverem explicitamente documentados na Change aprovada.
- Preserve uma cópia local de referência do estado atual via pull somente leitura antes da reconstrução. Revise `git status` e o diff dos arquivos Xano antes de sincronizar. Use sandbox/branch de desenvolvimento quando disponível.
- Use Xano Developer MCP para consultar documentação e validar XanoScript; use Xano CLI para conectar/sincronizar com o workspace. Não confunda os dois.
- Nunca registre tokens, senhas ou segredos no repositório. Não envie push para Xano antes de revisar o destino e o diff.

## Reflex e configuração local

- Reflex é adotado exclusivamente para o frontend. Qualquer outra tecnologia de frontend exige mudança arquitetural aprovada.
- Mitigação 1 cumprida: `:focus-visible` na busca foi implementado e verificado. A adoção do Reflex não autoriza deploy antes de validar o ambiente acadêmico, manter segredos somente no backend e inspecionar os logs.
- Cumprir o Apêndice B do curso e as instruções de setup antes de editar ou executar código; manter uma única estratégia de ambiente/dependências e consultar documentação/skills oficiais atuais.
- Não instalar dependências, iniciar processos ou executar comandos com efeito remoto sem relação com tarefas aprovadas.

## Segurança e consistência do domínio

- O catálogo é público; operações requerem autenticação. Operações administrativas exigem perfil bibliotecário, validadas no backend e não apenas ocultadas na interface.
- Revalidar no servidor disponibilidade, limite de empréstimo, atraso, elegibilidade da reserva e posição na fila para proteger operações concorrentes.
- Não inventar campos, endpoints, regras ou decisões pendentes. Registrar alternativas e pedir decisão quando forem necessárias para avançar.
