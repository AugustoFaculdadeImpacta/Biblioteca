table categoria {
  schema {
    int id
    timestamp created_at?=now
    text nome filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "nome", op: "asc"}]}
  ]
  guid = "otbNod0fXlDugytD9s7PF6KNapE"
}
