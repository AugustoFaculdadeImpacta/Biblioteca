# Design

## Context

Consulte `proposal.md` para motivação e `specs/identity-session/spec.md` para o contrato observável. O repositório não contém aplicação de produto nem specs consolidadas. A prova Reflex anterior é descartável e usa uma API simulada; não define integração ou contrato Xano.

## Goals / Non-Goals

**Goals:**

- Reconstruir e configurar no Xano somente a estrutura mínima para identidade e sessão, removendo o legado autorizado antes da integração funcional do Reflex.
- Implementar cadastro, login, sessão, logout, perfil confiável e proteção contra autoelevação numa única capacidade vertical; deixar a autorização de ações administrativas reais para a Change que introduzir a primeira dessas ações.
- Manter Xano como autoridade para autenticação, conta e perfil, e Reflex como intermediário sem enviar token ao cliente.
- Confirmar cada premissa operacional antes da primeira alteração remota, preservar uma referência do estado inicial e não codificar contratos Xano presumidos.
- Restringir mudanças remotas às atualizações, exclusões e limpeza de registros explicitamente listadas nesta Change.
- Incluir os dados e regras de servidor mínimos exigidos pela identidade, sem schema antecipado não relacionado.

**Non-Goals:**

- Criar operações funcionais de catálogo, empréstimo ou reserva.
- Implementar recuperação de conta, SSO, confirmação de matrícula ou promoção posterior de bibliotecários.
- Publicar a aplicação, definir o provedor acadêmico, alterar registros fora da limpeza autorizada da tabela `usuario`, variáveis de ambiente, configurações do workspace, funções ou recursos não listados nesta Change.

## Descoberta de Apply somente leitura

Em 2026-10-27, após confirmação do usuário, o Xano CLI identificou o workspace `151966` no host `x8ki-letl-twmt.n7.xano.io`. A listagem explícita de branches para esse workspace retornou apenas `v1`, com `live: true`; portanto o destino consultado é a branch live. O `workspace pull` foi executado explicitamente para `151966`/`v1`, somente para referência, sem opções `--records` ou `--env`: foram obtidos 35 documentos de definição, não dados de registros nem variáveis de ambiente. A cópia está fora do repositório, no estado local da sessão. Nenhuma escrita remota foi realizada.

O inventário encontrou estas quatro tabelas:

| Tabela | Conteúdo definido | Dados que seriam perdidos se removida |
|---|---|---|
| `usuario` | Identidade com nome, e-mail, telefone e senha protegida | Os registros atuais foram identificados pelo usuário como fake e sua exclusão foi autorizada; nenhuma outra linha pode ser alterada |
| `livro` | Título, autor, ano de publicação, quantidade disponível e referência de categoria | Registros do catálogo |
| `categorias` | Nome da categoria | Categorias existentes |
| `emprestimo` | Referências para usuário e livro, data de empréstimo e devolução | Histórico de empréstimos |

O pull não incluiu registros, então as quantidades de contas, títulos, categorias e empréstimos não foram verificadas. A exclusão das tabelas `livro`, `categorias` e `emprestimo` eliminará os dados nelas contidos; as referências de `emprestimo` apontam para `usuario` e `livro`. Os registros existentes em `usuario` serão excluídos por autorização específica do usuário, que os identificou como fake; nenhuma edição direta de outros registros está autorizada.

Foram encontrados 21 endpoints diretamente dependentes dessas tabelas:

- `usuario` (3): `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`.
- `livro` (6): `GET /livro`, `POST /livro`, `GET /livro/{livro_id}`, `PATCH /livro/{livro_id}`, `PUT /livro/{livro_id}`, `DELETE /livro/{livro_id}`.
- `categorias` (6): `GET /categorias`, `POST /categorias`, `GET /categorias/{categorias_id}`, `PATCH /categorias/{categorias_id}`, `PUT /categorias/{categorias_id}`, `DELETE /categorias/{categorias_id}`.
- `emprestimo` (6): `GET /emprestimo`, `POST /emprestimo`, `GET /emprestimo/{emprestimo_id}`, `PATCH /emprestimo/{emprestimo_id}`, `PUT /emprestimo/{emprestimo_id}`, `DELETE /emprestimo/{emprestimo_id}`.

