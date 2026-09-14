"""
Gestão Executiva — o acerto do mês entre você e a Ana.

A aba responde, nesta ordem:
  1. Quanto é o acerto do mês escolhido, para quem, e se já foi quitado.
  2. De onde vem esse valor: a conta armada, item por item.
  3. Quando o valor muda: itens que entram ou saem da conta.
  4. Como o acerto se distribui ao longo de todo o período.

Crédito soma (a Ana recebe) e débito abate. O SINAL carrega essa diferença; a cor
fica reservada ao status do mês. A ação de quitar continua só em Detalhamento
Mensal — aqui o status é apenas exibido, com o caminho para alterá-lo.
"""

import html
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend_antecipacao import AntecipacaoService

NOMES_MES = ["jan", "fev", "mar", "abr", "mai", "jun",
             "jul", "ago", "set", "out", "nov", "dez"]
NOMES_MES_LONGOS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

# Tokens (mesma paleta Marinho + Dourado de streamlit_custom_styles.py)
TINTA = "#0A1628"
TEXTO_2 = "#5F6673"        # 4,5:1+ tanto no branco quanto no creme
FONTE = "DM Sans, -apple-system, Segoe UI, sans-serif"
BARRA_QUITADO = "#7D8796"  # >= 3:1 no creme
BARRA_ABERTO = "#BEC5CF"   # abaixo de 3:1: valores também no tooltip e na tabela
GRADE = "#E5E0D8"
GUIA = "#CFC8BD"


class GestaoExecutiva:
    """Cálculo do resultado mensal (usado também por teste_gestao_executiva.py)."""

    def __init__(self, itens, meses_quitados, df_calculado):
        self.itens = itens
        self.meses_quitados = meses_quitados
        self.df = df_calculado
        self.antecipacao_service = AntecipacaoService()

    def formatar_moeda(self, valor):
        """Formata valor para moeda brasileira"""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def calcular_resultado_mensal(self, mes_ano):
        """Calcula o resultado financeiro de um mês específico"""
        if mes_ano not in self.df['mesAno'].values:
            return None

        mes_data = self.df[self.df['mesAno'] == mes_ano].iloc[0]

        receitas = 0
        despesas = 0
        for item in self.itens:
            col_name = item["id"]
            valor = mes_data[col_name] if col_name in mes_data else 0
            if item["tipo"] == "credito":
                receitas += valor
            else:
                despesas += valor

        antecipacoes_mes = self._calcular_antecipacoes_mes(mes_ano)

        return {
            'mes': mes_ano,
            'receitas': receitas,
            'despesas': abs(despesas),
            'saldo_liquido': receitas - abs(despesas),
            'antecipacoes_recebidas': antecipacoes_mes['recebidas'],
            'antecipacoes_enviadas': antecipacoes_mes['enviadas'],
            'status_quitacao': mes_ano in self.meses_quitados
        }

    def _calcular_antecipacoes_mes(self, mes_ano):
        """Calcula antecipações recebidas e enviadas no mês"""
        antecipacoes = self.antecipacao_service.listar_antecipacoes(status="confirmada")

        recebidas = 0
        enviadas = 0
        for ant in antecipacoes:
            if ant['destino'] == mes_ano:
                recebidas += ant['valor_antecipado']
            if ant['origem'] == mes_ano:
                enviadas += ant['valor_antecipado']

        return {'recebidas': recebidas, 'enviadas': enviadas}


# ==========================================================================
# Regras de apresentação
# ==========================================================================
def _brl(valor):
    """1067.88 -> '1.067,88' (sem sinal e sem R$)."""
    return f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _valor_texto(valor):
    return f"− R$ {_brl(valor)}" if valor < -0.005 else f"R$ {_brl(valor)}"


def _mes_extenso(mes):
    nome, ano = mes.split("/")
    return f"{NOMES_MES_LONGOS[NOMES_MES.index(nome)]} de 20{ano}"


def _mes_de_hoje(meses):
    """Mês corrente no formato 'set/26'; fora do período, a ponta mais próxima."""
    hoje = datetime.now()
    rotulo = f"{NOMES_MES[hoje.month - 1]}/{str(hoje.year)[2:]}"
    if rotulo in meses:
        return rotulo
    primeiro_ano = 2000 + int(meses[0].split("/")[1])
    return meses[0] if hoje.year < primeiro_ano else meses[-1]


def _meses_entre(meses, inicio, fim):
    try:
        return meses[meses.index(inicio):meses.index(fim) + 1]
    except ValueError:
        return []


def _antecipacoes(item, campo, mes):
    return [a for a in item.get("antecipacoes", [])
            if a.get("status") == "confirmada" and a.get(campo) == mes]


