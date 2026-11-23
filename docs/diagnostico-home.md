# Diagnóstico de layout da home

## Regras existentes antes da correção

As regras abaixo foram lidas de `app.style` em `biblioteca_mais_nova/biblioteca_mais_nova.py`.

| seletor | regras de layout do snapshot | observação |
|---|---|---|
| `.content-section` | `display:flex`, `flex-direction:column`, `gap:1.25rem`, `width:100%`, `max-width:75rem`, `margin:0 auto`, `padding:1.5rem 0` | Container de seção com fluxo normal. A margem só centraliza horizontalmente. |
| `.home-hero` | `width:100%`, `max-width:72rem`, `max-height:180px`, `margin:1rem auto`, `padding:clamp(1.5rem, 3vw, 2.5rem)` | `max-height` comprime o conteúdo do banner e causa transbordamento. Não há `overflow:hidden`, posição absoluta/fixa ou transformação nesta regra. |
| `.hero-layout` | `display:flex`, `flex-wrap:wrap`, `align-items:center`, `justify-content:space-between`, `width:100%`, `gap:1.5rem` | O layout não era o grid pedido e permitia que conteúdo fosse distribuído em linhas imprevisíveis. |
| `.hero-copy-wrap` | `flex:1 1 20rem`, `max-width:36rem` | Limita a largura, mas não a altura. |
| `.eyebrow` | `display:inline-flex`, padding, radius, cores e tipografia | Sem altura, overflow, posição ou transformação de posicionamento. |
| `.hero-copy` | cor, `font-size:1.05rem`, `max-width:32rem` | Sem altura ou corte. |
| `.hero-stat-grid` | `display:grid`, `grid-template-columns:repeat(auto-fit, minmax(min(100%, 10rem), 1fr))`, `gap:0.9rem`, `flex:1 1 18rem`, `min-width:0` | Três cartões ocupavam uma área própria dentro do banner em vez de uma faixa textual logo abaixo dele. |
| `.hero-stat-card` | flex em coluna, `min-height:6.5rem`, padding, borda, fundo e sombra | A altura mínima aumenta o bloco; os cartões não eram posicionados fora do fluxo. |
| `.hero-stat-value`, `.hero-stat-label` | tipografia e cores | Sem altura, overflow, posição ou transformação de posicionamento. |
| `.home-catalog-section` | padding responsivo, borda, radius, fundo e sombra | Sem altura, corte ou posicionamento. |
| `.home-about-section` | `width:100%`, `max-width:72rem`, `margin:1rem auto`, borda, fundo | Centralizada com margem positiva; não há margem negativa. |
| `.home-about-section p` | `max-width:50rem`, cor | Sem corte. |
| `.home-stat-status` | `display:flex`, `min-height:6.5rem`, padding, borda, fundo e cor | O estado de carregamento/erro também ocupa altura mínima de cartão. |
| `.home-section-heading` | flex com `flex-wrap:wrap`, alinhamento, distribuição e gap | Fluxo flex normal. |
| `.home-category-list` | flex com `flex-wrap:wrap`, gap e largura total | Regra anterior à definição final do trilho. |
| `.home-category-chip` (regra inicial) | `display:inline-flex`, alinhamento, `min-height:2.5rem`, padding, borda, fundo e texto | Sobrescrita depois pela regra do trilho. |
| `.home-category-rail` | flex, `flex-wrap:nowrap`, `overflow-x:auto`, gap, padding e largura total | Trilho horizontal intencional; não tinha `margin-top`. |
| `.home-category-chip` (regra efetiva) | `display:inline-flex`, `flex:0 0 auto`, `min-height:2.75rem`, padding, borda, fundo, texto | A pílula fica em fluxo normal dentro do trilho. |
| `.home-category-shelf` | flex, `flex-wrap:nowrap`, `overflow-x:auto`, gap e padding inferior | Regra de carrossel de cartões. Também era aplicada à grade principal da home, substituindo visualmente o grid por uma faixa horizontal. |
| `.home-category-shelf .catalog-card` | `flex:0 0 13.75rem` | Impedia a grade da estante de se distribuir em colunas. |
| `@media (max-width:48rem) .hero-layout` | `align-items:stretch`, `flex-direction:column` | Responsivo para o antigo flex; deve ser atualizado para o grid novo. |
| `@media (max-width:48rem) .hero-copy-wrap, .hero-stat-grid` | `width:100%`, `max-width:100%` | Mantém largura, mas o bloco de estatísticas não deve mais fazer parte do banner. |

