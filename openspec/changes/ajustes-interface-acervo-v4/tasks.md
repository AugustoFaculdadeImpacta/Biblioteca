# Tasks

## 1. Campos nativos e aparência

- [x] 1.1 Substituir controles Radix de formulário por elementos nativos com `.campo`, `.campo-area`, `.campo-select` e `.campo-check`, preservar ids, names, labels e handlers e garantir IDs ocultos como `type="hidden"`; validar com testes novos/alterados em `tests/test_frontend_foundation.py` e compilação Reflex.
- [x] 1.2 Implementar variantes de botão com contraste mínimo 4,5:1 em ambos os temas e estados, e contraste de capas geradas para os 30 títulos de `TITULOS`; validar com testes novos/alterados em `tests/test_frontend_foundation.py` e `tests/test_covers.py`.

## 2. Cabeçalho e dicionário de ícones

- [ ] 2.1 Separar Perfil e Acessibilidade em disclosures mutuamente exclusivos, acessíveis por Escape/clique fora e utilizáveis a 360 px, mantendo preferências de aparência privadas e o seletor de visão somente para admin; validar com testes novos/alterados em `tests/test_navigation.py`.
- [ ] 2.2 Criar `biblioteca_mais_nova/icons.py` e `docs/guia-de-icones.md`, aplicar emoji exclusivo, texto curto, `title`, `aria-label` e emoji `aria-hidden` em todas as ações/selos do site e confirmação destrutiva inline; validar exclusividade e atributos com novos testes em `tests/test_icons.py`.

## 3. Acervo e desativação

- [ ] 3.1 Exibir o Acervo em lista vertical com miniatura 72×108, dados e ações solicitados, busca sem acentos, painel único de edição/exemplares, dez itens por página e filtro de desativados desligado; validar busca, painéis, paginação, estados inativos e catálogo público com testes novos/alterados em `tests/test_admin_catalog.py`.
- [ ] 3.2 Confirmar desativação após recarregar e comparar `ativo`; testar sucesso real, sucesso aparente, 403, 404 e falta de conexão em `tests/test_admin_catalog.py`. Em Apply, confirmar workspace/branch/ambiente pelo Xano CLI e comparar somente definições locais/remotas por pull de leitura em pasta temporária externa ao repositório; se a definição local estiver errada, corrigir apenas o arquivo local e registrar a publicação pendente em `docs/publicacao-xano-pendente.md`, sem sincronizar nem publicar.

## 4. Reservas e seed

- [ ] 4.1 Mapear falhas da solicitação de reserva para 401, 403, 404, 409, 5xx, timeout e demais erros seguros; validar cada caso com testes novos/alterados em `tests/test_catalog.py`. Em Apply, comparar a definição local e um pull remoto somente de leitura após confirmar o destino, registrando que o endpoint público local exige perfil estudante; nunca gravar no Xano.
- [ ] 4.2 Auditar/completar o seed e `docs/seed-catalogo.md`: saída inicia com o alvo correto, dry-run permanece padrão, credenciais só vêm do ambiente, os 30 títulos têm descrições e 2–3 exemplares, categorias não são criadas e nomes de teste existentes são desativados; validar com `tests/test_seed_catalogo.py` sem executar `--apply`.

## Workflow follow-up

- Depois de cada tarefa, criar um commit pequeno em português e executar `.\\.venv\\Scripts\\python.exe -m reflex compile --dry` e `pytest --ignore=evaluation`. Só marcar a tarefa `[x]` após guardar o hash do commit e os nomes dos testes no relatório; itens visuais ficam “feito, aguarda conferência do usuário”.
- Ao concluir todas as tarefas, atualizar `docs/relatorio-noite.md` com item, commit, testes e status; validar a Change e as specs com `openspec.cmd validate --specs --strict` e validação da Change.
- Após Verify aprovado e revisão humana exigida pelo fluxo do projeto, sincronizar as specs, arquivar a Change, criar o commit de fechamento e enviar `trabalho-autopilot` sem force.
