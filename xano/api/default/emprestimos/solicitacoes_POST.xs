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

    precondition ($titulo.ativo != false) {
      error_type = "accessdenied"
      error = "Titulo inativo nao aceita novas solicitacoes."
    }

    var $agora {
      value = "now"|to_timestamp
    }

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $auth.id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.vence_em < $agora
      return = {type: "count"}
    } as $emprestimos_atrasados

    precondition ($emprestimos_atrasados == 0) {
      error_type = "accessdenied"
      error = "Emprestimo atrasado bloqueia novas solicitacoes."
    }

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $auth.id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0)
      return = {type: "count"}
    } as $emprestimos_ativos

    precondition ($emprestimos_ativos < 3) {
      error_type = "accessdenied"
      error = "Limite de tres emprestimos ativos atingido."
    }

    db.query exemplar {
      where = $db.exemplar.titulo_id == $input.titulo_id
      return = {type: "list"}
    } as $exemplares_titulo

    array.map ($exemplares_titulo) {
      by = $this.id
    } as $exemplar_ids

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $auth.id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.exemplar_id in ($exemplar_ids)
      return = {type: "count"}
    } as $emprestimos_do_titulo

    precondition ($emprestimos_do_titulo == 0) {
      error_type = "accessdenied"
      error = "Nao e permitido solicitar titulo ja emprestado a voce."
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
