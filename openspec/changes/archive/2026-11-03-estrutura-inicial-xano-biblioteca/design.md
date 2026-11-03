# Design

## Context

Consulte `proposal.md` e as cinco specs para escopo e comportamento. `docs/domain-model.md` é conceitual e não define nomes físicos de campos ou tabelas.

O destino autorizado pelo usuário para esta Change é workspace `151966` (`Augusto's Workspace`), host `x8ki-letl-twmt.n7.xano.io`, branch `v1`. A consulta CLI de metadados em 2026-10-27 confirmou que `v1` está live e `allow_push: false`. O inventário de 35 documentos abaixo é resultado de pull somente de definições anterior e não foi atualizado nesta execução; nenhum registro ou variável foi lido:

- **Tabelas (4):** `table/categorias.xs`, `table/emprestimo.xs`, `table/livro.xs`, `table/usuario.xs`.
- **Endpoints (24):** `api/default/auth/login_POST.xs`, `api/default/auth/me_GET.xs`, `api/default/auth/signup_POST.xs`, `api/default/categorias/categorias_id_DELETE.xs`, `api/default/categorias/categorias_id_GET.xs`, `api/default/categorias/categorias_id_PATCH.xs`, `api/default/categorias/categorias_id_PUT.xs`, `api/default/categorias_GET.xs`, `api/default/categorias_POST.xs`, `api/default/default.xs`, `api/default/emprestimo/emprestimo_id_DELETE.xs`, `api/default/emprestimo/emprestimo_id_GET.xs`, `api/default/emprestimo/emprestimo_id_PATCH.xs`, `api/default/emprestimo/emprestimo_id_PUT.xs`, `api/default/emprestimo_GET.xs`, `api/default/emprestimo_POST.xs`, `api/default/livro/livro_id_DELETE.xs`, `api/default/livro/livro_id_GET.xs`, `api/default/livro/livro_id_PATCH.xs`, `api/default/livro/livro_id_PUT.xs`, `api/default/livro_GET.xs`, `api/default/livro_POST.xs`, `api/event_logs/event_logs.xs`, `api/event_logs/logs/user/my_events_GET.xs`.
- **Outros recursos (7):** 3 funções (`enforce_role`, `generate_magic_link`, `log_event`), 1 addon (`user`), 2 objetos de IA (`xano_example_agent`, `search_xano_docs`) e 1 definição de workspace (`augustos_workspace`).

O workspace não está vazio. O schema legado é somente inventário do estado existente, não modelo para o desenho greenfield. O escopo remoto de definições limita operações a tabelas e endpoints necessários à biblioteca. Não alterar funções, addons, configuração/definição do workspace, variáveis de ambiente ou outros recursos. A verificação segura concluída criou fixtures pelos endpoints existentes, leu e removeu somente IDs capturados, com confirmação individual. Não executar leitura em massa, `--records`, `--truncate` nem tocar em registros preexistentes ou fora da lista capturada. Ajustes temporais e testes avançados foram separados para `verificacao-avancada-circulacao`, que exige ambiente isolado.

O projeto orienta Changes verticais pequenas, com dados, regras, API e interface evoluindo com cada capability. Esta Change é uma exceção deliberada solicitada pelo usuário: planeja a estrutura Xano e os contratos de API de todas as cinco áreas numa única Change e não implementa a interface. O conflito permanece explícito; não se declara que o escopo abrangente atende à regra vertical.

## Goals / Non-Goals

**Goals:**

- Definir o modelo lógico Xano, relações e contratos lógicos de endpoints para as cinco áreas aprovadas.
- Distinguir regras decididas das pendências que alteram o schema, o contrato ou os critérios de aceitação.
- Preparar e revisar todos os candidatos e o dry-run completo antes de qualquer escrita remota, com aprovação explícita da prévia exata.
- Após Apply, comparar o que foi aplicado com a prévia aprovada e verificar os contratos Xano.
- Documentar contratos para futura conexão do Reflex sem implementar o cliente.

**Non-Goals:**

- Implementar aplicação, telas, estado de sessão, integração executável, setup ou testes de UI Reflex.
- Usar ou reconstruir o schema legado ou a implementação de `biblioteca-nova`.
- Especificar renovação, multas, recuperação/regularização de exemplares perdidos ou operações de exclusão sem decisão aprovada.
- Escrever no workspace histórico ou escolher outro workspace/branch sem confirmação do usuário.

## Decisions

### Separar requisitos já aprovados de decisões pendentes

