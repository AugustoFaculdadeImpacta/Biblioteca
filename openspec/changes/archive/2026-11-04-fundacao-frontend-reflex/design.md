# Design

## Context

Consulte [proposal.md](./proposal.md) e [spec.md](./specs/frontend-foundation/spec.md). A raiz não contém aplicação Reflex nem `.gitignore`; a prova em `evaluation/reflex-poc/` documenta execução local em `venv + pip`, Reflex 0.10.0 e HTTPX 0.28.1, mas não é aplicação de produto. O OpenAPI local documenta bearer auth e endpoints Xano; esta Change não os invoca.

### Evidência de preparação do Apêndice B

O arquivo `docs/apendices/apendice_B_reflex.md` foi lido antes do setup. Ele exige `venv + pip` (sem misturar uv), `reflex init` com o template em branco, `reflex run` e `pip freeze > requirements.txt`; portanto o plano foi ajustado para usar `reflex init` e registrar o ambiente instalado. Python 3.14.7 e Node.js 24.20.0 estão disponíveis, não havia `.venv` preexistente e as três skills requeridas (`reflex-docs`, `setup-python-env`, `reflex-process-management`) aparecem em `.agents/skills/`. Como já estão disponíveis, não é necessário instalar skills com npx. O apêndice não fixa versões; Reflex 0.10.0/HTTPX 0.28.1 são apenas a combinação comprovada pela prova local e serão usados se a instalação suportar o ambiente atual. Após instalar, foi constatado que o Python de usuário já tinha Reflex 0.9.11; os comandos desta Change usaram explicitamente `.venv\Scripts\python.exe`/`reflex.exe` e não alteraram essa instalação global.

## Goals / Non-Goals

**Goals:**

- Preparar uma aplicação executável na raiz com dependências reproduzíveis e configuração local sem valores Xano hardcoded.
- Separar a interface Reflex das requisições HTTP, executando qualquer acesso ao Xano exclusivamente em código backend.
- Tornar foco de teclado visível e verificar que nenhum token ou cabeçalho de autorização chega ao cliente ou aos logs.

**Non-Goals:**

- Implementar cadastro, login, catálogo, formulários ou qualquer operação de negócio.
- Fazer chamadas reais, especialmente escritas, ao Xano, ou acessar/alterar o workspace remoto.
- Escolher ambiente acadêmico, fazer deploy ou guardar segredos em arquivos versionados.

## Decisions

### Seguir a sequência `venv + pip` do Apêndice B

Criar `.venv` na raiz com `py -m venv`, ativá-lo no PowerShell, atualizar pip, instalar Reflex e executar `reflex init` escolhendo o app em branco. Instalar somente dependências necessárias aos testes e configuração ambiental; ao final registrar as versões instaladas via `pip freeze > requirements.txt`, conforme o apêndice. Não inicializar uma segunda estratégia com uv, Poetry ou Conda. Manter compatibilidade com a combinação local comprovada (Python 3.14.7, Reflex 0.10.0, HTTPX 0.28.1) e verificar dependências com `pip check`.

### Manter a URL Xano no backend e carregar `.env` sem serialização

O cliente HTTP lê `XANO_API_BASE_URL` do ambiente no momento de preparar a chamada. A configuração local pode ser carregada de `.env` no processo backend; o arquivo real é ignorado pelo Git e somente um exemplo sem segredo pode ser versionado. A URL e o cliente HTTP não são expostos por variáveis Reflex serializadas nem usados na configuração pública do frontend.

Alternativa considerada: configurar a URL como variável do bundle/frontend. Rejeitada porque a chamada e sua configuração devem permanecer no servidor.

### Isolar o token em estado privado por sessão Reflex

Manter o token em estado privado do backend, sem expô-lo por vars públicas, eventos, retornos de handlers, mensagens, exceções ou logs. O HTTP client adiciona o bearer header somente no backend. Como Reflex envia deltas de estado ao navegador, testes devem inspecionar estado/eventos e bundle compilado e exercitar sessões separadas; não basta verificar que o atributo foi declarado privado. Se a versão escolhida não permitir provar esse isolamento, interromper a implementação e revisar a arquitetura antes de prosseguir.

