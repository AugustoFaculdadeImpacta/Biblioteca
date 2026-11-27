# Design

## Context

O cliente Xano já limita chamadas, mantém alguns caches em memória e recebe sessões Reflex no backend. A configuração pública é local ao processo; uma cópia em disco precisa sobreviver a reinícios sem ser armazenada no repositório.

## Goals / Non-Goals

**Goals:**
- Preservar dados recentes quando a rede estiver lenta ou limitada.
- Exibir estados otimistas reversíveis e evitar duplicar escritas.
- Manter os limites existentes do cliente e demonstrar latência no servidor simulado.

**Non-Goals:**
- Alterar endpoints, regras autoritativas ou dados no Xano.
- Mudar o layout aprovado ou adicionar dependências.

## Decisions

- Implementar cópias públicas num módulo pequeno, com JSON versionado e escrita atômica no diretório retornado por `tempfile.gettempdir()`. Cópias vencidas após 24 horas não serão usadas.
- Inicializar pré-carga por um caminho idempotente compatível com a versão instalada do Reflex; se não houver gancho de startup utilizável, dispará-la uma vez na primeira visita.
- Reutilizar os estados e o limitador atuais para atualizações em segundo plano; nunca servir dados antigos após uma escrita própria sem aplicar a alteração local e reconciliar a lista.
- Serializar escritas no cliente e agrupar invalidações por lista por 1,5 segundo. Escritas não terão retries.
- Preservar o README estritamente conciso e versionar nele apenas a URL base autorizada pelo usuário, sem copiar outros valores do `.env`.

## Risks / Trade-offs

- [Falha ou corrupção do arquivo] → validar conteúdo ao ler, gravar atomicamente e manter o cache em memória.
- [Atualização em segundo plano compete com chamadas do usuário] → submeter leituras ao limitador existente e não bloquear renderização.
- [Pré-carga por chamada de página] → proteger com um estado compartilhado de tarefa única.
