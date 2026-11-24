# Verificação de layout

O Edge foi lançado em headless na porta 9333, mas o robô não terminou a matriz de 216 combinações no prazo operacional e não produziu uma tabela completa nem capturas PNG verificadas.

Resultado: **não verificado visualmente**.

As rotas foram aquecidas pela página local, mas não há evidência visual desta execução para declarar PASSOU ou FALHOU por rota/perfil/largura/tema.

Fluxos funcionais: não cobertos nesta execução do robô; o script ainda não confirma reserva, aprovação, cadastro de acervo, troca de visão ou criação de bibliotecário como PASSOU.

## Rodada 2026-11-23T07:50:29.266Z

| rota | perfil | largura | tema | resultado | violações | captura |
|---|---|---:|---|---|---|---|
| / | visitante | 360 | claro | FALHOU | alvos menores que 44px=1 | [PNG](./capturas/verificacao/home-visitante-360-claro.png) |
| / | visitante | 360 | escuro | FALHOU | alvos menores que 44px=1 | [PNG](./capturas/verificacao/home-visitante-360-escuro.png) |
| / | visitante | 1366 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-1366-claro.png) |
| / | visitante | 1366 | escuro | FALHOU | erro de navegação ou inspeção | [PNG](./capturas/verificacao/home-visitante-1366-escuro.png) |
| /catalogo | visitante | 360 | claro | FALHOU | filhos fora do contêiner=1; alvos menores que 44px=2 | [PNG](./capturas/verificacao/catalogo-visitante-360-claro.png) |
| /catalogo | visitante | 360 | escuro | FALHOU | alvos menores que 44px=1 | [PNG](./capturas/verificacao/catalogo-visitante-360-escuro.png) |
| /catalogo | visitante | 1366 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/catalogo-visitante-1366-claro.png) |
| /catalogo | visitante | 1366 | escuro | FALHOU | filhos fora do contêiner=2 | [PNG](./capturas/verificacao/catalogo-visitante-1366-escuro.png) |
| /catalogo/1 | visitante | 360 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/catalogo-1-visitante-360-claro.png) |
| /catalogo/1 | visitante | 360 | escuro | FALHOU | filhos fora do contêiner=1; alvos menores que 44px=2 | [PNG](./capturas/verificacao/catalogo-1-visitante-360-escuro.png) |
| /catalogo/1 | visitante | 1366 | claro | FALHOU | filhos fora do contêiner=3; contraste abaixo de 4,5:1=1; alvos menores que 44px=1 | [PNG](./capturas/verificacao/catalogo-1-visitante-1366-claro.png) |
| /catalogo/1 | visitante | 1366 | escuro | FALHOU | filhos fora do contêiner=3; alvos menores que 44px=1 | [PNG](./capturas/verificacao/catalogo-1-visitante-1366-escuro.png) |
| /login | visitante | 360 | claro | FALHOU | alvos menores que 44px=1 | [PNG](./capturas/verificacao/login-visitante-360-claro.png) |
| /login | visitante | 360 | escuro | FALHOU | alvos menores que 44px=1 | [PNG](./capturas/verificacao/login-visitante-360-escuro.png) |
| /login | visitante | 1366 | claro | FALHOU | filhos fora do contêiner=2 | [PNG](./capturas/verificacao/login-visitante-1366-claro.png) |
| /login | visitante | 1366 | escuro | FALHOU | filhos fora do contêiner=2 | [PNG](./capturas/verificacao/login-visitante-1366-escuro.png) |
| /cadastro | visitante | 360 | claro | FALHOU | alvos menores que 44px=1 | [PNG](./capturas/verificacao/cadastro-visitante-360-claro.png) |
| /cadastro | visitante | 360 | escuro | FALHOU | alvos menores que 44px=1 | [PNG](./capturas/verificacao/cadastro-visitante-360-escuro.png) |
| /cadastro | visitante | 1366 | claro | FALHOU | filhos fora do contêiner=2 | [PNG](./capturas/verificacao/cadastro-visitante-1366-claro.png) |
| /cadastro | visitante | 1366 | escuro | FALHOU | filhos fora do contêiner=2 | [PNG](./capturas/verificacao/cadastro-visitante-1366-escuro.png) |
| /reservas | estudante | 1366 | escuro | FALHOU | autenticação do perfil falhou; filhos fora do contêiner=2 | [PNG](./capturas/verificacao/reservas-estudante-1366-escuro.png) |
| /reservas | estudante | 360 | escuro | FALHOU | autenticação do perfil falhou; alvos menores que 44px=1 | [PNG](./capturas/verificacao/reservas-estudante-360-escuro.png) |
| /admin/acervo | bibliotecario | 1366 | escuro | FALHOU | autenticação do perfil falhou; filhos fora do contêiner=2 | [PNG](./capturas/verificacao/admin-acervo-bibliotecario-1366-escuro.png) |
| /admin/acervo | bibliotecario | 360 | escuro | FALHOU | autenticação do perfil falhou; filhos fora do contêiner=1; alvos menores que 44px=1 | [PNG](./capturas/verificacao/admin-acervo-bibliotecario-360-escuro.png) |
| /admin/reservas | bibliotecario | 1366 | escuro | FALHOU | autenticação do perfil falhou; filhos fora do contêiner=2 | [PNG](./capturas/verificacao/admin-reservas-bibliotecario-1366-escuro.png) |
| /admin/reservas | bibliotecario | 360 | escuro | FALHOU | autenticação do perfil falhou; alvos menores que 44px=1 | [PNG](./capturas/verificacao/admin-reservas-bibliotecario-360-escuro.png) |
| /admin/bibliotecarios | admin | 1366 | escuro | FALHOU | autenticação do perfil falhou; redirecionado para /login; filhos fora do contêiner=2 | [PNG](./capturas/verificacao/admin-bibliotecarios-admin-1366-escuro.png) |
| /admin/bibliotecarios | admin | 360 | escuro | FALHOU | autenticação do perfil falhou; alvos menores que 44px=1 | [PNG](./capturas/verificacao/admin-bibliotecarios-admin-360-escuro.png) |

