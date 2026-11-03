query "admin/solicitacoes" verb=GET {
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

    precondition ($usuario.perfil == "bibliotecario") {
      error_type = "accessdenied"
      error = "Perfil bibliotecario necessario."
    }

    db.query solicitacao_emprestimo {
      where = $db.solicitacao_emprestimo.estado == "pendente"
      sort = {solicitacao_emprestimo.solicitada_em: "asc"}
    } as $solicitacoes
  }

  response = $solicitacoes
  guid = "hP8egOTsQHqnnKi_rqsbrXYznP0"
}