Alternativa considerada: armazenamento no navegador (incluindo local/session storage). Rejeitada porque exporia a credencial ao cliente.

O token fica em `_session_token`, variável privada da substate Reflex `State`; o único campo público de sessão é o booleano não sensível `is_authenticated`, usado pela interface para indicar acesso público/autenticado. O setter e o leitor do token são helpers privados, não eventos invocáveis pelo cliente.

### Manter chamadas Xano isoladas e testáveis

Injetar transporte HTTP em testes para usar mock/stub, cobrindo URL ausente/inválida, montagem de URL e bearer header sem saída de rede. A aplicação base não chama endpoints de negócio. Nenhum teste envia requisições de escrita ao Xano live; a validação de endpoints reais fica para as Changes funcionais, igualmente com mocks.

A configuração remota deve usar HTTPS; HTTP é aceito somente para loopback local. Erros de transporte e de status são sanitizados e não incluem URL, corpo de resposta, token ou cabeçalho de autorização.

### Tornar o foco visível sem adicionar fluxo de negócio

Aplicar estilo global `:focus-visible` a campos, botões e controles de navegação. Verificar os seletores no build e percorrer os controles com teclado no app local; a busca demonstrativa é somente leitura e não introduz busca funcional nesta Change.

## Evidências de Apply e Verify local

- O setup seguiu `docs/apendices/apendice_B_reflex.md`, com `.venv` e `pip`; `.env.example` contém somente a chave vazia e `.env`, `.venv/`, `.web/`, `.states/` e `__pycache__/` são ignorados pelo Git.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q`: 12 testes passaram, cobrindo renderização, controles alcançáveis por teclado, URL via ambiente/`.env`, transporte HTTP mockado, sanitização de erros, token privado no delta e isolamento entre duas sessões.
- `reflex compile --dry` e `reflex export --frontend-only` concluíram com sucesso.
- Walkthrough local em modo de produção: a página carregou e conectou ao backend Reflex. Em 360×800, Tab percorreu o link para pular conteúdo, os dois links de navegação, a busca demonstrativa e o botão; todos exibiram contorno `3px solid #005fcc` com deslocamento de `3px`. Em 1366×768, a navegação permaneceu utilizável. Não houve overflow horizontal nos dois viewports.
- No delta real do state manager após armazenar tokens de teste, somente `is_authenticated` foi serializado; `_session_token` e os valores dos tokens não apareceram nos deltas. O teste confirmou isolamento entre identificadores de sessão e ausência dos tokens nos logs.
- Todos os pedidos do cliente Xano nos testes usaram `httpx.MockTransport`; não houve tráfego para Xano live nem operação de escrita.
- O bundle de estado do frontend contém o indicador público `is_authenticated`, mas não `_session_token`; o log do servidor local não contém os marcadores de teste nem exceções de runtime.

## Gate de escopo

Após o usuário restaurar o cache compilado rastreado, o estado Git foi revalidado: `xano/`, `evaluation/` e `openspec/changes/verificacao-avancada-circulacao` não aparecem como alterados. O arquivo `xano/tests/__pycache__/test_candidates.cpython-314.pyc` está presente no worktree. As verificações finais de pytest foram executadas com `PYTHONDONTWRITEBYTECODE=1`.

## Risks / Trade-offs

- [O Apêndice B não está versionado na raiz e a prova local pode não conter todos os seus requisitos] → conferi-lo antes de setup; interromper se indisponível ou incompatível.
- [Um estado Reflex aparentemente privado pode vazar em deltas ou serialização] → inspecionar eventos, estado visível, bundle e isolamento de sessões; não aceitar apenas revisão de código.
- [A URL da API não estar configurada impede requisições] → falhar explicitamente antes de qualquer tráfego, com erro seguro e sem imprimir valor de configuração.
- [Testes locais podem ser confundidos com validação Xano] → todas as chamadas desta Change usam mock; registrar claramente que não houve integração remota.

## Migration Plan

Não há migração ou deploy. O resultado é uma aplicação local aditiva. Em caso de rollback, remover somente os arquivos adicionados por esta Change e o ambiente/artefatos locais gerados, sem afetar `xano/` ou arquivos preexistentes.