## Rodada 2026-11-23T08:24:22.224Z

| rota | perfil | largura | tema | resultado | violações | captura |
|---|---|---:|---|---|---|---|
| / | visitante | 360 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-360-claro.png) |
| / | visitante | 360 | escuro | FALHOU | alvos menores que 44px=a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/home-visitante-360-escuro.png) |
| / | visitante | 1366 | claro | FALHOU | filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/home-visitante-1366-claro.png) |
| / | visitante | 1366 | escuro | FALHOU | erro de navegação ou inspeção | [PNG](./capturas/verificacao/home-visitante-1366-escuro.png) |
| /catalogo | visitante | 360 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/catalogo-visitante-360-claro.png) |
| /catalogo | visitante | 360 | escuro | FALHOU | alvos menores que 44px=a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/catalogo-visitante-360-escuro.png) |
| /catalogo | visitante | 1366 | claro | FALHOU | filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/catalogo-visitante-1366-claro.png) |
| /catalogo | visitante | 1366 | escuro | FALHOU | filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/catalogo-visitante-1366-escuro.png) |
| /catalogo/1 | visitante | 360 | claro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; contraste abaixo de 4,5:1=button; alvos menores que 44px=button,a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/catalogo-1-visitante-360-claro.png) |
| /catalogo/1 | visitante | 360 | escuro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; alvos menores que 44px=button,a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/catalogo-1-visitante-360-escuro.png) |
| /catalogo/1 | visitante | 1366 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/catalogo-1-visitante-1366-claro.png) |
| /catalogo/1 | visitante | 1366 | escuro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div,summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-1366-escuro.png) |
| /login | visitante | 360 | claro | FALHOU | alvos menores que 44px=a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/login-visitante-360-claro.png) |
| /login | visitante | 360 | escuro | FALHOU | alvos menores que 44px=a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/login-visitante-360-escuro.png) |
| /login | visitante | 1366 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/login-visitante-1366-claro.png) |
| /login | visitante | 1366 | escuro | FALHOU | filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/login-visitante-1366-escuro.png) |
| /cadastro | visitante | 360 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/cadastro-visitante-360-claro.png) |
| /cadastro | visitante | 360 | escuro | FALHOU | hidratação | [PNG](./capturas/verificacao/cadastro-visitante-360-escuro.png) |
| /cadastro | visitante | 1366 | claro | FALHOU | filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/cadastro-visitante-1366-claro.png) |
| /cadastro | visitante | 1366 | escuro | FALHOU | filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/cadastro-visitante-1366-escuro.png) |
| /reservas | estudante | 1366 | escuro | FALHOU | autenticação do perfil falhou; redirecionado para /login; filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/reservas-estudante-1366-escuro.png) |
| /reservas | estudante | 360 | escuro | FALHOU | autenticação do perfil falhou; alvos menores que 44px=a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/reservas-estudante-360-escuro.png) |
| /admin/acervo | bibliotecario | 1366 | escuro | FALHOU | autenticação do perfil falhou; redirecionado para /login; filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/admin-acervo-bibliotecario-1366-escuro.png) |
| /admin/acervo | bibliotecario | 360 | escuro | FALHOU | autenticação do perfil falhou; alvos menores que 44px=a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/admin-acervo-bibliotecario-360-escuro.png) |
| /admin/reservas | bibliotecario | 1366 | escuro | FALHOU | autenticação do perfil falhou; filhos fora do contêiner=div.rt-Box.app-shell>div.a11y-shell.css-1thazht.a11y-dark,summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu; alvos menores que 44px=a.rt-Text.rt-reset.rt-Link.rt-underline-auto.profile-menu-item.css-1macts | [PNG](./capturas/verificacao/admin-reservas-bibliotecario-1366-escuro.png) |
| /admin/reservas | bibliotecario | 360 | escuro | FALHOU | autenticação do perfil falhou; hidratação | [PNG](./capturas/verificacao/admin-reservas-bibliotecario-360-escuro.png) |
| /admin/bibliotecarios | admin | 1366 | escuro | FALHOU | autenticação do perfil falhou; filhos fora do contêiner=summary.accessibility-menu-trigger>details.site-disclosure.accessibility-menu,summary.profile-menu-trigger>details.site-disclosure.profile-menu | [PNG](./capturas/verificacao/admin-bibliotecarios-admin-1366-escuro.png) |
| /admin/bibliotecarios | admin | 360 | escuro | FALHOU | autenticação do perfil falhou; alvos menores que 44px=a.rt-Text.rt-reset.rt-Link.rt-underline-auto.brand-link.css-1macts | [PNG](./capturas/verificacao/admin-bibliotecarios-admin-360-escuro.png) |

