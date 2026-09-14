"""
Antecipar Parcelas — registrar parcelas pagas fora do mês previsto.

A aba responde, nesta ordem:
  1. De qual item, quais parcelas em aberto e em que mês foram pagas.
  2. Como fica o acerto de cada mês afetado, antes de confirmar.
  3. O que já foi antecipado, com a opção de cancelar.

Em relação à versão anterior:
  - O mês de pagamento começava em jan/25 (primeiro mês, já quitado); agora
    começa no mês atual.
  - Pagamento depois do vencimento é chamado de adiamento, não de antecipação.
  - N parcelas = 1 gravação pela mesma via das outras abas (antes: N gravações
    e N pushes no serviço, mais um salvar_dados).
  - Cancelar pede confirmação e mostra os meses quitados afetados; toda
    gravação tem Desfazer.

Regras em antecipacao_modelo.py (testado em test_antecipacao_modelo.py).
"""

import copy
import html
from datetime import datetime

import streamlit as st

import antecipacao_modelo as ant
import itens_modelo as modelo
from detalhamento_mensal import _lista
from gestao_executiva import _brl, _mes_de_hoje, _valor_texto

# Nunca escreva o caractere "menor que" dentro do CSS (nem em comentário): o
# sanitizador do st.html descarta o bloco de estilo inteiro.
_CSS = """
<style>
.ant { font-family: 'DM Sans', -apple-system, 'Segoe UI', sans-serif; color: #0A1628; }
.ant h2.ant-titulo, .ant h3.ant-sub {
  font-family: 'Playfair Display', Georgia, serif !important; font-weight: 600 !important;
  color: #0A1628 !important; letter-spacing: -0.01em !important; padding: 0 !important; }
.ant h2.ant-titulo { font-size: 1.5rem !important; line-height: 1.25 !important; margin: 0 0 .25rem !important; }
.ant h3.ant-sub { font-size: 1.125rem !important; line-height: 1.3 !important; margin: 0 0 .25rem !important; }
.ant .ant-texto { font-size: .9375rem; line-height: 1.5; color: #374151; max-width: 64ch; }
.ant .ant-nota { font-size: .8125rem; line-height: 1.5; color: #5F6673; max-width: 64ch; }
.ant.ant-bloco, .ant .ant-bloco { margin-top: 1.75rem; }
.ant .ant-vazio { font-size: .9375rem; color: #5F6673; margin-top: 1.5rem; }
.ant .ant-aviso { background: #FDF1DC; color: #6B3A04; border-radius: 10px; padding: .625rem .875rem; font-size: .875rem; line-height: 1.5; margin-top: .5rem; }
.ant .ant-info { background: #F4F2EE; color: #374151; border-radius: 10px; padding: .625rem .875rem; font-size: .875rem; line-height: 1.5; margin-bottom: .75rem; }
.ant .ant-erro { background: #FBE9E6; color: #8A2418; border-radius: 10px; padding: .625rem .875rem; font-size: .875rem; line-height: 1.5; }
.ant .ant-erro ul { margin: 0; padding-left: 1.1rem; }
.ant .ant-erro li { margin: 0; color: #8A2418; }

.st-key-ant_efeito { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.25rem 1.5rem 1.375rem; margin-top: 1rem; }
@media (max-width: 560px) { .st-key-ant_efeito { padding: 1rem 1rem 1.125rem; } }
.ant .ant-rolagem { overflow-x: auto; margin-top: .5rem; }
.ant .ant-tabela { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.ant .ant-tabela th, .ant .ant-tabela td { padding: .625rem 0 .625rem 1rem; border-bottom: 1px solid #EEF0F3; text-align: right; font-size: .9375rem; white-space: nowrap; }
.ant .ant-tabela th:first-child { padding-left: 0; text-align: left; }
.ant .ant-tabela thead th { font-size: .8125rem; font-weight: 500; color: #5F6673; border-bottom: 1px solid #0A1628; }
.ant .ant-tabela tbody th { font-weight: 500; color: #0A1628; }
.ant .ant-tabela tbody tr:last-child th, .ant .ant-tabela tbody tr:last-child td { border-bottom: 0; }
.ant .ant-tabela td { color: #374151; }
.ant .ant-tabela td.ant-depois { color: #0A1628; font-weight: 600; }
.ant .ant-marca { display: inline-block; margin-left: .5rem; padding: .125rem .5rem; border-radius: 999px; font-size: .75rem; font-weight: 500; line-height: 1.4; background: #F1F3F5; color: #4B5563; vertical-align: 1px; }
.ant .ant-marca--destino { background: #E6EBF3; color: #1C2B4A; }
/* Celular: sem a coluna Diferença (Antes e Depois já dizem) e etiqueta abaixo do mês,
   para a coluna Depois caber sem rolagem. */
@media (max-width: 560px) {
  .ant .ant-tabela .ant-dif { display: none; }
  .ant .ant-tabela th, .ant .ant-tabela td { padding-left: .625rem; font-size: .875rem; }
  .ant .ant-marca { display: table; margin: .25rem 0 0; }
}

[class*="st-key-ant_reg_"] { padding: .75rem 0; border-bottom: 1px solid #E5E0D8; }
.ant .ant-reg { font-size: .9375rem; font-weight: 500; color: #0A1628; }
.ant .ant-reg-detalhe { font-size: .8125rem; line-height: 1.45; color: #5F6673; margin-top: .125rem; }

/* Pills de item e de parcelas. */
[class*="st-key-ant_escolha"] [data-testid="stButtonGroup"] button { border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; min-height: 2.5rem; }
[class*="st-key-ant_escolha"] button[data-testid="stBaseButton-pills"] {
  background: #FFFFFF !important; border: 1px solid #AEB5C0 !important; color: #0A1628 !important; }
[class*="st-key-ant_escolha"] button[data-testid="stBaseButton-pillsActive"] {
  background: #1C2B4A !important; border: 1px solid #1C2B4A !important; color: #FFFFFF !important; }
[class*="st-key-ant_escolha"] [data-testid="stButtonGroup"] button :is(span, p, div) { color: inherit !important; font-weight: inherit !important; }
[class*="st-key-ant_escolha"] [data-testid="stButtonGroup"] button:focus-visible { outline: 2px solid #0A1628 !important; outline-offset: 2px; }

/* Botões: terciário como link, sem hover vermelho, desabilitado com cara de desabilitado. */
.st-key-ant_tab .stButton > button[data-testid="stBaseButton-tertiary"] {
  background: transparent !important; color: #1C2B4A !important; border: 0 !important; box-shadow: none !important;
  text-decoration: underline; text-underline-offset: .2em; }
.st-key-ant_tab .stButton > button[kind="secondary"]:hover {
  border-color: #1C2B4A !important; color: #1C2B4A !important; background: #F4F2EE !important; }
.st-key-ant_tab .stButton > button:disabled {
  background: #ECE8E1 !important; color: #6B7280 !important; border: 1px solid #E0DBD2 !important;
  box-shadow: none !important; cursor: not-allowed !important; }
.st-key-ant_tab .stButton > button:disabled :is(span, p, div) { color: inherit !important; }
.st-key-ant_tab [data-testid="stPopover"] button {
  background: #FFFFFF !important; color: #9A2B1E !important; border: 1px solid #E8C4BE !important; }
.st-key-ant_tab [data-testid="stPopover"] button :is(span, p, div) { color: inherit !important; }
[class*="st-key-ant_cancelar_ok_"] button { background: #9A2B1E !important; color: #FFFFFF !important; border: 0 !important; }
[class*="st-key-ant_cancelar_ok_"] button :is(span, p, div) { color: inherit !important; }
</style>
"""


