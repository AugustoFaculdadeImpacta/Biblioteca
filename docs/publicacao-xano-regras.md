# Publicação manual das regras da biblioteca no Xano

Este documento descreve o contrato que a interface espera. A publicação é
manual e deve ser feita por uma pessoa autorizada no workspace correto. Esta
Change não consulta nem altera o Xano.

## Contrato de dados

Criar/usar a tabela `configuracao_biblioteca` com uma configuração vigente e
estes campos:

| Campo | Tipo | Padrão | Validação |
|---|---|---:|---|
| `limite_emprestimos_ativos` | inteiro | 3 | de 1 a 20 |
| `limite_pedidos_em_aberto` | inteiro | 3 | de 1 a 20 |
| `permitir_pedido_com_reserva_ativa` | booleano | `true` | aceitar somente `true` ou `false` |
| `bloquear_com_atraso` | booleano | `true` | aceitar somente `true` ou `false` |
| `exigir_autorizacao_bibliotecaria` | booleano | `true` | aceitar somente `true` ou `false` |
| `prazo_emprestimo_dias` | inteiro | 14 | de 1 a 60 |
| `prazo_retirada_horas` | inteiro | 48 | de 1 a 168 |

O serviço pode incluir `atualizado_em` e `atualizado_por` na resposta. São
metadados de leitura, não fazem parte do corpo enviado ao salvar regras.

## Endpoints

### `GET /configuracoes`

- Exigir uma sessão autenticada; estudantes, bibliotecários e admins podem
  consultar os limites usados na interface.
- Retornar um objeto com os sete campos acima e, quando disponíveis, os
  metadados `atualizado_em` e `atualizado_por`.
- A leitura não concede autorização para operações: cada pedido, reserva,
  retirada ou devolução deve revalidar as regras no servidor.

### `PUT /admin/configuracoes`

- Exigir perfil real `admin`.
- Receber somente os sete campos do contrato. Rejeitar campos extras,
  inteiros fracionários/fora da faixa e valores booleanos que não sejam
  `true` ou `false`; não gravar parcialmente uma configuração inválida.
- Atualizar a configuração e os metadados de alteração. Retornar o objeto
  atualizado; não exigir que o cliente envie `atualizado_em` ou
  `atualizado_por`.

## Regras aplicadas no servidor

1. Revalidar disponibilidade do título, empréstimos ativos, pedidos em aberto,
   atraso e elegibilidade a cada operação.
2. Recusar nova operação quando o estudante já atingiu
   `limite_emprestimos_ativos` ou `limite_pedidos_em_aberto`. Contar registros
   abertos sem contar duas vezes uma reserva vinculada ao mesmo pedido.
3. Quando `bloquear_com_atraso` for `true`, impedir novos pedidos e reservas
   enquanto houver empréstimo vencido e não devolvido.
4. Quando `permitir_pedido_com_reserva_ativa` for `false`, recusar um novo
   pedido para título com reserva ativa do estudante. Quando for `true`,
   associar o pedido à reserva existente, sem criar uma reserva ativa duplicada.
5. Quando `exigir_autorizacao_bibliotecaria` for `true`, deixar o pedido elegível
   pendente para a equipe. Quando for `false`, aprová-lo automaticamente,
   preservando as demais validações.
6. Iniciar `prazo_emprestimo_dias` somente na retirada física confirmada.
   Aplicar `prazo_retirada_horas` à oferta de retirada da reserva.
7. Proteger operações concorrentes no backend: uma validação feita antes de
   uma gravação não substitui a revalidação no momento da gravação.

## Perfis aceitos nas operações

Atualizar os guards do backend, sem confiar na visão selecionada no navegador:

- Operações de estudante usadas na visão Estudante: perfil real `estudante`
  **ou** `admin`.
- Operações de equipe usadas na visão Bibliotecário: perfil real
  `bibliotecario` **ou** `admin`.
