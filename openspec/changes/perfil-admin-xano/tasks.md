# Tasks

## 1. Gates de destino e prova do schema

- [x] 1.1 Confirmar pelo Xano CLI que workspace `151966`, branch `v1` live e ambiente selecionados correspondem ao grupo Biblioteca; verificar `allow_push`. Resultado: destino confirmado; `allow_push=false`; nenhum arquivo remoto foi alterado.
- [x] 1.2 Fazer pull somente de definições, salvar referência fora do repositório e conferir `git status` e diff. Resultado anterior: pull somente leitura; a leitura desta etapa também encontrou 57 documentos na branch `v1`, sem rota `/admin/usuarios`.
- [ ] 1.3 Provar remotamente o enum em tabela descartável, confirmar os três perfis, limpar tabela/registro e verificar GET 404. NÃO EXECUTADO: sessão limitada a alterações locais; não houve escrita remota, prova do schema ou limpeza.

## 2. Schema, autorização e contratos locais Xano

- [x] 2.1 Atualizar localmente `usuario.perfil` para os três perfis e adicionar `ativo` booleano com padrão verdadeiro; validar o arquivo com Xano Developer MCP. Resultado local: arquivo válido. A validação de sintaxe não substitui prova ou publicação remota.
- [ ] 2.2 Publicar `usuario.xs` com dry-run unitário, push autorizado e pull de conferência. NÃO EXECUTADO: Apply somente local, `allow_push=false`; nenhum push ou sandbox permitido.
- [x] 2.3 Atualizar localmente todos os guards administrativos existentes para bibliotecário/admin e recusar conta explicitamente desativada; validar cada arquivo com Xano Developer MCP. Resultado local: 15 guards e todos os 20 arquivos `.xs` alterados válidos; a estimativa anterior mencionava 14 guards.
- [ ] 2.4 Publicar individualmente os endpoints de autorização com dry-run, push e pull de conferência por arquivo. NÃO EXECUTADO: Apply somente local; publicação remota proibida.
- [x] 2.5 Preparar endpoints candidatos de listagem, criação e alteração de situação, atualizar OpenAPI e cobrir contrato/segredos/autorização com testes locais `httpx.MockTransport` e testes estruturais. Resultado local: 20/20 arquivos `.xs` alterados válidos. A leitura remota não encontrou esses endpoints; os contratos locais candidatos são `GET /admin/usuarios`, `POST /admin/usuarios` e `PATCH /admin/usuarios/{usuario_id}`; permanecem não confirmados no Xano remoto.
- [ ] 2.6 Executar testes Xano com contas sintéticas `zz-teste-*@exemplo.invalid`, registrar IDs fora do repositório, limpar individualmente pela Metadata API e confirmar GET 404, tabelas de negócio zero e `usuario=2`. NÃO EXECUTADO: nenhuma fixture ou escrita remota foi realizada.

## 3. Compatibilidade de sessão e gestão Reflex

- [x] 3.1 Permitir que a sessão Reflex reconheça `admin` e mantenha perfil/token privados; manter operações exclusivas de estudante bloqueadas.
- [x] 3.2 Testar login/admin, chamadas administrativas e recusas por perfil com mocks; nenhuma chamada de escrita real foi enviada.
- [x] 3.3 Criar a tela `/admin/bibliotecarios`, visível e acionável somente por admin, com listagem, cadastro, desativação e reativação; cobrir as chamadas com `httpx.MockTransport`, labels, foco visível e regras CSS responsivas. Testes locais verificam breakpoint móvel (até 40rem) e grade fluida móvel/desktop; não foi executado teste de navegador em viewport real.
- [x] 3.4 Adicionar alternância de visualização admin entre bibliotecário e estudante com faixa visível, sem alterar sessão/permissões; testar que a tela pessoal usa o token admin e não inventa registros quando o backend recusa. `tests/test_navigation.py` e `tests/test_student_area.py` passaram (34 testes focados); `python -m reflex compile --dry` concluiu; a rota pessoal mockada retornou 403 sem preencher registros.

## 4. Verificação local e escopo

- [x] 4.1 Executar `PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m pytest tests -q`, `PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m unittest discover -s xano\tests -v`, `reflex compile --dry` e `openspec validate perfil-admin-xano --strict`; registrar resultados locais separados de qualquer validação remota. Resultado: pytest 104 aprovados; unittest Xano 10 aprovados; compilação Reflex aprovada; OpenSpec estrito aprovado.
- [x] 4.2 Revisar `git status`, `git diff` e os caminhos protegidos. Confirmado: branch `trabalho-noturno`; nenhum `.env` ou segredo alterado, nenhuma alteração em `main`, nenhuma sandbox, publicação ou escrita no Xano remoto. `.mcp.json` permanece como arquivo não rastreado preexistente e não será incluído nos commits.

## Workflow follow-up

- Não arquivar: schema/contratos permanecem sem publicação e os testes Xano/limpeza remota não foram executados. Arquivar somente após publicação autorizada, Verify integrado e limpeza comprovada.