# ==========================================================================
# Estado e gravação
# ==========================================================================
def _estado():
    st.session_state.setdefault("ant_versao", 0)
    st.session_state.setdefault("ant_undo", None)
    st.session_state.setdefault("ant_undo_label", "")
    st.session_state.setdefault("ant_item_escolhido", None)


def _v():
    # Chaves versionadas: apagar a chave não reseta o widget no navegador.
    return st.session_state.ant_versao


def _chave(texto):
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in str(texto))


def _aplicar(novo_item, aviso, desfazer, salvar_fn):
    """Uma gravação por ação. `aviso` vai no toast; `desfazer` completa o botão."""
    st.session_state.ant_undo = copy.deepcopy(st.session_state.itens)
    st.session_state.ant_undo_label = desfazer
    st.session_state.itens[:] = [novo_item if i["id"] == novo_item["id"] else i
                                 for i in st.session_state.itens]
    salvar_fn()
    st.session_state.ant_versao += 1
    st.toast(aviso, icon="✅")
    st.rerun()


# ==========================================================================
# Textos
# ==========================================================================
def _plural(n, um, varios):
    return um if n == 1 else varios


def _data(ts):
    try:
        return datetime.fromisoformat(ts).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return ""


def _rotulo_item(item, meses, quitados):
    n = len(ant.parcelas_disponiveis(item, meses, quitados))
    if not n:
        return f"{item['nome']}, nenhuma em aberto"
    return f"{item['nome']}, {n} em aberto"


