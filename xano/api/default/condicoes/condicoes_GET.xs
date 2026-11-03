query "admin/exemplares/{exemplar_id}/condicoes" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int exemplar_id
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

    db.get exemplar {
      field_name = "id"
      field_value = $input.exemplar_id
    } as $exemplar

    precondition ($exemplar != null) {
      error_type = "notfound"
      error = "Exemplar nao encontrado."
    }

    db.query condicao_exemplar {
      where = $db.condicao_exemplar.exemplar_id == $input.exemplar_id
      sort = {condicao_exemplar.registrado_em: "desc"}
    } as $condicoes
  }

  response = $condicoes
  guid = "YcEYZQRD-lUYbtadJVzHYEY2IjY"
}
