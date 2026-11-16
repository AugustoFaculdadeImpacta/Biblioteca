# Proposal

## Why

No Windows, `reflex run` falha antes de deixar a interface utilizável: o frontend termina com erro ao iniciar pelo comando gerado e a limpeza pode lançar `psutil.NoSuchProcess`. Ajustes em `.web/` não persistem, pois essa pasta é gerada; precisamos de um caminho local suportado e repetível que mantenha a conexão entre frontend e backend.

## What Changes

- Definir e documentar uma forma persistente, compatível com a configuração Reflex do projeto, para executar a aplicação em Windows.
- Verificar que frontend, backend, rotas e conexão de estado Reflex funcionam juntos, e não apenas que a página ou `/ping` respondem.
- Tratar somente falhas de inicialização/encerramento que impeçam esse fluxo; não contornar políticas de segurança do Windows nem depender de editar arquivos gerados.
- Manter a execução local separada de deploy, Xano e credenciais reais.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `frontend-foundation`: acrescentar o comportamento verificável de execução local no Windows, sem alterar os requisitos de navegação, acessibilidade ou segurança já existentes.

## Impact

- Possíveis arquivos afetados após aprovação: `rxconfig.py`, testes locais de configuração/execução e documentação de setup Reflex em português.
- `.web/` permanece saída gerada e não será a configuração persistente da solução.
- Nenhuma API, dado, schema ou operação Xano é necessária. Não haverá deploy nem alteração de segredos.