def _detalhe_item(item, mes, meses):
    """Linha secundária do item: em que parcela está, ou o que foi antecipado."""
    antecipadas = sorted(
        (a["origem"] for a in _antecipacoes(item, "destino", mes)),
        key=lambda m: meses.index(m) if m in meses else len(meses),
    )
    if antecipadas:
        qtd = "1 parcela antecipada" if len(antecipadas) == 1 else f"{len(antecipadas)} parcelas antecipadas"
        return f"{qtd}: {', '.join(antecipadas)}"

    contrato = item.get("contrato") or {}
    # total_parcelas = 0 marca item recorrente (ex.: Plano de Saúde).
    if contrato and not contrato.get("total_parcelas"):
        return f"mensal, até {item['fim']}"

    # Mesma regra do Extrato Mensal: mapeamento (já deslocado) antes do período.
    mapeamento = (item.get("cronograma") or {}).get("mapeamento") or {}
    for info in mapeamento.values():
        if info.get("vencimento_atual") == mes and info.get("status") != "antecipada":
            if contrato["total_parcelas"] == 1:
                return "parcela única"
            return f"parcela {info['numero']} de {contrato['total_parcelas']}"

    ativos = _meses_entre(meses, item["inicio"], item["fim"])
    if mes in ativos:
        if len(ativos) == 1:
            return "parcela única"
        return f"parcela {ativos.index(mes) + 1} de {len(ativos)}"
    return ""


def _linhas_do_mes(itens, tab, mes, meses):
    linhas = []
    for item in itens:
        if item["id"] not in tab.columns:
            continue
        valor = float(tab.at[mes, item["id"]])
        if valor <= 0:
            continue
        sinal = 1 if item["tipo"] == "credito" else -1
        linhas.append({
            "nome": item["nome"],
            "detalhe": _detalhe_item(item, mes, meses),
            "valor": sinal * valor,
        })
    # Créditos primeiro, depois abatimentos; maiores no topo de cada bloco.
    linhas.sort(key=lambda l: (l["valor"] < 0, -abs(l["valor"])))
    return linhas


def _status(mes, quitados, meses, mes_hoje):
    """(chave, rótulo) do mês: quitado, em atraso, pendente ou a vencer."""
    if mes in quitados:
        return "quitado", "Quitado"
    i, hoje = meses.index(mes), meses.index(mes_hoje)
    if i < hoje:
        return "atraso", "Em atraso"
    if i == hoje:
        return "pendente", "Pendente"
    return "futuro", "A vencer"


def _motivo(item, tab, antes, agora):
    va = float(tab.at[antes, item["id"]])
    vb = float(tab.at[agora, item["id"]])
    if abs(vb - va) < 0.005:
        return None
    nome = item["nome"]
    if vb > va and _antecipacoes(item, "destino", agora):
        return f"{nome}: entram parcelas antecipadas"
    if vb < va and _antecipacoes(item, "origem", agora):
        return f"{nome}: parcela já foi antecipada"
    if vb < va and _antecipacoes(item, "destino", antes):
        return f"{nome} volta ao valor normal"
    if vb > va and _antecipacoes(item, "origem", antes):
        return f"{nome} volta à conta"
    if va <= 0:
        return f"{nome} entra na conta"
    if vb <= 0:
        return f"{nome} sai da conta"
    return f"{nome} muda de valor"


def _mudancas(itens, tab, mes, meses, limite=4):
    """Próximos meses, depois do escolhido, em que o valor do acerto muda."""
    eventos = []
    colunas = [i for i in itens if i["id"] in tab.columns]
    for i in range(meses.index(mes) + 1, len(meses)):
        antes, agora = meses[i - 1], meses[i]
        dif = float(tab.at[agora, "total"]) - float(tab.at[antes, "total"])
        if abs(dif) < 0.005:
            continue
        motivos = [m for m in (_motivo(item, tab, antes, agora) for item in colunas) if m]
        eventos.append({"mes": agora, "motivos": motivos,
                        "total": float(tab.at[agora, "total"]), "dif": dif})
        if len(eventos) >= limite:
            break
    return eventos


