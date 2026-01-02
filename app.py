# app.py - Dashboard Ana
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard Ana",
    page_icon="📊",
    layout="wide"
)

# Caminho do arquivo de dados (opcional, para persistência entre sessões)
DADOS_ARQUIVO = "dados_dashboard_ana.json"

# ========================================
# 1. Geração de todos os meses (jan/25 a dez/28)
# ========================================
def gerar_todos_meses():
    meses = []
    nomes_mes = ["jan", "fev", "mar", "abr", "mai", "jun", 
                 "jul", "ago", "set", "out", "nov", "dez"]
    for ano in range(2025, 2029):
        for mes in nomes_mes:
            meses.append(f"{mes}/{str(ano)[2:]}")
    return meses

MESES_TODOS = gerar_todos_meses()

# ========================================
# 2. Definição dos itens padrão (com prazo)
# ========================================
ITENS_PADRAO = {
    "planoSaude": {
        "nome": "Plano de Saúde",
        "valor": 1518.93,
        "inicio": "jan/25",
        "fim": "dez/28",
        "tipo": "debito"
    },
    "viagemNordeste": {
        "nome": "Viagem Nordeste",
        "valor": 206.50,
        "inicio": "set/25",
        "fim": "jun/26",
        "tipo": "debito"
    },
    "geladeira": {
        "nome": "Geladeira",
        "valor": 152.48,
        "inicio": "jul/25",
        "fim": "jun/27",
        "tipo": "debito"
    },
    "ferro": {
        "nome": "Ferro",
        "valor": 219.99,
        "inicio": "set/25",
        "fim": "dez/26",
        "tipo": "debito"
    }
}

# ========================================
# 3. Funções utilitárias
# ========================================
def get_meses_entre(inicio, fim):
    try:
        i1 = MESES_TODOS.index(inicio)
        i2 = MESES_TODOS.index(fim)
        return MESES_TODOS[i1:i2+1]
    except ValueError:
        return []

