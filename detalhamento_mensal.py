"""
Detalhamento Mensal — onde o acerto de cada mês é marcado como quitado.

A aba responde, nesta ordem:
  1. O que está em aberto agora, com a ação de quitar em um clique (e desfazer).
  2. A situação de todos os meses, numa caderneta por ano que também serve para
     quitar ou reabrir vários meses de uma vez.
  3. Como está cada item: parcelas pagas e quando termina.

Mantém as regras de quitacao_ui.py: na caderneta nada é gravado no clique; as
alterações ficam pendentes, com resumo, confirmação a partir de
LIMIAR_CONFIRMACAO meses, UMA gravação para N meses (1 push no GitHub) e
"Desfazer" depois de toda gravação. Toda gravação faz rerun completo, porque
meses_quitados alimenta também a Gestão Executiva e o Extrato.

Parcelas são contadas pelo que entra no acerto (DataFrame já com antecipações),
a mesma base da Gestão Executiva — assim as duas abas mostram os mesmos números.
"""

import html

import streamlit as st

from gestao_executiva import _brl, _mes_de_hoje, _mes_extenso, _valor_texto
from quitacao_ui import LIMIAR_CONFIRMACAO, _desfazer, _init_state, _rerun_local

# st.html sanitiza o conteúdo e o CSS global do app pinta todo <span>/<p>: por
# isso todo seletor aqui tem o prefixo .quit (vence o global) e não há <p>.
# Nunca escreva o caractere "menor que" dentro do CSS (nem em comentário): o
# sanitizador descarta o bloco <style> inteiro e a aba fica sem estilo.
_CSS = """
<style>
.quit { font-family: 'DM Sans', -apple-system, 'Segoe UI', sans-serif; color: #0A1628; }
.quit h2.quit-titulo, .quit h3.quit-sub {
  font-family: 'Playfair Display', Georgia, serif !important; font-weight: 600 !important;
  color: #0A1628 !important; letter-spacing: -0.01em !important; padding: 0 !important; }
.quit h2.quit-titulo { font-size: 1.5rem !important; line-height: 1.25 !important; margin: .625rem 0 .25rem !important; }
.quit h3.quit-sub { font-size: 1.125rem !important; line-height: 1.3 !important; margin: 0 !important; }
.quit .quit-texto { font-size: 1rem; line-height: 1.5; color: #374151; max-width: 60ch; }

.st-key-quit_topo { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.25rem 1.75rem 1.5rem; }
/* Desfazer é secundário à ação: link, não botão cheio (o CSS global pinta todo botão de marinho). */
.st-key-quit_topo .stButton > button[data-testid="stBaseButton-tertiary"] {
  background: transparent !important; color: #1C2B4A !important; border: 0 !important; box-shadow: none !important;
  text-decoration: underline; text-underline-offset: .2em; padding-left: .5rem !important; padding-right: .5rem !important; }
.st-key-quit_topo .stButton > button[data-testid="stBaseButton-tertiary"]:hover { color: #0A1628 !important; background: #F4F2EE !important; }
/* O hover global de botão secundário é vermelho (feito para Excluir); aqui não há exclusão. */
.st-key-quit_topo .stButton > button[kind="secondary"]:hover,
.st-key-quit_pendente .stButton > button[kind="secondary"]:hover {
  border-color: #1C2B4A !important; color: #1C2B4A !important; background: #F4F2EE !important; }
@media (max-width: 560px) { .st-key-quit_topo { padding: 1rem 1rem 1.25rem; } }

.quit .quit-status { display: inline-flex; align-items: center; gap: .45rem; padding: .375rem .7rem; border-radius: 999px; font-size: .8125rem; font-weight: 600; line-height: 1; white-space: nowrap; }
.quit .quit-status::before { content: ""; flex: none; box-sizing: border-box; }
.quit .quit-status--dia { color: #0B6B4B; background: #E7F5EE; }
.quit .quit-status--dia::before { content: "✓"; font-size: .9375rem; font-weight: 700; }
.quit .quit-status--pendente { color: #8A4B06; background: #FDF1DC; }
.quit .quit-status--pendente::before { width: 11px; height: 11px; border: 2px solid currentColor; border-radius: 50%; }
.quit .quit-status--atraso { color: #9A2B1E; background: #FBE9E6; }
.quit .quit-status--atraso::before { content: "!"; width: 15px; height: 15px; border-radius: 50%; background: #9A2B1E; color: #FBE9E6; font-size: .6875rem; font-weight: 700; line-height: 15px; text-align: center; }

.quit .quit-cabeca { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: .5rem 1.5rem; margin-top: 2.25rem; }
.quit .quit-legenda { display: flex; flex-wrap: wrap; gap: .375rem 1.125rem; list-style: none; margin: 0; padding: 0; font-size: .8125rem; color: #5F6673; }
.quit .quit-legenda li { display: inline-flex; align-items: center; gap: .45rem; margin: 0; }
.quit .quit-chave { position: relative; display: inline-block; width: 14px; height: 14px; border-radius: 4px; box-sizing: border-box; }
.quit .quit-chave--quitado { background: #1C2B4A; }
.quit .quit-chave--aberto { background: #FFFFFF; border: 1px solid #AEB5C0; }
.quit .quit-chave--atraso { background: #FFFFFF; border: 1px solid #9A2B1E; }
.quit .quit-chave--atraso::after { content: ""; position: absolute; top: -3px; right: -3px; width: 6px; height: 6px; border-radius: 50%; background: #9A2B1E; }
.quit .quit-chave--hoje { background: #FFFFFF; border: 1px solid #AEB5C0; box-shadow: 0 0 0 2px #F8F6F3, 0 0 0 3.5px #0A1628; margin: 0 .25rem; }
.quit .quit-chave--alterado { background: #FFFFFF; border: 2px dashed #A88B4A; }
.quit .quit-dica { font-size: .8125rem; color: #5F6673; margin-top: .5rem; }

.quit .quit-ano { display: flex; align-items: baseline; gap: .75rem; margin-top: 1rem; }
.quit .quit-ano-nome { font-size: .9375rem; font-weight: 600; color: #0A1628; font-variant-numeric: tabular-nums; }
.quit .quit-ano-conta { font-size: .8125rem; color: #5F6673; }

.st-key-quit_pendente { background: #FFFFFF; border: 1px solid #D9CBB0; border-radius: 12px; padding: .875rem 1.25rem 1rem; margin-top: 1rem; }
.quit .quit-pendente-texto { font-size: .9375rem; line-height: 1.5; color: #0A1628; }
.quit .quit-pendente-texto b { font-weight: 600; }

.quit .quit-itens { margin-top: 2.75rem; max-width: 46rem; }
.quit .quit-nota { font-size: .8125rem; color: #5F6673; margin: .25rem 0 .75rem; }
.quit .quit-lista { list-style: none; margin: 0; padding: 0; }
.quit .quit-linha { padding: .875rem 0; border-top: 1px solid #E5E0D8; margin: 0; }
.quit .quit-linha:first-child { border-top: 0; }
.quit .quit-linha-topo { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: .125rem 1rem; }
.quit .quit-nome { font-size: 1rem; font-weight: 500; color: #0A1628; }
.quit .quit-valor { font-size: .9375rem; color: #0A1628; font-variant-numeric: tabular-nums; white-space: nowrap; }
.quit .quit-medidor { display: block; height: 6px; margin: .5rem 0 .375rem; border-radius: 3px; background: #E4E0D9; overflow: hidden; }
.quit .quit-medidor-cheio { display: block; height: 100%; border-radius: 3px; background: #1C2B4A; }
.quit .quit-detalhe { font-size: .8125rem; color: #5F6673; }
.quit .quit-encerrados { margin-top: .75rem; padding-top: .875rem; border-top: 1px solid #E5E0D8; font-size: .8125rem; line-height: 1.5; color: #5F6673; }

/* Caderneta: st.pills estilizado por ano (container com key quit_ano_AAAA). */
[class*="st-key-quit_ano_"] [data-baseweb="button-group"] {
  display: grid !important; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: .375rem !important; width: 100%; }
@media (max-width: 640px) {
  [class*="st-key-quit_ano_"] [data-baseweb="button-group"] { grid-template-columns: repeat(6, minmax(0, 1fr)); } }
[class*="st-key-quit_ano_"] [data-testid="stButtonGroup"] button {
  position: relative; width: 100%; min-width: 0; margin: 0 !important; min-height: 2.5rem;
  border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important; justify-content: center; }
[class*="st-key-quit_ano_"] button[data-testid="stBaseButton-pills"] {
  background: #FFFFFF !important; border: 1px solid #AEB5C0 !important; color: #0A1628 !important; }
[class*="st-key-quit_ano_"] button[data-testid="stBaseButton-pillsActive"] {
  background: #1C2B4A !important; border: 1px solid #1C2B4A !important; color: #FFFFFF !important; }
/* O CSS global pinta todo span; o rótulo da pill fica dentro de span e p. */
[class*="st-key-quit_ano_"] [data-testid="stButtonGroup"] button :is(span, p, div) {
  color: inherit !important; font-weight: inherit !important; }
[class*="st-key-quit_ano_"] [data-testid="stButtonGroup"] button:focus-visible { outline: 2px solid #0A1628 !important; outline-offset: 2px; }
</style>
"""


