# Spec Delta

## MODIFIED Requirements

### Requirement: Rodapé comum não duplica a navegação principal
Todas as rotas MUST apresentar um rodapé curto compartilhado, identificado como “Biblioteca escolar” e contendo somente links já disponíveis. “Sobre a biblioteca” MUST ser uma seção de conteúdo da home, não um rótulo que substitui a identificação do rodapé.

#### Scenario: Rodapé compartilhado
- **WHEN** pessoa abre qualquer rota da aplicação
- **THEN** encontra um único rodapé com “Biblioteca escolar” e destinos existentes

#### Scenario: Seção Sobre na home
- **WHEN** pessoa percorre a home
- **THEN** encontra a seção “Sobre a biblioteca” separada do rodapé

#### Scenario: Navegação do corpo da página
- **WHEN** pessoa percorre o conteúdo de qualquer rota
- **THEN** não encontra cópias de links de navegação global que já estão no cabeçalho

### Requirement: Identificadores usam emojis decorativos
Marca, navegação, ações principais e selos MUST usar o símbolo previsto no guia, com texto curto visível. O emoji decorativo MUST ficar em elemento próprio com `aria-hidden="true"`; cada botão MUST fornecer `title` e `aria-label` descritivos. Fora desses usos, a home MUST usar `📚` somente no título “Livros em destaque”.

#### Scenario: Emoji decorativo em rótulo
- **WHEN** interface apresenta marca, destino, ação principal, selo ou o título de destaque
- **THEN** o emoji fica em elemento próprio com `aria-hidden="true"` antes do texto correspondente

#### Scenario: Ação com texto acessível
- **WHEN** pessoa encontra um botão de ação principal
- **THEN** encontra um emoji e um texto de uma a três palavras, com `title` e `aria-label` correspondentes

#### Scenario: Emoji não é espalhado pelo conteúdo
- **WHEN** pessoa percorre textos, metadados, títulos de seção ou descrições que não sejam o título de destaque
- **THEN** esses conteúdos não recebem emojis decorativos adicionais

#### Scenario: Confirmação destrutiva inline
- **WHEN** pessoa confirma ou cancela uma ação destrutiva
- **THEN** os controles oferecem “✅ Sim, desativar” e “❌ Não”

## ADDED Requirements

### Requirement: A interface recupera a hierarquia visual do modelo
A aplicação MUST usar a paleta, tipografia e hierarquia de cartões do modelo visual restaurado nos dois temas, sem remover conteúdo ou fluxos acrescentados depois dele.

#### Scenario: Tema escuro e identidade visual
- **WHEN** pessoa navega com o tema escuro ativo
- **THEN** a interface usa painéis azul-marinho, bordas finas, cantos arredondados e títulos serifados; ciano fica restrito a ações principais, números de estatística e links

#### Scenario: Cabeçalho e busca global
- **WHEN** pessoa abre qualquer página
- **THEN** encontra marca serifada, Catálogo, busca global compacta e neutra e controles de Perfil e Acessibilidade com contorno, mantendo a busca direcionada a `/catalogo`

#### Scenario: Home preserva conteúdo e hierarquia
- **WHEN** pessoa percorre a home
- **THEN** encontra o hero sem busca ou botões, as estatísticas reais, “📚 Livros em destaque”, as seções existentes de novidades, categorias e reserva, o resumo de perfil aplicável e “Sobre a biblioteca”

#### Scenario: Cartões de livros permanecem compactos
- **WHEN** a home exibe poucos ou muitos livros
- **THEN** os cartões mantêm largura contida, capa vertical e espaçamento consistente sem esticar para preencher uma seção vazia

### Requirement: Faixa da visão do admin fica abaixo do cabeçalho
Quando admin real usa uma visão diferente de Administrador, a aplicação MUST mostrar o estado da visão em uma faixa própria abaixo do cabeçalho, sem aumentar a altura do cabeçalho.

#### Scenario: Admin usa visão simulada
- **WHEN** admin seleciona a visão Estudante ou Bibliotecário
- **THEN** uma faixa de largura total, com altura mínima de `2.25rem`, mostra “Modo de visualização” em uma linha e “Voltar à visão de admin”

#### Scenario: Admin retorna à visão Administrador
- **WHEN** admin está na visão Administrador
- **THEN** a faixa de visão simulada não é exibida

### Requirement: Painel de Acessibilidade organiza controles em linhas
O painel de Acessibilidade MUST apresentar uma linha por opção, com rótulo à esquerda e controle à direita, sem sobreposição ou conteúdo fora do painel.

#### Scenario: Controles de aparência em viewport estreita
- **WHEN** pessoa abre Acessibilidade em viewport de 360 px
- **THEN** o painel cabe em `min(20rem, 92vw)`, usa coluna, espaçamento de `0.5rem` e preenchimento de `0.75rem`, sem rolagem horizontal

#### Scenario: Escala da fonte
- **WHEN** pessoa ajusta a escala da fonte no painel
- **THEN** A−, 100% e A+ são controles separados com alvos de pelo menos 44 px

#### Scenario: Preferências booleanas
- **WHEN** pessoa consulta alto contraste, redução de movimento ou tema
- **THEN** cada opção aparece em uma linha e anuncia “Ligado” ou “Desligado” conforme o estado efetivo
