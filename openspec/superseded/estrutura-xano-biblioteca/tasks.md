# Tasks

## 1. Confirmar destino limpo e contrato Xano

- [ ] 1.1 Imediatamente antes de qualquer escrita, confirmar pelo CLI workspace, branch, ambiente e permissão; fazer pull somente de definições. Verificar por saída do CLI que o destino está autorizado e sem recursos preexistentes; se houver qualquer recurso, `allow_push: false` ou divergência de destino, parar sem push e pedir decisão, registrando evidências sem segredos.
- [ ] 1.2 Confirmar na documentação oficial e no destino liberado que a autenticação nativa atende cadastro com e-mail/senha, sessão imediata, perfil autenticado e expiração. Registrar contratos físicos confirmados e erros observados; parar antes de escrever se faltar suporte ou for necessário inventar endpoint/token.

## 2. Implementar identidade no Xano

- [ ] 2.1 Definir a conta autenticável mínima (e-mail único, credencial de senha nativa e perfil estudante/bibliotecário) e validar a definição XanoScript contra a documentação/ferramenta suportada; documentar o schema aprovado sem campos escolares não requeridos.
- [ ] 2.2 Implementar no Xano os contratos confirmados de cadastro, login e perfil. Verificar cadastro imediato de estudante, rejeição de duplicidade, rejeição/ignorância de papel enviado pelo cliente, credenciais inválidas e sessão ausente; documentar request/response físicos sem expor credenciais.
- [ ] 2.3 Preparar um dry-run apenas da estrutura e endpoints novos no destino limpo confirmado, sem registros, variáveis, truncamento, sync destrutivo ou exclusões. Apresentar diff integral e aguardar aprovação explícita dessa prévia; verificar que não altera recursos preexistentes ou fora da Change.
- [ ] 2.4 Somente após aprovação do dry-run e dos gates de destino, aplicar os recursos de identidade aprovados. Conferir por pull somente de definições que foram criados apenas os recursos desta Change e que nenhum recurso anterior foi alterado; registrar o resultado e parar diante de qualquer divergência.
- [ ] 2.5 Coordenar o provisionamento manual da primeira conta bibliotecária somente após operador confirmar workspace e branch autorizados; verificar login e perfil retornado sem criar rota pública de promoção nem registrar credenciais nos artefatos.

## 3. Conectar os fluxos de identidade ao Reflex

- [ ] 3.1 Antes de editar ou executar código Reflex, cumprir o Apêndice B: usar uma única estratégia `venv` + `pip`, conferir Python, instalar/verificar `reflex-docs`, `setup-python-env` e `reflex-process-management` no Copilot e confirmar a configuração local com os comandos documentados; parar se as skills não estiverem disponíveis.
- [ ] 3.2 Implementar cadastro, login, perfil e mensagens de erro em português, fazendo o navegador chamar somente o backend Reflex e este usar os contratos Xano verificados. Verificar cadastro, duplicidade, login válido/inválido e perfil pelo conjunto de testes da aplicação; documentar comandos e limitações.
- [ ] 3.3 Manter a credencial Xano somente em estado privado e isolado por sessão no backend Reflex; verificar duas sessões concorrentes, inspeção de estado/eventos/respostas/bundle no cliente e logout local seguido de recusa de chamadas autenticadas.
- [ ] 3.4 Implementar indicador `:focus-visible` distinguível e validar navegação por teclado, mensagens e ausência de overflow horizontal em 360×800 e 1366×768; registrar evidências no guia local da aplicação.

## 4. Verificar a integração

- [ ] 4.1 Executar testes integrados Reflex–Xano para cadastro imediato, duplicidade, login, perfil confiável, sessão ausente/inválida, logout, tentativa de autoelevação e isolamento entre usuários; verificar que nenhum token chega ao navegador e que não foram criados recursos de catálogo/circulação.
- [ ] 4.2 Executar testes, compilação e verificações estáticas disponíveis, revisar os diffs locais e a prévia Xano aprovada e registrar comandos, resultados e limitações reais; confirmar que Verify não depende de recursos não implementados nem de deploy.

## Workflow follow-up

- Após revisão humana, executar Apply somente com os gates de destino satisfeitos; parar diante de recursos no destino ou push não permitido.
- Solicitar Verify após concluir as tarefas e evidenciar os cenários; arquivar somente se todas estiverem concluídas e Verify aprovado.
- Criar Changes verticais posteriores para catálogo público/administração, empréstimo e retirada/devolução, reservas e fila, e condição/danos/perdas. Cada uma define e implementa somente seus próprios dados, regras e contratos.
