query "admin/reservas/{reserva_id}/retirada" verb=POST {
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
    } as $usuario

    precondition ($usuario.ativo != false) {
      error_type = "accessdenied"
      error = "Conta desativada."
    }

    precondition ($usuario.perfil == "bibliotecario" || $usuario.perfil == "admin") {
      error_type = "accessdenied"
      error = "Perfil bibliotecario ou admin necessario."
    }

    db.get reserva {
      field_name = "id"
      field_value = $input.reserva_id
    } as $reserva

    var $agora {
      value = "now"|to_timestamp
    }

    precondition ($reserva != null && $reserva.estado == "ofertada" && $reserva.expira_em > $agora && $reserva.exemplar_id != null) {
      error_type = "accessdenied"
      error = "Reserva sem oferta vigente."
    }

    db.get exemplar {
      field_name = "id"
      field_value = $reserva.exemplar_id
    } as $exemplar

    precondition ($exemplar != null && $exemplar.estado == "reservado") {
      error_type = "accessdenied"
      error = "Exemplar nao esta reservado para esta oferta."
    }

    db.query condicao_exemplar {
      where = $db.condicao_exemplar.exemplar_id == $exemplar.id
      return = {type: "count"}
    } as $condicoes

    precondition ($condicoes == 0) {
      error_type = "accessdenied"
      error = "Exemplar com condicao registrada nao pode ser emprestado."
    }

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $reserva.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0)
      return = {type: "count"}
    } as $emprestimos_ativos

    precondition ($emprestimos_ativos < 3) {
      error_type = "accessdenied"
      error = "Limite de tres emprestimos ativos atingido."
    }

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $reserva.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.vence_em < $agora
      return = {type: "count"}
    } as $emprestimos_atrasados

    precondition ($emprestimos_atrasados == 0) {
      error_type = "accessdenied"
      error = "Estudante com emprestimo atrasado."
    }

    db.query exemplar {
      where = $db.exemplar.titulo_id == $exemplar.titulo_id
      return = {type: "list"}
    } as $exemplares_titulo

    array.map ($exemplares_titulo) {
      by = $this.id
    } as $exemplar_ids

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $reserva.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.exemplar_id in ($exemplar_ids)
      return = {type: "count"}
    } as $emprestimos_do_titulo

    precondition ($emprestimos_do_titulo == 0) {
      error_type = "accessdenied"
      error = "Estudante ja possui o titulo emprestado."
    }

    var $vence_em {
      value = $agora|add_secs_to_timestamp:1209600
    }

    db.transaction {
      stack {
        db.add emprestimo {
          data = {
            usuario_id: $reserva.usuario_id
            exemplar_id: $exemplar.id
            retirado_em: $agora
            vence_em: $vence_em
          }
        } as $emprestimo

        db.patch reserva {
          field_name = "id"
          field_value = $reserva.id
          data = {estado: "retirada"}
        } as $reserva_retirada

        db.patch exemplar {
          field_name = "id"
          field_value = $exemplar.id
          data = {estado: "emprestado"}
        } as $exemplar_emprestado

        db.query solicitacao_emprestimo {
          where = $db.solicitacao_emprestimo.reserva_id == $reserva.id && $db.solicitacao_emprestimo.estado == "em_reserva"
          return = {type: "single"}
        } as $solicitacao

        conditional {
          if ($solicitacao != null) {
            db.patch solicitacao_emprestimo {
              field_name = "id"
              field_value = $solicitacao.id
              data = {}|set:"estado":"atendida"|set:"atendida_em":$agora
            } as $solicitacao_atendida
          }
        }
      }
    }
  }

  response = $emprestimo
  guid = "EN_fBSHgCm2ezRDvwluZ6zqvLgY"
}
