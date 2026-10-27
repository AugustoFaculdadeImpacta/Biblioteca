# Resultados da prova Reflex — revisão registrada

**Escopo:** prova local descartável, com fixtures e sessões fictícias. Sem Xano, deploy público, credenciais reais, persistência ou funcionalidades duráveis do produto. A implementação anterior em `biblioteca-nova` não foi usada como dependência ou evidência.

## Ambiente e reprodução

- Windows / PowerShell; Python 3.14.7; Node.js v24.20.0.
- Dependências diretas fixadas em `requirements.txt`: Reflex 0.10.0, FastAPI 0.162.0, Uvicorn 0.38.0 e HTTPX 0.28.1.
- Em uma cópia temporária limpa, os comandos documentados `py -3 -m venv .venv`, atualização de pip e `pip install -r requirements.txt` concluíram; os três testes passaram, `reflex export --frontend-only` compilou e o comando de limpeza do README removeu `.venv`, `.web` e `.reflex`. A cópia temporária foi removida após a verificação.
- Na prova, `reflex run --env preview --frontend-port 3000 --backend-host 127.0.0.1` compilou e iniciou a aplicação; a página retornou HTTP 200. A API simulada iniciou em `127.0.0.1:8765`. Ambos os listeners observados estavam limitados a `127.0.0.1`.
- Um WebSocket local em `ws://127.0.0.1:3000/_event/` completou o handshake e transportou hidratação, estado de carregamento, resultados e eventos de UI. Não houve falha de request nem erro de console no walkthrough.
- `python -m unittest discover -s tests -v`: **3 testes passaram**. O build de frontend também passou com `reflex export --frontend-only`.
- O build/test final emitiu avisos não bloqueantes: `starlette.testclient` depreca o uso atual de HTTPX; Reflex avisa que a ativação implícita de Radix Themes será removida em versão futura; e recomenda WSL para acelerar instalações no Windows. Registrar/reavaliar esses avisos antes de atualizar dependências; não impediram esta execução.
- A configuração inicial do Reflex tinha telemetria opcional habilitada por padrão. Após identificar isso, a prova passou a definir `telemetry_enabled=False`; a configuração foi verificada e um novo preview em loopback executou catálogo, sessão e recusa 403 com WebSocket em `127.0.0.1:3001`, API em `127.0.0.1:8765` e sem erros de console. A execução anterior à desativação pode ter emitido telemetria anônima do framework; não foi possível confirmar retroativamente esse tráfego. A telemetria permanece desativada nas execuções finais/documentadas. A aplicação não define credenciais reais nem endpoints Xano; o payload da telemetria anterior não foi capturado.

## Evidências observadas

### REST, sessão e controle de acesso

- `/health`: serviço simulado saudável; `/catalog`: três fixtures; `mode=empty`: lista vazia; `mode=error`: HTTP 503.
- Testes e walkthrough exercitaram sessão fictícia, cabeçalho `X-Demo-Session`, solicitação, confirmação, fila, 401 sem sessão e 403 para ação administrativa de estudante; o mesmo tipo de ação retorna 200 para bibliotecário.
- O estado de carregamento foi emitido antes da resposta do catálogo. No navegador, busca por “príncipe” retornou somente o título correspondente; vazio e erro mostraram mensagens distintas.
- O cliente compilado em `.web/` não contém os tokens fictícios, o cabeçalho de sessão, o endereço da API mock ou referências a Xano na busca por esses marcadores. As chamadas à API são feitas pelo backend Reflex para `127.0.0.1:8765`; os recursos do navegador e o WebSocket observados usam `127.0.0.1:3000`.
- A configuração final confirma `telemetry_enabled=False`, impedindo o envio opcional de eventos do Reflex nas próximas execuções.
- Isto demonstra somente o padrão da simulação local, não autenticação, autorização nem contrato do Xano.

### Fluxos e navegação

- Percorridos: catálogo público; busca/filtro; tela de entrada/cadastro fictício; sessão estudante e bibliotecário; solicitação e confirmação simuladas; ação administrativa recusada para estudante; fila de reservas; encerramento de sessão.
- Resultados no navegador: solicitação sem sessão 401; solicitação autenticada 200; ação administrativa como estudante 403; confirmação/ação como bibliotecário 200; fila 200.
- A reserva é apenas uma transição para a tela/fila simulada. Não existe criação persistente de reserva, FIFO real, prazo de retirada, disponibilidade concorrente ou regra de empréstimo real.
- Tab alcançou controles de navegação, campo de busca e ações; digitação por teclado filtrou os resultados; Enter ativou navegação para catálogo e reserva. O campo de busca não exibiu indicador visual de foco no teste (outline e box-shadow ausentes e borda sem mudança observável); recomenda-se corrigir e repetir a inspeção antes de qualquer adoção. A limitação não foi silenciosamente tratada como aprovada.
- Em 360×800 e 1366×768 foram percorridos busca, sucesso, vazio, erro e reserva por teclado. Não houve overflow horizontal; os controles essenciais permaneceram acessíveis, com rolagem vertical quando necessária na tela de catálogo móvel.

