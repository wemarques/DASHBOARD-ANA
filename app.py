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
import hmac
import config_manager  # Novo gerenciador de config
from backend_antecipacao import AntecipacaoService  # Backend Antecipação
from github_integration import push_to_github, pull_from_github, get_github_token, diagnosticar_token, _ultimo_erro_push  # Integração GitHub
from streamlit_custom_styles import aplicar_estilos_customizados, formatar_valor_financeiro, CORES_GRAFICOS, get_plotly_layout_theme
from gestao_executiva import exibir_gestao_executiva  # Gestão Executiva (acerto do mês)
from detalhamento_mensal import exibir_detalhamento_mensal  # Detalhamento Mensal (quitação)
from gerenciar_itens import exibir_gerenciar_itens  # Gerenciar Itens (cadastro e reajustes)
from antecipar_parcelas import exibir_antecipar_parcelas  # Antecipar Parcelas
from itens_modelo import serie as serie_do_item  # valor por mês, com reajustes

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
def obter_senha_hash():
    """Hash SHA256 da senha de acesso, vindo de st.secrets ou do ambiente.

    O hash NÃO fica mais no código: o repositório precisa ser público para o
    Streamlit Community Cloud gratuito, e um hash versionado equivale a publicar
    a senha. Ordem de busca:

        1. st.secrets["SENHA_HASH"]          (Streamlit Cloud › Settings › Secrets)
        2. st.secrets["auth"]["senha_hash"]  (forma em seção, se preferir)
        3. variável de ambiente DASHBOARD_ANA_SENHA_HASH  (execução local)

    Se nada estiver configurado, retorna "" e o app NÃO autentica ninguém
    (fail closed) — melhor travado do que aberto com senha conhecida.
    """
    try:
        if "SENHA_HASH" in st.secrets:
            return str(st.secrets["SENHA_HASH"]).strip().lower()
        auth = st.secrets.get("auth", {})
        if isinstance(auth, dict) or hasattr(auth, "get"):
            valor = auth.get("senha_hash")
            if valor:
                return str(valor).strip().lower()
    except Exception:
        # Sem arquivo de secrets configurado: cai no ambiente.
        pass
    return os.environ.get("DASHBOARD_ANA_SENHA_HASH", "").strip().lower()


def _mostrar_instrucoes_secrets():
    """Tela exibida quando o hash da senha não está configurado."""
    st.error("🔒 Acesso não configurado: o hash da senha não foi encontrado.")
    st.markdown(
        """
Este app não guarda mais a senha no código. Configure o hash **antes** de usar:

**No Streamlit Cloud** — app › `⋮` › **Settings** › **Secrets**, e acrescente:

```toml
SENHA_HASH = "cole_aqui_o_hash_sha256"
```

**Localmente** — crie `.streamlit/secrets.toml` (já ignorado pelo git) com a
mesma linha, ou exporte `DASHBOARD_ANA_SENHA_HASH`.

Para gerar o hash da senha que você escolher, rode `python gerar_senha.py`.
        """
    )


def verificar_senha():
    """Retorna True se o usuário digitou a senha correta."""

    def hash_senha(senha):
        """Gera hash SHA256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()

    SENHA_HASH = obter_senha_hash()

    # Verificar se já está autenticado
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    
    if st.session_state.autenticado:
        return True

    if not SENHA_HASH:
        _mostrar_instrucoes_secrets()
        return False

    # Tela de login
    st.markdown("""
    <div style='
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #1C2B4A 0%, #2A3A52 100%);
        border-radius: 20px;
        margin: 2rem auto;
        max-width: 500px;
        box-shadow: 0 10px 25px rgba(10, 22, 40, 0.15);
    '>
        <div style='
            color: #FFFFFF;
            font-family: Playfair Display, serif;
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        '>Dashboard Ana</div>
        <div style='
            color: #C9A96E;
            font-family: DM Sans, sans-serif;
            font-size: 0.9rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        '>Gestão Financeira Pessoal</div>
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
        entrar_pressionado = col_btn1.button("Entrar", type="primary", use_container_width=True)

        # Botão de Ajuda
        ajuda_pressionado = col_btn2.button("Ajuda", use_container_width=True)
        
        # Processar ações APÓS os botões serem renderizados
        if entrar_pressionado:
            # Pegar senha do session_state (mais confiável)
            senha = st.session_state.get("senha_input", senha_digitada)
            
            # Se ainda estiver vazio, usar o valor direto (fallback)
            if not senha:
                senha = senha_digitada
            
            # Verificar senha
            # compare_digest: comparação em tempo constante, não vaza o hash
            # pelo tempo de resposta.
            if senha and hmac.compare_digest(hash_senha(senha), SENHA_HASH):
                st.session_state.autenticado = True
                # Não podemos limpar senha_input manualmente - é controlado pelo widget
                st.rerun()
            else:
                st.error("❌ Senha incorreta! Tente novamente.")
                # Não podemos limpar senha_input manualmente - o usuário pode limpar manualmente
        
        if ajuda_pressionado:
            st.info(
                "💡 A senha é definida em **Secrets** (`SENHA_HASH`), não no código.\n\n"
                "Para trocá-la: rode `python gerar_senha.py`, copie o hash gerado e "
                "atualize o segredo `SENHA_HASH` no Streamlit Cloud."
            )
    
    st.markdown("---")
    st.caption("Acesso protegido por senha | Dashboard Ana © 2026")
    
    return False