As três definições de identidade (`usuario` e `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`) serão atualizadas in-place, não excluídas e recriadas. Serão removidas apenas as outras 18 rotas das tabelas `livro`, `categorias` e `emprestimo`, junto dessas três tabelas. Também será atualizado `GET /logs/user/my_events`, uma atualização incidental do Xano CLI explicitamente autorizada; a referência de tabela vazia não autoriza criar tabela de eventos nem comportamento novo. O logout será apenas no estado Reflex; nenhuma rota Xano de logout será presumida sem confirmação documental.

A exclusão das três tabelas `livro`, `categorias` e `emprestimo` apagará os registros nelas; conteúdo e quantidade são desconhecidos. Os registros fake existentes em `usuario` também serão excluídos conforme autorização específica. As 18 rotas de catálogo, categorias e empréstimo deixarão de existir; os três endpoints de identidade permanecerão nos mesmos caminhos e serão atualizados. O endpoint `GET /logs/user/my_events` pode ser atualizado, conforme autorização explícita. Funções, addon `user`, configurações e quaisquer outros recursos permanecem fora do escopo.

### Evidência e limites do Xano CLI

O Xano CLI `1.3.4` identificou somente a branch `v1` no workspace `151966`, marcada `live: true`. `workspace get` retornou `allow_push: false`. Portanto, o CLI pode consultar, fazer pull e gerar dry-run, mas o estado atual do workspace não permite push; esta Change não autoriza alterar a configuração para habilitá-lo nem contornar a restrição. A tarefa de escrita permanece bloqueada até que o próprio destino permita push e isso seja confirmado novamente pelo CLI.

Foi observado um dry-run inicial executado com a pasta parcial `xano/` junto a `--sync --delete`. Ele propôs, além das mudanças pretendidas, excluir três funções Quick Start, o addon `user`, um agente, uma ferramenta, dois grupos de API e rotas de identidade/logs por cascata. Essa origem não representa o workspace inteiro e é insegura para sincronização destrutiva; não deve ser usada para push.

Um segundo dry-run foi executado a partir de uma cópia temporária do pull completo de 35 definições, sobrepondo os quatro candidatos locais e removendo da cópia as três tabelas e 18 endpoints aprovados para exclusão. O resumo foi: `~1` tabela e `-3` tabelas; `~4` endpoints e `-18` endpoints. Os quatro endpoints atualizados foram `auth/signup`, `auth/login`, `auth/me` e `logs/user/my_events`. As remoções foram exatamente `livro`, `categorias`, `emprestimo` e as 18 rotas de livro/categorias/empréstimo. Nenhuma exclusão de funções, addon, agente, ferramenta ou grupo de API apareceu nessa prévia.

O mesmo preview emitiu avisos de referências de tabela vazias no addon `user`, no endpoint `logs/user/my_events` e nas três funções Quick Start (`enforce_role`, `generate_magic_link`, `log_event`; o aviso da função de magic link apareceu duas vezes). O CLI informa que referências não resolvidas podem virar statements placeholder após import. Embora esses objetos não apareçam como atualizações/exclusões no resumo, seu comportamento após import não foi provado. A prévia não pode ser aprovada para escrita enquanto o impacto desses avisos sobre os recursos que devem ser preservados não estiver esclarecido; não corrigir addon, funções ou logs adicionando tabelas ou comportamento fora do escopo.

O preview da tabela `usuario` indicou `ADD_FIELD` e dois `UPDATE_FIELD`, mas o resumo não nomeou os campos nem esclareceu a semântica exata. O candidato local preserva `id`, `created_at`, `nome` e `telefone`; torna e-mail e senha obrigatórios, adiciona `perfil` e índice único de e-mail. A prévia detalhada deve confirmar cada alteração, incluindo impacto de obrigatoriedade/unicidade, antes da revisão humana. O índice de e-mail deve impedir duplicidade também sob cadastro concorrente; erros de conflito precisam ser tratados no fluxo de signup.

