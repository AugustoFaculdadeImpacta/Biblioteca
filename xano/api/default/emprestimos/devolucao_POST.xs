query "admin/emprestimos/{emprestimo_id}/devolucao" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int emprestimo_id
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

    db.get emprestimo {
      field_name = "id"
      field_value = $input.emprestimo_id
    } as $emprestimo

    precondition ($emprestimo != null && ($emprestimo.devolvido_em == null || $emprestimo.devolvido_em == 0)) {
      error_type = "notfound"
      error = "Emprestimo ativo nao encontrado."
    }

    var $agora {
      value = "now"|to_timestamp
    }

    db.patch emprestimo {
      field_name = "id"
      field_value = $emprestimo.id
      data = {}|set:"devolvido_em":$agora
    } as $emprestimo_devolvido

    db.query condicao_exemplar {
      where = $db.condicao_exemplar.exemplar_id == $emprestimo.exemplar_id
      return = {type: "count"}
    } as $condicoes

    db.get exemplar {
      field_name = "id"
      field_value = $emprestimo.exemplar_id
    } as $exemplar

    var $reserva_ofertada {
      value = null
    }

    conditional {
      if ($condicoes == 0) {
        db.patch exemplar {
          field_name = "id"
          field_value = $emprestimo.exemplar_id
          data = {estado: "disponivel"}
        } as $exemplar_disponivel

        db.query reserva {
          where = $db.reserva.titulo_id == $exemplar.titulo_id && $db.reserva.estado == "aguardando"
          sort = {reserva.criada_em: "asc", reserva.id: "asc"}
        } as $fila

        var $proxima_reserva {
          value = null
        }

        foreach ($fila) {
          each as $item {
            conditional {
              if ($proxima_reserva == null) {
                db.query emprestimo {
                  where = $db.emprestimo.usuario_id == $item.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.vence_em < $agora
                  return = {type: "count"}
                } as $atrasados

                db.query emprestimo {
                  join = {
                    exemplar: {
                      table: "exemplar"
                      where: $db.emprestimo.exemplar_id == $db.exemplar.id
                    }
                  }
                  where = $db.emprestimo.usuario_id == $item.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.exemplar.titulo_id == $exemplar.titulo_id
                  return = {type: "count"}
                } as $emprestimos_do_titulo

                conditional {
                  if ($atrasados == 0 && $emprestimos_do_titulo == 0) {
                    var.update $proxima_reserva {
                      value = $item
                    }
                  }
                }
              }
            }
          }
        }

        conditional {
          if ($proxima_reserva != null) {
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
                  field_value = $proxima_reserva.id
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
        }
      }
      else {
        db.patch exemplar {
          field_name = "id"
          field_value = $emprestimo.exemplar_id
          data = {estado: "indisponivel"}
        } as $exemplar_indisponivel
      }
    }
  }

  response = {emprestimo: $emprestimo_devolvido, reserva_ofertada: $reserva_ofertada}
  guid = "C92YTbhJYTfhgKcz_SiLLEpokAk"
}