# ==========================================================================
# HTML
# ==========================================================================
# st.html sanitiza o conteúdo (SVG inline é removido) e o CSS global do app
# pinta todo <span>/<p> sem classe — por isso: sem <p>, todo <span> com classe,
# e ícones de status desenhados em CSS.
_CSS = """
<style>
.acerto { font-family: 'DM Sans', -apple-system, 'Segoe UI', sans-serif; color: #0A1628; }
.acerto-grade { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 2.5rem; align-items: start; }
@media (max-width: 900px) { .acerto-grade { grid-template-columns: minmax(0, 1fr); gap: 2rem; } }

.acerto-conta { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.75rem 2rem 1.5rem; }
@media (max-width: 560px) { .acerto-conta { padding: 1.25rem 1rem 1.125rem; } }

.acerto h2.acerto-titulo, .acerto h3.acerto-subtitulo {
  font-family: 'Playfair Display', Georgia, serif !important; font-weight: 600 !important;
  color: #0A1628 !important; letter-spacing: -0.01em !important; padding: 0 !important; }
.acerto h2.acerto-titulo { font-size: 1.625rem !important; line-height: 1.2 !important; margin: 0 0 .75rem !important; }
.acerto h3.acerto-subtitulo { font-size: 1.125rem !important; line-height: 1.3 !important; margin: 0 0 .875rem !important; }

.acerto-sr { position: absolute !important; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

.acerto-tabela { width: 100%; border-collapse: collapse; }
.acerto-tabela th, .acerto-tabela td { padding: .75rem 0; border-bottom: 1px solid #EEF0F3; text-align: left; vertical-align: baseline; }
.acerto-tabela tr:last-child th, .acerto-tabela tr:last-child td { border-bottom: 0; }
.acerto-item { font-size: 1rem; font-weight: 500; color: #0A1628; line-height: 1.35; }
.acerto-detalhe { display: block; margin-top: .125rem; font-size: .8125rem; font-weight: 400; color: #5F6673; }
.acerto-valor { text-align: right !important; white-space: nowrap; padding-left: 1rem !important; font-size: 1rem; color: #0A1628; font-variant-numeric: tabular-nums; }

.acerto-total { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: .75rem 1.5rem; margin-top: .25rem; padding-top: 1.125rem; border-top: 1px solid #0A1628; }
.acerto-rotulo { font-size: .9375rem; font-weight: 500; color: #374151; margin-bottom: .125rem; }
.acerto-numero { font-size: clamp(2.5rem, 5.5vw, 3.5rem); font-weight: 600; line-height: 1.15; letter-spacing: -0.02em; color: #0A1628; white-space: nowrap; }
.acerto-numero .acerto-moeda { font-size: .42em; font-weight: 500; letter-spacing: 0; color: #5F6673; margin-right: .3em; }
/* Traço duplo sob o total final: convenção contábil, só no número. */
.acerto-numero .acerto-cifra { color: #0A1628; font-variant-numeric: proportional-nums;
  text-decoration-line: underline; text-decoration-style: double; text-decoration-color: #C9A96E;
  text-decoration-thickness: 2px; text-underline-offset: .16em; text-decoration-skip-ink: none; }

.acerto-status { display: inline-flex; align-items: center; gap: .45rem; padding: .4rem .75rem; border-radius: 999px; font-size: .8125rem; font-weight: 600; line-height: 1; white-space: nowrap; margin-bottom: .625rem; }
.acerto-status::before { content: ""; flex: none; box-sizing: border-box; }
.acerto-status--quitado { color: #0B6B4B; background: #E7F5EE; }
.acerto-status--quitado::before { content: "✓"; font-size: .9375rem; font-weight: 700; }
.acerto-status--pendente { color: #8A4B06; background: #FDF1DC; }
.acerto-status--pendente::before { width: 11px; height: 11px; border: 2px solid currentColor; border-radius: 50%; }
.acerto-status--atraso { color: #9A2B1E; background: #FBE9E6; }
.acerto-status--atraso::before { content: "!"; width: 15px; height: 15px; border-radius: 50%; background: #9A2B1E; color: #FBE9E6; font-size: .6875rem; font-weight: 700; line-height: 15px; text-align: center; }
.acerto-status--futuro { color: #4B5563; background: #F1F3F5; }
.acerto-status--futuro::before { width: 10px; height: 10px; border: 2px solid currentColor; border-radius: 2px; }
.acerto-nota { margin-top: 1rem; font-size: .8125rem; color: #5F6673; }
.acerto-nota b { font-weight: 600; color: #374151; }

.acerto-mudancas { padding-top: 1.75rem; }
@media (max-width: 900px) { .acerto-mudancas { padding-top: 0; } }
.acerto-eventos { list-style: none; margin: 0; padding: 0; }
.acerto-evento { display: grid; grid-template-columns: 3.75rem minmax(0, 1fr); gap: .75rem; padding: .875rem 0; border-top: 1px solid #E5E0D8; margin: 0; }
.acerto-evento:first-child { border-top: 0; padding-top: .125rem; }
.acerto-quando { font-size: .875rem; font-weight: 600; color: #0A1628; line-height: 1.45; }
.acerto-motivo { font-size: .9375rem; color: #0A1628; line-height: 1.45; }
.acerto-efeito { font-size: .8125rem; color: #5F6673; margin-top: .25rem; font-variant-numeric: tabular-nums; }
.acerto-vazio { font-size: .9375rem; color: #5F6673; line-height: 1.5; max-width: 34ch; }

.acerto-grafico-topo { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: .25rem 1.5rem; margin-top: 2.75rem; }
.acerto-legenda { display: flex; flex-wrap: wrap; gap: .375rem 1.25rem; list-style: none; margin: 0 0 .25rem; padding: 0; font-size: .8125rem; color: #5F6673; }
.acerto-legenda li { display: inline-flex; align-items: center; gap: .45rem; margin: 0; }
.acerto-chave { display: inline-block; width: 10px; height: 10px; border-radius: 2px; }
.acerto-chave--escolhido { background: #0A1628; }
.acerto-chave--quitado { background: #7D8796; }
.acerto-chave--aberto { background: #BEC5CF; }

/* Valor sobre o controle deslizante: o dourado do tema não tem contraste para texto. */
[data-testid="stSliderThumbValue"] { color: #0A1628 !important; font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; }
</style>
"""


