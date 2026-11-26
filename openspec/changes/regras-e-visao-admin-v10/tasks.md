# Tasks

## 1. Visão efetiva do admin

- [ ] 1.1 Separar perfil real e visão efetiva, atualizar seletor/faixa/menu Perfil e proteger rotas conforme as specs, mantendo `/regras` acessível ao admin em qualquer visão; verificar com testes de navegação e sessão que as chamadas preservam a identidade admin.

## 2. Contrato de regras e cliente Xano

- [ ] 2.1 Implementar GET/PUT de configuração e validações/regras configuráveis na API de demonstração; verificar padrões, permissões, limites e rejeições com testes da API.
- [ ] 2.2 Adicionar leitura/gravação no cliente Xano, cache de 60 s e invalidação após PUT; verificar chamadas, corpo exato, cache e erros 403/404 com cliente simulado.

## 3. Páginas e apresentação das regras

- [ ] 3.1 Implementar `/regras` com os sete campos, rótulos/ajudas, validação, descarte, estado de leitura somente com padrões e metadados; verificar acesso somente para admin real e comportamento com testes de estado/interface.
- [ ] 3.2 Exibir no detalhe do livro a frase curta com o limite vigente de pedidos; verificar carregamento da configuração em cache e ausência de autorização baseada somente na interface.

## 4. Ações simuladas e mensagens de regra

- [ ] 4.1 Habilitar operações de estudante e equipe nas respectivas visões do admin usando a sessão real, traduzir erros especificados e atualizar listas uma única vez após 403 de estado obsoleto; verificar POST/ações e chamadas de releitura em testes.

## 5. Contraste do cabeçalho

- [ ] 5.1 Inspecionar árvore do cabeçalho e cascata CSS gerada, igualar Acessibilidade ao estilo de Perfil sem alterar geometria e testar contraste calculado dos dois controles nos dois temas e estados; registrar “aguarda conferência do usuário” se Edge headless não responder em 60 s.

## 6. Documentação e integração

- [ ] 6.1 Documentar contrato e publicação manual em `docs/publicacao-xano-regras.md`, atualizar `docs/relatorio-noite.md` e validar todos os comportamentos, specs e tarefas com `reflex compile --dry`, seguido de pytest (nunca simultaneamente), `openspec validate --strict` e verificação de `git diff --check`.

## Workflow follow-up

- Sincronizar os deltas nas specs principais e arquivar a Change somente após todas as tarefas verificadas.
- Publicação no Xano permanece manual, documentada e fora do escopo de operações desta Change.
