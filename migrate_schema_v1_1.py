import json
import os
import shutil
import argparse
from datetime import datetime
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_FILE = "dados_dashboard_ana.json"
BACKUP_DIR = "backups"
TARGET_SCHEMA_VERSION = "1.1"

def backup_data(dry_run=False):
    """Realiza backup do arquivo de dados."""
    if not os.path.exists(DATA_FILE):
        logger.error(f"Arquivo {DATA_FILE} não encontrado.")
        return False

    if not os.path.exists(BACKUP_DIR) and not dry_run:
        os.makedirs(BACKUP_DIR)
        logger.info(f"Diretório {BACKUP_DIR} criado.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"dados_dashboard_ana_migration_{timestamp}.json")

    if dry_run:
        logger.info(f"[DRY-RUN] Backup seria criado em: {backup_path}")
        return True

    try:
        shutil.copy2(DATA_FILE, backup_path)
        logger.info(f"Backup criado com sucesso: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Falha ao criar backup: {e}")
        return False

def migrate_data(dry_run=False):
    """Executa a migração dos dados para versão 1.1."""
    if not os.path.exists(DATA_FILE):
        logger.error(f"Arquivo {DATA_FILE} não encontrado.")
        return

    logger.info("Lendo arquivo de dados...")
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        logger.error("Erro ao decodificar JSON. Arquivo corrompido?")
        return

    changes_count = 0
    
    # 1. Atualizar Schema Version
    current_version = data.get("versao_schema", "1.0")
    if current_version != TARGET_SCHEMA_VERSION:
        logger.info(f"Atualizando versão do schema: {current_version} -> {TARGET_SCHEMA_VERSION}")
        data["versao_schema"] = TARGET_SCHEMA_VERSION
        changes_count += 1
    
    # 2. Migrar Itens (adicionar campo 'antecipacoes')
    if "itens" in data:
        for item in data["itens"]:
            if "antecipacoes" not in item:
                item["antecipacoes"] = []
                logger.info(f"Item '{item.get('nome', '???')}' atualizado: campo 'antecipacoes' adicionado.")
                changes_count += 1
    else:
        logger.error("Estrutura inválida: chave 'itens' não encontrada.")
        return

    if changes_count == 0:
        logger.info("Nenhuma alteração necessária. Arquivo já está atualizado.")
        return

    # 3. Validar JSON Resultante
    try:
        json_output = json.dumps(data, ensure_ascii=False, indent=2)
        logger.info("Validação do JSON resultante: OK")
    except TypeError as e:
        logger.error(f"Erro na validação do JSON final: {e}")
        return

    # 4. Gravar Arquivo
    if dry_run:
        logger.info(f"[DRY-RUN] Arquivo seria atualizado com {changes_count} alterações.")
    else:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                f.write(json_output)
            logger.info(f"Arquivo {DATA_FILE} atualizado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao gravar arquivo: {e}")

def main():
    parser = argparse.ArgumentParser(description="Script de Migração de Schema (v1.1) - Antecipações")
    parser.add_argument("--dry-run", action="store_true", help="Executa sem realizar alterações físicas")
    args = parser.parse_args()

    logger.info("Iniciando processo de migração v1.1...")
    
    if args.dry_run:
        logger.warning("MODO DRY-RUN ATIVADO: Nenhuma alteração será salva.")

    if backup_data(dry_run=args.dry_run):
        migrate_data(dry_run=args.dry_run)
    else:
        logger.error("Abortando migração devido a falha no backup.")

if __name__ == "__main__":
    main()
