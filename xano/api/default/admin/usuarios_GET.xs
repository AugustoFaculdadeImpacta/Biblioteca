// Lista somente dados publicos de contas bibliotecarias.
query "admin/usuarios" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
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

    db.query usuario {
      where = $db.usuario.perfil == "bibliotecario"
      return = {type: "list"}
    } as $bibliotecarios

    var $resultado {
      value = []
    }

    foreach ($bibliotecarios) {
      each as $bibliotecario {
        var.update $resultado {
          value = $resultado|append:{
            id: $bibliotecario.id
            nome: $bibliotecario.nome
            email: $bibliotecario.email
            ativo: $bibliotecario.ativo != false
          }
        }
      }
    }
  }

  response = $resultado
}