def _html_conta(mes, linhas, total, status):
    esc = html.escape
    if linhas:
        corpo = "".join(
            '<tr><th scope="row" class="acerto-item">' + esc(l["nome"])
            + (f'<span class="acerto-detalhe">{esc(l["detalhe"])}</span>' if l["detalhe"] else "")
            + '</th><td class="acerto-valor">'
            + ("− " if l["valor"] < 0 else "") + _brl(l["valor"]) + "</td></tr>"
            for l in linhas
        )
        itens = (
            '<table class="acerto-tabela"><caption class="acerto-sr">'
            f"Itens do acerto de {esc(mes)}. Créditos somam, débitos abatem.</caption>"
            f"<tbody>{corpo}</tbody></table>"
        )
    else:
        itens = '<div class="acerto-vazio">Nenhum item entra na conta neste mês.</div>'

    if total > 0.005:
        rotulo = "Ana recebe"
    elif total < -0.005:
        rotulo = "Ana paga"
    else:
        rotulo = "Nada a acertar"

    chave, texto_status = status
    if chave == "quitado":
        nota = "Para reabrir o mês, use <b>Detalhamento Mensal</b>."
    else:
        nota = "Para marcar como quitado, use <b>Detalhamento Mensal</b>."

    return (
        '<div class="acerto-conta">'
        f'<h2 class="acerto-titulo">Acerto de {_mes_extenso(mes)}</h2>'
        f"{itens}"
        '<div class="acerto-total">'
        f'<div><div class="acerto-rotulo">{rotulo}</div>'
        '<div class="acerto-numero"><span class="acerto-moeda">R$</span>'
        f'<span class="acerto-cifra">{_brl(total)}</span></div></div>'
        f'<div class="acerto-status acerto-status--{chave}">{texto_status}</div>'
        "</div>"
        f'<div class="acerto-nota">{nota}</div>'
        "</div>"
    )


def _html_mudancas(eventos, total_atual, ultimo_mes):
    esc = html.escape
    if eventos:
        corpo = '<ol class="acerto-eventos">' + "".join(
            '<li class="acerto-evento">'
            f'<div class="acerto-quando">{esc(e["mes"])}</div><div>'
            + "".join(f'<div class="acerto-motivo">{esc(m)}</div>' for m in e["motivos"])
            + f'<div class="acerto-efeito">Acerto passa a {_valor_texto(e["total"])} '
            f'({"+" if e["dif"] > 0 else "−"} {_brl(e["dif"])})</div>'
            "</div></li>"
            for e in eventos
        ) + "</ol>"
    else:
        corpo = (f'<div class="acerto-vazio">Nenhuma mudança até {esc(ultimo_mes)}. '
                 f"O acerto fica em {_valor_texto(total_atual)} por mês.</div>")
    return ('<section class="acerto-mudancas">'
            f'<h3 class="acerto-subtitulo">Quando o acerto muda</h3>{corpo}</section>')


_HTML_GRAFICO_TOPO = (
    '<div class="acerto"><div class="acerto-grafico-topo">'
    '<h3 class="acerto-subtitulo">Acerto mês a mês</h3>'
    '<ul class="acerto-legenda">'
    '<li><span class="acerto-chave acerto-chave--escolhido"></span>Mês escolhido</li>'
    '<li><span class="acerto-chave acerto-chave--quitado"></span>Quitado</li>'
    '<li><span class="acerto-chave acerto-chave--aberto"></span>Em aberto</li>'
    "</ul></div></div>"
)


