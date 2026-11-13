# Modelo conceitual de domínio — Biblioteca escolar

Este modelo apresenta conceitos e relações do domínio, não tabelas Xano nem nomes físicos de campos. A persistência deve evoluir junto das Changes funcionais aprovadas.

## Conceitos

### Conta e perfil
Identidade de acesso com dados de identificação escolar, credenciais/sessão, papel de estudante, bibliotecário ou administrador e situação ativa. O autocadastro cria estudante. O administrador tem as permissões do bibliotecário e gere contas bibliotecárias; somente o dono do workspace provisiona a primeira conta administradora.

### Título
Obra bibliográfica descrita por metadados como título, autoria e edição/publicação. Um título pode ter várias categorias e possuir vários exemplares físicos.

### Categoria
Classificação do acervo. A relação entre títulos e categorias é muitos-para-muitos.

### Exemplar
Unidade física individual de um título. Possui condição e disponibilidade operacional; pode estar disponível, emprestado, reservado para retirada ou indisponível por dano/perda. A identificação individual e o fluxo de recuperação de um exemplar perdido precisam ser detalhados.

### Solicitação de empréstimo
Intenção de um estudante de obter um exemplar. Não inicia prazo nem representa retirada concluída. Deve ser confirmada pela biblioteca conforme disponibilidade e elegibilidade.

### Empréstimo
Registro da retirada física de um exemplar por um estudante. Guarda o instante de retirada, vencimento, estado e devolução. O prazo de 14 dias corridos inicia quando o bibliotecário registra a retirada; cada estudante pode ter até três empréstimos ativos, sem repetir título enquanto mantiver um exemplar daquele título.

### Reserva
Pedido de um estudante para um título, ordenado por instante de solicitação numa fila FIFO. Só pode haver uma reserva ativa por estudante por título. Reserva não aponta para exemplar específico até a biblioteca disponibilizar um exemplar para atendimento.

### Oportunidade de retirada
Janela de dois dias associada à reserva que chegou ao topo e recebeu exemplar disponível. Guarda o instante de disponibilização/aviso, prazo final e resultado (retirada, expiração ou cancelamento). O evento de aviso e as regras de calendário/fuso ainda precisam ser definidos.

### Registro de condição
Histórico de dano ou perda ligado a exemplar, com observação, data e responsável. Um exemplar com condição de dano/perda fica indisponível até regularização administrativa.

## Relações

- Conta estudante 1:N empréstimos históricos; no máximo três ativos simultaneamente e sem dois exemplares ativos do mesmo título.
- Conta estudante 1:N reservas; no máximo uma reserva ativa por título.
- Conta bibliotecário 1:N registros de operações administrativas.
- Título N:M categoria.
- Título 1:N exemplar.
- Exemplar 1:N empréstimos ao longo do tempo; no máximo um ativo.
- Título 1:N reservas, ordenadas pela solicitação.
- Reserva 0:1 oportunidade ativa de retirada; oportunidades anteriores podem permanecer no histórico.
- Exemplar 1:N registros de condição ao longo do tempo.

## Invariantes conceituais

- Disponibilidade é derivada dos exemplares elegíveis, não de uma quantidade agregada no título.
- Prazo só começa após retirada física registrada.
- Atraso existe quando o vencimento passou e não há devolução registrada.
- Qualquer atraso bloqueia novas solicitações de empréstimo e reservas.
- O limite global é de três empréstimos ativos por estudante; empréstimo de outro título, abaixo do limite, não bloqueia nova operação.
- Reserva e confirmação de empréstimo não podem prometer o mesmo exemplar a duas pessoas; backend deve revalidar elegibilidade e disponibilidade de forma concorrente-segura.
- Empréstimo ativo não atrasado do próprio título impede reserva desse título.
- Dano/perda mantém o exemplar indisponível e exige observação.

## Alternativas ainda não decididas

- Pedido de empréstimo sem exemplar disponível: fila própria de empréstimo ou reserva formal.
- Representação dos dados escolares, duplicidade e ativação de contas.
- Identificador individual (etiqueta, código de barras ou outro) do exemplar.
- Estados intermediários de solicitação e reserva, cancelamento, renovação, multas e regularização de perda.
