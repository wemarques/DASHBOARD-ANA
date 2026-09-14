"""
Gerenciar Itens — o que entra no acerto: cadastrar, corrigir, reajustar e excluir.

A aba responde, nesta ordem:
  1. Quais itens compõem o acerto, separados entre os que somam ao que a Ana
     recebe e os que abatem, com a faixa de meses em que cada um entra na conta.
  2. Como corrigir um item sem estragar o que já foi acertado.

Regras de segurança:
  - Editar preserva antecipações, reajustes e contrato. (A versão anterior
    regravava o item só com nome/valor/período e apagava as antecipações.)
  - Com parcelas antecipadas, valor e período ficam travados.
  - Toda mudança que altera o acerto de meses JÁ QUITADOS lista esses meses e
    exige confirmação.
  - Reajuste de item contínuo vale a partir de um mês; o passado não muda.
  - Toda gravação guarda o estado anterior para "Desfazer".

Regras de dados em itens_modelo.py (testado em test_itens_modelo.py).
"""

import copy
import html

import streamlit as st

import itens_modelo as modelo
from detalhamento_mensal import _lista
from gestao_executiva import _brl, _mes_de_hoje

NOVO = "__novo__"
TIPOS = ["credito", "debito"]
COLUNAS_LINHA = [5, 1.6, 1]  # item e faixa | valor | botão

