query "minhas/solicitacoes" verb=GET {
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
      error = "Somente estudantes podem consultar as proprias solicitacoes."
    }

    db.query solicitacao_emprestimo {
      where = $db.solicitacao_emprestimo.usuario_id == $auth.id
      sort = {solicitacao_emprestimo.solicitada_em: "desc"}
    } as $solicitacoes
  }

  response = $solicitacoes
  guid = "Q2WTmCkt5auNYowuIPwwO92KfbY"
}
