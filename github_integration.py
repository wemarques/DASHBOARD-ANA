import os
import json
import base64
import logging
import requests
import streamlit as st

logger = logging.getLogger(__name__)

# Configurações do Repositório
REPO_OWNER = "wemarques"
REPO_NAME = "DASHBOARD-ANA"
FILE_PATH = "dados_dashboard_ana.json"
BRANCH = "master"

# Log de último erro para exibição na UI
_ultimo_erro_push = {"msg": None}

def get_github_token():
    """Tenta recuperar o token do GitHub dos secrets ou env vars"""
    # 1. Tentar st.secrets (Streamlit Cloud)
    try:
        if hasattr(st, "secrets"):
            token = st.secrets.get("GITHUB_TOKEN", None)
            if token:
                return token
    except Exception:
        pass

    # 2. Tentar variável de ambiente
    return os.environ.get("GITHUB_TOKEN")

def diagnosticar_token():
    """
    Testa o token do GitHub: leitura e escrita.
    Retorna dict com resultado do diagnóstico.
    """
    result = {"token_encontrado": False, "leitura_ok": False, "escrita_ok": False, "erro": None}

    token = get_github_token()
    if not token:
        result["erro"] = "Token não encontrado em st.secrets nem em env vars"
        return result

    result["token_encontrado"] = True
    result["token_preview"] = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # Teste de leitura
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            result["leitura_ok"] = True
        else:
            result["erro"] = f"GET falhou: {resp.status_code} - {resp.json().get('message', '')}"
            return result

        # Teste de escrita (verificar permissões sem alterar dados)
        # Usar API de permissions do repo
        perm_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
        perm_resp = requests.get(perm_url, headers=headers, timeout=10)
        if perm_resp.status_code == 200:
            permissions = perm_resp.json().get("permissions", {})
            result["escrita_ok"] = permissions.get("push", False)
            if not result["escrita_ok"]:
                result["erro"] = f"Token sem permissão de escrita. Permissions: {permissions}"
        else:
            result["erro"] = f"Não foi possível verificar permissões: {perm_resp.status_code}"

    except Exception as e:
        result["erro"] = f"Exceção: {str(e)}"

    return result

def push_to_github(json_content, commit_message="Update data via Streamlit App"):
    """
    Envia o conteúdo JSON atualizado para o GitHub.
    Retorna True se sucesso, False se falha.
    Erros são logados e armazenados em _ultimo_erro_push para exibição na UI.
    """
    token = get_github_token()

    if not token:
        erro = "GITHUB_TOKEN não encontrado. Persistência na nuvem desativada."
        logger.warning(erro)
        _ultimo_erro_push["msg"] = erro
        return False

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. Obter o SHA atual do arquivo (necessário para update)
        get_response = requests.get(url, headers=headers, timeout=15)

        if get_response.status_code == 200:
            file_data = get_response.json()
            sha = file_data["sha"]
        elif get_response.status_code == 401:
            erro = f"Token inválido ou expirado (401). Verifique GITHUB_TOKEN."
            logger.error(erro)
            _ultimo_erro_push["msg"] = erro
            return False
        elif get_response.status_code == 404:
            erro = f"Arquivo não encontrado no GitHub (404). Verifique repo/branch."
            logger.error(erro)
            _ultimo_erro_push["msg"] = erro
            return False
        else:
            erro = f"Erro ao obter arquivo do GitHub: {get_response.status_code} - {get_response.text[:200]}"
            logger.error(erro)
            _ultimo_erro_push["msg"] = erro
            return False

        # 2. Preparar o conteúdo em Base64
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

        put_response = requests.put(url, headers=headers, json=data, timeout=30)

        if put_response.status_code in [200, 201]:
            logger.info("Dados salvos no GitHub com sucesso!")
            _ultimo_erro_push["msg"] = None
            return True
        elif put_response.status_code == 403:
            erro = f"Sem permissão de escrita (403). O token precisa de permissão 'Contents: Read and write' no repo."
            logger.error(erro)
            _ultimo_erro_push["msg"] = erro
            return False
        elif put_response.status_code == 409:
            erro = f"Conflito de SHA (409). Outro processo atualizou o arquivo. Tente novamente."
            logger.error(erro)
            _ultimo_erro_push["msg"] = erro
            return False
        else:
            erro = f"Erro ao salvar no GitHub: {put_response.status_code} - {put_response.text[:200]}"
            logger.error(erro)
            _ultimo_erro_push["msg"] = erro
            return False

    except requests.exceptions.Timeout:
        erro = "Timeout ao conectar com GitHub. Tente novamente."
        logger.error(erro)
        _ultimo_erro_push["msg"] = erro
        return False
    except Exception as e:
        erro = f"Exceção ao conectar com GitHub: {str(e)}"
        logger.error(erro)
        _ultimo_erro_push["msg"] = erro
        return False

def pull_from_github():
    """
    Baixa o conteúdo do dados_dashboard_ana.json do GitHub.
    Retorna o dict com os dados ou None em caso de erro.
    """
    token = get_github_token()

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            file_data = response.json()
            content_b64 = file_data["content"]
            content_str = base64.b64decode(content_b64).decode("utf-8")
            return json.loads(content_str)
        else:
            print(f"Erro ao baixar dados do GitHub: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exceção ao conectar com GitHub para pull: {e}")
        return None
