query "admin/titulos/{titulo_id}/categorias" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int titulo_id
    int categoria_id
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

    db.get titulo {
      field_name = "id"
      field_value = $input.titulo_id
    } as $titulo

    precondition ($titulo != null) {
      error_type = "notfound"
      error = "Titulo nao encontrado."
    }

    db.get categoria {
      field_name = "id"
      field_value = $input.categoria_id
    } as $categoria

    precondition ($categoria != null) {
      error_type = "notfound"
      error = "Categoria nao encontrada."
    }

    db.query titulo_categoria {
      where = $db.titulo_categoria.titulo_id == $input.titulo_id && $db.titulo_categoria.categoria_id == $input.categoria_id
      return = {type: "single"}
    } as $associacao_existente

    precondition ($associacao_existente == null) {
      error_type = "accessdenied"
      error = "A categoria ja esta associada ao titulo."
    }

    db.add titulo_categoria {
      data = {
        titulo_id   : $input.titulo_id
        categoria_id: $input.categoria_id
      }
    } as $associacao
  }

  response = $associacao
  guid = "b0ouT7M__59Rok12ebtspQF1cOU"
}