# Nunca escreva o caractere "menor que" dentro do CSS (nem em comentário): o
# sanitizador do st.html descarta o bloco de estilo inteiro.
_CSS = """
<style>
.itm { font-family: 'DM Sans', -apple-system, 'Segoe UI', sans-serif; color: #0A1628; }
.itm h2.itm-titulo, .itm h3.itm-sub {
  font-family: 'Playfair Display', Georgia, serif !important; font-weight: 600 !important;
  color: #0A1628 !important; letter-spacing: -0.01em !important; padding: 0 !important; }
.itm h2.itm-titulo { font-size: 1.5rem !important; line-height: 1.25 !important; margin: 0 0 .25rem !important; }
.itm h3.itm-sub { font-size: 1.125rem !important; line-height: 1.3 !important; margin: 0 0 .25rem !important; }
.itm .itm-texto { font-size: .9375rem; line-height: 1.5; color: #374151; max-width: 62ch; }
.itm .itm-nota { font-size: .8125rem; line-height: 1.5; color: #5F6673; max-width: 62ch; }
.itm .itm-rotulo { font-size: .9375rem; font-weight: 600; color: #0A1628; margin-top: .5rem; }

.itm .itm-legenda { display: flex; flex-wrap: wrap; gap: .375rem 1.125rem; list-style: none; margin: 1.5rem 0 0; padding: 0; font-size: .8125rem; color: #5F6673; }
.itm .itm-legenda li { display: inline-flex; align-items: center; gap: .45rem; margin: 0; }
.itm .itm-chave { display: inline-block; width: 16px; height: 8px; border-radius: 2px; }
.itm .itm-chave--passado { background: #1C2B4A; }
.itm .itm-chave--futuro { background: #7D8796; }
.itm .itm-chave--marco { width: 3px; height: 14px; border-radius: 1px; background: #C9A96E; }
.itm .itm-chave--hoje { width: 2px; height: 14px; border-radius: 0; background: #0A1628; }
.itm .itm-escala { display: grid; margin-top: .875rem; font-size: .75rem; color: #5F6673; font-variant-numeric: tabular-nums; }
.itm .itm-escala span { padding-left: 4px; border-left: 1px solid #D8D2C8; }

.itm .itm-grupo { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: .25rem 1rem; margin-top: 1.75rem; padding-bottom: .5rem; border-bottom: 1px solid #0A1628; }
.itm .itm-grupo-nome { font-size: 1rem; font-weight: 600; color: #0A1628; }
.itm .itm-grupo-total { font-size: .8125rem; color: #5F6673; font-variant-numeric: tabular-nums; }

[class*="st-key-item_"] { padding: .875rem 0 .875rem; border-bottom: 1px solid #E5E0D8; }
.itm .itm-nome { font-size: 1rem; font-weight: 500; color: #0A1628; line-height: 1.35; }
.itm .itm-detalhe { font-size: .8125rem; line-height: 1.45; color: #5F6673; margin-top: .125rem; }
.itm .itm-trilha { display: grid; height: 8px; margin: .75rem 0 .125rem; border-radius: 4px; background: #ECE8E1; }
.itm .itm-faixa { grid-row: 1; height: 8px; }
.itm .itm-faixa--passado { background: #1C2B4A; }
.itm .itm-faixa--futuro { background: #7D8796; }
.itm .itm-ano { grid-row: 1; justify-self: start; width: 2px; height: 8px; background: #F8F6F3; }
.itm .itm-marco { grid-row: 1; justify-self: start; align-self: center; width: 3px; height: 16px; border-radius: 1px; background: #C9A96E; box-shadow: 0 0 0 1px #F8F6F3; }
.itm .itm-hoje { grid-row: 1; justify-self: center; align-self: center; width: 2px; height: 18px; background: #0A1628; box-shadow: 0 0 0 1.5px #F8F6F3; }

.itm .itm-valor { font-size: 1rem; font-weight: 500; color: #0A1628; text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.itm .itm-valor-nota { font-size: .8125rem; color: #5F6673; text-align: right; }
@media (max-width: 640px) { .itm .itm-valor, .itm .itm-valor-nota { text-align: left; } }

[class*="st-key-painel_"] { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.25rem 1.5rem 1.375rem; margin-top: .5rem; }
@media (max-width: 560px) { [class*="st-key-painel_"] { padding: 1rem 1rem 1.125rem; } }
.itm .itm-aviso { background: #FDF1DC; color: #6B3A04; border-radius: 10px; padding: .625rem .875rem; font-size: .875rem; line-height: 1.5; }
.itm .itm-erro { background: #FBE9E6; color: #8A2418; border-radius: 10px; padding: .625rem .875rem; font-size: .875rem; line-height: 1.5; }
.itm .itm-erro ul { margin: 0; padding-left: 1.1rem; }
.itm .itm-erro li { margin: 0; color: #8A2418; }
.itm .itm-travado { background: #F4F2EE; color: #374151; border-radius: 10px; padding: .625rem .875rem; font-size: .875rem; line-height: 1.5; }
.itm .itm-vig { display: flex; flex-wrap: wrap; gap: .25rem 1.25rem; align-items: baseline; font-size: .9375rem; }
.itm .itm-vig-periodo { color: #374151; min-width: 9.5rem; }
.itm .itm-vig-valor { color: #0A1628; font-weight: 500; font-variant-numeric: tabular-nums; }
.itm .itm-divisor { border-top: 1px solid #E5E0D8; margin: 1.25rem 0 1rem; }
.itm .itm-vazio { font-size: .9375rem; color: #5F6673; margin-top: 1.5rem; }

/* Botões desta aba: sem hover vermelho (reservado a excluir) e terciário como link. */
.st-key-itens_cabeca .stButton > button[kind="secondary"]:hover,
[class*="st-key-painel_"] .stButton > button[kind="secondary"]:hover,
[class*="st-key-item_"] .stButton > button[kind="secondary"]:hover {
  border-color: #1C2B4A !important; color: #1C2B4A !important; background: #F4F2EE !important; }
.st-key-itens_cabeca .stButton > button[data-testid="stBaseButton-tertiary"],
[class*="st-key-item_"] .stButton > button[data-testid="stBaseButton-tertiary"] {
  background: transparent !important; color: #1C2B4A !important; border: 0 !important; box-shadow: none !important;
  text-decoration: underline; text-underline-offset: .2em; }
/* Desabilitado precisa parecer desabilitado: o CSS global pinta todo botão de marinho. */
.st-key-itens_cabeca .stButton > button:disabled,
[class*="st-key-painel_"] .stButton > button:disabled,
[class*="st-key-item_"] .stButton > button:disabled {
  background: #ECE8E1 !important; color: #6B7280 !important; border: 1px solid #E0DBD2 !important;
  box-shadow: none !important; cursor: not-allowed !important; }
[class*="st-key-painel_"] .stButton > button:disabled :is(span, p, div) { color: inherit !important; }
[class*="st-key-painel_"] [data-testid="stButtonGroup"] button:not([data-testid$="Active"]) {
  background: #FFFFFF !important; border-color: #AEB5C0 !important; color: #0A1628 !important; }
[class*="st-key-painel_"] [data-testid="stButtonGroup"] button[data-testid$="Active"] {
  background: #1C2B4A !important; border-color: #1C2B4A !important; color: #FFFFFF !important; }
[class*="st-key-painel_"] [data-testid="stButtonGroup"] button :is(span, p, div) { color: inherit !important; }
[class*="st-key-painel_"] [data-testid="stPopover"] button {
  background: #FFFFFF !important; color: #9A2B1E !important; border: 1px solid #E8C4BE !important; }
[class*="st-key-painel_"] [data-testid="stPopover"] button :is(span, p, div) { color: inherit !important; }
[class*="st-key-excluir_ok_"] button, [class*="st-key-remover_ok_"] button {
  background: #9A2B1E !important; color: #FFFFFF !important; border: 0 !important; }
[class*="st-key-excluir_ok_"] button :is(span, p, div), [class*="st-key-remover_ok_"] button :is(span, p, div) { color: inherit !important; }
/* No celular as colunas empilham: as duas vazias da escala só abririam um vão. */
@media (max-width: 640px) { .st-key-itens_escala [data-testid="stColumn"]:not(:first-child) { display: none; } }
</style>
"""


