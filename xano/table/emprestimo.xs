table emprestimo {
  schema {
    int id
    int usuario_id { table = "usuario" }
    int exemplar_id { table = "exemplar" }
    int solicitacao_id? { table = "solicitacao_emprestimo" }
    timestamp retirado_em
    timestamp vence_em
    timestamp devolvido_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "usuario_id", op: "asc"}, {name: "devolvido_em", op: "asc"}]}
    {type: "btree", field: [{name: "exemplar_id", op: "asc"}, {name: "devolvido_em", op: "asc"}]}
    {type: "btree", field: [{name: "vence_em", op: "asc"}]}
  ]
  guid = "EpL3kWYYsWXlJqjnWBlgDP9PsAE"
}
