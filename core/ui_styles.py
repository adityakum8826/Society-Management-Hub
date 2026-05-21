import streamlit as st
import config

THEME = config.THEME

def apply_global_styles():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Fix text overflow in all dropdowns and selections */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [data-baseweb="select"] {{
        overflow: visible !important;
    }}
    
    [data-baseweb="menu"] ul,
    [data-baseweb="popover"] ul {{
        overflow: visible !important;
        max-height: none !important;
    }}
    
    [data-baseweb="menu"] li,
    [data-baseweb="popover"] li {{
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }}
    
    .stApp {{
        background: {THEME['background']};
        color: {THEME['text_primary']};
    }}
    
    .main {{
        background: linear-gradient(180deg, {THEME['background']} 0%, #0a0f1a 50%, #0f172a 100%);
        min-height: 100vh;
    }}
    
    [data-testid="stMain"] {{
        margin-left: 0 !important;
        padding-top: 0 !important;
    }}
    
    [data-testid="stMainBlockContainer"] {{
        max-width: 100% !important;
        padding: 1rem 2rem 2rem 2rem !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {THEME['text_primary']} !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    
    h1 {{ font-size: 2rem; margin-bottom: 1rem; }}
    h2 {{ font-size: 1.5rem; margin-bottom: 0.75rem; }}
    h3 {{ font-size: 1.25rem; margin-bottom: 0.5rem; }}
    
    .gradient-text {{
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Premium Metric Cards */
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(30, 41, 59, 0.6));
        border: 1px solid {THEME['border_color']};
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.4);
    }}
    
    div[data-testid="stMetricLabel"] {{
        color: {THEME['text_secondary']} !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }}
    
    div[data-testid="stMetricValue"] {{
        color: {THEME['text_primary']} !important;
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #fff 0%, #a0aec0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    /* Premium Buttons with Glow */
    .stButton > button {{
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 50%, #4338CA 100%);
        border: none;
        border-radius: 14px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: 14px;
        color: white;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4), inset 0 1px 0 rgba(255,255,255,0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }}
    
    .stButton > button:hover::before {{
        left: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.6);
    }}
    
    .stButton > button:active {{
        transform: translateY(0) scale(0.98);
    }}
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {{
        background: linear-gradient(145deg, #334155, #1e293b);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    }}
    
    /* Form Inputs with Glow */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(15, 23, 42, 0.8));
        border: 1px solid {THEME['border_color']};
        border-radius: 14px;
        color: {THEME['text_primary']};
        padding: 14px 18px;
        font-size: 14px;
        transition: all 0.3s ease;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {THEME['accent_primary']};
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15), 0 0 20px rgba(99, 102, 241, 0.1);
        background: rgba(99, 102, 241, 0.05);
    }}
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        min-height: 48px;
        line-height: 1.5;
    }}
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: {THEME['text_secondary']};
        opacity: 0.6;
    }}
    
    /* Premium DataFrames */
    div[data-testid="stDataFrame"] {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(30, 41, 59, 0.6));
        border: 1px solid {THEME['border_color']};
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }}
    
    /* Expanders with Glass Effect */
    div[data-testid="stExpander"] {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(30, 41, 59, 0.6));
        border: 1px solid {THEME['border_color']};
        border-radius: 16px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }}
    
    div[data-testid="stExpander"]:hover {{
        border-color: rgba(99, 102, 241, 0.3);
    }}
    
    div[data-testid="stExpander"] details {{
        border-radius: 16px;
    }}
    
    /* Premium Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(30, 41, 59, 0.4));
        padding: 8px;
        border-radius: 16px;
        border: 1px solid {THEME['border_color']};
        backdrop-filter: blur(10px);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 12px;
        padding: 14px 24px;
        color: {THEME['text_secondary']};
        font-weight: 500;
        font-size: 13px;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(99, 102, 241, 0.1);
        color: {THEME['text_primary']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {THEME['accent_primary']}, #4F46E5);
        color: white;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }}
    
    /* Radio & Checkbox - Fixed for text cut-off */
    .stRadio > div {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(30, 41, 59, 0.6));
        border-radius: 14px;
        padding: 14px;
        border: 1px solid {THEME['border_color']};
    }}
    
    .stRadio > div > label {{
        color: {THEME['text_primary']};
        font-size: 14px;
        line-height: 1.6;
        padding: 8px 12px;
        border-radius: 8px;
        display: flex;
        align-items: center;
    }}
    
    .stRadio > div > label:hover {{
        background: rgba(99, 102, 241, 0.1);
    }}
    
    .stCheckbox > label {{
        color: {THEME['text_primary']};
        font-size: 14px;
        line-height: 1.6;
        padding: 8px 12px;
        border-radius: 8px;
        display: flex;
        align-items: center;
    }}
    
    .stCheckbox > label:hover {{
        background: rgba(99, 102, 241, 0.1);
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {THEME['background']};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {THEME['accent_primary']}, {THEME['accent_secondary']});
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, #818CF8, #22D3EE);
    }}
    
    /* Premium Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-8px); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.8; transform: scale(0.98); }}
    }}
    
    @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }}
        50% {{ box-shadow: 0 0 40px rgba(99, 102, 241, 0.6); }}
    }}
    
    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}
    
    .animate-fadeIn {{
        animation: fadeIn 0.5s ease-out;
    }}
    
    .animate-slideUp {{
        animation: slideUp 0.6s ease-out;
    }}
    
    .animate-float {{
        animation: float 3s ease-in-out infinite;
    }}
    
    .animate-pulse {{
        animation: pulse 2s ease-in-out infinite;
    }}
    
    .animate-glow {{
        animation: glow 4s ease-in-out infinite;
    }}
    
    /* Block Container Spacing */
    div[data-testid="stVerticalBlock"] {{
        gap: 1.2rem;
    }}
    
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}
    
    /* Selectbox Dropdown - Fixed for text cut-off */
    .stSelectbox [data-baseweb="select"] > div {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(15, 23, 42, 0.8));
        border: 1px solid {THEME['border_color']};
        border-radius: 14px;
        padding: 12px 16px;
        min-height: 48px;
    }}
    
    .stSelectbox [data-baseweb="select"] > div > div {{
        color: {THEME['text_primary']};
        -webkit-text-fill-color: {THEME['text_primary']};
        font-size: 14px;
        line-height: 1.5;
    }}

    /* FIX: selected value text invisible on dark theme 
       Must override both color AND -webkit-text-fill-color */
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div,
    .stSelectbox [data-baseweb="select"] p,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] > div > div span {{
        color: {THEME['text_primary']} !important;
        -webkit-text-fill-color: {THEME['text_primary']} !important;
        opacity: 1 !important;
    }}
    
    .stSelectbox [data-baseweb="popover"] {{
        background: {THEME['card_background']};
        border: 1px solid {THEME['border_color']};
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        z-index: 9999;
    }}
    
    .stSelectbox [data-baseweb="popover"] ul {{
        max-height: 300px;
        overflow-y: auto;
        padding: 8px;
    }}
    
    .stSelectbox [data-baseweb="popover"] li {{
        padding: 12px 16px;
        border-radius: 8px;
        margin: 2px 0;
        color: {THEME['text_primary']};
        font-size: 14px;
        white-space: normal;
        word-wrap: break-word;
    }}
    
    .stSelectbox [data-baseweb="popover"] li:hover {{
        background: rgba(99, 102, 241, 0.15);
    }}
    
    .stSelectbox [data-baseweb="popover"] li[aria-selected="true"] {{
        background: {THEME['accent_primary']};
    }}

    /* Selected value + placeholder: avoid invisible text (gradient clip / fill on nested nodes) */
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div {{
        color: {THEME['text_primary']} !important;
    }}
    .stSelectbox [data-baseweb="select"] input,
    .stSelectbox [data-baseweb="select"] p,
    .stSelectbox [data-baseweb="select"] span {{
        color: {THEME['text_primary']} !important;
        -webkit-text-fill-color: {THEME['text_primary']} !important;
        background-image: none !important;
        -webkit-background-clip: border-box !important;
        background-clip: border-box !important;
        opacity: 1 !important;
    }}
    .stSelectbox label, .stSelectbox [data-testid="stWidgetLabel"] p {{
        color: {THEME['text_secondary']} !important;
    }}

    /* Base Web combobox: selected value is often in a readonly/filter input — keep it visible */
    [data-baseweb="select"] input[role="combobox"],
    [data-baseweb="select"] input[readonly],
    .stSelectbox [data-baseweb="select"] input {{
        color: {THEME['text_primary']} !important;
        -webkit-text-fill-color: {THEME['text_primary']} !important;
        caret-color: {THEME['text_primary']} !important;
        opacity: 1 !important;
        -webkit-opacity: 1 !important;
    }}
    [data-baseweb="select"] input::placeholder {{
        color: {THEME['text_secondary']} !important;
        -webkit-text-fill-color: {THEME['text_secondary']} !important;
        opacity: 0.85 !important;
    }}
    /* Value text node (some Streamlit versions) */
    [data-baseweb="select"] [class*="SingleValue"],
    [data-baseweb="select"] [class*="singleValue"],
    [data-baseweb="select"] [class*="ValueContainer"] {{
        color: {THEME['text_primary']} !important;
        -webkit-text-fill-color: {THEME['text_primary']} !important;
    }}
    
    /* Multiselect Dropdown - Fixed for text cut-off */
    .stMultiSelect [data-baseweb="select"] > div {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(15, 23, 42, 0.8));
        border: 1px solid {THEME['border_color']};
        border-radius: 14px;
        padding: 10px 14px;
        min-height: 48px;
    }}
    
    .stMultiSelect [data-baseweb="popover"] {{
        background: {THEME['card_background']};
        border: 1px solid {THEME['border_color']};
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        z-index: 9999;
    }}
    
    .stMultiSelect [data-baseweb="popover"] ul {{
        max-height: 300px;
        overflow-y: auto;
        padding: 8px;
    }}
    
    .stMultiSelect [data-baseweb="popover"] li {{
        padding: 12px 16px;
        border-radius: 8px;
        margin: 2px 0;
        color: {THEME['text_primary']};
        font-size: 14px;
        white-space: normal;
        word-wrap: break-word;
    }}
    
    /* Number Input */
    .stNumberInput > div > div > button {{
        background: linear-gradient(135deg, #6366F1, #4F46E5);
        border-radius: 8px;
    }}
    
    /* Date Input */
    .stDateInput > div > div > div {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(15, 23, 42, 0.8));
        border: 1px solid {THEME['border_color']};
        border-radius: 14px;
    }}
    
    /* Time Input */
    .stTimeInput > div > div > div {{
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(15, 23, 42, 0.8));
        border: 1px solid {THEME['border_color']};
        border-radius: 14px;
    }}
    
    /* Progress Bar */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {THEME['accent_primary']}, {THEME['accent_secondary']});
        border-radius: 10px;
    }}
    
    /* Slider */
    .stSlider > div > div > div {{
        background: linear-gradient(90deg, {THEME['accent_primary']}, {THEME['accent_secondary']});
    }}
    
    /* Spinner */
    .stSpinner > div {{
        border-color: {THEME['accent_primary']} !important;
    }}
    
    /* Toast/Success/Error Messages */
    .stAlert {{
        border-radius: 14px;
        backdrop-filter: blur(10px);
    }}
    
    /* Divider */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, {THEME['border_color']}, transparent);
        margin: 24px 0;
    }}
    
    /* Code Block */
    code {{
        background: rgba(99, 102, 241, 0.1);
        padding: 2px 8px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
    }}
    
    /* Tooltip */
    .stTooltip {{
        background: {THEME['card_background']};
        border: 1px solid {THEME['border_color']};
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_login_page_styles():
    return f"""
    <style>
    .login-container {{
        max-width: 480px;
        margin: 60px auto;
        padding: 48px;
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(30, 41, 59, 0.7));
        border-radius: 24px;
        border: 1px solid {THEME['border_color']};
        backdrop-filter: blur(20px);
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5), 0 0 60px rgba(99, 102, 241, 0.1);
    }}
    
    .login-header {{
        text-align: center;
        margin-bottom: 40px;
    }}
    
    .login-logo {{
        font-size: 72px;
        animation: float 3s ease-in-out infinite;
        display: inline-block;
        margin-bottom: 24px;
        filter: drop-shadow(0 10px 30px rgba(99, 102, 241, 0.3));
    }}
    
    .login-title {{
        font-size: 32px;
        font-weight: 800;
        margin: 20px 0;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }}
    
    .login-badges {{
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 20px;
    }}
    
    .login-badge {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
        border: 1px solid rgba(99, 102, 241, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        color: {THEME['text_secondary']};
        font-weight: 500;
    }}
    
    .tab-container {{
        background: rgba(0, 0, 0, 0.2);
        border-radius: 16px;
        padding: 6px;
        margin-bottom: 32px;
        border: 1px solid {THEME['border_color']};
    }}
    
    .form-group {{
        margin-bottom: 20px;
    }}
    
    .form-label {{
        display: block;
        margin-bottom: 8px;
        color: {THEME['text_secondary']};
        font-size: 13px;
        font-weight: 500;
    }}
    
    .login-btn {{
        width: 100%;
        padding: 16px;
        font-size: 16px;
        margin-top: 24px;
        background: linear-gradient(135deg, #6366F1, #4F46E5);
        border-radius: 14px;
        font-weight: 600;
    }}
    
    .remember-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 24px 0;
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-10px); }}
    }}
    </style>
    """

def hide_default_elements():
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_premium_header(title, subtitle=None, user=None):
    subtitle_html = f'<p style="margin: 0; color: {THEME["text_secondary"]}; font-size: 14px;">{subtitle}</p>' if subtitle else ''
    return f"""
    <div style="
        padding: 24px 0;
        margin-bottom: 32px;
        border-bottom: 1px solid {THEME['border_color']};
    ">
        <h1 style="margin: 0 0 8px 0; font-size: 28px; font-weight: 700; color: {THEME['text_primary']};">
            {title}
        </h1>
        {subtitle_html}
    </div>
    """

def format_metric_card(label, value, delta=None, icon=None):
    return f"""
    <div style="
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(30, 41, 59, 0.6));
        border: 1px solid {THEME['border_color']};
        border-radius: 20px;
        padding: 28px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    ">
        <div style="color: {THEME['text_secondary']}; font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-bottom: 12px;">
            {icon or ''} {label}
        </div>
        <div style="font-size: 36px; font-weight: 700; color: {THEME['text_primary']}; margin-bottom: 8px;">
            {value}
        </div>
        {f'<div style="color: #10B981; font-size: 14px; font-weight: 500;">{delta}</div>' if delta else ''}
    </div>
    """

def get_glass_card(content):
    return f"""
    <div style="
        background: linear-gradient(145deg, {THEME['card_background']}, rgba(30, 41, 59, 0.5));
        border: 1px solid {THEME['border_color']};
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    ">
        {content}
    </div>
    """

def get_gradient_button(text, color="primary"):
    colors = {
        "primary": "linear-gradient(135deg, #6366F1, #4F46E5)",
        "success": "linear-gradient(135deg, #10B981, #059669)",
        "warning": "linear-gradient(135deg, #F59E0B, #D97706)",
        "danger": "linear-gradient(135deg, #EF4444, #DC2626)",
    }
    bg = colors.get(color, colors["primary"])
    return f"""
    <button style="
        background: {bg};
        border: none;
        border-radius: 14px;
        padding: 14px 28px;
        color: white;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 30px rgba(0,0,0,0.4)'" 
    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 20px rgba(0,0,0,0.3)'">
        {text}
    </button>
    """

def get_premium_card(title, content, icon=None, gradient=None):
    gradient_bg = gradient or "linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(6, 182, 212, 0.1))"
    return f"""
    <div style="
        background: {gradient_bg};
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    ">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <span style="font-size: 28px;">{icon or '📊'}</span>
            <h3 style="margin: 0; color: {THEME['text_primary']}; font-size: 18px;">{title}</h3>
        </div>
        <div style="color: {THEME['text_secondary']}; font-size: 14px; line-height: 1.6;">
            {content}
        </div>
    </div>
    """

def get_animated_icon(emoji, animation="float"):
    animations = {
        "float": "animation: float 3s ease-in-out infinite;",
        "pulse": "animation: pulse 2s ease-in-out infinite;",
        "glow": "animation: glow 2s ease-in-out infinite;",
    }
    anim = animations.get(animation, "")
    return f"""
    <span style="font-size: 32px; display: inline-block; {anim} filter: drop-shadow(0 4px 8px rgba(99, 102, 241, 0.3));">
        {emoji}
    </span>
    """

def get_premium_table_header(cells):
    cell_html = "".join([f"<th style='padding: 16px; text-align: left; color: {THEME['text_secondary']}; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid {THEME['border_color']};'>{cell}</th>" for cell in cells])
    return f"""
    <table style='width: 100%; border-collapse: collapse;'>
        <thead>
            <tr>{cell_html}</tr>
        </thead>
        <tbody>
    """

def get_premium_table_row(cells, row_type="normal"):
    colors = {
        "normal": THEME['text_primary'],
        "muted": THEME['text_secondary'],
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
    }
    color = colors.get(row_type, THEME['text_primary'])
    cell_html = "".join([f"<td style='padding: 14px 16px; color: {color}; border-bottom: 1px solid {THEME['border_color']};'>{cell}</td>" for cell in cells])
    return f"<tr>{cell_html}</tr>"

def get_premium_table_footer():
    return "</tbody></table>"