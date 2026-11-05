table zz_teste_nota {
  schema {
    int id
    text texto
    int prioridade?=0
    timestamp criado_em?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
  ]
  guid = "ghW_-0MQPrxsyDnbDlzk81t21h4"
}
