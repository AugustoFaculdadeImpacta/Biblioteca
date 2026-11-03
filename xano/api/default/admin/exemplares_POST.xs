query "admin/exemplares" verb=POST {
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

    precondition ($usuario.perfil == "bibliotecario") {
      error_type = "accessdenied"
      error = "Perfil bibliotecario necessario."
    }

    db.get titulo {
      field_name = "id"
      field_value = $input.titulo_id
    } as $titulo

    precondition ($titulo != null) {
      error_type = "notfound"
      error = "Titulo nao encontrado."
    }

    db.transaction {
      stack {
        db.add exemplar {
          data = {
            titulo_id: $input.titulo_id
            estado: "disponivel"
            codigo_tombo: null
          }
        } as $novo_exemplar

        var $sufixo {
          value = $novo_exemplar.id|to_text
        }

        precondition ($novo_exemplar.id <= 999999) {
          error_type = "inputerror"
          error = "Limite de codigos de tombo EX-999999 atingido."
        }

        conditional {
          if ($novo_exemplar.id < 10) {
            var.update $sufixo {
              value = "00000"|concat:$sufixo
            }
          }
        }
        conditional {
          if ($novo_exemplar.id >= 10 && $novo_exemplar.id < 100) {
            var.update $sufixo {
              value = "0000"|concat:$sufixo
            }
          }
        }
        conditional {
          if ($novo_exemplar.id >= 100 && $novo_exemplar.id < 1000) {
            var.update $sufixo {
              value = "000"|concat:$sufixo
            }
          }
        }
        conditional {
          if ($novo_exemplar.id >= 1000 && $novo_exemplar.id < 10000) {
            var.update $sufixo {
              value = "00"|concat:$sufixo
            }
          }
        }
        conditional {
          if ($novo_exemplar.id >= 10000 && $novo_exemplar.id < 100000) {
            var.update $sufixo {
              value = "0"|concat:$sufixo
            }
          }
        }

        db.patch exemplar {
          field_name = "id"
          field_value = $novo_exemplar.id
          data = {}|set:"codigo_tombo":("EX-"|concat:$sufixo)
        } as $exemplar_criado
      }
    }
  }

  response = $exemplar_criado
  guid = "q9qjPxsPsZr36wOwjJUsRPrEnSU"
}
