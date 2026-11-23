# Design

## Context

Consulte [proposal.md](./proposal.md) para a motivação e os deltas de [frontend-foundation](./specs/frontend-foundation/spec.md) e [catalog](./specs/catalog/spec.md) para os contratos. O app e o estado de sessão são Reflex; os clientes existentes de catálogo já validam os contratos das operações.

## Goals / Non-Goals

**Goals:**
- Reaplicar a identidade do snapshot `modelo-visual` sem reverter os comportamentos incorporados depois dele.
- Compartilhar uma única lista de livros entre o importador do site e o script local.
- Usar a sessão do admin e as operações de catálogo existentes, com prévia e tratamento de falha parcial.

**Non-Goals:**
- Alterar schema, endpoints ou dados no Xano durante esta Change.
- Criar categorias, apagar títulos ou adicionar uma operação em lote no backend.
- Executar o script remoto com `--apply`.

## Decisions

1. **Restilizar os componentes Reflex existentes.** Reutilizar `site_header`, `profile_menu`, `accessibility_menu`, `index`, cartões e rodapé. A busca permanece no cabeçalho; a faixa de visão passa a ser irmã do cabeçalho. As regras CSS mantêm dimensões de conteúdo intrínsecas, controles acessíveis e grade de livros de 190–220 px com capas 2:3.
2. **Compartilhar os dados, não duplicar o seed.** `biblioteca_mais_nova/seed_data.py` será a fonte de 30 livros; o script continuará importando essa fonte como alternativa local. Helpers de normalização compararão título e autoria sem caixa e acentos.
3. **Executar a importação no estado Reflex do admin.** A prévia consulta catálogo administrativo e categorias, calcula os pares título/autoria existentes e mapeia categorias por nome normalizado. A confirmação refaz as leituras para evitar aplicar um plano obsoleto e então chama, em série, os clientes existentes de criação de título, associação e exemplar. Categorias ausentes são informadas e seus títulos não são escritos.
4. **Não repetir automaticamente operações confirmadas.** A primeira resposta inesperada ou timeout encerra o fluxo. A interface mantém os contadores, explica eventual resultado parcial, não registra segredos e recarrega o acervo para refletir o estado do servidor.
5. **Testar sem destino remoto.** Testes substituirão os clientes de catálogo por doubles simulados e verificarão que a prévia não escreve, que uma segunda execução não duplica pares existentes, e que falhas encerram a sequência. CSS e contratos de navegação serão testados localmente.

## Riscos / Trade-offs

- **Falha após criar título e antes de concluir exemplares** → registrar o título como criado, contabilizar a falha, recarregar o acervo e não reenviar automaticamente a etapa; uma execução posterior o reconhecerá pelo par título/autoria.
- **Alteração concorrente entre prévia e confirmação** → recalcular o plano imediatamente antes de escrever e tratar a resposta do servidor como autoridade.
- **Categoria ausente no workspace** → mostrar o nome na prévia e no resumo; não criar categoria nem título sem associação.
- **Tema ou texto longo em tela estreita** → manter filhos de grid/flex com largura mínima zero e validar controles e cartões em 360 px.

## Migration Plan

Não há migração. A Change não realiza operações remotas; a importação só poderá gravar quando um admin autenticado confirmar no site.
