# quitacao_ui.py — Controle de Quitação (UX)
"""
Painel de quitação do Dashboard Ana.

Princípios de UX aplicados:
  - INTUITIVIDADE: a ação vive ao lado do indicador que ela altera (STATUS DO MÊS),
    com rótulo verbal explícito ("Marcar como quitado" / "Reabrir mês").
  - SEGURANÇA: no modo em lote nada é gravado no clique da caixa. As marcações ficam
    em staging, com resumo do que vai mudar; a partir de LIMIAR_CONFIRMACAO alterações
    exige confirmação explícita. Toda gravação guarda snapshot para "Desfazer".
  - FEEDBACK: st.toast na gravação + coluna "Situação salva" que distingue o estado
    já persistido da intenção pendente.
  - EFICIÊNCIA: o painel em lote roda em @st.fragment (filtro/ano/editor sem
    recarregar gráficos) e grava N meses com UMA chamada a salvar_dados
    (= 1 push GitHub), em vez de um push por clique. Toda GRAVAÇÃO faz rerun
    completo: meses_quitados é lido por KPIs, Progresso, Extrato e Gestão Executiva.
"""

import streamlit as st
import pandas as pd

# A partir de quantas alterações simultâneas exigimos confirmação explícita.
LIMIAR_CONFIRMACAO = 5


def _fmt_brl(x):
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _rerun_local():
    """Rerun só deste fragment quando possível; caso contrário, rerun completo.

    st.rerun(scope="fragment") só é aceito DURANTE um fragment rerun. Na primeira
    interação (ainda dentro do run completo do script) ele levanta
    StreamlitInvalidLayoutContextError — daí o fallback.
    """
    try:
        st.rerun(scope="fragment")
    except Exception:
        st.rerun()

def _init_state():
    st.session_state.setdefault("quitacao_undo", None)
    st.session_state.setdefault("quitacao_undo_label", "")


def _desfazer(salvar_fn):
    snapshot = st.session_state.quitacao_undo
    if snapshot is None:
        return False
    st.session_state.meses_quitados = list(snapshot)
    st.session_state.quitacao_undo = None
    st.session_state.quitacao_undo_label = ""
    salvar_fn()
    return True


# ==========================================================================
# 1) Status + toggle do mês selecionado  (fica dentro da coluna de KPIs)
# ==========================================================================
def bloco_status_mes(mes, total_meses, salvar_fn):
    """KPI de status + ação de quitar/reabrir o mês selecionado.

    NÃO roda em fragment: meses_quitados alimenta o Resumo de Itens (Progresso),
    a Gestão Executiva, o Extrato por ano e o painel em lote. Com rerun local,
    tudo isso ficava mostrando o estado anterior até a próxima interação
    (medido em navegador: Progresso 20/48 antes e 20/48 depois de quitar set/26).
    O custo do rerun completo é menor que uma tela inconsistente.
    """
    _init_state()

    quitados = st.session_state.meses_quitados
    quitado = mes in quitados

    st.metric(
        "Status",
        "Quitado" if quitado else "Pendente",
        delta=f"{len(quitados)}/{total_meses} quitados",
        delta_color="normal" if quitado else "off",
    )

    label = "↩ Reabrir mês" if quitado else "✔ Marcar como quitado"
    if st.button(
        label,
        key=f"toggle_quit_{mes}",
        type="secondary" if quitado else "primary",
        use_container_width=True,
        help=f"Altera apenas {mes}. A ação pode ser desfeita logo abaixo.",
    ):
        st.session_state.quitacao_undo = list(quitados)
        if quitado:
            quitados.remove(mes)
            st.session_state.quitacao_undo_label = f"{mes} reaberto"
            st.toast(f"↩ {mes} reaberto", icon="↩️")
        else:
            quitados.append(mes)
            st.session_state.quitacao_undo_label = f"{mes} quitado"
            st.toast(f"✅ {mes} marcado como quitado", icon="✅")
        salvar_fn()
        st.rerun()  # full: KPIs, Progresso dos itens, extrato e painel em lote

    if st.session_state.quitacao_undo is not None:
        if st.button(
            "Desfazer",
            key=f"undo_quit_{mes}",
            use_container_width=True,
            help=f"Reverte: {st.session_state.quitacao_undo_label}",
        ):
            if _desfazer(salvar_fn):
                st.toast("Alteração desfeita", icon="↩️")
                st.rerun()


