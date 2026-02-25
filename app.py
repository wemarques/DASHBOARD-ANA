# app.py - Dashboard Ana (Versão com Autenticação)
import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import config_manager  # Novo gerenciador de config
from backend_antecipacao import AntecipacaoService  # Backend Antecipação
from github_integration import push_to_github  # Integração GitHub
from streamlit_custom_styles import aplicar_estilos_customizados, formatar_valor_financeiro, CORES_GRAFICOS
from gestao_executiva import exibir_gestao_executiva, exibir_resumo_executivo  # Gestão Executiva

# Configuração da página
st.set_page_config(
    page_title="Dashboard Ana",
    page_icon="📊",
    layout="wide"
)

# Aplicar estilos customizados
aplicar_estilos_customizados()

# Inicializar Feature Flags
config_manager.init_flags()
FEATURE_ANTECIPACAO = st.session_state.flags["feature_antecipacao_parcelas"]

# Inicializar Serviço de Antecipação
antecipacao_service = AntecipacaoService()

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
        <p style='color: var(--muted-foreground);'>Sistema de Gestão Financeira Pessoal</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Digite a senha para acessar")
        
        # Input de senha
        # Não inicializamos manualmente o session_state - o widget faz isso automaticamente
        senha_digitada = st.text_input("Senha", type="password", key="senha_input")
        
        # Debug temporário (remover após testar)
        # st.write("Debug - Senha capturada:", "***" if senha_digitada else "(vazia)")
        
        # Botões FORA das colunas internas para evitar problemas
        col_btn1, col_btn2 = st.columns(2)
        
        # Botão de Entrar
        entrar_pressionado = col_btn1.button("🔓 Entrar", type="primary", use_container_width=True)
        
        # Botão de Ajuda
        ajuda_pressionado = col_btn2.button("ℹ️ Ajuda", use_container_width=True)
        
        # Processar ações APÓS os botões serem renderizados
        if entrar_pressionado:
            # Pegar senha do session_state (mais confiável)
            senha = st.session_state.get("senha_input", senha_digitada)
            
            # Se ainda estiver vazio, usar o valor direto (fallback)
            if not senha:
                senha = senha_digitada
            
            # Verificar senha
            if senha and hash_senha(senha) == SENHA_HASH:
                st.session_state.autenticado = True
                # Não podemos limpar senha_input manualmente - é controlado pelo widget
                st.rerun()
            else:
                st.error("❌ Senha incorreta! Tente novamente.")
                # Não podemos limpar senha_input manualmente - o usuário pode limpar manualmente
        
        if ajuda_pressionado:
            st.info("💡 **Senha padrão**: ana2025\n\nPara alterar a senha, edite o arquivo `app.py` ou entre em contato com o administrador.")
    
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
    
    # Backup e Restore Manual (para contornar falhas de persistência no Cloud)
    st.markdown("### 💾 Backup de Dados")
    
    # Ler dados atuais para download
    try:
        if os.path.exists("dados_dashboard_ana.json"):
            with open("dados_dashboard_ana.json", "r", encoding="utf-8") as f:
                dados_json = f.read()
            
            st.download_button(
                label="⬇️ Baixar Backup",
                data=dados_json,
                file_name=f"backup_dashboard_ana_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                help="Clique para salvar seus dados (quitações, itens, antecipações) no seu computador."
            )
    except Exception as e:
        st.error(f"Erro ao gerar backup: {e}")
        
    st.markdown("### ⬆️ Restaurar Dados")
    uploaded_file = st.file_uploader("Carregar arquivo JSON", type=["json"], key="restore_uploader")
    
    if uploaded_file is not None:
        if st.button("Confirmar Restauração", type="primary"):
            try:
                dados_novos = json.load(uploaded_file)
                # Validação básica
                if "itens" in dados_novos and "meses_quitados" in dados_novos:
                    with open("dados_dashboard_ana.json", "w", encoding="utf-8") as f:
                        json.dump(dados_novos, f, ensure_ascii=False, indent=2)
                    
                    # Tentar salvar no GitHub também se possível
                    try:
                        push_to_github(dados_novos, commit_message="Restore backup manual")
                    except:
                        pass
                        
                    st.success("✅ Dados restaurados com sucesso! O app será recarregado.")
                    st.rerun()
                else:
                    st.error("❌ Arquivo inválido: Formato JSON incorreto.")
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo: {e}")

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

