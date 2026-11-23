# Diagnóstico de layout da home

## Regras existentes antes da correção

As regras abaixo foram lidas de `app.style` em `biblioteca_mais_nova/biblioteca_mais_nova.py`.

| seletor | regras de layout atuais | observação |
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
