// Cria reserva administrativa; as validacoes de fila continuam no servidor.
query "admin/reservas" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int usuario_id
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

    db.get usuario {
      field_name = "id"
      field_value = $input.usuario_id
      output = ["id", "perfil", "ativo"]
    } as $estudante

    precondition ($estudante != null && $estudante.perfil == "estudante" && $estudante.ativo != false) {
      error_type = "notfound"
      error = "Estudante nao encontrado ou inativo."
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

    db.transaction {
      stack {
        var $agora {
          value = "now"|to_timestamp
        }

        db.query emprestimo {
          where = $db.emprestimo.usuario_id == $input.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.vence_em < $agora
          return = {type: "count"}
        } as $emprestimos_atrasados

        precondition ($emprestimos_atrasados == 0) {
          error_type = "accessdenied"
          error = "Estudante possui emprestimo atrasado."
        }

        db.query emprestimo {
          join = {
            exemplar: {
              table: "exemplar"
              where: $db.emprestimo.exemplar_id == $db.exemplar.id
            }
          }
          where = $db.emprestimo.usuario_id == $input.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.exemplar.titulo_id == $input.titulo_id
          return = {type: "count"}
        } as $emprestimos_do_titulo

        precondition ($emprestimos_do_titulo == 0) {
          error_type = "accessdenied"
          error = "Estudante ja possui o titulo emprestado."
        }

        db.query reserva {
          where = $db.reserva.usuario_id == $input.usuario_id && $db.reserva.titulo_id == $input.titulo_id && ($db.reserva.estado == "aguardando" || $db.reserva.estado == "ofertada")
          return = {type: "count"}
        } as $reservas_ativas

        precondition ($reservas_ativas == 0) {
          error_type = "accessdenied"
          error = "Estudante ja possui reserva ativa para este titulo."
        }

        db.add reserva {
          data = {
            usuario_id: $input.usuario_id
            titulo_id: $input.titulo_id
            estado: "aguardando"
          }
        } as $reserva
      }
    }
  }

  response = $reserva
}
