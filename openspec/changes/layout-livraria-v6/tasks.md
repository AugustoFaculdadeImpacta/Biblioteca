# Tasks

## 1. Registrar a versão v6

- [x] 1.1 Criar os artefatos OpenSpec da Change com escopo, cenários e tarefas.
- [x] 1.2 Preservar o layout estável v5 e identificar os componentes que ainda divergem da referência.

## 2. Completar o seed

- [ ] 2.1 Validar os 30 títulos reais, ISBN-13, categorias e descrições próprias.
- [x] 2.2 Confirmar resolução de `capa_url`, índice ISBN e fallback.
- [x] 2.3 Executar dry-run sem escrita e registrar o resultado.

## 3. Reescrever o layout

- [x] 3.1 Reescrever o cabeçalho único por perfil e tema.
- [ ] 3.2 Aplicar a hierarquia de home, catálogo e detalhe.
- [ ] 3.3 Aplicar Reservas, Acervo e Contas sem sobreposição.
- [ ] 3.4 Atualizar CSS do login e cadastro.

## 4. Robô e fluxos

- [x] 4.1 Criar o script local de layout no Edge por DTP.
- [ ] 4.2 Cobrir as nove rotas, quatro perfis, três larguras e dois temas.
- [ ] 4.3 Cobrir os fluxos funcionais da API demo.

## 5. Verificação

- [ ] 5.1 Corrigir violações em até seis iterações.
- [x] 5.2 Executar compile e pytest sequencialmente.
- [x] 5.3 Gerar relatório final e evidências.

## 6. Fechar mudanças abertas

- [x] 6.1 Concluir a tarefa 1.3 da Change de execução Windows com script sequencial.
- [x] 6.2 Preparar checklist do Xano e arquivar a validação remota sem publicação.
- [x] 6.3 Validar specs estritas, gerar relatório, commitar e publicar no Git.

## 7. Corrigir a home e documentar o diagnóstico

- [ ] 7.1 Auditar e registrar em `docs/diagnostico-home.md` todas as regras de hero, home, estatísticas, pílulas e seções, destacando altura, overflow, posicionamento, transformações e margens.
- [ ] 7.2 Remover propriedades de layout que comprimem ou sobrepõem hero, estatísticas, pílulas e seções; aplicar o contrato de grid e fluxo responsivo.
- [ ] 7.3 Reorganizar a home com banner e busca, faixa de estatísticas, resumo autenticado, estante, novidades, categorias e três passos de reserva.
- [ ] 7.4 Atualizar os testes para provar ausência de altura fixa/overflow de corte e presença da hierarquia de conteúdo exigida.

## 8. Auditar demais páginas e estilos

- [ ] 8.1 Varrer todos os estilos e componentes do app para alturas fixas, cortes, posicionamento, transformações e margens negativas fora das exceções.
- [ ] 8.2 Corrigir os defeitos encontrados em catálogo, detalhe, reservas, acervo, contas, login e cadastro.
- [ ] 8.3 Adicionar testes CSS cobrindo classes e contêineres de todas as páginas principais.

## 9. Robustecer e executar o robô visual

- [ ] 9.1 Reescrever o robô para persistir cada combinação, limitar duração e encerrar apenas o Edge próprio.
- [ ] 9.2 Executar a matriz inicial visitante em 5 rotas, 2 larguras e 2 temas, e os perfis autenticados nas rotas administrativas e pessoais especificadas.
- [ ] 9.3 Corrigir violações e repetir até quatro iterações, registrando resultado e captura de cada combinação.
- [ ] 9.4 Se Edge não funcionar, tentar uma vez o navegador integrado; na ausência de evidência, registrar explicitamente não verificado visualmente.

## 10. Fechamento da continuação

- [ ] 10.1 Atualizar relatório com tabela completa do último passe e itens não verificados.
- [ ] 10.2 Executar `scripts/verificar.ps1` sequencialmente e `openspec.cmd validate --specs --strict`.
- [ ] 10.3 Comitar cada tarefa concluída e publicar a branch `trabalho-autopilot`.