# ==========================================================================
# Estado e gravação
# ==========================================================================
def _estado():
    st.session_state.setdefault("itens_editando", None)
    st.session_state.setdefault("itens_versao", 0)
    st.session_state.setdefault("itens_undo", None)
    st.session_state.setdefault("itens_undo_label", "")


def _versao():
    return st.session_state.itens_versao


def _nova_versao():
    # Chaves versionadas: apagar a chave não reseta o widget no navegador.
    st.session_state.itens_versao += 1


def _pref(ident):
    return f"it_{_chave(ident)}_v{_versao()}"


def _chave(ident):
    if ident == NOVO:
        return "novo"
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in str(ident))


def _fechar():
    st.session_state.itens_editando = None
    _nova_versao()
    st.rerun()


def _aplicar(novos, aviso, desfazer, salvar_fn, manter_aberto=False):
    """Grava a lista nova. `aviso` vai no toast; `desfazer` completa o botão "Desfazer …".

    Os textos não concordam com o nome do item ("Geladeira atualizado"): o gênero
    do item é desconhecido, então a frase gira em torno da ação.
    """
    st.session_state.itens_undo = copy.deepcopy(st.session_state.itens)
    st.session_state.itens_undo_label = desfazer
    st.session_state.itens[:] = novos
    salvar_fn()
    if not manter_aberto:
        st.session_state.itens_editando = None
    _nova_versao()
    st.toast(aviso, icon="✅")
    st.rerun()


# ==========================================================================
# Textos
# ==========================================================================
def _rotulo_tipo(tipo):
    return "Soma (Ana recebe)" if tipo == "credito" else "Abate"


def _plural(n, um, varios):
    return um if n == 1 else varios


def _pct(atual, novo):
    if not atual:
        return ""
    v = (novo - atual) / atual * 100
    return f" ({'+' if v >= 0 else '−'}{abs(v):.1f}%)".replace(".", ",")


def _detalhe(item, meses, hoje):
    i_hoje = meses.index(hoje)
    if modelo.eh_continuo(item):
        partes = [f"contínuo desde {item['inicio']}"]
        rs = modelo.reajustes(item, meses)
        futuros = [r for r in rs if meses.index(r["a_partir_de"]) > i_hoje]
        passados = [r for r in rs if meses.index(r["a_partir_de"]) <= i_hoje]
        if futuros:
            partes.append(f"reajuste para R$ {_brl(futuros[0]['valor'])} em {futuros[0]['a_partir_de']}")
        elif passados:
            partes.append(f"último reajuste em {passados[-1]['a_partir_de']}")
        else:
            partes.append("sem reajustes")
        return ", ".join(partes)

    total = len(modelo.meses_do_item(item, meses))
    if total == 1:
        texto = f"parcela única em {item['inicio']}"
    else:
        texto = f"{total} parcelas, de {item['inicio']} a {item['fim']}"
    n_ant = len(modelo.antecipacoes_confirmadas(item))
    if n_ant:
        texto += f", {n_ant} {_plural(n_ant, 'antecipada', 'antecipadas')}"
    if item["inicio"] in meses and meses.index(item["inicio"]) > i_hoje:
        texto += ", ainda não começou"
    return texto


def _html_erros(erros):
    itens = "".join(f"<li>{html.escape(e)}</li>" for e in erros)
    return f'<div class="itm"><div class="itm-erro"><ul>{itens}</ul></div></div>'


