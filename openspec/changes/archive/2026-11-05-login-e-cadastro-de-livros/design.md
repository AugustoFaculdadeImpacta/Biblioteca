# Design

## Context

Consulte [proposal.md](./proposal.md) e as deltas [identity-session](./specs/identity-session/spec.md) e [catalog](./specs/catalog/spec.md). A fundação Reflex já mantém o token em estado privado e fornece cliente Xano com transporte injetável. O cliente atual ainda não envia o token real no cabeçalho de autorização. A implementação dos endpoints locais em `xano/api/default/` define respostas com IDs mesmo onde `xano/openapi.json` omite schemas; os arquivos `.xs` e tabelas citados abaixo são a fonte de cada campo do fluxo.

## Goals / Non-Goals

**Goals:**

- Implementar login com normalização de e-mail, senha inalterada, perfil vindo da API e token somente no estado backend.
- Corrigir o envio de autorização do cliente HTTP sem registrar nem expor o token.
- Completar cadastro de título, seleção/associação de categorias e criação de exemplares, usando IDs e códigos de tombo retornados pelo backend.
- Manter cada escrita sequencial, mostrar o progresso confirmado e não repetir automaticamente operações cujo resultado ficou incerto.

**Non-Goals:**

- Alterar arquivos ou schemas em `xano/`, fazer chamadas de escrita reais, ou criar endpoints.
- Enviar campos que não existam nos inputs dos `.xs`; a quantidade de exemplares é somente uma instrução local para repetir a chamada que aceita `titulo_id`.
- Criar ou editar categorias. A interface seleciona categorias já listadas pela consulta pública.
- Implementar logout remoto, pois não há endpoint documentado para isso.

## Decisões

### Proveniência dos campos e respostas

| Etapa | Campos de entrada/saída usados | Fonte local |
|---|---|---|
| Login | Entrada `email`, `senha`; retorno `authToken` e `usuario{id,nome,email,perfil}` | `xano/api/default/auth/login_POST.xs` |
| Criar título | Entrada `titulo`, `autores`, opcionais `isbn`, `editora`, `edicao`, `ano_publicacao`, `descricao`; retorno da linha criada incluindo `id` | `xano/api/default/admin/titulos_POST.xs`; tabela `xano/table/titulo.xs` |
| Listar títulos | Retorno `{titulo, categorias, exemplares_disponiveis}`; `titulo.id`, `categorias[].categoria_id` e contagem disponível | `xano/api/default/catalogo/titulos_GET.xs`; tabelas `xano/table/titulo_categoria.xs` e `xano/table/exemplar.xs` |
| Listar categorias | Cada registro contém `id` e `nome` | `xano/api/default/catalogo/categorias_GET.xs`; tabela `xano/table/categoria.xs` |
| Listar títulos de uma categoria | Entrada de rota `categoria_id`; retorno de linhas de título com `id` e metadados | `xano/api/default/catalogo/categorias_titulos_GET.xs`; tabelas `xano/table/titulo_categoria.xs` e `xano/table/titulo.xs` |
| Associar categoria | Entrada de rota `titulo_id`, corpo `categoria_id`; retorno da linha de associação com `id`, `titulo_id`, `categoria_id` | `xano/api/default/admin/titulos_categoria_POST.xs`; tabela `xano/table/titulo_categoria.xs` |
| Criar exemplar | Entrada `titulo_id`; retorno do exemplar incluindo `id`, `titulo_id`, `estado`, `codigo_tombo` | `xano/api/default/admin/exemplares_POST.xs`; tabela `xano/table/exemplar.xs` |

`categorias_titulos_GET.xs` devolve títulos, não opções de categoria; a seleção de opções usa `categorias_GET.xs`. O endpoint de associação declara `titulo_id` na rota e `categoria_id` no corpo. O OpenAPI usa `tituloId` como nome do parâmetro de rota e não inclui vários schemas de resposta; a implementação seguirá a rota real local e não alterará o OpenAPI nem presumirá campos além dos `.xs`. A listagem de títulos por categoria pode confirmar uma associação após um resultado de transporte incerto, comparando o `id` retornado.

### Usar a sessão de login como fonte confiável

Enviar somente `email` e `senha` para `POST /auth/login`. Remover espaços externos e converter o e-mail para minúsculas antes de validar; rejeitar espaços internos; preservar a senha. Validar `authToken` e `usuario` antes de atualizar o estado privado. O perfil é sempre o valor retornado pela API.

