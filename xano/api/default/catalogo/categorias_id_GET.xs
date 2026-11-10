query "catalogo/categorias/{categoria_id}" verb=GET {
  api_group = "Biblioteca"

  input {
    int categoria_id
  }

  stack {
    db.get categoria {
      field_name = "id"
      field_value = $input.categoria_id
    } as $categoria

    precondition ($categoria != null) {
      error_type = "notfound"
      error = "Categoria nao encontrada."
    }

    db.query titulo_categoria {
      where = $db.titulo_categoria.categoria_id == $input.categoria_id
      return = {type: "list"}
    } as $associacoes

    array.map ($associacoes) {
      by = $this.titulo_id
    } as $titulo_ids

    db.query titulo {
      where = $db.titulo.id in ($titulo_ids)
      return = {type: "list"}
    } as $titulos
  }

  response = {categoria: $categoria, titulos: $titulos}
  guid = "EXPdKeHFsIXWAHn8KjDMqFTR4kM"
}
