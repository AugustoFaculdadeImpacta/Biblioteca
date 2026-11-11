# Tasks

## 1. Cliente autenticado de circulação

- [x] 1.1 Implementar wrappers validados para os três GETs pessoais existentes e `POST /solicitacoes-emprestimo` conforme o OpenAPI, usando token somente no backend Reflex; cobrir contratos, headers, erros e payload `titulo_id` com `httpx.MockTransport`.
- [x] 1.2 Testar respostas de empréstimos com `devolvido_em` nulo e `0`, datas UTC, solicitações com e sem `reserva_id`, e reservas com `expira_em_sao_paulo`; respostas malformadas devem falhar sem sucesso em formato válido.

## 2. Ações de empréstimo e reserva no catálogo

- [x] 2.1 Adicionar ações de estudante ao detalhe do título, distinguindo disponibilidade apenas como indicação e usando o mesmo POST de solicitação; testar títulos disponíveis/indisponíveis e disponibilidade alterada no mock.
- [x] 2.2 Tratar resposta confirmada, solicitação em reserva e recusas de elegibilidade com mensagens claras; testar que não se chama `POST /reservas` nem se repete automaticamente uma escrita incerta.

## 3. Área “Minha biblioteca”

- [x] 3.1 Implementar rota protegida e carregar empréstimos, solicitações, reservas e metadados públicos; testar bloqueio de visitante/perfil bibliotecário e isolamento dos dados por sessão.
- [x] 3.2 Exibir estados vazios, status e prazos, aviso de atraso para empréstimo não devolvido vencido tratando `null`/`0`, e ocultar a duplicação visual da solicitação vinculada a reserva; testar datas, timezone e agrupamento.

## 4. Navegação e verificação integrada

- [x] 4.1 Adicionar “Minha biblioteca” apenas ao menu de estudante autenticado e garantir links, labels, teclado, `:focus-visible`, contraste e layout sem overflow em 360px; cobrir renderização e perfil por testes.
- [x] 4.2 Executar `PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m pytest tests -q`, `openspec validate area-do-estudante --strict`, `openspec validate --specs --strict` e `reflex compile --dry`; registrar resultados e confirmar que nenhuma escrita real foi enviada ao Xano.
- [x] 4.3 Verificar no navegador com mock os caminhos de solicitar empréstimo, fila de reserva, área pessoal, aviso de atraso e bloqueio por perfil; testar claro/escuro em 360px e 1366px, contraste, foco, overflow e ausência de token no estado/logs.
- [x] 4.4 Revisar `git status` e `git diff` para confirmar que somente arquivos Reflex, testes e esta Change foram alterados; registrar itens preexistentes ignorados e confirmar ausência de mudanças de implementação em `xano/`, `evaluation/`, `.vscode/` e `devolvido-em-nulavel`.

## Workflow follow-up

- Arquivar a Change somente após Review, Verify aprovado e sincronização das quatro deltas em `openspec/specs/`.

## Evidências de verificação

- Testes direcionados de navegação, catálogo e área do estudante: 39 aprovados.
- Suíte completa: 88 aprovados. `openspec validate area-do-estudante --strict` e `openspec validate --specs --strict` passaram; 6 specs consolidadas válidas. `reflex compile --dry` compilou com sucesso.
- Nenhuma escrita remota foi enviada ao Xano. As operações de leitura e solicitação foram executadas somente contra servidor mock local; contadores finais do mock: 3 consultas pessoais e 2 solicitações. Nenhuma escrita de negócio foi enviada ao Xano.
- Navegador (Playwright): caminhos de login, links entre Entrar/Cadastrar, solicitação de exemplar disponível, entrada em fila para título indisponível, área pessoal, aviso de atraso, deduplicação de solicitação/reserva e bloqueios de `/admin/acervo` e `/minha-biblioteca` verificados com respostas mockadas. Em 360px e 1366px, nos modos claro e escuro, campos de login/cadastro e controles do catálogo tiveram contraste 15,98:1 e 16,25:1, respectivamente, sem overflow horizontal. Navegação por Tab exibiu outline sólido de 3px no link de pular conteúdo. Nenhum token apareceu no estado público ou nos logs; a privacidade também está coberta pelos testes automatizados. Os processos locais foram encerrados após a verificação.
- A revisão de escopo não encontrou alterações em `xano/`, `evaluation/`, `.vscode/` ou `openspec/changes/devolvido-em-nulavel`. Os arquivos já presentes da Change A1 (`openspec/specs/catalog/spec.md`, `openspec/specs/frontend-foundation/spec.md` e seu diretório arquivado) foram preservados. `reflex.log` já existia sem rastreamento e foi atualizado para a execução local; a busca por padrões de token/autorização no arquivo não encontrou correspondências.