def _plural(n, singular, plural):
    return singular if n == 1 else plural


def _anos(meses):
    anos = []
    for m in meses:
        ano = "20" + m.split("/")[1]
        if ano not in anos:
            anos.append(ano)
    return anos


def _versao():
    return st.session_state.get("quit_versao", 0)


def _chave_ano(ano):
    return f"quit_meses_{ano}_v{_versao()}"


def _limpar_caderneta(meses):
    """Descarta as seleções pendentes: os pills voltam ao estado salvo.

    Apagar a chave do widget não basta — o navegador reenvia o valor antigo no
    rerun e a caderneta mostraria como pendente o mês que acabou de ser gravado.
    Trocar a versão das chaves cria widgets novos, que nascem do estado salvo.
    """
    st.session_state["quit_versao"] = _versao() + 1


def _lista(meses):
    if len(meses) == 1:
        return meses[0]
    if len(meses) <= 4:
        return ", ".join(meses[:-1]) + " e " + meses[-1]
    return ", ".join(meses[:3]) + f" e mais {len(meses) - 3}"


def _gravar(marcar, reabrir, rotulo, meses, salvar_fn):
    quitados = st.session_state.meses_quitados
    st.session_state.quitacao_undo = list(quitados)
    st.session_state.quitacao_undo_label = rotulo
    for m in marcar:
        if m not in quitados:
            quitados.append(m)
    for m in reabrir:
        if m in quitados:
            quitados.remove(m)
    salvar_fn()  # 1 gravação para N meses
    _limpar_caderneta(meses)


