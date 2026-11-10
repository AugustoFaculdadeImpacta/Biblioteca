query "catalogo/categorias/{categoria_id}" verb=PATCH {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int categoria_id
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

    db.get categoria {
      field_name = "id"
      field_value = $input.categoria_id
    } as $categoria_existente

    precondition ($categoria_existente != null) {
      error_type = "notfound"
      error = "Categoria nao encontrada."
    }

    db.patch categoria {
      field_name = "id"
      field_value = $input.categoria_id
      data = {nome: $input.nome}
    } as $categoria_atualizada
  }

  response = $categoria_atualizada
  guid = "4qZk5S6euRv6RtXLGERTFoW9DSM"
}
