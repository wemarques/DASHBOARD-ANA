"""
Módulo de Estilos Customizados para Dashboard ANA
Design: Minimalista Luxuoso — Paleta Marinho + Dourado
Tipografia: Playfair Display (headings), DM Sans (body), DM Mono (dados financeiros)
"""

import streamlit as st


# Dicionário de cores para gráficos Plotly
CORES_GRAFICOS = {
    'positivo': '#10B981',    # Emerald
    'negativo': '#EF4444',    # Red
    'neutro': '#0A1628',      # Deep Navy
    'acento': '#C9A96E',      # Gold
    'navy_medium': '#162036',
    'navy_light': '#1C2940',
    'gold_light': '#E8D5B0',
    'text_muted': '#6B7280',
    'bg_warm': '#F8F6F3',
    'bg_white': '#FFFFFF',
}


def aplicar_estilos_customizados():
    """
    Aplica estilos CSS customizados ao dashboard.
    Paleta Marinho + Dourado com tipografia premium via Google Fonts.
    """
    # Google Fonts via <link> para evitar FOUT
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* ========================================
       CSS VARIABLES — MARINHO + DOURADO
       ======================================== */
    :root {
        /* Navy */
        --navy-deep: #0A1628;
        --navy-button: #1C2B4A;
        --navy-medium: #162036;
        --navy-light: #1C2940;
        --navy-muted: #2A3A52;

        /* Gold */
        --gold-primary: #C9A96E;
        --gold-light: #E8D5B0;
        --gold-dark: #A88B4A;
        --gold-subtle: rgba(201, 169, 110, 0.1);
        --gold-border: rgba(201, 169, 110, 0.3);

        /* Neutral */
        --bg-warm: #F8F6F3;
        --bg-white: #FFFFFF;
        --text-heading: #0A1628;
        --text-body: #374151;
        --text-muted: #6B7280;
        --text-caption: #9CA3AF;

        /* Financial */
        --finance-positive: #10B981;
        --finance-positive-light: #ECFDF5;
        --finance-negative: #EF4444;
        --finance-negative-light: #FEF2F2;

        /* Borders & Shadows */
        --border-light: #E5E7EB;
        --border-gold: rgba(201, 169, 110, 0.25);
        --shadow-card: 0 1px 3px rgba(10, 22, 40, 0.04), 0 1px 2px rgba(10, 22, 40, 0.06);
        --shadow-card-hover: 0 4px 12px rgba(10, 22, 40, 0.08), 0 2px 4px rgba(10, 22, 40, 0.04);
        --shadow-elevated: 0 10px 25px rgba(10, 22, 40, 0.1);

        /* Typography */
        --font-heading: 'Playfair Display', Georgia, 'Times New Roman', serif;
        --font-body: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono: 'DM Mono', 'SF Mono', 'Fira Code', monospace;

        /* Spacing */
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --radius-xl: 20px;

        /* Transitions */
        --transition: 200ms ease;
    }

    /* ========================================
       GLOBAL
       ======================================== */
    .stApp {
        background-color: var(--bg-warm) !important;
        font-family: var(--font-body) !important;
    }

    .main .block-container {
        max-width: 1200px !important;
        padding: 2rem 2.5rem !important;
    }

    /* ========================================
       TYPOGRAPHY
       ======================================== */
    h1, h2, h3,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: var(--font-heading) !important;
        color: var(--text-heading) !important;
        letter-spacing: -0.01em !important;
    }

    h1 { font-size: 2rem !important; font-weight: 600 !important; }
    h2 { font-size: 1.5rem !important; font-weight: 600 !important; }
    h3 { font-size: 1.125rem !important; font-weight: 600 !important; }

    p, .stMarkdown p, label, .stText {
        font-family: var(--font-body) !important;
        color: var(--text-body) !important;
    }

    /* Button text must inherit button color, not body text color */
    .stButton > button p,
    .stButton > button span,
    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: inherit !important;
    }

    /* Apply body font to spans but exclude Streamlit Material icons */
    span:not([data-testid="stIconMaterial"]) {
        font-family: var(--font-body);
        color: var(--text-body);
    }

    /* Preserve Material Symbols font for Streamlit UI icons (expander arrows, sidebar toggle, etc.) */
    [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    .stCaption, [data-testid="stCaptionContainer"] p {
        color: var(--text-caption) !important;
        font-family: var(--font-body) !important;
    }

    /* ========================================
       SIDEBAR — DARK NAVY
       ======================================== */
    [data-testid="stSidebar"] {
        background-color: var(--navy-deep) !important;
        border-right: 1px solid var(--navy-medium) !important;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stText,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] .stCaption p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: rgba(255, 255, 255, 0.85) !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: 1px solid var(--gold-border) !important;
        color: var(--gold-primary) !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
        transition: all var(--transition) !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(201, 169, 110, 0.15) !important;
        border-color: var(--gold-primary) !important;
    }

    [data-testid="stSidebar"] .stDownloadButton > button {
        background-color: transparent !important;
        border: 1px solid var(--gold-border) !important;
        color: var(--gold-primary) !important;
    }

    [data-testid="stSidebar"] .stDownloadButton > button:hover {
        background-color: rgba(201, 169, 110, 0.15) !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--navy-medium) !important;
    }

    [data-testid="stSidebar"] .stFileUploader {
        border: 1px dashed var(--gold-border) !important;
        border-radius: var(--radius-md) !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
    [data-testid="stSidebar"] .stFileUploader section {
        background-color: rgba(255, 255, 255, 0.08) !important;
    }

    [data-testid="stSidebar"] .stFileUploader small,
    [data-testid="stSidebar"] .stFileUploader span,
    [data-testid="stSidebar"] .stFileUploader div,
    [data-testid="stSidebar"] .stFileUploader p,
    [data-testid="stSidebar"] .stFileUploader label,
    [data-testid="stSidebar"] .stFileUploader button {
        color: rgba(255, 255, 255, 0.85) !important;
    }

    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: rgba(201, 169, 110, 0.15) !important;
        border: 1px solid var(--gold-border) !important;
    }

    /* ========================================
       METRIC CARDS (KPIs)
       ======================================== */
    [data-testid="stMetric"] {
        background-color: var(--bg-white) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.25rem 1.5rem !important;
        box-shadow: var(--shadow-card) !important;
        transition: box-shadow var(--transition), border-color var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-card-hover) !important;
        border-color: var(--border-gold) !important;
    }

    /* Gold accent underline */
    [data-testid="stMetric"]::after {
        content: '' !important;
        position: absolute !important;
        bottom: 0 !important;
        left: 1.5rem !important;
        right: 1.5rem !important;
        height: 2px !important;
        background: linear-gradient(90deg, var(--gold-primary), var(--gold-light)) !important;
        border-radius: 1px !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-family: var(--font-body) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-heading) !important;
        font-family: var(--font-mono) !important;
        font-size: 1.5rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricDelta"] {
        font-family: var(--font-body) !important;
    }

    /* ========================================
       TABS — ELEGANT GOLD UNDERLINE
       ======================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        border-bottom: 1px solid var(--border-light) !important;
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-body) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        padding: 0.75rem 1.25rem !important;
        border-bottom: 2px solid transparent !important;
        background-color: transparent !important;
        transition: all var(--transition) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-heading) !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--navy-deep) !important;
        font-weight: 600 !important;
        border-bottom-color: var(--gold-primary) !important;
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--gold-primary) !important;
    }

    /* ========================================
       BUTTONS
       ======================================== */
    .stButton > button {
        background-color: var(--navy-button) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.25rem !important;
        transition: all var(--transition) !important;
        box-shadow: none !important;
        min-height: 42px !important;
    }

    .stButton > button:hover {
        background-color: var(--navy-medium) !important;
        box-shadow: var(--shadow-card) !important;
    }

    /* Secondary buttons — outlined style */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"] {
        background-color: transparent !important;
        color: var(--navy-button) !important;
        border: 1px solid var(--border-light) !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        border-color: var(--finance-negative) !important;
        color: var(--finance-negative) !important;
        background-color: var(--finance-negative-light) !important;
    }

    .stDownloadButton > button {
        background-color: transparent !important;
        color: var(--navy-deep) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
        min-height: 42px !important;
    }

    .stDownloadButton > button:hover {
        border-color: var(--gold-primary) !important;
        color: var(--gold-dark) !important;
    }

    /* ========================================
       INPUTS & SELECTS
       ======================================== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background-color: var(--bg-white) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-body) !important;
        font-family: var(--font-body) !important;
        padding: 0.625rem 0.875rem !important;
        min-height: 42px !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--gold-primary) !important;
        box-shadow: 0 0 0 3px var(--gold-subtle) !important;
    }

    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: var(--bg-white) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
    }

    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--gold-primary) !important;
        box-shadow: 0 0 0 3px var(--gold-subtle) !important;
    }

    /* ========================================
       DATAFRAMES & TABLES
       ======================================== */
    .stDataFrame {
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-card) !important;
        border: 1px solid var(--border-light) !important;
    }

    /* ========================================
       EXPANDERS
       ======================================== */
    .streamlit-expanderHeader {
        background-color: var(--bg-white) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
        color: var(--text-heading) !important;
        transition: all var(--transition) !important;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--border-gold) !important;
    }

    .streamlit-expanderContent {
        background-color: var(--bg-white) !important;
        border: 1px solid var(--border-light) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    }

    /* ========================================
       ALERTS
       ======================================== */
    .stAlert {
        border-radius: var(--radius-md) !important;
        border-left-width: 3px !important;
        font-family: var(--font-body) !important;
    }

    /* ========================================
       DIVIDERS
       ======================================== */
    hr {
        border-color: var(--border-light) !important;
        margin: 2rem 0 !important;
    }

    /* ========================================
       PLOTLY CHARTS
       ======================================== */
    .js-plotly-plot {
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
    }

    /* ========================================
       SCROLLBAR
       ======================================== */
    ::-webkit-scrollbar {
        width: 6px !important;
        height: 6px !important;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-warm) !important;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--gold-light) !important;
        border-radius: 3px !important;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--gold-primary) !important;
    }

    /* ========================================
       BADGE CLASSES
       ======================================== */
    .badge-positive {
        display: inline-block;
        background-color: var(--finance-positive-light);
        color: var(--finance-positive);
        padding: 0.2rem 0.6rem;
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 0.8rem;
        font-family: var(--font-body);
        border: 1px solid var(--finance-positive);
    }

    .badge-negative {
        display: inline-block;
        background-color: var(--finance-negative-light);
        color: var(--finance-negative);
        padding: 0.2rem 0.6rem;
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 0.8rem;
        font-family: var(--font-body);
        border: 1px solid var(--finance-negative);
    }

    .badge-neutral {
        display: inline-block;
        background-color: var(--bg-warm);
        color: var(--text-muted);
        padding: 0.2rem 0.6rem;
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 0.8rem;
        font-family: var(--font-body);
        border: 1px solid var(--border-light);
    }

    .badge-gold {
        display: inline-block;
        background-color: var(--gold-subtle);
        color: var(--gold-dark);
        padding: 0.2rem 0.6rem;
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 0.8rem;
        font-family: var(--font-body);
        border: 1px solid var(--gold-primary);
    }

    /* ========================================
       FINANCIAL VALUE CLASSES
       ======================================== */
    .valor-positivo {
        color: var(--finance-positive);
        font-weight: 600;
        font-family: var(--font-mono);
    }

    .valor-negativo {
        color: var(--finance-negative);
        font-weight: 600;
        font-family: var(--font-mono);
    }

    .valor-neutro {
        color: var(--text-muted);
        font-weight: 500;
        font-family: var(--font-mono);
    }

    /* ========================================
       CUSTOM KPI CARD
       ======================================== */
    .kpi-card {
        background: var(--bg-white);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-card);
        position: relative;
        overflow: hidden;
        transition: all var(--transition);
    }

    .kpi-card:hover {
        box-shadow: var(--shadow-card-hover);
        border-color: var(--border-gold);
    }

    .kpi-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 1.5rem;
        right: 1.5rem;
        height: 2px;
        background: linear-gradient(90deg, var(--gold-primary), var(--gold-light));
    }

    .kpi-card .kpi-label {
        font-family: var(--font-body);
        color: var(--text-muted);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 0.5rem 0;
        font-weight: 500;
    }

    .kpi-card .kpi-value {
        font-family: var(--font-mono);
        font-size: 1.75rem;
        font-weight: 500;
        margin: 0;
        line-height: 1.2;
    }

    .kpi-card .kpi-subtitle {
        font-family: var(--font-body);
        color: var(--text-caption);
        font-size: 0.75rem;
        margin: 0.25rem 0 0 0;
    }
    </style>
    """, unsafe_allow_html=True)


def formatar_valor_financeiro(valor: float, incluir_sinal: bool = True) -> str:
    """
    Formata um valor financeiro com cor apropriada (emerald para positivo, red para negativo).
    Usa DM Mono para a fonte dos valores.
    """
    valor_abs = abs(valor)
    valor_fmt = f"{valor_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
    Tipos: "positive", "negative", "neutral", "gold"
    """
    classe = f"badge-{tipo}"
    return f"<span class='{classe}'>{texto}</span>"


