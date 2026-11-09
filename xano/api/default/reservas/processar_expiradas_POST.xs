query "admin/reservas/processar-expiradas" verb=POST {
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

    precondition ($usuario.perfil == "bibliotecario") {
      error_type = "accessdenied"
      error = "Perfil bibliotecario necessario."
    }

    var $agora {
      value = "now"|to_timestamp
    }

    db.query reserva {
      where = $db.reserva.estado == "ofertada" && $db.reserva.expira_em < $agora
    } as $expiradas

    var $expiradas_ordenadas {
      value = $expiradas|sort:"id":"number":true|sort:"expira_em":"number":true
    }

    var $processadas {
      value = 0
    }

    foreach ($expiradas_ordenadas) {
      each as $reserva_expirada {
        db.transaction {
          stack {
            db.patch reserva {
              field_name = "id"
              field_value = $reserva_expirada.id
              data = {estado: "expirada"}
            } as $reserva_atualizada

            db.get exemplar {
              field_name = "id"
              field_value = $reserva_expirada.exemplar_id
            } as $exemplar_expirado

            db.patch exemplar {
              field_name = "id"
              field_value = $reserva_expirada.exemplar_id
              data = {estado: "disponivel"}
            } as $exemplar_liberado

            db.query condicao_exemplar {
              where = $db.condicao_exemplar.exemplar_id == $reserva_expirada.exemplar_id
              return = {type: "count"}
            } as $condicoes

            conditional {
              if ($condicoes == 0) {
                db.query reserva {
                  where = $db.reserva.titulo_id == $reserva_expirada.titulo_id && $db.reserva.estado == "aguardando"
                } as $fila

                var $fila_reoferta_ordenada {
                  value = $fila|sort:"id":"number":true|sort:"criada_em":"number":true
                }

                var $proxima_reserva {
                  value = null
                }

                foreach ($fila_reoferta_ordenada) {
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
                          where = $db.emprestimo.usuario_id == $item.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.exemplar.titulo_id == $reserva_expirada.titulo_id
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
                    var $nova_ofertada_em {
                      value = "now"|to_timestamp
                    }

                    db.patch reserva {
                      field_name = "id"
                      field_value = $proxima_reserva.id
                      data = {}|set:"estado":"ofertada"|set:"exemplar_id":$exemplar_expirado.id|set:"ofertada_em":$nova_ofertada_em|set:"expira_em":($nova_ofertada_em|add_secs_to_timestamp:172800)
                    } as $nova_reserva_ofertada

                    db.patch exemplar {
                      field_name = "id"
                      field_value = $exemplar_expirado.id
                      data = {estado: "reservado"}
                    } as $exemplar_reofertado
                  }
                }
              }
              else {
                db.patch exemplar {
                  field_name = "id"
                  field_value = $exemplar_expirado.id
                  data = {estado: "indisponivel"}
                } as $exemplar_indisponivel
              }
            }

            var.update $processadas {
              value = $processadas + 1
            }
          }
        }
      }
    }
  }

  response = {reservas_expiradas_processadas: $processadas}
  guid = "UZ9mvPjQLH_osN0_Ui0T0SGhssI"
}
