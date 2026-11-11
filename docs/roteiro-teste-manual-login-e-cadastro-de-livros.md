# Roteiro manual: login e cadastro de acervo

Este roteiro deve ser executado somente em um ambiente acadêmico não produtivo,
com uma conta de bibliotecário de teste. Os testes automatizados usam
`httpx.MockTransport` e não criam dados no Xano.

## Preparação

1. Confirme no painel/ambiente do Xano que o destino é o workspace acadêmico de
   desenvolvimento ou sandbox, nunca produção.
2. Configure `XANO_API_BASE_URL` somente no ambiente backend local ou em um
   `.env` local não versionado. Confira a origem antes de iniciar a aplicação;
   não registre tokens, senhas nem cabeçalhos em capturas ou logs.
3. Na raiz do projeto, inicie:

   ```powershell
   .\.venv\Scripts\reflex.exe run
   ```

4. Abra `http://localhost:3000/login`.

## Verificação do login

1. Entre com uma conta de bibliotecário de teste do ambiente confirmado.
2. Confirme o redirecionamento para `/admin/acervo`.
3. Em uma sessão separada, entre com perfil estudante e confirme o
   redirecionamento à página inicial.
4. Como estudante e como visitante, abra diretamente
   `http://localhost:3000/admin/acervo`; confirme que a tela retorna ao login
   ou à página inicial e que nenhuma operação de escrita é enviada.

## Cadastro de título, categorias e exemplares

1. Na área de acervo como bibliotecário, confirme que as categorias existentes
   são carregadas do catálogo.
2. Cadastre um título de teste usando título e autores; preencha ISBN, editora,
   edição, ano ou descrição somente quando desejar.
3. Marque uma ou mais categorias existentes e envie uma vez. Confirme que a
   interface apresenta o sucesso apenas para associações confirmadas.
4. Use **Criar um exemplar** uma vez para cada unidade desejada. Registre os
   códigos de tombo retornados pelo servidor e confirme-os no ambiente
   acadêmico.
5. Se o navegador ou a rede falhar durante título ou exemplar, não reenvie a
   etapa automaticamente. Confira o acervo no Xano antes de iniciar outro
   cadastro. Se uma associação ficar pendente, use **Retomar associações de
   categorias** somente após a interface reconciliar a situação.

Ao terminar, confira o ambiente selecionado e remova os dados de teste segundo
os procedimentos acadêmicos locais. Não use dados pessoais reais.
