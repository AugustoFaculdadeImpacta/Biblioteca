# Spec Delta

## Purpose

Define identidade, autenticação, sessão e atribuição confiável de perfil para estudantes e bibliotecários da biblioteca escolar, incluindo proteção contra autoelevação. A autorização de ações administrativas reais será especificada e verificada pela Change que introduzir a primeira dessas ações.

## ADDED Requirements

### Requirement: Cadastro imediato de estudante
O sistema SHALL permitir que uma pessoa crie uma conta com e-mail e senha sem confirmação de e-mail e SHALL iniciar uma sessão de estudante após cadastro bem-sucedido.

#### Scenario: Cadastro bem-sucedido
- **WHEN** uma pessoa envia um e-mail ainda não cadastrado e uma senha que atende às regras confirmadas do provedor
- **THEN** o sistema cria uma conta de estudante e disponibiliza imediatamente uma sessão autenticada

#### Scenario: E-mail já cadastrado
- **WHEN** uma pessoa tenta cadastrar um e-mail que já possui conta
- **THEN** o sistema não cria uma segunda conta e informa que o cadastro não foi concluído

#### Scenario: Cadastro não concede perfil bibliotecário
- **WHEN** uma pessoa tenta incluir ou alterar o perfil no pedido de cadastro
- **THEN** o sistema ignora ou rejeita o campo de perfil e, se o cadastro for bem-sucedido, a conta resultante tem somente o perfil de estudante

### Requirement: Login de conta existente
O sistema SHALL autenticar contas existentes por e-mail e senha e SHALL estabelecer uma sessão somente após autenticação bem-sucedida.

#### Scenario: Credenciais válidas de estudante
- **WHEN** um estudante envia credenciais válidas
- **THEN** o sistema estabelece uma sessão associada à conta de estudante autenticada

#### Scenario: Credenciais válidas de bibliotecário provisionado
- **WHEN** um bibliotecário provisionado envia credenciais válidas
- **THEN** o sistema estabelece uma sessão associada à conta de bibliotecário autenticada

#### Scenario: Credenciais inválidas
- **WHEN** uma pessoa envia credenciais inválidas
- **THEN** o sistema não estabelece uma sessão autenticada e informa que o login falhou

### Requirement: Uso e encerramento da sessão
O sistema SHALL exigir uma sessão válida para operações protegidas, associar cada sessão à identidade e ao perfil determinados pelo backend e encerrar a sessão da aplicação após logout.

#### Scenario: Operação protegida sem sessão
- **WHEN** um visitante tenta executar uma operação protegida sem sessão
- **THEN** o backend recusa a operação e não executa seus efeitos

#### Scenario: Sessão inválida
- **WHEN** uma pessoa apresenta uma sessão inválida ou não reconhecida pelo provedor de autenticação confirmado
- **THEN** o backend recusa a operação protegida e não executa seus efeitos

#### Scenario: Logout
- **WHEN** uma pessoa solicita logout em uma sessão autenticada
- **THEN** o sistema encerra a sessão ativa da aplicação, remove o contexto autenticado e exige novo login para operações protegidas

### Requirement: Adiar bootstrap de bibliotecário
Esta Change SHALL permitir autocadastro somente de estudantes e SHALL adiar o provisionamento do primeiro bibliotecário para uma Change futura. Esta Change não cria nem promove uma conta bibliotecária; a única limpeza direta de registros permitida é a exclusão dos registros fake de `usuario`, conforme requisito de substituição do legado.

#### Scenario: Bootstrap adiado
- **WHEN** a capacidade de identidade é implementada nesta Change
- **THEN** nenhuma conta bibliotecária é provisionada ou promovida; o bootstrap é especificado em Change futura e a limpeza autorizada dos registros fake não afeta essa decisão

#### Scenario: Tentativa pública de promoção
- **WHEN** um estudante tenta alterar o próprio perfil ou invoca uma operação pública de promoção
- **THEN** o sistema não concede perfil bibliotecário e não disponibiliza endpoint público para essa promoção

### Requirement: Atualizar identidade e remover somente o legado autorizado
Condicionada à confirmação da auth nativa do Xano, esta Change SHALL aplicar somente as atualizações e exclusões de recursos e registros explicitamente autorizadas nos cenários abaixo.

#### Scenario: Identidade existente é atualizada in-place
- **WHEN** as mudanças autorizadas são aplicadas
- **THEN** a tabela `usuario` e `POST /auth/signup`, `POST /auth/login`, `GET /auth/me` são atualizados in-place, sem exclusão e recriação ou alteração de seus caminhos

#### Scenario: Estrutura da identidade é preservada e completada
- **WHEN** a definição de `usuario` é atualizada
- **THEN** os campos existentes `id`, `created_at`, `nome` e `telefone` permanecem; e-mail e senha são obrigatórios, `perfil` é adicionado e a unicidade do e-mail é garantida no backend

#### Scenario: Legado de catálogo é removido
- **WHEN** as mudanças autorizadas são aplicadas
- **THEN** as tabelas `livro`, `categorias` e `emprestimo` e suas 18 rotas deixam de existir, e todos os registros dessas três tabelas são perdidos

#### Scenario: Registros fake de identidade são excluídos
- **WHEN** a limpeza autorizada é aplicada
- **THEN** somente os registros fake autorizados dentro de `usuario` são removidos; nenhum outro registro é alterado