# Verificar autenticação antes de mostrar o dashboard
if not verificar_senha():
    st.stop()

# ========================================
# Botão de Logout no sidebar
# ========================================
with st.sidebar:
    st.markdown("<p style='font-family: DM Sans, sans-serif; color: rgba(255,255,255,0.5) !important; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;'>Conta</p>", unsafe_allow_html=True)
    st.markdown("### Usuário Autenticado")
    if st.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
    
    st.divider()
    
    # Backup e Restore Manual (para contornar falhas de persistência no Cloud)
    st.markdown("### Backup de Dados")
    
    # Ler dados atuais para download
    try:
        if os.path.exists("dados_dashboard_ana.json"):
            with open("dados_dashboard_ana.json", "r", encoding="utf-8") as f:
                dados_json = f.read()
            
            st.download_button(
                label="Baixar Backup",
                data=dados_json,
                file_name=f"backup_dashboard_ana_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                help="Clique para salvar seus dados (quitações, itens, antecipações) no seu computador."
            )
    except Exception as e:
        st.error(f"Erro ao gerar backup: {e}")
        
    st.markdown("### Restaurar Dados")
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

    # Status de persistência — usar mesma função que push_to_github usa
    _token = get_github_token()
    if not _token:
        st.warning("GITHUB_TOKEN não encontrado. Dados serão perdidos ao reiniciar. Configure em Settings > Secrets no Streamlit Cloud.")
    else:
        # Token existe, verificar se último push teve erro
        if _ultimo_erro_push.get("msg"):
            st.error(f"Erro no último save: {_ultimo_erro_push['msg']}")

    # Diagnóstico de token (expansível)
    with st.expander("Diagnóstico GitHub", expanded=False):
        if st.button("Testar Conexão"):
            with st.spinner("Testando..."):
                diag = diagnosticar_token()
            if diag["token_encontrado"]:
                st.write(f"Token: `{diag.get('token_preview', '***')}`")
                if diag["leitura_ok"]:
                    st.success("Leitura: OK")
                else:
                    st.error("Leitura: FALHOU")
                if diag["escrita_ok"]:
                    st.success("Escrita: OK")
                else:
                    st.error("Escrita: SEM PERMISSAO")
            else:
                st.error("Token nao encontrado")
            if diag.get("erro"):
                st.code(diag["erro"])

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

