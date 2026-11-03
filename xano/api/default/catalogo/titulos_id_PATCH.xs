query "catalogo/titulos/{titulo_id}" verb=PATCH {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int titulo_id
    text titulo filters=trim
    text autores filters=trim
    text isbn?
    text editora?
    text edicao?
    int ano_publicacao?
    text descricao?
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

    precondition ($input.titulo != "" && $input.autores != "") {
      error_type = "inputerror"
      error = "Titulo e autores sao obrigatorios."
    }

    db.get titulo {
      field_name = "id"
      field_value = $input.titulo_id
    } as $titulo_existente

    precondition ($titulo_existente != null) {
      error_type = "notfound"
      error = "Titulo nao encontrado."
    }

    db.patch titulo {
      field_name = "id"
      field_value = $input.titulo_id
      data = {
        titulo: $input.titulo
        autores: $input.autores
        isbn: $input.isbn
        editora: $input.editora
        edicao: $input.edicao
        ano_publicacao: $input.ano_publicacao
        descricao: $input.descricao
      }
    } as $titulo_atualizado
  }

  response = $titulo_atualizado
  guid = "2DGn41XXVeWJn4N18jeE89RvE7c"
}
