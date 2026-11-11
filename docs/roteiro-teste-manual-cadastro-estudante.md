# Roteiro de teste manual: cadastro de estudante

Este roteiro cria uma conta persistente. Execute-o somente em um ambiente
acadêmico não produtivo, depois de confirmar que `XANO_API_BASE_URL` aponta
para o destino correto. Não use dados pessoais reais.

## Pré-requisitos

1. Confirme com a pessoa responsável pelo ambiente que o destino é não
   produtivo.
2. Configure `XANO_API_BASE_URL` no ambiente do backend Reflex; não inclua
   tokens, senhas ou URLs com credenciais no repositório.
3. Inicie a aplicação com `reflex run` e abra `/cadastro`.
4. Escolha um endereço de e-mail de teste exclusivo e controlado por você.

## Cadastro válido

1. Informe nome, e-mail de teste ainda não cadastrado e senha de teste.
2. Envie o formulário.
3. Confirme a mensagem de sucesso e o estado de sessão autenticada.
4. Confirme que o perfil é estudante e que não foi possível escolher outro
   perfil no formulário.

## E-mail duplicado

1. Reenvie o cadastro usando o mesmo e-mail, inclusive com espaços externos
   e letras maiúsculas.
2. Confirme a mensagem de e-mail já cadastrado.
3. Confirme que a falha não cria nem autentica uma segunda conta.

## Limites e limpeza

- Os testes automatizados usam somente transporte HTTP simulado; nenhum deles
  grava no Xano live.
- A API documentada não define endpoint para excluir a conta de teste. Não
  presuma que ela pode ser removida automaticamente; combine previamente com
  o responsável pelo ambiente o procedimento de limpeza.
- Antes de qualquer teste, verifique novamente o ambiente, pois uma submissão
  de cadastro é uma operação de escrita persistente.
