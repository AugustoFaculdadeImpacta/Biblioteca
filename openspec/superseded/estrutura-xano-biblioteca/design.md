# Design

## Context

Consulte `proposal.md` para motivação e `specs/identity-session/spec.md` para o contrato observável. A avaliação documentada recomenda Reflex (11/14, com mitigação de foco visual); o mock da avaliação não é código de produto nem valida integração real com Xano.

Em 2026-10-27, uma consulta somente de leitura confirmou workspace `151966` (`Augusto's Workspace`), host `x8ki-letl-twmt.n7.xano.io`, branch `v1` com `live: true` e `allow_push: false`. Pull explicitamente dessa branch trouxe 35 documentos de definição: quatro documentos de tabela (`categorias`, `emprestimo`, `livro`, `usuario`), 24 documentos de API, três funções Quick Start, um addon, dois objetos de IA e uma definição de workspace. O pull não incluiu registros nem variáveis de ambiente. O destino não está vazio no estado consultado; esta leitura não confirma se algum reset foi executado. Esta enumeração é somente o estado atual encontrado; não fornece o modelo-alvo e não autoriza edição, exclusão ou reconstrução de qualquer recurso listado.

Manifesto observado no pull, para registrar o estado encontrado e não como modelo da biblioteca:

- Tabelas: `table/categorias.xs`, `table/emprestimo.xs`, `table/livro.xs`, `table/usuario.xs`.
- APIs: `api/default/default.xs`, `api/default/categorias_GET.xs`, `api/default/categorias_POST.xs`, `api/default/categorias/categorias_id_DELETE.xs`, `api/default/categorias/categorias_id_GET.xs`, `api/default/categorias/categorias_id_PATCH.xs`, `api/default/categorias/categorias_id_PUT.xs`, `api/default/emprestimo_GET.xs`, `api/default/emprestimo_POST.xs`, `api/default/emprestimo/emprestimo_id_DELETE.xs`, `api/default/emprestimo/emprestimo_id_GET.xs`, `api/default/emprestimo/emprestimo_id_PATCH.xs`, `api/default/emprestimo/emprestimo_id_PUT.xs`, `api/default/livro_GET.xs`, `api/default/livro_POST.xs`, `api/default/livro/livro_id_DELETE.xs`, `api/default/livro/livro_id_GET.xs`, `api/default/livro/livro_id_PATCH.xs`, `api/default/livro/livro_id_PUT.xs`, `api/default/auth/login_POST.xs`, `api/default/auth/me_GET.xs`, `api/default/auth/signup_POST.xs`, `api/event_logs/event_logs.xs`, `api/event_logs/logs/user/my_events_GET.xs`.
- Funções: `function/quick_start/enforce_role.xs`, `function/quick_start/generate_magic_link.xs`, `function/quick_start/log_event.xs`.
- Outros: `addon/user.xs`, `ai/agent/xano_example_agent.xs`, `ai/tool/search_xano_docs.xs`, `workspace/augustos_workspace.xs`.

O repositório contém apenas candidatos locais de Xano para identidade e uma prova Reflex simulada. Nenhum deles será usado como fonte de schema ou contrato greenfield. O modelo-alvo desta Change deriva dos requisitos aprovados e do modelo conceitual em `docs/domain-model.md`.

## Goals / Non-Goals

**Goals:**

- Entregar a primeira fatia vertical de identidade: estrutura mínima da conta, autenticação nativa Xano, contratos de cadastro/login/perfil e a conexão Reflex correspondente.
- Preservar os contratos aprovados: e-mail e senha, cadastro imediato de estudante, perfil não controlável pelo cliente, credencial privada no backend e logout local.
- Preparar uma sequência segura e verificável para o primeiro Apply, sem tratar o workspace observado como vazio.

**Non-Goals:**

- Criar ou alterar qualquer recurso Xano no Propose.
- Reutilizar, sincronizar, adaptar, remover ou substituir definições que já existem no destino observado. Se elas continuarem presentes no destino de Apply, esta Change para antes de escrever.
- Criar agora estruturas ou endpoints de catálogo, categorias, exemplares, empréstimos, reservas ou condições de exemplares.
- Implementar confirmação de matrícula/e-mail, SSO, recuperação de conta, promoção pública, revogação remota de sessão ou deploy.

## Decisions

### Evoluir verticalmente a identidade, não criar o banco inteiro

Esta Change cobre somente identidade e sessão ponta a ponta. Sua única entidade persistida proposta é uma conta autenticável, com identificador, e-mail único, credencial de senha tratada pelo mecanismo nativo e perfil restrito a `estudante` ou `bibliotecario`. A implementação confirmará os nomes e tipos físicos suportados pelo Xano antes de qualquer escrita. Não acrescentar nome, matrícula, telefone ou outros dados sem requisito aprovado.

