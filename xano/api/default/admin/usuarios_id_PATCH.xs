// Altera somente a situacao de uma conta bibliotecaria.
query "admin/usuarios/{usuario_id}" verb=PATCH {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int usuario_id
    bool ativo
  }

  stack {
    db.get usuario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfil", "ativo"]
    } as $administrador

    precondition ($administrador.ativo != false) {
      error_type = "accessdenied"
      error = "Conta desativada."
    }

    precondition ($administrador.perfil == "admin") {
      error_type = "accessdenied"
      error = "Somente admin pode gerir bibliotecarios."
    }

    precondition ($input.usuario_id != $auth.id) {
      error_type = "accessdenied"
      error = "Admin nao pode alterar a propria conta."
    }

    db.get usuario {
      field_name = "id"
      field_value = $input.usuario_id
      output = ["id", "nome", "email", "perfil", "ativo"]
    } as $bibliotecario

    precondition ($bibliotecario != null) {
      error_type = "notfound"
      error = "Bibliotecario nao encontrado."
    }

    precondition ($bibliotecario.perfil == "bibliotecario") {
      error_type = "accessdenied"
      error = "Somente contas bibliotecarias podem ser alteradas."
    }

    db.patch usuario {
      field_name = "id"
      field_value = $input.usuario_id
      data = {ativo: $input.ativo}
    } as $bibliotecario_atualizado
  }

  response = {
    id: $bibliotecario_atualizado.id
    nome: $bibliotecario_atualizado.nome
    email: $bibliotecario_atualizado.email
    ativo: $bibliotecario_atualizado.ativo
  }
}
