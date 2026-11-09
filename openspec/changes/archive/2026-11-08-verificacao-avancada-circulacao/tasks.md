# Tasks

## 1. Review, pré-condições e fixtures rastreáveis

- [x] 1.1 No Review, obter confirmação do usuário de que ele fez backup/export e aprovação explícita para Apply; não inferir aprovação pelo silêncio.
- [x] 1.2 Confirmar por GET na Metadata API que `v1` é live, resolver IDs das cinco tabelas pelo GET de tabelas e ler todas as páginas de registros de `reserva`, `emprestimo`, `solicitacao_emprestimo`, `usuario` e `exemplar`; registrar somente totais agregados e os três estados críticos.
- [x] 1.3 Aprovar o gate somente se não houver reserva ofertada vencida, empréstimo ativo ou solicitação pendente e se a leitura das cinco tabelas estiver completa; caso contrário, registrar apenas contagens agregadas e parar sem fixtures ou processamento global.
- [x] 1.4 Criar um bibliotecário e estudantes sintéticos via Metadata API autorizada; registrar tabela/ID imediatamente, validar login sem expor credenciais e confirmar limpeza individual em ordem de dependência com GET 404. Nunca tocar nos dois usuários existentes.

## 2. Verificar regras temporais e de capacidade

- [x] 2.1 Executar o cenário de atraso, ajustar somente `vence_em` da fixture e registrar o resultado da solicitação e da reserva (passou ou achado), além da limpeza individual.
- [x] 2.2 Executar duas retiradas concorrentes para um estudante e registrar quantas foram aceitas (passou ou achado), além da limpeza individual.
- [x] 2.3 Executar a consulta FIFO e a oferta da próxima reserva, registrando resultado e limpeza. Tentar expiração/reoferta somente se a oferta vencida da fixture for confirmável; caso contrário, interromper pelo pré-check e registrar a etapa como não avaliada, sem chamar o processador global.

## 3. Verificar concorrência e registrar evidências

- [x] 3.1 Disputar em paralelo o último exemplar e a geração do código de tombo; registrar as respostas e verificar invariantes e ausência de colisão.
- [x] 3.2 Registrar comandos, respostas sanitizadas, IDs/tabelas, resultado dos pré-checks e limpeza em `RESULTS.md`; verificar ausência de segredos e dados pessoais, e confirmar contagens finais `reserva=0`, `emprestimo=0`, `solicitacao_emprestimo=0`, `exemplar=0`, `usuario=2`.

> Verificação concluída com achados de backend: solicitação com empréstimo vencido aceita (HTTP 200); duas retiradas concorrentes aceitas (HTTP 200/200); consulta FIFO ordenada como esperado, mas oferta da próxima reserva HTTP 500. A etapa de expiração/reoferta não foi executada porque o pré-check não confirmou uma oferta vencida elegível; o processador global não foi chamado. Concorrência do último exemplar produziu uma aceitação e uma rejeição (HTTP 200/403); geração concorrente produziu dois códigos distintos. Limpezas individuais e contagens finais foram confirmadas. Os achados seguem para a Change `corrigir-regras-circulacao`; esta verificação não modifica produto.

## Workflow follow-up

- Review, Apply e Verify desta Change foram concluídos. Os cenários com resultados inesperados contam como achados documentados, não como falha do teste. A etapa de expiração/reoferta foi bloqueada pelo pré-check e permanece explicitamente não avaliada. Limpeza, contagens e sanitização foram confirmadas; arquivar esta verificação não corrige nem aprova os comportamentos encontrados.
