query "admin/titulos/{titulo_id}/fila-reservas" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int titulo_id
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

    db.get titulo {
      field_name = "id"
      field_value = $input.titulo_id
    } as $titulo

    precondition ($titulo != null) {
      error_type = "notfound"
      error = "Titulo nao encontrado."
    }

    db.query reserva {
      where = $db.reserva.titulo_id == $input.titulo_id && $db.reserva.estado == "aguardando"
      sort = {reserva.criada_em: "asc", reserva.id: "asc"}
    } as $fila
  }

  response = $fila
  guid = "iQCNvPkjq_-AgM1gIvb2l2k0J7E"
}
