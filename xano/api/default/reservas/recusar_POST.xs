query "admin/reservas/{reserva_id}/recusar" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int reserva_id
  }

  stack {
    db.get usuario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfil", "ativo"]
    } as $bibliotecario

    precondition ($bibliotecario.ativo != false) {
      error_type = "accessdenied"
      error = "Conta desativada."
    }

    precondition ($bibliotecario.perfil == "bibliotecario" || $bibliotecario.perfil == "admin") {
      error_type = "accessdenied"
      error = "Perfil bibliotecario ou admin necessario."
    }

    db.transaction {
      stack {
        db.get reserva {
          field_name = "id"
          field_value = $input.reserva_id
        } as $reserva

        precondition ($reserva != null && $reserva.estado == "aguardando") {
          error_type = "accessdenied"
          error = "Somente reserva aguardando pode ser recusada."
        }

        db.patch reserva {
          field_name = "id"
          field_value = $reserva.id
          data = {estado: "recusada"}
        } as $reserva_recusada

        db.query solicitacao_emprestimo {
          where = $db.solicitacao_emprestimo.reserva_id == $reserva.id && $db.solicitacao_emprestimo.estado == "em_reserva"
          return = {type: "single"}
        } as $solicitacao

        conditional {
          if ($solicitacao != null) {
            db.patch solicitacao_emprestimo {
              field_name = "id"
              field_value = $solicitacao.id
              data = {estado: "recusada"}
            } as $solicitacao_recusada
          }
        }
      }
    }
  }

  response = $reserva_recusada
}
