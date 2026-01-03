import unittest
import os
import json
import time
from backend_antecipacao import AntecipacaoService
# Vamos importar a logica de calculo do test_calculo para garantir consistencia nos testes de integração
from test_calculo import calcular_logica_teste

class TestIntegracaoAntecipacao(unittest.TestCase):
    
    def setUp(self):
        # Ambiente de teste limpo
        self.test_file = "dados_integracao.json"
        self.initial_data = {
            "versao_schema": "1.1",
            "itens": [
                {"id": "item1", "nome": "Item Teste", "valor": 100.0, "inicio": "jan/25", "fim": "dez/25", "tipo": "debito", "antecipacoes": []}
            ]
        }
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(self.initial_data, f)
            
        self.service = AntecipacaoService(data_file=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_fluxo_completo_antecipacao(self):
        # 1. Estado Inicial
        with open(self.test_file, "r", encoding="utf-8") as f:
            data_before = json.load(f)
        
        df_before = calcular_logica_teste(data_before["itens"])
        val_jan_before = df_before.loc[df_before["mesAno"] == "jan/25", "item1"].values[0]
        val_mar_before = df_before.loc[df_before["mesAno"] == "mar/25", "item1"].values[0]
        
        self.assertEqual(val_jan_before, 100.0)
        self.assertEqual(val_mar_before, 100.0)
        
        # 2. Executar Antecipação (Mar -> Jan)
        print("\n[TEST] Executando antecipação de R$ 100,00 (mar/25 -> jan/25)...")
        start_time = time.time()
        
        res = self.service.criar_antecipacao("item1", "mar/25", "jan/25", 100.0, "tester")
        self.assertTrue(res["success"])
        
        duration = time.time() - start_time
        print(f"[PERF] Tempo de gravação: {duration:.4f}s")
        
        # 3. Verificar Persistência
        with open(self.test_file, "r", encoding="utf-8") as f:
            data_after = json.load(f)
            
        self.assertEqual(len(data_after["itens"][0]["antecipacoes"]), 1)
        self.assertEqual(data_after["itens"][0]["antecipacoes"][0]["status"], "confirmada")
        
        # 4. Verificar Recálculo
        df_after = calcular_logica_teste(data_after["itens"])
        val_jan_after = df_after.loc[df_after["mesAno"] == "jan/25", "item1"].values[0]
        val_mar_after = df_after.loc[df_after["mesAno"] == "mar/25", "item1"].values[0]
        
        # Jan deve ter 200 (100 original + 100 antecipado)
        self.assertEqual(val_jan_after, 200.0)
        # Mar deve ter 0 (100 original - 100 antecipado)
        self.assertEqual(val_mar_after, 0.0)
        
        print("[TEST] Valores recalculados corretamente.")
        
        # 5. Cancelar Antecipação
        print("[TEST] Cancelando antecipação...")
        id_ant = res["data"]["id_antecipacao"]
        res_undo = self.service.cancelar_antecipacao("item1", id_ant, "tester")
        self.assertTrue(res_undo["success"])
        
        # 6. Verificar Rollback Lógico
        with open(self.test_file, "r", encoding="utf-8") as f:
            data_final = json.load(f)
            
        df_final = calcular_logica_teste(data_final["itens"])
        val_jan_final = df_final.loc[df_final["mesAno"] == "jan/25", "item1"].values[0]
        val_mar_final = df_final.loc[df_final["mesAno"] == "mar/25", "item1"].values[0]
        
        self.assertEqual(val_jan_final, 100.0)
        self.assertEqual(val_mar_final, 100.0)
        
        print("[TEST] Rollback de valores confirmado.")

if __name__ == '__main__':
    unittest.main()