def _html_aviso_quitados(afetados):
    n = len(afetados)
    texto = (f"Esta mudança altera o acerto de {n} "
             f"{_plural(n, 'mês já quitado', 'meses já quitados')}: {_lista(afetados)}.")
    return f'<div class="itm"><div class="itm-aviso">{html.escape(texto)}</div></div>'


def _confirmar_quitados(afetados, chave):
    """Aviso + confirmação quando a mudança mexe em meses já quitados. True = liberado."""
    if not afetados:
        return True
    st.html(_html_aviso_quitados(afetados))
    return st.checkbox("Quero alterar meses já quitados", key=chave)


# ==========================================================================
# Lista
# ==========================================================================
def _anos(meses):
    anos = []
    for m in meses:
        a = "20" + m.split("/")[1]
        if a not in anos:
            anos.append(a)
    return anos


def _html_escala(meses):
    anos = _anos(meses)
    return (
        '<div class="itm"><ul class="itm-legenda">'
        '<li><span class="itm-chave itm-chave--passado"></span>Meses que já passaram</li>'
        '<li><span class="itm-chave itm-chave--futuro"></span>Próximos meses</li>'
        '<li><span class="itm-chave itm-chave--marco"></span>Reajuste</li>'
        '<li><span class="itm-chave itm-chave--hoje"></span>Mês atual</li>'
        "</ul>"
        f'<div class="itm-escala" style="grid-template-columns:repeat({len(anos)}, minmax(0, 1fr))">'
        + "".join(f"<span>{a}</span>" for a in anos)
        + "</div></div>"
    )


def _trechos(indices):
    trechos = []
    for i in indices:
        if trechos and i == trechos[-1][1] + 1:
            trechos[-1][1] = i
        else:
            trechos.append([i, i])
    return trechos


def _html_item(item, valores, meses, hoje):
    esc = html.escape
    i_hoje = meses.index(hoje)
    ativos = [i for i, v in enumerate(valores) if v > 0.005]
    partes = []
    for ini, fim in _trechos(ativos):
        for a, b, classe in ((ini, min(fim, i_hoje), "passado"), (max(ini, i_hoje + 1), fim, "futuro")):
            if a <= b:
                partes.append(f'<span class="itm-faixa itm-faixa--{classe}" '
                              f'style="grid-column:{a + 1} / {b + 2}"></span>')
    for i, m in enumerate(meses):
        if i and m.startswith("jan/"):
            partes.append(f'<span class="itm-ano" style="grid-column:{i + 1}"></span>')
    if modelo.eh_continuo(item):
        for r in modelo.reajustes(item, meses):
            partes.append(f'<span class="itm-marco" style="grid-column:{meses.index(r["a_partir_de"]) + 1}"></span>')
    partes.append(f'<span class="itm-hoje" style="grid-column:{i_hoje + 1}"></span>')

    detalhe = _detalhe(item, meses, hoje)
    return (
        '<div class="itm">'
        f'<div class="itm-nome">{esc(item["nome"])}</div>'
        f'<div class="itm-detalhe">{esc(detalhe)}</div>'
        f'<div class="itm-trilha" role="img" aria-label="{esc(item["nome"])}: {esc(detalhe)}" '
        f'style="grid-template-columns:repeat({len(meses)}, minmax(0, 1fr))">'
        + "".join(partes)
        + "</div></div>"
    )


def _html_valor(item, meses, hoje):
    sinal = "− " if item["tipo"] != "credito" else ""
    if modelo.eh_continuo(item):
        valor, nota = modelo.valor_vigente(item, hoje, meses), "por mês"
    else:
        valor, nota = float(item["valor"]), "por parcela"
    return (f'<div class="itm"><div class="itm-valor">{sinal}R$ {_brl(valor)}</div>'
            f'<div class="itm-valor-nota">{nota}</div></div>')


def _linha(item, tab, meses, hoje, salvar_fn, recalcular):
    ident = item["id"]
    editando = st.session_state.itens_editando == ident
    if ident in tab.columns:
        valores = [float(tab.at[m, ident]) for m in meses]
    else:
        valores = modelo.serie_no_acerto(item, meses)

    with st.container(key=f"item_{_chave(ident)}"):
        c1, c2, c3 = st.columns(COLUNAS_LINHA, gap="medium", vertical_alignment="center")
        with c1:
            st.html(_html_item(item, valores, meses, hoje))
        with c2:
            st.html(_html_valor(item, meses, hoje))
        with c3:
            if st.button("Fechar" if editando else "Editar", key=f"{_pref(ident)}_abrir", width="stretch"):
                st.session_state.itens_editando = None if editando else ident
                _nova_versao()
                st.rerun()
        if editando:
            _painel_edicao(item, meses, hoje, salvar_fn, recalcular)


