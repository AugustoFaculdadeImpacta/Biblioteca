# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas de [reservations](./specs/reservations/spec.md) e [frontend-foundation](./specs/frontend-foundation/spec.md).

O Xano atual oferece `POST /reservas`, autenticado como o próprio usuário e restrito no servidor ao perfil estudante. Ele valida atraso com `devolvido_em` nulo ou zero, empréstimo ativo do mesmo título e reserva ativa nos estados `aguardando`/`ofertada`. Não há operação local para pesquisar estudantes nem criar reserva para outra conta. A tela Reflex administrativa de reservas também não existe.

## Goals / Non-Goals

**Goals:**
- Separar a identidade do funcionário autenticado da conta estudante alvo.
- Reutilizar exatamente as regras atuais de elegibilidade e FIFO no servidor.
- Limitar a busca ao necessário para identificar estudante e registrar a reserva.

**Non-Goals:**
- Criar sessão, autenticar ou alterar credenciais do estudante alvo.
- Permitir alterar horário, posição, prioridade, estado ou estudante de uma reserva existente.
- Emitir oferta de exemplar diretamente por esta operação.

## Decisions

### Busca de estudante por e-mail exato

Pesquisar pelo endereço completo, aplicando a mesma normalização já usada no login/cadastro: remover espaços externos, converter para minúsculas e rejeitar espaços internos. A busca não lista contas nem aceita busca parcial por nome. O resultado retorna somente identificador e nome necessários à confirmação da pessoa; nenhum segredo ou dado escolar adicional é devolvido.

**Alternativa considerada:** busca parcial por nome ou listagem de estudantes; rejeitada por expor mais dados pessoais e ampliar a possibilidade de enumeração.

### Reserva executada pelo funcionário autenticado

O Xano deve autenticar a conta que faz a operação e confirmar no servidor seu perfil `bibliotecario` ou `admin`; separadamente deve validar que o identificador alvo pertence a uma conta `estudante`. O cliente não envia papel de quem solicita nem pode converter uma conta de outro perfil em estudante.

**Alternativa considerada:** chamar `POST /reservas` usando identidade do estudante ou aceitar token informado pelo cliente; rejeitada porque falsificaria a identidade e contornaria a autorização.

### Elegibilidade e ordem FIFO

Reutilizar os invariantes do endpoint atual: sem empréstimo atrasado (empréstimo ainda não devolvido quando `devolvido_em` é nulo ou zero), sem empréstimo ativo do mesmo título, sem reserva ativa duplicada e com título ativo. O backend cria a nova reserva com instante próprio do servidor no fim normal da fila. A ação não escolhe exemplar, não cria oferta e não altera as reservas existentes. A aplicação de `ativo` depende de `acervo-bibliotecario`.

**Alternativa considerada:** atribuir imediatamente um exemplar disponível ao estudante atendido pelo funcionário; rejeitada porque pode pular a fila existente e mistura reserva com retirada/atendimento.

### Contratos Xano pendentes

O CLI confirmou workspace `151966`, branch `v1` live, grupo Biblioteca e `allow_push=false`; o pull isolado de referência com 57 definições está fora do repositório, e `xano/` local continua sem alterações. A ferramenta Xano Developer MCP não está disponível nesta sessão. Não há contrato local para busca por estudante ou criação em nome de terceiro. Não inventar caminho, verbo, campos ou formato de resposta. Validar o desenho com Xano Developer antes de implementar; a operação de criação deve usar o ator autenticado para autorização e o estudante alvo como beneficiário, e precisa garantir atomicidade entre validação de duplicidade/FIFO e gravação. Se a documentação ou a capacidade de push unitário não estiver disponível, marcar tarefas Xano como NÃO EXECUTADAS e não simular sucesso de produção.

**Alternativa considerada:** estender `POST /reservas` existente para aceitar `usuario_id`; rejeitada até validação explícita, pois mudaria uma operação de identidade própria e poderia ampliar sua superfície de autorização.

### Dependências de perfil e acervo

Admin só pode usar as mesmas permissões depois que `perfil-admin-xano` estiver concluída no backend. Título inativo deve ser recusado depois que `acervo-bibliotecario` criar e validar essa regra. Enquanto qualquer dependência não estiver entregue, não afirmar disponibilidade real da operação para admin ou títulos inativos.

**Alternativa considerada:** tratar a validação de perfil no Reflex como suficiente; rejeitada porque a API é a autoridade de autorização.

### Interface

Usar a rota Reflex `/admin/reservas` para busca e criação. A tela coleta o e-mail exato, permite confirmar a identidade retornada e então envia somente identificador do estudante e identificador do título à operação administrativa validada. O token permanece no estado privado Reflex. Rejeições por atraso, empréstimo, duplicidade, fila ou perfil devem ser exibidas sem detalhes internos.

**Alternativa considerada:** adicionar o fluxo à tela pública ou permitir envio para a fila por estudante; rejeitada porque exporia busca de pessoas e atribuição administrativa.

## Risks / Trade-offs

- [Busca por e-mail pode revelar existência de conta] → limitar a bibliotecário/admin e retornar apenas identidade mínima.
- [Corrida entre duplicidade/elegibilidade e criação] → validar atomicidade no Xano; se não for garantida, não habilitar a operação.
- [Perfil `admin` ainda não aceito pelo backend] → depender da conclusão de `perfil-admin-xano`.
- [Título inativo ainda não existe no schema] → depender da conclusão de `acervo-bibliotecario`.
- [Contrato ou ferramenta Xano indisponível] → não adivinhar endpoint; manter a Change ativa e testes locais claramente mockados.

## Migration Plan

1. Reconfirmar workspace `151966`, branch `v1`, ambiente live, grupo Biblioteca e permissões do CLI; usar pull isolado e rollback fora do repositório.
2. Consultar Xano Developer para validar busca, criação para terceiro, payload mínimo, autorização, consistência/FIFO e integração com título ativo.
3. Implementar cada endpoint em arquivo separado somente com contrato validado; exigir dry-run de um único CREATE/UPDATE, push unitário permitido e pull de conferência.
4. Testar com estudantes sintéticos `zz-teste-*@exemplo.invalid`, registrar IDs fora do repositório, limpar individualmente pela Metadata API e verificar GET 404 e contagens finais.
5. Testar Reflex com respostas mockadas, documentando-as como simuladas; não chamar Xano real com dados de teste enquanto o gate não estiver aprovado.

## Decisões tomadas por delegação (revisar)

- Busca de estudante por e-mail completo normalizado, não parcial por nome, para reduzir exposição de dados.
- A resposta da busca contém somente identificador e nome.
- A reserva criada pelo funcionário entra no fim da fila segundo o horário gerado pelo servidor; não há prioridade, escolha de exemplar nem oferta imediata pela tela.
- São mantidos atraso, empréstimo ativo do mesmo título, reserva ativa única e perfil estudante, sem exceções administrativas.
- `devolvido_em` nulo ou zero significa empréstimo não devolvido.
- A tela Reflex fica em `/admin/reservas`; isso é uma rota de interface, não um endpoint Xano.
- Não inventar contrato Xano; título ativo depende de `acervo-bibliotecario`, e perfil admin depende de `perfil-admin-xano`.
- O destino Xano permanece workspace `151966`, branch `v1`, grupo Biblioteca; `allow_push` não será alterado.