Duração desta rodada: 801s. Limite total: 1200s.

## Rodada 2026-11-23T08:47:24.527Z

| rota | perfil | largura | tema | resultado | violações | captura |
|---|---|---:|---|---|---|---|
| / | visitante | 360 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/home-visitante-360-claro.png) |
| / | visitante | 360 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/home-visitante-360-escuro.png) |
| / | visitante | 1366 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/home-visitante-1366-claro.png) |
| / | visitante | 1366 | escuro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-1366-escuro.png) |
| /catalogo | visitante | 360 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-360-claro.png) |
| /catalogo | visitante | 360 | escuro | FALHOU | hidratação | [PNG](./capturas/verificacao/catalogo-visitante-360-escuro.png) |
| /catalogo | visitante | 1366 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/catalogo-visitante-1366-claro.png) |
| /catalogo | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-1366-escuro.png) |
| /catalogo/1 | visitante | 360 | claro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; contraste abaixo de 4,5:1=button; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-360-claro.png) |
| /catalogo/1 | visitante | 360 | escuro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-360-escuro.png) |
| /catalogo/1 | visitante | 1366 | claro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; contraste abaixo de 4,5:1=button; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-1366-claro.png) |
| /catalogo/1 | visitante | 1366 | escuro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-1366-escuro.png) |
| /login | visitante | 360 | claro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; contraste abaixo de 4,5:1=button; alvos menores que 44px=button | [PNG](./capturas/verificacao/login-visitante-360-claro.png) |
| /login | visitante | 360 | escuro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; alvos menores que 44px=button | [PNG](./capturas/verificacao/login-visitante-360-escuro.png) |
| /login | visitante | 1366 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/login-visitante-1366-claro.png) |
| /login | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/login-visitante-1366-escuro.png) |
| /cadastro | visitante | 360 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/cadastro-visitante-360-claro.png) |
| /cadastro | visitante | 360 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/cadastro-visitante-360-escuro.png) |
| /cadastro | visitante | 1366 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/cadastro-visitante-1366-claro.png) |
| /cadastro | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/cadastro-visitante-1366-escuro.png) |
| /reservas | estudante | 1366 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/reservas-estudante-1366-escuro.png) |
| /reservas | estudante | 360 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/reservas-estudante-360-escuro.png) |
| /admin/acervo | bibliotecario | 1366 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-acervo-bibliotecario-1366-escuro.png) |
| /admin/acervo | bibliotecario | 360 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-acervo-bibliotecario-360-escuro.png) |
| /admin/reservas | bibliotecario | 1366 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-reservas-bibliotecario-1366-escuro.png) |
| /admin/reservas | bibliotecario | 360 | escuro | FALHOU | conta de demonstração indisponível; hidratação | [PNG](./capturas/verificacao/admin-reservas-bibliotecario-360-escuro.png) |
| /admin/bibliotecarios | admin | 1366 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-bibliotecarios-admin-1366-escuro.png) |
| /admin/bibliotecarios | admin | 360 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-bibliotecarios-admin-360-escuro.png) |

