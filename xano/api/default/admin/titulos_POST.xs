query "catalogo/titulos" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    text titulo filters=trim
    text autores filters=trim
    text isbn?
    text editora?
    text edicao?
    int ano_publicacao?
    text descricao?
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

    db.add titulo {
      data = {
        titulo          : $input.titulo
        autores         : $input.autores
        isbn            : $input.isbn
        editora         : $input.editora
        edicao          : $input.edicao
        ano_publicacao  : $input.ano_publicacao
        descricao       : $input.descricao
      }
    } as $novo_titulo
  }

  response = $novo_titulo
  guid = "8xhkMx6rU1VmHIhLK7Tq6jUcdc8"
}
