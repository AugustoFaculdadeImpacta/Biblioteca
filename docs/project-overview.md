# Visão geral do projeto — Biblioteca escolar

## Visão e objetivo

Construir do zero uma aplicação web funcional para uma biblioteca escolar. A aplicação permite que estudantes consultem o acervo, solicitem empréstimos e reservem títulos; bibliotecários mantêm o acervo e registram as operações físicas de retirada, devolução, danos e perdas.

O projeto é acadêmico e será desenvolvido incrementalmente com OpenSpec. Cada Change deve entregar uma capacidade pequena, vertical e verificável. Dados, regras do backend, API e interface evoluem juntos com a capacidade, sem criar antecipadamente todo o banco de dados.

## Usuários

- **Visitante:** consulta pública do catálogo e disponibilidade agregada.
- **Estudante:** autocadastra-se e recebe acesso imediatamente, sem confirmação de e-mail; solicita empréstimos e reservas se estiver elegível.
- **Bibliotecário:** administra títulos, categorias e exemplares; confirma fisicamente retiradas e devoluções; registra condições dos exemplares.

Autocadastro nunca concede perfil de bibliotecário. O método seguro de provisionamento de bibliotecários ainda precisa ser especificado.

## Escopo funcional

1. Identidade, login, sessão e autorização por perfil.
2. Catálogo público e administração de títulos, categorias e exemplares individuais.
3. Solicitação de empréstimo, retirada e devolução.
4. Reserva por título em fila de ordem de solicitação, com janela de retirada e expiração.
5. Registro de danos/perdas e histórico operacional relevante.

## Regras globais aprovadas

- Uma obra/título pode ter várias categorias e vários exemplares físicos.
- A reserva é por título; o empréstimo confirmado é de um exemplar físico.
- O estudante solicita; o bibliotecário confirma a retirada física e a devolução.
- O prazo do empréstimo é de 14 dias corridos e começa no instante em que a retirada física é registrada.
- Limite de um empréstimo ativo por estudante.
- Empréstimo vencido e não devolvido bloqueia novos empréstimos e reservas.
- Reservas são atendidas por FIFO; cada estudante pode ter uma reserva ativa por título.
- Não se permite reservar título que o estudante já possui em empréstimo ativo não atrasado.
- Quando uma reserva for disponibilizada para retirada, a pessoa tem 2 dias. O instante/canal do aviso, calendário da biblioteca, fins de semana, feriados e fuso ainda precisam ser fechados.
- Exemplar danificado ou perdido fica indisponível e recebe observação.

## Arquitetura e decisões de tecnologia

- Backend e fonte de dados: Xano, integrado por API REST e XanoScript versionado quando exigido pela Change.
- Frontend: Reflex é a tecnologia adotada e exclusiva. Qualquer outra tecnologia de frontend exige uma mudança arquitetural aprovada.
- Pendências obrigatórias para liberar funcionalidades e deploy: a adoção do Reflex não autoriza implementar funcionalidades de produto nem fazer deploy até que as duas mitigações estejam concluídas:
  1. Implementar o indicador visual `:focus-visible` na busca e verificar seu funcionamento antes de iniciar funcionalidades de produto.
  2. Escolher e validar o ambiente acadêmico antes de qualquer deploy; manter segredos somente no backend e inspecionar os logs antes do deploy.
- Especificação e histórico: OpenSpec com schema `spec-driven`; Git versiona código, documentação, changes ativas, specs consolidadas e arquivo.
- Idioma do produto e documentação: português do Brasil.

## Reconstrução e fonte de verdade

Esta pasta (`biblioteca-mais-nova`) é o projeto novo. A implementação anterior em `biblioteca-nova` serve apenas como referência e não define o domínio, os schemas, endpoints ou permissões deste projeto. O usuário autorizou excluir e reconstruir as tabelas antigas do workspace Xano selecionado para a biblioteca; operações remotas só podem ocorrer em Apply, dentro de Change aprovada que identifique claramente o destino e o escopo.

O modelo conceitual está em `docs/domain-model.md`. Requisitos comportamentais detalhados pertencem às specs de cada Change e, após verificação e Archive, às specs consolidadas em `openspec/specs/`.

## Questões ainda abertas

- Dados mínimos de cadastro escolar e prevenção de duplicidade/contas indevidas.
- Provisionamento inicial e promoção de bibliotecários.
- Se pedidos sem exemplar disponível entram em fila de empréstimo ou exigem reserva.
- Evento/canal que inicia a janela de retirada de dois dias e regras do calendário local.
- Cancelamento de reservas, renovação, multas, limites de reservas e regularização de perdas.
- Metadados bibliográficos e identificador individual do exemplar.
- Validação do ambiente de deploy e escolha do workspace/branch Xano.
