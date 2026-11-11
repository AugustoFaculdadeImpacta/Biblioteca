table titulo {
  schema {
    int id
    timestamp created_at?=now
    text titulo filters=trim
    text autores filters=trim
    text isbn?
    text editora?
    text edicao?
    int ano_publicacao?
    text descricao?
    bool ativo?=true
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "titulo", op: "asc"}]}
  ]
  guid = "VsCMfcV707HGzg4Tbmgrx8Eaacs"
}
