# Design

## Layout

O cabeçalho usa grid CSS em desktop e três linhas operacionais em telas estreitas. Não há botão hambúrguer, variantes duplicadas ou links com classes de botão. Navegação e ações são componentes únicos, renderizados por perfil.

As páginas usam um contêiner único de até 75 rem. Grades de livros usam quatro, três ou cinco colunas conforme a largura, sem contêineres internos com altura fixa. Menus suspensos são os únicos painéis posicionados de forma absoluta.

## Conteúdo

A home apresenta banner, faixa de estatísticas, estante, novidades, categorias e três passos de reserva. O catálogo mantém busca, filtros e grade consistente. Detalhe, reservas, Acervo e Contas seguem hierarquias verticais claras.

## Capas e seed

A resolução mantém prioridade: `capa_url` HTTPS, ISBN do índice local ou informado, Open Library, e fallback SVG local. O seed contém 30 títulos reais em oito categorias. Escrita remota ocorre exclusivamente por `--apply`, exige credenciais no ambiente e continua idempotente.

## Verificação

Os testes Python cobrem estrutura e CSS. Um script Node dirigido ao Edge testa hidratação, cabeçalho, sobreposição, contraste, toque e fluxos contra a API demo. A alteração de layout deve ser corrigida até zero violações ou registrado como não verificado visualmente.
