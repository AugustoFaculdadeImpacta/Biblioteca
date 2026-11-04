# Tasks

## 1. Registrar a decisão e as condições

- [x] 1.1 Atualizar `docs/project-overview.md` para registrar Reflex como adotado e exclusivo, e listar como pendências o foco visual `:focus-visible` verificado antes de iniciar funcionalidades e a validação do ambiente acadêmico/segredos no backend/inspeção de logs antes de deploy; conferir a seção de decisões e pendências.
- [x] 1.2 Atualizar `openspec/config.yaml` para registrar Reflex como tecnologia adotada e exclusiva, mantendo explícito que adoção não autoriza funcionalidades nem deploy antes das duas mitigações; reler e validar a configuração YAML.
- [x] 1.3 Atualizar `AGENTS.md` para substituir a avaliação prévia por instruções coerentes com a adoção, exclusividade e bloqueios das mitigações; conferir que continua exigindo setup conforme Apêndice B antes de editar ou executar código.

## 2. Verificar consistência e escopo

- [x] 2.1 Comparar o diff dos três arquivos com proposal e design, buscar referências que ainda chamem Reflex de candidato ou avaliação futura e confirmar que funcionalidades/deploy continuam condicionados às duas mitigações.
- [x] 2.2 Conferir `git status` e o diff para confirmar que, fora dos artefatos desta Change, somente `docs/project-overview.md`, `openspec/config.yaml` e `AGENTS.md` foram alterados; não criar interface, `.venv` nem alterar `xano/` ou a Change ativa.

## Workflow follow-up

- Archive é o último passo: executar somente após Apply e Verify aprovados explicitamente pelo usuário.
