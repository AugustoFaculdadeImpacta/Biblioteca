table titulo_categoria {
  schema {
    int id
    int titulo_id { table = "titulo" }
    int categoria_id { table = "categoria" }
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "titulo_id", op: "asc"}, {name: "categoria_id", op: "asc"}]}
  ]
  guid = "ireCrI66lSPvCkneODicXpe5Vgw"
}
