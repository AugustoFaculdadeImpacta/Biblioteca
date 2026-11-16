# Spec Delta

## Purpose

Descrever os percursos integrados que conectam identidade, catálogo, circulação e acervo para que estudante e bibliotecário consigam concluir as tarefas prioritárias com resultados claros e sem alterar regras de domínio existentes.

## ADDED Requirements

### Requirement: Estudante percorre cadastro, catálogo e solicitação
A interface MUST permitir que estudante conclua o percurso de entrada, descubra um título e acompanhe uma solicitação ou reserva usando os resultados confirmados pelos serviços.

#### Scenario: Estudante solicita título disponível
- **WHEN** visitante conclui o cadastro ou estudante entra, abre um título disponível e solicita empréstimo
- **THEN** a interface mantém a sessão conforme o perfil retornado, mostra a confirmação somente após resposta de sucesso e permite consultar o estado na área pessoal

#### Scenario: Estudante solicita título indisponível
- **WHEN** estudante autenticado abre título sem exemplar disponível e escolhe solicitar reserva
- **THEN** a interface apresenta o resultado confirmado da solicitação e permite acompanhar a reserva sem inventar posição ou prazo

### Requirement: Bibliotecário percorre cadastro e circulação
A interface MUST permitir que bibliotecário percorra as tarefas operacionais existentes sem perder o resultado confirmado de cada etapa.

#### Scenario: Bibliotecário cadastra título e exemplares
- **WHEN** bibliotecário autenticado informa os dados obrigatórios, associa categorias existentes e cria exemplares
- **THEN** a interface apresenta identificadores e códigos de tombo retornados e permite conferir o título no acervo

#### Scenario: Bibliotecário processa circulação
- **WHEN** bibliotecário autenticado confirma retirada ou devolução por uma ação disponível no painel
- **THEN** a interface atualiza a lista com o estado retornado e não apresenta como concluída uma ação recusada

### Requirement: Jornadas apresentam erros de integração com segurança
A interface MUST distinguir falhas de entrada, autenticação/autorização, conflito, servidor e comunicação sem expor conteúdo interno nem simular sucesso.

#### Scenario: Sessão expirada ou perfil sem permissão
- **WHEN** uma operação da jornada recebe recusa de autenticação ou autorização
- **THEN** a interface orienta a pessoa em português, não apresenta sucesso e não expõe corpo técnico da resposta

#### Scenario: Falha de comunicação após uma escrita
- **WHEN** o resultado de uma escrita fica incerto por falha de transporte
- **THEN** a interface informa que é necessário conferir o estado antes de repetir e não repete a escrita automaticamente

#### Scenario: Dados inválidos ou resposta incompatível
- **WHEN** formulário contém dados inválidos ou o serviço retorna uma resposta incompatível com o contrato
- **THEN** a interface informa o problema com segurança e não avança a jornada como se a operação tivesse sido concluída
