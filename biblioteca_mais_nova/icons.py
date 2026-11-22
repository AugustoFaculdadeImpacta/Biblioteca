"""Dicionário de ícones, rótulos e categorias visuais das ações do site."""

from dataclasses import dataclass
from typing import Literal

import reflex as rx


TipoAcao = Literal["confirmar", "perigo", "navegar", "atencao"]


@dataclass(frozen=True)
class Icone:
    emoji: str
    rotulo: str
    tipo: TipoAcao


ACOES: dict[str, Icone] = {
    "marca": Icone("🏫", "Biblioteca escolar", "navegar"),
    "catalogo": Icone("📚", "Catálogo", "navegar"),
    "minhas_reservas": Icone("🙋", "Minhas reservas", "navegar"),
    "acervo": Icone("🗂️", "Acervo", "navegar"),
    "pedidos_reserva": Icone("📬", "Pedidos de reserva", "navegar"),
    "contas": Icone("👥", "Contas", "navegar"),
    "regras": Icone("⚙️", "Regras", "navegar"),
    "perfil": Icone("👤", "Perfil", "navegar"),
    "acessibilidade": Icone("♿", "Acessibilidade", "navegar"),
    "entrar": Icone("🔑", "Entrar", "navegar"),
    "cadastrar": Icone("✍️", "Cadastrar-se", "confirmar"),
    "sair": Icone("🚪", "Sair", "navegar"),
    "buscar": Icone("🔎", "Buscar", "navegar"),
    "reservar": Icone("📮", "Quero reservar", "confirmar"),
    "cancelar_reserva": Icone("🛑", "Cancelar reserva", "perigo"),
    "aceitar": Icone("🤝", "Aceitar", "confirmar"),
    "recusar": Icone("🚫", "Recusar", "perigo"),
    "emprestar": Icone("📤", "Emprestar", "confirmar"),
    "devolver": Icone("📥", "Devolver", "confirmar"),
    "editar": Icone("✏️", "Editar", "navegar"),
    "salvar": Icone("💾", "Salvar", "confirmar"),
    "novo_titulo": Icone("➕", "Novo título", "confirmar"),
    "exemplares": Icone("📦", "Exemplares", "navegar"),
    "desativar": Icone("⛔", "Desativar", "perigo"),
    "reativar": Icone("♻️", "Reativar", "confirmar"),
    "voltar": Icone("⬅️", "Voltar", "navegar"),
    "confirmar_desativacao": Icone("✅", "Sim, desativar", "confirmar"),
    "nao_confirmar": Icone("❌", "Não", "perigo"),
    "restaurar_visao": Icone("↩️", "Voltar à visão de admin", "navegar"),
    "diminuir_fonte": Icone("🔡", "Diminuir fonte", "atencao"),
    "fonte_padrao": Icone("🔠", "Tamanho padrão", "navegar"),
    "aumentar_fonte": Icone("🔤", "Aumentar fonte", "atencao"),
    "alto_contraste": Icone("🌗", "Alto contraste", "atencao"),
    "reduzir_movimento": Icone("🎞️", "Reduzir movimento", "atencao"),
    "tema": Icone("🌓", "Modo escuro", "atencao"),
    "menu_navegacao": Icone("🧭", "Abrir menu", "navegar"),
    "administrador": Icone("👑", "Administrador", "navegar"),
    "bibliotecario": Icone("🧑‍🏫", "Bibliotecário", "navegar"),
    "estudante": Icone("🎓", "Estudante", "navegar"),
    "pular_conteudo": Icone("⏭️", "Pular conteúdo", "navegar"),
    "detalhes": Icone("🔍", "Ver detalhes", "navegar"),
    "atualizar_acervo": Icone("🔄", "Atualizar acervo", "navegar"),
    "mostrar_mais": Icone("⏬", "Mostrar mais", "navegar"),
    "retomar_categorias": Icone("🔗", "Retomar vínculos", "atencao"),
    "criar_exemplar": Icone("🧱", "Criar exemplar", "confirmar"),
    "novo_cadastro": Icone("🆕", "Novo cadastro", "confirmar"),
    "fechar_cadastro": Icone("🧹", "Fechar cadastro", "atencao"),
    "atualizar_lista": Icone("🔃", "Atualizar lista", "navegar"),
    "liberar_acervo": Icone("🧐", "Liberar lista", "atencao"),
    "cadastrar_bibliotecario": Icone("🧑‍💼", "Criar conta", "confirmar"),
    "buscar_estudante": Icone("🧑‍🎓", "Buscar estudante", "navegar"),
    "registrar_reserva": Icone("🧾", "Registrar reserva", "confirmar"),
    "liberar_fila": Icone("🕵️", "Liberar tentativa", "atencao"),
    "retirada": Icone("🪪", "Registrar retirada", "confirmar"),
    "oferecer_reserva": Icone("📣", "Oferecer reserva", "confirmar"),
    "atualizar_circulacao": Icone("📲", "Atualizar circulação", "navegar"),
    "emprestimos": Icone("📕", "Empréstimos", "navegar"),
    "confirmar_fila": Icone("🗳️", "Conferir fila", "atencao"),
}


SELOS: dict[str, Icone] = {
    "disponivel": Icone("🟢", "Disponível", "confirmar"),
    "indisponivel": Icone("🔴", "Indisponível", "perigo"),
    "aguardando": Icone("⏳", "Aguardando", "atencao"),
    "aprovada": Icone("✅", "Aprovada", "confirmar"),
    "emprestado": Icone("📖", "Emprestado", "navegar"),
    "atraso": Icone("⚠️", "Em atraso", "atencao"),
}


def _obter_icone(dicionario: dict[str, Icone], chave: str) -> Icone:
    try:
        return dicionario[chave]
    except KeyError as erro:
        raise ValueError(f"Ícone não cadastrado: {chave}") from erro


def conteudo_acao(
    chave: str,
    rotulo: object | None = None,
    complemento: rx.Component | None = None,
) -> rx.Component:
    acao = _obter_icone(ACOES, chave)
    texto = acao.rotulo if rotulo is None else rotulo
    atributos_rotulo = {"data_action_label": "true"}
    atributos_emoji = {}
    if chave == "tema":
        atributos_rotulo["data_appearance_theme_label"] = "true"
        atributos_emoji["data_appearance_theme_emoji"] = "true"
    partes = [
        rx.el.span(
            acao.emoji,
            aria_hidden="true",
            class_name="emoji-acao",
            **atributos_emoji,
        ),
        rx.el.span(texto, class_name="rotulo-acao", **atributos_rotulo),
    ]
    if complemento is not None:
        partes.append(complemento)
    return rx.fragment(*partes)


def atributos_acao(
    chave: str,
    rotulo: object | None = None,
) -> dict[str, object]:
    acao = _obter_icone(ACOES, chave)
    texto = acao.rotulo if rotulo is None else rotulo
    return {
        "title": texto,
        "aria_label": texto,
        "data_action_type": acao.tipo,
    }


def conteudo_selo(
    chave: str,
    rotulo: str | None = None,
) -> rx.Component:
    selo = _obter_icone(SELOS, chave)
    return rx.fragment(
        rx.el.span(selo.emoji, aria_hidden="true", class_name="emoji-selo"),
        rx.el.span(selo.rotulo if rotulo is None else rotulo),
    )
