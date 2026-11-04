# Design

## Context

Veja `proposal.md` para a motivação e o escopo. A avaliação registrada em `evaluation/reflex-poc/RESULTS.md` recomenda adotar Reflex com duas mitigações explícitas. Esta Change atualiza somente contexto e documentação; não altera comportamento executável.

## Goals / Non-Goals

**Goals:**

- Fazer `docs/project-overview.md`, `openspec/config.yaml` e `AGENTS.md` concordarem que Reflex foi adotado como tecnologia exclusiva do frontend.
- Registrar as duas mitigações como pendências explícitas na visão geral e como condições para implementar funcionalidades ou fazer deploy.

**Non-Goals:**

- Criar ou alterar qualquer interface, dependência, ambiente virtual ou integração com Xano.
- Escolher ou validar agora um provedor/ambiente de deploy, implementar `:focus-visible` ou afirmar que as mitigações foram concluídas.
- Transformar a documentação em manual de uso do Reflex ou alterar decisões de backend/domínio.

## Decisions

### Registrar Reflex como adotado, sem ampliar autorização

Os três documentos usarão uma formulação consistente: Reflex é a tecnologia adotada e exclusiva do frontend; outra tecnologia de frontend requer mudança arquitetural aprovada. A adoção é uma decisão tecnológica, não autorização para iniciar funcionalidades de produto ou deploy.

Alternativa considerada: manter a linguagem de candidato ou tratar a recomendação como autorização imediata para implementação. Ambas contradizem a decisão registrada e os limites expressos pela avaliação.

### Tratar as duas mitigações como pré-condições

Antes de implementar funcionalidades do produto, deve existir indicador de foco visual `:focus-visible` na busca e sua verificação. Antes de qualquer deploy, deve haver ambiente acadêmico escolhido e validado, segredos mantidos somente no backend e inspeção de logs sem expor valores. As duas condições serão mantidas visíveis na seção de decisões/pendências de `docs/project-overview.md`; não serão consideradas cumpridas por esta atualização documental.

Alternativa considerada: registrar as mitigações apenas como recomendações na avaliação. Rejeitada porque isso não as torna pendências operacionais visíveis nos documentos centrais.

## Risks / Trade-offs

- [A adoção pode ser interpretada como autorização para iniciar o produto] → declarar em cada contexto relevante que funcionalidades e deploy aguardam o cumprimento das mitigações.
- [A prova de conceito pode ser confundida com integração real ou validação de deploy] → preservar o limite de que a avaliação foi local/simulada, sem acesso ao Xano nem deploy público.
- [Os três documentos podem divergir após a edição] → verificar no Apply o texto nos três arquivos e buscar referências remanescentes que ainda chamem Reflex de candidato ou mantenham a avaliação como futura.
