query "solicitacoes-emprestimo" verb=POST {
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

    precondition ($usuario.perfil == "estudante") {
      error_type = "accessdenied"
      error = "Somente estudantes podem solicitar emprestimo."
    }

    db.get titulo {
      field_name = "id"
      field_value = $input.titulo_id
    } as $titulo

    precondition ($titulo != null) {
      error_type = "notfound"
      error = "Titulo nao encontrado."
    }

    var $agora {
      value = "now"|to_timestamp
    }

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $auth.id && $db.emprestimo.devolvido_em == null && $db.emprestimo.vence_em < $agora
      return = {type: "count"}
    } as $emprestimos_atrasados

    precondition ($emprestimos_atrasados == 0) {
      error_type = "accessdenied"
      error = "Emprestimo atrasado bloqueia novas solicitacoes."
    }

    db.query exemplar {
      where = $db.exemplar.titulo_id == $input.titulo_id && $db.exemplar.estado == "disponivel"
      return = {type: "count"}
    } as $exemplares_disponiveis

    db.query reserva {
      where = $db.reserva.titulo_id == $input.titulo_id && $db.reserva.estado == "aguardando"
      return = {type: "count"}
    } as $reservas_aguardando

    db.add solicitacao_emprestimo {
      data = {
        usuario_id: $auth.id
        titulo_id: $input.titulo_id
        estado: "pendente"
      }
    } as $solicitacao

    var $solicitacao_resultado {
      value = $solicitacao
    }

    conditional {
      if ($exemplares_disponiveis == 0 || $reservas_aguardando > 0) {
        db.query emprestimo {
          join = {
            exemplar: {
              table: "exemplar"
              where: $db.emprestimo.exemplar_id == $db.exemplar.id
            }
          }
          where = $db.emprestimo.usuario_id == $auth.id && $db.emprestimo.devolvido_em == null && $db.emprestimo.vence_em >= $agora && $db.exemplar.titulo_id == $input.titulo_id
          return = {type: "count"}
        } as $emprestimos_ativos_do_titulo

        precondition ($emprestimos_ativos_do_titulo == 0) {
          error_type = "accessdenied"
          error = "Nao e permitido reservar titulo ja emprestado a voce."
        }

        db.add reserva {
          data = {
            usuario_id: $auth.id
            titulo_id: $input.titulo_id
            estado: "aguardando"
          }
        } as $reserva

        db.patch solicitacao_emprestimo {
          field_name = "id"
          field_value = $solicitacao.id
          data = {}|set:"estado":"em_reserva"|set:"reserva_id":$reserva.id
        } as $solicitacao_atualizada

        var.update $solicitacao_resultado {
          value = $solicitacao_atualizada
        }
      }
    }
  }

  response = $solicitacao_resultado
  guid = "WrvWe1GX5b2AoMjUEajS7ENPWMo"
}