def _rotulo_mes(mes, hoje, quitados):
    if mes == hoje:
        return f"{mes}, mês atual"
    if mes in quitados:
        return f"{mes}, quitado"
    return mes


def _verbos(origens, destino, meses):
    """(botão, particípio singular, particípio plural, substantivo) conforme a direção."""
    atrasadas = ant.adiadas(origens, destino, meses)
    if not atrasadas:
        return "Antecipar", "antecipada", "antecipadas", "antecipação"
    if len(atrasadas) == len(origens):
        return "Adiar", "adiada", "adiadas", "adiamento"
    return "Mover", "movida", "movidas", "mudança"


def _html_erros(erros):
    itens = "".join(f"<li>{html.escape(e)}</li>" for e in erros)
    return f'<div class="ant"><div class="ant-erro"><ul>{itens}</ul></div></div>'


def _confirmar_quitados(afetados, chave):
    """Aviso + confirmação quando a ação mexe em meses já quitados. True = liberado."""
    if not afetados:
        return True
    n = len(afetados)
    texto = (f"Isto altera o acerto de {n} {_plural(n, 'mês já quitado', 'meses já quitados')}: "
             f"{_lista(afetados)}.")
    st.html(f'<div class="ant"><div class="ant-aviso">{html.escape(texto)}</div></div>')
    return st.checkbox("Quero alterar meses já quitados", key=chave)


def _html_efeito(linhas, origens, destino, item, meses):
    corpo = []
    for mes, antes, depois in linhas:
        marcas = ""
        if mes == destino:
            marcas += '<span class="ant-marca ant-marca--destino">pagamento</span>'
        if mes in origens:
            numero, total = ant.numero_parcela(item, mes, meses)
            marcas += (f'<span class="ant-marca">parcela {numero} de {total}</span>' if numero
                       else '<span class="ant-marca">parcela</span>')
        diferenca = depois - antes
        corpo.append(
            f'<tr><th scope="row">{mes}{marcas}</th>'
            f"<td>{_valor_texto(antes)}</td>"
            f'<td class="ant-depois">{_valor_texto(depois)}</td>'
            f'<td class="ant-dif">{"+" if diferenca >= 0 else "−"} R$ {_brl(diferenca)}</td></tr>'
        )
    return (
        '<div class="ant"><h3 class="ant-sub">Como fica o acerto</h3>'
        '<div class="ant-nota">Valor do acerto de cada mês afetado, antes e depois de confirmar.</div>'
        '<div class="ant-rolagem"><table class="ant-tabela"><thead><tr>'
        '<th scope="col">Mês</th><th scope="col">Antes</th><th scope="col">Depois</th>'
        '<th scope="col" class="ant-dif">Diferença</th></tr></thead>'
        f'<tbody>{"".join(corpo)}</tbody></table></div></div>'
    )


# ==========================================================================
# Blocos
# ==========================================================================
def _cabecalho(salvar_fn):
    with st.container(key="ant_cabeca"):
        st.html(
            '<div class="ant"><h2 class="ant-titulo">Antecipar parcelas</h2>'
            '<div class="ant-texto">Quando uma parcela é paga antes do previsto, o valor sai do mês '
            "em que ela venceria e entra no acerto do mês em que foi paga.</div></div>"
        )
        if st.session_state.ant_undo is not None:
            if st.button(f"Desfazer {st.session_state.ant_undo_label}", type="tertiary",
                         key=f"ant_desfazer_v{_v()}"):
                st.session_state.itens[:] = st.session_state.ant_undo
                st.session_state.ant_undo = None
                st.session_state.ant_undo_label = ""
                salvar_fn()
                st.session_state.ant_versao += 1
                st.toast("Alteração desfeita", icon="↩️")
                st.rerun()


