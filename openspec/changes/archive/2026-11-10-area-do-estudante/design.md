# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de [catalog](./specs/catalog/spec.md), [loan-circulation](./specs/loan-circulation/spec.md), [reservations](./specs/reservations/spec.md) e [frontend-foundation](./specs/frontend-foundation/spec.md). A aplicação já mantém token e perfil em variáveis privadas do estado Reflex; a lista pública de títulos fornece metadados para `titulo_id`.

## Goals / Non-Goals

**Goals:**
- Consumir somente os endpoints locais existentes para solicitar e consultar dados do próprio estudante.
- Exibir situação e prazos sem enviar credenciais ao navegador e sem substituir autorização ou elegibilidade do servidor.
- Tornar explícitos limites do formato atual de resposta e inconsistências locais entre endpoint e spec.

**Non-Goals:**
- Alterar Xano, tabelas, endpoints, regras de servidor ou especificações consolidadas.
- Permitir bibliotecário/admin/visitante na área pessoal de estudante.
- Inferir posição na fila, título de exemplar emprestado ou qualquer dado ausente dos GETs.

## Decisions

### Fluxo de solicitação autenticado

Usar `POST /solicitacoes-emprestimo` conforme o caminho publicado no OpenAPI do grupo Biblioteca, com `titulo_id` e token privado do estudante. Os arquivos `.xs` confirmam o nome lógico da operação e sua regra de negócio; o OpenAPI define o caminho HTTP. O catálogo apenas escolhe a apresentação inicial do botão usando `exemplares_disponiveis`; a interface sempre trata a resposta do backend como autoridade porque a disponibilidade pode mudar. Não usar `POST /reservas`: o endpoint local permite criar reserva sem exigir que não haja exemplar disponível. A API de solicitação local verifica perfil, atraso, disponibilidade e fila e, conforme o caso, registra solicitação e reserva.

**Alternativas consideradas:** chamar diretamente o POST de reservas quando o catálogo mostra zero; rejeitado porque o dado pode estar desatualizado e o endpoint de reservas não impõe indisponibilidade.

### Consultas da página “Minha biblioteca”

Carregar, autenticado e no estado backend Reflex, `GET /minhas/emprestimos`, `GET /minhas/solicitacoes` e `GET /minhas/reservas`, conforme os caminhos do OpenAPI e os arquivos `.xs` locais. Usar a lista pública de títulos para resolver `titulo_id` de solicitações e reservas. O GET de empréstimos fornece `exemplar_id`, `retirado_em`, `vence_em` e `devolvido_em`, mas não junta título/exemplar: apresentar esses campos disponíveis, sem tentar obter dados privados de outros estudantes. Não inventar posição de fila: `GET /minhas/reservas` não a retorna.

O serviço de reservas acrescenta `expira_em_sao_paulo`; a interface apresenta esse campo como recebido e não recalcula o fuso. Para estado ativo de devolução, tratar `devolvido_em` nulo ou `0` como não devolvido. Calcular o aviso de atraso comparando timestamps interpretados com fuso contra o instante atual UTC; essa indicação é informativa, e o backend continua a única autoridade para bloquear pedidos.

**Alternativas consideradas:** inferir o título do empréstimo por `exemplar_id`, calcular posição de fila ou converter novamente o prazo no cliente; rejeitadas por falta de dados/endpoints ou por duplicar a conversão já oferecida pelo servidor.

### Divergência entre spec e endpoint de solicitação

O arquivo local `xano/api/default/emprestimos/solicitacoes_POST.xs` (caminho publicado como `POST /solicitacoes-emprestimo`) primeiro cria `solicitacao_emprestimo`; quando não há disponibilidade (ou há reserva aguardando), também cria `reserva` e muda o estado da solicitação para `em_reserva`, com `reserva_id`. Isso diverge do requisito existente em `openspec/specs/loan-circulation/spec.md` que diz que a solicitação sem exemplar entra na fila sem criar solicitação separada. A2 não mudará endpoint nem spec consolidada. Na apresentação, relacionar solicitação `em_reserva` à reserva pelo ID retornado e evitar duplicar a mesma ação na lista; registrar o desvio como pendência para decisão/revisão humana antes de alterar o backend.

**Alternativas consideradas:** ignorar a divergência, ocultar todo o fluxo de indisponibilidade ou alterar o Xano nesta Change; as duas primeiras impedem transparência e a última viola o escopo frontend-only.

### Autorização e falhas

Exigir perfil estudante no estado antes de montar/usar a rota pessoal e antes de cada evento. Em caso de sessão ausente, direcionar para login; outro perfil retorna à área pública. Todo GET pessoal e POST usa o token privado somente no cliente backend. Apresentar erro sanitizado quando o Xano recusar, estiver indisponível ou retornar formato inválido; não registrar token ou corpo sensível.

**Alternativas consideradas:** proteger somente o link no menu; rejeitado porque navegação direta e chamadas a eventos precisam ser protegidas.

## Risks / Trade-offs

- [O endpoint local e a spec divergirem quanto à fila de empréstimos] → não mudar servidor/spec nesta Change; deduplicar a apresentação e sinalizar a pendência.
- [Empréstimos não incluírem dados bibliográficos] → mostrar exemplar e datas sem inventar título; requer decisão/backend futuro se nome do título for obrigatório.
- [O aviso de atraso usar relógio do backend Reflex] → manter comparação em UTC e tratar o aviso como indicativo; o servidor sempre revalida bloqueios.
- [Resposta de um GET pessoal falhar] → mostrar erro explicitamente e não reportar sucesso de solicitação; não usar dados desatualizados como se fossem atuais.

## Migration Plan

Sem migração ou push remoto. Implementar somente cliente de operações existentes, eventos/estado Reflex e interface; testar GETs e POSTs com `httpx.MockTransport`. Reversão consiste em retirar as rotas e os eventos da interface, sem alteração de dados ou contrato remoto.

## Open Questions

Não há decisões pendentes para a implementação frontend desta Change. A divergência do endpoint e a ausência do título no GET de empréstimos são limites conhecidos, tratados pelas decisões acima. Qualquer alteração futura de backend para alinhar o endpoint à spec ou incluir metadados bibliográficos exige Change própria e revisão humana.
