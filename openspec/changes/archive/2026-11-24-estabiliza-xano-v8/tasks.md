# Tasks

## 1. Barra de navegação

- [x] 1.1 Fazer o realce pertencer ao controle externo inteiro, impedir encolhimento/corte de marca, links, Perfil e Acessibilidade, manter foco visível no mesmo formato e cobrir o contrato de CSS em testes; `pytest tests/test_navigation.py tests/test_icons.py -q` passou (55 testes); implementação no commit `c9a4b7d`.

## 2. Capas públicas

- [x] 2.1 Manter a capa SVG gerada como camada inferior acessível, ocultar imagens reais que falhem por um único script no head e testar cartões/detalhes e a varredura de imagens já falhadas; `pytest tests/test_catalog.py tests/test_covers.py -q` passou (37 testes), e `node --check` validou o script; implementação no commit `bec7045`.
- [x] 2.2 Resolver capas Open Library no servidor por título e primeira autoria, com cache, timeout, limite de concorrência, modo sem rede e execução posterior ao primeiro render; `pytest tests/test_covers.py tests/test_catalog.py tests/test_admin_catalog.py tests/test_primary_journeys.py -q` passou (84 testes); implementação no commit `1c320cb`.

## 3. Cliente Xano resiliente

- [x] 3.1 Implementar diagnóstico opt-in sem segredos, contagem por carregamento, semáforo de três chamadas, retries exclusivamente GET com backoff/Retry-After e mensagens específicas; documentar uso em `docs/diagnostico-xano.md`; `pytest tests\test_xano_client.py tests\test_circulation.py tests\test_catalog.py` e testes focados de mensagens passaram (83 testes), e após o ajuste final de logging `pytest tests\test_xano_client.py -q` passou (22 testes); Pylance não reportou diagnósticos; implementação no commit `1ff684e`.

## 4. Carregamentos e cache por rota

- [x] 4.1 Auditar home, catálogo, detalhe, reservas, Acervo e Contas; reutilizar catálogo/categorias por 60 s com invalidação após escritas, evitar consultas pessoais sem sessão/necessidade, encerrar flags em `finally`, oferecer retry visível e separar os indicadores da home; cobrir chamadas/cache/erros em testes e completar a tabela de rotas em `docs/diagnostico-xano.md`; 8 testes focados passaram em `3816d77` e a auditoria foi registrada em `docs/diagnostico-xano.md`.

## 5. Diagnóstico do Acervo

- [x] 5.1 Criar “🩺 Testar conexão” exclusivo para admin real, com cinco leituras sequenciais, resumo solicitado e testes simulados; confirmar a coerência local do PATCH `ativo` com a entrada XanoScript, `db.patch` e releitura, registrando que não houve pull remoto ou acesso sem destino inequívoco; 6 testes focados passaram em `92ee9fb`.

## 6. Importação retomável

- [x] 6.1 Executar a importação em evento Reflex de segundo plano, com progresso, pausa de 1,5 s, repetição limitada após releitura, retomada idempotente e parada após três falhas; 5 testes focados passaram em `fed5245`, e o seed local contém 30 títulos incluindo Dom Casmurro e Memórias Póstumas de Brás Cubas.

## 7. Integração e fechamento

- [x] 7.1 Executar compile `--dry` e pytest em sequência, registrar a rodada do robô e as lacunas no relatório, sincronizar specs, validar com `--strict` e arquivar sem force. Evidências: commit `43e707e` registra `reflex compile --dry` aprovado, `pytest --ignore=evaluation` aprovado com 354 testes, e a única rodada do robô em 12 combinações; `openspec validate "estabiliza-xano-v8" --strict` e `openspec validate --specs --strict` passaram nesta conclusão (10 specs). O build de produção excedeu o timeout no prerender de `/`, o frontend não ficou disponível e nenhuma combinação recebeu PASSOU visual. A aparência implementada fica **aguardando conferência do usuário**; não houve aprovação visual.

## Workflow follow-up

- Fazer um commit pequeno em português após cada tarefa concluída, incluindo seu hash e resultado de teste na própria tarefa.
- Não executar comandos de escrita/sincronização no Xano; nenhum seed remoto será aplicado.
- Não alterar a lista compartilhada dos livros de exemplo.
- Registrar qualquer combinação visual que falhe como pendente de conferência; não alegar hidratação visual aprovada.
