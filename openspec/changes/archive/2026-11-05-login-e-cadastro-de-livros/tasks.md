# Tasks

## 1. Login e sessão

- [x] 1.1 Reutilizar a normalização de e-mail do cadastro e implementar `POST /auth/login` com somente `email` e `senha`; verificar normalização, senha inalterada, método, rota e payload por `httpx.MockTransport`.
- [x] 1.2 Validar a resposta `Sessao`, manter token e perfil apenas no estado privado, mapear erros `400`/`401` para mensagens seguras e testar que token, senha, perfil, URL e cabeçalho não aparecem em deltas, estado público ou logs e que sessões permanecem isoladas.

## 2. Administração do acervo

- [x] 2.1 Corrigir o cliente HTTP para enviar o token real apenas no cabeçalho backend de autorização; testar o valor no transporte mockado e ausência de vazamento em logs e estado cliente.
- [x] 2.2 Implementar bloqueio/redirect da área administrativa para visitantes e estudantes, liberar o perfil bibliotecário e tratar `403`; verificar por testes de estado e componentes que perfis não autorizados não iniciam escrita.
- [x] 2.3 Implementar listagem de categorias por `GET /catalogo/categorias` e formulário com os campos aceitos por `titulos_POST.xs`; verificar `id`/`nome` da lista e o payload e registro retornado pelo mock, conferindo nomes e tipos no `.xs` e nas tabelas referidas em design.md.
- [x] 2.4 Associar cada categoria selecionada ao título retornado usando `titulo_id` na rota e `categoria_id` no corpo; testar rota, payload, resposta, duplicidade e referências inválidas com mock, conferindo `titulos_categoria_POST.xs` e `titulo_categoria.xs`.
- [x] 2.5 Criar cada exemplar solicitado enviando somente `titulo_id`; exibir `codigo_tombo` do retorno e testar sucesso/falha parcial sem repetição automática com mock, conferindo `exemplares_POST.xs` e `exemplar.xs`.
- [x] 2.6 Implementar o fluxo sequencial título→categorias→exemplares, mantendo progresso e IDs apenas no backend, permitindo retomar etapas definitivamente rejeitadas, reconciliando associações via `categorias_titulos_GET.xs` e bloqueando repetição automática de título/exemplar com resultado incerto; testar sequência, privacidade e falhas com transporte simulado.

## 3. Documentação e integração

- [x] 3.1 Criar roteiro em português para testar login, cadastro de título, associação de categorias e criação de exemplares em ambiente não produtivo, confirmando o destino antes da escrita real e registrando os códigos de tombo retornados; verificar que testes automatizados usam somente mocks.
- [x] 3.2 Executar `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q`, `openspec validate "login-e-cadastro-de-livros" --strict` e `reflex compile --dry`; abrir as rotas no navegador, verificar `:focus-visible` e confirmar que `xano/`, `evaluation/` e `openspec/changes/verificacao-avancada-circulacao` não foram alterados.

## Workflow follow-up

- Sincronizar as deltas `identity-session` e `catalog` e arquivar somente após Review e Verify aprovados.
