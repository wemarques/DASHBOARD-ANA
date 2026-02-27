import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from backend_antecipacao import AntecipacaoService
from streamlit_custom_styles import get_plotly_layout_theme

class GestaoExecutiva:
    def __init__(self, itens, meses_quitados, df_calculado):
        self.itens = itens
        self.meses_quitados = meses_quitados
        self.df = df_calculado
        self.antecipacao_service = AntecipacaoService()

    def formatar_moeda(self, valor):
        """Formata valor para moeda brasileira"""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def calcular_resultado_mensal(self, mes_ano):
        """Calcula o resultado financeiro de um mês específico"""
        if mes_ano not in self.df['mesAno'].values:
            return None

        # Filtrar dados do mês
        mes_data = self.df[self.df['mesAno'] == mes_ano].iloc[0]

        # Calcular receitas e despesas
        receitas = 0
        despesas = 0

        for item in self.itens:
            col_name = item["id"]
            valor = mes_data[col_name] if col_name in mes_data else 0

            if item["tipo"] == "credito":
                receitas += valor
            else:
                despesas += valor

        # Calcular antecipações do mês
        antecipacoes_mes = self._calcular_antecipacoes_mes(mes_ano)

        return {
            'mes': mes_ano,
            'receitas': receitas,
            'despesas': abs(despesas),  # Valor positivo para despesas
            'saldo_liquido': receitas - abs(despesas),
            'antecipacoes_recebidas': antecipacoes_mes['recebidas'],
            'antecipacoes_enviadas': antecipacoes_mes['enviadas'],
            'status_quitacao': mes_ano in self.meses_quitados
        }

    def _calcular_antecipacoes_mes(self, mes_ano):
        """Calcula antecipações recebidas e enviadas no mês"""
        antecipacoes = self.antecipacao_service.listar_antecipacoes(status="confirmada")

        recebidas = 0
        enviadas = 0

        for ant in antecipacoes:
            if ant['destino'] == mes_ano:
                recebidas += ant['valor_antecipado']
            if ant['origem'] == mes_ano:
                enviadas += ant['valor_antecipado']

        return {'recebidas': recebidas, 'enviadas': enviadas}

    def criar_dashboard_executivo(self, mes_selecionado=None):
        """Cria o dashboard executivo completo"""

        # Se não houver mês selecionado, usar o mês atual
        if not mes_selecionado:
            mes_atual = datetime.now().strftime("%b/%y").lower()
            # Encontrar o mês mais próximo nos dados
            meses_disponiveis = [m for m in self.df['mesAno'] if datetime.strptime(m, "%b/%y") <= datetime.now()]
            mes_selecionado = meses_disponiveis[-1] if meses_disponiveis else self.df['mesAno'].iloc[0]

        resultado = self.calcular_resultado_mensal(mes_selecionado)

        if not resultado:
            st.error(f"Mês {mes_selecionado} não encontrado nos dados.")
            return

        st.title("Dashboard Executivo — Gestão Financeira")
        st.subheader(f"Resultado Mensal: {mes_selecionado}")

        # Cards de KPIs principais – layout responsivo
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            st.metric(
                label="RECEITAS DO MÊS",
                value=self.formatar_moeda(resultado['receitas']),
                delta="vs média" if resultado['receitas'] > 0 else None
            )

        with col2:
            st.metric(
                label="DESPESAS DO MÊS",
                value=self.formatar_moeda(resultado['despesas']),
                delta_color="inverse"
            )

        with col3:
            cor_delta = "normal" if resultado['saldo_liquido'] >= 0 else "inverse"
            st.metric(
                label="SALDO LÍQUIDO",
                value=self.formatar_moeda(resultado['saldo_liquido']),
                delta_color=cor_delta
            )

        with col4:
            status_text = "Quitado" if resultado['status_quitacao'] else "Pendente"
            st.metric(
                label="STATUS DO MÊS",
                value=status_text
            )

        st.divider()

        # Análise de Antecipações
        if resultado['antecipacoes_recebidas'] > 0 or resultado['antecipacoes_enviadas'] > 0:
            st.subheader("Movimentação de Antecipações")

            col_ant1, col_ant2 = st.columns([1, 1])

            with col_ant1:
                st.metric(
                    label="ANTECIPAÇÕES RECEBIDAS",
                    value=self.formatar_moeda(resultado['antecipacoes_recebidas'])
                )

            with col_ant2:
                st.metric(
                    label="ANTECIPAÇÕES ENVIADAS",
                    value=self.formatar_moeda(resultado['antecipacoes_enviadas'])
                )

        st.divider()

        # Gráfico de composição do resultado
        st.subheader("Composição do Resultado Mensal")

        # Dados para o gráfico de barras
        dados_grafico = {
            'Categoria': ['Receitas', 'Despesas', 'Saldo Líquido'],
            'Valor': [resultado['receitas'], -resultado['despesas'], resultado['saldo_liquido']],
            'Cor': ['Receitas', 'Despesas', 'Saldo']
        }

        df_grafico = pd.DataFrame(dados_grafico)

        fig = go.Figure()

        # Cores Marinho + Dourado
        colors = {'Receitas': '#10B981', 'Despesas': '#EF4444', 'Saldo Líquido': '#0A1628'}

        for categoria in df_grafico['Categoria'].unique():
            df_cat = df_grafico[df_grafico['Categoria'] == categoria]
            fig.add_trace(go.Bar(
                name=categoria,
                x=df_cat['Categoria'],
                y=df_cat['Valor'],
                marker_color=colors.get(categoria, '#0A1628'),
                marker_line=dict(color='rgba(255,255,255,0.3)', width=0),
                text=[self.formatar_moeda(val) for val in df_cat['Valor']],
                textposition='auto',
                textfont=dict(family='DM Mono, monospace', size=12)
            ))

        fig.update_layout(**get_plotly_layout_theme())
        fig.update_layout(
            title=f"Análise Financeira — {mes_selecionado}",
            xaxis_title="Categoria",
            yaxis_title="Valor (R$)",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Tabela detalhada por item
        st.subheader("Detalhamento por Item")

        dados_detalhados = []
        for item in self.itens:
            col_name = item["id"]
            valor_mes = self.df[self.df['mesAno'] == mes_selecionado][col_name].iloc[0] if col_name in self.df.columns else 0

            if valor_mes != 0:  # Mostrar apenas itens com valor no mês
                dados_detalhados.append({
                    'Item': item['nome'],
                    'Tipo': 'Despesa' if item['tipo'] == 'debito' else 'Receita',
                    'Valor Mensal': self.formatar_moeda(valor_mes),
                    'Categoria': 'Despesa Fixa' if item['tipo'] == 'debito' else 'Receita'
                })

        if dados_detalhados:
            df_detalhe = pd.DataFrame(dados_detalhados)
            st.dataframe(df_detalhe, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum item com valor no mês selecionado.")

        st.divider()

        # Seletor de mês para análise comparativa
        st.subheader("Análise Comparativa")

        meses_disponiveis = list(self.df['mesAno'])
        mes_comparativo = st.selectbox(
            "Selecione um mês para comparar:",
            meses_disponiveis,
            index=meses_disponiveis.index(mes_selecionado) if mes_selecionado in meses_disponiveis else 0
        )

        if mes_comparativo and mes_comparativo != mes_selecionado:
            resultado_comparativo = self.calcular_resultado_mensal(mes_comparativo)

            if resultado_comparativo:
                col_comp1, col_comp2, col_comp3 = st.columns([1, 1, 1])

                with col_comp1:
                    delta_receitas = resultado['receitas'] - resultado_comparativo['receitas']
                    st.metric(
                        label="VARIAÇÃO RECEITAS",
                        value=self.formatar_moeda(delta_receitas),
                        delta=f"vs {mes_comparativo}"
                    )

                with col_comp2:
                    delta_despesas = resultado['despesas'] - resultado_comparativo['despesas']
                    st.metric(
                        label="VARIAÇÃO DESPESAS",
                        value=self.formatar_moeda(delta_despesas),
                        delta=f"vs {mes_comparativo}"
                    )

                with col_comp3:
                    delta_saldo = resultado['saldo_liquido'] - resultado_comparativo['saldo_liquido']
                    st.metric(
                        label="VARIAÇÃO SALDO",
                        value=self.formatar_moeda(delta_saldo),
                        delta=f"vs {mes_comparativo}"
                    )

    def criar_resumo_executivo(self):
        """Cria um resumo executivo rápido"""
        st.title("Resumo Executivo")

        # Últimos 3 meses até o mês atual (não meses futuros do DataFrame)
        _nomes = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
        agora = datetime.now()
        mes_atual_str = f"{_nomes[agora.month - 1]}/{str(agora.year)[2:]}"
        todos_meses = list(self.df['mesAno'])
        if mes_atual_str in todos_meses:
            idx = todos_meses.index(mes_atual_str)
            start = max(0, idx - 2)
            ultimos_meses = todos_meses[start:idx + 1]
        else:
            # Fallback: pegar últimos 3 meses com dados (total != 0)
            meses_com_dados = [m for m in todos_meses if self.df.loc[self.df['mesAno'] == m, 'total'].iloc[0] != 0]
            ultimos_meses = meses_com_dados[-3:] if meses_com_dados else todos_meses[:3]

        resultados = []
        for mes in ultimos_meses:
            resultado = self.calcular_resultado_mensal(mes)
            if resultado:
                resultados.append(resultado)

        if resultados:
            # KPIs consolidados
            receita_media = sum(r['receitas'] for r in resultados) / len(resultados)
            despesa_media = sum(r['despesas'] for r in resultados) / len(resultados)
            saldo_medio = sum(r['saldo_liquido'] for r in resultados) / len(resultados)

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                st.metric(
                    label="RECEITA MÉDIA (3M)",
                    value=self.formatar_moeda(receita_media)
                )

            with col2:
                st.metric(
                    label="DESPESA MÉDIA (3M)",
                    value=self.formatar_moeda(despesa_media)
                )

            with col3:
                cor = "normal" if saldo_medio >= 0 else "inverse"
                st.metric(
                    label="SALDO MÉDIO (3M)",
                    value=self.formatar_moeda(saldo_medio),
                    delta_color=cor
                )

        return resultados

# Função auxiliar para integrar ao app principal
def exibir_gestao_executiva(itens, meses_quitados, df_calculado, mes_selecionado=None):
    """Função para ser chamada pelo app principal"""
    gestao = GestaoExecutiva(itens, meses_quitados, df_calculado)
    gestao.criar_dashboard_executivo(mes_selecionado)

# Função de resumo rápido
def exibir_resumo_executivo(itens, meses_quitados, df_calculado):
    """Exibe apenas o resumo executivo"""
    gestao = GestaoExecutiva(itens, meses_quitados, df_calculado)
    return gestao.criar_resumo_executivo()
