# Tasks

## 1. Preparar isolamento e fixtures rastreáveis

- [ ] 1.1 Confirmar um workspace/branch isolado, descartável e com escrita autorizada; verificar pelo CLI que não é `151966/v1` live antes de criar qualquer fixture.
- [ ] 1.2 Preparar o harness de fixtures com IDs por tabela, mutação temporal apenas em fixtures e limpeza em ordem de dependência; verificar que cada exclusão é confirmada por GET individual HTTP 404.

## 2. Verificar regras temporais e de capacidade

- [ ] 2.1 Verificar que empréstimo vencido bloqueia nova solicitação e reserva, ajustando somente `vence_em` de fixture identificada; verificar a recusa e a limpeza posterior.
- [ ] 2.2 Verificar o limite de um empréstimo ativo por estudante com duas solicitações concorrentes/retiradas; verificar que somente uma retirada é aceita.
- [ ] 2.3 Verificar expiração de oferta de 48 horas e reoferta FIFO à próxima reserva, ajustando somente `expira_em` das fixtures e processando apenas no ambiente isolado; verificar estados e limpeza.

## 3. Verificar concorrência e registrar evidências

- [ ] 3.1 Disputar em paralelo o último exemplar e a geração do código de tombo; verificar invariantes, ausência de colisão e respostas de rejeição esperadas.
- [ ] 3.2 Registrar comandos, respostas sanitizadas, IDs, limpeza e limitações em `RESULTS.md`; verificar que nenhum segredo, dado preexistente ou alteração fora das fixtures aparece na evidência.

## Workflow follow-up

- Arquivar esta Change somente após todos os cenários avançados passarem em ambiente isolado e o Verify ser aprovado.
