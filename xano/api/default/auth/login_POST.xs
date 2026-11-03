// Login de estudante ou de bibliotecário provisionado.
query "auth/login" verb=POST {
  api_group = "Biblioteca"

  input {
    email email filters=trim|lower
    password senha
  }

  stack {
    precondition (!($input.email|contains:" ")) {
      error_type = "inputerror"
      error = "O e-mail nao pode conter espacos internos."
    }

    db.get usuario {
      field_name = "email"
      field_value = $input.email
      output = ["id", "nome", "email", "senha", "perfil"]
    } as $usuario

    precondition ($usuario != null) {
      error = "Credenciais inválidas."
    }

    security.check_password {
      text_password = $input.senha
      hash_password = $usuario.senha
    } as $senha_valida

    precondition ($senha_valida) {
      error = "Credenciais inválidas."
    }

    security.create_auth_token {
      table = "usuario"
      extras = {}
      expiration = 86400
      id = $usuario.id
    } as $authToken
  }

  response = {
    authToken: $authToken
    usuario: {
      id: $usuario.id
      nome: $usuario.nome
      email: $usuario.email
      perfil: $usuario.perfil
    }
  }
  guid = "YizbhwNyoY5oz-qT8ZsofKo3WWc"
}