Alternativa considerada: aceitar perfil no formulário ou obter um perfil informado pelo cliente. Rejeitada porque `login_POST.xs` retorna a identidade e o perfil confiáveis.

### Enviar autorização somente em requisições backend

Enviar o token no cabeçalho Bearer HTTP somente quando a chamada requer autenticação. O cliente não registra o cabeçalho nem a URL; os testes verificam o token somente no `httpx.MockTransport`. Token e perfil permanecem em campos privados do estado Reflex.

Alternativa considerada: preservar o cabeçalho mascarado atual. Rejeitada porque o backend não autentica a operação com um valor fictício.

### Orquestrar a criação em etapas sem duplicação automática

O evento administrativo valida o perfil bibliotecário no servidor antes de qualquer escrita, cria o título e valida o `id` retornado. Em seguida, associa cada categoria selecionada e permite criar exemplares um por vez. Cada retorno é validado antes de atualizar o progresso; os códigos de tombo vêm exclusivamente da resposta do servidor.

O progresso da operação fica em variáveis privadas da sessão, incluindo o ID do título, categorias pendentes/confirmadas e os códigos de tombo. Uma falha HTTP explícita mantém o que foi confirmado e permite retomar a partir da etapa pendente. Uma falha de transporte ou uma resposta 2xx sem a estrutura esperada torna o resultado daquela escrita incerto; para associação, a tela pode reconciliar com `categorias_titulos_GET.xs`. Para título ou exemplar sem identificador confirmado, a interface não repete essa escrita automaticamente e orienta a conferência antes de iniciar outro cadastro.

A quantidade de exemplares é controlada por ações repetidas na interface, não por um campo enviado: `exemplares_POST.xs` recebe somente `titulo_id`. Os valores confirmados usam os registros retornados, não IDs inseridos manualmente.

Alternativa considerada: enviar todas as operações no navegador ou repetir a sequência inteira ao retentar. Rejeitada porque exporia dados da sessão e poderia duplicar títulos, associações ou exemplares.

### Manter o limite de perfil e a validação do backend

Visitantes são encaminhados ao login e estudantes recebem bloqueio sem iniciar chamadas de escrita. Bibliotecários podem usar a tela; todas as operações são autenticadas e o backend continua a validar o perfil. Erros `403`, `404` e conflitos não são tratados como sucesso.

Alternativa considerada: ocultar somente a navegação administrativa. Rejeitada porque uma rota direta ou evento manipulado não deve iniciar uma escrita.

### Testar sem escritas remotas

Testar login, listagens públicas, criação de título, associações, exemplares, falhas parciais, autorização e privacidade via `httpx.MockTransport`. Nenhum teste automatizado usa a URL Xano real. Leituras públicas reais não são necessárias, pois as respostas estão definidas nas cópias locais `.xs`; a confirmação do destino não produtivo é obrigatória no roteiro manual antes da primeira escrita.

## Riscos / Trade-offs

- [O OpenAPI omite schemas de respostas que os `.xs` locais retornam] → documentar a proveniência aqui e validar os corpos de resposta esperados nos mocks; não inferir campos de outras fontes.
- [A sequência contém múltiplas gravações independentes] → manter o progresso privado, retomar após rejeições explícitas e nunca repetir automaticamente uma escrita de resultado incerto.
- [A autorização do frontend pode ficar desatualizada] → exigir perfil bibliotecário antes da escrita e tratar qualquer `403` do servidor como recusa definitiva.
- [Uma falha de transporte pode ocorrer depois de o servidor persistir] → bloquear repetição automática e solicitar conferência manual do título/associação/exemplar antes de recomeçar.

## Migration Plan

Não há migração de dados nem deploy nesta Change. Todos os testes de API usam transporte simulado. O roteiro manual requer validar ambiente acadêmico não produtivo antes de qualquer criação persistente.

## Decisão em aberto

`xano/openapi.json` deve ser alinhado futuramente às respostas existentes em `titulos_POST.xs`, `categorias_GET.xs`, `titulos_categoria_POST.xs` e `exemplares_POST.xs`, e ao nome `titulo_id` do parâmetro de rota. Essa documentação pendente não bloqueia a implementação local, que se baseia explicitamente nos `.xs`; nenhum campo utilizado pelo fluxo está ausente das implementações lidas.
