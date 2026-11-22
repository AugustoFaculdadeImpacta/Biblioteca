# Design

## Context

Ver `proposal.md` e `specs/frontend-foundation/spec.md`. A interface está concentrada em `biblioteca_mais_nova/biblioteca_mais_nova.py`, com `app.style`, `site_header`, `index` e `public_catalog`. O catálogo público fornece títulos, autoria, categorias e disponibilidade; não fornece imagem de capa nem data de aquisição. Cabeçalho e controles de acessibilidade são compartilhados entre as páginas.

## Goals / Non-Goals

**Goals:**

- Aplicar a identidade visual em cinco blocos pequenos, preservando navegação e regras dos perfis.
- Padronizar o cabeçalho em todas as rotas com navegação principal central, menu `rx.menu` Perfil e navegação móvel recolhível.
- Separar a vitrine pública das telas de autenticação e oferecer páginas próprias de perfil e acessibilidade, usando somente estado de sessão já disponível.
- Manter uso offline e suporte a teclado, leitor de tela, ampliação de fonte, alto contraste e movimento reduzido.
- Registrar evidências por bloco: nomes de testes, hash do commit e métricas DOM em 360 px e 1366 px; declarar explicitamente quando a aparência não tiver sido inspecionada.

**Non-Goals:**

- Alterar API, contrato de dados, Xano, autenticação ou regras de negócio.
- Inventar capas, datas de aquisição, métricas do acervo, endereços de contato ou conteúdo jurídico.
- Baixar fontes, ícones ou imagens, adicionar dependências ou modificar arquivos gerados.

## Decisions

1. **Tema local em `app.style`.** Definir tokens CSS para creme, grafite, azul-petróleo, verde-escuro, âmbar, estados e sombras; usar Georgia/serif em títulos e system-ui/Segoe UI no corpo. Validar as combinações de texto por cálculo WCAG AA em testes. Alternativa descartada: importar fontes ou imagens externas, pois a interface deve funcionar offline e manter identidade própria.
2. **Estrutura compartilhada.** Estender `site_header` e o rodapé usado pelas páginas, preservando os guards e links existentes por perfil. Adicionar slogan e poucas opções de navegação sem transformar a preferência visual do admin em autorização. Não criar links quebrados: contato e privacidade aguardam destinos oficiais; não há conteúdo aprovado para esses destinos no projeto.
3. **Página inicial com dados verdadeiros.** A página pública pode usar os métodos atuais do catálogo para exibir uma seleção de títulos, com estados de carregamento, vazio e erro. Sessões autenticadas também podem abrir `/` e recebem atalhos do perfil/visão ativa; somente `/login` e `/cadastro` redirecionam sessões existentes à página inicial do perfil. Não apresentar “novidades” sem data confiável nem repetir contagens estáticas como se fossem dados vivos.
4. **Capa determinística sem contrato novo.** Construir a capa com CSS, usando a categoria conhecida para cor e inicial, e o título como fallback quando a categoria faltar. A tipagem/validação atual não reconhece URL de imagem; portanto esta Change não amplia o contrato nem tenta exibir campos extras. Alternativa descartada: consumir imagens arbitrárias do backend ou de terceiros.
5. **Alterar em cinco blocos com prova independente.** (1) tokens; (2) cabeçalho/rodapé; (3) página inicial; (4) cartões/catálogo; (5) formulários/painéis/estados e relatório final. Cada bloco recebe testes focados, `reflex compile --dry`, `pytest --ignore=evaluation`, verificação a 360 px e 1366 px e um commit em português. Só marcar tarefa como concluída após registrar hash, testes e caminho de captura ou métricas DOM com declaração de inspeção visual.
6. **Acessibilidade como critério de aceite.** Manter `:focus-visible`, navegação por teclado, controles de fonte e alto contraste; manter movimento reduzido e contraste AA; medir alvos acionáveis com no mínimo 44 px em 360 px e ausência de rolagem horizontal. Os testes devem cobrir valores e o navegador deve confirmar métricas do DOM nas larguras pedidas. Se não houver inspeção visual, o relatório declarará “não visto”.
7. **Menu e rotas de navegação.** Usar o componente `rx.menu` para Perfil, por delegar ao primitivo Radix a navegação por teclado, fechamento por Escape e restauração de foco. A navegação central representa o perfil efetivo da sessão ou a visão escolhida pelo admin; a faixa de visão do admin e o retorno à visão admin permanecem fora do menu. Em largura móvel, um botão com `aria-expanded` expõe os mesmos links e o menu Perfil. Redirecionamentos de páginas de autenticação são eventos Reflex e os guards existentes continuam responsáveis pelas páginas protegidas.
8. **Dados de perfil sem nova operação remota.** Guardar e-mail retornado pelo fluxo de autenticação em estado privado de sessão, junto ao nome/papel já mantidos. Exibir os dados somente em `/perfil`; não criar edição, troca de senha ou leitura adicional no backend.

## Risks / Trade-offs

- [O carregamento extra da página inicial pode expor indisponibilidade do catálogo] → Mostrar estados explícitos e preservar a página de entrada; usar exclusivamente os serviços públicos existentes.
- [Algumas páginas têm perfis diferentes e estados Reflex dinâmicos] → Validar DOM com mocks e cenários por perfil, além das medidas em ambos os viewports.
- [Ausência de destinos de contato/privacidade] → Não publicar links sem destino oficial; registrar essa limitação no relatório para resolução posterior.
- [O backend não oferece capas nem data de aquisição] → Usar capa CSS e títulos de seção neutros; não inventar valores nem ampliar o escopo para Xano.

## Migration Plan

Sem migração de dados ou publicação remota. Implementar os cinco blocos em commits separados na branch `trabalho-autopilot`; após cada bloco executar compilação e testes completos, coletar evidência DOM nas duas larguras e registrar o commit. Atualizar `docs/relatorio-noite.md` com telas, perfis, medidas e limites observados. Reverter somente os commits próprios do bloco se uma verificação falhar; nunca descartar alterações preexistentes.
