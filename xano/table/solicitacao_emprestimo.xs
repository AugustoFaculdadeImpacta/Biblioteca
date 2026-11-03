table solicitacao_emprestimo {
  schema {
    int id
    int usuario_id { table = "usuario" }
    int titulo_id { table = "titulo" }
    timestamp solicitada_em?=now
    enum estado {
      values = ["pendente", "em_reserva", "atendida", "recusada"]
    }
    int reserva_id? { table = "reserva" }
    timestamp atendida_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "usuario_id", op: "asc"}, {name: "solicitada_em", op: "asc"}]}
    {type: "btree", field: [{name: "titulo_id", op: "asc"}, {name: "estado", op: "asc"}]}
  ]
  guid = "ujAFJ9nauhLDBWFhkbrHGweSAG0"
}
