# Tasks

## 1. Capturar e inventariar o estado remoto

- [x] 1.1 Confirmar workspace `151966`, branch live `v1`, CLI 1.3.4 e fazer pull somente de definições para pasta temporária fora do repositório.
- [x] 1.2 Inventariar 11 tabelas/36 endpoints remotos e 9 tabelas/28 endpoints locais; classificar recursos remotos de plataforma e confirmar que não há tabelas ou endpoints somente locais.
- [x] 1.3 Inspecionar e sanitizar campos sensíveis na cópia temporária; não importar registros, variáveis, drafts ou credenciais.

## 2. Reconciliar as definições aprovadas no Git

- [x] 2.1 Aplicar somente retornos explícitos de lista em quatro GETs públicos de catálogo; registrar como (b)/(c) todas as divergências não aprovadas, sem sobrescritas em lote.
- [x] 2.2 Atualizar `xano/README.md` e `docs/xano-workflow.md` com contagens, grupos, recursos de plataforma e pendências classificadas.
- [x] 2.3 Executar os 9 testes locais e revisar `git diff -- xano/` e `git status --short -- xano/`; nenhuma escrita remota ocorreu.

## 3. Verificar a reconciliação

- [x] 3.1 Comparar novamente os arquivos reconciliados com o snapshot, documentar diferenças (b)/(c) e aprovar `openspec validate "reconciliar-xano-com-git" --strict --json`.
- [x] 3.2 Revisar o diff completo; busca de atribuições literais de credenciais encontrou zero valores, e os artefatos temporários estão fora do repositório.

## Workflow follow-up

- Arquivar somente após Verify local aprovado. Não enviar arquivos ao Xano nem criar commit como parte desta Change.
