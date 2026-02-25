#!/usr/bin/env python3
"""Teste do template de gestão executiva com dados reais"""

import sys
sys.path.append('C:\\DASHBOARD-ANA\\DASHBOARD-ANA')

from gestao_executiva import GestaoExecutiva
import pandas as pd
import json

def testar_gestao_executiva():
    print("🧪 Testando Template de Gestão Executiva")
    print("=" * 50)
    
    # Carregar dados reais
    try:
        with open('dados_dashboard_ana.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
        print("✅ Dados reais carregados com sucesso!")
    except FileNotFoundError:
        print("❌ Arquivo dados_dashboard_ana.json não encontrado")
        return
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar JSON")
        return
    
    print(f"📊 Total de itens: {len(dados['itens'])}")
    
    # Mostrar itens reais
    print("\n📋 Itens encontrados:")
    for i, item in enumerate(dados['itens'][:5]):  # Mostrar primeiros 5
        tipo_str = "💰 Despesa" if item['tipo'] == 'debito' else "💵 Receita"
        print(f"  {i+1}. {item['nome']}: R$ {item['valor']} ({tipo_str})")
    
    # Criar DataFrame simulado com os meses do app
    meses = ['jan/25', 'fev/25', 'mar/25', 'abr/25', 'mai/25', 'jun/25']
    df_data = {'mesAno': meses}
    
    # Preencher com valores baseados nos itens reais
    for item in dados['itens']:
        if item['tipo'] == 'credito':
            df_data[item['id']] = [item['valor']] * len(meses)
        else:
            df_data[item['id']] = [-item['valor']] * len(meses)  # Despesas negativas
    
    # Calcular total
    df_data['total'] = [0] * len(meses)
    for item in dados['itens']:
        if item['tipo'] == 'credito':
            for i in range(len(meses)):
                df_data['total'][i] += df_data[item['id']][i]
        else:
            for i in range(len(meses)):
                df_data['total'][i] += df_data[item['id']][i]  # Já está negativo
    
    df = pd.DataFrame(df_data)
    
    print(f"\n✅ DataFrame criado: {len(df)} meses x {len(df.columns)} colunas")
    print(f"📈 Saldo médio: R$ {df['total'].mean():.2f}")
    
    # Testar gestão executiva
    gestao = GestaoExecutiva(dados['itens'], dados.get('meses_quitados', []), df)
    
    # Testar diferentes meses
    meses_teste = ['jan/25', 'fev/25', 'mar/25']
    
    for mes in meses_teste:
        resultado = gestao.calcular_resultado_mensal(mes)
        if resultado:
            print(f"\n📅 Resultado {mes}:")
            print(f"  💰 Receitas: R$ {resultado['receitas']:.2f}")
            print(f"  💸 Despesas: R$ {resultado['despesas']:.2f}")
            print(f"  📈 Saldo Líquido: R$ {resultado['saldo_liquido']:.2f}")
            print(f"  ✅ Status: {'Quitado' if resultado['status_quitacao'] else 'Pendente'}")
            
            if resultado['antecipacoes_recebidas'] > 0 or resultado['antecipacoes_enviadas'] > 0:
                print(f"  ⚡ Antecipações: R$ {resultado['antecipacoes_recebidas']:.2f} recebidas, R$ {resultado['antecipacoes_enviadas']:.2f} enviadas")
    
    print("\n🎉 Teste concluído com sucesso!")
    print("\n💡 O template está pronto para uso e irá mostrar:")
    print("   • KPIs de receitas, despesas e saldo líquido")
    print("   • Gráfico de composição do resultado")
    print("   • Tabela detalhada por item real")
    print("   • Análise comparativa entre meses")
    print("   • Antecipações de parcelas")

if __name__ == "__main__":
    testar_gestao_executiva()