# Tasks

## 1. Leitura tolerante

- [ ] 1.1 Implementar extração dos envelopes, conversões escalares e validação por registro nos leitores autenticados de empréstimos, pedidos, reservas, equipe, bibliotecários, acervo e categorias; cobrir lista simples/embrulhada, ms/s, nulos, campos extras, registro ilegível e topo inválido com fixtures simuladas.

## 2. Escritas sem repetição

- [ ] 2.1 Tratar respostas POST/PATCH 2xx ilegíveis como sucesso com aviso e atualizar as listas correspondentes sem repetir a escrita; testar status 2xx, erro, transporte e ausência de retry.
- [ ] 2.2 Bloquear novo clique em Reservar durante a tentativa e até a atualização das listas; testar liberação somente após o recarregamento.

## 3. Resumo da home

- [ ] 3.1 Tornar independentes o carregamento, erro, valor “—” e retry de cada indicador; testar falha isolada e preservação dos demais resultados.

## 4. Diagnóstico pelo Perfil

- [ ] 4.1 Adicionar diagnóstico somente leitura para usuários autenticados, com chamadas autorizadas pelo perfil, validação estrutural e relatório copiável sem valores sensíveis; documentar em `docs/diagnostico-xano.md` e testar 200 válido/inválido, 403, 404, 429, não JSON e sanitização.

## 5. Comparação de contratos Xano

- [ ] 5.1 Antes do pull, confirmar via Xano CLI o workspace, branch e ambiente selecionados e registrar a identificação na Change; puxar somente definições para pasta temporária fora do repositório, inventariar todas as chamadas do app e documentar em `docs/xano-diferencas.md` existência, autorização, entradas, resposta esperada, diferença local e recomendação “Publicar: sim/não”; conferir que não houve escrita remota nem segredo/URL no relatório.

## 6. Verificação local

- [ ] 6.1 Atualizar `docs/relatorio-noite.md`, validar Change e specs com `--strict`, executar `reflex compile --dry` e pytest em sequência e revisar as evidências; registrar sucesso/falha sem executar build de produção ou robô visual.

## Workflow follow-up

- Revisar e aprovar os artefatos antes de iniciar Apply.
- Depois de Apply e Verify aprovados, sincronizar specs, arquivar a Change e enviar commits sem force.