As regras abaixo são requisitos aprovados e permanecem no contrato:

- Cadastro de estudante exige nome, e-mail único e senha, sem confirmação de e-mail e com acesso imediato; autocadastro nunca concede papel de bibliotecário.
- Perfil da conta autenticada é confiável e operações administrativas são autorizadas no backend.
- Catálogo público; um título pode ter várias categorias e vários exemplares físicos. Disponibilidade é derivada de exemplares elegíveis.
- Estudante solicita; bibliotecário confirma retirada e devolução física. O prazo é de 14 dias corridos a partir do registro da retirada.
- No máximo um empréstimo ativo por estudante; atraso não devolvido bloqueia novos empréstimos e reservas.
- Reservas são por título e FIFO; no máximo uma reserva ativa por estudante/título; não se reserva título que a própria pessoa possui em empréstimo ativo não atrasado.
- A oportunidade de retirada dura 48 horas corridas desde a associação do exemplar e o registro da oferta; timestamps são armazenados em UTC e apresentados em `America/Sao_Paulo`.
- Dano/perda exige observação e torna o exemplar indisponível. Não se presume processo de regularização.
- Quando não há exemplar imediatamente disponível para um pedido elegível, o pedido entra na fila FIFO de reservas do título; não há uma fila separada de solicitações.
- Cancelamento de pedidos/reservas e exclusão/arquivamento de títulos, categorias e exemplares estão fora desta Change.

Decisões aprovadas para o contrato físico:

1. Antes de validar, salvar ou verificar duplicidade, normalizar o e-mail removendo espaços no início/fim e convertendo todas as letras para minúsculas; rejeitar espaços internos. Aplicar a unicidade ao e-mail normalizado. Não normalizar nem alterar a senha.
2. Título e autor(es) são obrigatórios. ISBN, editora, edição, ano de publicação e descrição são opcionais.
3. Cada exemplar recebe do sistema um código de tombo único e imutável, no formato exemplificado por `EX-000001`. Cada cópia do mesmo título tem código próprio; o código de tombo não é o ISBN.
4. A oportunidade de retirada dura 48 horas corridas a partir do instante em que o sistema associa exemplar disponível à reserva e registra a oferta. Persistir timestamps em UTC e apresentá-los no fuso `America/Sao_Paulo`. Essa regra não altera o prazo de empréstimo de 14 dias corridos.

O primeiro bibliotecário será provisionado manualmente por operador autorizado no Xano; não há endpoint público de promoção e nenhuma senha ou token será gravado em arquivos. Permanecem como gates técnicos, e não decisões de domínio: confirmar suporte Xano para geração concorrente do código de tombo, garantias atômicas das transições concorrentes, processamento de expirações sem tarefa em background (fora dos tipos de recurso autorizados), autenticação/autorização nativa e validação efetiva dos candidatos no workspace.

Renovação, multas e regularização/recuperação de perdas não são requisitos nem pendências que precisem ser resolvidas para esta Change; ficam fora do escopo. Não criar estados ou endpoints para eles.

### Propor entidades lógicas separadas, sem nomes físicos presumidos

As entidades abaixo representam o modelo lógico necessário. Os nomes são rótulos conceituais; schema físico, campos e índices seguem as decisões aprovadas acima. A importabilidade e as garantias de implementação ainda dependem de validação no Xano.

| Entidade lógica | Relações e invariantes aprovadas | Pendências relevantes |
|---|---|---|
| Conta | Nome, e-mail normalizado único e perfil estudante/bibliotecário; credencial protegida pelo mecanismo nativo | Método seguro de provisionamento inicial |
| Título | Obra bibliográfica com título e autor(es) obrigatórios, metadados opcionais, relacionada a categorias e exemplares | Nenhuma pendência de metadados aprovada |
| Categoria | Classificação de acervo | Regras de nome duplicado ou remoção, se necessárias |
| Associação título-categoria | Relação muitos-para-muitos | Política de remoção, se necessária |
| Exemplar | Unidade física pertencente a um título; código de tombo único, imutável e gerado pelo sistema; disponibilidade derivada de empréstimo/reserva/condição | Validar geração sem colisão sob concorrência |
| Solicitação de empréstimo | Intenção de estudante separada de retirada/empréstimo; sem exemplar disponível, o pedido entra na fila FIFO de reservas do título, sem fila paralela | Garantias atômicas de elegibilidade e transição concorrente no Xano |
| Empréstimo | Estudante, exemplar, retirada, vencimento e devolução; vencimento 14 dias corridos após retirada | Validação de garantias concorrentes no Xano |
| Reserva | Estudante, título e ordem de solicitação FIFO; no máximo uma ativa por estudante/título; recebe exemplar quando chega à vez | Nenhuma operação de cancelamento nesta Change |
| Oportunidade de retirada | Reserva atendida, exemplar associado e expiração após 48 horas corridas desde o registro da oferta; timestamps UTC e apresentação em `America/Sao_Paulo` | Validar execução automática de expiração/realocação sem criar recurso fora do escopo de endpoints e tabelas |
| Evento de condição | Exemplar, dano/perda, observação, instante e responsável bibliotecário | Sem fluxo de recuperação nesta Change |