def calcular_cronograma_atual(item):
    """
    Calcula o cronograma atual baseado nas antecipações confirmadas.
    
    Retorna:
        dict: {
            "inicio_atual": str,
            "fim_atual": str,
            "parcelas_pagas": int,
            "parcelas_restantes": int,
            "mapeamento": dict
        }
    """
    contrato = item.get("contrato", {})
    if not contrato:
        # Fallback: usar dados antigos
        return {
            "inicio_atual": item["inicio"],
            "fim_atual": item["fim"],
            "parcelas_pagas": 0,
            "parcelas_restantes": len(get_meses_entre(item["inicio"], item["fim"])),
            "mapeamento": {}
        }
    
    inicio_original = contrato["inicio_original"]
    fim_original = contrato["fim_original"]
    total_parcelas = contrato["total_parcelas"]
    
    # Obter todas as parcelas originais
    meses_originais = get_meses_entre(inicio_original, fim_original)
    
    # Obter antecipações confirmadas
    antecipacoes_confirmadas = [
        ant for ant in item.get("antecipacoes", [])
        if ant.get("status") == "confirmada"
    ]
    
    # Criar mapeamento: parcela_original → vencimento_atual
    mapeamento = {}
    antecipacoes_anteriores = 0
    
    for i, mes_original in enumerate(meses_originais):
        numero_parcela = i + 1
        
        # Verificar se esta parcela foi antecipada
        antecipacao = next(
            (a for a in antecipacoes_confirmadas if a["origem"] == mes_original),
            None
        )
        
        if antecipacao:
            # Parcela antecipada
            mapeamento[mes_original] = {
                "numero": numero_parcela,
                "vencimento_atual": antecipacao["destino"],
                "status": "antecipada"
            }
            antecipacoes_anteriores += 1
        else:
            # Parcela não antecipada: deslocar para trás
            novo_indice = i - antecipacoes_anteriores
            mes_vencimento = meses_originais[novo_indice]
            
            mapeamento[mes_original] = {
                "numero": numero_parcela,
                "vencimento_atual": mes_vencimento,
                "status": "pendente"
            }
    
    # Calcular início e fim atuais
    parcelas_pendentes = [
        v for v in mapeamento.values()
        if v["status"] == "pendente"
    ]
    
    if parcelas_pendentes:
        vencimentos_pendentes = [p["vencimento_atual"] for p in parcelas_pendentes]
        # Ordenar cronologicamente usando MESES_TODOS
        vencimentos_ordenados = sorted(vencimentos_pendentes, key=lambda x: MESES_TODOS.index(x) if x in MESES_TODOS else 999)
        inicio_atual = vencimentos_ordenados[0]
        fim_atual = vencimentos_ordenados[-1]
    else:
        # Todas as parcelas foram antecipadas
        inicio_atual = fim_original
        fim_atual = fim_original
    
    parcelas_pagas = len([v for v in mapeamento.values() if v["status"] == "antecipada"])
    parcelas_restantes = len([v for v in mapeamento.values() if v["status"] == "pendente"])
    
    return {
        "inicio_atual": inicio_atual,
        "fim_atual": fim_atual,
        "parcelas_pagas": parcelas_pagas,
        "parcelas_restantes": parcelas_restantes,
        "mapeamento": mapeamento
    }

def calcular_numero_parcela(mes, inicio, fim):
    """
    Calcula o número da parcela de um mês dentro do range inicio-fim.
    Retorna (numero_parcela, total_parcelas) ou (None, total) se fora do range.
    """
    meses_ativos = get_meses_entre(inicio, fim)
    total_parcelas = len(meses_ativos)
    
    if mes in meses_ativos:
        numero_parcela = meses_ativos.index(mes) + 1
        return numero_parcela, total_parcelas
    else:
        # Retornar None para indicar que está fora do range
        return None, total_parcelas

def listar_antecipacoes_por_mes(mes_destino):
    """
    Lista todas as antecipações que foram movidas para um mês específico
    Retorna: lista de dicionários com info das antecipações
    """
    antecipacoes_mes = []
    
    for item in st.session_state.itens:
        if "antecipacoes" not in item:
            continue
        
        for ant in item["antecipacoes"]:
            if ant.get("status") != "confirmada":
                continue
            
            if ant["destino"] == mes_destino:
                antecipacoes_mes.append({
                    "item_nome": item["nome"],
                    "origem": ant["origem"],
                    "destino": ant["destino"],
                    "valor": ant["valor_antecipado"],
                    "motivo": ant.get("motivo", "")
                })
    
    return antecipacoes_mes

