query "admin/reservas" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
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

    db.query reserva {
      where = $db.reserva.estado == "aguardando" || $db.reserva.estado == "ofertada"
      sort = {reserva.criada_em: "asc", reserva.id: "asc"}
    } as $reservas_ativas

    var $resultado {
      value = []
    }

    foreach ($reservas_ativas) {
      each as $reserva {
        db.get usuario {
          field_name = "id"
          field_value = $reserva.usuario_id
          output = ["id", "nome"]
        } as $estudante

        db.get titulo {
          field_name = "id"
          field_value = $reserva.titulo_id
          output = ["id", "titulo"]
        } as $titulo

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

        var.update $resultado {
          value = $resultado|append:{
            id: $reserva.id
            usuario_id: $reserva.usuario_id
            usuario_nome: $estudante.nome
            titulo_id: $reserva.titulo_id
            titulo: $titulo.titulo
            estado: $reserva.estado
            criada_em: $reserva.criada_em
            exemplar_id: $reserva.exemplar_id
            ofertada_em: $reserva.ofertada_em
            expira_em: $reserva.expira_em
            expira_em_sao_paulo: $expira_em_sao_paulo
          }
        }
      }
    }
  }

  response = $resultado
}