def _formulario(item, meses, hoje, quitados, salvar_fn, recalcular):
    esc = html.escape
    ident = _chave(item["id"])
    v = _v()
    disponiveis = ant.parcelas_disponiveis(item, meses, quitados)
    if not disponiveis:
        st.html(f'<div class="ant ant-bloco"><div class="ant-nota">{esc(item["nome"])} não tem parcelas '
                "em aberto. As antecipações já feitas estão abaixo.</div></div>")
        return

    n_disp = len(disponiveis)
    st.html(
        f'<div class="ant ant-bloco"><h3 class="ant-sub">Parcelas em aberto de {esc(item["nome"])}</h3>'
        f'<div class="ant-nota">{n_disp} {_plural(n_disp, "parcela", "parcelas")} de R$ {_brl(item["valor"])}. '
        "Toque nas que foram pagas fora do mês previsto.</div></div>"
    )
    with st.container(key="ant_escolha_parcelas"):
        origens = st.pills("Parcelas pagas", disponiveis, selection_mode="multi",
                           key=f"ant_parcelas_{ident}_v{v}", label_visibility="collapsed")
    origens = sorted(origens or [], key=meses.index)

    c1, c2 = st.columns([1, 2])
    destino = c1.selectbox("Pagas no acerto de", meses, index=meses.index(hoje),
                           format_func=lambda m: _rotulo_mes(m, hoje, quitados),
                           key=f"ant_destino_{ident}_v{v}")
    motivo = c2.text_input("Motivo (opcional)", key=f"ant_motivo_{ident}_v{v}",
                           placeholder="Ex.: pago junto com o 13º")

    if not origens:
        st.html('<div class="ant"><div class="ant-nota">Escolha ao menos uma parcela para ver como fica '
                "o acerto.</div></div>")
        return

    erros = ant.validar(item, origens, destino, meses, quitados)
    if erros:
        st.html(_html_erros(erros))
        return

    novo = ant.antecipar(item, origens, destino, meses, motivo=motivo)
    if novo.get("contrato"):
        novo["cronograma"] = recalcular(novo)
    linhas = ant.efeito(st.session_state.itens, item, novo, meses)
    botao, part_um, part_varios, substantivo = _verbos(origens, destino, meses)
    n = len(origens)

    with st.container(key="ant_efeito"):
        atrasadas = ant.adiadas(origens, destino, meses)
        if atrasadas:
            k = len(atrasadas)
            st.html(
                '<div class="ant"><div class="ant-info">'
                f"{destino} vem depois de {_lista(atrasadas)}: "
                f"{_plural(k, 'essa parcela fica adiada', 'essas parcelas ficam adiadas')}, não antecipada"
                f"{'' if k == 1 else 's'}.</div></div>"
            )
        st.html(_html_efeito(linhas, origens, destino, item, meses))
        afetados = modelo.meses_quitados_afetados(item, novo, meses, quitados)
        liberado = _confirmar_quitados(afetados, f"ant_confirma_{ident}_v{v}")
        rotulo = f"{botao} {n} {_plural(n, 'parcela', 'parcelas')}"
        if st.button(rotulo, type="primary", disabled=not liberado, key=f"ant_salvar_{ident}_v{v}"):
            parcelas = _plural(n, "parcela", "parcelas")
            _aplicar(
                novo,
                f"{n} {parcelas} de {item['nome']} {_plural(n, part_um, part_varios)} para {destino}",
                f"{substantivo} de {n} {parcelas} de {item['nome']}",
                salvar_fn,
            )