def mostrar_detalhes_contrato(item):
    """Exibe detalhes completos do contrato e cronograma"""
    contrato = item.get("contrato", {})
    cronograma = item.get("cronograma", {})
    
    if not contrato or not cronograma:
        st.warning("🚧 Dados do contrato não disponíveis. Execute a migração de dados.")
        return
    
    st.markdown("---")
    st.markdown("### 📋 Detalhes do Contrato")
    
    # Contrato Original
    st.markdown("**CONTRATO ORIGINAL**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Período", f"{contrato['inicio_original']} a {contrato['fim_original']}")
        st.metric("Total de Parcelas", contrato['total_parcelas'])
    with col2:
        st.metric("Valor por Parcela", f"R$ {contrato['valor_parcela']:,.2f}")
        valor_total = contrato['valor_parcela'] * contrato['total_parcelas']
        st.metric("Valor Total", f"R$ {valor_total:,.2f}")
    
    st.markdown("---")
    
    # Cronograma Atual
    st.markdown("**CRONOGRAMA ATUAL (após antecipações)**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Período", f"{cronograma['inicio_atual']} a {cronograma['fim_atual']}")
        st.metric("Parcelas Pagas", f"{cronograma['parcelas_pagas']}/{contrato['total_parcelas']}")
    with col2:
        valor_pago = cronograma['parcelas_pagas'] * contrato['valor_parcela']
        st.metric("Valor Pago", f"R$ {valor_pago:,.2f}")
        valor_restante = cronograma['parcelas_restantes'] * contrato['valor_parcela']
        st.metric("Valor Restante", f"R$ {valor_restante:,.2f}")
    
    st.markdown("---")
    
    # Mapeamento de Parcelas
    st.markdown("**MAPEAMENTO DE PARCELAS**")
    
    mapeamento = cronograma.get("mapeamento", {})
    if mapeamento:
        for mes_original, info in mapeamento.items():
            numero = info["numero"]
            vencimento = info["vencimento_atual"]
            status = info["status"]
            
            if status == "antecipada":
                st.markdown(
                    f"• Parcela {numero}/{contrato['total_parcelas']} "
                    f"({mes_original}) → **{vencimento}** ✅ *Antecipada*"
                )
            else:
                st.markdown(
                    f"• Parcela {numero}/{contrato['total_parcelas']} "
                    f"({mes_original}) → **{vencimento}** ⏳ *Pendente*"
                )

def migrar_dados_para_novo_formato():
    """
    Migra dados existentes para incluir campos 'contrato' e 'cronograma'
    """
    dados = carregar_dados()
    
    for item in dados["itens"]:
        # Se já tem 'contrato', pular
        if "contrato" in item:
            continue
        
        # Criar contrato original baseado nos dados atuais
        meses_ativos = get_meses_entre(item["inicio"], item["fim"])
        
        item["contrato"] = {
            "inicio_original": item["inicio"],
            "fim_original": item["fim"],
            "total_parcelas": len(meses_ativos),
            "valor_parcela": item["valor"]
        }
        
        # Calcular cronograma atual
        item["cronograma"] = calcular_cronograma_atual(item)
    
    salvar_dados(dados["itens"], dados["meses_quitados"])
    return len(dados["itens"])

