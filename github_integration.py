import os
import json
import base64
import requests
import streamlit as st

# Configurações do Repositório
REPO_OWNER = "wemarques"
REPO_NAME = "DASHBOARD-ANA"
FILE_PATH = "dados_dashboard_ana.json"
BRANCH = "master"

def get_github_token():
    """Tenta recuperar o token do GitHub dos secrets ou env vars"""
    if hasattr(st, "secrets") and "GITHUB_TOKEN" in st.secrets:
        return st.secrets["GITHUB_TOKEN"]
    return os.environ.get("GITHUB_TOKEN")

def push_to_github(json_content, commit_message="Update data via Streamlit App"):
    """
    Envia o conteúdo JSON atualizado para o GitHub.
    """
    token = get_github_token()
    
    if not token:
        print("⚠️ GITHUB_TOKEN não encontrado. Persistência na nuvem desativada.")
        return False

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. Obter o SHA atual do arquivo (necessário para update)
        get_response = requests.get(url, headers=headers)
        
        if get_response.status_code == 200:
            file_data = get_response.json()
            sha = file_data["sha"]
        else:
            # Se arquivo não existe (o que seria estranho), ou erro de permissão
            print(f"Erro ao obter arquivo do GitHub: {get_response.text}")
            return False

        # 2. Preparar o conteúdo em Base64
        # Converter dict para string JSON formatada se necessário
        if isinstance(json_content, dict) or isinstance(json_content, list):
            content_str = json.dumps(json_content, ensure_ascii=False, indent=2)
        else:
            content_str = json_content
            
        content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")

        # 3. Enviar atualização (PUT)
        data = {
            "message": commit_message,
            "content": content_b64,
            "sha": sha,
            "branch": BRANCH
        }

        put_response = requests.put(url, headers=headers, json=data)

        if put_response.status_code in [200, 201]:
            print("✅ Dados salvos no GitHub com sucesso!")
            return True
        else:
            print(f"❌ Erro ao salvar no GitHub: {put_response.status_code} - {put_response.text}")
            return False

    except Exception as e:
        print(f"❌ Exceção ao conectar com GitHub: {str(e)}")
        return False