## Propriedades de risco encontradas

- **Altura limitada:** `.home-hero` tinha `max-height:180px`.
- **Altura fixa:** nenhuma regra de `.hero-*` ou `.home-*` declarava `height` fixa.
- **Overflow que corta conteúdo:** nenhuma regra de hero ou home tinha `overflow:hidden`; `.home-category-rail` e `.home-category-shelf` usam `overflow-x:auto` para rolagem horizontal.
- **Posicionamento absoluto/fixo:** nenhuma regra de hero ou home usava `position:absolute` ou `position:fixed`.
- **Transformação de posicionamento:** nenhuma regra de hero ou home aplicava `transform` de posicionamento.
- **Margens negativas:** nenhuma regra de hero ou home usava margem negativa.
- **Colisão estrutural:** a estante de destaque recebia simultaneamente `catalog-grid` e `home-category-shelf`; a regra posterior de carrossel substituía o grid e mantinha cartões com largura fixa.

## Contrato após correção

- Banner sem altura máxima ou fixa, com grid `minmax(0, 1fr) auto`, gap de `1.5rem`, alinhamento central e padding de `1.5rem`; em tela estreita vira uma coluna.
- Estatísticas em uma faixa colorida após o banner, apresentadas em flex-wrap e fluxo estático, sem cartões flutuantes.
- Pílulas seguem o banner em fluxo normal, com flex sem quebra, rolagem horizontal e margem superior positiva.
- Seções permanecem em fluxo normal com margem inferior de `1.5rem`.
- Filhos de flex/grid recebem `min-width:0`; a grade da estante usa `auto-fill` entre `160px` e `200px`, com capas 2:3.

## Regras efetivas depois da correção

Este inventário foi conferido no `app.style` e nos componentes após a reorganização. Propriedades de cor e apresentação estão incluídas para permitir comparar cada regra efetiva, não apenas os riscos de geometria.

