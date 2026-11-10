// Lista todo o acervo para bibliotecario ou admin, inclusive titulos inativos.
query "admin/acervo" verb=GET {
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

    db.query titulo as $titulos

    var $resultado {
      value = []
    }

    foreach ($titulos) {
      each as $titulo {
        db.query exemplar {
          where = $db.exemplar.titulo_id == $titulo.id
        } as $exemplares

        db.query exemplar {
          where = $db.exemplar.titulo_id == $titulo.id && $db.exemplar.estado == "disponivel"
          return = {type: "count"}
        } as $disponiveis

        db.query titulo_categoria {
          where = $db.titulo_categoria.titulo_id == $titulo.id
        } as $categorias

        var.update $resultado {
          value = $resultado|append:{
            titulo: $titulo,
            categorias: $categorias,
            exemplares: $exemplares,
            exemplares_disponiveis: $disponiveis
          }
        }
      }
    }
  }

  response = $resultado
}
