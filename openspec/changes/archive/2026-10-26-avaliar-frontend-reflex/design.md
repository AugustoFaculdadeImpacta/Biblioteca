# Design

## Context

Consulte `proposal.md` para a motivação e o escopo. A raiz do projeto contém contexto OpenSpec, mas não contém aplicação Reflex, dependências ou testes. Os critérios de avaliação estão no planejamento consolidado; Reflex continua candidato, e a implementação de `biblioteca-nova` não serve como evidência de aprovação para este projeto.

## Goals / Non-Goals

**Goals:**

- Fazer uma prova local reproduzível no Windows, pequena o bastante para ser descartada após a decisão.
- Simular apenas o necessário para avaliar navegação, chamadas REST, sessão e diferenças de interface por perfil.
- Coletar evidências separadas por critério, para que ausência de evidência não seja tratada como aprovação.

**Non-Goals:**

- Implementar regras de negócio reais, persistência, autenticação de produção ou partes reutilizáveis do produto.
- Confirmar o contrato, permissões ou comportamento de qualquer workspace Xano.
- Fazer deploy público, criar conta em serviço externo ou armazenar credenciais reais.
- Demonstrar que uma proteção visual substitui autorização no backend.

## Decisions

### Prova isolada e descartável

Manter a aplicação e seus dados simulados em `evaluation/reflex-poc/`, separados da raiz que futuramente conterá o produto. Fixar a versão de Python/Reflex testada, as dependências próprias da prova e comandos curtos para criar ambiente, instalar, executar e verificar. Não adicionar dependências à aplicação de produto nem copiar módulos da implementação de referência.

Alternativa considerada: iniciar a aplicação principal diretamente na raiz. Rejeitada porque Reflex ainda não foi aprovado e isso confundiria uma prova descartável com a arquitetura do produto.

### Dados e REST inteiramente simulados

Usar fixtures locais e uma API REST simulada, sem encaminhamento, DNS ou configuração apontando para Xano. A prova deverá exercitar sucesso, carregamento, vazio, erro e sessão usando credenciais/dados fictícios. Incluir resposta simulada que recuse uma operação administrativa feita como estudante, para demonstrar que autorização deve ser aplicada no servidor; a proteção visual por perfil, sozinha, não conta como autorização.

Alternativa considerada: consultar o Xano existente em modo somente leitura. Rejeitada: o usuário excluiu acesso ao Xano nesta etapa, e um contrato remoto não é necessário para testar a viabilidade básica do framework.

### Navegação mínima, sem implementar biblioteca

Usar telas e transições simuladas apenas para percorrer catálogo público, login/cadastro, painel bibliotecário, solicitação e confirmação de empréstimo e reserva/fila. Não implementar persistência, vencimentos, disponibilidade concorrente, FIFO real ou qualquer regra de negócio completa. Registrar explicitamente quais fluxos foram apenas representados.

Alternativa considerada: construir um CRUD funcional como prova. Rejeitada por exceder o objetivo de avaliar tecnologia e aproximar a prova de uma funcionalidade de produto prematura.

### Rubrica e evidência

Avaliar separadamente os sete critérios do planejamento, com nota 0, 1 ou 2, evidência reproduzível, bloqueio identificado e eventual mitigação verificável. Os critérios são: compatibilidade operacional; REST/sessão; fluxos essenciais; controle de acesso; interface utilizável; deploy/apresentação; manutenibilidade.

Registrar também o parecer da equipe e a decisão: adotar, adotar com condição ou não adotar. A nota mínima proposta é 11/14 e todos os critérios eliminatórios devem ser considerados atendidos; uma pontuação parcial não elimina a necessidade de justificar a mitigação e obter revisão humana. A Change não aprova automaticamente Reflex: a equipe confirma a rubrica e a decisão ao revisar as evidências.

Para tornar a coleta comparável, usar esta escala comum: **0** = falha ou ausência de evidência; **1** = atendimento parcial, com lacuna e mitigação simples, verificável e explicitamente aceita pela equipe; **2** = critério demonstrado pelas evidências abaixo. Registrar gate separadamente da nota. A regra exata de tratamento de nota 1 nos critérios eliminatórios deve ser confirmada na revisão desta Change; gate sem evidência ou sem mitigação aceita impede recomendação de adoção.

