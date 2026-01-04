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

# Lista completa de meses (jan/25 a dez/28)
MESES_TODOS = [
    "jan/25", "fev/25", "mar/25", "abr/25", "mai/25", "jun/25",
    "jul/25", "ago/25", "set/25", "out/25", "nov/25", "dez/25",
    "jan/26", "fev/26", "mar/26", "abr/26", "mai/26", "jun/26",
    "jul/26", "ago/26", "set/26", "out/26", "nov/26", "dez/26",
    "jan/27", "fev/27", "mar/27", "abr/27", "mai/27", "jun/27",
    "jul/27", "ago/27", "set/27", "out/27", "nov/27", "dez/27",
    "jan/28", "fev/28", "mar/28", "abr/28", "mai/28", "jun/28",
    "jul/28", "ago/28", "set/28", "out/28", "nov/28", "dez/28"
]

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

    def encurtar_fluxo_item(self, item_id):
        """
        Encurta o fluxo de um item baseado nas antecipações confirmadas.
        
        Para cada antecipação confirmada, o fim do item é encurtado em 1 mês.
        
        Args:
            item_id: ID do item a ser encurtado
        
        Returns:
            dict: {"success": bool, "novo_fim": str, "meses_encurtados": int}
        """
        data = self._load_data()
        
        if not data:
            return {"success": False, "message": "Dados não encontrados"}
        
        # Encontrar item
        item_found = None
        for item in data.get("itens", []):
            if item["id"] == item_id:
                item_found = item
                break
        
        if not item_found:
            return {"success": False, "message": "Item não encontrado"}
        
        # Contar antecipações confirmadas
        antecipacoes_confirmadas = [
            ant for ant in item_found.get("antecipacoes", [])
            if ant.get("status") == "confirmada"
        ]
        
        if not antecipacoes_confirmadas:
            return {"success": False, "message": "Nenhuma antecipação confirmada"}
        
        # Calcular novo fim
        inicio = item_found["inicio"]
        fim_atual = item_found["fim"]
        
        try:
            idx_inicio = MESES_TODOS.index(inicio)
            idx_fim = MESES_TODOS.index(fim_atual)
        except ValueError:
            return {"success": False, "message": "Meses inválidos"}
        
        # Encurtar: subtrair número de antecipações
        meses_encurtados = len(antecipacoes_confirmadas)
        novo_idx_fim = idx_fim - meses_encurtados
        
        # Validar que não fica menor que o início
        if novo_idx_fim < idx_inicio:
            novo_idx_fim = idx_inicio
        
        novo_fim = MESES_TODOS[novo_idx_fim]
        
        # Atualizar item
        fim_anterior = item_found["fim"]
        item_found["fim"] = novo_fim
        
        # Salvar
        self._save_data(data)
        self._log_audit("ENCURTAR_FLUXO", "sistema", {
            "item_id": item_id,
            "fim_anterior": fim_anterior,
            "novo_fim": novo_fim,
            "meses_encurtados": meses_encurtados
        })
        
        return {
            "success": True,
            "novo_fim": novo_fim,
            "meses_encurtados": meses_encurtados,
            "fim_anterior": fim_anterior
        }

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

        # Validação: verificar se a parcela já foi antecipada
        # Cada parcela só pode ser antecipada UMA VEZ
        for ant in item_found.get("antecipacoes", []):
            if ant["origem"] == mes_origem and ant["status"] == "confirmada":
                return {
                    "success": False, 
                    "message": f"A parcela {mes_origem} já foi antecipada para {ant['destino']}. Cancele a antecipação anterior se desejar reagendar."
                }

        # Permitir antecipar para qualquer mês (inclusive posteriores)
        # A validação de lógica de negócio será feita no frontend

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
