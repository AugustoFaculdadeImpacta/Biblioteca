query "reservas" verb=POST {
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
      error = "Somente estudantes podem criar reservas."
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
      error = "Titulo inativo nao aceita novas reservas."
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
      error = "Emprestimo atrasado bloqueia reservas."
    }

    db.query emprestimo {
      join = {
        exemplar: {
          table: "exemplar"
          where: $db.emprestimo.exemplar_id == $db.exemplar.id
        }
      }
      where = $db.emprestimo.usuario_id == $auth.id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.exemplar.titulo_id == $input.titulo_id
      return = {type: "count"}
    } as $emprestimos_do_titulo

    precondition ($emprestimos_do_titulo == 0) {
      error_type = "accessdenied"
      error = "Nao e permitido reservar titulo ja emprestado a voce."
    }

    db.query reserva {
      where = $db.reserva.usuario_id == $auth.id && $db.reserva.titulo_id == $input.titulo_id && ($db.reserva.estado == "aguardando" || $db.reserva.estado == "ofertada")
      return = {type: "count"}
    } as $reservas_ativas

    precondition ($reservas_ativas == 0) {
      error_type = "accessdenied"
      error = "Ja existe reserva ativa para este titulo."
    }

    db.add reserva {
      data = {
        usuario_id: $auth.id
        titulo_id: $input.titulo_id
        estado: "aguardando"
      }
    } as $reserva
  }

  response = $reserva
  guid = "HzMiSiwh71BmpJ2kxTlsKx5e788"
}