| Critério | Verificação observável para a prova |
|---|---|
| Compatibilidade operacional | Seguir do zero as instruções no Windows, instalar as versões fixadas e iniciar/compilar a prova em ambiente virtual novo; guardar versões e comandos executados. |
| Integração REST e sessão | Percorrer sucesso, erro e sessão usando apenas API local simulada; verificar cabeçalho/autenticação simulados, restauração/encerramento e ausência de segredo no bundle e no tráfego do navegador. |
| Fluxos essenciais | Percorrer catálogo público, login/cadastro, painel bibliotecário, solicitação e confirmação de empréstimo e reserva/fila; marcar cada fluxo individualmente como demonstrado ou ausente. |
| Controle de acesso | Verificar catálogo anônimo, ações visíveis por perfil e tentativa direta de ação administrativa recusada pelo serviço REST simulado para estudante; registrar que isso prova apenas o padrão local, não autorização no Xano. |
| Interface utilizável | Exercitar busca/filtro, carregamento, vazio e erro, além de navegação por teclado, nas dimensões 360x800 e 1366x768; registrar problemas e evidência visual/observável. |
| Deploy e apresentação | Documentar um caminho de demonstração, configuração de segredos fora do cliente e inspeção de erros; separar o que foi verificado localmente do que depende de provedor/ambiente acadêmico ainda não escolhido. Não publicar. |
| Manutenibilidade | Fazer walkthrough por outra pessoa da equipe; registrar se ela consegue localizar estado/eventos e explicar como alterar um fluxo, bem como testes e feedback encontrados. |

### Verificações locais sem serviços externos

Executar a prova em Windows com dependências fixadas; validar compilação/inicialização, cenários simulados, erros e estados da UI; inspecionar requests e artefatos do navegador para confirmar que credenciais/secrets de exemplo não são embutidos no frontend. Avaliar visualmente/por navegação teclado em 360x800 e 1366x768. Fazer revisão de deploy documentada, sem publicação externa.

Alternativa considerada: declarar o deploy aprovado com base apenas na execução local. Rejeitada porque execução local não prova publicação, configuração de segredo ou observabilidade num ambiente acadêmico.

## Risks / Trade-offs

- [Mocks podem ocultar incompatibilidades com o contrato Xano] → Registrar que a integração real não foi testada e manter a adoção condicionada a validar o contrato numa Change futura aprovada.
- [A prova parecer uma funcionalidade pronta] → Isolá-la, usar dados fictícios, deixar explícito o caráter descartável e não incluir domínio persistente.
- [O critério de deploy não poder ser comprovado sem publicar] → Avaliar/documentar um caminho reproduzível e segredos/logs esperados; marcar lacunas como não atendidas em vez de simular evidência de publicação.
- [A rubrica mistura pontuação e critérios eliminatórios] → Para cada item, registrar nota, resultado do gate, evidência e mitigação; submeter a regra de aprovação à revisão humana antes de adotar Reflex.
- [Diferenças no ambiente acadêmico não estarem especificadas] → Registrar o ambiente realmente testado e listar como limitação qualquer ambiente de destino que não esteja disponível localmente.

## Migration Plan

Não há migração de dados nem deploy de produto. Na conclusão, registrar a decisão e os artefatos/evidências, manter a prova isolada enquanto for necessária para revisão e removê-la numa Change posterior se a equipe aprovar Reflex e decidir que a prova não deve permanecer. Não realizar limpeza fora do escopo aprovado.

## Open Questions

- O ambiente de apresentação acadêmica (provedor, domínio e requisitos institucionais) ainda não está definido; a prova deve registrar essa lacuna sem escolher um serviço externo.
- A equipe precisa confirmar, durante a revisão desta Change, a interpretação do gate eliminatório quando algum critério obtiver nota 1 e depender de mitigação.
