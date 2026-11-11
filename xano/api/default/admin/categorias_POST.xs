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