def salvar_dados(itens_pers, meses_quit):
    """Salva dados no disco (JSON)"""
    dados = {
        "itens_personalizados": itens_pers,
        "meses_quitados": meses_quit
    }
    with open(DADOS_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def carregar_dados():
    """Carrega dados do disco, se existir"""
    if os.path.exists(DADOS_ARQUIVO):
        try:
            with open(DADOS_ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
    return {"itens_personalizados": [], "meses_quitados": MESES_TODOS[:10]}  # jan/25 a out/25

# ========================================
# 4. Inicialização do estado da sessão
# ========================================
if "inicializado" not in st.session_state:
    dados_salvos = carregar_dados()
    st.session_state.itens_personalizados = dados_salvos["itens_personalizados"]
    st.session_state.meses_quitados = dados_salvos["meses_quitados"]
    st.session_state.inicializado = True

# ========================================
# 5. Função principal de cálculo
# ========================================
def calcular_dataframe():
    df = pd.DataFrame({"mesAno": MESES_TODOS})
    
    # Adicionar itens padrão
    for chave, info in ITENS_PADRAO.items():
        df[chave] = 0.0
        meses_ativos = get_meses_entre(info["inicio"], info["fim"])
        df.loc[df["mesAno"].isin(meses_ativos), chave] = info["valor"]
    
    # Adicionar itens personalizados
    for i, item in enumerate(st.session_state.itens_personalizados):
        col_name = f"item_{i}"
        df[col_name] = 0.0
        meses_ativos = get_meses_entre(item["inicio"], item["fim"])
        df.loc[df["mesAno"].isin(meses_ativos), col_name] = item["valor"]
    
    # Calcular saldo total por mês
    df["total"] = 0.0
    for col in df.columns:
        if col in ["mesAno", "total"]:
            continue
        # Identificar tipo do item
        if col in ITENS_PADRAO:
            tipo = ITENS_PADRAO[col]["tipo"]
        elif col.startswith("item_"):
            idx = int(col.split("_")[1])
            tipo = st.session_state.itens_personalizados[idx]["tipo"]
        else:
            tipo = "debito"
        
        if tipo == "credito":
            df["total"] += df[col]
        else:
            df["total"] -= df[col]
    
    return df

# ========================================
# 6. Função para exibir quadro resumo
# ========================================
def exibir_quadro_resumo(df):
    total_debitos = 0
    total_creditos = 0
    
    for col in df.columns:
        if col in ["mesAno", "total"]:
            continue
        valor_total = df[col].sum()
        # Identificar tipo
        if col in ITENS_PADRAO:
            tipo = ITENS_PADRAO[col]["tipo"]
        elif col.startswith("item_"):
            idx = int(col.split("_")[1])
            tipo = st.session_state.itens_personalizados[idx]["tipo"]
        else:
            tipo = "debito"
        
        if tipo == "credito":
            total_creditos += valor_total
        else:
            total_debitos += valor_total
    
    saldo = total_creditos - total_debitos
    meses_quit = len(st.session_state.meses_quitados)
    total_meses = len(MESES_TODOS)
    
    # Formatação monetária BR
    def fmt_brl(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Débitos", fmt_brl(total_debitos))
    col2.metric("Total Créditos", fmt_brl(total_creditos))
    col3.metric("Saldo Total", fmt_brl(saldo))
    col4.metric("Meses Quitados", f"{meses_quit}/{total_meses}")

# ========================================
# 7. Interface do usuário
# ========================================
st.title("📊 Dashboard Ana")
st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} — valores em R$")

# Quadro resumo
df = calcular_dataframe()
exibir_quadro_resumo(df)

st.divider()

# Seção: Adicionar novo item
with st.expander("➕ Adicionar Novo Item de Despesa/Receita"):
    col_nome, col_valor = st.columns(2)
    nome = col_nome.text_input("Nome do Item")
    valor = col_valor.number_input("Valor Mensal (R$)", min_value=0.01, step=10.0, format="%.2f")
    
    col_tipo, col_ini, col_fim = st.columns(3)
    tipo = col_tipo.selectbox("Tipo", ["debito", "credito"], 
                             format_func=lambda x: "Débito (Despesa)" if x == "debito" else "Crédito (Receita)")
    inicio = col_ini.selectbox("Mês Início", MESES_TODOS)
    fim = col_fim.selectbox("Mês Fim", MESES_TODOS, index=len(MESES_TODOS)-1)
    
    if st.button("✅ Adicionar Item"):
        if nome.strip():
            st.session_state.itens_personalizados.append({
                "nome": nome.strip(),
                "valor": float(valor),
                "tipo": tipo,
                "inicio": inicio,
                "fim": fim
            })
            salvar_dados(st.session_state.itens_personalizados, st.session_state.meses_quitados)
            st.rerun()
        else:
            st.warning("O nome do item não pode estar vazio.")

st.divider()

# Filtro por ano
ano_filtro = st.selectbox("🔍 Filtrar por Ano", ["Todos os Anos", "2025", "2026", "2027", "2028"])
if ano_filtro != "Todos os Anos":
    df_exibir = df[df["mesAno"].str.endswith(f"/{ano_filtro[2:]}")].copy()
else:
    df_exibir = df.copy()

# Exibir cards por mês
for _, row in df_exibir.iterrows():
    mes = row["mesAno"]
    quitado = mes in st.session_state.meses_quitados
    saldo = row["total"]
    
    # Formatação do saldo
    def fmt_brl_valor(x):
        s = f"{abs(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{'+' if x >= 0 else '-'} R$ {s}"
    
    # Cabeçalho do card
    titulo = f"{'✅' if quitado else '📅'} {mes}"
    if quitado:
        titulo += " — ✓ QUITADO"
    
    with st.expander(titulo, expanded=False):
        # Botão para alternar QUITADO
        if st.button("🔄 Alternar QUITADO", key=f"btn_{mes}"):
            if quitado:
                st.session_state.meses_quitados.remove(mes)
            else:
                st.session_state.meses_quitados.append(mes)
            salvar_dados(st.session_state.itens_personalizados, st.session_state.meses_quitados)
            st.rerun()
        
        # Listar itens do mês
        itens_exibidos = False
        for col in df_exibir.columns:
            if col in ["mesAno", "total"]:
                continue
            valor_item = row[col]
            if valor_item <= 0:
                continue
            
            itens_exibidos = True
            
            # Obter info do item
            if col in ITENS_PADRAO:
                info = ITENS_PADRAO[col]
            elif col.startswith("item_"):
                idx = int(col.split("_")[1])
                info = st.session_state.itens_personalizados[idx]
            else:
                continue
            
            nome_item = info["nome"]
            tipo_item = info["tipo"]
            
            # Contador de prazo (exceto Plano de Saúde)
            contador = ""
            if nome_item != "Plano de Saúde":
                meses_ativos = get_meses_entre(info["inicio"], info["fim"])
                if mes in meses_ativos:
                    prest_atual = meses_ativos.index(mes) + 1
                    total_prest = len(meses_ativos)
                    contador = f" (PRAZO {prest_atual}/{total_prest})"
            
            # Formatação do valor
            sinal = "+" if tipo_item == "credito" else "-"
            valor_fmt = f"{valor_item:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.write(f"**{nome_item}{contador}:** {sinal} R$ {valor_fmt}")
        
        if not itens_exibidos:
            st.write("_Nenhum item neste mês._")
        
        # Saldo final
        cor = "green" if saldo >= 0 else "red"
        st.markdown(f"**Saldo:** <span style='color:{cor}'>{fmt_brl_valor(saldo)}</span>", unsafe_allow_html=True)

# Seção: Gerenciar itens personalizados
if st.session_state.itens_personalizados:
    st.divider()
    st.subheader("🛠️ Itens Personalizados")
    for i, item in enumerate(st.session_state.itens_personalizados):
        cols = st.columns([4, 1, 1])
        cols[0].write(f"**{item['nome']}** — R$ {item['valor']:.2f} ({item['inicio']} a {item['fim']})")
        if cols[1].button("✏️ Editar", key=f"edit_{i}"):
            st.session_state.editando = i
            st.session_state.edit_form = True
        if cols[2].button("🗑️ Remover", key=f"del_{i}"):
            st.session_state.itens_personalizados.pop(i)
            salvar_dados(st.session_state.itens_personalizados, st.session_state.meses_quitados)
            st.rerun()

# Formulário de edição (opcional, simplificado)
if "edit_form" in st.session_state and st.session_state.edit_form:
    idx = st.session_state.editando
    item = st.session_state.itens_personalizados[idx]
    
    st.divider()
    st.subheader("✏️ Editar Item")
    with st.form("form_edicao"):
        nome_ed = st.text_input("Nome", item["nome"])
        valor_ed = st.number_input("Valor", value=item["valor"], min_value=0.01, step=10.0)
        tipo_ed = st.selectbox("Tipo", ["debito", "credito"], 
                              index=0 if item["tipo"] == "debito" else 1,
                              format_func=lambda x: "Débito" if x == "debito" else "Crédito")
        ini_ed = st.selectbox("Início", MESES_TODOS, index=MESES_TODOS.index(item["inicio"]))
        fim_ed = st.selectbox("Fim", MESES_TODOS, index=MESES_TODOS.index(item["fim"]))
        
        col1, col2 = st.columns(2)
        if col1.form_submit_button("💾 Salvar"):
            st.session_state.itens_personalizados[idx] = {
                "nome": nome_ed,
                "valor": valor_ed,
                "tipo": tipo_ed,
                "inicio": ini_ed,
                "fim": fim_ed
            }
            salvar_dados(st.session_state.itens_personalizados, st.session_state.meses_quitados)
            st.session_state.edit_form = False
            st.rerun()
        if col2.form_submit_button("❌ Cancelar"):
            st.session_state.edit_form = False
            st.rerun()

# Rodapé
st.divider()
st.caption("Dashboard Ana — Sistema Financeiro Pessoal")
