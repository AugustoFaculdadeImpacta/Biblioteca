# Backend Xano - biblioteca escolar

Este diretório contém os schemas, endpoints e o contrato OpenAPI da biblioteca. O escopo abaixo foi enviado ao Xano e conferido por pull somente de definições.

## Destino e escopo aplicado

- Workspace: `151966` (`Augusto's Workspace`)
- Instância: `x8ki-letl-twmt.n7.xano.io`
- Branch: `v1` (live)
- Grupo de API: `Biblioteca`
- O metadado `allow_push` apareceu como `false`, mas o CLI 1.3.4 aceitou o push escopado; essa preferência não foi alterada.
- Prévia combinada: 9 arquivos de tabela e 28 de API considerados; **somente 28 endpoints foram listados para criação**. Nenhuma tabela ou outro tipo de recurso apareceu como alteração.
- Aplicação: CLI informou `Pushed 37 documents` e sincronizou 28 GUIDs.
- Pull posterior, sem `--records` e sem `--env`: 57 documentos, 11 tabelas no total (9 da biblioteca e 2 legadas), 36 endpoints no total (28 da biblioteca, 7 legados de `Authentication` e 1 de `Event Logs`). Os recursos legados permaneceram presentes.
- Não foram importados/lidos registros via CLI, nem variáveis ou segredos. Nenhum `--sync --delete`, `--truncate` ou deploy adicional foi usado.

## Conteúdo local

- `table/*.xs`: usuário, título, categoria, relação título-categoria, exemplar, solicitação, empréstimo, reserva e condição.
- `api/default/**/*.xs`: 28 endpoints com `api_group = "Biblioteca"`.
- `openapi.json`: contrato REST de 28 operações.
- `tests/test_candidates.py`: verificações estruturais e de contrato.

## Verificações concluídas

- `openspec validate "estrutura-inicial-xano-biblioteca" --strict --json`: aprovado, sem issues.
- `python -m unittest discover -s xano\tests -v`: 9 testes passaram. A checagem de relações foi atualizada para a sintaxe XanoScript `table = "nome"`.
- Pull pós-push confirmou todas as 9 tabelas da biblioteca e as 28 APIs no grupo `Biblioteca`.
- Smoke tests sem autenticação: `GET /catalogo/categorias` e `GET /catalogo/titulos` retornaram HTTP 200 e `[]` (catálogo vazio).

## Segurança e regras representadas

- Cadastro sempre atribui perfil `estudante`; não há endpoint público de promoção.
- E-mail é removido de espaços externos e convertido para minúsculas antes de validar, salvar ou verificar duplicidade; espaços internos são rejeitados. A senha não é normalizada.
- Dados públicos de identidade não incluem senha ou token; o primeiro bibliotecário deve ser provisionado manualmente por operador autorizado.
- Não foram incluídos endpoints de cancelamento, exclusão ou arquivamento.

## Verificações ainda necessárias

1. Executar testes autenticados controlados de cadastro/login/perfil e dos fluxos de circulação com contas e dados de teste autorizados. Não foram criados usuários, empréstimos ou reservas de teste neste workspace live.
2. Verificar autorização por perfil em runtime e invariantes de atraso, limite de empréstimo, FIFO, oferta/expiração e condição do exemplar.
3. Verificar garantias contra concorrência e imutabilidade do código de tombo no runtime. A aceitação do import não prova essas propriedades.
4. A expiração possui endpoint manual `admin/reservas/processar-expiradas`; não foi criada nem verificada tarefa agendada.
5. O Xano CLI não oferece lint/compilador local XanoScript. O sucesso do import e do pull demonstra aceitação pelo Xano, mas não substitui os testes de comportamento acima.

Nenhuma senha, token, registro de teste ou variável de ambiente foi gravado no repositório.
