# Design

## Context

Ver [proposal.md](./proposal.md) para motivação e os deltas em `specs/` para o comportamento esperado. Hoje o Reflex envolve cada página em `.a11y-shell`; preferências de fonte, alto contraste e movimento reduzido já são aplicadas nessa camada. O cabeçalho contém `rx.menu` e a aplicação usa `rx.select.trigger` na seleção de título. O catálogo público fornece títulos, categorias e disponibilidade agregada; `descricao` já é opcional. A resposta pessoal de empréstimo local tipada contém exemplar e vencimento, mas não `titulo_id`; `solicitada_em` é opcional em pedidos. A tela de contas atual opera sobre bibliotecários e permite criar, ativar e desativar, não alterar genericamente o papel de qualquer conta.

## Goals / Non-Goals

**Goals:**

- Corrigir o ponto de renderização do cabeçalho eliminando o menu Radix e preservar os seletores Radix restantes apenas quando cada trigger tiver um único filho válido.
- Consolidar no Reflex a navegação, preferências e fluxos existentes, com estados acessíveis, dados de sessão privados e comportamento responsivo.
- Tornar o cliente tolerante à ausência de campos opcionais sem sucesso silencioso, inventar dados ou repetir escritas incertas.

**Non-Goals:**

- Alterar operações, regras, tabelas ou contratos no Xano real; criar endpoints; sincronizar schemas ou registros.
- Inventar contagem de popularidade, nome de título para empréstimo sem vínculo disponível, datas ausentes ou ações genéricas de alteração de papel.
- Implementar ferramentas de direção adiadas (indicadores novos, regras de empréstimo, auditoria, exportação CSV e aviso geral).
- Adicionar dependências de UI, fontes, ícones ou serviços externos.

## Decisions

1. **Disclosure nativo para Perfil.** Usar `<details>/<summary>` como controle expansível e manter a marcação condicional fora de qualquer trigger Radix. Um script inline pequeno trata Escape e clique fora; Escape fecha a caixa e devolve foco ao `summary`, e o listener de fora não consome a ação no destino. Alternativa descartada: conservar `rx.menu` e tentar corrigir a árvore de filhos, pois isso mantém a classe de falha relatada.
2. **Auditoria restrita dos triggers.** Procurar usos de `rx.menu`, `rx.popover`, `rx.dialog`, `rx.tooltip`, `rx.hover_card` e APIs `*.trigger` no código do app. Remover o menu Perfil Radix; não substituir automaticamente `rx.select.trigger`, que serve ao seletor de título e deve ser avaliado quanto a um único filho React antes de alteração. Uma regressão automatizada proíbe `rx.menu` nos módulos da aplicação.
3. **Uma fonte de navegação derivada da identidade real e visão ativa.** O layout mantém marca, um menu móvel colapsável e links específicos. O papel real governa autorização; a visão admin só ajusta destinos e rótulos, nunca permissões ou token. O controle para retornar à visão Administrador permanece fora de Perfil. `/perfil` e `/acessibilidade` tornam-se redirecionamentos compatíveis para `/`.
4. **Preferência de tema sem persistência.** Guardar o tema escuro apenas no estado corrente da página/sessão Reflex. A inicialização consulta `prefers-color-scheme`; o usuário pode alternar durante a sessão. Aplicar tokens pelo contêiner `.a11y-shell`, combinados às classes existentes de alto contraste/redução de movimento. Não gravar tema em LocalStorage, cookie, perfil ou backend. Validar contraste dos dois conjuntos e da combinação de alto contraste.
5. **Estatísticas derivadas, sem nova consulta.** Calcular total de títulos ativos, soma de exemplares disponíveis e categorias somente após o carregamento público atual. Mostrar estados de carregamento/erro/vazio existentes. A seção “Livros que mais saem” fica ausente até haver dado confiável de contagem por título.
6. **Metadados de capa tolerantes à evolução do contrato.** Tratar `capa_url` ausente, nulo ou vazio como ausência de imagem e usar a capa CSS existente; validar URL HTTPS quando preenchida. Incluir o campo somente quando preenchido e reportar recusas do serviço conforme os erros padrão, sem converter uma falha em sucesso nem repetir automaticamente. Registrar no `validacao-remota-xano` a tarefa exata: `Campo opcional \`capa_url\` na tabela \`titulo\` (URL HTTPS da capa do livro).` A descrição permanece opcional conforme contrato local existente.
7. **Manter contratos pessoais e identificar lacunas.** Reagrupar somente as solicitações, reservas e empréstimos já retornados, calcular dias restantes/atraso a partir do vencimento existente e não fabricar campos ausentes. O cliente atual não associa empréstimos pessoais a título: registrar dependência para `titulo_id`/título em `GET /minhas/emprestimos`. Se `solicitada_em` não vier, mostrar a data como indisponível e registrar sua validação. A autorização e decisão final continuam no backend.
8. **Reutilizar telas e ações administrativas existentes.** As abas de Pedidos e Empréstimos e devoluções compõem as interfaces atuais de reserva e circulação. Contas pode filtrar em memória as contas bibliotecárias carregadas e manter criar/ativar/desativar. Não apresentar promoção/rebaixamento genéricos até existir contrato que os suporte. Contadores operacionais só aparecem quando deriváveis dos registros já carregados.

## Risks / Trade-offs

- [Ausência de `capa_url` na API atual] → renderizar fallback sem falha; só enviar campo preenchido com erro explícito se o serviço não o aceitar; manter a validação do contrato como tarefa pendente.
- [Dados pessoais sem `titulo_id`/data] → não adivinhar nomes ou datas; apresentar ausência de modo explícito e manter tarefas de contrato pendentes em vez de alegar que a tela tem dados completos.
- [Script de interação duplicar listeners após navegação Reflex] → usar inicialização idempotente e listeners delegados; cobrir a estrutura e os caminhos Escape/foco/clique fora por testes focados, sem abrir navegador nem produzir capturas nesta execução. A conferência visual fica a cargo do usuário e não bloqueia os commits.
- [Tema do sistema e estado hidratado divergirem] → inicializar a escolha transitória por `matchMedia`, aplicar tokens somente em `.a11y-shell` e testar renderização/contraste nos estados claro, escuro e alto contraste.
- [Contas atuais não permitem alterar papéis arbitrários] → limitar as ações à capacidade comprovada pelo cliente e não inferir que desativar é equivalente a rebaixar perfil.

## Migration Plan

1. Após revisão humana dos artefatos, implementar por blocos curtos: navegação/Perfil/tema; home; catálogo/capas; área pessoal; abas operacionais.
2. Após cada bloco, executar `.\.venv\Scripts\python.exe -m reflex compile --dry` e `.\.venv\Scripts\python.exe -m pytest --ignore=evaluation -q`; registrar commits e testes. Não abrir navegador nem criar capturas; classificar itens visuais como “feito, aguarda conferência do usuário”.
3. Não executar operações remotas. Antes de qualquer futura sincronização, validar a tarefa `capa_url` no Change `validacao-remota-xano` e confirmar o destino Xano selecionado conforme o procedimento do projeto.
4. Reverter somente o bloco que falhar nos testes, preservando mudanças preexistentes e sem remover arquivos de ambiente/saída gerada.

## Open Questions

Não há decisões de comportamento pendentes para iniciar a implementação. A aceitação do campo `capa_url` pelo Xano e a associação título/empréstimo são dependências explícitas de validação de contrato, não decisões a presumir nesta Change.
