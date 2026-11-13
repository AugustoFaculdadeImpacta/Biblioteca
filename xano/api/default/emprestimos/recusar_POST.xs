query "admin/solicitacoes/{solicitacao_id}/recusar" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int solicitacao_id
  }

  stack {
    db.get usuario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfil", "ativo"]
    } as $bibliotecario

    precondition ($bibliotecario.ativo != false) {
      error_type = "accessdenied"
      error = "Conta desativada."
    }

    precondition ($bibliotecario.perfil == "bibliotecario" || $bibliotecario.perfil == "admin") {
      error_type = "accessdenied"
      error = "Perfil bibliotecario ou admin necessario."
    }

    db.get solicitacao_emprestimo {
      field_name = "id"
      field_value = $input.solicitacao_id
    } as $solicitacao

    precondition ($solicitacao != null && $solicitacao.estado == "pendente") {
      error_type = "accessdenied"
      error = "Somente solicitacao pendente pode ser recusada."
    }

    db.patch solicitacao_emprestimo {
      field_name = "id"
      field_value = $solicitacao.id
      data = {estado: "recusada"}
    } as $solicitacao_recusada
  }

  response = $solicitacao_recusada
}
