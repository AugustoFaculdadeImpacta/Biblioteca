// Retorna o perfil associado à identidade autenticada.
query "auth/me" verb=GET {
  api_group = "Biblioteca"
  auth = "usuario"

  input {
  }

  stack {
    db.get usuario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "created_at", "nome", "email", "perfil"]
    } as $usuario
  }

  response = {id: $usuario.id, nome: $usuario.nome, email: $usuario.email, perfil: $usuario.perfil}
  guid = "Pke5AHMPfR-9OtLMgkT3uA7Stkk"
}
