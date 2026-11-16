# Proposal

## Why

Cadastro, login, catálogo, empréstimos, reservas e administração do acervo já têm contratos e testes isolados, mas o usuário precisa conseguir percorrer os fluxos prioritários de ponta a ponta sem perder contexto ou receber sucesso enganoso. Esta Change integra essas jornadas com feedback de erro seguro e uma apresentação visual mais consistente, sem alterar regras do domínio nem depender de dados reais.

## What Changes

- Verificar e ajustar a jornada de estudante desde cadastro/login até catálogo, solicitação ou reserva e consulta do resultado.
- Verificar e ajustar a jornada de bibliotecário desde login até cadastro de título, categoria e exemplar, além das ações de circulação existentes.
- Garantir feedback claro e seguro para validação, sessão expirada, permissão insuficiente, conflito, falha de servidor/rede e resposta inesperada, sem expor detalhes privados ou indicar escrita incerta como concluída.
- Harmonizar hierarquia visual e componentes das telas principais, preservando português, navegação por teclado, foco visível, contraste e responsividade.
- Usar transporte/API simulados e testes locais de navegador; não criar contas, não executar seed e não fazer escritas no Xano real nesta Change.

## Capabilities

### New Capabilities

- `primary-journeys`: define as jornadas integradas de estudante e bibliotecário pelas capacidades já existentes, com estados de sucesso e falha observáveis.

### Modified Capabilities

- `frontend-foundation`: acrescentar um requisito de consistência visual nas telas principais, preservando os requisitos de acessibilidade e navegação existentes.

## Impact

- Áreas prováveis: telas Reflex em `biblioteca_mais_nova/`, testes de login, cadastro, catálogo, circulação e navegação, e documentação diretamente relacionada.
- Verificação: testes Python com transporte simulado e uma execução local controlada no navegador; nenhum token ou credencial real será usado.
- Fora do escopo: mudança de modelo/endpoints/regra do Xano, publicação, seed, criação ou remoção de contas, deploy e alteração da arquitetura Reflex/Xano.