# ==========================================================================
# 1) O que está em aberto agora
# ==========================================================================
def _topo(meses, totais, salvar_fn):
    quitados = st.session_state.meses_quitados
    hoje = _mes_de_hoje(meses)
    i_hoje = meses.index(hoje)
    abertos = [m for m in meses[:i_hoje + 1] if m not in quitados]

    if abertos:
        atrasado = any(m != hoje for m in abertos)
        status = ("atraso", "Em atraso") if atrasado else ("pendente", "Pendente")
        if len(abertos) == 1:
            m = abertos[0]
            titulo = f"{_mes_extenso(m).capitalize()} está em aberto"
            texto = f"Acerto de {_valor_texto(totais[m])}" + (", já vencido." if atrasado else ".")
            botao = f"Marcar {m} como quitado"
        else:
            titulo = f"{len(abertos)} meses em aberto"
            soma = sum(totais[m] for m in abertos)
            texto = f"{_lista(abertos)}, somando {_valor_texto(soma)}."
            botao = f"Marcar os {len(abertos)} como quitados"
        alvo, tipo = abertos, "primary"
    else:
        status = ("dia", "Em dia")
        titulo = f"Tudo quitado até {_mes_extenso(hoje)}"
        proximo = meses[i_hoje + 1] if i_hoje + 1 < len(meses) else None
        if proximo:
            texto = f"Próximo acerto: {_mes_extenso(proximo)}, {_valor_texto(totais[proximo])}."
            alvo, botao, tipo = [proximo], f"Marcar {proximo} como quitado", "secondary"
        else:
            texto = "Não há meses seguintes no período."
            alvo, botao, tipo = [], "", "secondary"

    with st.container(key="quit_topo"):
        st.html(
            '<div class="quit">'
            f'<span class="quit-status quit-status--{status[0]}">{status[1]}</span>'
            f'<h2 class="quit-titulo">{html.escape(titulo)}</h2>'
            f'<div class="quit-texto">{html.escape(texto)}</div>'
            "</div>"
        )
        liberado = True
        if len(alvo) >= LIMIAR_CONFIRMACAO:
            liberado = st.checkbox(f"Confirmo quitar {len(alvo)} meses de uma vez",
                                   key=f"quit_topo_confirma_v{_versao()}")
        with st.container(horizontal=True, gap="small"):
            if alvo and st.button(botao, type=tipo, disabled=not liberado, key="quit_topo_acao"):
                rotulo = f"{_lista(alvo)} {_plural(len(alvo), 'quitado', 'quitados')}"
                _gravar(alvo, [], rotulo, meses, salvar_fn)
                st.toast(f"{_lista(alvo)} {_plural(len(alvo), 'marcado como quitado', 'marcados como quitados')}",
                         icon="✅")
                st.rerun()
            if st.session_state.quitacao_undo is not None:
                if st.button(f"Desfazer: {st.session_state.quitacao_undo_label}",
                             type="tertiary", key="quit_desfazer"):
                    if _desfazer(salvar_fn):
                        _limpar_caderneta(meses)
                        st.toast("Alteração desfeita", icon="↩️")
                        st.rerun()