def _registro(reg, item, meses, quitados, salvar_fn, recalcular, ativo):
    esc = html.escape
    origem, destino = reg.get("origem", "?"), reg.get("destino", "?")
    numero, total = ant.numero_parcela(item, origem, meses) if origem in meses else (None, 0)
    parcela = f"parcela {numero} de {total}" if numero else "parcela"
    adiada = origem in meses and destino in meses and meses.index(destino) > meses.index(origem)

    detalhe = [f"R$ {_brl(reg.get('valor_antecipado', 0))}"]
    quando = _data(reg.get("timestamp"))
    if quando:
        detalhe.append(f"{'adiada' if adiada else 'antecipada'} em {quando}")
    if not ativo and _data(reg.get("cancelado_em")):
        detalhe.append(f"cancelada em {_data(reg.get('cancelado_em'))}")
    if reg.get("motivo"):
        detalhe.append(f"motivo: {reg['motivo']}")

    with st.container(key=f"ant_reg_{_chave(reg.get('id_antecipacao'))}"):
        c1, c2 = st.columns([5, 1.4], vertical_alignment="center")
        c1.html(f'<div class="ant"><div class="ant-reg">{esc(parcela.capitalize())}: {origem} para {destino}</div>'
                f'<div class="ant-reg-detalhe">{esc(", ".join(detalhe))}</div></div>')
        if not ativo:
            return
        novo = ant.cancelar(item, reg["id_antecipacao"])
        if novo.get("contrato"):
            novo["cronograma"] = recalcular(novo)
        afetados = modelo.meses_quitados_afetados(item, novo, meses, quitados)
        with c2:
            with st.popover("Cancelar"):
                notas = [f"O valor volta para {origem} e sai do acerto de {destino}."]
                if afetados:
                    k = len(afetados)
                    notas.append(f"O acerto de {k} {_plural(k, 'mês já quitado muda', 'meses já quitados muda')}: "
                                 f"{_lista(afetados)}.")
                notas.append("Dá para desfazer logo depois.")
                st.html(f'<div class="ant"><div class="ant-texto">Cancelar a antecipação da {esc(parcela)}?</div>'
                        + "".join(f'<div class="ant-nota">{esc(t)}</div>' for t in notas) + "</div>")
                if st.button("Cancelar antecipação", type="primary",
                             key=f"ant_cancelar_ok_{_chave(reg['id_antecipacao'])}_v{_v()}"):
                    _aplicar(novo, f"Antecipação cancelada: {parcela} de {item['nome']}",
                             f"cancelamento da {parcela} de {item['nome']}", salvar_fn)


def _historico(item, meses, quitados, salvar_fn, recalcular):
    registros = item.get("antecipacoes") or []
    if not registros:
        return

    def por_origem(r):
        return meses.index(r["origem"]) if r.get("origem") in meses else len(meses)

    # Em ordem de parcela: registros de um mesmo lote diferem por segundos no horário,
    # e ordenar por data embaralhava a sequência (parcela 7, 6, 5...).
    confirmadas = sorted((r for r in registros if r.get("status") == "confirmada"), key=por_origem)
    canceladas = [r for r in registros if r.get("status") != "confirmada"]

    st.html(f'<div class="ant ant-bloco"><h3 class="ant-sub">Antecipações de {html.escape(item["nome"])}</h3></div>')
    if not confirmadas:
        st.html('<div class="ant"><div class="ant-nota">Nenhuma antecipação ativa.</div></div>')
    for reg in confirmadas:
        _registro(reg, item, meses, quitados, salvar_fn, recalcular, ativo=True)
    if canceladas:
        with st.expander(f"Canceladas ({len(canceladas)})"):
            for reg in sorted(canceladas, key=por_origem):
                _registro(reg, item, meses, quitados, salvar_fn, recalcular, ativo=False)


# ==========================================================================
# Entrada chamada por app.py
# ==========================================================================
def exibir_antecipar_parcelas(df_calculado, salvar_fn, recalcular_cronograma):
    """Aba Antecipar Parcelas: escolher parcelas, ver o efeito no acerto, confirmar."""
    _estado()
    st.html(_CSS)

    meses = list(df_calculado["mesAno"])
    if not meses:
        st.info("Nenhum mês cadastrado.")
        return
    hoje = _mes_de_hoje(meses)
    quitados = st.session_state.meses_quitados

    with st.container(key="ant_tab"):
        _cabecalho(salvar_fn)

        elegiveis = [i for i in st.session_state.itens
                     if ant.pode_antecipar(i)
                     and (ant.parcelas_disponiveis(i, meses, quitados) or i.get("antecipacoes"))]
        if not elegiveis:
            st.html('<div class="ant"><div class="ant-vazio">Nenhum item parcelado tem parcelas em aberto. '
                    "Para cadastrar um, use Gerenciar Itens.</div></div>")
            return

        por_id = {i["id"]: i for i in elegiveis}
        escolhido = st.session_state.ant_item_escolhido
        if escolhido not in por_id:
            escolhido = next((i["id"] for i in elegiveis if ant.parcelas_disponiveis(i, meses, quitados)),
                             elegiveis[0]["id"])

        with st.container(key="ant_escolha_item"):
            selecionado = st.pills("Item", list(por_id), selection_mode="single", default=escolhido,
                                   format_func=lambda i: _rotulo_item(por_id[i], meses, quitados),
                                   key=f"ant_item_v{_v()}")
        item_id = selecionado or escolhido
        st.session_state.ant_item_escolhido = item_id
        item = por_id[item_id]

        _formulario(item, meses, hoje, quitados, salvar_fn, recalcular_cronograma)
        _historico(item, meses, quitados, salvar_fn, recalcular_cronograma)
