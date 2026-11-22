# Proposal

## Why

Os formulários, ações administrativas e controles de aparência ainda têm inconsistências visuais e de acessibilidade, enquanto o Acervo e as respostas de reserva não comunicam com precisão o estado confirmado pelo servidor. Esta Change reúne os ajustes de interface e as verificações de contrato já solicitadas, sem ampliar o modelo de dados.

## What Changes

- Substituir controles de formulário do Radix por elementos HTML nativos com estilos compartilhados, foco visível, autofill compatível com o tema e campos ocultos realmente ocultos.
- Garantir contraste WCAG AA em variantes de botões e no texto de capas SVG geradas, independentemente do tema.
- Separar os menus de Perfil e Acessibilidade, mantendo as preferências globais e a visão administrativa restrita ao admin real.
- Criar um dicionário documentado de ações e selos com emoji exclusivo por ação, texto curto e semântica acessível, aplicado de forma consistente.
- Apresentar o Acervo em linhas verticais responsivas, com busca normalizada, expansão independente de edição e exemplares, paginação e filtro explícito de desativados.
- Confirmar a desativação pelo estado recarregado do servidor e apresentar erro explícito quando a resposta indicar sucesso mas o título permanecer ativo.
- Mapear erros de reserva por status HTTP e timeout, com mensagens seguras e códigos curtos.
- Conferir o seed existente, preservando dry-run como padrão e registrando claramente se o plano é local ou remoto.

## Capabilities

### New Capabilities

Nenhuma. Os comportamentos pertencem às capacidades existentes.

### Modified Capabilities

- `frontend-foundation`: controles nativos, contraste e estados de botões, separação dos menus, dicionário visual acessível e responsividade.
- `catalog`: layout e filtros do Acervo, confirmação da desativação pelo estado do servidor, contraste das capas e saída segura do seed.
- `reservations`: mensagens claras para falhas de solicitação de reserva.

## Impact

- Frontend Reflex em `biblioteca_mais_nova/biblioteca_mais_nova.py` e geração SVG em `biblioteca_mais_nova/covers.py`.
- Novo módulo de ícones em `biblioteca_mais_nova/icons.py` e guia em `docs/guia-de-icones.md`.
- Tratamento de respostas em `biblioteca_mais_nova/catalog.py` e clientes relacionados; auditoria do seed em `scripts/seed_catalogo_real.py` e sua documentação/testes.
- Testes pytest existentes e novos focalizados nos contratos alterados; registro de evidências em `docs/relatorio-noite.md`.
- A inspeção do Xano será somente de leitura e apenas durante Apply: confirmar destino antes de qualquer pull de definições para diretório temporário fora do repositório. Esta Change não autoriza publicar, sincronizar nem gravar dados no Xano.
