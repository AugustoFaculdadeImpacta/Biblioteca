# Publicação Xano pendente

Este arquivo registra trabalho local que poderá exigir publicação ou execução
futura no Xano real. **Nada foi publicado, executado, excluído ou alterado
remotamente nesta sessão.**

## Gate obrigatório antes de qualquer operação

Identificar e confirmar, com o responsável pelo ambiente, o workspace, a branch,
o ambiente e o grupo de API da biblioteca escolar. Não assumir que um destino
registrado anteriormente continua correto. Se houver mais de um destino
plausível, não operar. Antes de qualquer sincronização futura, revisar backup,
permissões e diff unitário. Este documento não autoriza operações remotas.

## Ordem pendente

1. **Confirmar o destino e a autorização operacional.** Workspace, branch,
   ambiente e grupo devem ser identificados e confirmados antes de qualquer
   operação remota.
2. **Conferir schema e autenticação locais pendentes.** Revisar, em conjunto,
   `xano/table/usuario.xs`, `xano/table/titulo.xs` e
   `xano/api/default/auth/login_POST.xs`, incluindo enum de perfil, estado ativo
   e compatibilidade de login.
3. **Conferir autorização administrativa.** Revisar os guards e candidatos
   locais de gestão de usuários indicados em
   `docs/publicacao-xano.md`; validar cada rota no destino confirmado antes de
   considerar a permissão operacional.
4. **Conferir e publicar, se aprovado, os contratos locais do acervo.** Inclui
   o estado ativo do título, listagem administrativa, atualização e bloqueios
   de exclusão/desativação. A lista exata de arquivos será atualizada depois
   das Changes locais.
5. **Conferir fluxos de reserva e circulação alterados localmente.** Validar
   fila, disponibilidade, retirada, devolução e autorização antes de qualquer
   publicação.
6. **Preparar e revisar o seed Xano sem executá-lo.** O script deve ser
   idempotente e obter senhas somente de variáveis de ambiente em tempo de
   execução; nenhuma senha ou URL poderá ser gravada no repositório.
7. **Executar testes remotos somente após autorização e destino confirmado.**
   Inclui testes de autorização, concorrência/FIFO e limpeza individual de
   registros sintéticos `@example.invalid`, sem exclusão global.

## Rotas pessoais

Segundo as evidências fornecidas pelo usuário, `/minhas/emprestimos`,
`/minhas/solicitacoes` e `/minhas/reservas` já estão publicadas. Elas responderam
401 sem token, comportamento esperado de rotas autenticadas. Não há publicação
pendente dessas rotas identificada neste diagnóstico; o erro observado após
login requer tratamento local da sessão e verificação posterior autorizada.

P1 alterou somente o cliente Reflex, parsers e mensagens locais; não adicionou
nem modificou contratos Xano e não requer publicação.

## Estado da verificação

- Validação local de sintaxe MCP: três rotas pessoais válidas.
- Workspace, branch e tabelas ativos: não consultados; as ferramentas MCP
  disponíveis não expõem listagem de metadados do workspace e o Xano CLI está
  fora dos limites desta execução.
- Publicação, seed e testes autenticados no Xano real: pendentes e não
  executados.
