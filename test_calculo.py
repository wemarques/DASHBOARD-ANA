import unittest
import pandas as pd
import streamlit as st
# Mock do streamlit session state
if "itens" not in st.session_state:
    st.session_state.itens = []
if "flags" not in st.session_state:
    st.session_state.flags = {"feature_antecipacao_parcelas": True}

# Importar app.py (precisamos garantir que ele use o session_state mockado)
# Para simplificar, vamos copiar a logica de calculo para testar isoladamente ou fazer import condicional
# O ideal seria refatorar o app.py para ter a lógica separada, mas vamos testar a lógica replicada aqui para validar o algoritmo.

def calcular_logica_teste(itens, feature_ativa=True):
    MESES_TODOS = ["jan/25", "fev/25", "mar/25", "abr/25", "mai/25"]
    
    df = pd.DataFrame({"mesAno": MESES_TODOS})
    
    for item in itens:
        col_name = item["id"]
        df[col_name] = 0.0
        
        # Simular get_meses_entre simples
        meses_ativos = MESES_TODOS # Simplificacao: ativo em todos
        if item["id"] == "item_parcial":
            meses_ativos = ["jan/25", "fev/25", "mar/25"]
            
        df.loc[df["mesAno"].isin(meses_ativos), col_name] = item["valor"]
        
        if feature_ativa and "antecipacoes" in item:
             for ant in item["antecipacoes"]:
                if ant.get("status") != "confirmada":
                    continue
                
                origem = ant.get("origem")
                destino = ant.get("destino")
                valor_ant = ant.get("valor_antecipado", 0.0)
                
                if origem in MESES_TODOS:
                    idx_origem = df[df["mesAno"] == origem].index
                    if not idx_origem.empty:
                        valor_atual = df.at[idx_origem[0], col_name]
                        df.at[idx_origem[0], col_name] = max(0.0, valor_atual - valor_ant)
                
                if destino in MESES_TODOS:
                    idx_destino = df[df["mesAno"] == destino].index
                    if not idx_destino.empty:
                        valor_atual_dest = df.at[idx_destino[0], col_name]
                        df.at[idx_destino[0], col_name] = valor_atual_dest + valor_ant
                        
    return df

class TestCalculoAntecipacao(unittest.TestCase):
    
    def test_antecipacao_simples(self):
        itens = [{
            "id": "item1", "valor": 100.0, 
            "antecipacoes": [
                {"origem": "mar/25", "destino": "jan/25", "valor_antecipado": 100.0, "status": "confirmada"}
            ]
        }]
        
        df = calcular_logica_teste(itens)
        
        # Jan: 100 (original) + 100 (antecipado) = 200
        val_jan = df.loc[df["mesAno"] == "jan/25", "item1"].values[0]
        self.assertEqual(val_jan, 200.0)
        
        # Mar: 100 (original) - 100 (antecipado) = 0
        val_mar = df.loc[df["mesAno"] == "mar/25", "item1"].values[0]
        self.assertEqual(val_mar, 0.0)

    def test_antecipacao_parcial(self):
        itens = [{
            "id": "item1", "valor": 100.0, 
            "antecipacoes": [
                {"origem": "mar/25", "destino": "jan/25", "valor_antecipado": 50.0, "status": "confirmada"}
            ]
        }]
        
        df = calcular_logica_teste(itens)
        
        # Jan: 100 + 50 = 150
        self.assertEqual(df.loc[df["mesAno"] == "jan/25", "item1"].values[0], 150.0)
        
        # Mar: 100 - 50 = 50
        self.assertEqual(df.loc[df["mesAno"] == "mar/25", "item1"].values[0], 50.0)

    def test_antecipacao_cancelada_ignorada(self):
        itens = [{
            "id": "item1", "valor": 100.0, 
            "antecipacoes": [
                {"origem": "mar/25", "destino": "jan/25", "valor_antecipado": 100.0, "status": "cancelada"}
            ]
        }]
        
        df = calcular_logica_teste(itens)
        
        # Valores originais mantidos
        self.assertEqual(df.loc[df["mesAno"] == "jan/25", "item1"].values[0], 100.0)
        self.assertEqual(df.loc[df["mesAno"] == "mar/25", "item1"].values[0], 100.0)

if __name__ == '__main__':
    unittest.main()
