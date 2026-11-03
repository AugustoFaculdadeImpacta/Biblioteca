table condicao_exemplar {
  schema {
    int id
    int exemplar_id { table = "exemplar" }
    enum tipo {
      values = ["danificado", "perdido"]
    }
    text observacao filters=trim
    timestamp registrado_em?=now
    int registrado_por { table = "usuario" }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "exemplar_id", op: "asc"}, {name: "registrado_em", op: "desc"}]}
  ]
  guid = "tOFrrtM3OK1LLUS3N4sI5sAt3sE"
}
