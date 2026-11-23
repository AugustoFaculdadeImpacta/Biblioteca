# Tasks

## 1. Diagnóstico e solução persistente

- [x] 1.1 Reproduzir `reflex run` no ambiente Windows atual e registrar a cadeia de inicialização/erro; confirmar opções de configuração na documentação oficial e no código da versão instalada, sem editar `.web/` nem contornar políticas do Windows.
- [x] 1.2 Implementar a menor configuração persistente suportada que faça `reflex run` iniciar frontend e backend juntos; se depender de atualização do Reflex, justificar e atualizar a única manifestação de dependências do projeto. Verificar por teste/configuração versionada que regenerar `.web/` não remove a solução.
- [x] 1.3 Corrigir ou atualizar o tratamento de encerramento somente se a falha `NoSuchProcess` mascarar o erro original; adicionar teste focal que reproduza frontend encerrado antes da limpeza e confirme saída sem processo residual. Evidência: `scripts/verificar.ps1` executa compile dry e pytest em sequência; a última execução passou com 310 testes.
- [x] 1.4 Documentar em português o setup Windows e o comando exato `reflex run` no guia Reflex existente; verificar que cada comando documentado corresponde ao fluxo testado.

## 2. Verificação integrada

- [x] 2.1 Executar compilação Reflex e testes focados de configuração/inicialização; confirmar que falhas são explícitas e não alteram arquivos gerados como requisito da solução.
- [x] 2.2 Iniciar a aplicação pelo fluxo acordado e verificar no navegador uma rota pública, recursos carregados e conexão de estado Reflex funcional entre frontend e backend; registrar status observados e inspecionar logs sem segredos.
- [x] 2.3 Encerrar a execução de teste e confirmar que somente processos iniciados por ela foram encerrados, sem afetar listeners preexistentes; repetir `reflex run` para confirmar a solução persistente.

## Workflow follow-up

- Arquivar somente após revisão humana, todas as verificações aprovadas e `openspec validate` estrito válido.
