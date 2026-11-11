# Design

## Contexto e evidências

O workspace `151966`, branch live `v1`, foi confirmado pela CLI Xano 1.3.4. O pull de definições foi feito para uma pasta temporária fora do repositório, sem registros, variáveis de ambiente ou drafts. O snapshot inicialmente continha credenciais em campos de metadados/exemplos; esses valores foram substituídos por `null` na cópia temporária antes de qualquer inspeção posterior. Nenhum valor de credencial foi copiado ao Git.

Inventário do snapshot: 57 documentos — 11 tabelas, 36 endpoints em três grupos de API, três funções quick-start, um addon, dois recursos AI e metadados do workspace. O Git contém 9 tabelas e 28 endpoints da biblioteca. Não há tabela nem endpoint somente no Git. As 9 tabelas locais têm correspondentes remotos; `usuario` é igual no snapshot, enquanto as outras oito divergem.

## Decisões de classificação

### (a) Compatível e importado no Git

Foram adicionadas declarações explícitas `return = {type: "list"}` em quatro endpoints GET públicos de catálogo, sem trazer os documentos remotos inteiros:

- `GET /catalogo/categorias`;
- `GET /catalogo/categorias/{categoria_id}`;
- `GET /catalogo/categorias/{categoria_id}/titulos`;
- `GET /catalogo/titulos/{titulo_id}`.

As declarações tornam explícito o formato de lista já esperado pelas consultas e pelos contratos de catálogo. Nenhum outro comportamento ou metadado remoto foi copiado.

### (a) Recursos de plataforma fora do escopo — documentados, não importados

O snapshot contém os grupos `Authentication` e `Event Logs`, a tabela `user`, a tabela `event_log`, três funções quick-start, um addon, dois recursos AI e metadados do workspace. São recursos de plataforma, não definições da biblioteca a importar para `xano/`. A tabela `event_log` também está listada abaixo como achado de segurança por declarar `auth = false`.

### (b) Git mantido; divergência remota pendente

As specs de reservas e circulação exigem fila FIFO. O remoto omite a ordenação explícita nos seguintes pontos; o Git permanece inalterado e nenhum push será feito:

- `GET /admin/titulos/{titulo_id}/fila-reservas`: ordenação da fila por `criada_em` e `id`;
- `POST /admin/reservas/ofertar-proxima`: seleção da próxima reserva em FIFO;
- `POST /admin/reservas/processar-expiradas`: ordenação de ofertas expiradas e da próxima reserva elegível;
- `POST /admin/emprestimos/{emprestimo_id}/devolucao`: ordenação usada ao ofertar após devolução.

Estas divergências devem ser verificadas como cenário de FIFO em `verificacao-avancada-circulacao`; esta Change não corrige o remoto.

### (c) Não importar; decisão/equivalência pendente

**Achados de segurança abertos:** o remoto declara `auth = false` para `categoria`, `condicao_exemplar`, `emprestimo`, `exemplar`, `reserva`, `solicitacao_emprestimo`, `titulo`, `titulo_categoria` e `event_log`. A decisão final exige não trazer essas permissões ao Git; `event_log` também é recurso de plataforma. Os demais diffs de schema das oito tabelas comuns permanecem sem importação:

- `categoria` e `titulo`: diferença de permissão;
- `condicao_exemplar`: schema também diverge em `exemplar_id` e `registrado_em`;
- `emprestimo`: schema também diverge em `devolvido_em`, `exemplar_id` e `usuario_id`;
- `exemplar`: schema também diverge em `codigo_tombo`;
- `reserva`: schema também diverge em `criada_em`, `estado`, `id`, `titulo_id` e `usuario_id`;
- `solicitacao_emprestimo`: schema também diverge em `solicitada_em`, `titulo_id` e `usuario_id`;
- `titulo_categoria`: schema também diverge em `categoria_id` e `titulo_id`.

**Divergências de endpoints não importadas:**

- `GET /admin/exemplares/{exemplar_id}/condicoes` e `GET /admin/solicitacoes`: ordenação/serialização divergente, sem contrato que prove equivalência;
- `GET /catalogo/titulos`: reescrita da expressão de append/serialização; `GET /catalogo/titulos/{titulo_id}`: diferenças de resposta/consulta além da lista explícita aplicada;
- `GET /minhas/emprestimos` e `GET /minhas/solicitacoes`: ordenação e forma de consulta/resposta;
- `GET /minhas/reservas`: conversão de fuso e forma da resposta divergentes;
- `PATCH /catalogo/titulos/{titulo_id}`: diferença de comportamento não equivalente comprovada;
- `POST /admin/exemplares`, `POST /admin/exemplares/{exemplar_id}/condicoes`, `POST /admin/reservas/{reserva_id}/retirada` e `POST /admin/solicitacoes/{solicitacao_id}/retirada`: diferenças de consulta, autorização, validação, ordenação ou resposta não comprovadas contra as specs;
- `POST /auth/login`, `POST /auth/signup` e `GET /auth/me`: divergência de resposta/identidade entre `user` e `usuario`, inclusive cópias no grupo de plataforma `Authentication`;
- `POST /catalogo/categorias`, `POST /catalogo/titulos` e `POST /solicitacoes-emprestimo`: diferenças de consulta, validação, autorização ou prazo não comprovadas contra as specs.

Para os quatro endpoints de FIFO classificados (b), diferenças adicionais de resposta, serialização ou prazo também permanecem sem importação. O fluxo de identidade remoto e as alterações relacionadas a `user`/`usuario` não são considerados equivalentes apenas por terem rotas com nomes correspondentes.

## Segurança e execução

- `swagger.token` do grupo Biblioteca foi tratado como exposto e deve ser rotacionado pelo operador no painel. Seu valor não é registrado neste documento nem copiado ao Git.
- `preferences.allow_push = false` não foi alterado. Não houve push, sincronização ou escrita no Xano.
- Não houve commit Git. A cópia temporária sanitizada permanece fora do repositório.
- `.openspec.yaml` declara `skip_specs: true`: esta Change documenta drift de infraestrutura e não altera as specs de produto.
