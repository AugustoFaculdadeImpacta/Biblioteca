query "catalogo/categorias" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    text nome filters=trim
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

    precondition ($input.nome != "") {
      error_type = "inputerror"
      error = "Nome da categoria obrigatorio."
    }

    db.add categoria {
      data = {
        nome: $input.nome
      }
    } as $nova_categoria
  }

  response = $nova_categoria
  guid = "6tgtpEJzxZoE0_41MGgZc-5R1Xo"
}