def salvar_dados(itens_todos, meses_quit):
    """Salva dados no disco (JSON) e no GitHub"""
    dados = {
        "itens": itens_todos,
        "meses_quitados": meses_quit
    }
    # Local
    with open(DADOS_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    # GitHub Cloud Persistence
    try:
        push_to_github(dados, commit_message="Update data: Itens/Quitação alterados via App")
    except Exception as e:
        print(f"Erro ao salvar no GitHub: {e}")

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
                
                # Fix: Garantir que Bancorbras Vila Galé exista
                tem_vila_gale = any(i.get("nome") == "Bancorbras Vila Galé" for i in dados.get("itens", []))
                if not tem_vila_gale and "itens" in dados:
                    vila_gale = {
                        "id": "bancorbrasVilaGale",
                        "nome": "Bancorbras Vila Galé",
                        "valor": 398.57,
                        "tipo": "debito",
                        "inicio": "jan/26",
                        "fim": "dez/26",
                        "antecipacoes": [],
                        "contrato": {
                            "inicio_original": "jan/26",
                            "fim_original": "dez/26",
                            "total_parcelas": 12,
                            "valor_parcela": 398.57
                        }
                    }
                    try:
                        vila_gale["cronograma"] = calcular_cronograma_atual(vila_gale)
                    except:
                        pass
                    dados["itens"].append(vila_gale)
                    # Salvar a correção
                    try:
                        salvar_dados(dados["itens"], dados["meses_quitados"])
                    except:
                        pass

                return dados
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
    
    # Dados padrão iniciais
    return {
        "itens": [
            {"id": "planoSaude", "nome": "Plano de Saúde", "valor": 1518.93, "inicio": "jan/25", "fim": "dez/28", "tipo": "debito"},
            {"id": "viagemNordeste", "nome": "Viagem Nordeste", "valor": 206.50, "inicio": "set/25", "fim": "jun/26", "tipo": "debito"},
            {"id": "geladeira", "nome": "Geladeira", "valor": 152.48, "inicio": "jul/25", "fim": "jun/27", "tipo": "debito"},
            {"id": "ferro", "nome": "Ferro", "valor": 219.99, "inicio": "set/25", "fim": "dez/26", "tipo": "debito"},
            {"id": "bancorbrasVilaGale", "nome": "Bancorbras Vila Galé", "valor": 398.57, "inicio": "jan/26", "fim": "dez/26", "tipo": "debito"}
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
        
        # 1. Calcular valores base (recorrência normal)
        df.loc[df["mesAno"].isin(meses_ativos), col_name] = item["valor"]
        
        # 2. Aplicar Antecipações (se feature ativa)
        if FEATURE_ANTECIPACAO and "antecipacoes" in item:
            for ant in item["antecipacoes"]:
                if ant.get("status") != "confirmada":
                    continue
                
                origem = ant.get("origem")
                destino = ant.get("destino")
                valor_ant = ant.get("valor_antecipado", 0.0)
                
                # Remover da origem (subtrair o valor antecipado)
                # Se for antecipação total, isso zera o mês. Se parcial, reduz.
                if origem in MESES_TODOS:
                    idx_origem = df[df["mesAno"] == origem].index
                    if not idx_origem.empty:
                        valor_atual = df.at[idx_origem[0], col_name]
                        novo_valor = max(0.0, valor_atual - valor_ant) # Evitar negativo
                        df.at[idx_origem[0], col_name] = novo_valor
                
                # Adicionar ao destino (somar o valor antecipado)
                if destino in MESES_TODOS:
                    idx_destino = df[df["mesAno"] == destino].index
                    if not idx_destino.empty:
                        valor_atual_dest = df.at[idx_destino[0], col_name]
                        df.at[idx_destino[0], col_name] = valor_atual_dest + valor_ant

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
# 5. Interface do usuário
# ========================================
st.title("📊 Dashboard Ana - Gestão Financeira")
st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} — valores em R$")

# ========================================
# CÁLCULO DO DATAFRAME ANTES DAS ABAS
# ========================================
df = calcular_dataframe()

# ========================================
# NAVEGAÇÃO POR ABAS
# ========================================
aba1, aba2, aba3, aba4 = st.tabs(["📊 Gestão Executiva", "📅 Detalhamento Mensal", "🛠️ Gerenciar Itens", "⚡ Antecipar Parcelas"])

with aba1:
    # === GESTÃO EXECUTIVA - RESULTADO MENSAL ===
    st.header("📊 Gestão Executiva - Resultado Mensal")
    
    # Resumo Executivo Rápido
    st.subheader("📈 Resumo Executivo")
    exibir_resumo_executivo(st.session_state.itens, st.session_state.meses_quitados, df)
    
    st.divider()
    
    # Seletor de mês para análise executiva detalhada
    mes_atual = datetime.now().strftime("%b/%y").lower()
    meses_disponiveis = list(df['mesAno'])
    
    # Encontrar o mês mais próximo da data atual
    mes_default = meses_disponiveis[0]
    for mes in meses_disponiveis:
        try:
            mes_dt = datetime.strptime(mes, "%b/%y")
            if mes_dt <= datetime.now():
                mes_default = mes
        except:
            continue
    
    mes_selecionado = st.selectbox(
        "📅 Selecione o mês para análise executiva detalhada:",
        meses_disponiveis,
        index=meses_disponiveis.index(mes_default) if mes_default in meses_disponiveis else 0,
        key="mes_executivo"
    )
    
    # Chamar a função de gestão executiva detalhada
    exibir_gestao_executiva(st.session_state.itens, st.session_state.meses_quitados, df, mes_selecionado)

with aba2:
    # === DETALHAMENTO MENSAL (CONTEÚDO EXISTENTE) ===
    st.header("📅 Detalhamento Mensal")
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
            color_discrete_map={"Positivo": CORES_GRAFICOS['positivo'], "Negativo": CORES_GRAFICOS['negativo']},
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
            total_parcelas = len(meses_ativos)
            
            # Contar quantas parcelas já foram quitadas
            parcelas_quitadas = sum(1 for m in meses_ativos if m in st.session_state.meses_quitados)
            if total_parcelas > 0:
                percentual = (parcelas_quitadas / total_parcelas) * 100
                progresso = f"{parcelas_quitadas}/{total_parcelas} ({percentual:.1f}%)"
            else:
                progresso = "0/0 (0.0%)"
            
            dados_tabela.append({
                "Item": item["nome"],
                "Tipo": "💵 Crédito" if item["tipo"] == "credito" else "💰 Débito",
                "Valor Mensal": fmt_brl(item["valor"]),
                "Período": f"{item['inicio']} - {item['fim']}",
                "Progresso": progresso,
                "Total Acumulado": fmt_brl(valor_total)
            })
        
        df_tabela = pd.DataFrame(dados_tabela)
        st.dataframe(df_tabela, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum item cadastrado.")


with aba4:
    if FEATURE_ANTECIPACAO:
        with st.expander("⚡ Antecipar Parcelas (Feature Ativa)", expanded=False):
            st.caption("Antecipe pagamentos futuros para meses atuais.")
            
            # 1. Selecionar Item (apenas Débitos)
            opcoes_itens = [i for i in st.session_state.itens if i["tipo"] == "debito"]
            item_sel = st.selectbox(
                "Selecione a Despesa", 
                opcoes_itens, 
                format_func=lambda x: x["nome"],
                key="ant_item"
            )
            
            if item_sel:
                # 2. Listar Parcelas Futuras (Origem)
                # Regra: Parcela deve estar no futuro e ainda ter saldo > 0
                # Vamos simplificar pegando meses do item que ainda não passaram
                
                # Identificar mês atual (simulação ou real)
                mes_atual_str = datetime.now().strftime("%b/%y").lower()
                # Mapa de ordem dos meses para comparação
                def get_date_from_str(m):
                    meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
                    mes, ano = m.split('/')
                    return datetime(int("20"+ano), meses.index(mes)+1, 1)
    
                hoje = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                meses_ativos = get_meses_entre(item_sel["inicio"], item_sel["fim"])
                meses_futuros = []
                
                for m in meses_ativos:
                    # Regra: Permitir antecipar parcelas de qualquer mês que ainda não foi quitado
                    # Ou seja, se o mês já passou mas não foi marcado como quitado, ele é elegível.
                    # Se o mês é futuro, sempre é elegível.
                    
                    # Vamos checar se o mês está na lista de meses_quitados
                    is_quitado = m in st.session_state.meses_quitados
                    
                    if not is_quitado:
                        # Verificar se já foi totalmente antecipada (opcional, mas bom pra UX)
                        meses_futuros.append(m)
                
                if not meses_futuros:
                    st.warning("Não há parcelas disponíveis para antecipação.")
                else:
                    # Função para formatar mês com indicador de parcela
                    def format_mes_com_parcela(mes):
                        num, total = calcular_numero_parcela(mes, item_sel["inicio"], item_sel["fim"])
                        if num is not None:
                            return f"{mes} (Parcela {num}/{total})"
                        else:
                            return f"{mes} (Fora do fluxo)"
                    
                    col_origem, col_destino = st.columns(2)
                    
                    # Seleção múltipla de parcelas de origem
                    origem_sels = col_origem.multiselect(
                        "Parcelas a Antecipar (Origem) - Selecione uma ou mais", 
                        meses_futuros, 
                        format_func=format_mes_com_parcela,
                        key="ant_origem",
                        help="Você pode selecionar múltiplas parcelas, inclusive não consecutivas"
                    )
                    
                    if not origem_sels:
                        st.info("💡 Selecione ao menos uma parcela para antecipar.")
                    else:
                        # Destino: permitir QUALQUER mês (inclusive fora do range do item)
                        # Permitir antecipar para qualquer mês disponível, excluindo apenas os selecionados como origem
                        meses_destino = []
                        for m in MESES_TODOS:
                            # Excluir apenas meses que já estão na seleção de origem
                            if m not in origem_sels:
                                meses_destino.append(m)
                        
                        if not meses_destino:
                            st.error("Não há meses de destino disponíveis.")
                        else:
                            destino_sel = col_destino.selectbox(
                                "Mover TODAS para (Destino)", 
                                meses_destino, 
                                format_func=format_mes_com_parcela,
                                key="ant_destino",
                                help="Você pode antecipar para qualquer mês, inclusive posteriores"
                            )
                            
                            # Resumo visual
                            st.info(f"📦 Você está antecipando **{len(origem_sels)} parcela(s)** para **{destino_sel}**")
                            
                            # Mostrar lista de parcelas selecionadas
                            with st.expander("📋 Parcelas Selecionadas", expanded=True):
                                for origem in origem_sels:
                                    num, total = calcular_numero_parcela(origem, item_sel["inicio"], item_sel["fim"])
                                    if num is not None:
                                        st.write(f"• {origem} (Parcela {num}/{total}) → {destino_sel}")
                                    else:
                                        st.write(f"• {origem} (Fora do fluxo) → {destino_sel}")
                            
                            # Valor total
                            valor_total = item_sel["valor"] * len(origem_sels)
                            def fmt_brl(x):
                                return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            st.metric("Valor Total a Antecipar", fmt_brl(valor_total))
                            
                            motivo = st.text_input("Motivo (Opcional)", key="ant_motivo", placeholder="Ex: Antecipação de fim de ano")
                            
                            if st.button("🚀 Confirmar Antecipação", type="primary"):
                                sucessos = 0
                                erros = []
                                warnings = []
                                
                                # Processar cada antecipação
                                for origem in origem_sels:
                                    # Calcular mês original da parcela usando cronograma
                                    cronograma = item_sel.get("cronograma", {})
                                    mapeamento = cronograma.get("mapeamento", {})
                                    
                                    # Buscar mês original no mapeamento
                                    mes_original = None
                                    for mes_orig, mes_venc in mapeamento.items():
                                        if mes_venc == origem:
                                            mes_original = mes_orig
                                            break
                                    
                                    # Se não encontrou no mapeamento, usar origem (compatibilidade)
                                    if not mes_original:
                                        mes_original = origem
                                    
                                    res = antecipacao_service.criar_antecipacao(
                                        item_id=item_sel["id"],
                                        mes_origem=origem,
                                        mes_destino=destino_sel,
                                        valor=item_sel["valor"],
                                        usuario="usuario_logado",
                                        motivo=motivo,
                                        mes_original_parcela=mes_original
                                    )
                                    
                                    if res["success"]:
                                        sucessos += 1
                                        if "warning" in res:
                                            warnings.append(f"• {origem}: {res['warning']}")
                                    else:
                                        erros.append(f"• {origem}: {res['message']}")
                                
                                # Mostrar resultado
                                if sucessos > 0:
                                    st.success(f"✅ {sucessos} antecipação(ões) realizada(s) com sucesso!")
                                    
                                    if warnings:
                                        # Mostrar apenas avisos únicos
                                        unique_warnings = list(set(warnings))
                                        st.warning("⚠️ **Atenção:**\n" + "\n".join(unique_warnings))
                                    
                                    # Encurtar fluxo automaticamente (agora restaura o original)
                                    resultado_enc = antecipacao_service.encurtar_fluxo_item(item_sel["id"])
                                    if resultado_enc.get("success") and resultado_enc.get("novo_fim"):
                                        st.info(f"🔄 Fluxo do item validado e restaurado para o contrato original (Fim: {resultado_enc['novo_fim']})")
                                
                                if erros:
                                    st.error("❌ Erros encontrados:\n" + "\n".join(erros))
                                
                                # Recarregar dados e recalcular cronograma
                                if sucessos > 0:
                                    dados_rec = carregar_dados()
                                    
                                    # Recalcular cronograma do item (sem encurtar)
                                    for item in dados_rec["itens"]:
                                        if item["id"] == item_sel["id"]:
                                            if "contrato" in item:
                                                item["cronograma"] = calcular_cronograma_atual(item)
                                            break
                                    
                                    salvar_dados(dados_rec["itens"], dados_rec["meses_quitados"])
                                    st.session_state.itens = dados_rec["itens"]
                                    st.rerun()
            
            st.divider()
            st.subheader("📜 Histórico de Antecipações")
            historico = antecipacao_service.listar_antecipacoes(item_id=item_sel["id"] if item_sel else None)
            
            if historico:
                for ant in historico:
                    # Encontrar item correspondente para calcular número da parcela
                    # Se item_sel está definido, usar ele; caso contrário, buscar pelo nome do item
                    if item_sel:
                        item_hist = item_sel
                    else:
                        # Buscar item pelo nome (retornado pelo backend)
                        item_hist = next((i for i in st.session_state.itens if i["nome"] == ant.get("item_nome", "")), None)
                    
                    if item_hist:
                        num_origem, total_origem = calcular_numero_parcela(ant['origem'], item_hist["inicio"], item_hist["fim"])
                        num_destino, total_destino = calcular_numero_parcela(ant['destino'], item_hist["inicio"], item_hist["fim"])
                        
                        # Formatar parcela origem
                        if num_origem is not None:
                            texto_origem = f"{ant['origem']} (Parcela {num_origem}/{total_origem})"
                        else:
                            texto_origem = f"{ant['origem']} (Fora do fluxo)"
                        
                        # Formatar parcela destino
                        if num_destino is not None:
                            texto_destino = f"{ant['destino']} (Parcela {num_destino}/{total_destino})"
                        else:
                            texto_destino = f"{ant['destino']} (Fora do fluxo)"
                        
                        def fmt_brl_valor(x):
                            return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        
                        valor_fmt = fmt_brl_valor(ant['valor_antecipado'])
                        titulo = f"{texto_origem} ➔ {texto_destino} - R$ {valor_fmt} - {ant['status'].upper()}"
                    else:
                        valor_fmt = f"{ant['valor_antecipado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        titulo = f"{ant['origem']} ➔ {ant['destino']} - {valor_fmt} - {ant['status'].upper()}"
                    
                    # Ícone baseado no status
                    icone = "✅" if ant['status'] == 'confirmada' else "❌"
                    
                    with st.expander(f"{icone} {titulo}", expanded=False):
                        st.write(f"**Item:** {ant.get('item_nome', 'N/A')}")
                        st.write(f"**Data:** {ant['timestamp']}")
                        st.write(f"**Usuário:** {ant.get('usuario', 'N/A')}")
                        
                        if ant.get('motivo'):
                            st.write(f"**Motivo:** {ant['motivo']}")
                        
                        if ant['status'] == 'confirmada':
                            if st.button("🔄 Desfazer (Cancelar)", key=f"undo_{ant['id_antecipacao']}"):
                                # Buscar item_id para cancelamento
                                if item_sel:
                                    item_id_para_cancelar = item_sel["id"]
                                else:
                                    # Buscar pelo nome do item
                                    item_encontrado = next((i for i in st.session_state.itens if i["nome"] == ant.get("item_nome", "")), None)
                                    item_id_para_cancelar = item_encontrado["id"] if item_encontrado else None
                                
                                if not item_id_para_cancelar:
                                    st.error("❌ Não foi possível identificar o item para cancelar a antecipação.")
                                else:
                                    res_undo = antecipacao_service.cancelar_antecipacao(
                                        item_id=item_id_para_cancelar, 
                                        id_antecipacao=ant["id_antecipacao"],
                                        usuario="usuario_logado"
                                    )
                                    
                                    if res_undo["success"]:
                                        if "warning" in res_undo:
                                            st.warning(f"⚠️ Atenção: {res_undo['warning']}")
                                            time.sleep(3) # Tempo para leitura
                                        else:
                                            st.success("✅ Antecipação cancelada com sucesso!")
                                            time.sleep(1)
                                        
                                        dados_rec = carregar_dados()
                                        st.session_state.itens = dados_rec["itens"]
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Erro: {res_undo.get('message', 'Erro desconhecido')}")
            else:
                st.info("Nenhuma antecipação registrada.")
    

with aba3:
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
                    
                    # Exibir período com formato "atual (original)"
                    contrato = item.get("contrato", {})
                    cronograma = item.get("cronograma", {})
                    
                    if contrato and cronograma:
                        inicio_original = contrato["inicio_original"]
                        fim_original = contrato["fim_original"]
                        inicio_atual = cronograma["inicio_atual"]
                        fim_atual = cronograma["fim_atual"]
                        parcelas_pagas = cronograma["parcelas_pagas"]
                        parcelas_restantes = cronograma["parcelas_restantes"]
                        
                        # Verificar se houve antecipações
                        if parcelas_pagas > 0:
                            # Formato: jan/26 (mar/26) até out/26 (dez/26)
                            periodo_texto = (
                                f"{inicio_atual} ({inicio_original}) até "
                                f"{fim_atual} ({fim_original})"
                            )
                            st.write(f"**Período:** {periodo_texto}")
                            st.caption(
                                f"⚡ {parcelas_pagas} parcela(s) antecipada(s) | "
                                f"{parcelas_restantes} restante(s) de {contrato['total_parcelas']}"
                            )
                        else:
                            # Sem antecipações: exibir normal
                            st.write(f"**Período:** {inicio_original} até {fim_original}")
                            st.caption(f"📋 {parcelas_restantes} parcela(s) de {contrato['total_parcelas']}")
                    else:
                        # Fallback para formato antigo
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
                
                # Botão para ver detalhes do contrato
                if item.get("contrato") and item.get("cronograma"):
                    if st.button("📋 Ver Detalhes do Contrato", key=f"detalhes_{item['id']}"):
                        mostrar_detalhes_contrato(item)
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
                    # Usar cronograma se disponível
                    cronograma = item.get("cronograma", {})
                    mapeamento = cronograma.get("mapeamento", {})
                    
                    # Encontrar parcela original correspondente a este mês
                    parcela_info = None
                    for mes_original, info in mapeamento.items():
                        if info["vencimento_atual"] == mes:
                            parcela_info = info
                            break
                    
                    if parcela_info:
                        numero = parcela_info["numero"]
                        total = item["contrato"]["total_parcelas"]
                        contador = f" (Parcela {numero}/{total})"
                    else:
                        # Fallback para cálculo antigo
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
            
            # Verificar se há antecipações para este mês
            antecipacoes_mes = listar_antecipacoes_por_mes(mes)
            
            if antecipacoes_mes:
                st.markdown("---")
                st.markdown("**📥 Prestações Antecipadas para este mês:**")
                
                for ant in antecipacoes_mes:
                    # Formato: jan/26 ➔ nov/25 (R$ 398.57) Prestação Antecipada
                    def fmt_brl_valor(x):
                        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    valor_fmt = fmt_brl_valor(ant['valor'])
                    
                    # Buscar item para calcular número da parcela
                    item_ant = next((i for i in st.session_state.itens if i["nome"] == ant['item_nome']), None)
                    
                    if item_ant:
                        num_parcela, total_parcelas = calcular_numero_parcela(ant['origem'], item_ant["inicio"], item_ant["fim"])
                        
                        if num_parcela is not None:
                            texto_parcela = f" (Parcela {num_parcela}/{total_parcelas})"
                        else:
                            texto_parcela = " (Fora do fluxo)"
                    else:
                        texto_parcela = ""
                    
                    # Formato: jan/26 ➔ nov/25 (R$ 398.57) Prestação Antecipada
                    st.markdown(
                        f"• {ant['origem']}{texto_parcela} ➔ {ant['destino']} (R$ {valor_fmt}) *Prestação Antecipada*",
                        unsafe_allow_html=True
                    )
                    
                    if ant['motivo']:
                        st.caption(f"  Motivo: {ant['motivo']}")
            
            # Saldo final
            st.markdown(f"**Saldo:** {formatar_valor_financeiro(saldo)}", unsafe_allow_html=True)
    
    # Rodapé
    st.divider()
    st.caption("Dashboard Ana — Sistema de Gestão Financeira Pessoal | Desenvolvido com Streamlit | 🔒 Protegido por Senha")
