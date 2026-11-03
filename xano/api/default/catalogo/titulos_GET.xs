query "catalogo/titulos" verb=GET {
  api_group = "Biblioteca"

  input {
  }

  stack {
    db.query titulo as $titulos

    var $resultado {
      value = []
    }

    foreach ($titulos) {
      each as $titulo {
        db.query exemplar {
          where = $db.exemplar.titulo_id == $titulo.id && $db.exemplar.estado == "disponivel"
          return = {type: "count"}
        } as $disponiveis

        db.query titulo_categoria {
          where = $db.titulo_categoria.titulo_id == $titulo.id
        } as $categorias

        var.update $resultado {
          value = $resultado|append:{
            titulo: $titulo,
            categorias: $categorias,
            exemplares_disponiveis: $disponiveis
          }
        }
      }
    }
  }

  response = $resultado
  guid = "izvFtTTvNoVAXjylVOzkry2KxiM"
}
