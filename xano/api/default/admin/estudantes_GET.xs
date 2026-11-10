// Busca uma conta estudante ativa por e-mail exato e retorna identidade minima.
query "admin/estudantes" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    email email filters=trim|lower
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

    precondition (!($input.email|contains:" ")) {
      error_type = "inputerror"
      error = "O e-mail nao pode conter espacos internos."
    }

    db.query usuario {
      where = $db.usuario.email == $input.email && $db.usuario.perfil == "estudante" && $db.usuario.ativo != false
      return = {type: "list"}
    } as $estudantes

    var $resultado {
      value = []
    }

    foreach ($estudantes) {
      each as $estudante {
        var.update $resultado {
          value = $resultado|append:{
            id: $estudante.id
            nome: $estudante.nome
          }
        }
      }
    }
  }

  response = $resultado
}
