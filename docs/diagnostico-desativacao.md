# Diagnóstico da desativação de título

## Uso

No terminal do backend local, habilite a variável antes de iniciar o aplicativo:

```powershell
$env:BIBLIOTECA_DIAGNOSTICO="1"
.\.venv\Scripts\python.exe -m reflex run
```

No painel administrativo, clique em Desativar, confirme e observe a saída do terminal. Remova a variável ao terminar:

```powershell
Remove-Item Env:BIBLIOTECA_DIAGNOSTICO
```

## Dados registrados

- método HTTP `PATCH`;
- caminho relativo `/catalogo/titulos/{id}`;
- nomes das chaves enviadas no corpo;
- status HTTP;
- nomes das chaves da resposta;
- valor `ativo` informado pela resposta;
- valor `ativo` confirmado pela releitura.

Não são registrados host, token, e-mail, senha, corpo completo ou metadados pessoais.

## Xano

Confira no terminal se o PATCH envia `ativo: false` como booleano e se a releitura retorna `ativo: false`. O endpoint local `titulos_id_PATCH.xs` utiliza a entrada booleana `ativo` e o campo de tabela `titulo.ativo`.
