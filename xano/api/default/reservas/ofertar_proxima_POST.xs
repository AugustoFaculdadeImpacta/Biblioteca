query "admin/reservas/ofertar-proxima" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int titulo_id
    int exemplar_id
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

    db.get exemplar {
      field_name = "id"
      field_value = $input.exemplar_id
    } as $exemplar

    precondition ($exemplar != null && $exemplar.titulo_id == $input.titulo_id && $exemplar.estado == "disponivel") {
      error_type = "inputerror"
      error = "Exemplar disponivel do titulo informado necessario."
    }

    var $agora {
      value = "now"|to_timestamp
    }

    db.query reserva {
      where = $db.reserva.titulo_id == $input.titulo_id && $db.reserva.estado == "aguardando"
    } as $fila

    var $fila_ordenada {
      value = $fila|sort:"id":"number":true|sort:"criada_em":"number":true
    }

    var $reserva_escolhida {
      value = null
    }

    foreach ($fila_ordenada) {
      each as $item {
        conditional {
          if ($reserva_escolhida == null) {
            db.query emprestimo {
              where = $db.emprestimo.usuario_id == $item.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.vence_em < $agora
              return = {type: "count"}
            } as $atrasados

            db.query emprestimo {
              where = $db.emprestimo.usuario_id == $item.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0)
              return = {type: "count"}
            } as $emprestimos_ativos

            db.query exemplar {
              where = $db.exemplar.titulo_id == $input.titulo_id
              return = {type: "list"}
            } as $exemplares_titulo

            array.map ($exemplares_titulo) {
              by = $this.id
            } as $exemplar_ids

            db.query emprestimo {
              where = $db.emprestimo.usuario_id == $item.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.exemplar_id in ($exemplar_ids)
              return = {type: "count"}
            } as $emprestimos_do_titulo

            conditional {
              if ($atrasados == 0 && $emprestimos_ativos < 3 && $emprestimos_do_titulo == 0) {
                var.update $reserva_escolhida {
                  value = $item
                }
              }
            }
          }
        }
      }
    }

    precondition ($reserva_escolhida != null) {
      error_type = "notfound"
      error = "Nao ha reserva elegivel na fila."
    }

    var $ofertada_em {
      value = "now"|to_timestamp
    }

    var $expira_em {
      value = $ofertada_em|add_secs_to_timestamp:172800
    }

    db.transaction {
      stack {
        db.patch reserva {
          field_name = "id"
          field_value = $reserva_escolhida.id
          data = {}|set:"estado":"ofertada"|set:"exemplar_id":$exemplar.id|set:"ofertada_em":$ofertada_em|set:"expira_em":$expira_em
        } as $reserva_ofertada

        db.patch exemplar {
          field_name = "id"
          field_value = $exemplar.id
          data = {estado: "reservado"}
        } as $exemplar_reservado
      }
    }
  }

  response = {
    reserva: $reserva_ofertada,
    expira_em_utc: $expira_em,
    expira_em_sao_paulo: $expira_em|format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo"
  }
  guid = "WEgGvGLA0p6QpdFSDeKabYi43mw"
}