# ==========================================================================
# 2) Painel em lote — data_editor com staging + confirmação
# ==========================================================================
@st.fragment
def painel_quitacao(df, salvar_fn):
    """Editor em lote dos meses quitados, com staging e confirmação."""
    _init_state()

    if df.empty or "mesAno" not in df.columns:
        st.info("Sem meses para exibir.")
        return

    anos = sorted({"20" + m.split("/")[1] for m in df["mesAno"]})
    c1, c2 = st.columns([1, 2])
    ano = c1.selectbox("Ano", anos, key="quit_ano")
    filtro = c2.radio(
        "Exibir", ["Todos", "Só pendentes", "Só quitados"],
        horizontal=True, key="quit_filtro", label_visibility="visible",
    )

    sufixo = "/" + ano[2:]
    df_ano = df[df["mesAno"].str.endswith(sufixo)]

    base = pd.DataFrame([
        {
            "Quitado": row["mesAno"] in st.session_state.meses_quitados,
            "Mês": row["mesAno"],
            "Saldo": float(row["total"]),
        }
        for _, row in df_ano.iterrows()
    ])

    if base.empty:
        st.info(f"Nenhum mês cadastrado em {ano}.")
        return

    n_quit = int(base["Quitado"].sum())
    st.caption(
        f"**{ano}:** {n_quit} de {len(base)} meses quitados. "
        "Marque as caixas e clique em **Salvar** — nada é gravado antes disso."
    )

    if filtro == "Só pendentes":
        vis = base[~base["Quitado"]].reset_index(drop=True)
    elif filtro == "Só quitados":
        vis = base[base["Quitado"]].reset_index(drop=True)
    else:
        vis = base.reset_index(drop=True)

    if vis.empty:
        st.info("Nenhum mês neste filtro.")
        return

    vis = vis.assign(
        Situação=vis["Quitado"].map({True: "✅ Quitado", False: "⏳ Pendente"})
    )

    edited = st.data_editor(
        vis,
        key=f"quit_editor_{ano}_{filtro}",
        hide_index=True,
        use_container_width=True,
        column_order=["Quitado", "Mês", "Saldo", "Situação"],
        disabled=["Mês", "Saldo", "Situação"],
        column_config={
            "Quitado": st.column_config.CheckboxColumn(
                "✔ Quitar",
                width="small",
                help="Marque para quitar, desmarque para reabrir. "
                     "Nada é gravado até você clicar em Salvar.",
            ),
            "Mês": st.column_config.TextColumn("Mês", width="small"),
            "Saldo": st.column_config.NumberColumn("Saldo do mês", format="R$ %.2f"),
            "Situação": st.column_config.TextColumn("Situação salva", width="small"),
        },
    )

    antes = set(vis.loc[vis["Quitado"], "Mês"])
    depois = set(edited.loc[edited["Quitado"], "Mês"])
    marcar = sorted(depois - antes)
    reabrir = sorted(antes - depois)
    n = len(marcar) + len(reabrir)

    if n == 0:
        st.caption("_Nenhuma alteração pendente._")
        if st.session_state.quitacao_undo is not None:
            if st.button("↩ Desfazer última alteração", key="undo_lote"):
                if _desfazer(salvar_fn):
                    st.toast("Alteração desfeita", icon="↩️")
                    st.rerun()
        return

    partes = []
    if marcar:
        partes.append(f"**{len(marcar)}** a quitar ({', '.join(marcar[:4])}"
                      + ("…" if len(marcar) > 4 else "") + ")")
    if reabrir:
        partes.append(f"**{len(reabrir)}** a reabrir ({', '.join(reabrir[:4])}"
                      + ("…" if len(reabrir) > 4 else "") + ")")
    st.warning(f"{n} alteração(ões) pendente(s) — " + " · ".join(partes))

    liberado = True
    if n >= LIMIAR_CONFIRMACAO:
        liberado = st.checkbox(
            f"Confirmo alterar {n} meses de uma só vez",
            key=f"confirma_lote_{ano}",
        )

    b1, b2 = st.columns(2)
    salvar = b1.button(
        "Salvar alterações", type="primary", disabled=not liberado,
        use_container_width=True, key=f"salvar_lote_{ano}",
    )
    descartar = b2.button(
        "Descartar", use_container_width=True, key=f"descartar_lote_{ano}",
    )

    if descartar:
        st.session_state.pop(f"quit_editor_{ano}_{filtro}", None)
        st.toast("Alterações descartadas", icon="🗑️")
        _rerun_local()

    if salvar:
        st.session_state.quitacao_undo = list(st.session_state.meses_quitados)
        st.session_state.quitacao_undo_label = f"{n} mês(es) em {ano}"

        quitados = st.session_state.meses_quitados
        for m in marcar:
            if m not in quitados:
                quitados.append(m)
        for m in reabrir:
            if m in quitados:
                quitados.remove(m)

        salvar_fn()  # 1 gravação para N meses (1 push GitHub, não N)

        valor = float(base.loc[base["Mês"].isin(marcar + reabrir), "Saldo"].abs().sum())
        st.toast(
            f"✅ {len(marcar)} quitado(s) · {len(reabrir)} reaberto(s) — "
            f"{_fmt_brl(valor)} movimentados",
            icon="✅",
        )
        st.rerun()  # full: atualiza KPIs, progresso dos itens e gráficos
