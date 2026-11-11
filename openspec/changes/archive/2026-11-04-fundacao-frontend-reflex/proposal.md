# Proposal

## Why

O projeto já adotou Reflex como frontend exclusivo, mas ainda não possui uma aplicação na raiz nem uma base local segura para evoluí-la. Uma fundação pequena, acessível e conectável ao contrato OpenAPI do Xano reduz retrabalho sem antecipar funcionalidades de negócio.

## What Changes

- Criar a estrutura mínima Reflex na raiz do projeto seguindo a sequência do Apêndice B: `venv + pip`, `reflex init` com app em branco e registro de dependências em `requirements.txt`.
- Definir o `.gitignore` para artefatos locais de Python/Reflex e arquivos `.env`, fornecendo somente um `.env.example` sem valores secretos.
- Documentar instalação, configuração e comando de execução local no README da aplicação.
- Implementar layout e navegação base sem fluxos de negócio, com foco `:focus-visible` perceptível em campos e botões.
- Adicionar cliente HTTP server-side cuja base venha de `XANO_API_BASE_URL`; manter token de sessão isolado no estado backend por sessão Reflex e impedir sua exposição no cliente ou em logs.
- Validar com testes automatizados usando mock/stub, compilação e execução local; não enviar chamadas de escrita ao Xano live.

## Capabilities

### New Capabilities

- `frontend-foundation`: estrutura acessível da aplicação Reflex, navegação base e limites seguros do cliente HTTP server-side.

### Modified Capabilities

Nenhuma. Os fluxos de identidade e catálogo serão entregues por Changes verticais posteriores, conforme as specs existentes.

## Impact

- Novos arquivos de aplicação, dependências fixadas, configuração Reflex, `.gitignore`, `.env.example`, README e testes na raiz do projeto.
- Uso do contrato local `xano/openapi.json` como referência, sem alterar `xano/` nem acessar operações de escrita do ambiente live.
- Nenhuma tela de cadastro, login ou administração do catálogo e nenhum deploy nesta Change.
