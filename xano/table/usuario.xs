table usuario {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    text nome filters=trim
    email email filters=trim|lower
    password senha {
      sensitive = true
      visibility = "internal"
    }
    enum perfil {
      values = ["estudante", "bibliotecario"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]
  guid = "A3p26pXCe-umou8YNb12XtduyaU"
}
