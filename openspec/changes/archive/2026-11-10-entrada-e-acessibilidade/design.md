# Design

## Context

Ver [proposal.md](./proposal.md) e o contrato de comportamento em
[specs/frontend-foundation/spec.md](./specs/frontend-foundation/spec.md).
O cabeçalho é compartilhado por páginas Reflex, a raiz agora renderiza o login
e `LoginSession.usuario.nome` já é validado pelo cliente de login. O estado
privado da sessão atualmente mantém token e perfil; não há dependência de
frontend fora do Reflex.

## Goals / Non-Goals

**Goals:**

- Reutilizar o cabeçalho e o estado Reflex para manter identidade e preferências
  consistentes em todas as rotas.
- Limitar os controles de fonte no próprio estado de aplicação e persistir
  preferências locais sem enviar dados pessoais ao backend.
- Tornar auditáveis contraste, teclado, responsividade e persistência por
  testes e Playwright.

**Non-Goals:**

- Alterar contratos, schemas, credenciais, endpoints ou dados no Xano.
- Persistir a sessão de autenticação ou o nome do usuário no armazenamento do
  navegador; somente preferências de acessibilidade são persistidas.
- Alterar regras de autorização ou criar uma página inicial independente.

## Decisions

1. **Raiz como entrada, sem destino “Início”.** Renderizar o mesmo formulário de
   login em `/` e `/login`, sem link de navegação separado para “Início”.
   Manter o redirecionamento de sessão autenticada de `/` para `/catalogo`.
   O catálogo continua disponível publicamente, com link direto no formulário
   de login. Essa abordagem evita duplicar a tela e não muda a rota pública do
   catálogo.

2. **Identidade de sessão mínima e privada.** Armazenar `usuario.nome` retornado
   pelo login em estado privado Reflex junto dos dados de sessão e expor ao
   cabeçalho somente uma saudação renderizada. Para visitantes, renderizar
   “Entrar”; não usar e-mail como fallback. Limpar o nome junto com a sessão ao
   sair. O nome não deve ser gravado em `LocalStorage`, variáveis públicas ou
   logs.

3. **Preferências de acessibilidade somente no cliente.** Usar o mecanismo
   persistente de armazenamento local suportado pelo Reflex para escala de
   fonte, alto contraste e redução de animações. Valores ausentes ou inválidos
   inicializam com fonte em 100% e modos desligados. Limitar a fonte a passos
   definidos entre 100% e 150%; “Restaurar fonte” seleciona 100%. Não persistir
   estado de autenticação nesse mecanismo.

4. **Aplicação global por atributos/classes no documento.** Aplicar escala por
   variável CSS raiz e os modos por classes ou atributos globais; o cabeçalho
   deve permanecer utilizável em telas estreitas com quebra de linha. Alto
   contraste deve usar cores verificadas para texto e controles que atendam
   razão mínima 4.5:1. Redução de animações deve eliminar/reduzir transições e
   animações da aplicação. Os controles terão rótulos explícitos em português,
   estado acessível ligado/desligado e manterão `:focus-visible`.

5. **Verificação em camadas.** Testes pytest cobrem raiz, navegação, nome
   privado, limites 100/150 e alternâncias. Playwright contra o `reflex run`
   padrão verifica persistência, operação por teclado, contraste calculado,
   links e ausência de overflow em 360px e 1366px. A autenticação real só pode
   ser verificada com credenciais autorizadas e permanece independente dos
   testes locais.

## Risks / Trade-offs

- [O armazenamento local pode hidratar depois do primeiro render] → fornecer
  valores padrão seguros e validar restauração sem piscar ou deixar controles
  em estado divergente.
- [A saudação pode expor informação pessoal em telas compartilhadas] → exibir
  somente o nome já retornado para a sessão autenticada e removê-lo ao sair;
  nunca persistir localmente nem registrar em log.
- [As preferências visuais podem não alcançar componentes de terceiros] →
  auditar os componentes renderizados e medir contraste e overflow em Playwright
  nos dois viewports solicitados.
