query "admin/solicitacoes/{solicitacao_id}/retirada" verb=POST {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
    int solicitacao_id
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

    db.get solicitacao_emprestimo {
      field_name = "id"
      field_value = $input.solicitacao_id
    } as $solicitacao

    precondition ($solicitacao != null && $solicitacao.estado == "pendente") {
      error_type = "notfound"
      error = "Solicitacao pendente nao encontrada."
    }

    db.query solicitacao_emprestimo {
      where = $db.solicitacao_emprestimo.titulo_id == $solicitacao.titulo_id && $db.solicitacao_emprestimo.estado == "pendente"
      sort = {solicitacao_emprestimo.solicitada_em: "asc", solicitacao_emprestimo.id: "asc"}
      return = {type: "single"}
    } as $proxima_solicitacao

    precondition ($proxima_solicitacao.id == $solicitacao.id) {
      error_type = "accessdenied"
      error = "A solicitacao deve seguir a ordem de chegada."
    }

    var $agora {
      value = "now"|to_timestamp
    }

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $solicitacao.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0)
      return = {type: "count"}
    } as $emprestimos_ativos

    precondition ($emprestimos_ativos == 0) {
      error_type = "accessdenied"
      error = "Estudante ja possui emprestimo ativo."
    }

    db.query emprestimo {
      where = $db.emprestimo.usuario_id == $solicitacao.usuario_id && ($db.emprestimo.devolvido_em == null || $db.emprestimo.devolvido_em == 0) && $db.emprestimo.vence_em < $agora
      return = {type: "count"}
    } as $emprestimos_atrasados

    precondition ($emprestimos_atrasados == 0) {
      error_type = "accessdenied"
      error = "Estudante com emprestimo atrasado."
    }

    db.query exemplar {
      where = $db.exemplar.titulo_id == $solicitacao.titulo_id && $db.exemplar.estado == "disponivel"
      sort = {exemplar.id: "asc"}
      return = {type: "single"}
    } as $exemplar

    precondition ($exemplar != null) {
      error_type = "accessdenied"
      error = "Nao ha exemplar disponivel para retirada."
    }

    db.add emprestimo {
      data = {
        usuario_id: $solicitacao.usuario_id
        exemplar_id: $exemplar.id
        solicitacao_id: $solicitacao.id
        retirado_em: $agora
        vence_em: $agora|add_secs_to_timestamp:1209600
      }
    } as $emprestimo

    db.patch exemplar {
      field_name = "id"
      field_value = $exemplar.id
      data = {estado: "emprestado"}
    } as $exemplar_atualizado

    db.patch solicitacao_emprestimo {
      field_name = "id"
      field_value = $solicitacao.id
      data = {}|set:"estado":"atendida"|set:"atendida_em":$agora
    } as $solicitacao_atendida
  }

  response = $emprestimo
  guid = "vfVqEfy7NomPL_S1oiM3ds8Uang"
}
