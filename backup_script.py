import shutil
import hashlib
import os
import json
from datetime import datetime

SOURCE_FILE = "dados_dashboard_ana.json"
BACKUP_DIR = "backups"

def backup_data():
    # 1. Verificar se arquivo origem existe
    if not os.path.exists(SOURCE_FILE):
        return {"status": "error", "message": "Arquivo de origem não encontrado"}

    # 2. Criar diretório de backup se não existir
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # 3. Gerar nome do backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"dados_dashboard_ana_backup_{timestamp}.json"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        # 4. Copiar arquivo
        shutil.copy2(SOURCE_FILE, backup_path)

        # 5. Calcular Hash SHA256
        sha256_hash = hashlib.sha256()
        with open(backup_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        file_hash = sha256_hash.hexdigest()

        return {
            "status": "success",
            "path": os.path.abspath(backup_path),
            "hash": file_hash
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    result = backup_data()
    print(json.dumps(result, indent=2))