A limpeza seletiva dos registros fake de `usuario` não aparece no dry-run de documentos e não foi demonstrada por um comando do CLI. O pull de referência não contém registros. `--records` importa dados, e `--truncate` trunca tabelas antes de importar; nenhum deles será usado para apagar registros. Se não houver mecanismo documentado e comprovadamente limitado a `usuario` e aos registros autorizados, parar antes de qualquer escrita.

#### Critérios para aceitar ou interromper diante do dry-run

Antes de qualquer push, apresentar a prévia integral e aguardar aprovação explícita daquela prévia específica. Ela só pode incluir:

- atualização in-place da tabela `usuario` e de seus três endpoints `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`;
- atualização de `GET /logs/user/my_events`, limitada à definição autorizada e sem criar tabela de eventos;
- exclusão das tabelas `livro`, `categorias`, `emprestimo` e das 18 rotas de catálogo/categorias/empréstimo.

Interromper se aparecer qualquer exclusão ou atualização de recursos não listados, cascata sobre grupo de API, endpoint de identidade/logs, addon, função, agente ou ferramenta; se referências não resolvidas puderem alterar comportamento de recursos preservados; se os campos/índices tiverem efeitos não explicados; se não houver limpeza seletiva comprovada dos registros de `usuario`; se `allow_push` continuar falso; ou se o destino divergir. `--sync --delete` só pode ser usado com o snapshot completo de referência. Nunca usar `--truncate`, `--records`, `--env` ou um conjunto parcial de arquivos como forma de contornar os gates de escopo.

## Decisions

### Adotar Reflex com as mitigações aceitas

A revisão registrada da prova local confirmou explicitamente o limiar de 11/14, aceitou nota 1 quando há mitigação explícita e recomendou adotar Reflex. Esta Change usa Reflex para a interface e mediação de chamadas, sem tratar a prova mockada como evidência de integração Xano. Antes de editar ou executar código, Apply deve cumprir o Apêndice B do curso e as instruções oficiais de setup, manter uma única estratégia de ambiente/dependências e verificar foco `:focus-visible` na interface. Nenhum deploy faz parte desta Change; destino acadêmico, segredos e observabilidade devem ser decididos antes de uma Change própria de deploy.

### Confirmar destino e auth nativa antes de alterar Xano

Imediatamente antes de qualquer escrita, confirmar pelo CLI que o destino continua workspace `151966`, branch `v1`, e que o próprio workspace permite push. O usuário autorizou operações delimitadas nessa branch apesar de `live: true`, mas não autorizou contornar `allow_push: false`. Se workspace, branch ou permissão divergirem, parar. As operações autorizadas são: atualizar in-place a tabela `usuario` e os três endpoints de identidade existentes; excluir somente os registros fake da tabela `usuario`; excluir as tabelas `livro`, `categorias`, `emprestimo` e suas 18 rotas; atualizar `GET /logs/user/my_events`. Não alterar quaisquer outros registros, variáveis, configurações, funções, addon ou recursos.

Consultar documentação oficial e verificar se a autenticação nativa suporta e-mail/senha, cadastro com sessão imediata, associação confiável de perfil, login, perfil e os erros/logout exigidos. Atualizar in-place a tabela autenticável `usuario` e os endpoints existentes `POST /auth/signup`, `POST /auth/login` e `GET /auth/me`, seguindo o contrato nativo confirmado e preservando seus caminhos. O diff deve também mostrar a exclusão dos registros fake somente de `usuario`, exclusão das outras três tabelas e 18 endpoints, e atualização de `GET /logs/user/my_events`. Se o diff divergir ou exigir qualquer alteração não autorizada, parar e retornar à revisão.

Se a auth nativa não atender ou seus requisitos não puderem ser confirmados, interromper Apply antes de qualquer escrita. Não inventar token, endpoint ou ciclo de sessão.

