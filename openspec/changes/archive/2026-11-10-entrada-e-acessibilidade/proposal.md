# Proposal

## Why

A aplicação ainda apresenta conceitos de página inicial que conflitam com a
entrada direta pelo login, e o cabeçalho não identifica a pessoa autenticada
nem oferece preferências de acessibilidade persistentes. Esta Change unifica a
entrada, preserva o catálogo público e torna ajustes básicos de leitura e
movimento disponíveis em todas as telas Reflex.

## What Changes

- Fazer `/` apresentar o login para visitantes e direcionar sessões
  autenticadas ao catálogo; remover a navegação de “Início” como destino
  separado.
- Oferecer no login um link explícito ao catálogo público.
- Exibir no cabeçalho o nome retornado na sessão para contas autenticadas e
  “Entrar” para visitantes, sem expor e-mail, senha ou token.
- Adicionar controles globais de acessibilidade para escala tipográfica entre
  100% e 150%, alto contraste e redução de animações, com preferências
  persistidas no navegador e operáveis por teclado.
- Preservar foco visível e validar legibilidade com contraste mínimo de 4.5:1
  e ausência de rolagem horizontal em 360px e 1366px.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `frontend-foundation`: alterar o comportamento da rota raiz e do cabeçalho e
  acrescentar preferências globais persistentes de acessibilidade.

## Impact

- Frontend Reflex: estado da sessão, entrada, cabeçalho compartilhado e estilos
  globais.
- Testes pytest da navegação, identidade exibida e limites/alternâncias dos
  controles de acessibilidade.
- Verificação manual automatizada com Playwright em `reflex run` padrão, nos
  viewports de 360px e 1366px.
- Nenhuma alteração de API, schema ou operação no Xano.