# ==========================================================================
# Painéis
# ==========================================================================
def _popover_excluir(item, meses, salvar_fn):
    esc = html.escape
    afetados = modelo.meses_quitados_afetados(item, None, meses, st.session_state.meses_quitados)
    n_ant = len(modelo.antecipacoes_confirmadas(item))
    with st.popover("Excluir item"):
        notas = []
        if afetados:
            notas.append(f"O acerto de {len(afetados)} "
                         f"{_plural(len(afetados), 'mês já quitado muda', 'meses já quitados muda')}: "
                         f"{_lista(afetados)}.")
        if n_ant:
            notas.append(_plural(n_ant, "A antecipação deste item também é apagada.",
                                 f"As {n_ant} antecipações deste item também são apagadas."))
        notas.append("Dá para desfazer logo depois.")
        st.html(
            f'<div class="itm"><div class="itm-texto">Excluir <b>{esc(item["nome"])}</b>?</div>'
            + "".join(f'<div class="itm-nota">{esc(n)}</div>' for n in notas)
            + "</div>"
        )
        if st.button("Excluir item", type="primary",
                     key=f"excluir_ok_{_chave(item['id'])}_v{_versao()}"):
            novos = [i for i in st.session_state.itens if i["id"] != item["id"]]
            _aplicar(novos, f"Item excluído: {item['nome']}", f"exclusão de {item['nome']}", salvar_fn)


def _secao_reajustes(item, meses, hoje, salvar_fn):
    esc = html.escape
    p = _pref(item["id"])
    quitados = st.session_state.meses_quitados
    st.html(
        f'<div class="itm"><h3 class="itm-sub">Valores de {esc(item["nome"])}</h3>'
        '<div class="itm-nota">Um reajuste vale a partir do mês escolhido. '
        "Os meses anteriores continuam com o valor antigo.</div></div>"
    )

    vig = modelo.vigencias(item, meses)
    for k, (desde, valor) in enumerate(vig):
        prox = vig[k + 1][0] if k + 1 < len(vig) else None
        periodo = f"{desde} a {meses[meses.index(prox) - 1]}" if prox else f"{desde} em diante"
        with st.container(horizontal=True, gap="small", vertical_alignment="center"):
            st.html(f'<div class="itm"><div class="itm-vig"><span class="itm-vig-periodo">{periodo}</span>'
                    f'<span class="itm-vig-valor">R$ {_brl(valor)} por mês</span></div></div>')
            if k > 0:
                sem = modelo.remover_reajuste(item, desde, meses)
                afetados = modelo.meses_quitados_afetados(item, sem, meses, quitados)
                with st.popover("Remover"):
                    notas = [f"A partir de {desde} o valor volta a ser R$ {_brl(vig[k - 1][1])}."]
                    if afetados:
                        notas.append(f"O acerto de {len(afetados)} "
                                     f"{_plural(len(afetados), 'mês já quitado muda', 'meses já quitados muda')}: "
                                     f"{_lista(afetados)}.")
                    st.html(f'<div class="itm"><div class="itm-texto">Remover o reajuste de {desde}?</div>'
                            + "".join(f'<div class="itm-nota">{esc(n)}</div>' for n in notas) + "</div>")
                    if st.button("Remover reajuste", type="primary",
                                 key=f"remover_ok_{_chave(item['id'])}_{desde.replace('/', '_')}_v{_versao()}"):
                        novos = [sem if i["id"] == item["id"] else i for i in st.session_state.itens]
                        _aplicar(novos, f"Reajuste removido: {item['nome']}, {desde}",
                                 f"remoção do reajuste de {desde}", salvar_fn, manter_aberto=True)

    opcoes = meses[meses.index(item["inicio"]) + 1:]
    if not opcoes:
        return
    i_hoje = meses.index(hoje)
    seguinte = meses[i_hoje + 1] if i_hoje + 1 < len(meses) else None
    padrao = seguinte if seguinte in opcoes else opcoes[0]

    st.html('<div class="itm"><div class="itm-rotulo">Registrar reajuste</div></div>')
    c1, c2 = st.columns(2)
    mes = c1.selectbox("A partir de", opcoes, index=opcoes.index(padrao), key=f"{p}_rj_mes")
    atual = modelo.valor_vigente(item, mes, meses)
    novo_valor = c2.number_input("Novo valor por mês (R$)", min_value=0.0, value=None, step=10.0,
                                 format="%.2f", placeholder=f"hoje {_brl(atual)}", key=f"{p}_rj_valor")

    candidato = None
    if novo_valor is not None:
        erros = modelo.validar_reajuste(item, mes, novo_valor, meses)
        if erros:
            st.html(_html_erros(erros))
        else:
            candidato = modelo.registrar_reajuste(item, mes, novo_valor, meses)
            ja_existe = any(r["a_partir_de"] == mes for r in modelo.reajustes(item, meses))
            texto = (f"De R$ {_brl(atual)} para R$ {_brl(novo_valor)} a partir de {mes}"
                     f"{_pct(atual, novo_valor)}.")
            if ja_existe:
                texto += f" Substitui o reajuste já registrado para {mes}."
            st.html(f'<div class="itm"><div class="itm-nota">{html.escape(texto)}</div></div>')

    afetados = modelo.meses_quitados_afetados(item, candidato, meses, quitados) if candidato else []
    liberado = candidato is not None and _confirmar_quitados(afetados, f"{p}_rj_confirma")
    if st.button("Registrar reajuste", type="primary", disabled=not liberado, key=f"{p}_rj_salvar"):
        novos = [candidato if i["id"] == item["id"] else i for i in st.session_state.itens]
        _aplicar(novos, f"Reajuste registrado: {item['nome']} a partir de {mes}",
                 f"reajuste de {mes} em {item['nome']}", salvar_fn, manter_aberto=True)


