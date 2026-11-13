table reserva {
  schema {
    int id
    int usuario_id { table = "usuario" }
    int titulo_id { table = "titulo" }
    timestamp criada_em?=now
    enum estado {
      values = ["aguardando", "ofertada", "retirada", "expirada", "recusada"]
    }
    int exemplar_id? { table = "exemplar" }
    timestamp ofertada_em?
    timestamp expira_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "titulo_id", op: "asc"}, {name: "criada_em", op: "asc"}, {name: "id", op: "asc"}]}
    {type: "btree", field: [{name: "usuario_id", op: "asc"}, {name: "titulo_id", op: "asc"}, {name: "estado", op: "asc"}]}
    {type: "btree", field: [{name: "estado", op: "asc"}, {name: "expira_em", op: "asc"}]}
  ]
  guid = "XYWfcliO7lKn4jXVlNfToWd-t3s"
}
