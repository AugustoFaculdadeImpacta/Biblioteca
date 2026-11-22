# Proposal

## Why

A aplicação já tem uma base navegável e acessível, mas a página inicial, o cabeçalho, o catálogo e o rodapé ainda parecem pouco decorados e não formam uma identidade visual consistente. A mudança organiza essa apresentação com uma identidade própria da biblioteca, preservando a navegação por perfil e a acessibilidade.

## What Changes

- Definir tokens visuais próprios em creme, grafite, azul-petróleo, verde-escuro e âmbar, com contraste WCAG AA, tipografia de sistema e respeito a redução de movimento.
- Dar ao cabeçalho uma marca com slogan, menu horizontal conciso e opções condicionadas ao perfil; ampliar o rodapé sem copiar marca, textos ou imagens da referência.
- Reorganizar a página inicial com hero, chamadas para o catálogo e seções de títulos com links para o catálogo.
- Reforçar cartões de livro, capas CSS derivadas da categoria, disponibilidade, busca e filtros; só usar imagem de capa se ela já existir no contrato público aprovado.
- Aplicar o mesmo sistema visual a formulários, listas e estados de carregamento, vazio, erro e sucesso.
- Consolidar a navegação em um cabeçalho único e responsivo, com menu Perfil implementado por `rx.menu`, itens por perfil/visão e acesso a Perfil e Acessibilidade.
- Transformar `/` em vitrine sem formulários; manter login e cadastro em páginas próprias e redirecionar sessões autenticadas para a página inicial do perfil.
- Adicionar `/perfil` somente leitura usando dados já recebidos na sessão e `/acessibilidade` reaproveitando os controles existentes.
- Garantir cabeçalho e rodapé compartilhados nas rotas públicas e protegidas, sem duplicar links de navegação no corpo das páginas.
- Entregar os cinco blocos visuais em commits pequenos e independentes, cada um seguido de `reflex compile --dry`, `pytest --ignore=evaluation` e evidência de navegador.
- Não alterar endpoints, modelos de dados ou configurações do Xano; não adicionar dependências, fontes ou ícones externos.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `frontend-foundation`: detalha identidade visual, apresentação das páginas, cartões e estados, mantendo acessibilidade, navegação por perfil e responsividade.

## Impact

- Interface Reflex em `biblioteca_mais_nova/biblioteca_mais_nova.py` e testes de apresentação/navegação em `tests/`.
- Relatório final em `docs/relatorio-noite.md`, com tela, perfil, larguras de 360 px e 1366 px, distinguindo o que foi visto do que foi alterado sem inspeção visual.
- A referência foi aberta no navegador: fonte Poppins, base branca, texto grafite e acentos vermelhos/verde foram observados. Esses elementos não serão copiados; a nova identidade seguirá a paleta própria descrita acima.
- O contrato público tipado não inclui URL de capa nem data de aquisição. A interface não inventará imagens, datas, números de títulos ou a alegação “novidades”; a capa CSS usa categorias já apresentadas pelo catálogo.
- Não foram encontrados destinos oficiais de contato ou privacidade. Não serão inventados endereço, e-mail ou política; os links do rodapé só apontarão para destinos oficiais disponíveis e verificados.
- Nenhuma chamada ou escrita no Xano real faz parte desta Change.
- O escopo de navegação foi ampliado por solicitação explícita do usuário em 2026-11-18. As novas telas usam apenas dados recebidos no login/cadastro; não adicionam operações, contratos ou campos Xano.
