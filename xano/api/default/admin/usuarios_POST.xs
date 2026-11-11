// Cria somente contas bibliotecarias; perfil e ativo sao definidos pelo servidor.
query "admin/usuarios" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    text nome filters=trim
    email email filters=trim|lower
    password senha
  }

  stack {
    db.get usuario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfil", "ativo"]
    } as $administrador

    precondition ($administrador.ativo != false) {
      error_type = "accessdenied"
      error = "Conta desativada."
    }

    precondition ($administrador.perfil == "admin") {
      error_type = "accessdenied"
      error = "Somente admin pode gerir bibliotecarios."
    }

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
      output = ["id"]
    } as $usuario_existente

    precondition ($usuario_existente == null) {
      error_type = "accessdenied"
      error = "Este e-mail ja esta cadastrado."
    }

    db.add usuario {
      data = {
        nome: $input.nome
        email: $input.email
        senha: $input.senha
        perfil: "bibliotecario"
        ativo: true
      }
    } as $novo_bibliotecario
  }

  response = {
    id: $novo_bibliotecario.id
    nome: $novo_bibliotecario.nome
    email: $novo_bibliotecario.email
    ativo: $novo_bibliotecario.ativo
  }
}
