# Tasks

## 1. Barra de navegação

- [x] 1.1 Fazer o realce pertencer ao controle externo inteiro, impedir encolhimento/corte de marca, links, Perfil e Acessibilidade, manter foco visível no mesmo formato e cobrir o contrato de CSS em testes; `pytest tests/test_navigation.py tests/test_icons.py -q` passou (55 testes); implementação no commit `c9a4b7d`.

## 2. Capas públicas

- [x] 2.1 Manter a capa SVG gerada como camada inferior acessível, ocultar imagens reais que falhem por um único script no head e testar cartões/detalhes e a varredura de imagens já falhadas; `pytest tests/test_catalog.py tests/test_covers.py -q` passou (37 testes), e `node --check` validou o script; implementação no commit `bec7045`.
- [ ] 2.2 Resolver capas Open Library no servidor por título e primeira autoria, com cache, timeout, limite de concorrência, modo sem rede e execução posterior ao primeiro render; testar resultado mais parecido, cache, falha silenciosa, prioridade e concorrência com transporte simulado usando `pytest tests/test_covers.py tests/test_catalog.py`.

## 3. Cliente Xano resiliente

- [ ] 3.1 Implementar diagnóstico opt-in sem segredos, contagem por carregamento, semáforo de três chamadas, retries exclusivamente GET com backoff/Retry-After e mensagens específicas; documentar uso em `docs/diagnostico-xano.md` e verificar com `pytest tests/test_xano_client.py tests/test_circulation.py tests/test_catalog.py`.

## 4. Carregamentos e cache por rota

- [ ] 4.1 Auditar home, catálogo, detalhe, reservas, Acervo e Contas; reutilizar catálogo/categorias por 60 s com invalidação após escritas, evitar consultas pessoais sem sessão/necessidade, encerrar flags em `finally`, oferecer retry visível e separar os indicadores da home; cobrir chamadas/cache/erros em testes e completar a tabela de rotas em `docs/diagnostico-xano.md`.

## 5. Diagnóstico do Acervo

- [ ] 5.1 Criar “🩺 Testar conexão” exclusivo para admin real, com cinco leituras sequenciais, resumo solicitado e testes simulados; conferir o PATCH local de desativação contra um pull remoto somente leitura se o workspace/branch/ambiente selecionados forem confirmados sem ambiguidade, caso contrário registrar a limitação sem acessar destino remoto.

## 6. Importação retomável

- [ ] 6.1 Executar a importação em evento Reflex de segundo plano, com progresso, pausa de 1,5 s, repetição limitada após releitura, retomada idempotente e parada após três falhas; testar pausa, repetição, retomada e interrupção, e confirmar que os 30 dados originais ainda incluem Dom Casmurro e Memórias Póstumas de Brás Cubas.

## 7. Integração e fechamento

- [ ] 7.1 Rodar compile `--dry` e pytest em sequência, uma rodada do robô apenas nas rotas e larguras solicitadas com limite de 10 minutos, registrar fatos/lacunas no relatório, validar Change e specs com `--strict`, sincronizar specs, arquivar e enviar commits sem force.

## Workflow follow-up

- Fazer um commit pequeno em português após cada tarefa concluída, incluindo seu hash e resultado de teste na própria tarefa.
- Não executar comandos de escrita/sincronização no Xano; nenhum seed remoto será aplicado.
- Não alterar a lista compartilhada dos livros de exemplo.
- Registrar qualquer combinação visual que falhe como pendente de conferência; não alegar hidratação visual aprovada.
