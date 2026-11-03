table exemplar {
  schema {
    int id
    int titulo_id { table = "titulo" }
    text codigo_tombo?
    enum estado {
      values = ["disponivel", "reservado", "emprestado", "indisponivel"]
    }
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "codigo_tombo", op: "asc"}]}
    {type: "btree", field: [{name: "titulo_id", op: "asc"}]}
    {type: "btree", field: [{name: "estado", op: "asc"}]}
  ]
  guid = "kp1x0pukoaYIr6ulFhJCy38Wbok"
}
