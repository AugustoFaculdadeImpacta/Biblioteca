# Proposal

## Why

As telas de autenticação têm campos com contraste inadequado e não oferecem uma navegação coerente entre as áreas da biblioteca. Também é difícil entender e continuar os fluxos de entrada e cadastro, e a página inicial não orienta visitantes nem usuários autenticados.

## What Changes

- Definir uma apresentação visual consistente para modo claro e escuro, com cores de texto e fundo explícitas em todos os campos, formulários em cartões responsivos, estados de erro/sucesso destacados e contraste WCAG AA.
- Introduzir um cabeçalho compartilhado e navegação adequada ao perfil: visitantes acessam início, login e cadastro; estudantes acessam início e podem sair; bibliotecários acessam início, cadastro de livro e podem sair.
- Incluir links cruzados entre login e cadastro e tornar a página inicial útil para orientar visitantes e usuários.
- Corrigir as transições: login encaminha estudantes ao início e bibliotecários ao acervo; cadastro concluído inicia acesso estudantil imediato, redireciona ao início e apresenta uma mensagem de sucesso.
- Preservar foco visível, navegação por teclado, labels, privacidade de sessão e bloqueio administrativo existente.
- Adicionar testes com respostas Xano mockadas e verificar visualmente as rotas em 360px e 1366px, em modos claro e escuro, sem chamadas de escrita ao Xano live.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `frontend-foundation`: especificar navegação compartilhada e links disponíveis de acordo com o estado autenticado e perfil.
- `identity-session`: especificar destinos após login/cadastro e a confirmação de cadastro após o redirecionamento, sem alterar o contrato de identidade ou sessão.

## Impact

- Frontend Reflex: componentes comuns de cabeçalho e formulário, tema e estilos globais, estado de sessão e handlers de navegação na página inicial, login, cadastro e área administrativa.
- Specs `frontend-foundation` e `identity-session`, testes automatizados com mocks e validação visual local via navegador.
- Nenhuma alteração a endpoints, modelos de dados ou arquivos Xano; nenhuma escrita remota.
