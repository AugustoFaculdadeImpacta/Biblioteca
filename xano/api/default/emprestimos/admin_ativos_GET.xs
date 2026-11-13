query "admin/emprestimos" verb=GET {
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

    db.query emprestimo {
      where = $db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0
      sort = {emprestimo.vence_em: "asc", emprestimo.id: "asc"}
    } as $emprestimos_ativos

    var $resultado {
      value = []
    }

    foreach ($emprestimos_ativos) {
      each as $emprestimo {
        db.get usuario {
          field_name = "id"
          field_value = $emprestimo.usuario_id
          output = ["id", "nome"]
        } as $estudante

        db.get exemplar {
          field_name = "id"
          field_value = $emprestimo.exemplar_id
          output = ["id", "titulo_id"]
        } as $exemplar

        db.get titulo {
          field_name = "id"
          field_value = $exemplar.titulo_id
          output = ["id", "titulo", "autores"]
        } as $titulo

        var.update $resultado {
          value = $resultado|append:{
            id: $emprestimo.id
            usuario_id: $emprestimo.usuario_id
            usuario_nome: $estudante.nome
            titulo_id: $titulo.id
            titulo: $titulo.titulo
            autores: $titulo.autores
            exemplar_id: $emprestimo.exemplar_id
            retirado_em: $emprestimo.retirado_em
            vence_em: $emprestimo.vence_em
          }
        }
      }
    }
  }

  response = $resultado
}
