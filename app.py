# app.py - Dashboard Ana (Versão com Autenticação)
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import hashlib

# Configuração da página
st.set_page_config(
    page_title="Dashboard Ana",
    page_icon="📊",
    layout="wide"
)

# ========================================
# SISTEMA DE AUTENTICAÇÃO
# ========================================
def verificar_senha():
    """Retorna True se o usuário digitou a senha correta."""
    
    def hash_senha(senha):
        """Gera hash SHA256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    # Senha padrão: "ana2025" (você pode mudar)
    # Hash SHA256 de "ana2025"
    SENHA_HASH = "5fd698c40bb0cc98f7c00994b523dec70d4ddc3393e6d67de47a3c11be2d1984"
    
    # Verificar se já está autenticado
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    
    if st.session_state.autenticado:
        return True
    
    # Tela de login
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h1>🔐 Dashboard Ana</h1>
        <p style='color: #666;'>Sistema de Gestão Financeira Pessoal</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Digite a senha para acessar")
        senha_digitada = st.text_input("Senha", type="password", key="senha_input")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔓 Entrar", type="primary", use_container_width=True):
                hash_digitado = hash_senha(senha_digitada)
                if hash_digitado == SENHA_HASH:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    # Debug temporário (remova após testar)
                    st.error("❌ Senha incorreta! Tente novamente.")
                    with st.expander("🔍 Debug (remover após testar)", expanded=False):
                        st.write(f"Hash digitado: `{hash_digitado}`")
                        st.write(f"Hash esperado: `{SENHA_HASH}`")
                        st.write(f"Senha digitada: `{senha_digitada}`")
                        st.write(f"Corresponde: {hash_digitado == SENHA_HASH}")
        
        with col_btn2:
            if st.button("ℹ️ Ajuda", use_container_width=True):
                st.info("💡 **Senha padrão**: ana2025\n\nPara alterar a senha, edite o arquivo `config.py` ou entre em contato com o administrador.")
    
    st.markdown("---")
    st.caption("🔒 Acesso protegido por senha | Dashboard Ana © 2026")
    
    return False

# Verificar autenticação antes de mostrar o dashboard
if not verificar_senha():
    st.stop()

# ========================================
# Botão de Logout no sidebar
# ========================================
with st.sidebar:
    st.markdown("### 👤 Usuário Autenticado")
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
    st.divider()

# Caminho do arquivo de dados
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
# 2. Funções utilitárias
# ========================================
def get_meses_entre(inicio, fim):
    try:
        i1 = MESES_TODOS.index(inicio)
        i2 = MESES_TODOS.index(fim)
        return MESES_TODOS[i1:i2+1]
    except ValueError:
        return []

def salvar_dados(itens_todos, meses_quit):
    """Salva dados no disco (JSON)"""
    dados = {
        "itens": itens_todos,
        "meses_quitados": meses_quit
    }
    with open(DADOS_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def carregar_dados():
    """Carrega dados do disco, se existir"""
    if os.path.exists(DADOS_ARQUIVO):
        try:
            with open(DADOS_ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # Migração de dados antigos
                if "itens_personalizados" in dados:
                    itens_padrao = [
                        {"id": "planoSaude", "nome": "Plano de Saúde", "valor": 1518.93, "inicio": "jan/25", "fim": "dez/28", "tipo": "debito"},
                        {"id": "viagemNordeste", "nome": "Viagem Nordeste", "valor": 206.50, "inicio": "set/25", "fim": "jun/26", "tipo": "debito"},
                        {"id": "geladeira", "nome": "Geladeira", "valor": 152.48, "inicio": "jul/25", "fim": "jun/27", "tipo": "debito"},
                        {"id": "ferro", "nome": "Ferro", "valor": 219.99, "inicio": "set/25", "fim": "dez/26", "tipo": "debito"}
                    ]
                    itens_personalizados = dados["itens_personalizados"]
                    for i, item in enumerate(itens_personalizados):
                        item["id"] = f"custom_{i}"
                    return {"itens": itens_padrao + itens_personalizados, "meses_quitados": dados.get("meses_quitados", MESES_TODOS[:10])}
                return dados
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
    
    # Dados padrão iniciais
    return {
        "itens": [
            {"id": "planoSaude", "nome": "Plano de Saúde", "valor": 1518.93, "inicio": "jan/25", "fim": "dez/28", "tipo": "debito"},
            {"id": "viagemNordeste", "nome": "Viagem Nordeste", "valor": 206.50, "inicio": "set/25", "fim": "jun/26", "tipo": "debito"},
            {"id": "geladeira", "nome": "Geladeira", "valor": 152.48, "inicio": "jul/25", "fim": "jun/27", "tipo": "debito"},
            {"id": "ferro", "nome": "Ferro", "valor": 219.99, "inicio": "set/25", "fim": "dez/26", "tipo": "debito"}
        ],
        "meses_quitados": MESES_TODOS[:10]
    }

# ========================================
# 3. Inicialização do estado da sessão
# ========================================
if "inicializado" not in st.session_state:
    dados_salvos = carregar_dados()
    st.session_state.itens = dados_salvos["itens"]
    st.session_state.meses_quitados = dados_salvos["meses_quitados"]
    st.session_state.inicializado = True

# ========================================
# 4. Função principal de cálculo
# ========================================
def calcular_dataframe():
    df = pd.DataFrame({"mesAno": MESES_TODOS})
    
    # Adicionar todos os itens
    for item in st.session_state.itens:
        col_name = item["id"]
        df[col_name] = 0.0
        meses_ativos = get_meses_entre(item["inicio"], item["fim"])
        df.loc[df["mesAno"].isin(meses_ativos), col_name] = item["valor"]
    
    # Calcular saldo total por mês
    df["total"] = 0.0
    for item in st.session_state.itens:
        col_name = item["id"]
        if item["tipo"] == "credito":
            df["total"] += df[col_name]
        else:
            df["total"] -= df[col_name]
    
    return df

# ========================================
# 5. Função para exibir quadro resumo com gráficos
# ========================================
def exibir_quadro_resumo_gerencial(df):
    st.header("📊 Resumo Gerencial")
    
    # Calcular totais
    total_debitos = 0
    total_creditos = 0
    
    for item in st.session_state.itens:
        col_name = item["id"]
        valor_total = df[col_name].sum()
        if item["tipo"] == "credito":
            total_creditos += valor_total
        else:
            total_debitos += valor_total
    
    saldo = total_creditos - total_debitos
    meses_quit = len(st.session_state.meses_quitados)
    total_meses = len(MESES_TODOS)
    
    # Formatação monetária BR
    def fmt_brl(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Débitos", fmt_brl(total_debitos), delta=None, delta_color="inverse")
    col2.metric("💵 Total Créditos", fmt_brl(total_creditos), delta=None)
    col3.metric("📈 Saldo Total", fmt_brl(saldo), delta=None, delta_color="normal" if saldo >= 0 else "inverse")
    col4.metric("✅ Meses Quitados", f"{meses_quit}/{total_meses}", delta=f"{(meses_quit/total_meses*100):.1f}%")
    
    st.divider()
    
    # Gráficos
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Evolução Mensal do Saldo")
        # Preparar dados para o gráfico
        df_grafico = df[["mesAno", "total"]].copy()
        df_grafico["cor"] = df_grafico["total"].apply(lambda x: "Positivo" if x >= 0 else "Negativo")
        
        fig_evolucao = px.bar(
            df_grafico, 
            x="mesAno", 
            y="total",
            color="cor",
            color_discrete_map={"Positivo": "#10b981", "Negativo": "#ef4444"},
            labels={"mesAno": "Mês/Ano", "total": "Saldo (R$)"},
            title="Saldo Mensal (2025-2028)"
        )
        fig_evolucao.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    with col_right:
        st.subheader("🥧 Distribuição de Despesas")
        # Calcular despesas por item
        despesas_por_item = []
        for item in st.session_state.itens:
            if item["tipo"] == "debito":
                col_name = item["id"]
                valor_total = df[col_name].sum()
                if valor_total > 0:
                    despesas_por_item.append({"Item": item["nome"], "Valor": valor_total})
        
        if despesas_por_item:
            df_despesas = pd.DataFrame(despesas_por_item)
            fig_pizza = px.pie(
                df_despesas, 
                values="Valor", 
                names="Item",
                title="Proporção de Despesas por Item",
                hole=0.4
            )
            fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
            fig_pizza.update_layout(height=400)
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.info("Nenhuma despesa cadastrada.")
    
    st.divider()
    
    # Tabela de itens
    st.subheader("📋 Resumo de Itens Cadastrados")
    
    if st.session_state.itens:
        dados_tabela = []
        for item in st.session_state.itens:
            col_name = item["id"]
            valor_total = df[col_name].sum()
            meses_ativos = get_meses_entre(item["inicio"], item["fim"])
            dados_tabela.append({
                "Item": item["nome"],
                "Tipo": "💵 Crédito" if item["tipo"] == "credito" else "💰 Débito",
                "Valor Mensal": fmt_brl(item["valor"]),
                "Período": f"{item['inicio']} - {item['fim']}",
                "Meses Ativos": len(meses_ativos),
                "Total Acumulado": fmt_brl(valor_total)
            })
        
        df_tabela = pd.DataFrame(dados_tabela)
        st.dataframe(df_tabela, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum item cadastrado.")

# ========================================
# 6. Interface do usuário
# ========================================
st.title("📊 Dashboard Ana - Gestão Financeira")
st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} — valores em R$")

# Quadro resumo gerencial
df = calcular_dataframe()
exibir_quadro_resumo_gerencial(df)

st.divider()

# Seção: Gerenciar itens
st.header("🛠️ Gerenciar Itens")

# Adicionar novo item
with st.expander("➕ Adicionar Novo Item de Despesa/Receita", expanded=False):
    col_nome, col_valor = st.columns(2)
    nome = col_nome.text_input("Nome do Item", key="add_nome")
    valor = col_valor.number_input("Valor Mensal (R$)", min_value=0.01, step=10.0, format="%.2f", key="add_valor")
    
    col_tipo, col_ini, col_fim = st.columns(3)
    tipo = col_tipo.selectbox("Tipo", ["debito", "credito"], 
                             format_func=lambda x: "💰 Débito (Despesa)" if x == "debito" else "💵 Crédito (Receita)",
                             key="add_tipo")
    inicio = col_ini.selectbox("Mês Início", MESES_TODOS, key="add_inicio")
    fim = col_fim.selectbox("Mês Fim", MESES_TODOS, index=len(MESES_TODOS)-1, key="add_fim")
    
    if st.button("✅ Adicionar Item", type="primary"):
        if nome.strip():
            novo_id = f"custom_{len([i for i in st.session_state.itens if i['id'].startswith('custom')])}"
            st.session_state.itens.append({
                "id": novo_id,
                "nome": nome.strip(),
                "valor": float(valor),
                "tipo": tipo,
                "inicio": inicio,
                "fim": fim
            })
            salvar_dados(st.session_state.itens, st.session_state.meses_quitados)
            st.success(f"✅ Item '{nome}' adicionado com sucesso!")
            st.rerun()
        else:
            st.warning("⚠️ O nome do item não pode estar vazio.")

st.divider()

# Listar e editar/excluir itens
if st.session_state.itens:
    st.subheader("📝 Itens Cadastrados")
    
    for i, item in enumerate(st.session_state.itens):
        with st.expander(f"{'💵' if item['tipo'] == 'credito' else '💰'} {item['nome']} — R$ {item['valor']:.2f}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Tipo:** {'Crédito (Receita)' if item['tipo'] == 'credito' else 'Débito (Despesa)'}")
                st.write(f"**Período:** {item['inicio']} até {item['fim']}")
                st.write(f"**Valor Mensal:** R$ {item['valor']:.2f}")
            
            with col2:
                if st.button("✏️ Editar", key=f"edit_btn_{i}"):
                    st.session_state.editando_item = i
                    st.rerun()
                
                if st.button("🗑️ Excluir", key=f"del_btn_{i}", type="secondary"):
                    st.session_state.itens.pop(i)
                    salvar_dados(st.session_state.itens, st.session_state.meses_quitados)
                    st.success(f"✅ Item '{item['nome']}' excluído com sucesso!")
                    st.rerun()
else:
    st.info("Nenhum item cadastrado. Adicione um novo item acima.")

# Formulário de edição
if "editando_item" in st.session_state:
    idx = st.session_state.editando_item
    if idx < len(st.session_state.itens):
        item = st.session_state.itens[idx]
        
        st.divider()
        st.subheader(f"✏️ Editando: {item['nome']}")
        
        with st.form("form_edicao"):
            nome_ed = st.text_input("Nome", item["nome"])
            valor_ed = st.number_input("Valor (R$)", value=item["valor"], min_value=0.01, step=10.0)
            tipo_ed = st.selectbox("Tipo", ["debito", "credito"], 
                                  index=0 if item["tipo"] == "debito" else 1,
                                  format_func=lambda x: "💰 Débito" if x == "debito" else "💵 Crédito")
            ini_ed = st.selectbox("Início", MESES_TODOS, index=MESES_TODOS.index(item["inicio"]))
            fim_ed = st.selectbox("Fim", MESES_TODOS, index=MESES_TODOS.index(item["fim"]))
            
            col1, col2 = st.columns(2)
            if col1.form_submit_button("💾 Salvar Alterações", type="primary"):
                st.session_state.itens[idx] = {
                    "id": item["id"],
                    "nome": nome_ed,
                    "valor": valor_ed,
                    "tipo": tipo_ed,
                    "inicio": ini_ed,
                    "fim": fim_ed
                }
                salvar_dados(st.session_state.itens, st.session_state.meses_quitados)
                del st.session_state.editando_item
                st.success("✅ Item atualizado com sucesso!")
                st.rerun()
            
            if col2.form_submit_button("❌ Cancelar"):
                del st.session_state.editando_item
                st.rerun()

st.divider()

# Seção: Visualização por mês
st.header("📅 Detalhamento Mensal")

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
        if st.button("🔄 Alternar Status de Quitação", key=f"btn_{mes}"):
            if quitado:
                st.session_state.meses_quitados.remove(mes)
            else:
                st.session_state.meses_quitados.append(mes)
            salvar_dados(st.session_state.itens, st.session_state.meses_quitados)
            st.rerun()
        
        # Listar itens do mês
        itens_exibidos = False
        for item in st.session_state.itens:
            col_name = item["id"]
            valor_item = row[col_name]
            if valor_item <= 0:
                continue
            
            itens_exibidos = True
            
            # Contador de prazo (exceto Plano de Saúde)
            contador = ""
            if item["nome"] != "Plano de Saúde":
                meses_ativos = get_meses_entre(item["inicio"], item["fim"])
                if mes in meses_ativos:
                    prest_atual = meses_ativos.index(mes) + 1
                    total_prest = len(meses_ativos)
                    contador = f" (PRAZO {prest_atual}/{total_prest})"
            
            # Formatação do valor
            sinal = "+" if item["tipo"] == "credito" else "-"
            valor_fmt = f"{valor_item:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.write(f"**{item['nome']}{contador}:** {sinal} R$ {valor_fmt}")
        
        if not itens_exibidos:
            st.write("_Nenhum item neste mês._")
        
        # Saldo final
        cor = "green" if saldo >= 0 else "red"
        st.markdown(f"**Saldo:** <span style='color:{cor}'>{fmt_brl_valor(saldo)}</span>", unsafe_allow_html=True)

# Rodapé
st.divider()
st.caption("Dashboard Ana — Sistema de Gestão Financeira Pessoal | Desenvolvido com Streamlit | 🔒 Protegido por Senha")
