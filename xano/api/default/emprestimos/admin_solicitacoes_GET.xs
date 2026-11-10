query "admin/solicitacoes" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
  }

  stack {
    db.get usuario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfil", "ativo"]
    } as $usuario

    precondition ($usuario.ativo != false) {
      error_type = "accessdenied"
      error = "Conta desativada."
    }

    precondition ($usuario.perfil == "bibliotecario" || $usuario.perfil == "admin") {
      error_type = "accessdenied"
      error = "Perfil bibliotecario ou admin necessario."
    }

    db.query solicitacao_emprestimo {
      where = $db.solicitacao_emprestimo.estado == "pendente"
      sort = {solicitacao_emprestimo.solicitada_em: "asc"}
    } as $solicitacoes
  }

  response = $solicitacoes
  guid = "hP8egOTsQHqnnKi_rqsbrXYznP0"
}
