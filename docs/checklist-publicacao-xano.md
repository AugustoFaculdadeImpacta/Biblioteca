# Checklist de publicação no Xano

## Antes de publicar

1. Acesse o painel do Xano e confirme o workspace `Augusto's Workspace`, branch `v1` e ambiente antes de clicar em publicar.
2. Faça backup do workspace atual pelo painel.
3. Confirme que `allow_push` está habilitado somente se a pessoa responsável autorizar a publicação.
4. Não use `--sync`, `--delete`, `--records` ou `--truncate`.

## Itens pendentes

- Campo opcional `capa_url` na tabela `titulo`.
- Campo opcional `descricao` na tabela `titulo`; a descrição já aparece como campo local no pull remoto.
- Exibir `titulo_id` ou dados do título em `GET /minhas/emprestimos`.
- Confirmar `solicitada_em` em `GET /minhas/solicitacoes`.
- Confirmar a rota remota de desativação `PATCH /catalogo/titulos/{titulo_id}`.
- Validar em runtime os perfis estudante, bibliotecário e admin com contas sintéticas.
- Publicar somente os arquivos Xano cujo diff foi confirmado com o estado remoto.

## Publicação

1. Publique primeiro as alterações de tabela necessárias.
2. Use o dry-run do CLI e revise o preview antes de qualquer push.
3. Publique os endpoints separados pela menor unidade possível.
4. Faça pull somente de definições para conferência após a publicação.
5. Rode os testes sintéticos e os GET públicos.

## Testes

- Catálogo público deve listar títulos sem autenticação.
- Categorias públicas devem retornar os oito nomes aprovados.
- `/minhas/*` sem token deve responder 401.
- Fluxos sintéticos de login, reserva, retirada e devolução devem ser executados sem apagar dados reais.

## Desfazer

Use o backup feito antes da publicação para restaurar o workspace pelo painel. Se apenas um endpoint tiver sido publicado, desfaça esse endpoint individualmente e confirme o pull de definições.
