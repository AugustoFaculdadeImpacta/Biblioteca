# Design

## Context

Consulte `proposal.md` para a motivação e `specs/` para os contratos completos. A interface principal está concentrada em `biblioteca_mais_nova/biblioteca_mais_nova.py`: coexistem campos Radix e elementos HTML, um único menu Perfil contém aparência e identidade, o Acervo já mantém busca/paginação/um identificador de edição, e a desativação atual recarrega a lista sem comparar explicitamente o valor `ativo`. As capas são SVGs determinísticas em `covers.py`; o seed padrão simula e não imprime segredos.

O script `_APPEARANCE_SCRIPT` já centraliza preferências de aparência no navegador e é incluído no cabeçalho de todas as rotas. Sua persistência deve continuar limitada a tema, escala da fonte, alto contraste e redução de movimento. Nenhum token, sessão, e-mail ou dado pessoal pode entrar no armazenamento local.

As definições locais indicam que `PATCH /catalogo/titulos/{titulo_id}` exige bibliotecário ou admin e bloqueia desativação com empréstimos ou reservas ativos; `POST /reservas` exige perfil estudante. Isso é evidência somente dos arquivos locais. O contrato remoto ainda precisa ser comparado por pull de definições somente leitura durante Apply, após confirmação do workspace, branch e ambiente selecionados.

## Goals / Non-Goals

**Goals:**

- Fazer mudanças verticais nas capacidades existentes sem introduzir tabelas, campos de domínio ou dependências.
- Usar testes automatizados para verificar controles, perfis, contraste, estados de catálogo, mensagens de reserva e segurança do seed.
- Registrar cada uma das oito entregas com commit, testes e estado de conferência visual em `docs/relatorio-noite.md`.

**Non-Goals:**

- Publicar ou sincronizar Xano, executar seed remoto ou gravar dados remotos.
- Capturar telas, operar navegador ou declarar aprovados visualmente os ajustes.
- Alterar permissões efetivas, persistir preferências no perfil do usuário ou acrescentar dados pessoais a `localStorage`.
- Refatorar rotas e operações fora dos comportamentos especificados.

## Decisions

1. **Controles nativos com classes compartilhadas.** Renderizar entrada, área de texto, seleção e checkbox como elementos HTML nativos; concentrar dimensões, borda única, autofill e foco nos estilos `.campo`, `.campo-area`, `.campo-select` e `.campo-check`. Manter os identificadores e handlers existentes. Campos de formulário ocultos permanecem nativos `type="hidden"`. Isso substitui estilos específicos de Radix sem alterar contratos de envio.

2. **Contraste calculado a partir dos tokens efetivos.** Definir tokens de texto/fundo para cada variante e tema, incluindo estados interativos, e testar a razão de contraste. Para capas, calcular a luminância da cor que aparece na faixa após a opacidade SVG e escolher uma cor de texto clara ou escura que atenda 4,5:1. A capa continua determinística e independente do tema.

3. **Dois disclosures com script compartilhado.** Separar Perfil e Acessibilidade em controles próprios; reaproveitar um único script inline, já executado antes da pintura, para aplicar as quatro preferências permitidas e controlar clique externo e Escape nos dois disclosures. O seletor de visão permanece condicionado à sessão de admin real e não altera permissões.

4. **Dicionário central com rótulos explícitos.** Definir em `icons.py` o emoji, texto curto e tipo visual de cada ação/selo. A interface usa um helper pequeno para produzir emoji decorativo e atributos acessíveis. Testes detectam emojis duplicados entre ações, ausência de texto, `title`, `aria-label` ou `aria-hidden`. Usar SVG inline somente se uma ação do dicionário não tiver emoji adequado.

5. **Acervo como lista com seleção de painel.** Reutilizar os dados completos carregados por `list_admin_catalog`, a busca normalizada e o limite existente de dez linhas. Acrescentar um filtro desligado por padrão para inativos e estado de seleção que permita apenas um painel de edição ou exemplares por vez. O catálogo público continua sendo regido pela resposta pública e pelo filtro de inativos já existente, não pelo filtro administrativo.

6. **Confirmação após a escrita, sem otimismo.** Após `update_title`, recarregar o acervo e localizar o mesmo `titulo_id`; comparar o campo `ativo` solicitado com o valor retornado pela leitura. Somente então atualizar a mensagem e a linha. Se a leitura falhar ou continuar ativa, preservar o valor conhecido e apresentar o erro de confirmação solicitado. Os testes usam clientes simulados para sucesso confirmado, sucesso aparente e falhas HTTP/rede.

7. **Mensagens de reserva isoladas por operação.** Adicionar mapeamento específico no caminho de solicitação de reserva, preservando as mensagens gerais das demais operações de catálogo. Usar códigos públicos curtos e mensagens de negócio permitidas; não propagar resposta bruta do Xano. O código local confirma perfil estudante no endpoint público, mas a regra remota será considerada desconhecida até a conferência somente leitura.

8. **Seed seguro por padrão.** Manter o dry-run sem chamadas de escrita, imprimir a linha do destino como primeira linha e preservar credenciais somente em variáveis de ambiente. Ajustar o planejamento de desativação de `Jack Sparrow` e `Something` para procurar esses nomes entre os títulos existentes, não apenas entre os títulos novos planejados. Testes não executarão `--apply`.

## Risks / Trade-offs

- [Risco] HTML nativo pode ter diferenças de estilo entre navegadores → concentrar regras em classes próprias e cobrir atributos, estados e contraste com testes de componentes; validação visual permanece aguardando conferência do usuário.
- [Risco] Uma preferência salva pode não ser lida se o navegador bloquear `localStorage` → manter `try/catch` e fallback para tema do sistema, sem interromper a página.
- [Risco] Resposta HTTP de sucesso não garante que o ambiente remoto tenha a versão esperada do endpoint → confirmar estado por leitura posterior; comparar definições locais e remotas sem publicar.
- [Risco] Exigir texto curto e emoji único para todas as ações pode expor rótulos legados inconsistentes → inventariar botões e selos durante a tarefa de ícones e validar exclusividade automaticamente.

## Migration Plan

Não há migração de dados nem mudança de endpoint prevista. Durante Apply, executar cada tarefa em commit separado, rodar `.\\.venv\\Scripts\\python.exe -m reflex compile --dry` e `pytest --ignore=evaluation` após cada commit e registrar evidências. Fazer pull de definições Xano somente após identificar e registrar destino e somente para diretório temporário fora do repositório; não usar sincronização, publicação ou operações de dados. Ao final, validar a Change e specs, sincronizar/arquivar somente após Verify e revisão exigida, atualizar o relatório, e enviar a branch sem force.