#### Scenario: Endpoint de logs explicitamente autorizado
- **WHEN** o diff do Xano inclui a atualização incidental de `GET /logs/user/my_events`
- **THEN** somente essa definição pode ser atualizada, sem excluir o endpoint ou o grupo `Event Logs`, criar tabela de eventos ou implementar comportamento novo

#### Scenario: Recurso fora da lista
- **WHEN** o dry-run ou a execução indica alteração em qualquer recurso, registro, variável ou configuração fora da lista autorizada, inclusive addon `user` ou funções Quick Start
- **THEN** nenhuma escrita é enviada ou a execução é interrompida e volta à revisão

#### Scenario: Prévia completa corresponde ao escopo
- **WHEN** o dry-run é preparado para revisão
- **THEN** a origem contém o snapshot completo de definições e a prévia lista somente atualização de `usuario` e das quatro rotas autorizadas, exclusão das três tabelas legadas e das 18 rotas autorizadas

#### Scenario: CLI propõe exclusões ou efeitos colaterais extras
- **WHEN** a prévia inclui exclusões em cascata, recursos fora da lista, ou referências não resolvidas cujo efeito sobre recursos preservados não foi esclarecido
- **THEN** a prévia é rejeitada e nenhuma escrita é enviada

#### Scenario: Limpeza seletiva de registros não está comprovada
- **WHEN** não há método demonstrado que remova somente os registros fake autorizados em `usuario`
- **THEN** a limpeza e qualquer escrita dependente dela param; `--truncate` e importação ampla de registros não são usados

#### Scenario: Funcionalidades futuras
- **WHEN** a capacidade de identidade e sessão é implementada
- **THEN** não são criadas estruturas antecipadas para funcionalidades futuras de catálogo, empréstimo ou reserva

### Requirement: Aplicar alterações somente no destino Xano confirmado
Imediatamente antes da primeira escrita, esta Change SHALL confirmar pelo CLI o workspace `151966` e a branch `v1`. O usuário autorizou operações delimitadas nessa branch mesmo estando marcada `live`. Se o destino divergir, a execução SHALL parar. Nenhuma escrita pode ocorrer antes de confirmar a compatibilidade da auth nativa e o diff das operações autorizadas.

#### Scenario: Destino reconfirmado
- **WHEN** o CLI confirma workspace `151966` e branch `v1` imediatamente antes da primeira escrita
- **THEN** somente as atualizações, exclusões de tabelas e endpoints e a limpeza de registros explicitamente enumeradas nesta Change podem ser aplicadas

#### Scenario: Workspace não permite push
- **WHEN** o CLI informa que o workspace não permite push, incluindo `allow_push: false`
- **THEN** nenhuma escrita ocorre e a restrição não é alterada nem contornada por esta Change

#### Scenario: Destino diverge
- **WHEN** o workspace ou a branch identificados pelo CLI divergem do destino aprovado
- **THEN** nenhuma escrita é enviada e a execução para para esclarecimento

#### Scenario: Auth nativa incompatível ou não confirmável
- **WHEN** a documentação ou o workspace não confirmam que auth nativa atende aos fluxos e recursos planejados
- **THEN** nenhuma escrita é enviada e a Change retorna à revisão sem inventar contratos alternativos

### Requirement: Preservar recursos não enumerados
Esta Change SHALL preservar endpoints, funções, addons, configurações e demais recursos Xano que não estejam explicitamente enumerados para atualização ou exclusão nos artefatos aprovados. A única limpeza direta de registros permitida é a exclusão dos registros fake de `usuario`.

#### Scenario: Recursos fora do inventário autorizado
- **WHEN** são aplicadas as mudanças desta Change
- **THEN** somente `usuario` e seus três endpoints de identidade são atualizados in-place, os registros de `usuario` são excluídos, as tabelas `livro`, `categorias`, `emprestimo` e suas 18 rotas são removidas, e `GET /logs/user/my_events` é atualizado

### Requirement: Expor somente o perfil confiável da conta
O backend SHALL determinar o perfil da sessão a partir da conta autenticada no Xano. O cliente SHALL NOT poder escolher nem alterar o próprio perfil. Esta Change não cria operações administrativas; a verificação de recusa de uma ação administrativa real SHALL ocorrer na Change que introduzir a primeira operação protegida.

#### Scenario: Cadastro ignora tentativa de autoelevação
- **WHEN** uma pessoa envia um perfil de bibliotecário ou outro valor de papel durante o autocadastro
- **THEN** o backend rejeita ou ignora esse valor e a conta criada recebe somente o perfil estudante

#### Scenario: Sessão retorna o perfil determinado pelo backend
- **WHEN** a pessoa consulta sua sessão autenticada
- **THEN** o perfil retornado corresponde ao perfil confiável associado à conta no Xano, e não a um valor fornecido pelo cliente

#### Scenario: Ação administrativa ainda não existe nesta Change
- **WHEN** esta Change é verificada sem endpoint ou ação administrativa no escopo
- **THEN** a verificação cobre perfil confiável e tentativa de autoelevação; o teste de negação de ação administrativa é adiado para a Change que introduzir essa ação, sem criar endpoint fictício nesta Change
