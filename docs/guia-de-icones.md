# Guia de ícones

Cada ação tem um emoji exclusivo e um rótulo curto. O emoji fica em um `<span aria-hidden="true">`; o botão recebe `title`, `aria-label` e uma categoria visual. Os selos de estado têm um dicionário separado.

| Ação | Emoji | Texto |
|---|---|---|
| Marca | 🏫 | Biblioteca escolar |
| Catálogo | 📚 | Catálogo |
| Minhas reservas | 🙋 | Minhas reservas |
| Acervo | 🗂️ | Acervo |
| Pedidos de reserva | 📬 | Pedidos de reserva |
| Contas | 👥 | Contas |
| Regras | ⚙️ | Regras |
| Perfil | 👤 | Perfil |
| Acessibilidade | ♿ | Acessibilidade |
| Entrar | 🔑 | Entrar |
| Cadastrar-se | ✍️ | Cadastrar-se |
| Sair | 🚪 | Sair |
| Buscar | 🔎 | Buscar |
| Reservar título | 📮 | Quero reservar |
| Cancelar reserva | 🛑 | Cancelar reserva |
| Aceitar | 🤝 | Aceitar |
| Recusar | 🚫 | Recusar |
| Emprestar | 📤 | Emprestar |
| Devolver | 📥 | Devolver |
| Editar | ✏️ | Editar |
| Salvar | 💾 | Salvar |
| Novo título | ➕ | Novo título |
| Exemplares | 📦 | Exemplares |
| Desativar | ⛔ | Desativar |
| Reativar | ♻️ | Reativar |
| Voltar | ⬅️ | Voltar |
| Confirmar desativação | ✅ | Sim, desativar |
| Cancelar confirmação | ❌ | Não |
| Restaurar visão de admin | ↩️ | Voltar à visão de admin |
| Diminuir fonte | 🔡 | Diminuir fonte |
| Tamanho padrão | 🔠 | Tamanho padrão |
| Aumentar fonte | 🔤 | Aumentar fonte |
| Alto contraste | 🌗 | Alto contraste |
| Reduzir movimento | 🎞️ | Reduzir movimento |
| Tema | 🌓 | Modo escuro ou Modo claro |
| Abrir/fechar navegação | 🧭 | Abrir menu ou Fechar menu |
| Administrador | 👑 | Administrador |
| Bibliotecário | 🧑‍🏫 | Bibliotecário |
| Estudante | 🎓 | Estudante |
| Pular conteúdo | ⏭️ | Pular conteúdo |
| Ver detalhes | 🔍 | Ver detalhes |
| Atualizar acervo | 🔄 | Atualizar acervo |
| Mostrar mais | ⏬ | Mostrar mais |
| Retomar vínculos | 🔗 | Retomar vínculos |
| Criar exemplar | 🧱 | Criar exemplar |
| Novo cadastro | 🆕 | Novo cadastro |
| Fechar cadastro | 🧹 | Fechar cadastro |
| Atualizar lista | 🔃 | Atualizar lista |
| Liberar lista | 🧐 | Liberar lista |
| Criar conta bibliotecária | 🧑‍💼 | Criar conta |
| Buscar estudante | 🧑‍🎓 | Buscar estudante |
| Registrar reserva | 🧾 | Registrar reserva |
| Liberar tentativa | 🕵️ | Liberar tentativa |
| Registrar retirada | 🪪 | Registrar retirada |
| Oferecer reserva | 📣 | Oferecer reserva |
| Atualizar circulação | 📲 | Atualizar circulação |
| Empréstimos | 📕 | Empréstimos |
| Conferir fila | 🗳️ | Conferir fila |

| Selo | Emoji | Texto |
|---|---|---|
| Disponível | 🟢 | Disponível |
| Indisponível | 🔴 | Indisponível |
| Aguardando | ⏳ | Aguardando |
| Aprovada | ✅ | Aprovada |
| Emprestado | 📖 | Emprestado |
| Em atraso | ⚠️ | Em atraso |

## Cores e confirmações

- Verde identifica confirmação; vermelho, perigo; azul, navegação; âmbar, atenção.
- A categoria visual é aplicada pelo atributo `data-action-type`, com tokens próprios para tema claro e escuro.
- A ação destrutiva de desativar pede confirmação em linha: **✅ Sim, desativar** ou **❌ Não**.
- O botão de restauração administrativa mantém o texto exigido pelo fluxo (**Voltar à visão de admin**), embora seja mais longo que os demais rótulos.
- Alguns emojis foram escolhidos diferentes da lista inicial para manter exclusividade: **📮 Quero reservar** não repete **🙋 Minhas reservas**; **🤝 Aceitar** deixa **✅** livre para confirmar a desativação; **🛑 Cancelar reserva** deixa **❌ Não** exclusivo da confirmação. Os selos são estados, não ações, e têm dicionário separado.
- Os controles sem um pictograma de ação claro usam emojis de uso comum; não carregam scripts ou imagens externos.