Duração desta rodada: 666s. Limite total: 1200s.

## Rodada 2026-11-23T09:05:48.605Z

| rota | perfil | largura | tema | resultado | violações | captura |
|---|---|---:|---|---|---|---|
| / | visitante | 360 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-360-claro.png) |
| / | visitante | 360 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/home-visitante-360-escuro.png) |
| / | visitante | 1366 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-1366-claro.png) |
| / | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/home-visitante-1366-escuro.png) |
| /catalogo | visitante | 360 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-360-claro.png) |
| /catalogo | visitante | 360 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-360-escuro.png) |
| /catalogo | visitante | 1366 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-1366-claro.png) |
| /catalogo | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-1366-escuro.png) |
| /catalogo/1 | visitante | 360 | claro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; contraste abaixo de 4,5:1=button; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-360-claro.png) |
| /catalogo/1 | visitante | 360 | escuro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-360-escuro.png) |
| /catalogo/1 | visitante | 1366 | claro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; contraste abaixo de 4,5:1=button; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-1366-claro.png) |
| /catalogo/1 | visitante | 1366 | escuro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; alvos menores que 44px=button | [PNG](./capturas/verificacao/catalogo-1-visitante-1366-escuro.png) |
| /login | visitante | 360 | claro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; contraste abaixo de 4,5:1=button; alvos menores que 44px=button | [PNG](./capturas/verificacao/login-visitante-360-claro.png) |
| /login | visitante | 360 | escuro | FALHOU | erro de conexão/renderização ou corpo menor que 200 caracteres; filhos fora do contêiner=svg>div; alvos menores que 44px=button | [PNG](./capturas/verificacao/login-visitante-360-escuro.png) |
| /login | visitante | 1366 | claro | FALHOU | hidratação | [PNG](./capturas/verificacao/login-visitante-1366-claro.png) |
| /login | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/login-visitante-1366-escuro.png) |
| /cadastro | visitante | 360 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/cadastro-visitante-360-claro.png) |
| /cadastro | visitante | 360 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/cadastro-visitante-360-escuro.png) |
| /cadastro | visitante | 1366 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/cadastro-visitante-1366-claro.png) |
| /cadastro | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/cadastro-visitante-1366-escuro.png) |
| /reservas | estudante | 1366 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/reservas-estudante-1366-escuro.png) |
| /reservas | estudante | 360 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/reservas-estudante-360-escuro.png) |
| /admin/acervo | bibliotecario | 1366 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-acervo-bibliotecario-1366-escuro.png) |
| /admin/acervo | bibliotecario | 360 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-acervo-bibliotecario-360-escuro.png) |
| /admin/reservas | bibliotecario | 1366 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-reservas-bibliotecario-1366-escuro.png) |
| /admin/reservas | bibliotecario | 360 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-reservas-bibliotecario-360-escuro.png) |
| /admin/bibliotecarios | admin | 1366 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-bibliotecarios-admin-1366-escuro.png) |
| /admin/bibliotecarios | admin | 360 | escuro | FALHOU | conta de demonstração indisponível | [PNG](./capturas/verificacao/admin-bibliotecarios-admin-360-escuro.png) |

Duração desta rodada: 992s. Limite total: 1200s.

A matriz registrou as 28 combinações, mas a execução terminou com código 1:
a limpeza do Edge pelo filtro WMI excedeu o tempo limite. O perfil temporário
exclusivo desta rodada foi removido após o término do processo. O robô foi
ajustado depois para encerrar pelo PID que iniciou; essa revisão não foi
executada em uma quinta rodada.

