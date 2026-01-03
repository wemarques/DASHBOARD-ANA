import unittest
import os
import json
import shutil
from migrate_schema_v1_1 import migrate_data, backup_data, DATA_FILE, BACKUP_DIR
from backend_antecipacao import AntecipacaoService

class TestAntecipacaoBackend(unittest.TestCase):
    
    def setUp(self):
        # Setup: Criar arquivo de dados fake
        self.test_file = "dados_test_antecipacao.json"
        self.initial_data = {
            "versao_schema": "1.0",
            "itens": [
                {"id": "item1", "nome": "Item Teste", "valor": 100.0, "inicio": "jan/25", "fim": "dez/25", "tipo": "debito"}
            ]
        }
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(self.initial_data, f)
            
        # Redirecionar constantes para teste (Monkey Patching simples seria ideal, mas aqui vamos usar injeção se possível ou apenas cuidar dos arquivos)
        # Como o script de migração usa variáveis globais, vamos ter que confiar no ambiente de teste isolado ou modificar o script para aceitar parametro de arquivo.
        # Para simplificar neste teste rápido, vamos instanciar o Service apontando para o arquivo de teste.
        
        self.service = AntecipacaoService(data_file=self.test_file)

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists("audit_log.json"):
            os.remove("audit_log.json")

    def test_criar_antecipacao_sucesso(self):
        # Precisamos primeiro garantir que o schema suporta (embora o código suporte sem, é bom testar o fluxo completo)
        # O backend adiciona a lista se não existir, então ok.
        
        result = self.service.criar_antecipacao(
            item_id="item1",
            mes_origem="mai/25",
            mes_destino="mar/25",
            valor=100.0,
            usuario="tester"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["status"], "confirmada")
        
        # Verificar persistência
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data["itens"][0]["antecipacoes"]), 1)
            self.assertEqual(data["itens"][0]["antecipacoes"][0]["origem"], "mai/25")

    def test_validacao_destino_invalido(self):
        # Tentar antecipar para o futuro (origem antes do destino) -> ERRO
        result = self.service.criar_antecipacao(
            item_id="item1",
            mes_origem="mar/25",
            mes_destino="mai/25", # Destino depois da origem
            valor=100.0,
            usuario="tester"
        )
        self.assertFalse(result["success"])
        self.assertIn("anterior", result["message"])

    def test_validacao_duplicidade(self):
        self.service.criar_antecipacao("item1", "mai/25", "mar/25", 100.0, "tester")
        
        # Tentar criar de novo para mesma origem
        result = self.service.criar_antecipacao("item1", "mai/25", "abr/25", 100.0, "tester")
        
        self.assertFalse(result["success"])
        self.assertIn("Já existe", result["message"])

    def test_cancelar_antecipacao(self):
        # Criar
        res_criar = self.service.criar_antecipacao("item1", "mai/25", "mar/25", 100.0, "tester")
        id_ant = res_criar["data"]["id_antecipacao"]
        
        # Cancelar
        res_cancel = self.service.cancelar_antecipacao("item1", id_ant, "admin")
        self.assertTrue(res_cancel["success"])
        
        # Verificar status
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            status = data["itens"][0]["antecipacoes"][0]["status"]
            self.assertEqual(status, "cancelada")

if __name__ == '__main__':
    unittest.main()
