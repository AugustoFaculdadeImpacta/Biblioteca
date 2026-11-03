query "admin/exemplares/{exemplar_id}/condicoes" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int exemplar_id
    enum tipo {
      values = ["danificado", "perdido"]
    }
    text observacao filters=trim
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

    precondition ($input.observacao != "") {
      error_type = "inputerror"
      error = "Observacao obrigatoria."
    }

    db.get exemplar {
      field_name = "id"
      field_value = $input.exemplar_id
    } as $exemplar

    precondition ($exemplar != null) {
      error_type = "notfound"
      error = "Exemplar nao encontrado."
    }

    db.transaction {
      stack {
        db.add condicao_exemplar {
          data = {
            exemplar_id: $exemplar.id
            tipo: $input.tipo
            observacao: $input.observacao
            registrado_por: $auth.id
          }
        } as $condicao

        db.patch exemplar {
          field_name = "id"
          field_value = $exemplar.id
          data = {estado: "indisponivel"}
        } as $exemplar_indisponivel
      }
    }
  }

  response = $condicao
  guid = "1USwN8KuDB1Ig77gsaZ0LzKCOkI"
}