def _painel_edicao(item, meses, hoje, salvar_fn, recalcular):
    esc = html.escape
    ident = item["id"]
    p = _pref(ident)
    quitados = st.session_state.meses_quitados
    continuo = modelo.eh_continuo(item)
    n_ant = len(modelo.antecipacoes_confirmadas(item))
    travado = n_ant > 0 and not continuo

    with st.container(key=f"painel_{_chave(ident)}"):
        if continuo:
            _secao_reajustes(item, meses, hoje, salvar_fn)
            st.html('<div class="itm"><div class="itm-divisor"></div><h3 class="itm-sub">Dados do item</h3></div>')
        else:
            st.html(f'<div class="itm"><h3 class="itm-sub">Editar {esc(item["nome"])}</h3></div>')

        c1, c2 = st.columns([3, 2])
        nome = c1.text_input("Nome", value=item["nome"], key=f"{p}_nome")
        with c2:
            tipo = st.segmented_control("Na conta", TIPOS, default=item["tipo"], format_func=_rotulo_tipo,
                                        key=f"{p}_tipo", width="stretch")

        valor = inicio = parcelas = None
        if continuo:
            c3, c4 = st.columns(2)
            inicio = c3.selectbox("Desde", meses, index=meses.index(item["inicio"]), key=f"{p}_inicio")
            valor = c4.number_input("Valor inicial por mês (R$)", min_value=0.0, value=float(item["valor"]),
                                    step=10.0, format="%.2f", key=f"{p}_valor",
                                    help="Valor antes do primeiro reajuste. Para mudar o valor daqui "
                                         "para frente, registre um reajuste acima.")
        elif travado:
            st.html(
                '<div class="itm"><div class="itm-travado">'
                f"Valor (R$ {_brl(item['valor'])} por parcela) e período ({item['inicio']} a {item['fim']}) "
                f"ficam travados porque este item tem {n_ant} "
                f"{_plural(n_ant, 'parcela antecipada', 'parcelas antecipadas')}. Para mudar, cancele as "
                "antecipações em Antecipar Parcelas.</div></div>"
            )
        else:
            c3, c4, c5 = st.columns([2, 2, 1])
            valor = c3.number_input("Valor da parcela (R$)", min_value=0.0, value=float(item["valor"]),
                                    step=10.0, format="%.2f", key=f"{p}_valor")
            inicio = c4.selectbox("Primeira parcela", meses, index=meses.index(item["inicio"]), key=f"{p}_inicio")
            parcelas = c5.number_input("Parcelas", min_value=1, max_value=len(meses), step=1,
                                       value=max(len(modelo.meses_do_item(item, meses)), 1), key=f"{p}_parcelas")
            fim = modelo.fim_por_parcelas(inicio, parcelas, meses)
            if fim:
                st.html(f'<div class="itm"><div class="itm-nota">Última parcela em {fim}.</div></div>')

        erros = modelo.validar_item(
            st.session_state.itens, nome=nome, tipo=tipo,
            valor=item["valor"] if valor is None else valor,
            inicio=item["inicio"] if inicio is None else inicio,
            meses=meses, continuo=continuo, parcelas=parcelas, id_atual=ident,
            reajustes=[r["a_partir_de"] for r in modelo.reajustes(item, meses)] if continuo else None,
        )
        novo = None
        if erros:
            st.html(_html_erros(erros))
        else:
            novo = modelo.editar_item(item, meses, nome=nome, tipo=tipo, valor=valor, inicio=inicio,
                                      parcelas=parcelas)
            if not continuo and not travado:
                novo["cronograma"] = recalcular(novo)
        mudou = novo is not None and modelo.resumo(novo, meses) != modelo.resumo(item, meses)

        afetados = modelo.meses_quitados_afetados(item, novo, meses, quitados) if mudou else []
        liberado = mudou and _confirmar_quitados(afetados, f"{p}_confirma")
        with st.container(horizontal=True, gap="small", vertical_alignment="center"):
            if st.button("Salvar alterações", type="secondary" if continuo else "primary",
                         disabled=not liberado, key=f"{p}_salvar"):
                novos = [novo if i["id"] == ident else i for i in st.session_state.itens]
                _aplicar(novos, f"Alterações salvas: {novo['nome']}", f"alterações em {novo['nome']}", salvar_fn)
            if st.button("Cancelar", key=f"{p}_cancelar"):
                _fechar()
            _popover_excluir(item, meses, salvar_fn)


