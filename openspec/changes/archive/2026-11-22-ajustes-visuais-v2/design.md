# Design

## Context

O frontend concentra componentes e tokens em `biblioteca_mais_nova.py`. Acessibilidade já usa três chaves `LocalStorage`, enquanto o tema é alternado por script e não persiste. Formulários reutilizam `signup-input`; páginas operacionais já expõem operações e mensagens existentes.

## Goals / Non-Goals

**Goals:**
- Corrigir a demarcação de campos preservando semântica, rótulos, eventos e foco de teclado.
- Compartilhar controles de aparência entre visitante e sessão autenticada e aplicar preferências antes da pintura em todas as rotas.
- Deixar o tema escuro consistente e verificável por cálculo de contraste.
- Simplificar o hero e revisar responsividade e feedback das jornadas de bibliotecário/admin.

**Non-Goals:**
- Alterar endpoints, regras de domínio, autenticação ou contratos Xano.
- Persistir dados além das quatro preferências visuais ou fazer capturas/navegação para inspeção visual.

## Decisions

- Manter os componentes Reflex e corrigir a camada visual compartilhada: o contêiner Radix recebe borda, raio, fundo e altura; o campo interno não desenha borda/sombra, e o foco do teclado permanece perceptível. Usar `rx.el.input` somente se os testes demonstrarem que o `rx.input` não pode cumprir esse contrato.
- Consolidar tema, escala, contraste e movimento em um único valor JSON da chave `biblioteca-aparencia`. Leitura e gravação no navegador ficam protegidas por `try/catch`; um script inline compartilhado aplica atributos/classes no `.a11y-shell` antes da pintura. Sem valor válido, usar `prefers-color-scheme` e os padrões de acessibilidade. A sessão, token, nome e e-mail continuam exclusivamente no backend.
- Centralizar os quatro controles no componente Perfil usado por visitante e autenticado. Sair limpa apenas a sessão e não altera as preferências.
- Revisar tokens e cores fixas do app para que os componentes listados consumam tokens do tema; calcular contraste em testes, com limiar WCAG AA de 4,5:1 para texto e 3:1 para texto grande e limites de controles. Capas de fallback usam variações escuras saturadas no tema escuro.
- Remover a busca, ações e atalhos do hero e o evento/estado/estilos exclusivos dessa busca; manter busca e filtros do catálogo intactos. Renomear apenas o título do rodapé para evitar duplicação com a seção da home.
- Auditar telas e ações operacionais existentes com testes focados e adaptar apenas apresentação, feedback e responsividade. Reutilizar serviços e permissões atuais; qualquer lacuna real de endpoint ou dado será documentada, sem criar contrato substituto.

## Risks / Trade-offs

- [Acesso ao armazenamento pode falhar ou conter JSON inválido] → validar os quatro campos, capturar somente falhas de armazenamento e continuar com padrão do sistema sem bloquear a interface.
- [Tokens incompletos deixam componentes ilegíveis no tema escuro] → auditar cores explícitas e combinações por componente; verificar contraste por teste em vez de depender de inspeção visual.
- [Uma revisão visual ampla pode revelar lacunas de serviço] → manter o escopo frontend, preservar a mensagem de erro existente e registrar dependências do Xano sem operações remotas.

## Migration Plan

Atualizar os controles e estilos compartilhados, substituir o armazenamento atual das preferências pelo formato único com fallback, corrigir os componentes escuros e ajustar home e jornadas operacionais. Se a chave nova não existir, migrar somente os três valores de acessibilidade já salvos, gravar o formato unificado e remover apenas essas chaves antigas de aparência. Valores ausentes ou inválidos usam padrões; não há migração de sessão nem chamada ao Xano.
