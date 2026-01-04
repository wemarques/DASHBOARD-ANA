"""
Módulo de Estilos Customizados para Dashboard ANA
Sistema de cores moderno baseado em OKLCH com paleta financeira dedicada.
"""

import streamlit as st


def aplicar_estilos_customizados():
    """
    Aplica estilos CSS customizados ao dashboard usando variáveis CSS baseadas em OKLCH.
    Cores financeiras: verde para positivo, vermelho para negativo, azul neutro.
    """
    st.markdown("""
    <style>
    /* ========================================
       VARIÁVEIS CSS - PALETA DE CORES OKLCH
       ======================================== */
    :root {
        /* Cores Primárias */
        --primary: #3333CC;
        --primary-hover: #2A2AA8;
        --background: #FCFCFE;
        --secondary-background: #F5F5F7;
        --text: #1A1A1F;
        --muted-foreground: #6B6B99;
        
        /* Cores Financeiras */
        --finance-positive: #00A86B;
        --finance-positive-light: #E6F5F0;
        --finance-negative: #E63946;
        --finance-negative-light: #FDE8EA;
        --finance-neutral: #6B6B99;
        
        /* Cores de Interface */
        --border: #E8E8EB;
        --border-hover: #D0D0D5;
        --card-background: #FFFFFF;
        --shadow: rgba(0, 0, 0, 0.1);
        --shadow-hover: rgba(0, 0, 0, 0.15);
    }
    
    /* ========================================
       ESTILOS GLOBAIS
       ======================================== */
    .main {
        background-color: var(--background);
        color: var(--text);
    }
    
    .stApp {
        background-color: var(--background);
    }
    
    /* ========================================
       CARDS E CONTAINERS
       ======================================== */
    .card {
        background-color: var(--card-background);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px var(--shadow);
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
    
    .card:hover {
        box-shadow: 0 4px 8px var(--shadow-hover);
        border-color: var(--border-hover);
    }
    
    .card h3 {
        color: var(--text);
        margin-top: 0;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* ========================================
       BADGES E INDICADORES
       ======================================== */
    .badge-positive {
        display: inline-block;
        background-color: var(--finance-positive-light);
        color: var(--finance-positive);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.875rem;
        border: 1px solid var(--finance-positive);
    }
    
    .badge-negative {
        display: inline-block;
        background-color: var(--finance-negative-light);
        color: var(--finance-negative);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.875rem;
        border: 1px solid var(--finance-negative);
    }
    
    .badge-neutral {
        display: inline-block;
        background-color: var(--secondary-background);
        color: var(--finance-neutral);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.875rem;
        border: 1px solid var(--border);
    }
    
    /* ========================================
       VALORES FINANCEIROS
       ======================================== */
    .valor-positivo {
        color: var(--finance-positive);
        font-weight: 600;
    }
    
    .valor-negativo {
        color: var(--finance-negative);
        font-weight: 600;
    }
    
    .valor-neutro {
        color: var(--finance-neutral);
        font-weight: 500;
    }
    
    /* ========================================
       BOTÕES CUSTOMIZADOS
       ======================================== */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        border-color: var(--primary);
        box-shadow: 0 2px 4px var(--shadow);
    }
    
    /* ========================================
       INPUTS E SELECTBOXES
       ======================================== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid var(--border);
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(51, 51, 204, 0.1);
    }
    
    /* ========================================
       TABELAS
       ======================================== */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid var(--border);
    }
    
    .dataframe thead {
        background-color: var(--secondary-background);
    }
    
    .dataframe th {
        color: var(--text);
        font-weight: 600;
        border-bottom: 2px solid var(--border);
    }
    
    .dataframe td {
        border-bottom: 1px solid var(--border);
    }
    
    .dataframe tr:hover {
        background-color: var(--secondary-background);
    }
    
    /* ========================================
       EXPANDERS
       ======================================== */
    .streamlit-expanderHeader {
        border-radius: 8px;
        border: 1px solid var(--border);
        background-color: var(--card-background);
        transition: background-color 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--secondary-background);
    }
    
    /* ========================================
       MÉTRICAS
       ======================================== */
    [data-testid="stMetricValue"] {
        color: var(--text);
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--muted-foreground);
        font-weight: 500;
    }
    
    /* ========================================
       DIVIDERS
       ======================================== */
    hr {
        border-color: var(--border);
        margin: 1.5rem 0;
    }
    
    /* ========================================
       CAPTIONS E TEXTOS SECUNDÁRIOS
       ======================================== */
    .stCaption {
        color: var(--muted-foreground);
    }
    
    /* ========================================
       SIDEBAR
       ======================================== */
    .css-1d391kg {
        background-color: var(--secondary-background);
    }
    
    /* ========================================
       GRÁFICOS PLOTLY - ESTILOS BASE
       ======================================== */
    .js-plotly-plot {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)


def formatar_valor_financeiro(valor: float, incluir_sinal: bool = True) -> str:
    """
    Formata um valor financeiro com cor apropriada (verde para positivo, vermelho para negativo).
    
    Args:
        valor: Valor numérico a ser formatado
        incluir_sinal: Se True, inclui sinal + ou - antes do valor
    
    Returns:
        String HTML formatada com cor e valor em R$
    """
    # Formatação monetária BR
    valor_abs = abs(valor)
    valor_fmt = f"{valor_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Determinar cor e classe CSS
    if valor >= 0:
        classe_cor = "valor-positivo"
        sinal = "+ " if incluir_sinal else ""
    else:
        classe_cor = "valor-negativo"
        sinal = "- " if incluir_sinal else ""
    
    return f"<span class='{classe_cor}'>{sinal}R$ {valor_fmt}</span>"


def criar_badge(texto: str, tipo: str = "neutral") -> str:
    """
    Cria um badge HTML com estilo apropriado.
    
    Args:
        texto: Texto a ser exibido no badge
        tipo: Tipo do badge ("positive", "negative", "neutral")
    
    Returns:
        String HTML do badge
    """
    classe = f"badge-{tipo}"
    return f"<span class='{classe}'>{texto}</span>"


# Dicionário de cores para gráficos Plotly
CORES_GRAFICOS = {
    'positivo': '#00A86B',  # Verde
    'negativo': '#E63946',  # Vermelho
    'neutro': '#3333CC',    # Azul primário
    'acento': '#6B6B99'     # Azul neutro
}