def contar_parcelas_pagas(mapeamento, meses_periodo, quitados):
    """Conta parcelas pagas por PARCELA, não por mês.

    Uma parcela está paga se foi antecipada ou se o mês em que ela vence hoje
    (vencimento_atual, já deslocado pelas antecipações) está em meses_quitados.
    Somar "meses quitados do período + antecipadas" conta o mês que ficou vazio
    após o deslocamento como se fosse parcela, e min(..., total) só esconde o
    excesso quando passa de 100%. Ex.: Bancorbras (6 antecipadas, pendentes
    vencendo jan..jun/26) com jan/26 + jul/26 + ago/26 quitados dava 9/12; a
    tabela de mapeamento, com a regra correta, mostra 7/12.

    Sem mapeamento (item sem contrato), vale a regra antiga: meses do período
    que estão em meses_quitados.
    """
    if not mapeamento:
        return sum(1 for m in meses_periodo if m in quitados)
    return sum(
        1 for info in mapeamento.values()
        if info["status"] == "antecipada" or info["vencimento_atual"] in quitados
    )

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
    
    def _brl(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    meses_item = get_meses_entre(item["inicio"], item["fim"])
    quitados = st.session_state.get("meses_quitados", [])

    # O JSON traz total_parcelas = 0 em itens antigos (ex.: Plano de Saúde), o que
    # zerava "Total de Parcelas" e "Valor Total". Derivamos do período nesse caso.
    total_parcelas = contrato.get("total_parcelas") or len(meses_item)
    # Contagem por PARCELA (mesma regra da tabela de mapeamento abaixo), não por mês.
    pagas = min(
        contar_parcelas_pagas(cronograma.get("mapeamento", {}), meses_item, quitados),
        total_parcelas,
    )

    st.markdown("---")
    st.markdown("### Detalhes do Contrato")

    # Contrato Original
    st.markdown("**CONTRATO ORIGINAL**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Período", f"{contrato['inicio_original']} a {contrato['fim_original']}")
        st.metric("Total de Parcelas", total_parcelas)
    with col2:
        st.metric("Valor por Parcela", _brl(contrato["valor_parcela"]))
        valor_total = contrato['valor_parcela'] * total_parcelas
        st.metric("Valor Total", _brl(valor_total))

    st.markdown("---")

    # Cronograma Atual
    st.markdown("**CRONOGRAMA ATUAL (após antecipações)**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Período", f"{cronograma['inicio_atual']} a {cronograma['fim_atual']}")
        # Antes contava só antecipações, e dava "0/24" mesmo com meses quitados.
        st.metric("Parcelas Pagas", f"{pagas}/{total_parcelas}",
                  help="Meses quitados + parcelas antecipadas.")
    with col2:
        valor_pago = pagas * contrato['valor_parcela']
        st.metric("Valor Pago", _brl(valor_pago))
        valor_restante = max(total_parcelas - pagas, 0) * contrato['valor_parcela']
        st.metric("Valor Restante", _brl(valor_restante))

    st.markdown("---")

    # Mapeamento de Parcelas — tabela com 3 estados reais
    st.markdown("**MAPEAMENTO DE PARCELAS**")

    mapeamento = cronograma.get("mapeamento", {})
    linhas = []

    if mapeamento:
        for mes_original, info in mapeamento.items():
            venc = info["vencimento_atual"]
            if info["status"] == "antecipada":
                situacao = "⚡ Antecipada"
            elif venc in quitados:
                situacao = "✅ Quitada"
            else:
                situacao = "⏳ A vencer"
            linhas.append({
                "Parcela": f"{info['numero']}/{total_parcelas}",
                "Competência": mes_original,
                "Vencimento": venc,
                "Situação": situacao,
            })
    else:
        # Sem mapeamento gravado: derivamos do período para não exibir lista vazia.
        for n, mes in enumerate(meses_item, start=1):
            linhas.append({
                "Parcela": f"{n}/{total_parcelas}",
                "Competência": mes,
                "Vencimento": mes,
                "Situação": "✅ Quitada" if mes in quitados else "⏳ A vencer",
            })

    if linhas:
        df_map = pd.DataFrame(linhas)
        resumo = df_map["Situação"].value_counts().to_dict()
        st.caption(" · ".join(f"{k}: {v}" for k, v in resumo.items())
                   + "  —  para alterar, use **Detalhamento Mensal › Controle de Quitação**.")
        st.dataframe(df_map, use_container_width=True, hide_index=True,
                     height=min(38 * len(df_map) + 38, 420))
    else:
        st.info("Este item não possui parcelas mapeadas.")

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
        success = push_to_github(dados, commit_message="Update data: Itens/Quitacao alterados via App")
        if not success and _ultimo_erro_push.get("msg"):
            st.toast(f"Aviso: {_ultimo_erro_push['msg']}", icon="⚠️")
    except Exception as e:
        st.toast(f"Erro ao salvar no GitHub: {e}", icon="❌")

def _mesclar_antecipacoes(dados_local, dados_github):
    """
    Mescla antecipações do GitHub nos dados locais.
    Para cada item, mantém as antecipações com mais registros (local ou GitHub).
    """
    if not dados_github or "itens" not in dados_github:
        return dados_local

    # Indexar itens do GitHub por ID
    github_por_id = {i["id"]: i for i in dados_github.get("itens", [])}

    for item in dados_local.get("itens", []):
        github_item = github_por_id.get(item["id"])
        if not github_item:
            continue

        ant_local = item.get("antecipacoes", [])
        ant_github = github_item.get("antecipacoes", [])

        # Se GitHub tem mais antecipações confirmadas, usar as do GitHub
        conf_local = [a for a in ant_local if a.get("status") == "confirmada"]
        conf_github = [a for a in ant_github if a.get("status") == "confirmada"]

        if len(conf_github) > len(conf_local):
            item["antecipacoes"] = ant_github

    return dados_local

def carregar_dados():
    """Carrega dados do disco e mescla com GitHub para preservar antecipações"""
    dados = None

    # 1. Tentar carregar do disco local
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
        except Exception as e:
            st.error(f"Erro ao carregar dados locais: {e}")

    # 2. Buscar dados do GitHub (uma única vez)
    dados_github = None
    try:
        dados_github = pull_from_github()
    except:
        pass

    # 3. Se não tem dados locais, usar GitHub
    if not dados or "itens" not in dados:
        if dados_github and "itens" in dados_github:
            dados = dados_github
            # Salvar localmente para cache
            try:
                with open(DADOS_ARQUIVO, "w", encoding="utf-8") as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)
            except:
                pass

    # 4. Se tem dados, mesclar antecipações do GitHub (evita perda)
    if dados and "itens" in dados:
        dados = _mesclar_antecipacoes(dados, dados_github)
        return dados

    # 4. Dados padrão iniciais (último recurso)
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
        # 1. Valores base: parcela fixa, ou o valor vigente em cada mês para item
        #    contínuo com reajustes (itens_modelo.py). Fora do período, 0.
        df[col_name] = serie_do_item(item, MESES_TODOS)
        
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
st.markdown("""
<div style='margin-bottom: 0.5rem;'>
    <h1 style='
        font-family: Playfair Display, serif !important;
        color: #0A1628 !important;
        font-size: 1.875rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.25rem !important;
    '>Dashboard Ana</h1>
    <p style='
        font-family: DM Sans, sans-serif;
        color: #6B7280;
        font-size: 0.8rem;
        letter-spacing: 0.04em;
    '>Gestão Financeira Pessoal</p>
</div>
""", unsafe_allow_html=True)
st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} — valores em R$")

