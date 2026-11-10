# Backend Xano - biblioteca escolar

Este diretório contém as definições Xano versionadas da biblioteca e o contrato OpenAPI. As contagens abaixo refletem o pull somente de definições do workspace `151966`, branch live `v1`, usado na reconciliação de 2026-11-08; não afirmam que o Git e o workspace estejam sincronizados.

## Estado observado

- CLI Xano: `1.3.4`; destino confirmado: workspace `151966`, branch live `v1`.
- `allow_push = false`; a preferência não foi alterada. A reconciliação foi somente leitura e não executou push.
- Remoto: 11 tabelas e 36 endpoints em três grupos de API; também 3 funções quick-start, 1 addon, 2 recursos AI e metadados do workspace (57 documentos no pull).
- Git: 9 tabelas e 31 operações da biblioteca. As três operações locais de gestão de bibliotecários são candidatas e não foram confirmadas no workspace remoto; não há tabela somente no Git.
- As 9 tabelas locais têm correspondentes remotos; `usuario` coincide. O remoto declara `auth = false` em outras 8 tabelas comuns e em `event_log`; essas permissões não foram importadas e estão registradas como achado de segurança aberto.
- `Authentication`, `Event Logs`, tabela `user`, tabela `event_log`, funções quick-start, addon, recursos AI e metadados do workspace são recursos de plataforma fora do escopo de `xano/`.
- A reconciliação adicionou somente `return = {type: "list"}` em quatro GETs públicos de catálogo. Divergências de FIFO e demais diferenças sem equivalência comprovada permanecem pendentes; consulte a seção de reconciliação em [docs/xano-workflow.md](../docs/xano-workflow.md).
- O valor `swagger.token` do grupo Biblioteca foi tratado como exposto e deve ser rotacionado pelo operador no painel. Nenhum valor de credencial foi versionado.

## Conteúdo local

- `table/*.xs`: as 9 tabelas da biblioteca.
- `api/default/**/*.xs`: 31 endpoints locais com `api_group = "Biblioteca"`, incluindo três candidatos de gestão de bibliotecários não confirmados remotamente.
- `openapi.json`: contrato REST local de 31 operações.
- `tests/test_candidates.py`: verificações estruturais e de contrato.

## Verificações já registradas

Os resultados abaixo são do histórico da implantação inicial; não substituem a revisão de drift desta reconciliação:

- `openspec validate "estrutura-inicial-xano-biblioteca" --strict --json`: aprovado, sem issues.
- `python -m unittest discover -s xano\tests -v`: 9 testes passaram.
- Pull posterior à implantação confirmou 9 tabelas e 28 APIs da biblioteca.
- Smoke tests sem autenticação retornaram HTTP 200 e `[]` para `GET /catalogo/categorias` e `GET /catalogo/titulos`, naquele momento.

## Regras representadas e verificações pendentes

- Cadastro atribui perfil `estudante`; não há endpoint público de promoção. Admin é o terceiro perfil e somente admin gere contas bibliotecárias.
- O schema local de `usuario` contém o campo `ativo` com padrão verdadeiro; `ativo=false` bloqueia login e operações administrativas.
- E-mail é normalizado antes de validar, salvar ou verificar duplicidade; a senha não é normalizada.
- Dados públicos de identidade não incluem senha ou token; a primeira conta admin deve ser provisionada manualmente pelo dono do workspace autorizado.
- Permanecem pendentes testes autenticados de cadastro, login e perfil; condição; imutabilidade do código de tombo; processador global de expiração/reoferta; e cenários de concorrência fora do limite de empréstimo verificado abaixo.
- A expiração possui endpoint manual `admin/reservas/processar-expiradas`; tarefa agendada não foi criada nem verificada.
- O Xano CLI não oferece lint/compilador local XanoScript. Pull e validação de estrutura não provam comportamento em runtime.

## Verificação de circulação no workspace live

Em 2026-11-09, a Change `corrigir-regras-circulacao` foi aplicada com pushes individuais delimitados e verificada em runtime:

- Solicitação e reserva com empréstimo atrasado foram bloqueadas; o limite concorrente aceitou uma retirada e recusou a outra.
- A fila FIFO retornou três reservas com o mesmo `criada_em` em ordem crescente de ID; a oferta respondeu HTTP 200 para a reserva mais antiga.
- A limpeza foi confirmada por GET 404 para cada fixture. As contagens finais foram `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `titulo=0` e `usuario=2`.
- O processador global de expiração/reoferta não foi executado; seus filtros de ordenação foram conferidos somente por pull após o push delimitado.
- Evidências detalhadas e limitações estão em [RESULTS.md](../openspec/changes/corrigir-regras-circulacao/RESULTS.md).

Nenhuma credencial, registro de teste ou variável de ambiente foi gravado no repositório.