A inspeção das capturas também mostrou estado `Carregando` nas duas
combinações escuras da home e nas quatro combinações do catálogo que o robô
registrou como `PASSOU`. Elas não contam como confirmação visual de conteúdo
carregado. O critério do robô foi ajustado para detectar esse estado, sem uma
quinta rodada.

## Rodada 2026-11-23T21:17:58.468Z

| rota | perfil | largura | tema | resultado | violações | captura |
|---|---|---:|---|---|---|---|
| / | visitante | 360 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/home-visitante-360-claro.png) |
| / | visitante | 360 | escuro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-360-escuro.png) |
| / | visitante | 1366 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/home-visitante-1366-claro.png) |
| / | visitante | 1366 | escuro | FALHOU | hidratação | [PNG](./capturas/verificacao/home-visitante-1366-escuro.png) |
| /catalogo | visitante | 360 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-360-claro.png) |
| /catalogo | visitante | 360 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-360-escuro.png) |
| /catalogo | visitante | 1366 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-1366-claro.png) |
| /catalogo | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/catalogo-visitante-1366-escuro.png) |
| /login | visitante | 360 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/login-visitante-360-claro.png) |
| /login | visitante | 360 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/login-visitante-360-escuro.png) |
| /login | visitante | 1366 | claro | PASSOU | nenhuma | [PNG](./capturas/verificacao/login-visitante-1366-claro.png) |
| /login | visitante | 1366 | escuro | PASSOU | nenhuma | [PNG](./capturas/verificacao/login-visitante-1366-escuro.png) |

Duração desta rodada: 287s. Limite total: 900s.

## Rodada 2026-11-24T16:27:51.968Z

| rota | perfil | largura | tema | resultado | violações | captura |
|---|---|---:|---|---|---|---|
| / | visitante | 360 | claro | FALHOU | cabeçalhos=0; filhos fora do contêiner=div.nav-wrapper.suggested-left>div.interstitial-wrapper; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/home-visitante-360-claro.png) |
| / | visitante | 360 | escuro | FALHOU | cabeçalhos=0; filhos fora do contêiner=div.nav-wrapper.suggested-left>div.interstitial-wrapper; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/home-visitante-360-escuro.png) |
| / | visitante | 1366 | claro | FALHOU | cabeçalhos=0; filhos fora do contêiner=div.footer>div; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/home-visitante-1366-claro.png) |
| / | visitante | 1366 | escuro | FALHOU | cabeçalhos=0; filhos fora do contêiner=div.footer>div; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/home-visitante-1366-escuro.png) |
| /catalogo | visitante | 360 | claro | FALHOU | redirecionado para /; cabeçalhos=0; filhos fora do contêiner=div.nav-wrapper.suggested-left>div.interstitial-wrapper; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/catalogo-visitante-360-claro.png) |
| /catalogo | visitante | 360 | escuro | FALHOU | redirecionado para /; cabeçalhos=0; filhos fora do contêiner=div.nav-wrapper.suggested-left>div.interstitial-wrapper; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/catalogo-visitante-360-escuro.png) |
| /catalogo | visitante | 1366 | claro | FALHOU | redirecionado para /; cabeçalhos=0; filhos fora do contêiner=div.footer>div; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/catalogo-visitante-1366-claro.png) |
| /catalogo | visitante | 1366 | escuro | FALHOU | redirecionado para /; cabeçalhos=0; filhos fora do contêiner=div.footer>div; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/catalogo-visitante-1366-escuro.png) |
| /login | visitante | 360 | claro | FALHOU | redirecionado para /; cabeçalhos=0; filhos fora do contêiner=div.nav-wrapper.suggested-left>div.interstitial-wrapper; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/login-visitante-360-claro.png) |
| /login | visitante | 360 | escuro | FALHOU | redirecionado para /; cabeçalhos=0; filhos fora do contêiner=div.nav-wrapper.suggested-left>div.interstitial-wrapper; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/login-visitante-360-escuro.png) |
| /login | visitante | 1366 | claro | FALHOU | redirecionado para /; cabeçalhos=0; filhos fora do contêiner=div.footer>div; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/login-visitante-1366-claro.png) |
| /login | visitante | 1366 | escuro | FALHOU | redirecionado para /; cabeçalhos=0; filhos fora do contêiner=div.footer>div; alvos menores que 44px=a,a,button.blue-button.text-button | [PNG](./capturas/verificacao/login-visitante-1366-escuro.png) |

Duração desta rodada: 177s. Limite total: 900s.