Disponibilidade deve ser derivada, não duplicada como contador independente no título. Empréstimos e eventos de condição precisam preservar histórico. Não incluir exclusões físicas de dados sem política aprovada.

### Documentar contratos lógicos da API Xano para clientes futuros

Os caminhos abaixo são identificadores lógicos de operações para discussão, não caminhos físicos Xano já validados. O contrato de cada operação deve documentar perfil, entradas, saída, falhas e invariantes; caminhos, nomes de campos, paginação, autenticação nativa e formatos/códigos de erro serão confirmados antes do preview. A especificação OpenAPI local deverá refletir apenas as decisões aprovadas.

| Operação lógica | Acesso | Resultado esperado |
|---|---|---|
| Cadastro | Público | Criar estudante com nome, e-mail normalizado único e senha, permitindo acesso imediato sem aceitar papel do cliente; senha não é normalizada |
| Login | Público | Normalizar o e-mail segundo a regra aprovada, autenticar e retornar identidade pública/perfil confiável conforme contrato |
| Minha identidade | Conta autenticada | Retornar dados públicos da conta e papel confiável |
| Listar/consultar títulos | Público | Título e autor(es), metadados opcionais publicados, categorias e disponibilidade agregada |
| Listar categorias e títulos relacionados | Público | Classificação e títulos publicados relacionados |
| Criar/atualizar título, categoria e associação | Bibliotecário | Persistir recurso autorizado e validar relações |
| Criar exemplar | Bibliotecário | Persistir unidade física, atribuir código de tombo único e imutável no backend, e validar título; o cliente não define nem altera o código; estado muda somente pelos fluxos operacionais |
| Solicitar empréstimo e consultar próprios pedidos/reservas | Estudante | Registrar intenção sem tratá-la como retirada; sem exemplar, inserir o pedido na fila FIFO de reservas do título, sem fila paralela |
| Consultar solicitações e confirmar retirada/devolução | Bibliotecário | Revalidar elegibilidade; registrar retirada, vencimento ou devolução |
| Criar/listar reservas próprias | Estudante | Registrar reserva elegível e retornar somente dados próprios; sem operação de cancelamento nesta Change |
| Consultar fila e associar exemplar à próxima reserva | Bibliotecário | Atender a fila FIFO quando a reserva chega à vez e registrar oferta com expiração 48 horas corridas após a associação; armazenar timestamps UTC |
| Processar ofertas expiradas | Operação protegida | Marcar expirada, liberar exemplar e oferecer à próxima reserva elegível; acionamento automático periódico ainda depende de mecanismo não autorizado nesta Change |
| Consultar oportunidade própria e confirmar retirada | Estudante/Bibliotecário conforme operação | Expor prazo convertido para `America/Sao_Paulo` à pessoa titular e registrar a retirada por confirmação física do bibliotecário |
| Registrar/consultar condição | Bibliotecário | Registrar dano/perda com observação e preservar histórico; detalhes não são públicos |

Não propor endpoint de logout Xano: o comportamento de logout/interface pertence à futura integração. Não propor endpoints de cancelamento ou exclusão/arquivamento nesta Change. Semântica de falhas a documentar inclui entrada inválida, sessão ausente/inválida, perfil insuficiente, recurso inexistente, conflito de duplicidade/invariante e disputa concorrente.

### Tratar o destino e o dry-run como gates absolutos

O destino desta Change é o workspace `151966`, branch `v1`, conforme autorização expressa do usuário; não selecionar destino alternativo. A consulta somente de metadados pelo CLI confirmou workspace `151966`, branch `v1` live e `allow_push: false`. Nenhum registro ou variável foi lido. Enquanto esse bloqueio persistir, não executar dry-run que dependa de permissão de escrita, push, sync ou outra operação remota; não tentar habilitar configuração, contornar plano/permissão ou trocar de destino.

