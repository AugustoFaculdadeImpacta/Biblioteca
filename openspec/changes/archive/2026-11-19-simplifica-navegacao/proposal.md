# Proposal

## Why

O cabeçalho atual usa `rx.menu`/Radix e a interface pode falhar ao renderizar quando o trigger recebe uma composição de filhos incompatível. Além disso, navegação, catálogo, área pessoal e telas operacionais precisam de uma organização mais previsível, mantendo regras de domínio e contratos Xano existentes.

## What Changes

- **BREAKING (navegação):** substituir o menu Radix do cabeçalho por `<details>/<summary>` nativo, fechar por Escape e clique fora, e simplificar a barra para uma linha adaptável ao perfil e à visão ativa.
- Usar um rodapé curto compartilhado em todas as rotas e remover atalhos de navegação duplicados do conteúdo das páginas.
- Reunir identidade, acessibilidade, alternância de tema escuro, saída e seletor de visão admin na caixa Perfil; remover `/perfil` e `/acessibilidade` do fluxo de navegação e redirecionar essas rotas para `/`.
- Acrescentar tema escuro com tokens no contêiner `.a11y-shell`, preferência inicial do sistema e escolha transitória por sessão de página, sem persistir a escolha.
- Organizar a home com estatísticas derivadas do catálogo carregado, destaques, apresentação da biblioteca e atalhos de acordo com o perfil. Não exibir seção de popularidade sem dado de empréstimos já disponível.
- Simplificar cartões e detalhe do catálogo; aceitar `capa_url` opcional de forma compatível com respostas que ainda não contenham o campo, preservando a capa CSS de fallback e mostrando descrição ausente de forma explícita.
- Consolidar a área pessoal em `/reservas`, com quatro grupos ordenados de solicitações, reservas aprovadas e empréstimos em dia/atraso; manter `/minha-biblioteca` como redirecionamento compatível.
- Organizar as telas operacionais de bibliotecário/admin em navegação e abas mais diretas, reutilizando as operações atuais. Não implementar indicadores, auditoria, exportação CSV, regras de empréstimo ou avisos gerais.
- Registrar a validação do novo campo no backlog `validacao-remota-xano`; não acessar nem alterar o Xano real nesta Change.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `frontend-foundation`: cabeçalho responsivo por perfil/visão, caixa Perfil nativa, remoção de Radix no menu, controles de acessibilidade no cabeçalho e tema escuro acessível.
- `primary-journeys`: home baseada em dados reais, atalhos por perfil e organização das entradas operacionais sem introduzir métricas indisponíveis.
- `catalog`: capas e descrições opcionais, simplificação de cartões e detalhe, ação condicionada ao papel.
- `loan-circulation`: apresentação da área pessoal em `/reservas`, com estados de pedidos e empréstimos e redirecionamento da rota anterior.
- `reservations`: agrupamento visual de reservas próprias e prazos, sem alterar FIFO, elegibilidade ou dados de outras pessoas.

## Impact

- Frontend Reflex: `biblioteca_mais_nova/biblioteca_mais_nova.py`, `biblioteca_mais_nova/catalog.py` e testes existentes em `tests/`.
- O cliente deve tolerar resposta sem `capa_url`; a presença do campo não pode ser presumida antes de validar o contrato. `descricao` já existe como metadado opcional no contrato local/spec e deve continuar opcional.
- Dependência pendente de validação: adicionar a `validacao-remota-xano` a tarefa `Campo opcional \`capa_url\` na tabela \`titulo\` (URL HTTPS da capa do livro).` antes de qualquer sincronização do contrato. Esta Change não executa operação remota.
- Dependências externas, endpoints novos, contagens de popularidade e qualquer regra de negócio nova ficam fora do escopo.
