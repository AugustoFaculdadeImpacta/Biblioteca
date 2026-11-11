query "catalogo/titulos/{titulo_id}" verb=GET {
  api_group = "Biblioteca"

  input {
    int titulo_id
  }

  stack {
    db.get titulo {
      field_name = "id"
      field_value = $input.titulo_id
    } as $titulo

    precondition ($titulo != null) {
      error_type = "notfound"
      error = "Titulo nao encontrado."
    }

    precondition ($titulo.ativo != false) {
      error_type = "notfound"
      error = "Titulo nao encontrado."
    }

    db.query exemplar {
      where = $db.exemplar.titulo_id == $input.titulo_id && $db.exemplar.estado == "disponivel"
      return = {type: "count"}
    } as $disponiveis

    db.query titulo_categoria {
      where = $db.titulo_categoria.titulo_id == $input.titulo_id
      return = {type: "list"}
    } as $categorias
  }

  response = {
    titulo: $titulo,
    categorias: $categorias,
    exemplares_disponiveis: $disponiveis
  }
  guid = "1MZVc7LLI_igRYobUqsOGiotEX0"
}