# ==========================================================================
# 2) Caderneta: todos os meses, por ano — também quita e reabre em lote
# ==========================================================================
_HTML_CABECA = (
    '<div class="quit"><div class="quit-cabeca">'
    '<h3 class="quit-sub">Controle de quitação</h3>'
    '<ul class="quit-legenda">'
    '<li><span class="quit-chave quit-chave--quitado"></span>Quitado</li>'
    '<li><span class="quit-chave quit-chave--aberto"></span>Em aberto</li>'
    '<li><span class="quit-chave quit-chave--atraso"></span>Em atraso</li>'
    '<li><span class="quit-chave quit-chave--hoje"></span>Mês atual</li>'
    '<li><span class="quit-chave quit-chave--alterado"></span>Alteração sem salvar</li>'
    "</ul></div>"
    '<div class="quit-dica">Toque num mês para quitar ou reabrir. Nada é gravado até você salvar.</div>'
    "</div>"
)


def _css_estados(ano, do_ano, selecionados, quitados, i_hoje, meses):
    """CSS por posição: atraso, mês atual e alteração pendente em cada pill."""
    regras = []
    base = f".st-key-quit_ano_{ano} [data-testid=\"stButtonGroup\"] button:nth-of-type"
    for pos, m in enumerate(do_ano, start=1):
        alvo = f"{base}({pos})"
        i = meses.index(m)
        if m in selecionados and m not in quitados or m in quitados and m not in selecionados:
            regras.append(f"{alvo}{{border:2px dashed #A88B4A !important;}}")
        elif i < i_hoje and m not in selecionados:
            regras.append(
                f"{alvo}{{border-color:#9A2B1E !important;color:#9A2B1E !important;position:relative;}}"
                f"{alvo}::after{{content:'';position:absolute;top:5px;right:5px;width:7px;height:7px;"
                "border-radius:50%;background:#9A2B1E;}"
            )
        if i == i_hoje:
            regras.append(f"{alvo}{{box-shadow:0 0 0 2px #F8F6F3,0 0 0 3.5px #0A1628 !important;}}")
    return "".join(regras)


