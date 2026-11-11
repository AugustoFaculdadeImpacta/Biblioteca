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

    db.query reserva {
      where = $db.reserva.titulo_id == $input.titulo_id && $db.reserva.estado == "aguardando"
    } as $fila

    var $fila_ordenada {
      value = $fila|sort:"id":"number":true|sort:"criada_em":"number":true
    }
  }

  response = $fila_ordenada
  guid = "iQCNvPkjq_-AgM1gIvb2l2k0J7E"
}