**Confirmação somente leitura (2026-10-27):** a documentação oficial [User Auth & Data](https://docs.xano.com/building-backend-features/user-authentication-and-user-data) descreve tabela com autenticação habilitada, endpoints predefinidos Login, Signup e `auth/me`, checagem de conta duplicada no fluxo típico de signup e emissão de token após signup/login. O pull atual do workspace/branch aprovados confirma `auth = true` na tabela legada `usuario`; `POST /auth/signup` verifica e-mail duplicado e cria token imediatamente, `POST /auth/login` valida a senha e cria token, e `GET /auth/me` exige autenticação e busca a conta pelo id autenticado. A documentação [Restricting Access (RBAC)](https://docs.xano.com/building-backend-features/user-authentication-and-user-data/restricting-access-rbac) confirma que o backend pode obter o registro associado ao id autenticado e aplicar uma precondition ao perfil, sem confiar no valor enviado pelo cliente. Isto confirma o mecanismo nativo necessário, não a sintaxe nem o schema da tabela nova. O contrato legado observado usa expiração de token de `86400` segundos; o parser do CLI exige um campo de expiração no candidato XanoScript. Esse valor foi observado, mas não é decisão aprovada para o contrato novo: confirmar documentação/mecanismo nativo antes de fixá-lo. Se não for possível confirmar o valor ou uma configuração equivalente, parar sem push. A Change exige logout local Reflex; a documentação examinada não confirmou revogação remota, portanto não será presumida.

A ferramenta Xano Developer MCP para validação de XanoScript não está disponível nesta sessão; a confirmação documental foi feita nas fontes oficiais acima e as definições atuais foram inspecionadas por pull do Xano CLI somente leitura, sem dados ou variáveis de ambiente. Não declarar validação MCP. Antes de qualquer push, apresentar dry-run completo e aguardar revisão humana explícita. Respeitar `allow_push: false`; não alterar essa configuração. Usar snapshot completo, não a pasta parcial `xano/` com `--sync --delete`. Parar diante de qualquer recurso ou cascata fora da lista, de warnings com efeito não esclarecido, de contrato de expiração não confirmado ou da impossibilidade de remover apenas os registros autorizados de `usuario`. Não usar `--truncate`, `--records` nem `--env`.

Alternativa considerada: inferir o contrato pela prova anterior ou pelo projeto `biblioteca-nova`. Rejeitada porque aquela prova usa fixtures e o projeto antigo não é fonte de verdade para este backend.

### Limitar cadastro público a estudante

O fluxo público delega a criação de credencial ao mecanismo Xano confirmado e define o perfil de estudante no backend. Campos de papel recebidos do cliente não são fonte de autorização. Não há endpoint público de promoção. O bootstrap do primeiro bibliotecário fica adiado para Change futura: a única edição de registros nesta Change é a exclusão especificamente autorizada dos registros fake existentes em `usuario`.

Alternativa considerada: aceitar perfil enviado pelo cliente ou criar bootstrap público. Rejeitada por permitir elevação de privilégios.

### Substituir recursos legados conforme a lista autorizada

Atualizar in-place a tabela `usuario` e os endpoints de identidade legados `POST /auth/signup`, `POST /auth/login` e `GET /auth/me`; excluir somente os registros fake existentes em `usuario`; excluir as tabelas `livro`, `categorias`, `emprestimo` e as 18 rotas listadas para elas; e atualizar `GET /logs/user/my_events`. A exclusão dos três conjuntos de dados das tabelas removidas e das linhas fake de `usuario` é intencional e autorizada. Os três endpoints de identidade mantêm seus caminhos. Não alterar addon `user`, funções Quick Start nem outros recursos não enumerados.

O bootstrap da conta de bibliotecário fica adiado. Uma Change futura deve definir o provisionamento do primeiro bibliotecário. Changes futuras também devem especificar e implementar as capacidades de catálogo, categorias, exemplares e empréstimo sem assumir que as tabelas antigas são o modelo final.

### Intermediar a sessão pelo backend Reflex

Chamadas de cadastro/login e operações autenticadas passam pelo backend Reflex. O token retornado pelo mecanismo confirmado permanece somente em estado privado e isolado por sessão de usuário no backend; nunca em estado público, bundle, armazenamento local do navegador ou resposta de UI. O backend usa o token ao chamar Xano e deriva o perfil de uma fonte confiável no servidor. Verificar isolamento concorrente entre usuários e que payloads/eventos enviados ao navegador não incluem o token.

Logout limpa o contexto autenticado e o token mantidos para a sessão da aplicação, bloqueando novas chamadas autenticadas a partir dela. Revogação do token no Xano não é presumida: implementá-la somente se auth nativa e documentação confirmarem o mecanismo. Registrar a diferença entre invalidar a sessão local da aplicação e revogar credencial no provedor.

Alternativa considerada: enviar token ao navegador para chamadas REST diretas. Rejeitada porque expõe a credencial ao cliente e contraria o limite de segurança definido.

### Estabelecer perfil confiável; deferir autorização de ações administrativas

Nesta Change, o backend sempre atribui o perfil estudante no autocadastro, ignora ou rejeita um papel enviado pelo cliente e obtém o perfil da conta autenticada a partir da fonte confiável no Xano. Os testes cobrem tentativa de autoelevação e confirmação do perfil da sessão, sem usar token forjado nem alterar registros diretamente.

Esta Change não cria nenhuma ação administrativa nem endpoint que represente uma ação dessas. Portanto, não há operação cujo efeito possa ser testado como negado a um estudante. A implementação e o teste de autorização de uma ação administrativa real ficam para a Change futura que introduzir a primeira operação protegida; essa futura Change deverá validar sessão e perfil no backend antes de qualquer efeito, não apenas ocultar controles na interface. Não adicionar endpoint fictício ou de teste para preencher essa lacuna.

### Qualidade de senha e mensagens de erro

Usar as regras de senha, unicidade de e-mail e erros suportados pelo auth nativo confirmado. Não inventar política local divergente. A interface comunica falha de cadastro/login sem exibir token, segredo ou detalhes internos; a forma de evitar enumeração de contas deve seguir o comportamento seguro disponível e ser registrada se o provedor limitar essa personalização.

## Risks / Trade-offs

- [O Xano nativo pode não oferecer todos os comportamentos ou o isolamento esperado] → Validar documentação e destino antes de implementar; parar e revisar a Change se houver incompatibilidade.
- [O workspace informa `allow_push: false`] → O CLI permite consulta/pull/dry-run, mas não há autorização técnica para push no estado observado. Aguardar que o próprio workspace permita escrita e reconfirmar; não alterar configurações nem contornar a restrição.
- [Estado privado Reflex ser confundido com estado isolado por usuário] → Testar duas sessões simultâneas e provar que tokens e perfis nunca cruzam usuários.
- [Logout local não revogar token ainda válido no Xano] → Limpar o estado servidor da aplicação; documentar a semântica exata confirmada e exigir revogação no provedor apenas se suportada e necessária.
- [Cadastro sem confirmação de e-mail facilitar contas indevidas] → Preservar a decisão aprovada; não inventar confirmação. Registrar limites de elegibilidade e duplicidade para decisão futura se se tornarem requisito.
- [Perda irrecuperável de registros legados] → A exclusão das tabelas `livro`, `categorias` e `emprestimo` apaga seus registros; o pull não incluiu dados nem quantidades. Os registros fake de `usuario` também serão excluídos por autorização explícita. Não copiar nem editar linhas fora dessa limpeza autorizada.
- [18 rotas legadas deixam de existir] → Declarar explicitamente a indisponibilidade. As três rotas de identidade continuam nos mesmos caminhos; rotas de catálogo/empréstimo só serão reintroduzidas em Changes futuras. Manter fora do escopo qualquer outra rota e recurso, exceto a atualização expressamente autorizada de `GET /logs/user/my_events`.
- [O CLI pode modificar recursos incidentais] → A pasta parcial com `--sync --delete` propôs exclusões não autorizadas de addon/funções/agente/ferramenta/grupos e endpoints por cascata. Usar somente baseline completo; parar se recursos extras ou cascatas reaparecerem. Os warnings de referências vazias podem virar placeholders e precisam ter o efeito esclarecido antes de escrita.
- [A atualização de `usuario` pode alterar validação de dados existentes] → O candidato torna e-mail/senha obrigatórios, adiciona perfil e índice único. Confirmar o diff detalhado; preservar `nome`/`telefone` e interromper se surgirem efeitos não autorizados ou inconsistentes.
- [A limpeza de registros não está representada no dry-run de documentos] → Não considerar as linhas fake removidas por omissão de ficheiros. Exigir operação seletiva comprovada para `usuario`; sem ela, parar. Não usar truncamento global ou importação de registros como substituto.
- [Expiração do token não confirmada para o contrato novo] → O CLI exige `expiration` no candidato e o legado usa 86400 segundos; confirmar mecanismo/documentação antes de fixar o valor, sem presumir que o legado define a política nova.
- [Escrita no destino incorreto] → Reconfirmar workspace `151966` e branch `v1` imediatamente antes da primeira escrita; qualquer discrepância interrompe a operação.
- [Auth nativa exigir contrato diferente] → Confirmar documentação/compatibilidade antes de escrever; interromper e voltar à revisão se tabela/rotas propostas não forem suportadas.
- [Nenhuma conta bibliotecária poderá autenticar nesta Change] → O bootstrap é adiado para Change futura; a exclusão autorizada das linhas fake de `usuario` não cria nem promove uma conta bibliotecária.
- [Autorização de ação administrativa não verificável nesta capacidade] → Não existe endpoint administrativo após a remoção das 18 rotas de catálogo, categorias e empréstimo; verificar agora o perfil confiável e a proteção contra autoelevação, e exigir teste de negação em backend quando uma Change futura adicionar a primeira ação administrativa.
- [A avaliação Reflex registrou que o campo de busca não tinha foco visual distinguível] → Corrigir e verificar foco `:focus-visible` na base visual antes ou durante a primeira tela funcional, conforme a mitigação aceita pela equipe.

## Migration Plan

1. Reconfirmar por CLI o workspace `151966`, branch `v1`, estado live e permissão de push; parar se o destino divergir ou `allow_push` continuar falso.
2. Confirmar autenticação nativa, contrato de perfil e política de expiração de token; parar antes de escrita se qualquer contrato necessário não puder ser confirmado.
3. Preparar snapshot completo do pull somente de definições e sobrepor os candidatos aprovados. Não incluir registros ou variáveis de ambiente.
4. Gerar dry-run com a fonte completa; revisar a prévia detalhada e os warnings. A lista permitida é update in-place da tabela e três rotas de identidade, update de `GET /logs/user/my_events`, exclusão das três tabelas legadas e 18 rotas. Parar se aparecer qualquer outro recurso, cascata, warning com efeito não esclarecido ou alteração de campo não explicada. Apresentar a prévia integral e aguardar aprovação explícita.
5. Demonstrar, separadamente do dry-run de definições, um método específico de limpeza apenas dos registros fake de `usuario`. Se não for possível comprovar e limitar a operação, parar sem escrita; não usar `--truncate`, `--records`, nem operação ampla. Reconfirmar workspace/branch imediatamente antes de qualquer escrita.
6. Aplicar somente a prévia aprovada, se o destino permitir push e todos os gates anteriores estiverem satisfeitos. Revisar resultado e provar que recursos preservados e registros não autorizados não foram alterados.
7. Testar no Xano cadastro imediato de estudante, duplicidade, papel confiável, login e sessão conforme as rotas atualizadas; documentar evidências sem credenciais. Não provisionar bibliotecário nem criar operação administrativa.
8. Cumprir o Apêndice B e setup Reflex; integrar pelo backend Reflex os fluxos de cadastro, login, sessão e logout local, mantendo token privado.
9. Verificar integração Reflex/Xano, isolamento de sessão, erros, tentativa de autoelevação, navegação e acessibilidade conforme os requisitos; deixar ação administrativa real e login bibliotecário dependentes das Changes de bootstrap/operação correspondentes.

Rollback não recupera registros excluídos das três tabelas removidas nem os registros fake apagados de `usuario`; o pull não contém dados. Não apagar nem recriar as três rotas de identidade como forma de rollback: os endpoints devem ser atualizados in-place. Se o plano de execução não puder aplicar ou reverter somente as atualizações/exclusões autorizadas, parar antes da escrita e voltar à revisão.
