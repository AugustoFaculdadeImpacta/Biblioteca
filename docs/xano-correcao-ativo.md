# Diagnóstico da desativação de títulos

## Comparação do PATCH

O arquivo local `xano/api/default/catalogo/titulos_id_PATCH.xs` foi comparado
linha a linha com a cópia remota já existente
`api/biblioteca/catalogo/titulos/titulo_id_PATCH.xs`. A diferença encontrada é
somente de formatação: alinhamento de chaves, linhas em branco com espaços e
ausência de quebra de linha final na cópia remota. Não há diferença funcional
entre os dois arquivos.

O caminho de `ativo` é:

```xanoscript
bool ativo?
```

```xanoscript
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
```

```xanoscript
db.patch titulo {
  field_name = "id"
  field_value = $input.titulo_id
  data = $dados_atualizacao
}
```

Entre esses blocos, o arquivo tem exatamente:

```xanoscript
conditional {
  if ($input.ativo != null) {
    var.update $dados_atualizacao {
      value = $dados_atualizacao|set:"ativo":$input.ativo
    }
  }
}
```

`ativo` é um booleano opcional. O filtro `!= null` inclui `false`; o valor é
inserido no mapa com `set`. A condição de desativação compara explicitamente
com `$input.ativo == false` antes das verificações de empréstimos e reservas,
e o `db.patch` recebe o mapa atualizado. Não há `is_empty`, `first_notempty`
nem condição truthy sobre `$input.ativo` descartando o valor.
Não foi encontrado defeito Xano a corrigir, portanto o arquivo local permanece
inalterado e não há trecho de correção para aplicar no painel.

No frontend, `update_title` também adiciona `ativo` quando o argumento não é
`None`; `False` permanece booleano no JSON. O teste local confirma que o corpo
PATCH contém `"ativo": false` como booleano. Quando a releitura contradiz a
resposta, o log de erro registra os valores booleanos enviados, respondidos e
relidos, e a mensagem da ação inclui a referência correlacionada.

## Como validar manualmente no painel

Faça esta validação somente em um ambiente de teste e com um título de teste
sem empréstimo ou reserva ativa. Não use registros reais:

1. Abra a query PATCH do catálogo e confirme que `ativo` tem tipo booleano.
2. Confira o bloco `if ($input.ativo != null)` e a atribuição por `set` acima.
3. Execute a query com os campos obrigatórios `titulo` e `autores`, o id do
   título de teste e `"ativo": false` (booleano, sem aspas em `false`).
4. Confirme que a resposta contém `ativo: false` e que uma releitura do acervo
   retorna o mesmo valor.
5. Se os valores divergirem, abra o Request History da query e compare o corpo
   recebido, a resposta e o valor persistido antes de alterar a implementação.

Esta inspeção foi estática e local; não houve escrita nem validação HTTP no
Xano nesta tarefa.
