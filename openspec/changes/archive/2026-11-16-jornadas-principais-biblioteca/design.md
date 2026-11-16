# Design

## Context

Ver proposta em [proposal.md](./proposal.md) e contratos em [specs/primary-journeys/spec.md](./specs/primary-journeys/spec.md) e [specs/frontend-foundation/spec.md](./specs/frontend-foundation/spec.md). O app já contém telas Reflex para cadastro/login, catálogo e detalhes, área do estudante, administração do acervo e circulação. Os testes existentes cobrem essas áreas em arquivos separados e usam `httpx.MockTransport`; há também uma API demonstrativa local para verificações reproduzíveis.

As especificações `identity-session`, `catalog`, `loan-circulation` e `reservations` já definem regras de domínio, autorização, mensagens seguras e prevenção de repetição de escritas incertas. Esta Change integra essas regras, sem alterar contratos Xano ou os arquivos de tarefas de outras Changes ativas.

## Goals / Non-Goals

**Goals:**

- Exercitar os dois percursos integrados com estados controlados e resultados reproduzíveis.
- Detectar regressões entre formulário, estado Reflex, cliente HTTP e atualização da interface.
- Reutilizar o tema e componentes existentes, elevando consistência sem substituir a identidade visual estabelecida.

**Non-Goals:**

- Criar ou alterar endpoints, tabelas, campos, regras de elegibilidade ou perfis.
- Usar credenciais reais, criar contas, rodar seed ou escrever no Xano.
- Adicionar uma dependência de interface ou introduzir outro frontend.

## Decisions

- **Reutilizar os clientes e contratos atuais.** Os testes de integração simulam respostas por `httpx.MockTransport`, mantendo validação, perfis, mensagens e prevenção de duplicidade no caminho real do app. A alternativa de um backend de teste que imite toda a API aumenta manutenção e pode divergir dos clientes locais.
- **Executar no máximo a API demonstrativa local para a jornada no navegador.** Ela permite percorrer cliques e navegação sem efeitos remotos. Não substituirá as verificações de contrato com mocks, nem será apresentada como evidência de funcionamento no Xano real.
- **Manter o design existente e aprimorar consistência.** Reutilizar tema Radix, cores azul/slate, cabeçalho, padrões de formulário e estilos de estado do Reflex; não introduzir paleta/brand diferente ou biblioteca nova. Validar foco de teclado, contraste e larguras já adotadas no projeto.
- **Tratar falhas em camadas.** Testes de cliente cobrem classes de status e transporte; testes de estado verificam mensagens, ausência de falso sucesso, isolamento de sessão e bloqueio de repetição; Playwright verifica a apresentação e navegação das jornadas.
- **Executar o navegador somente após a inicialização local ser confiável.** A verificação completa depende de frontend e backend Reflex ativos e conectados. Recomenda-se aplicar primeiro `execucao-reflex-windows`; não usar uma página servida isoladamente como substituto da sessão Reflex.

## Risks / Trade-offs

- [Mocks podem divergir do contrato remoto] → manter testes ancorados nas especificações e registrar que não são validação do Xano.
- [A API demonstrativa pode não cobrir determinada ação] → limitar seu uso a cenários existentes; verificar contratos adicionais com transporte mockado, sem simular que houve escrita real.
- [Polimento visual pode alterar espaços e quebras responsivas] → comparar telas em 360px e 1366px, preservar foco visível e validar navegação por teclado.
- [O runtime local pode continuar bloqueando a validação Playwright] → depender da Change do runtime; não contornar políticas do Windows nem deixar processos não identificados.

## Migration Plan

1. Conferir os testes e componentes atuais e mapear lacunas nos percursos já especificados.
2. Adicionar testes de jornada e de erros com respostas simuladas antes de alterar o comportamento da interface.
3. Ajustar somente as telas/estados que falharem nos contratos e harmonizar o estilo reutilizando os componentes existentes.
4. Executar testes focados e a suíte local; depois de o runtime estar aprovado, validar navegação e responsividade com Playwright usando somente a API demonstrativa.
5. Inspecionar diff e logs. Não há migração de dados nem rollback remoto; reverter somente as alterações desta Change caso as verificações falhem.
