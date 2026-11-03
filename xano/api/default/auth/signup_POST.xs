// Cadastro publico; o cliente nunca escolhe o perfil.
query "auth/signup" verb=POST {
  api_group = "Biblioteca"

  input {
    text nome filters=trim
    email email filters=trim|lower
    password senha
  }

  stack {
    precondition ($input.nome != "") {
      error_type = "inputerror"
      error = "Nome obrigatorio."
    }

    precondition (!($input.email|contains:" ")) {
      error_type = "inputerror"
      error = "O e-mail nao pode conter espacos internos."
    }

    db.get usuario {
      field_name = "email"
      field_value = $input.email
    } as $usuario_existente

    precondition ($usuario_existente == null) {
      error_type = "accessdenied"
      error = "Este e-mail já está cadastrado."
    }

    db.add usuario {
      data = {
        nome   : $input.nome
        email  : $input.email
        senha  : $input.senha
        perfil : "estudante"
      }
    } as $usuario

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
  guid = "OHkHIsgzRe2QDsnRG3rFfWmGLC4"
}