| seletor | declarações efetivas |
|---|---|
| `*` | `min-width:0` |
| `.content-section` | flex em coluna; `align-items:flex-start`; `gap:1.25rem`; `width:100%`; `max-width:75rem`; `margin:0 auto 1.5rem`; `padding:1.5rem 0` |
| `.home-hero` | `width:100%`; `max-width:75rem`; `margin:0 auto 1.5rem`; `padding:0.75rem`; borda e raio `1.2rem`; gradiente de marca e sombra suave |
| `.hero-layout` | grid `minmax(0, 1fr) auto`; `align-items:center`; `width:100%`; `gap:1.5rem`; `padding:1.5rem`; cartão `var(--bg-panel)` com raio `0.9rem` |
| `.hero-copy-wrap` | `min-width:0` |
| `.hero-copy` | cor `var(--slate-700)`; fonte `1.05rem`; largura máxima `100%`; usada também no perfil |
| `.home-search-form` | grid `minmax(0, 1fr) auto`; alinhamento central; `gap:0.5rem`; largura `min(100%, 30rem)`; padding, borda, raio e fundo suave |
| `.home-search-input` | `height:auto`; `min-height:3rem`; sem borda; fundo transparente; fonte `1rem` |
| `.home-search-submit` | `min-height:3rem`; padding `0.5rem 1rem`; borda e raio; cores de ação primária; peso `700` |
| `.home-stat-band` | flex em linha com `flex-wrap:wrap`; `position:static`; alinhamento central; `gap:0.35rem`; `width:100%`; padding `1rem`; fundo de marca e texto de ação primária |
| `.home-profile-summary` | `gap:0.75rem`; padding `1rem 1.25rem`; borda, raio e fundo de painel |
| `.home-profile-summary h2` | `margin:0` |
| `.home-summary-metrics` | flex com quebra de linha; `gap:0.75rem`; `width:100%` |
| `.home-summary-metric` | flex em coluna; `gap:0.2rem`; `min-width:8rem`; padding; raio e fundo suave |
| `.home-section-copy` | `min-width:0` |
| `.home-section-copy h2` | `margin:0`; peso `800` |
| `.home-section-subtitle` | cor cinza `var(--slate-700)` |
| `.home-book-section` | `gap:1rem`; `margin-bottom:1.5rem` |
| `.home-book-section-content` | flex em coluna; filhos esticados; `gap:1rem`; `width:100%`; `min-width:0` |
| `.home-book-grid` | `repeat(auto-fill, minmax(min(100%, 10rem), 12.5rem))`; itens esticados; `width:100%` |
| `.home-empty-state` | `width:100%`; padding; raio; fundo suave e cor legível |
| `.home-view-more` | flex centralizado; `width:100%`; `min-height:2.75rem`; padding; raio; fundo e texto de ação primária; sem decoração de link |
| `.home-category-section` | `gap:0.75rem`; `margin-bottom:1.5rem` |
| `.home-category-rail` | flex sem quebra; `overflow-x:auto`; `gap:0.6rem`; `width:100%`; `margin-top:1rem`; padding vertical |
| `.home-category-chip` | flex sem encolher; alinhamento central; `min-height:2.75rem`; padding; borda e raio de pílula; fundo e texto do tema |
| `.home-reservation-section` | `gap:0.75rem`; `margin-bottom:1.5rem` |
| `.home-reservation-steps` | grid de três colunas `minmax(0, 1fr)`; `gap:1rem`; `width:100%`; `margin:0`; padding esquerdo `1.25rem` |
| `.status-pill` e variantes | pílulas de estado em fluxo inline, com altura mínima `1.8rem`, padding, raio e cores específicas; sem altura fixa ou posicionamento |
| `@media (max-width:48rem) .hero-layout` | grid de uma coluna `minmax(0, 1fr)`; alinhamento central |
| `@media (48.01rem–64rem) .home-book-grid` | quatro colunas `minmax(0, 1fr)` |
| `@media (max-width:48rem) .home-book-grid` | três colunas `minmax(0, 1fr)` |
| `@media (max-width:30rem) .home-book-grid` | duas colunas `minmax(0, 1fr)` |

As regras antigas `.hero-stat-*`, `.home-stat-status`, `.home-category-shelf` e o componente que reutilizava o carrossel para a estante foram removidos. Na home não há `height`, `max-height`, `overflow:hidden`, posição absoluta/fixa, transformação de posicionamento ou margem negativa em hero, estatísticas, categorias ou seções. A única rolagem intencional da home é horizontal no trilho de categorias. As capas usam proporção `2 / 3`; a grade geral da estante continua em fluxo normal e não força um trilho.

## Resultado da varredura das demais páginas

As classes de conteúdo de Catálogo, Detalhe, Reservas, Acervo, Contas, Login e Cadastro foram verificadas junto com os estilos da home. As ações do detalhe móvel deixaram de ficar fixas no rodapé; agora acompanham o fluxo da seção. A capa substituta do Acervo também deixou de cortar o título e usa proporção `2 / 3`. O detalhe do livro preserva o grid de duas colunas no desktop e uma coluna em telas estreitas.

Permanecem posicionados somente o cabeçalho `sticky`, os painéis de menus suspensos e o link de pular conteúdo, que fica fora da área visível até receber foco para preservar a navegação por teclado. Efeitos `translateY` restantes são animações ou estados de hover/pressionamento, não posicionamento de contêineres. Campos mantêm altura mínima/altura de controle para atingir o alvo de toque; não são contêineres de conteúdo.
