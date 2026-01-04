import uuid
from datetime import datetime
import json
import logging
import os

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_FILE = "dados_dashboard_ana.json"
AUDIT_LOG_FILE = "audit_log.json"

class AntecipacaoService:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
    
    def _load_data(self):
        if not os.path.exists(self.data_file):
            return None
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self, data):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _log_audit(self, action, user, details, success=True):
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "success": success,
            "details": details
        }
        
        # Append to audit log file (simple implementation)
        mode = "a" if os.path.exists(AUDIT_LOG_FILE) else "w"
        try:
            with open(AUDIT_LOG_FILE, mode, encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Falha ao gravar auditoria: {e}")

    def listar_antecipacoes(self, item_id=None, status=None):
        data = self._load_data()
        if not data:
            return []
        
        all_antecipacoes = []
        for item in data.get("itens", []):
            if item_id and item["id"] != item_id:
                continue
            
            for ant in item.get("antecipacoes", []):
                if status and ant["status"] != status:
                    continue
                # Enriquecer com nome do item para display
                ant_display = ant.copy()
                ant_display["item_nome"] = item["nome"]
                all_antecipacoes.append(ant_display)
        
        return all_antecipacoes

    def criar_antecipacao(self, item_id, mes_origem, mes_destino, valor, usuario, motivo=None):
        # Validações Server-Side
        if valor <= 0:
            return {"success": False, "message": "Valor deve ser positivo."}

        data = self._load_data()
        item_found = None
        for item in data.get("itens", []):
            if item["id"] == item_id:
                item_found = item
                break
        
        if not item_found:
            return {"success": False, "message": "Item não encontrado."}

        # Validar se já existe antecipação para esta origem
        for ant in item_found.get("antecipacoes", []):
            if ant["origem"] == mes_origem and ant["status"] != "cancelada":
                return {"success": False, "message": "Já existe uma antecipação ativa para este mês de origem."}

        # Validar mês de destino (não pode ser depois da origem)
        # Assumindo formato "mmm/yy" -> converter para date para comparar
        try:
            def parse_mes(m):
                meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
                mes_str, ano_str = m.split('/')
                mes_idx = meses.index(mes_str) + 1
                return datetime(int("20" + ano_str), mes_idx, 1)

            dt_origem = parse_mes(mes_origem)
            dt_destino = parse_mes(mes_destino)

            # Nova regra: Destino pode ser igual à origem (se quiser pagar no mesmo mês mas marcar diferente)
            # Mas o principal uso é antecipar (destino < origem).
            # Se destino > origem, é postergação (ainda não suportado, mas vamos bloquear).
            
            if dt_destino > dt_origem:
                return {"success": False, "message": "Mês de destino deve ser anterior ou igual ao mês de origem."}
            
        except ValueError:
             return {"success": False, "message": "Formato de mês inválido (use mmm/yy)."}

        # Criar Objeto de Antecipação
        nova_antecipacao = {
            "id_antecipacao": str(uuid.uuid4()),
            "id_parcela": f"{item_id}_{mes_origem}", # ID lógico da parcela
            "origem": mes_origem,
            "destino": mes_destino,
            "valor_antecipado": float(valor),
            "usuario": usuario,
            "timestamp": datetime.now().isoformat(),
            "motivo": motivo or "",
            "status": "confirmada" # Ou pendente se tiver fluxo de aprovação
        }

        # Adicionar e Salvar (Atomicidade simples via arquivo único)
        if "antecipacoes" not in item_found:
            item_found["antecipacoes"] = []
        
        item_found["antecipacoes"].append(nova_antecipacao)
        
        self._save_data(data)
        self._log_audit("CRIAR_ANTECIPACAO", usuario, nova_antecipacao)
        
        return {"success": True, "data": nova_antecipacao}

    def cancelar_antecipacao(self, item_id, id_antecipacao, usuario):
        data = self._load_data()
        item_found = None
        ant_found = None
        
        for item in data.get("itens", []):
            if item["id"] == item_id:
                item_found = item
                for ant in item.get("antecipacoes", []):
                    if ant["id_antecipacao"] == id_antecipacao:
                        ant_found = ant
                        break
                break
        
        if not ant_found:
            return {"success": False, "message": "Antecipação não encontrada."}
            
        if ant_found["status"] == "cancelada":
             return {"success": False, "message": "Antecipação já está cancelada."}

        # Atualizar status
        ant_found["status"] = "cancelada"
        ant_found["cancelado_por"] = usuario
        ant_found["cancelado_em"] = datetime.now().isoformat()

        self._save_data(data)
        self._log_audit("CANCELAR_ANTECIPACAO", usuario, {"id_antecipacao": id_antecipacao, "item_id": item_id})

        return {"success": True}