# ========================================
# CÁLCULO DO DATAFRAME ANTES DAS ABAS
# ========================================
df = calcular_dataframe()

# ========================================
# NAVEGAÇÃO POR ABAS
# ========================================
aba1, aba2, aba3, aba4 = st.tabs(["Gestão Executiva", "Detalhamento Mensal", "Gerenciar Itens", "Antecipar Parcelas"])

with aba1:
    # === GESTÃO EXECUTIVA — o acerto do mês entre você e a Ana ===
    # O seletor de mês agora vive dentro do módulo. O antigo usava strptime("%b/%y"),
    # que não reconhece "fev", "set", "dez"... e caía sempre num mês errado.
    exibir_gestao_executiva(st.session_state.itens, st.session_state.meses_quitados, df)

with aba2:
    # === DETALHAMENTO MENSAL — quitar meses e acompanhar as parcelas ===
    # KPIs e gráfico de saldo saíram: repetiam a Gestão Executiva. A rosca somava
    # os 48 meses e o "Total Acumulado" não tinha leitura útil.
    exibir_detalhamento_mensal(
        st.session_state.itens,
        df,
        lambda: salvar_dados(st.session_state.itens, st.session_state.meses_quitados),
    )


with aba4:
    # === ANTECIPAR PARCELAS — parcelas pagas fora do mês previsto e o efeito no acerto ===
    # Grava pela mesma via das outras abas (salvar_dados): uma gravação por ação,
    # em vez de uma gravação e um push por parcela no AntecipacaoService.
    if FEATURE_ANTECIPACAO:
        exibir_antecipar_parcelas(
            df,
            lambda: salvar_dados(st.session_state.itens, st.session_state.meses_quitados),
            calcular_cronograma_atual,
        )
    else:
        st.info("A antecipação de parcelas está desligada neste ambiente.")


with aba3:
    # === GERENCIAR ITENS — o que entra no acerto, reajustes e correções ===
    # O "Extrato Mensal por Ano" saiu: a Gestão Executiva mostra a conta de cada mês.
    exibir_gerenciar_itens(
        df,
        lambda: salvar_dados(st.session_state.itens, st.session_state.meses_quitados),
        calcular_cronograma_atual,
    )
