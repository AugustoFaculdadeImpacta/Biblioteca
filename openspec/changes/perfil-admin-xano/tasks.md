# Tasks

## 1. Gates de destino e prova do schema

- [x] 1.1 Confirmar pelo Xano CLI que workspace `151966`, branch `v1` live e ambiente selecionados correspondem ao grupo Biblioteca; verificar `allow_push` e que o destino aceita push delimitado por um único arquivo. Resultado: destino confirmado; `allow_push=false` e o push unitário não está disponível; nenhum arquivo Xano foi alterado.
- [x] 1.2 Fazer pull isolado somente de definições, salvar referência/rollback fora do repositório e verificar `git status` e diff. Resultado: pull local de referência concluído sem registros/ambiente; `xano/` permaneceu sem alterações.
- [ ] 1.3 Validar com Xano Developer a alteração do enum em tabela de teste reversível; comprovar aceitação dos três perfis, remover a tabela de teste e confirmar sua ausência antes de editar `usuario`.

## 2. Perfil e autorização no Xano

- [ ] 2.1 Adicionar `admin` ao enum `usuario.perfil`; executar dry-run com `-i` contendo somente `xano/table/usuario.xs` e exigir exatamente um UPDATE antes de um push unitário permitido; confirmar com pull isolado.
- [ ] 2.2 Atualizar os 14 endpoints administrativos existentes para aceitar bibliotecário ou admin, mantendo endpoints pessoais exclusivos de estudante e demais regras intactas; validar e enviar cada arquivo isoladamente após dry-run de uma única operação, com pull de conferência após cada push.
- [ ] 2.3 Criar `POST /admin/usuarios` no grupo Biblioteca, restrito a admin, para os campos e perfis definidos no design; atualizar OpenAPI e roteiro sem segredos para o primeiro admin; validar contrato, resposta sem senha/token, erros e autorização com testes mockados.
- [ ] 2.4 Executar testes Xano somente com contas sintéticas `zz-teste-*@exemplo.invalid`, registrar IDs fora do relatório público e limpar recursos individualmente pela Metadata API; verificar GET 404 e contagens finais de tabelas de negócio zero e `usuario=2`.

## 3. Compatibilidade de sessão Reflex

- [x] 3.1 Permitir que login Reflex valide o perfil admin e que as verificações administrativas tratem admin como bibliotecário; manter operações exclusivas de estudante bloqueadas e provar privacidade do token/perfil com testes. Implementação local concluída; autorização Xano real permanece pendente nas tarefas 2.x.
- [x] 3.2 Testar login/admin, chamadas administrativas e recusas por perfil com mocks; verificar que nenhum segredo ou dado pessoal real aparece em logs ou estado público. Resultado: testes de login, navegação e administração passaram com transportes mockados; nenhuma chamada de escrita real foi enviada.
- [ ] 3.3 Criar tela de gestão de bibliotecários somente para admin, incluindo criação e desativação lógica. Bloqueada até existir contrato Xano verificável para listar e desativar contas; não inventar campos ou rotas.

## 4. Verificação integrada

- [x] 4.1 Executar `PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m pytest tests -q`, `openspec validate perfil-admin-xano --strict`, `openspec validate --specs --strict` e `reflex compile --dry`; resultado: 91 testes passaram, validações OpenSpec passaram (6 specs), compilação Reflex passou.
- [x] 4.2 Revisar `git status` e `git diff`; os arquivos alterados pertencem ao código Reflex, testes, documentação e artefatos desta Change; `xano/` e outras Changes não foram alterados. `reflex.log` já estava como não rastreado e não foi editado; será ignorado conforme solicitado no fechamento.

## Workflow follow-up

- Arquivar somente após todos os gates, testes, limpeza de dados sintéticos e revisão do diff passarem; sincronizar todas as deltas com `openspec/specs/` antes de arquivar.