@st.fragment
def _caderneta(meses, totais, salvar_fn):
    _init_state()
    quitados = set(st.session_state.meses_quitados) & set(meses)
    i_hoje = meses.index(_mes_de_hoje(meses))

    st.html(_HTML_CABECA)

    selecionados = set()
    estilos = []
    for ano in _anos(meses):
        do_ano = [m for m in meses if m.endswith("/" + ano[2:])]
        salvos = [m for m in do_ano if m in quitados]
        with st.container(key=f"quit_ano_{ano}"):
            st.html(
                '<div class="quit"><div class="quit-ano">'
                f'<span class="quit-ano-nome">{ano}</span>'
                f'<span class="quit-ano-conta">{len(salvos)} de {len(do_ano)} quitados</span>'
                "</div></div>"
            )
            escolha = st.pills(
                f"Meses quitados em {ano}",
                do_ano,
                selection_mode="multi",
                default=salvos,
                format_func=lambda m: m.split("/")[0],
                key=_chave_ano(ano),
                label_visibility="collapsed",
                width="stretch",
            )
        selecionados |= set(escolha or [])
        estilos.append(_css_estados(ano, do_ano, set(escolha or []), quitados, i_hoje, meses))

    st.html(f"<style>{''.join(estilos)}</style>")

    marcar = [m for m in meses if m in selecionados and m not in quitados]
    reabrir = [m for m in meses if m in quitados and m not in selecionados]
    n = len(marcar) + len(reabrir)
    if n == 0:
        return

    partes = []
    if marcar:
        partes.append(f"quitar {_lista(marcar)} ({_valor_texto(sum(totais[m] for m in marcar))})")
    if reabrir:
        partes.append(f"reabrir {_lista(reabrir)}")

    with st.container(key="quit_pendente"):
        st.html(
            '<div class="quit"><div class="quit-pendente-texto">'
            f"<b>{n} {_plural(n, 'alteração sem salvar', 'alterações sem salvar')}:</b> "
            f"{html.escape(' e '.join(partes))}."
            "</div></div>"
        )
        liberado = True
        if n >= LIMIAR_CONFIRMACAO:
            liberado = st.checkbox(f"Confirmo alterar {n} meses de uma vez",
                                   key=f"quit_lote_confirma_v{_versao()}")
        with st.container(horizontal=True, gap="small"):
            salvar = st.button("Salvar alterações", type="primary", disabled=not liberado,
                               key="quit_lote_salvar")
            descartar = st.button("Descartar", key="quit_lote_descartar")

    if descartar:
        _limpar_caderneta(meses)
        st.toast("Alterações descartadas", icon="🗑️")
        _rerun_local()

    if salvar:
        rotulo = f"{n} {_plural(n, 'mês alterado', 'meses alterados')}"
        _gravar(marcar, reabrir, rotulo, meses, salvar_fn)
        resumo = []
        if marcar:
            resumo.append(f"{len(marcar)} {_plural(len(marcar), 'quitado', 'quitados')}")
        if reabrir:
            resumo.append(f"{len(reabrir)} {_plural(len(reabrir), 'reaberto', 'reabertos')}")
        st.toast("Alterações salvas: " + " e ".join(resumo), icon="✅")
        st.rerun()  # full: Gestão Executiva e Extrato também leem meses_quitados


