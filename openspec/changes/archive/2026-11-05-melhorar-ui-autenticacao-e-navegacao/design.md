# Design

## Context

Consulte [proposal.md](./proposal.md) para motivação e as deltas desta Change para os comportamentos normativos. O frontend Reflex já possui rotas públicas e administrativas, estado de autenticação e estilos globais; esta mudança deve reutilizar esses mecanismos sem alterar a API Xano ou a autorização no servidor.

## Goals / Non-Goals

**Goals:**
- Centralizar a navegação e os estilos globais para manter a mesma experiência entre rotas.
- Deixar explícitas as cores de texto, fundo, borda e foco dos controles, em vez de depender do `appearance` do sistema ou dos padrões do navegador.
- Fazer handlers retornarem os resultados de navegação do Reflex e manter mensagens pós-fluxo sem colocar credenciais na URL ou em estado público.
- Verificar comportamento de tela e legibilidade no navegador em tamanhos e aparências definidos na proposta.

**Non-Goals:**
- Alterar contratos Xano, regras de autenticação/autorização ou implementar novas funcionalidades de domínio.
- Guardar token, senha ou credenciais em estado público do Reflex, armazenamento do navegador, URLs ou logs.
- Adicionar dependências de frontend ou substituir Reflex.

## Decisions

### Tema e controles com cores explícitas

Definir tokens de cor, tipografia, raio e espaçamento no tema da aplicação Reflex e estilos globais para `input`, `textarea` e `select`, complementados por estilos explícitos nos componentes Reflex que não herdem de forma consistente. Declarar cor de texto, fundo, placeholder, borda, seleção e estados de foco para ambos os temas; definir o tema da aplicação de modo explícito e permitir a alternância clara/escura por estado controlado, sem depender de estilos nativos do sistema operacional. Botões terão estados distinguíveis e foco visível. A validação no navegador medirá as cores computadas e contrastes, além de confirmar que o conteúdo digitado permanece legível.

**Alternativas consideradas:** usar apenas o tema Radix ou deixar o navegador escolher cores nativas. Foram rejeitadas porque campos brancos já coexistem com texto herdado e a aparência do sistema pode inverter cores sem controle.

### Cabeçalho comum guiado por estado seguro

Construir um componente de cabeçalho compartilhado pelas rotas. A renderização consulta somente informação não secreta necessária à navegação (autenticado e perfil); token permanece no estado backend privado. Visitantes, estudantes e bibliotecários recebem as opções previstas na delta `frontend-foundation`. A ação Sair delega à operação de limpeza de sessão já existente e, ao concluí-la, retorna à navegação pública. A proteção real de operações administrativas continua sendo responsabilidade do backend e do bloqueio de rota já existente.

**Alternativas consideradas:** duplicar links em cada tela ou usar apenas redirecionamentos sem navegação persistente. Foram rejeitadas por divergência entre páginas e pela falta de acesso consistente às rotas.

### Transições e confirmação pós-fluxo

Os handlers de login e cadastro retornam diretamente o resultado de navegação suportado pelo Reflex, em vez de apenas disparar um efeito lateral no cliente. Login direciona conforme o perfil. Cadastro bem-sucedido preserva a sessão privada que habilita o acesso imediato e redireciona à página inicial. Uma indicação de sucesso é mantida como estado efêmero do backend, consumida/limpa ao ser apresentada na página inicial; não usar query string para mensagem ou credenciais. Erros de API permanecem na tela correspondente.

**Alternativas consideradas:** redirecionar via JavaScript separado do handler, ou pôr a mensagem na URL. Foram rejeitadas porque podem não estar associadas ao ciclo de evento do Reflex e porque URLs são persistentes e compartilháveis.

### Início útil e formulários consistentes

Reutilizar os componentes e tokens existentes para apresentar boas-vindas, links públicos e orientações diferentes para visitante e usuário autenticado. Formulários ficam em cartões centralizados com largura máxima, espaço suficiente para labels/mensagens e largura fluida em telas estreitas; o layout deve caber sem rolagem horizontal em 360px. Links entre login e cadastro são explícitos e acessíveis.

**Alternativas consideradas:** introduzir um framework de componentes ou redesenhar cada página isoladamente. Foram rejeitadas para reduzir dependências e evitar inconsistência.

### Verificação sem escrita remota

Exercitar autenticação e navegação com respostas Xano mockadas em testes automatizados. A verificação visual usa navegador local e mede estilos computados em 360px/1366px, tema claro/escuro, navegação por links, redirects e bloqueio administrativo de visitante. Nenhum teste deve executar operações de escrita no Xano live.

## Risks / Trade-offs

- [O perfil visível no cliente pode ficar desatualizado em relação à sessão] → usar os indicadores de sessão existentes e preservar a autorização do backend; limpar o estado do cliente ao sair.
- [Contraste calculado não garante legibilidade de todos os estados] → medir texto, placeholder, borda e foco dos controles em ambos os temas e testar teclado no navegador.
- [Mensagens efêmeras podem desaparecer ao recarregar a página] → manter o comportamento em estado de sessão Reflex e validar a apresentação imediatamente após o redirect, sem persistir dados sensíveis.
- [CSS global pode afetar componentes de terceiros] → limitar seletores aos controles/formulários do app e verificar as páginas existentes no compile e no navegador.

## Migration Plan

Não há migração de dados nem deploy nesta Change. Aplicar os estilos e o componente compartilhado localmente; executar os testes e as verificações de navegador mockadas; reverter somente os arquivos desta Change caso a validação não passe. Não realizar chamadas de escrita ao Xano live.