def get_plotly_layout_theme():
    """Returns a Plotly layout dict for consistent chart theming across the dashboard."""
    return dict(
        font=dict(family="DM Sans, sans-serif", color="#374151"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        title_font=dict(family="Playfair Display, serif", size=16, color="#0A1628"),
        xaxis=dict(
            gridcolor="rgba(229,231,235,0.5)",
            linecolor="#E5E7EB",
            tickfont=dict(family="DM Sans, sans-serif", size=11, color="#6B7280"),
            title_font=dict(family="DM Sans, sans-serif", size=12, color="#374151"),
        ),
        yaxis=dict(
            gridcolor="rgba(229,231,235,0.5)",
            linecolor="#E5E7EB",
            tickfont=dict(family="DM Mono, monospace", size=11, color="#6B7280"),
            title_font=dict(family="DM Sans, sans-serif", size=12, color="#374151"),
        ),
        legend=dict(
            font=dict(family="DM Sans, sans-serif", size=11),
            bgcolor="rgba(255,255,255,0)",
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(
            bgcolor="#0A1628",
            font_size=12,
            font_family="DM Sans, sans-serif",
            font_color="#FFFFFF",
            bordercolor="#C9A96E",
        ),
    )


def criar_kpi_card(label: str, valor: str, subtexto: str = "", cor_valor: str = "#0A1628") -> str:
    """
    Creates a luxury HTML KPI card.
    cor_valor: hex color for the value text (e.g. #10B981 for positive, #EF4444 for negative)
    """
    subtexto_html = f"<p class='kpi-subtitle'>{subtexto}</p>" if subtexto else ""
    return f"""
    <div class='kpi-card'>
        <p class='kpi-label'>{label}</p>
        <p class='kpi-value' style='color: {cor_valor};'>{valor}</p>
        {subtexto_html}
    </div>
    """
