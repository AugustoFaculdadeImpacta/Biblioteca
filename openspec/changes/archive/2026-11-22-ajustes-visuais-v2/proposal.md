# Proposal

## Why

Campos estão visualmente duplicados e o tema escuro não acompanha a pessoa entre páginas. O Perfil do visitante não oferece os controles de acessibilidade disponíveis a quem já entrou, e a home mantém ações que o usuário quer remover do hero.

## What Changes

- Unificar a borda dos campos no contêiner Reflex, preservando foco visível, altura mínima e controles nativos acessíveis.
- Compartilhar controles de aparência entre visitantes e pessoas autenticadas; persistir apenas tema, escala de fonte, alto contraste e redução de movimento no navegador.
- Completar tokens escuros e testes de contraste para os componentes principais.
- Simplificar o hero da home, remover sua busca e atalhos, e evitar repetir “Sobre a biblioteca” no rodapé.
- Revisar as telas de bibliotecário e admin para estados, ações, feedback, alvos e tabelas responsivas sem alterar contratos de serviço.

## Capabilities

### New Capabilities

### Modified Capabilities

- `frontend-foundation`: estilos e foco de campos, controles de aparência para visitantes, persistência local das preferências, tema escuro legível, composição da home e consistência/responsividade das telas operacionais.

## Impact

- Frontend Reflex em `biblioteca_mais_nova/biblioteca_mais_nova.py` e testes de `tests/`, incluindo testes de estilos/tokens e fluxos de navegação e operação.
- Nenhuma alteração de endpoints, dados, dependências ou escrita no Xano. A persistência será limitada a quatro preferências não pessoais no navegador.