def _grafico(tab, meses, mes, situacoes):
    valores = [float(tab.at[m, "total"]) for m in meses]
    cores = [TINTA if m == mes else (BARRA_QUITADO if s[0] == "quitado" else BARRA_ABERTO)
             for m, s in zip(meses, situacoes)]

    topo = max(valores + [0.0]) * 1.06 or 1.0
    base = min(valores + [0.0]) * 1.1

    fig = go.Figure(go.Bar(
        x=meses,
        y=valores,
        marker=dict(color=cores, line=dict(width=0)),
        customdata=[[_valor_texto(v), s[1].lower()] for v, s in zip(valores, situacoes)],
        hovertemplate="<b>%{customdata[0]}</b><br>%{x}, %{customdata[1]}<extra></extra>",
    ))

    # Rótulo direto só no mês escolhido, no topo do gráfico (nunca sobre barras
    # vizinhas mais altas), ligado à barra por uma guia fina.
    i = meses.index(mes)
    v = valores[i]
    ancora = "left" if i < 4 else ("right" if i > len(meses) - 5 else "center")
    fig.add_shape(type="line", x0=mes, x1=mes, y0=v, y1=topo, layer="below",
                  line=dict(color=GUIA, width=1))
    fig.add_annotation(
        x=mes, y=1, yref="paper", yanchor="bottom", xanchor=ancora, yshift=4,
        text=f"<b>{_valor_texto(v)}</b>", showarrow=False,
        font=dict(family=FONTE, size=13, color=TINTA),
    )

    anos = [m for m in meses if m.startswith("jan/")]
    fig.update_layout(
        height=280,
        margin=dict(l=4, r=4, t=28, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONTE, size=12, color=TEXTO_2),
        separators=",.",
        bargap=0.35,
        barcornerradius=4,
        showlegend=False,
        dragmode=False,
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E5E7EB",
                        font=dict(family=FONTE, size=13, color=TINTA)),
        xaxis=dict(type="category", tickmode="array", tickvals=anos,
                   ticktext=["20" + m[-2:] for m in anos], showgrid=False,
                   showline=False, ticks="", fixedrange=True,
                   tickfont=dict(family=FONTE, size=12, color=TEXTO_2)),
        yaxis=dict(showgrid=True, gridcolor=GRADE, gridwidth=1, zeroline=True,
                   zerolinecolor=GUIA, zerolinewidth=1, tickformat=",.0f",
                   nticks=5, fixedrange=True, automargin=True, range=[base, topo],
                   tickfont=dict(family=FONTE, size=12, color=TEXTO_2)),
    )
    return fig


# ==========================================================================
# Entrada chamada por app.py
# ==========================================================================
def exibir_gestao_executiva(itens, meses_quitados, df_calculado):
    """Aba Gestão Executiva: o acerto do mês, sua composição e sua trajetória."""
    meses = list(df_calculado["mesAno"])
    if not meses:
        st.info("Nenhum mês cadastrado. Adicione itens em Gerenciar Itens.")
        return

    mes_hoje = _mes_de_hoje(meses)
    if st.session_state.get("mes_executivo") not in meses:
        st.session_state["mes_executivo"] = mes_hoje

    st.html(_CSS)

    col_mes, _ = st.columns([3, 2])
    with col_mes:
        mes = st.select_slider("Mês do acerto", options=meses, key="mes_executivo")

    tab = df_calculado.set_index("mesAno")
    total = float(tab.at[mes, "total"])
    situacoes = [_status(m, meses_quitados, meses, mes_hoje) for m in meses]

    st.html(
        '<div class="acerto"><div class="acerto-grade">'
        + _html_conta(mes, _linhas_do_mes(itens, tab, mes, meses), total,
                      situacoes[meses.index(mes)])
        + _html_mudancas(_mudancas(itens, tab, mes, meses), total, meses[-1])
        + "</div></div>"
    )

    st.html(_HTML_GRAFICO_TOPO)
    st.plotly_chart(_grafico(tab, meses, mes, situacoes), use_container_width=True,
                    config={"displayModeBar": False}, key="grafico_acerto")

    with st.expander("Ver valores em tabela"):
        st.dataframe(
            pd.DataFrame({
                "Mês": meses,
                "Acerto": [_valor_texto(float(tab.at[m, "total"])) for m in meses],
                "Situação": [s[1] for s in situacoes],
            }),
            hide_index=True, use_container_width=True, height=320,
        )
