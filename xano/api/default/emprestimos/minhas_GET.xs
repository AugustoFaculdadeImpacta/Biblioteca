query "minhas/emprestimos" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
  }

  stack {
    db.get usuario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfil"]
    } as $usuario

    precondition ($usuario.perfil == "estudante") {
      error_type = "accessdenied"
      error = "Somente estudantes podem consultar os proprios emprestimos."
    }

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $auth.id
      sort = {emprestimo.retirado_em: "desc"}
    } as $emprestimos
  }

  response = $emprestimos
  guid = "nK1bKfHafEb9zl1BMg2sEinnTrk"
}