**Alternativa considerada:** criar de uma vez todas as tabelas conceituais do domínio. Rejeitada porque o projeto exige que dados, regras e API evoluam junto de cada capability vertical.

Para Changes posteriores, o domínio conceitual aponta para capacidades que poderão exigir título, categoria e associação entre títulos e categorias, exemplar físico, solicitação de empréstimo, empréstimo confirmado, reserva, oportunidade de retirada e registro de condição. Esses conceitos são um roteiro de dependências, não schemas aprovados por esta Change. Cada Change futura deverá decidir os campos e contratos necessários à sua própria fatia.

### Usar autenticação nativa Xano, condicionada à confirmação no Apply

O contrato funcional exige cadastro, login e consulta da identidade autenticada. Durante Apply, confirmar na documentação oficial e no destino limpo como a autenticação nativa trata e-mail/senha, unicidade, emissão imediata de sessão, leitura do perfil autenticado e expiração. Não fixar nomes de endpoints Xano, formatos de token, refresh, revogação ou códigos de erro sem evidência do mecanismo suportado. Se a autenticação nativa não satisfizer o contrato, interromper antes de escrever e devolver a decisão à revisão.

**Alternativa considerada:** implementar manualmente emissão e validação de tokens. Rejeitada por duplicar o provedor de identidade sem necessidade comprovada e por aumentar o risco de segurança.

O contrato lógico entre Reflex e Xano contém as operações de cadastro (`email`, `senha`), login (`email`, `senha`) e identidade atual. O retorno visível à aplicação é limitado ao identificador público, e-mail e perfil. A resposta nativa que contém a credencial permanece no backend Reflex. A correspondência com caminhos, payloads, headers e respostas físicos do Xano será documentada somente após confirmação no Apply.

O lado Reflex oferece os fluxos equivalentes de cadastro, login, consulta da sessão e logout local. A interface do navegador chama apenas o backend Reflex. O logout limpa a sessão privada local; não se presume que isso revogue um token ainda válido no Xano.

### Perfil confiável e bootstrap manual

O perfil de estudante é definido pelo servidor em todo autocadastro; qualquer papel recebido do cliente é ignorado ou rejeitado. Não existe operação pública de promoção. A conta inicial de bibliotecário é criada manualmente por operador somente após confirmar workspace e branch autorizados; esta Change não cria endpoint administrativo de promoção. A autorização de ações administrativas reais será especificada e testada junto da primeira capability que oferecer uma dessas ações.

**Alternativa considerada:** permitir que o cliente envie `perfil` no cadastro ou criar uma rota pública de promoção. Rejeitada por permitir autoelevação.

### Não escrever em um destino com recursos preexistentes

Antes do Apply, fazer pull somente de definições do destino autorizado, sem registros ou variáveis, para constatar seu estado atual. A tarefa não usará esse conteúdo para formar o schema greenfield. Se houver qualquer recurso existente, parar sem push, sync, delete, adaptação ou substituição; pedir uma decisão revisada sobre um destino limpo. A cópia observada nesta investigação não substitui a nova verificação imediatamente antes do Apply.

O workspace atualmente identificado já contém definições e informa `allow_push: false`; portanto, com as evidências de hoje não há um alvo liberado para escrita. A Change não instrui habilitar essa opção, contornar permissão/plano, criar branch ou escolher outro workspace sem confirmação explícita.

**Alternativas consideradas:** usar os arquivos do pull atual como baseline de `--sync --delete`, atualizar recursos com nomes coincidentes ou limpar o workspace. Rejeitadas por contrariar o pedido greenfield de preservar recursos encontrados.

### Aplicação Reflex e preparação local

Reflex foi aprovado na avaliação do projeto com 11/14 e mitigação aceita para incluir foco visual distinguível antes da interface funcional. Antes de editar ou executar código no Apply, seguir o Apêndice B: usar uma única estratégia `venv` + `pip`, conferir Python e skills Reflex no Copilot (`reflex-docs`, `setup-python-env`, `reflex-process-management`) e parar se o pré-requisito de skills não estiver disponível. A prova em `evaluation/reflex-poc/` permanece descartável; não copiar seu mock para o produto.

## Dependências e Changes posteriores

Esta Change depende de uma conta autenticável e de um destino Xano limpo e confirmado. Ela desbloqueia a integração Reflex de cadastro/login/perfil e, depois, as operações autenticadas das próximas capabilities. A sequência planejada é:

