# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas para [catalog](./specs/catalog/spec.md) e [frontend-foundation](./specs/frontend-foundation/spec.md). O app Reflex já tem cabeçalho comum, cliente HTTP Xano no backend e consulta pública de categorias; ainda não há telas ou serviço frontend para listar e detalhar títulos.

## Goals / Non-Goals

**Goals:**
- Reutilizar o estado e os estilos Reflex existentes, mantendo filtros e ordenação no backend de estado Reflex e sem transmitir token.
- Buscar o catálogo e categorias por GETs públicos já existentes.
- Oferecer rotas públicas para a lista e o detalhe, com estados acessíveis de carregamento, erro e ausência de resultados.

**Non-Goals:**
- Alterar arquivos, dados, endpoints ou configurações do Xano; criar escritas ou chamadas ao ambiente live.
- Incluir fluxos de empréstimo, reserva, manutenção do acervo ou suporte ao perfil admin, pertencentes a blocos posteriores.
- Instalar dependências ou introduzir tecnologia adicional de frontend.

## Decisions

### Contratos públicos existentes verificados em leitura local

- `xano/api/default/catalogo/titulos_GET.xs`: `GET /catalogo/titulos` retorna uma lista de objetos `{titulo, categorias, exemplares_disponiveis}`. `titulo` vem da tabela `titulo` (`id`, `titulo`, `autores`, `isbn`, `editora`, `edicao`, `ano_publicacao`, `descricao`); `categorias` contém associações `titulo_categoria` (`id`, `titulo_id`, `categoria_id`); a contagem é um inteiro calculado por exemplares cujo `estado` seja `"disponivel"`.
- `xano/api/default/catalogo/titulos_id_GET.xs`: `GET /catalogo/titulos/{titulo_id}` retorna o mesmo envelope; ID ausente produz 404.
- `xano/api/default/catalogo/categorias_GET.xs`: `GET /catalogo/categorias` retorna categorias (`id`, `nome`).
- `xano/api/default/catalogo/categorias_titulos_GET.xs` retorna títulos e não é necessário para montar os filtros, porque a lista já inclui as associações no envelope.
- As tabelas `titulo.xs`, `titulo_categoria.xs`, `exemplar.xs` e `categoria.xs` confirmam os campos acima. A tabela `titulo` não contém `ativo`; o GET de lista não filtra títulos inativos. A remoção lógica/campo `ativo` será tratada no bloco posterior B2, sem antecipar ou simular esse campo em A1.

Os nomes de categoria serão obtidos juntando, em memória, os IDs das associações aos registros de `GET /catalogo/categorias`. A disponibilidade será exibida usando exatamente o contador já retornado, sem inferir devoluções ou recalcular estados físicos. Implementar somente clientes GET e validar estritamente o envelope antes de colocar dados no estado Reflex.

**Alternativas consideradas:** obter títulos por chamadas separadas para cada categoria ou inferir disponibilidade no cliente a partir dos exemplares. Foram rejeitadas porque a lista já entrega associações e contagem agregada, e não há endpoint público de exemplares necessário à consulta.

### Estado e filtros da consulta

Carregar títulos e categorias ao entrar na lista pública. Manter no estado Reflex somente os dados públicos retornados pelos GETs e os critérios de busca, categoria, disponibilidade e direção da ordenação. Calcular em memória a lista visível; normalizar o texto por `casefold` e remoção de diacríticos, e ordenar pelo título usando essa mesma chave determinística, para que letras acentuadas sejam comparadas junto à letra-base sem depender da locale do servidor. O detalhe usa o ID inteiro da rota dinâmica `/catalogo/[titulo_id]` e consulta o GET de detalhe existente.

**Alternativas consideradas:** enviar cada critério ao Xano ou manter filtros duplicados no navegador. Ambas adicionariam contrato/comunicação sem necessidade, pois a lista pública já é carregada no estado do backend Reflex e a ordenação é deliberadamente local.

### Navegação e acessibilidade

Adicionar Catálogo ao cabeçalho comum para visitante, estudante e bibliotecário. Manter visível o acesso administrativo atual somente para bibliotecário; não antecipar o reconhecimento do perfil admin, que será implementado em B1. Utilizar controles nativos com labels, foco `:focus-visible` existente e os tokens de tema. Cards e resultado de detalhe devem caber no layout responsivo já aplicado.

**Alternativas consideradas:** duplicar links em cada tela ou alterar a autorização por perfil neste bloco; foram descartadas para preservar o cabeçalho compartilhado e a separação de fases.

### Rota de detalhe

Usar uma rota de detalhe identificada pelo ID retornado pelo catálogo, sem colocar credenciais ou dados sensíveis na URL. Confirmar a forma de rota dinâmica compatível com a versão Reflex instalada durante o Apply. Um identificador inválido ou título ausente produz mensagem de não encontrado e link de retorno à listagem.

**Alternativas consideradas:** guardar título selecionado somente em estado global, que não suporta abrir/compartilhar/recarregar diretamente o detalhe.

### Limite dos contratos existentes quanto a inativação

Como a tabela não possui `ativo` e o GET público atual lista todos os registros, A1 não tentará esconder títulos por uma condição inexistente. Até B2 implementar e validar a remoção lógica e o backend público passar a filtrar títulos inativos, o comportamento da lista permanece exatamente o do endpoint atual.

**Alternativas consideradas:** ignorar esse limite ou inferir inativação de outros campos; ambas poderiam ocultar ou revelar registros incorretamente.

## Risks / Trade-offs

- [A lista pública atual inclui todos os títulos e não tem filtro de ativo] → manter o comportamento existente nesta Change e endereçar a remoção lógica no bloco B2, sem modificar Xano agora.
- [A lista pode ficar desatualizada após uma alteração administrativa] → carregar novamente ao visitar a rota; não manter cache permanente nesta etapa.
- [Resposta pública malformada pode quebrar filtros] → validar estrutura e tipos no cliente de serviço, exibir erro seguro em português e cobrir resposta inválida com mocks.
- [Dados de catálogo são públicos, mas a sessão Reflex é privada] → não incluir token/perfil na resposta pública, no estado serializado ou nos logs.

## Migration Plan

Não há migração, push ou operação remota. Implementar cliente de leitura, estado e rotas Reflex; validar com pytest e navegador usando API mockada. Se os GETs existentes forem insuficientes, parar sem modificar Xano ou relaxar os requisitos. Arquivar apenas depois de todos os critérios locais e do OpenSpec passarem.

## Open Questions

- Nenhuma decisão funcional está pendente. A disponibilidade exata de campos nos GETs e a sintaxe de rota Reflex são verificações técnicas obrigatórias antes da implementação, não autorização para criar contratos novos.
