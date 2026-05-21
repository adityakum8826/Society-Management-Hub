import streamlit as st
import config
from core.helpers import get_initials, get_priority_color, get_status_color, get_role_badge_color

def metric_card(label, value, delta=None, icon="📊", color=None):
    st.markdown(f"""
    <div style="
        background: {config.THEME['card_background']};
        border: 1px solid {config.THEME['border_color']};
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
    ">
        <div style="color: {config.THEME['text_secondary']}; font-size: 14px; margin-bottom: 8px;">
            {icon} {label}
        </div>
        <div style="color: {color or config.THEME['text_primary']}; font-size: 28px; font-weight: 700;">
            {value}
        </div>
        {f'<div style="color: #10B981; font-size: 14px; margin-top: 8px;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def stat_card(title, value, subtitle=None, icon="📊", bg_color=None):
    bg = bg_color or f"linear-gradient(135deg, {config.THEME['accent_primary']}20, {config.THEME['accent_secondary']}20)"
    st.markdown(f"""
    <div style="
        background: {config.THEME['card_background']};
        border: 1px solid {config.THEME['border_color']};
        border-radius: 16px;
        padding: 20px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -20px;
            right: -20px;
            font-size: 60px;
            opacity: 0.1;
        ">{icon}</div>
        <div style="color: {config.THEME['text_secondary']}; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">
            {title}
        </div>
        <div style="font-size: 32px; font-weight: 700; color: {config.THEME['text_primary']}; margin: 8px 0;">
            {value}
        </div>
        {f"<div style='font-size: 12px; color: {config.THEME['text_secondary']};'>{subtitle}</div>" if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def status_badge(status, size="medium"):
    color = get_status_color(status)
    size_map = {"small": "10px", "medium": "12px", "large": "14px"}
    font_size = size_map.get(size, "12px")
    st.markdown(f"""
    <span style="
        background: {color}20;
        color: {color};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: {font_size};
        font-weight: 500;
        display: inline-block;
    ">
        {status}
    </span>
    """, unsafe_allow_html=True)

def priority_indicator(priority):
    color = get_priority_color(priority)
    st.markdown(f"""
    <span style="
        background: {color}20;
        color: {color};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    ">
        {priority}
    </span>
    """, unsafe_allow_html=True)

def info_card(title, content):
    st.markdown(f"""
    <div style="
        background: {config.THEME['card_background']};
        border-left: 4px solid {config.THEME['accent_primary']};
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
    ">
        <div style="font-weight: 600; color: {config.THEME['text_primary']}; margin-bottom: 8px;">
            {title}
        </div>
        <div style="color: {config.THEME['text_secondary']}; font-size: 14px;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def warning_card(title, content):
    st.markdown(f"""
    <div style="
        background: {config.THEME['card_background']};
        border-left: 4px solid {config.THEME['warning']};
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
    ">
        <div style="font-weight: 600; color: {config.THEME['warning']}; margin-bottom: 8px;">
            ⚠️ {title}
        </div>
        <div style="color: {config.THEME['text_secondary']}; font-size: 14px;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def success_card(title, content):
    st.markdown(f"""
    <div style="
        background: {config.THEME['card_background']};
        border-left: 4px solid {config.THEME['success']};
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
    ">
        <div style="font-weight: 600; color: {config.THEME['success']}; margin-bottom: 8px;">
            ✅ {title}
        </div>
        <div style="color: {config.THEME['text_secondary']}; font-size: 14px;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def error_card(title, content):
    st.markdown(f"""
    <div style="
        background: {config.THEME['card_background']};
        border-left: 4px solid {config.THEME['danger']};
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
    ">
        <div style="font-weight: 600; color: {config.THEME['danger']}; margin-bottom: 8px;">
            ❌ {title}
        </div>
        <div style="color: {config.THEME['text_secondary']}; font-size: 14px;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def user_avatar(name, size="medium"):
    initials = get_initials(name)
    size_map = {"small": "30px", "medium": "50px", "large": "70px"}
    font_size = size_map.get(size, "50px")
    st.markdown(f"""
    <div style="
        width: {font_size};
        height: {font_size};
        border-radius: 50%;
        background: linear-gradient(135deg, {config.THEME['accent_primary']}, {config.THEME['accent_secondary']});
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: white;
        font-size: {int(int(font_size.replace('px','')) * 0.35)}px;
    ">
        {initials}
    </div>
    """, unsafe_allow_html=True)

def section_header(title, icon=None):
    st.markdown(f"""
    <div style="
        border-bottom: 1px solid {config.THEME['border_color']};
        padding-bottom: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    ">
        <span style="font-size: 20px;">{icon or '📋'}</span>
        <h3 style="margin: 0; color: {config.THEME['text_primary']};">{title}</h3>
    </div>
    """, unsafe_allow_html=True)

def role_badge(role):
    color = get_role_badge_color(role)
    st.markdown(f"""
    <span style="
        background: {color}20;
        color: {color};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    ">
        {role}
    </span>
    """, unsafe_allow_html=True)

def action_button(label, icon=None, key=None, type="primary"):
    colors = {
        "primary": "linear-gradient(135deg, #3b82f6, #2563eb, #1d4ed8)",
        "secondary": "linear-gradient(145deg, #475569, #334155)",
        "danger": "linear-gradient(135deg, #ef4444, #dc2626, #b91c1c)",
        "success": "linear-gradient(135deg, #10b981, #059669, #047857)"
    }
    color = colors.get(type, colors["primary"])
    
    st.markdown(f"""
    <button style="
        background: {color};
        border: none;
        border-radius: 50px;
        padding: 10px 24px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    ">
        {icon or ''} {label}
    </button>
    """, unsafe_allow_html=True)

def empty_state(title, description, icon="📭"):
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 60px 20px;
        color: {config.THEME['text_secondary']};
    ">
        <div style="font-size: 60px; margin-bottom: 20px; opacity: 0.5;">{icon}</div>
        <h3 style="color: {config.THEME['text_primary']}; margin-bottom: 10px;">{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def premium_card(title, value, subtitle=None, icon="💎", gradient=None):
    gradient_bg = gradient or f"linear-gradient(135deg, {config.THEME['accent_primary']}20, {config.THEME['accent_secondary']}10)"
    st.markdown(f"""
    <div style="
        background: {gradient_bg};
        border: 1px solid {config.THEME['border_color']};
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -10px;
            right: -10px;
            font-size: 50px;
            opacity: 0.1;
        ">{icon}</div>
        <div style="color: {config.THEME['text_secondary']}; font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-bottom: 8px;">
            {icon} {title}
        </div>
        <div style="font-size: 32px; font-weight: 700; color: {config.THEME['text_primary']}; margin-bottom: 4px;">
            {value}
        </div>
        {f"<div style='font-size: 13px; color: {config.THEME['text_secondary']};'>{subtitle}</div>" if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def glass_panel(content, icon=None):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {config.THEME['card_background']}, rgba(30, 41, 59, 0.5));
        border: 1px solid {config.THEME['border_color']};
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    ">
        {f'<div style="font-size: 24px; margin-bottom: 12px;">{icon}</div>' if icon else ''}
        {content}
    </div>
    """, unsafe_allow_html=True)