- Leitura/gravação de regras: leitura autenticada; gravação somente por `admin`.
- A sessão/token do admin continua sendo do admin. Os pedidos de teste ficam
  associados à própria conta admin; não criar identidade nem token substituto.

## Mensagens de regra

Retorne mensagens curtas em português no campo `message` do erro. A interface
preserva a referência de diagnóstico e exibe estas mensagens de negócio
permitidas, inclusive quando o Xano não enviar os acentos:

| Condição | Mensagem do Xano reconhecida | Texto mostrado ao usuário |
|---|---|---|
| Limite de empréstimos atingido | `Limite de emprestimos ativos atingido.` | A mensagem do Xano, em português |
| Limite de pedidos atingido | `Limite de pedidos em aberto atingido.` | A mensagem do Xano, em português |
| Reserva ativa impede novo pedido | `Pedido recusado por reserva ativa.` | A mensagem do Xano, em português |
| Atraso bloqueia operação | `Bloqueado por atraso de emprestimo.` | A mensagem do Xano, em português |
| Recusa de pedido que já mudou de estado | `Somente solicitacao pendente pode ser recusada` | `Só dá para recusar pedidos que ainda estão pendentes. A lista foi atualizada.` |
| Exemplar indisponível para retirada | `Nao ha exemplar disponivel para retirada` | `Não há exemplar disponível deste livro para retirada agora.` |

Para a equipe, um 403 por pedido que deixou de estar pendente deve provocar uma
única releitura das listas, sem repetir a escrita. Um 403 de perfil do admin em
visão simulada deve orientar a publicação deste contrato e não indicar sucesso.

## Como conferir no aplicativo

1. Depois de publicar, acesse `/regras` com a conta admin. Confira os sete
   valores; confirme que a tela mostra a data e o responsável quando a API
   retornar os metadados.
2. Altere uma regra válida e salve. Reabra a tela e confirme o valor persistido.
   Um valor inválido deve ser recusado sem gravação parcial; “Descartar
   mudanças” deve restaurar o último valor carregado.
3. Abra o detalhe de um livro autenticado como estudante e confirme a frase do
   limite vigente. Essa informação é apenas indicativa; teste também uma
   operação que atinja cada limite para confirmar a validação do servidor.
4. Na visão Estudante do admin, solicite um livro e confirme que o pedido fica
   no nome da própria conta admin. Na visão Bibliotecário, teste aceitar,
   recusar e registrar retirada conforme o estado e a disponibilidade.
5. Confira as mensagens e os estados no Request History do Xano. Não use dados
   reais de estudantes para testes; use contas e títulos sintéticos autorizados.

## Se algo der errado

- **A tela diz que as regras não foram publicadas:** confirme se
  `GET /configuracoes` existe e se permite leitura autenticada. Respostas 403
  ou 404 mantêm os padrões somente para consulta; não significam que esses
  padrões estão gravados no Xano.
- **Salvar retorna 403:** confirme que `PUT /admin/configuracoes` valida o
  perfil real `admin` e que a sessão utilizada é a conta admin.
- **Salvar retorna erro de validação:** compare nomes, tipos, faixas e booleanos
  com a tabela acima. O corpo de gravação não deve incluir metadados.
- **Ações simuladas retornam 403:** atualize os guards dos endpoints de
  estudante para `estudante OU admin` e os de equipe para
  `bibliotecario OU admin`; não altere o perfil real da sessão.
- **O aplicativo ainda mostra um valor anterior:** o cliente mantém a leitura
  em cache por até 60 segundos e invalida o cache depois de uma gravação
  bem-sucedida. Recarregue a página após esse período e confira o Request
  History antes de repetir qualquer escrita.
- Se a resposta continuar inesperada, anote a referência exibida pela
  interface, localize a chamada no terminal do backend e confira método, rota,
  status e corpo higienizado. Nunca compartilhe tokens, senhas ou URLs com
  credenciais.