1. **Identidade e sessão (esta Change):** conta e perfil confiável; cadastro cria estudante; sessão Reflex mediada e isolada; nenhum papel escolhido pelo cliente.
2. **Catálogo e exemplares (Change futura):** consulta pública do acervo; títulos podem pertencer a várias categorias e ter vários exemplares físicos; manutenção de títulos, categorias e exemplares exige perfil bibliotecário no backend. Disponibilidade agregada deriva dos exemplares elegíveis, não de uma quantidade agregada.
3. **Empréstimo e retirada/devolução (Change futura, dependente de identidade e exemplares):** estudante solicita; bibliotecário registra a retirada física e a devolução; prazo de 14 dias corridos começa na retirada; no máximo um empréstimo ativo por estudante; atraso bloqueia novos empréstimos e reservas; o servidor revalida elegibilidade e disponibilidade para concorrência.
4. **Reservas e fila (Change futura, dependente de identidade, catálogo e estados de empréstimo):** reserva por título em FIFO; no máximo uma ativa por estudante/título; não reservar título já emprestado pelo próprio estudante sem atraso; janela de retirada de dois dias a partir da disponibilização.
5. **Danos e perdas (Change futura, dependente de exemplares e perfil bibliotecário):** registrar observação e manter exemplar indisponível até regularização.

Antes de especificar as Changes de circulação, decidir se pedido sem exemplar disponível entra em fila de empréstimo ou exige reserva, o evento/canal do aviso da janela de retirada, calendário, feriados e fuso. Não inventar essas regras nem materializar antecipadamente as entidades futuras.

## Risks / Trade-offs

- [O workspace de referência continua povoado] → Não considerar o reset concluído. Interromper Apply antes de qualquer escrita se o pull pré-Apply encontrar recursos; solicitar destino vazio e autorizado ou decisão revisada.
- [`allow_push` está desabilitado e a branch encontrada é live] → Não tentar habilitar push, contornar plano/permissões, criar branch ou escrever. Reconfirmar o alvo e a permissão no Apply; manter a tarefa bloqueada enquanto não houver autorização técnica.
- [A auth nativa pode não corresponder ao contrato aprovado] → Confirmar documentação e comportamento antes de definir os artefatos físicos; parar e revisar se exigir contratos inventados ou fluxo incompatível.
- [E-mail único pode ter semântica de normalização concorrente] → Confirmar política do Xano e testar cadastro duplicado concorrente; não confiar somente em validação prévia no cliente.
- [Credencial privada no estado Reflex pode vazar em estado serializado] → Testar duas sessões simultâneas e inspecionar respostas/eventos/bundle para garantir isolamento e ausência de token.
- [Logout local não revoga necessariamente a credencial do provedor] → Limpar o contexto Reflex e documentar o limite; não anunciar revogação Xano sem mecanismo comprovado.
- [Mudanças futuras podem criar schemas adiantados] → Exigir que cada Change de catálogo/circulação desenvolva dados, regras, API e interface da capability em conjunto, com decisões ainda abertas resolvidas antes de fixar o schema.
- [Acessibilidade da interface anterior tinha lacuna de foco] → Aplicar e verificar `:focus-visible` na interface de produto antes de concluir Verify.

## Migration Plan

1. Em Apply, confirmar pelo CLI o workspace, branch, ambiente e permissão imediatamente antes de qualquer operação remota.
2. Fazer pull de definições somente para verificar o estado e colisões. Se houver recursos, parar; não importar, adaptar ou excluir a cópia e não fazer push.
3. Confirmar que há destino limpo, explicitamente autorizado e tecnicamente habilitado para escrita. Uma mudança de destino ou a necessidade de limpar recursos requer nova decisão humana e revisão dos artefatos.
4. Confirmar a autenticação nativa e então preparar apenas o contrato de identidade desta Change. Mostrar o diff/dry-run para revisão explícita, sem incluir registros, variáveis, truncamento ou sincronização destrutiva.
5. Após aprovação específica, implementar os contratos Xano e Reflex, provisionar bibliotecário somente pelo procedimento manual confirmado e testar a integração.
6. Se qualquer gate falhar, não escrever no Xano e não marcar tarefas dependentes como concluídas. Não há migração nem rollback de recursos legados nesta Change, pois esses recursos estão fora de seu escopo.

## Open Questions

- Qual destino vazio e explicitamente autorizado será usado se o workspace `151966`/branch `v1` continuar com recursos ou `allow_push: false` no Apply?
- A autenticação nativa Xano oferece o contrato, configuração de expiração e retorno de perfil necessários sem operações adicionais fora do escopo?
- Qual processo operacional seguro o operador usará para provisionar a conta inicial de bibliotecário após a confirmação do destino?
- Como serão decididos o fluxo de pedido sem exemplar e o evento/calendário/fuso da janela de retirada, antes das Changes de circulação?
- Qual ambiente acadêmico será usado para deploy? A escolha e o deploy ficam para Change posterior.