def _painel_novo(meses, hoje, salvar_fn, recalcular):
    p = _pref(NOVO)
    quitados = st.session_state.meses_quitados
    with st.container(key="painel_novo"):
        st.html('<div class="itm"><h3 class="itm-sub">Novo item</h3></div>')
        c1, c2 = st.columns([3, 2])
        nome = c1.text_input("Nome", key=f"{p}_nome", placeholder="Ex.: Conserto da máquina")
        with c2:
            tipo = st.segmented_control("Na conta", TIPOS, default="debito", format_func=_rotulo_tipo,
                                        key=f"{p}_tipo", width="stretch")
        forma = st.segmented_control("Forma", ["parcelado", "continuo"], default="parcelado",
                                     format_func=lambda f: "Parcelado" if f == "parcelado" else "Contínuo, sem data fim",
                                     key=f"{p}_forma")
        continuo = forma == "continuo"

        parcelas = None
        if continuo:
            c3, c4 = st.columns(2)
            valor = c3.number_input("Valor por mês (R$)", min_value=0.0, value=None, step=10.0, format="%.2f",
                                    placeholder="0,00", key=f"{p}_valor")
            inicio = c4.selectbox("Desde", meses, index=meses.index(hoje), key=f"{p}_inicio")
            st.html('<div class="itm"><div class="itm-nota">Quando o valor mudar, registre um reajuste: '
                    "os meses anteriores ficam como estão.</div></div>")
        else:
            c3, c4, c5 = st.columns([2, 2, 1])
            valor = c3.number_input("Valor da parcela (R$)", min_value=0.0, value=None, step=10.0, format="%.2f",
                                    placeholder="0,00", key=f"{p}_valor")
            inicio = c4.selectbox("Primeira parcela", meses, index=meses.index(hoje), key=f"{p}_inicio")
            parcelas = c5.number_input("Parcelas", min_value=1, max_value=len(meses), value=1, step=1,
                                       key=f"{p}_parcelas")
            fim = modelo.fim_por_parcelas(inicio, parcelas, meses)
            if fim:
                st.html(f'<div class="itm"><div class="itm-nota">Última parcela em {fim}.</div></div>')

        erros = modelo.validar_item(st.session_state.itens, nome=nome, tipo=tipo, valor=valor, inicio=inicio,
                                    meses=meses, continuo=continuo, parcelas=parcelas)
        if forma is None:
            erros.append("Escolha se o item é parcelado ou contínuo.")
        novo = None
        if not erros:
            novo = modelo.criar_item(st.session_state.itens, nome=nome, tipo=tipo, valor=valor, inicio=inicio,
                                     meses=meses, continuo=continuo, parcelas=parcelas)
            if not continuo:
                novo["cronograma"] = recalcular(novo)
        elif (nome or "").strip() or valor is not None:
            st.html(_html_erros(erros))

        afetados = modelo.meses_quitados_afetados(None, novo, meses, quitados) if novo else []
        liberado = novo is not None and _confirmar_quitados(afetados, f"{p}_confirma")
        with st.container(horizontal=True, gap="small", vertical_alignment="center"):
            if st.button("Adicionar item", type="primary", disabled=not liberado, key=f"{p}_salvar"):
                _aplicar(st.session_state.itens + [novo], f"Item incluído: {novo['nome']}",
                         f"inclusão de {novo['nome']}", salvar_fn)
            if st.button("Cancelar", key=f"{p}_cancelar"):
                _fechar()


