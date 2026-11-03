query "minhas/reservas" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
  }

  stack {
    db.get usuario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfil"]
    } as $usuario

    precondition ($usuario.perfil == "estudante") {
      error_type = "accessdenied"
      error = "Somente estudantes podem consultar as proprias reservas."
    }

    db.query reserva {
      where = $db.reserva.usuario_id == $auth.id
      sort = {reserva.criada_em: "asc"}
      return = {type: "list"}
    } as $reservas

    var $resultado {
      value = []
    }

    foreach ($reservas) {
      each as $reserva {
        var $expira_em_sao_paulo {
          value = null
        }

        conditional {
          if ($reserva.expira_em != null) {
            var.update $expira_em_sao_paulo {
              value = $reserva.expira_em
                |format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo"
            }
          }
        }

        var $reserva_com_prazo {
          value = $reserva
            |set:"expira_em_sao_paulo":$expira_em_sao_paulo
        }

        var.update $resultado {
          value = $resultado|append:$reserva_com_prazo
        }
      }
    }
  }

  response = $resultado
  guid = "jd3wC3Qjl-AlDzzUDah5DQdSVCA"
}