Se o CLI passar a permitir escrita, reconfirmar workspace/branch/live/permissão, preparar e revisar todos os candidatos, executar dry-run integral e conferir seu escopo antes de aplicar. O usuário já autorizou nesta execução reconstruir tabelas e endpoints legados necessários à biblioteca, inclusive a perda potencial dos dados existentes nessas tabelas, que não foram consultados. Aplicar somente tabelas/endpoints necessários à biblioteca. Qualquer função, addon, objeto de IA, configuração, variável ou outro recurso fora do escopo no preview bloqueia o push. Não usar `--records`, `--env` ou `--truncate`; não executar sync/delete amplo. A exceção da tarefa 5.2 permite apenas operações sobre fixtures e IDs capturados conforme descrito no Context. Registrar operações e o potencial de perda de dados no relatório, sem ampliar autorização a outros recursos.

**Alternativa considerada:** reaproveitar recursos históricos para acelerar. Rejeitada porque não são a fonte do modelo greenfield e o destino ainda não está liberado para escrita.

### Manter Reflex como consumidor futuro, não como implementação desta Change

Registrar a superfície REST, as autorizações e a semântica de resposta/erro necessárias para um cliente futuro. Não implementar token/session handling no Reflex, telas, UX, dependências ou chamadas executáveis. Uma Change posterior deverá implementar e verificar a integração, incluindo a proteção do token no backend, segundo os critérios e decisões então aprovados.

**Alternativa considerada:** incluir o cliente Reflex agora para tornar a Change vertical. Rejeitada nesta Change porque o pedido explícito delimita o trabalho ao Xano e aos contratos documentais; a exceção à orientação vertical foi autorizada e fica registrada.

## Risks / Trade-offs

- [O workspace autorizado contém 35 definições, está na branch live e `allow_push: false`] → Nenhuma escrita até o CLI confirmar capacidade; não escolher outro destino nem contornar a restrição.
- [Uma alteração ou substituição das tabelas legadas pode perder dados não consultados] → O usuário autorizou reconstruir as tabelas/endpoints da biblioteca; registrar o risco, nunca importar/exportar registros nem executar truncamento direto.
- [Recursos de funções/addons/configuração coexistem com tabelas e endpoints no mesmo pull] → Comparar cada recurso do dry-run ao escopo permitido e parar se qualquer um dos tipos fora do escopo aparecer.
- [A Change cruza cinco capabilities em vez de uma Change vertical pequena] → Tratar como exceção explícita solicitada; não afirmar conformidade com a regra vertical e manter a implementação Reflex fora do escopo.
- [Decisões de domínio podem alterar schema ou payload] → Resolver e registrar antes de preparar/aprovar o dry-run; não preencher lacunas por conveniência.
- [Xano pode não garantir atomicidade, geração de tombo ou expiração automática como exigido] → Validar em documentação/ferramenta suportada; deixar a verificação remota bloqueada se o plano ou os recursos autorizados não permitirem a prova.
- [Prévia e Apply podem divergir] → Comparar saída da operação e pull posterior com a prévia aprovada; parar ao primeiro delta não aprovado.
- [Integração Reflex futura pode exigir detalhes ainda não fechados] → Entregar contratos documentais e adiar a implementação do cliente para Change própria.

## Migration Plan

1. Reconfirmar pelo CLI workspace `151966`, branch `v1`, estado live e `allow_push`; com `allow_push: false`, não executar dry-run dependente de escrita nem push.
2. Refletir as decisões aprovadas nos contratos e preparar candidatos locais para tabelas e endpoints apenas; validar o que for possível localmente sem alegar validação do parser/servidor Xano.
3. Com escrita oficialmente habilitada, revisar diff local, produzir dry-run integral e confirmar que somente tabelas/endpoints do escopo aparecem. O usuário autorizou a reconstrução desses recursos e reconhece a perda potencial dos dados das tabelas legadas não consultadas.
4. Aplicar o preview autorizado somente se o CLI permitir, preservando todos os tipos de recurso fora do escopo e sem records/env/truncate/sync-delete amplo.
5. Após Apply, fazer pull somente de definições, comparar com preview, verificar endpoints e registrar limitações. Na verificação 5.2, aplicar apenas a exceção restrita de fixtures sintéticos e remoção por IDs capturados; nenhuma outra operação de registro é autorizada.
6. Arquivar apenas depois de Verify e todas as tasks concluídas. Não alterar funções, addons, objetos de IA, configurações, variáveis ou outros recursos.