## Rubrica revisada (0–2 por critério)

Escala do design: 0 = falha/sem evidência; 1 = parcial com lacuna e mitigação; 2 = demonstrado. Nota e gate são separados. A equipe confirmou a regra de aprovação e a política de nota 1 nesta revisão.

| Critério | Nota | Gate | Evidência e limitação / mitigação |
|---|---:|---|---|
| Compatibilidade operacional | 2/2 | Demonstrado localmente | Instalação limpa no Windows, execução preview, HTTP 200 e build confirmados. Registrar esta combinação de versões ao reproduzir. |
| REST e sessão | 2/2 | Demonstrado na simulação | Testes e eventos cobrem catálogo, sessão, cabeçalho, estados e respostas 401/403/200. Xano não foi acessado; validar contrato real em Change futura aprovada. |
| Fluxos essenciais | 2/2 | Demonstrado como navegação fictícia | Walkthrough dos fluxos listados acima; sem persistência nem regras reais, como delimitado no escopo. |
| Controle de acesso | 2/2 | Demonstrado somente no mock | Tentativa direta do endpoint administrativo por estudante recebe 403; isso não comprova autorização no Xano. |
| Interface utilizável | 1/2 | Mitigação aceita pela equipe | Busca, estados, teclado e dois viewports passaram sem overflow horizontal. O campo de busca não teve foco visual distinguível; adicionar estilo `:focus-visible` e repetir o walkthrough antes de iniciar interface de produto. |
| Deploy e apresentação | 1/2 | Mitigação aceita pela equipe | README documenta um caminho e segredos no backend, mas provedor/ambiente acadêmico não foi escolhido nem testado. Escolher e validar o destino, segredos e observabilidade antes de qualquer deploy. |
| Manutenibilidade | 1/2 | Walkthrough concluído, evidência detalhada limitada | Estrutura pequena, isolada e com testes. A equipe confirmou que outra pessoa concluiu o walkthrough independente; os detalhes do feedback e do fluxo explicado não foram fornecidos, portanto não se presume sucesso além da conclusão confirmada nem se atribui nota máxima. |

**Total técnico: 11/14.** A equipe confirmou explicitamente o limiar e que uma nota 1 pode passar quando a mitigação for explicitamente aceita. O resultado atende à regra confirmada com as duas mitigações aceitas; elas continuam obrigatórias antes das etapas indicadas.

## Revisão e recomendação

- Na revisão humana desta Change, a equipe **confirmou explicitamente 11/14** como limiar e a política de que nota 1 pode passar com mitigação explicitamente aceita.
- A equipe confirmou a conclusão de walkthrough independente e recomendou **adotar Reflex**. O nome/papel do revisor e os achados específicos do walkthrough não foram compartilhados; o relatório não presume feedback ou sucesso além da confirmação de conclusão, mantendo a nota de manutenibilidade em 1/2.
- A equipe aceitou manter estas mitigações obrigatórias, sem bloquear a adoção técnica: (1) adicionar e verificar indicador visual `:focus-visible` no campo de busca antes de iniciar interface de produto; (2) escolher e validar o ambiente acadêmico, segredos exclusivamente no backend e inspeção de logs antes de qualquer deploy.
- A adoção é uma decisão sobre a tecnologia candidata, não autorização para implementar funcionalidades nem publicar esta prova. Integração real com Xano e deploy continuam fora deste escopo.

## Deploy e limites

Nenhum provedor, conta ou serviço de deploy foi acessado. O caminho acadêmico continua sendo uma proposta: confirmar provedor e política com a instituição; armazenar segredos apenas no backend do ambiente aprovado; validar health check e logs sem expor valores; publicar somente após Change própria aprovada. A documentação oficial do Reflex sobre [segredos e variáveis de ambiente](https://reflex.dev/docs/hosting/secrets-environment-vars/) e [monitoramento e logs](https://reflex.dev/docs/hosting/app-management/) é referência, não evidência de deploy testado.

Não houve tráfego para Xano, deploy público, credenciais reais, alteração de dados remotos ou implementação de funcionalidade de produto. Os resultados cobrem apenas a prova local e os mocks desta pasta.
