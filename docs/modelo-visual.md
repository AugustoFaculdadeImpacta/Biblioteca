# Referência do modelo visual

## Commit escolhido

O snapshot de referência é `2afca9385ebc3a7fc52131f3f37f16f23e62518a` (`Registra evidências de contraste visual`, 22/11/2026, 16:23 -03), marcado localmente como `modelo-visual`. Ele é o pai imediato de `703331d3bd039b50162156537525a7bf72d50062` (`Separa menus de Perfil e Acessibilidade`). O arquivo `biblioteca_mais_nova/biblioteca_mais_nova.py` é idêntico em `2afca938` e no último commit anterior que o alterou, `f093328fe8500907e2647ee471c54e9774799c95`; portanto, `2afca938` é o último snapshot antes da separação dos menus.

## Evidências por critério

| Critério | Evidência no snapshot |
| --- | --- |
| Cabeçalho público com marca, Catálogo e Perfil, sem busca nem botão separado de Acessibilidade | `site_header` (linha 2515) compõe a marca, `site_primary_nav` (linha 2091) e `profile_menu` (linha 2404). Para visitante, a navegação contém Catálogo. A barra não compõe campo de busca nem menu separado de Acessibilidade. As versões desktop e móvel existem no DOM, com apenas uma visível por breakpoint. |
| Opções de aparência dentro do Perfil | `profile_appearance_controls` (linha 2344) reúne escala da fonte, alto contraste, redução de movimento e tema; `profile_menu` (linha 2404) inclui esses controles no menu Perfil. |
| Hero sem busca e sem ações, com texto e estatísticas | `index` (linha 3402) apresenta etiqueta, título, apoio e estatísticas do catálogo no hero. |
| Destaques, ação Ver mais e seção Sobre | `index` (linha 3402) compõe a seção Livros em destaque com Ver mais e a seção Sobre a biblioteca. |
| Cartão público de livro | `public_catalog_card` (linha 2722) reúne capa, categoria, título, autoria, disponibilidade e detalhes. |
| Rodapé | `site_footer` (linha 2572) apresenta Biblioteca escolar e Catálogo. |
| Tokens e estilos | `dark_theme_tokens` (linha 5211) define a paleta escura azul-marinho; os tokens claros e regras globais começam em `.a11y-shell` (linha 5274). Os estilos do cabeçalho, Perfil, hero, cartões e rodapé começam, respectivamente, em `.site-header` (linha 5350), `.profile-menu-content` (linha 5492), `.home-hero` (linha 5722), `.catalog-card, .catalog-detail-card` (linha 6042) e `.site-footer` (linha 6543). |

## Ajustes explícitos em relação ao código histórico

O código do snapshot dá ao acionador Perfil um fundo azul preenchido, embora tenha borda. A descrição visual solicitada especifica contorno; a restauração usará o estilo de contorno para Perfil, Acessibilidade e o controle com nome do usuário. O snapshot também usa `⭐` no título da seção; a interface restaurada usará `📚 Livros em destaque`, conforme a instrução explícita do usuário. Esses dois ajustes não alteram a seleção do snapshot estrutural.

Os excertos em [`modelo-visual/`](./modelo-visual/) são referências históricas em texto, extraídas desse estado do aplicativo. Não são importados pelo app.
