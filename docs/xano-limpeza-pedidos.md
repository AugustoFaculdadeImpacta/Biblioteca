# Limpeza manual de pedidos duplicados no Xano

## Por que existem duplicados

Cliques anteriores em “Reservar” podiam criar o pedido no Xano antes de a
interface conseguir confirmar pela releitura. Uma falha de leitura ou o limite
de chamadas podia fazer o usuário acreditar que o pedido não existia e clicar
novamente. O Xano real continuava recebendo os POST válidos.

## Identificar duplicados

No painel do Xano, compare os registros de solicitações por:

- `usuario_id`: estudante proprietário;
- `titulo_id`: livro solicitado;
- `estado`: preferencialmente `pendente` ou `em_reserva`;
- horário próximo ou igual de `solicitada_em`.

Um grupo com o mesmo `usuario_id` e `titulo_id`, repetido mais de uma vez,
é candidato a pedido duplicado. Confirme também se há reserva ligada pelo
campo `reserva_id`; não remova automaticamente registros atendidos,
recusados ou vinculados a empréstimo sem conferir o histórico.

## Limpeza segura pelo administrador

1. Faça backup/exportação dos registros de solicitações e reservas antes.
2. Abra o Request History para confirmar quais registros foram persistidos.
3. Identifique uma única solicitação válida pelo mesmo `usuario_id` e
   `titulo_id`.
4. No painel, desative ou exclua somente os registros repetidos, começando
   pelos mais recentes e documentando o identificador removido.
5. Confira em seguida as listas pessoais do estudante e reabra o pedido.

Não execute scripts, exclusões ou registros desta documentação; ela descreve
apenas um procedimento manual com backup.

## Estado desta versão

A prevenção local foi acrescentada ao aplicativo: quando as listas carregadas
já mostram pedido pendente/aprovado ou reserva ativa para o título, o POST não
é enviado e a interface orienta consultar Reservas. A regra remota não foi
publicada nesta Change. Os contratos XanoScript 5.3 e 5.4 continuam bloqueados
por `allow_push=false`, portanto o Xano real ainda aceita duplicados enviados
fora dessa prevenção local.