# ==========================================================================
# Entrada chamada por app.py
# ==========================================================================
def exibir_gerenciar_itens(df_calculado, salvar_fn, recalcular_cronograma):
    """Aba Gerenciar Itens: lista com faixa de meses, edição segura e reajustes."""
    _estado()
    st.html(_CSS)

    meses = list(df_calculado["mesAno"])
    if not meses:
        st.info("Nenhum mês cadastrado.")
        return
    hoje = _mes_de_hoje(meses)
    i_hoje = meses.index(hoje)
    tab = df_calculado.set_index("mesAno")
    itens = st.session_state.itens

    with st.container(key="itens_cabeca"):
        st.html('<div class="itm"><h2 class="itm-titulo">Itens do acerto</h2>'
                '<div class="itm-texto">Tudo o que entra na conta de cada mês. Mudanças que '
                "alteram meses já quitados pedem confirmação.</div></div>")
        with st.container(horizontal=True, gap="small", vertical_alignment="center"):
            if st.session_state.itens_editando != NOVO:
                if st.button("Novo item", type="primary", key=f"itens_novo_v{_versao()}"):
                    st.session_state.itens_editando = NOVO
                    _nova_versao()
                    st.rerun()
            if st.session_state.itens_undo is not None:
                if st.button(f"Desfazer {st.session_state.itens_undo_label}", type="tertiary",
                             key=f"itens_desfazer_v{_versao()}"):
                    st.session_state.itens[:] = st.session_state.itens_undo
                    st.session_state.itens_undo = None
                    st.session_state.itens_undo_label = ""
                    st.session_state.itens_editando = None
                    salvar_fn()
                    _nova_versao()
                    st.toast("Alteração desfeita", icon="↩️")
                    st.rerun()

    if st.session_state.itens_editando == NOVO:
        _painel_novo(meses, hoje, salvar_fn, recalcular_cronograma)

    if not itens:
        st.html('<div class="itm"><div class="itm-vazio">Nenhum item ainda. '
                "Use Novo item para cadastrar o primeiro.</div></div>")
        return

    def encerrado(item):
        return (not modelo.eh_continuo(item)
                and item.get("fim") in meses and meses.index(item["fim"]) < i_hoje)

    def ordem(item):
        fim = modelo.ultimo_mes(item, meses)
        return (modelo.eh_continuo(item), meses.index(fim) if fim in meses else len(meses))

    ativos = [i for i in itens if not encerrado(i)]
    encerrados = [i for i in itens if encerrado(i)]

    with st.container(key="itens_escala"):
        c1, _, _ = st.columns(COLUNAS_LINHA, gap="medium")  # mesma grade das linhas: escala alinhada às faixas
        with c1:
            st.html(_html_escala(meses))

    grupos = (("credito", "Somam ao que a Ana recebe"), ("debito", "Abatem do acerto"))
    for tipo, titulo in grupos:
        grupo = sorted((i for i in ativos if i["tipo"] == tipo), key=ordem, reverse=False)
        if not grupo:
            continue
        total = sum(float(tab.at[hoje, i["id"]]) for i in grupo if i["id"] in tab.columns)
        st.html(f'<div class="itm"><div class="itm-grupo"><span class="itm-grupo-nome">{titulo}</span>'
                f'<span class="itm-grupo-total">R$ {_brl(total)} em {hoje}</span></div></div>')
        for item in grupo:
            _linha(item, tab, meses, hoje, salvar_fn, recalcular_cronograma)

    if encerrados:
        aberto = any(i["id"] == st.session_state.itens_editando for i in encerrados)
        with st.expander(f"Encerrados ({len(encerrados)})", expanded=aberto):
            for item in sorted(encerrados, key=lambda i: meses.index(i["fim"]), reverse=True):
                _linha(item, tab, meses, hoje, salvar_fn, recalcular_cronograma)