# ==========================================================================
# 3) Parcelas por item
# ==========================================================================
def _html_itens(itens, tab, meses):
    esc = html.escape
    quitados = set(st.session_state.meses_quitados)
    i_hoje = meses.index(_mes_de_hoje(meses))
    ativos, encerrados = [], []

    for item in itens:
        valor = float(item.get("valor") or 0)
        if item["id"] not in tab.columns or valor <= 0:
            continue
        serie = tab[item["id"]]
        com_valor = [m for m in meses if float(serie[m]) > 0.005]
        if not com_valor:
            continue

        total = max(round(float(serie.sum()) / valor), 1)
        pagas = min(round(sum(float(serie[m]) for m in com_valor if m in quitados) / valor), total)
        primeiro, ultimo = com_valor[0], com_valor[-1]
        contrato = item.get("contrato") or {}
        recorrente = bool(contrato) and not contrato.get("total_parcelas")

        if pagas >= total and meses.index(ultimo) <= i_hoje:
            encerrados.append(item["nome"])
            continue
        if meses.index(primeiro) > i_hoje:
            detalhe = f"começa em {primeiro}" if recorrente else f"{total} parcelas, começa em {primeiro}"
        elif recorrente:
            detalhe = f"{pagas} de {total} meses quitados, até {ultimo}"
        elif total == 1:
            detalhe = f"parcela única, em {ultimo}"
        else:
            detalhe = f"{pagas} de {total} pagas, termina em {ultimo}"

        sinal = "− " if item["tipo"] != "credito" else ""
        ativos.append({
            "nome": item["nome"], "detalhe": detalhe, "fim": meses.index(ultimo),
            "valor": f"{sinal}R$ {_brl(valor)} por mês",
            "fracao": pagas / total, "rotulo": f"{pagas} de {total}",
        })

    ativos.sort(key=lambda a: a["fim"])

    if ativos:
        linhas = "".join(
            '<li class="quit-linha"><div class="quit-linha-topo">'
            f'<span class="quit-nome">{esc(a["nome"])}</span>'
            f'<span class="quit-valor">{a["valor"]}</span></div>'
            f'<span class="quit-medidor" role="img" aria-label="{a["rotulo"]}">'
            f'<span class="quit-medidor-cheio" style="width:{a["fracao"] * 100:.1f}%"></span></span>'
            f'<div class="quit-detalhe">{esc(a["detalhe"])}</div></li>'
            for a in ativos
        )
        corpo = f'<ul class="quit-lista">{linhas}</ul>'
    else:
        corpo = '<div class="quit-detalhe">Nenhum item com parcelas em andamento.</div>'

    rodape = ""
    if encerrados:
        rodape = ('<div class="quit-encerrados">Já quitados por completo: '
                  f"{esc(', '.join(encerrados))}.</div>")

    return (
        '<div class="quit"><section class="quit-itens">'
        '<h3 class="quit-sub">Parcelas por item</h3>'
        '<div class="quit-nota">Valores com sinal de menos abatem do que a Ana recebe. '
        "Para cadastrar ou editar itens, use Gerenciar Itens.</div>"
        f"{corpo}{rodape}</section></div>"
    )


# ==========================================================================
# Entrada chamada por app.py
# ==========================================================================
def exibir_detalhamento_mensal(itens, df_calculado, salvar_fn):
    """Aba Detalhamento Mensal: quitar meses e acompanhar as parcelas."""
    meses = list(df_calculado["mesAno"])
    if not meses:
        st.info("Nenhum mês cadastrado. Adicione itens em Gerenciar Itens.")
        return

    _init_state()
    st.html(_CSS)

    tab = df_calculado.set_index("mesAno")
    totais = {m: float(tab.at[m, "total"]) for m in meses}

    _topo(meses, totais, salvar_fn)
    _caderneta(meses, totais, salvar_fn)
    st.html(_html_itens(itens, tab, meses))
