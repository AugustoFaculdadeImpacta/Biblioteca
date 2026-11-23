# Design

## Context

Consulte `proposal.md` para o motivo da mudança. O frontend é concentrado em `biblioteca_mais_nova/biblioteca_mais_nova.py` e já possui dados públicos e administrativos reutilizáveis. A quebra atual vem da aplicação de estilos compartilhados de ações sobre links de navegação.

## Goals / Non-Goals

**Goals:**

- Restaurar uma barra única, estável e sem vazamento de classes de botão.
- Aplicar um contêiner máximo de 1200 px e layouts verticais consistentes.
- Usar dados reais do catálogo para home e categorias.
- Resolver capas sem download local e sem requisição externa do servidor.
- Tornar o diagnóstico da desativação opt-in e não secreto.

**Non-Goals:**

- Alterar regras de autenticação ou tabelas Xano.
- Publicar, sincronizar ou excluir dados no Xano.
- Criar downloads ou arquivos binários de capa no repositório.
- Alterar o modelo conceitual além de metadados bibliográficos já necessários.

## Decisions

1. **Header separado por semântica.** `site-header`, `brand-link`, `site-nav`, `site-nav-link`, `site-header-actions` e `site-menu-toggle` terão seletores próprios. Links de navegação não receberão `data-action-type` nem classes de ação.

2. **Variáveis efetivas do tema.** Todo o CSS novo usará tokens existentes como `--bg-panel`, `--text`, `--brand-100`, `--line` e `--brand-*`; estados serão verificados por contraste em ambos os temas.

3. **Contêineres explícitos.** Páginas operacionais usarão uma única área larga centralizada. Login/cadastro usarão cartão estreito único com abas. Grades de catálogo usarão `auto-fill` com cartões de 180–220 px.

4. **Capas em cascata.** Prioridade: `capa_url` HTTPS, URL Open Library com ISBN13, `gerar_capa_svg`, e fallback CSS. A imagem real fica acima da gerada visualmente; `onerror` remove a imagem.

5. **Seed declarativo.** A lista terá exatamente 30 títulos únicos, somente nas oito categorias aprovadas, campos bibliográficos completos e ISBN-13 válido. O modo padrão continua dry-run.

6. **Diagnóstico ambiental.** `BIBLIOTECA_DIAGNOSTICO=1` habilita logs de PATCH e releitura em terminal. Os logs registram método, caminho relativo, nomes de chaves, status e campo `ativo`, nunca host, tokens, corpo completo ou dados pessoais.

## Risks / Trade-offs

- [Risco] Edições de muitos componentes em uma única Change → Mitigação: commits por tarefa e testes por superfície.
- [Risco] ISBN de edição brasileira pode não existir na Open Library → Mitigação: verificar rede, preferir edição original e registrar pendência sem publicação.
- [Risco] Navegador bloquear imagens externas → Mitigação: `onerror` revela a capa gerada e não deixa ícone quebrado.
- [Risco] Ambiente não expor `BIBLIOTECA_DIAGNOSTICO` → Mitigação: fallback silencioso e teste automatizado.

## Migration Plan

Aplicar cada tarefa em commit separado, rodar `.\\.venv\\Scripts\\python.exe -m reflex compile --dry` e pytest completo após cada commit, registrar hashes no relatório e validar/arquivar depois de 8/8 tarefas. Nenhuma operação remota de escrita será executada.
