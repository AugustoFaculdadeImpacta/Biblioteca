query "catalogo/titulos/{titulo_id}" verb=PATCH {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int titulo_id
    text titulo filters=trim
    text autores filters=trim
    text isbn?
    text editora?
    text edicao?
    int ano_publicacao?
    text descricao?
    bool ativo?
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

    precondition ($input.titulo != "" && $input.autores != "") {
      error_type = "inputerror"
      error = "Titulo e autores sao obrigatorios."
    }

    db.get titulo {
      field_name = "id"
      field_value = $input.titulo_id
    } as $titulo_existente

    precondition ($titulo_existente != null) {
      error_type = "notfound"
      error = "Titulo nao encontrado."
    }

    var $dados_atualizacao {
      value = {
        titulo: $input.titulo
        autores: $input.autores
        isbn: $input.isbn
        editora: $input.editora
        edicao: $input.edicao
        ano_publicacao: $input.ano_publicacao
        descricao: $input.descricao
      }
    }

    conditional {
      if ($input.ativo != null) {
        var.update $dados_atualizacao {
          value = $dados_atualizacao|set:"ativo":$input.ativo
        }
      }
    }

    db.transaction {
      stack {
        conditional {
          if ($input.ativo == false) {
            db.query emprestimo {
              join = {
                exemplar: {
                  table: "exemplar"
                  where: $db.emprestimo.exemplar_id == $db.exemplar.id
                }
              }
              where = $db.exemplar.titulo_id == $input.titulo_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0)
              return = {type: "count"}
            } as $emprestimos_ativos

            precondition ($emprestimos_ativos == 0) {
              error_type = "accessdenied"
              error = "A desativacao foi recusada: ha emprestimo ativo."
            }

            db.query reserva {
              where = $db.reserva.titulo_id == $input.titulo_id && ($db.reserva.estado == "aguardando" || $db.reserva.estado == "ofertada")
              return = {type: "count"}
            } as $reservas_ativas

            precondition ($reservas_ativas == 0) {
              error_type = "accessdenied"
              error = "A desativacao foi recusada: ha reserva ativa."
            }
          }
        }

        db.patch titulo {
          field_name = "id"
          field_value = $input.titulo_id
          data = $dados_atualizacao
        } as $titulo_atualizado
      }
    }
  }

  response = {
    id: $titulo_atualizado.id
    titulo: $titulo_atualizado.titulo
    autores: $titulo_atualizado.autores
    isbn: $titulo_atualizado.isbn
    editora: $titulo_atualizado.editora
    edicao: $titulo_atualizado.edicao
    ano_publicacao: $titulo_atualizado.ano_publicacao
    descricao: $titulo_atualizado.descricao
    ativo: $titulo_atualizado.ativo
  }
  guid = "2DGn41XXVeWJn4N18jeE89RvE7c"
}
