# Design

## Context

Ver proposta em [proposal.md](./proposal.md) e contrato em [specs/frontend-foundation/spec.md](./specs/frontend-foundation/spec.md). A configuração versionada em `rxconfig.py` não define portas nem um gerenciador de frontend alternativo. O `.web/package.json` é gerado pelo Reflex e chama `react-router dev`; portanto, alterações manuais nessa pasta não são persistentes.

No ambiente observado, o Reflex é a versão 0.10.0. O início padrão falhou no processo de frontend e, depois, a limpeza lançou `psutil.NoSuchProcess`. A tentativa com `REFLEX_USE_NPM=1` ainda encontrou um shim executável bloqueado pela política do Windows. Executar o entrypoint JavaScript do React Router com Node serviu uma rota por HTTP em uma tentativa, mas isso, isoladamente, não demonstrou uma sessão Reflex funcional. Nenhuma alternativa foi confirmada como solução integrada.

## Goals / Non-Goals

**Goals:**

- Fazer o comando documentado `reflex run` iniciar os dois lados do app e completar a conexão de estado no navegador.
- Manter a solução em configuração versionada ou em comandos de setup documentados; não depender de editar `.web/`.
- Preservar a política de segurança do Windows, a estratégia atual de ambiente Python e a privacidade das configurações.
- Garantir que falhas e encerramentos não ocultem a causa nem deixem processos iniciados pela execução.

**Non-Goals:**

- Trocar Reflex ou introduzir outra tecnologia de frontend.
- Publicar ou testar operações reais no Xano, alterar dados, configurar deploy ou mudar segredos.
- Encerrar processos preexistentes cuja identidade e relação com esta execução não estejam confirmadas.

## Decisions

- **Investigar primeiro as opções suportadas pela versão do Reflex instalada.** A documentação oficial e o código da versão do ambiente determinam se há configuração persistente para o gerenciador e como o processo frontend é iniciado/encerrado. A solução não presume que a variável `REFLEX_USE_NPM` baste: a tentativa anterior ainda encontrou o shim bloqueado.
- **Não aceitar sucesso HTTP isolado como critério.** A validação deve iniciar frontend e backend juntos pelo comando acordado, abrir uma rota no navegador e comprovar a conexão de estado Reflex. A tentativa direta do entrypoint Node é apenas evidência diagnóstica enquanto não completar esse fluxo.
- **Manter a arquitetura e as dependências mínimas.** Primeiro preferir configuração existente e suportada. Só propor alteração de versão/dependência se a investigação mostrar que não há caminho compatível na versão atual; documentar o motivo e preservar a estratégia única de ambiente indicada pelo projeto.
- **Não contornar controles do Windows.** Se o executável continuar bloqueado, registrar o erro e buscar uma opção suportada. Não desativar Device Guard, não copiar shims para caminhos alternativos e não editar a saída gerada para contornar a política.
- **Validar limpeza apenas nos processos da execução de teste.** Identificar as portas antes do teste, usar portas livres e encerrar somente processos cuja criação/identidade nesta tentativa seja confirmada.

## Risks / Trade-offs

- [A política local pode bloquear todos os executáveis de frontend compatíveis] → não reduzir a segurança; apresentar evidência precisa e parar com a limitação caso não exista caminho aprovado.
- [A porta 8000 já apareceu ocupada por um processo não identificado] → não encerrá-lo; escolher portas livres e manter as URLs de frontend/backend coerentes durante o teste.
- [O comportamento de inicialização muda entre versões Reflex] → validar contra a versão real e a documentação correspondente, sem inferir suporte de versões mais novas.

## Migration Plan

1. Reproduzir a falha no ambiente atual e identificar o comando/processo frontend usado pelo Reflex.
2. Implementar, após aprovação, a menor configuração persistente compatível com a versão e documentar o uso no setup existente.
3. Executar compilação e testes focados; validar navegação no navegador e conexão Reflex com frontend/backend iniciados pelo comando acordado.
4. Confirmar encerramento dos processos da tentativa e revisar logs sem expor segredos. Não há migração remota nem rollback de dados; reverter somente a configuração/documentação da Change se a verificação falhar.
