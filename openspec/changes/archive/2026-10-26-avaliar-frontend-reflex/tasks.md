# Tasks

## 1. Ambiente local isolado

- [x] 1.1 Criar a estrutura descartável em `evaluation/reflex-poc/` com uma estratégia única de dependências e versões fixadas; verificar que um ambiente virtual novo no Windows instala e inicia a prova sem depender de arquivos de `biblioteca-nova`.
- [x] 1.2 Documentar pré-requisitos e comandos de preparação, execução, compilação e limpeza da prova; verificar cada comando em uma cópia/ambiente local limpo e confirmar que nenhuma etapa solicita credenciais Xano.

## 2. Serviço REST e sessão simulados

- [x] 2.1 Implementar um serviço REST local com fixtures fictícias para catálogo, sessão/perfis e transições representativas; verificar respostas de sucesso, carregamento, vazio, erro e rejeição de ação administrativa quando a sessão simulada é de estudante.
- [x] 2.2 Ligar o estado Reflex ao serviço local e exercitar autenticação/sessão e cabeçalhos sem segredos reais; inspecionar chamadas e artefatos compilados para confirmar que não há segredos no navegador e que todo tráfego fica restrito ao serviço local simulado.

## 3. Navegação e usabilidade da prova

- [x] 3.1 Construir apenas navegação/transições fictícias para catálogo público, login/cadastro, painel bibliotecário, solicitação/confirmação de empréstimo e reserva/fila; verificar que todos os fluxos podem ser percorridos sem persistência nem regras de negócio reais.
- [x] 3.2 Exercitar busca/filtro, estados vazio/erro/carregamento e navegação por teclado em 360x800 e 1366x768; registrar resultados observáveis e verificar que os elementos essenciais permanecem utilizáveis nas duas dimensões.

## 4. Avaliação e decisão

- [x] 4.1 Avaliar compatibilidade operacional, REST/sessão, fluxos essenciais, controle de acesso, usabilidade, deploy/apresentação e manutenibilidade; para cada critério registrar evidência reproduzível, nota 0–2, resultado do gate, limitação e mitigação verificável quando houver.
- [x] 4.2 Revisar e documentar um caminho de deploy acadêmico, configuração de variáveis secretas e inspeção de erros sem publicar a prova; verificar que premissas não confirmadas (incluindo provedor/ambiente de apresentação) ficam identificadas como lacunas, não como resultados comprovados.
- [x] 4.3 Fazer walkthrough técnico da prova e registrar em `evaluation/reflex-poc/RESULTS.md` a rubrica, as evidências, a pontuação total, o parecer da equipe e a recomendação (adotar, adotar com condição ou não adotar); verificar que qualquer gate pendente e sua mitigação estão explícitos e que a regra proposta de 11/14 foi confirmada na revisão desta Change.
- [x] 4.4 Executar a compilação e os testes locais da prova do início ao fim e conferir o registro final; verificar que não houve tráfego para Xano, deploy público, credenciais reais ou implementação de funcionalidade de produto.
