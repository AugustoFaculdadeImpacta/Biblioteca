query "catalogo/categorias" verb=GET {
  api_group = "Biblioteca"

  input {
  }

  stack {
    db.query categoria as $categorias
  }

  response = $categorias
  guid = "hUlfu1BDvJoAHb2Lzdll3EsIgkc"
}
