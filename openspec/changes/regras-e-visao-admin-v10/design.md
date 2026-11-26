# Design

## Context

O frontend Reflex concentra navegação e cabeçalho em `biblioteca_mais_nova.py`, com operações de domínio em módulos como `circulation.py`; chamadas externas passam pelo cliente Xano compartilhado. A API de demonstração em `scripts/demo_api.py` já implementa fluxos de empréstimo e reservas. O Xano remoto não será consultado nem alterado nesta Change.

## Goals / Non-Goals

**Goals:**
- Separar perfil real da sessão e visão efetiva, preservando a sessão admin em todos os fluxos simulados.
- Centralizar a leitura e validação da configuração para páginas administrativas, detalhe do livro e API de demonstração.
- Corrigir a cascata CSS renderizada do botão Acessibilidade sem alterar geometria.

**Non-Goals:**
- Publicar ou testar operações contra o Xano real; as permissões e endpoints novos serão entregues para publicação manual.
- Mudar a identidade/autorização real da sessão, permitir gestão de contas fora do contrato ou alterar o layout aprovado.
- Inferir os valores vigentes no servidor quando a configuração não puder ser consultada.

## Decisions

- **Visão é estado de apresentação, não identidade.** Guardas e menus consultam o perfil real e a visão efetiva; chamadas continuam usando a sessão/token original. A visão Estudante ou Bibliotecário não cria token, perfil ou usuário substituto. As rotas exclusivas seguem as guardas do spec, com `/regras` como exceção acessível ao admin real em qualquer visão.
- **Configuração tem uma fonte única e um contrato estrito.** Os sete campos são validados no cliente e novamente na API de demonstração. O corpo de gravação contém somente esses campos; metadados retornados podem ser exibidos, mas não enviados. A leitura é cacheada por 60 segundos e escrita bem-sucedida invalida o cache.
- **Padrões não simulam publicação.** Em 403 ou 404 na leitura, a tela usa os padrões especificados apenas para exibição, fica somente leitura e apresenta a orientação de publicação. Falhas diferentes permanecem erros visíveis, sem fallback silencioso.
- **Regras são aplicadas no servidor.** A API de demonstração valida limite de empréstimos e pedidos, atraso, reserva ativa, autorização bibliotecária, prazo de empréstimo e oferta de retirada. O frontend usa os valores apenas para informar e melhorar a experiência; cada operação revalida o estado.
- **Estilo parte da cascata efetiva.** Inspecionar árvore do cabeçalho, seletores e CSS gerado; identificar estados e variáveis vencedores. Reutilizar os tokens do botão Perfil e aplicar uma regra específica ao controle Acessibilidade e descendentes com prioridade suficiente, validando CSS final e contraste. Não alterar dimensões, posição ou formato.

## Risks / Trade-offs

- [O Xano ainda pode recusar ações simuladas ou não ter endpoints de regras] → apresentar mensagem de publicação clara e registrar os passos manuais em `docs/publicacao-xano-regras.md`; a Change não afirma validação remota.
- [Armazenar visão junto ao perfil pode falsificar permissões] → manter campos distintos e testar chamadas para garantir que a sessão e identidade usadas são as reais.
- [Cache de regras pode mostrar valor anterior por até 60 segundos] → invalidar após salvar e não usar valores de cache como autorização.
- [CSS gerado pode divergir da regra fonte] → validar seletores no CSS compilado e calcular cores renderizadas; se Edge headless exceder 60 segundos, registrar “aguarda conferência do usuário”.

## Migration Plan

1. Implementar visão efetiva e guardas, preservando a sessão real.
2. Adicionar API de regras e comportamento equivalente na demonstração, com testes.
3. Implementar página, resumo de limites e mensagens de erro, depois corrigir a regra CSS do cabeçalho.
4. Rodar `.\.venv\Scripts\python.exe -m reflex compile --dry` e, em seguida, pytest; atualizar `docs/relatorio-noite.md`.
5. Entregar o contrato para publicação manual no Xano. Não executar publicação nesta Change.

Rollback local consiste em reverter os commits desta Change; nenhuma migração ou escrita remota será executada.
