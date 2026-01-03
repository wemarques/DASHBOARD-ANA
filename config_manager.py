import os
import json
import streamlit as st

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "features.json")

def load_feature_flags():
    """
    Carrega as feature flags baseadas no ambiente (APP_ENV).
    Ordem de prioridade:
    1. Variável de ambiente específica (ex: FEATURE_ANTECIPACAO_PARCELAS)
    2. Arquivo features.json (ambiente específico)
    3. Arquivo features.json (default)
    """
    
    # 1. Determinar ambiente
    env = os.environ.get("APP_ENV", "production")
    
    # 2. Carregar arquivo de configuração
    config_data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"Erro ao ler {CONFIG_FILE}: {e}")
            
    # 3. Função helper para buscar flag
    def get_flag(flag_name):
        env_var_name = flag_name.upper()
        
        # Prioridade 0: Streamlit Secrets (Cloud)
        if hasattr(st, "secrets") and env_var_name in st.secrets:
            val = str(st.secrets[env_var_name]).lower()
            return val in ("true", "1", "yes", "on")

        # Prioridade 1: Variável de ambiente direta
        if env_var_name in os.environ:
            val = os.environ[env_var_name].lower()
            return val in ("true", "1", "yes", "on")
            
        # Prioridade 2: Config do ambiente
        if env in config_data and flag_name in config_data[env]:
            return config_data[env][flag_name]
            
        # Prioridade 3: Default
        if "default" in config_data and flag_name in config_data["default"]:
            return config_data["default"][flag_name]
            
        return False

    return {
        "feature_antecipacao_parcelas": get_flag("feature_antecipacao_parcelas")
    }

# Inicializa flags no session_state se não existir
def init_flags():
    if "flags" not in st.session_state:
        st.session_state.flags = load_feature_flags()
