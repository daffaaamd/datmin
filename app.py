"""
🗺️ Dashboard Wisata Indonesia - Modern UI/UX Redesign
A beautiful, modern tourism dashboard with enhanced user experience
"""

import os
import html
from urllib.parse import quote

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import hashlib
import urllib.request
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Import recommender system
from recommender import get_similar_places

# =========================
# 0. PAGE CONFIGURATION
# =========================
st.set_page_config(
    page_title="🗺️ Wisata Indonesia",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# 1. MODERN CSS DESIGN SYSTEM
# =========================
def inject_custom_css():
    """Inject modern CSS design system with DARK THEME"""
    st.markdown("""
    <style>
    /* ===== ROOT VARIABLES - DARK THEME DESIGN TOKENS ===== */
    :root {
        --primary-50: #1e1b4b;
        --primary-100: #312e81;
        --primary-200: #4338ca;
        --primary-300: #6366f1;
        --primary-400: #818cf8;
        --primary-500: #a5b4fc;
        --primary-600: #c7d2fe;
        --primary-700: #e0e7ff;
        
        --success-500: #10b981;
        --success-600: #34d399;
        --warning-500: #f59e0b;
        --warning-600: #fbbf24;
        --error-500: #ef4444;
        
        --bg-primary: #0f0f23;
        --bg-secondary: #1a1a2e;
        --bg-card: #16213e;
        --bg-card-hover: #1f2937;
        --bg-input: #1e293b;
        
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        
        --border-color: #334155;
        --border-light: #475569;
        
        --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --gradient-warm: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-ocean: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient-sunset: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --gradient-dark: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.3);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.3);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.5), 0 8px 10px -6px rgb(0 0 0 / 0.4);
        --shadow-glow: 0 0 20px rgba(102, 126, 234, 0.3);
        
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --radius-2xl: 1.5rem;
    }
    
    /* ===== GLOBAL DARK STYLES ===== */
    .stApp {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 50%, #0f0f23 100%) !important;
    }
    
    .stApp > header {
        background: transparent !important;
    }
    
    .main .block-container {
        background: transparent !important;
    }
    
    /* ===== HEADER STYLING ===== */
    .main-header {
        background: var(--gradient-primary);
        padding: 2rem 2.5rem;
        border-radius: var(--radius-2xl);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-xl), var(--shadow-glow);
        color: white;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* ===== METRIC CARDS - DARK ===== */
    .metric-card {
        background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%);
        padding: 1.5rem;
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl), var(--shadow-glow);
        border-color: var(--primary-300);
    }
    
    .metric-card .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    .metric-card .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
        font-weight: 500;
    }
    
    .metric-card .metric-change {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: var(--radius-sm);
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .metric-card .metric-change.positive {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
    }
    
    .metric-card .metric-change.negative {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
    }
    
    /* ===== PLACE CARDS - DARK ===== */
    .place-card {
        background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%);
        border-radius: var(--radius-xl);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        border: 1px solid var(--border-color);
        height: 100%;
    }
    
    .place-card:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-xl), var(--shadow-glow);
        border-color: var(--primary-300);
    }
    
    .place-card-content {
        padding: 1.25rem;
    }
    
    .place-card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }
    
    .place-card-location {
        font-size: 0.875rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 0.25rem;
        margin-bottom: 0.75rem;
    }
    
    .place-card-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border-color);
    }
    
    .place-card-rating {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-weight: 600;
        color: var(--warning-500);
    }
    
    .place-card-price {
        font-weight: 600;
        color: var(--success-600);
        font-size: 0.9rem;
    }
    
    .place-card-category {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        border-radius: var(--radius-md);
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    /* ===== SECTION HEADERS - DARK ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .section-header h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    
    .section-header .section-icon {
        width: 40px;
        height: 40px;
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #e2e8f0;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stTextInput label {
        color: #e2e8f0 !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1);
    }
    
    /* ===== FILTER BADGES - DARK ===== */
    .filter-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: var(--radius-2xl);
        font-size: 0.875rem;
        color: #a5b4fc;
        margin: 0.25rem;
        font-weight: 500;
    }
    
    .filter-badge .remove-btn {
        cursor: pointer;
        opacity: 0.7;
        transition: opacity 0.2s;
    }
    
    .filter-badge .remove-btn:hover {
        opacity: 1;
    }
    
    /* ===== CHART CONTAINERS - DARK ===== */
    .chart-container {
        background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%);
        padding: 1.5rem;
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* ===== RECOMMENDATION CARDS - DARK ===== */
    .recommendation-card {
        background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%);
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border: 1px solid var(--border-color);
    }
    
    .recommendation-card:hover {
        box-shadow: var(--shadow-lg), var(--shadow-glow);
        transform: translateX(4px);
    }
    
    .recommendation-rank {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: var(--gradient-primary);
        color: white;
        border-radius: 50%;
        font-weight: 700;
        font-size: 0.875rem;
        margin-right: 1rem;
    }
    
    .similarity-bar {
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: var(--radius-sm);
        overflow: hidden;
        margin-top: 0.75rem;
    }
    
    .similarity-bar-fill {
        height: 100%;
        background: var(--gradient-success);
        border-radius: var(--radius-sm);
        transition: width 0.5s ease;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-lg);
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* ===== DATA TABLES - DARK ===== */
    .stDataFrame {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    .stDataFrame > div {
        background: var(--bg-card) !important;
    }
    
    /* ===== EXPANDERS - DARK ===== */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: var(--radius-lg);
        font-weight: 600;
        color: var(--text-primary) !important;
    }
    
    /* ===== TABS - DARK ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--bg-card);
        padding: 0.5rem;
        border-radius: var(--radius-xl);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-lg);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: var(--text-secondary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bg-secondary);
        box-shadow: var(--shadow-sm);
        color: var(--text-primary);
    }
    
    /* ===== EMPTY STATES - DARK ===== */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        border: 2px dashed var(--border-color);
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .empty-state-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .empty-state-description {
        color: var(--text-secondary);
        font-size: 0.95rem;
    }
    
    /* ===== LOADING STATES - DARK ===== */
    .loading-skeleton {
        background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-secondary) 50%, var(--bg-card) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: var(--radius-md);
    }
    
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* ===== TOOLTIPS ===== */
    .tooltip {
        position: relative;
        cursor: help;
    }
    
    .tooltip::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 0.5rem 0.75rem;
        background: var(--bg-card);
        color: var(--text-primary);
        font-size: 0.75rem;
        border-radius: var(--radius-md);
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        border: 1px solid var(--border-color);
    }
    
    .tooltip:hover::after {
        opacity: 1;
        visibility: visible;
    }
    
    /* ===== STREAMLIT ELEMENTS - DARK OVERRIDE ===== */
    .stMarkdown, .stText {
        color: var(--text-primary) !important;
    }
    
    .stMetric label {
        color: var(--text-secondary) !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-input) !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
    }
    
    .stTextInput > div > div > input {
        background: var(--bg-input) !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
    }
    
    /* Success/Info/Warning messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        background: var(--bg-card) !important;
        border-radius: var(--radius-lg);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        color: var(--text-primary) !important;
    }
    
    /* ===== RESPONSIVE ADJUSTMENTS ===== */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem;
        }
        
        .main-header h1 {
            font-size: 1.75rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .metric-card .metric-value {
            font-size: 1.5rem;
        }
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    /* ===== SCROLLBAR STYLING - DARK ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-light);
    }
    
    /* ===== ADDITIONAL DARK THEME OVERRIDES ===== */
    /* Main content area */
    section[data-testid="stSidebar"] + section {
        background: transparent !important;
    }
    
    /* All text elements */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
    }
    
    /* Links */
    a {
        color: #818cf8 !important;
    }
    
    a:hover {
        color: #a5b4fc !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: transparent !important;
    }
    
    .stRadio label {
        color: var(--text-primary) !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: var(--text-primary) !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: var(--gradient-success) !important;
        color: white !important;
    }
    
    /* Metric delta */
    [data-testid="stMetricDelta"] {
        color: var(--success-500) !important;
    }
    
    /* DataFrame styling */
    .stDataFrame [data-testid="StyledDataFrameDataCell"],
    .stDataFrame [data-testid="StyledDataFrameHeaderCell"] {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    /* Altair chart background */
    .vega-embed {
        background: transparent !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--primary-400) transparent transparent transparent !important;
    }
    
    /* Container with border - Dark Theme */
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stVerticalBlockBorderWrapper"]) {
        background: transparent !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%) !important;
        border: 1px solid #334155 !important;
        border-radius: 0.75rem !important;
        padding: 1rem !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Inject CSS
inject_custom_css()

# =========================
# 2. HELPER FUNCTIONS
# =========================
def render_header():
    """Render modern header with gradient background"""
    st.markdown("""
    <div class="main-header">
        <h1>🗺️ Dashboard Wisata Indonesia</h1>
        <p>Temukan destinasi wisata terbaik di seluruh Indonesia dengan analisis data interaktif</p>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(icon, value, label, color="primary", change=None):
    """Render a beautiful metric card"""
    gradient_colors = {
        "primary": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "success": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "warning": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "info": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    }
    
    change_html = ""
    if change:
        change_class = "positive" if change > 0 else "negative"
        change_symbol = "↑" if change > 0 else "↓"
        change_html = f'<span class="metric-change {change_class}">{change_symbol} {abs(change)}%</span>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-icon" style="background: {gradient_colors.get(color, gradient_colors['primary'])};">
            {icon}
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {change_html}
    </div>
    """

def render_place_card(place, city, category, rating, fee, link=None):
    """Render a beautiful place card with dark theme"""
    rating_stars = "⭐" * int(rating) if pd.notna(rating) else ""
    fee_display = f"Rp {fee:,.0f}" if pd.notna(fee) else "Gratis"
    
    # Create Google Maps search link (not embed)
    link_html = ""
    if link:
        # Convert embed URL to search URL if needed
        if "output=embed" in str(link):
            # Extract query and create search URL
            search_link = link.replace("&output=embed", "").replace("https://www.google.com/maps?q=", "https://www.google.com/maps/search/?api=1&query=")
        else:
            search_link = link
        link_html = f'<a href="{search_link}" target="_blank" style="color: #818cf8; text-decoration: none; font-size: 0.875rem; display: inline-block; margin-top: 0.75rem; padding: 0.5rem 1rem; background: rgba(99, 102, 241, 0.2); border-radius: 0.5rem;">🌐 Lihat di Maps</a>'
    
    return f"""
    <div class="place-card">
        <div class="place-card-content">
            <span class="place-card-category">{category}</span>
            <div class="place-card-title">{place}</div>
            <div class="place-card-location">📍 {city}</div>
            <div class="place-card-meta">
                <span class="place-card-rating">⭐ {f'{rating:.1f}' if pd.notna(rating) else 'N/A'}</span>
                <span class="place-card-price">{fee_display}</span>
            </div>
            {link_html}
        </div>
    </div>
    """

def render_section_header(icon, title, color="primary"):
    """Render a section header with icon"""
    gradient_colors = {
        "primary": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "success": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "warning": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "info": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    }
    
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon" style="background: {gradient_colors.get(color, gradient_colors['primary'])}; color: white;">
            {icon}
        </div>
        <h2>{title}</h2>
    </div>
    """, unsafe_allow_html=True)

def render_empty_state(icon, title, description):
    """Render an empty state message"""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)

def render_recommendation_card(rank, place, city, category, rating, fee, score, reasons, description=None):
    """Render a recommendation result card with optional description"""
    score_pct = int(score * 100)
    
    # Escape HTML characters in text fields
    place_safe = html.escape(str(place)) if place else ""
    city_safe = html.escape(str(city)) if city else ""
    category_safe = html.escape(str(category)) if category else ""
    
    reasons_html = "".join([f"<li>{html.escape(str(r))}</li>" for r in reasons[:3]]) if reasons else "<li>Kemiripan umum</li>"
    
    # Add description if available
    desc_html = ""
    if description and pd.notna(description) and str(description).strip():
        desc_text = str(description)[:200] + "..." if len(str(description)) > 200 else str(description)
        desc_safe = html.escape(desc_text)
        desc_html = f'<p style="color: #cbd5e1; font-size: 0.85rem; margin-top: 0.75rem; line-height: 1.5; padding: 0.75rem; background: rgba(99, 102, 241, 0.1); border-radius: 0.5rem; border-left: 3px solid #667eea;">📝 {desc_safe}</p>'
    
    return f"""
    <div style="background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.4); border-left: 4px solid #667eea; margin-bottom: 1rem; border: 1px solid #334155;">
        <div style="display: flex; align-items: flex-start;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 50%; font-weight: 700; font-size: 0.875rem; margin-right: 1rem; flex-shrink: 0;">{rank}</span>
            <div style="flex: 1;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #f1f5f9;">{place_safe}</div>
                <div style="color: #94a3b8; font-size: 0.9rem; margin: 0.25rem 0;">📍 {city_safe} • {category_safe}</div>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                    <span style="color: #f59e0b; font-weight: 600;">⭐ {f'{rating:.1f}' if pd.notna(rating) else 'N/A'}</span>
                    <span style="color: #34d399; font-weight: 600;">Rp {f'{fee:,.0f}' if pd.notna(fee) else '0'}</span>
                </div>
                {desc_html}
                <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 0.375rem; overflow: hidden; margin-top: 0.75rem;">
                    <div style="height: 100%; width: {score_pct}%; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 0.375rem;"></div>
                </div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem;">Kemiripan: {score_pct}%</div>
                <ul style="font-size: 0.85rem; color: #cbd5e1; margin-top: 0.75rem; padding-left: 1.25rem;">
                    {reasons_html}
                </ul>
            </div>
        </div>
    </div>
    """


# =========================
# 3. DATA LOADING
# =========================
@st.cache_data
def load_data():
    """Load and preprocess the tourism dataset"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    image_cols = ["image", "image_url", "foto", "gambar", "photo", "photo_url"]
    required_cols = ["place", "city", "category", "rating", "fee"]
    
    dataset_candidates = [f for f in os.listdir(base_dir) if f.lower().endswith('.xlsx') and 'dataset' in f.lower()]
    selected_path = None
    
    for fname in sorted(dataset_candidates):
        path = os.path.join(base_dir, fname)
        try:
            tmp = pd.read_excel(path, engine="openpyxl")
        except Exception:
            continue
        tmp.columns = [c.strip().lower() for c in tmp.columns]
        missing = [c for c in required_cols if c not in tmp.columns]
        if missing:
            continue
        if any(c in tmp.columns for c in image_cols):
            selected_path = path
            break
        if selected_path is None:
            selected_path = path
    
    if selected_path is None:
        file_path = os.path.join(base_dir, "DATASET.xlsx")
        if not os.path.exists(file_path):
            st.error(f"❌ DATASET.xlsx tidak ditemukan di: {file_path}")
            st.stop()
    else:
        file_path = selected_path
    
    df = pd.read_excel(file_path, engine="openpyxl")
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.copy()
    
    def _clean_string_val(v):
        if pd.isna(v):
            return v
        if isinstance(v, str):
            s = v.replace("\u00A0", " ").replace("\u200B", "").strip()
            return pd.NA if s == "" else s
        return v
    
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].apply(_clean_string_val)
    
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["fee"] = pd.to_numeric(df["fee"], errors="coerce")
    
    # Ensure lat/lon columns exist
    if "lat" not in df.columns and "latitude" in df.columns:
        df["lat"] = df["latitude"]
    elif "lat" not in df.columns:
        df["lat"] = np.nan
        
    if "lon" not in df.columns and "longitude" in df.columns:
        df["lon"] = df["longitude"]
    elif "lon" not in df.columns:
        df["lon"] = np.nan
    
    # Create fee groups
    max_fee = df["fee"].max()
    if pd.isna(max_fee) or not np.isfinite(max_fee):
        max_fee = 100000
    upper = max(max_fee, 100000) + 1
    bins = [-0.1, 0, 25000, 50000, 100000, upper]
    labels = ["Gratis", "<= 25k", "25k - 50k", "50k - 100k", "> 100k"]
    try:
        df["fee_group"] = pd.cut(df["fee"], bins=bins, labels=labels)
    except Exception:
        df["fee_group"] = pd.Series([pd.NA] * len(df))
    
    # Create rating groups
    df["rating_group"] = pd.cut(
        df["rating"],
        bins=[0, 3, 3.5, 4, 4.5, 5],
        labels=["< 3", "3 - 3.5", "3.5 - 4", "4 - 4.5", "4.5 - 5"]
    )
    
    return df, file_path

# Load data
df, dataset_file = load_data()

# =========================
# 4. UTILITY FUNCTIONS
# =========================
def build_embed_url(row: pd.Series) -> str | None:
    """Build Google Maps embed URL from place data (for iframe)"""
    parts = []
    for col in ["place", "city", "alamat"]:
        if col in row.index:
            val = row.get(col)
            if isinstance(val, str) and val.strip():
                parts.append(val.strip())
    
    if not parts:
        return None
    
    query = quote(", ".join(parts))
    return f"https://www.google.com/maps?q={query}&output=embed"

def build_maps_search_url(row: pd.Series) -> str | None:
    """Build Google Maps search URL from place data (for direct link)"""
    parts = []
    for col in ["place", "city", "alamat"]:
        if col in row.index:
            val = row.get(col)
            if isinstance(val, str) and val.strip():
                parts.append(val.strip())
    
    if not parts:
        return None
    
    query = quote(", ".join(parts))
    return f"https://www.google.com/maps/search/?api=1&query={query}"

def get_safe_col(df: pd.DataFrame, col: str):
    """Safely get a column from dataframe"""
    return df[col] if col in df.columns else None

# =========================
# 5. SIDEBAR - MODERN FILTERS
# =========================
with st.sidebar:
    # Sidebar header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🗺️</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0;">Wisata Indonesia</div>
        <div style="font-size: 0.8rem; color: #94a3b8;">Dashboard Explorer</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">📍 Navigasi</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Pilih Halaman",
        ["📊 Overview", "🔍 Eksplor Data", "🗺️ Peta & Detail", "✨ Spotlight", "📈 Insights", "🎯 Recommender", "💡 Personalized"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Filters section
    st.markdown('<p style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">🎛️ Filter Data</p>', unsafe_allow_html=True)
    
    # City filter
    city_col = get_safe_col(df, "city")
    if city_col is not None:
        all_cities = sorted(city_col.dropna().unique())
        selected_cities = st.multiselect(
            "🏙️ Kota",
            options=all_cities,
            default=all_cities,
            help="Pilih satu atau lebih kota"
        )
    else:
        selected_cities = []
    
    # Category filter
    cat_col = get_safe_col(df, "category")
    if cat_col is not None:
        all_categories = sorted(cat_col.dropna().unique())
        selected_categories = st.multiselect(
            "🏷️ Kategori",
            options=all_categories,
            default=all_categories,
            help="Pilih kategori wisata"
        )
    else:
        selected_categories = []
    
    # Rating filter
    min_rating = float(df["rating"].min()) if pd.notna(df["rating"].min()) else 0.0
    max_rating = float(df["rating"].max()) if pd.notna(df["rating"].max()) else 5.0
    rating_range = st.slider(
        "⭐ Range Rating",
        min_value=0.0,
        max_value=5.0,
        value=(min_rating, max_rating),
        step=0.1,
        help="Filter berdasarkan rating"
    )
    
    # Price filter
    min_fee = int(df["fee"].min()) if pd.notna(df["fee"].min()) else 0
    max_fee_slider = int(df["fee"].max()) if pd.notna(df["fee"].max()) else 500000
    try:
        default_cap = int(df["fee"].quantile(0.99))
        if default_cap < min_fee:
            default_cap = max_fee_slider
    except Exception:
        default_cap = max_fee_slider
    
    max_fee = st.slider(
        "💰 Max Harga (IDR)",
        min_value=min_fee,
        max_value=max_fee_slider,
        value=default_cap,
        step=5000,
        format="Rp %d",
        help="Filter berdasarkan harga tiket maksimal"
    )
    
    st.markdown("---")
    
    # Search
    st.markdown('<p style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">🔍 Pencarian</p>', unsafe_allow_html=True)
    keyword = st.text_input(
        "Cari tempat...",
        value="",
        placeholder="Ketik nama tempat...",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Dataset info
    st.markdown('<p style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">📁 Info Dataset</p>', unsafe_allow_html=True)
    
    try:
        ds_name = os.path.basename(dataset_file)
        st.markdown(f'<p style="color: #cbd5e1; font-size: 0.85rem;">📄 {ds_name}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #94a3b8; font-size: 0.8rem;">📊 {len(df):,} tempat wisata</p>', unsafe_allow_html=True)
    except Exception:
        pass
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# =========================
# 6. APPLY FILTERS
# =========================
def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Apply all filters to the dataset"""
    filtered = data.copy()
    
    if "city" in filtered.columns and selected_cities:
        filtered = filtered[filtered["city"].isin(selected_cities)]
    
    if "category" in filtered.columns and selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]
    
    filtered = filtered[
        (filtered["rating"] >= rating_range[0]) &
        (filtered["rating"] <= rating_range[1]) &
        (filtered["fee"] <= max_fee)
    ]
    
    if keyword:
        mask_parts = []
        for col in ["place", "alamat", "deskripsi"]:
            if col in filtered.columns:
                mask_parts.append(
                    filtered[col].astype(str).str.contains(keyword, case=False, na=False)
                )
        if mask_parts:
            mask = mask_parts[0]
            for m in mask_parts[1:]:
                mask |= m
            filtered = filtered[mask]
    
    return filtered

filtered_df = apply_filters(df)

# Check if data is empty
if filtered_df.empty:
    render_header()
    render_empty_state(
        "🔍",
        "Tidak Ada Data",
        "Tidak ada tempat wisata yang cocok dengan filter Anda. Coba ubah kriteria pencarian."
    )
    st.stop()


# =========================
# 7. PAGE: OVERVIEW
# =========================
if page == "📊 Overview":
    render_header()
    
    # Active filters display
    active_filters = []
    if len(selected_cities) < len(all_cities):
        active_filters.append(f"🏙️ {len(selected_cities)} kota")
    if len(selected_categories) < len(all_categories):
        active_filters.append(f"🏷️ {len(selected_categories)} kategori")
    if rating_range != (min_rating, max_rating):
        active_filters.append(f"⭐ {rating_range[0]}-{rating_range[1]}")
    if keyword:
        active_filters.append(f"🔍 '{keyword}'")
    
    if active_filters:
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <span style="color: var(--neutral-500); font-size: 0.875rem; margin-right: 0.5rem;">Filter aktif:</span>
            {"".join([f'<span class="filter-badge">{f}</span>' for f in active_filters])}
        </div>
        """, unsafe_allow_html=True)
    
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_metric_card(
            "🏛️",
            f"{len(filtered_df):,}",
            "Total Tempat Wisata",
            "primary"
        ), unsafe_allow_html=True)
    
    with col2:
        avg_rating = filtered_df['rating'].mean()
        st.markdown(render_metric_card(
            "⭐",
            f"{avg_rating:.2f}" if pd.notna(avg_rating) else "N/A",
            "Rata-rata Rating",
            "warning"
        ), unsafe_allow_html=True)
    
    with col3:
        avg_fee = filtered_df['fee'].mean()
        st.markdown(render_metric_card(
            "💰",
            f"Rp {avg_fee:,.0f}" if pd.notna(avg_fee) else "N/A",
            "Rata-rata Harga",
            "success"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(render_metric_card(
            "🏙️",
            f"{filtered_df['city'].nunique():,}",
            "Jumlah Kota",
            "info"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row 1
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        with st.container(border=True):
            st.markdown('<p style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">📍 Distribusi per Kota</p>', unsafe_allow_html=True)
            
            city_counts = filtered_df.groupby("city")["place"].count().reset_index(name="count")
            city_counts = city_counts.sort_values("count", ascending=False).head(10)
            
            chart = alt.Chart(city_counts).mark_bar(
                cornerRadiusTopRight=8,
                cornerRadiusBottomRight=8,
                color='#667eea'
            ).encode(
                x=alt.X("count:Q", title="Jumlah Tempat"),
                y=alt.Y("city:N", sort="-x", title=""),
                tooltip=["city", "count"]
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
    
    with chart_col2:
        with st.container(border=True):
            st.markdown('<p style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">🏷️ Distribusi per Kategori</p>', unsafe_allow_html=True)
            
            cat_counts = filtered_df.groupby("category")["place"].count().reset_index(name="count")
            cat_counts = cat_counts.sort_values("count", ascending=False)
            
            chart = alt.Chart(cat_counts).mark_arc(innerRadius=60).encode(
                theta=alt.Theta("count:Q"),
                color=alt.Color("category:N", scale=alt.Scale(scheme='tableau20'), legend=alt.Legend(orient='right')),
                tooltip=["category", "count"]
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
    
    # Charts Row 2
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        with st.container(border=True):
            st.markdown('<p style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">⭐ Rating vs 💰 Harga</p>', unsafe_allow_html=True)
            
            scatter = alt.Chart(filtered_df).mark_circle(size=80, opacity=0.6).encode(
                x=alt.X("fee:Q", title="Harga Tiket (IDR)"),
                y=alt.Y("rating:Q", title="Rating"),
                color=alt.Color("category:N", scale=alt.Scale(scheme='tableau20'), legend=None),
                tooltip=["place", "city", "category", "rating", "fee"]
            ).properties(height=300)
            
            st.altair_chart(scatter, use_container_width=True)
    
    with chart_col4:
        with st.container(border=True):
            st.markdown('<p style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">📊 Distribusi Rating</p>', unsafe_allow_html=True)
            
            rating_hist = alt.Chart(filtered_df).mark_bar(
                cornerRadiusTopLeft=4,
                cornerRadiusTopRight=4,
                color='#10b981'
            ).encode(
                x=alt.X("rating:Q", bin=alt.Bin(maxbins=10), title="Rating"),
                y=alt.Y("count():Q", title="Jumlah"),
                tooltip=["count()"]
            ).properties(height=300)
            st.altair_chart(rating_hist, use_container_width=True)
    
    # Smart Picks Section
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("✨", "Smart Picks - Rekomendasi Terbaik", "success")
    
    st.markdown("""
    <p style="color: var(--neutral-500); margin-bottom: 1.5rem;">
        Tempat wisata dengan kombinasi rating tinggi dan harga terjangkau
    </p>
    """, unsafe_allow_html=True)
    
    # Calculate smart score
    scored_df = filtered_df.copy()
    scored_df["rating_norm"] = scored_df["rating"].fillna(0) / 5.0
    fee_min, fee_max = scored_df["fee"].min(), scored_df["fee"].max()
    if pd.notna(fee_min) and pd.notna(fee_max) and fee_max != fee_min:
        scored_df["fee_norm"] = 1 - ((scored_df["fee"].fillna(fee_max) - fee_min) / (fee_max - fee_min))
    else:
        scored_df["fee_norm"] = 0.5
    scored_df["smart_score"] = (0.7 * scored_df["rating_norm"]) + (0.3 * scored_df["fee_norm"])
    top_picks = scored_df.sort_values("smart_score", ascending=False).head(5)
    
    # Display top picks as cards
    pick_cols = st.columns(5)
    for i, (_, row) in enumerate(top_picks.iterrows()):
        with pick_cols[i]:
            link = build_maps_search_url(row)
            st.markdown(render_place_card(
                row['place'],
                row['city'],
                row['category'],
                row['rating'],
                row['fee'],
                link
            ), unsafe_allow_html=True)

# =========================
# 8. PAGE: EKSPLOR DATA
# =========================
elif page == "🔍 Eksplor Data":
    render_header()
    render_section_header("🔍", "Eksplorasi Data Wisata", "primary")
    
    # Summary stats
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.metric("Total Data", f"{len(filtered_df):,}")
    with stat_cols[1]:
        st.metric("Kota", f"{filtered_df['city'].nunique()}")
    with stat_cols[2]:
        st.metric("Kategori", f"{filtered_df['category'].nunique()}")
    with stat_cols[3]:
        free_count = len(filtered_df[filtered_df['fee'] == 0])
        st.metric("Gratis", f"{free_count:,}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data table
    display_cols = [c for c in ["place", "city", "category", "rating", "fee", "alamat", "deskripsi"] if c in filtered_df.columns]
    
    st.dataframe(
        filtered_df[display_cols].fillna("").reset_index(drop=True),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv_bytes = filtered_df[display_cols].fillna("").to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_bytes,
        file_name="wisata_filtered.csv",
        mime="text/csv"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Top lists
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        with st.container(border=True):
            st.markdown('<div class="chart-title">🏆 Top 10 Rating Tertinggi</div>', unsafe_allow_html=True)
            top_rating = filtered_df.sort_values("rating", ascending=False).head(10)
            st.dataframe(
                top_rating[["place", "city", "rating", "fee"]].reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )
    
    with col_top2:
        with st.container(border=True):
            st.markdown('<div class="chart-title">💎 Top 10 Value Terbaik</div>', unsafe_allow_html=True)
            value_df = filtered_df[filtered_df["rating"] >= 4].sort_values("fee").head(10)
            st.dataframe(
                value_df[["place", "city", "rating", "fee"]].reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )


# =========================
# 9. PAGE: PETA & DETAIL
# =========================
elif page == "🗺️ Peta & Detail":
    render_header()
    render_section_header("🗺️", "Peta & Detail Tempat", "info")
    
    # Row 1: Selection controls
    sel_col1, sel_col2 = st.columns(2)
    
    with sel_col1:
        selected_city_map = st.selectbox(
            "🏙️ Pilih Kota",
            options=sorted(filtered_df["city"].unique()),
            key="map_city"
        )
    
    df_city = filtered_df[filtered_df["city"] == selected_city_map]
    
    with sel_col2:
        selected_place = st.selectbox(
            "📍 Pilih Tempat Wisata",
            options=df_city["place"].tolist(),
            key="map_place"
        )
    
    if selected_place:
        place_row = df_city[df_city["place"] == selected_place].iloc[0]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Row 2: Main content - 3 columns (Info | Map | Description/Review)
        col_info, col_map, col_detail = st.columns([1, 1.5, 1.5])
        
        # Column 1: Basic Info
        with col_info:
            st.markdown(f"""
            <div style="padding: 1.25rem; background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%); border-radius: 0.75rem; border: 1px solid #334155; height: 100%;">
                <h3 style="margin: 0 0 1rem 0; color: #f1f5f9; font-size: 1.25rem;">{place_row['place']}</h3>
                <p style="color: #94a3b8; margin: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">📍 {place_row['city']}</p>
                <p style="color: #94a3b8; margin: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">🏷️ {place_row['category']}</p>
                <p style="color: #f59e0b; font-weight: 600; margin: 0.75rem 0; font-size: 1.1rem;">⭐ {f"{place_row['rating']:.1f}" if pd.notna(place_row['rating']) else 'N/A'}</p>
                <p style="color: #34d399; font-weight: 600; margin: 0.5rem 0; font-size: 1.1rem;">💰 Rp {f"{place_row['fee']:,.0f}" if pd.notna(place_row['fee']) else '0'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Opening hours
            opening_hours = None
            for oh_col in ['opening_hours', 'opening hours', 'jam_buka', 'jam buka']:
                if oh_col in place_row.index and pd.notna(place_row.get(oh_col)):
                    opening_hours = place_row.get(oh_col)
                    break
            
            if opening_hours:
                st.markdown(f"""
                <div style="margin-top: 0.75rem; padding: 0.75rem; background: rgba(16, 185, 129, 0.15); border-radius: 0.5rem; border-left: 4px solid #10b981;">
                    <p style="color: #34d399; margin: 0; font-size: 0.9rem;">🕐 {opening_hours}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Address
            if 'alamat' in place_row.index and pd.notna(place_row.get('alamat')):
                st.markdown(f"""
                <div style="margin-top: 0.75rem; padding: 0.75rem; background: rgba(99, 102, 241, 0.15); border-radius: 0.5rem; border-left: 4px solid #667eea;">
                    <p style="color: #a5b4fc; margin: 0; font-size: 0.85rem;">📍 {place_row['alamat']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Column 2: Google Maps
        with col_map:
            st.markdown('<p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.5rem;">🗺️ Lokasi di Google Maps</p>', unsafe_allow_html=True)
            embed_url = build_embed_url(place_row)
            if embed_url:
                st.components.v1.iframe(embed_url, height=350)
            else:
                render_empty_state("🗺️", "Peta Tidak Tersedia", "Tidak dapat memuat peta")
        
        # Column 3: Description & Review (side by side, not stacked)
        with col_detail:
            # Description
            if 'deskripsi' in place_row.index and pd.notna(place_row.get('deskripsi')):
                st.markdown(f"""
                <div style="padding: 1rem; background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%); border-radius: 0.75rem; border: 1px solid #334155; margin-bottom: 0.75rem;">
                    <p style="color: #a5b4fc; font-weight: 600; margin: 0 0 0.5rem 0; font-size: 0.9rem;">📝 Deskripsi</p>
                    <p style="color: #e2e8f0; margin: 0; line-height: 1.6; font-size: 0.9rem; max-height: 120px; overflow-y: auto;">{place_row['deskripsi']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Review/Ulasan
            review_text = None
            for rev_col in ['review', 'ulasan', 'reviews']:
                if rev_col in place_row.index and pd.notna(place_row.get(rev_col)):
                    review_text = place_row.get(rev_col)
                    break
            
            if review_text:
                st.markdown(f"""
                <div style="padding: 1rem; background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%); border-radius: 0.75rem; border: 1px solid #334155;">
                    <p style="color: #a5b4fc; font-weight: 600; margin: 0 0 0.5rem 0; font-size: 0.9rem;">💬 Ulasan / Review</p>
                    <p style="color: #e2e8f0; margin: 0; line-height: 1.6; font-size: 0.9rem; max-height: 150px; overflow-y: auto;">{review_text}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if not review_text and not ('deskripsi' in place_row.index and pd.notna(place_row.get('deskripsi'))):
                st.markdown("""
                <div style="padding: 1.5rem; background: linear-gradient(145deg, #16213e 0%, #1a1a2e 100%); border-radius: 0.75rem; border: 1px solid #334155; text-align: center;">
                    <p style="color: #64748b; margin: 0;">Tidak ada deskripsi atau ulasan</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Row 3: Map with markers (if coordinates available)
        if {"lat", "lon"}.issubset(df_city.columns):
            df_map = df_city.copy()
            df_map["latitude"] = pd.to_numeric(df_map["lat"], errors="coerce")
            df_map["longitude"] = pd.to_numeric(df_map["lon"], errors="coerce")
            coords = df_map[["latitude", "longitude"]].dropna()
            if not coords.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.5rem;">📍 Semua Lokasi di Kota Ini</p>', unsafe_allow_html=True)
                st.map(coords)

# =========================
# 10. PAGE: SPOTLIGHT
# =========================
elif page == "✨ Spotlight":
    render_header()
    render_section_header("✨", "Spotlight - Pilihan Menarik", "warning")
    
    # Random spotlight
    with st.container(border=True):
        st.markdown('<div class="chart-title">🎲 Sorotan Acak</div>', unsafe_allow_html=True)
        
        col_btn, col_info = st.columns([1, 3])
        
        with col_btn:
            if st.button("🎲 Acak Tempat Baru", use_container_width=True):
                st.session_state["spotlight_idx"] = int(filtered_df.sample(1).index[0])
        
        if "spotlight_idx" not in st.session_state or st.session_state["spotlight_idx"] not in filtered_df.index:
            st.session_state["spotlight_idx"] = int(filtered_df.sample(1).index[0])
        
        try:
            spotlight_row = filtered_df.loc[st.session_state["spotlight_idx"]]
        except Exception:
            spotlight_row = filtered_df.sample(1).iloc[0]
        
        with col_info:
            st.markdown(f"""
            <div style="padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: var(--radius-xl); color: white;">
                <h2 style="margin: 0 0 0.5rem 0;">{spotlight_row['place']}</h2>
                <p style="opacity: 0.9; margin: 0.25rem 0;">📍 {spotlight_row['city']} • 🏷️ {spotlight_row['category']}</p>
                <p style="margin: 0.75rem 0; font-size: 1.1rem;">
                    ⭐ {f"{spotlight_row['rating']:.1f}" if pd.notna(spotlight_row['rating']) else 'N/A'} 
                    &nbsp;•&nbsp; 
                    💰 Rp {f"{spotlight_row['fee']:,.0f}" if pd.notna(spotlight_row['fee']) else '0'}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Show map for spotlight place
    with st.container(border=True):
        st.markdown('<div class="chart-title">🗺️ Lokasi di Peta</div>', unsafe_allow_html=True)
        embed_url = build_embed_url(spotlight_row)
        if embed_url:
            st.components.v1.iframe(embed_url, height=300)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Leaderboards
    render_section_header("🏆", "Leaderboard", "success")
    
    lb_col1, lb_col2 = st.columns(2)
    
    with lb_col1:
        with st.container(border=True):
            st.markdown('<div class="chart-title">💎 Termurah (Top 5)</div>', unsafe_allow_html=True)
            cheap = filtered_df.sort_values("fee").head(5)[["place", "city", "fee", "rating"]]
            st.dataframe(cheap.reset_index(drop=True), use_container_width=True, hide_index=True)
        
        with st.container(border=True):
            st.markdown('<div class="chart-title">⭐ Rating Tertinggi (Top 5)</div>', unsafe_allow_html=True)
            top_r = filtered_df.sort_values("rating", ascending=False).head(5)[["place", "city", "rating", "fee"]]
            st.dataframe(top_r.reset_index(drop=True), use_container_width=True, hide_index=True)
    
    with lb_col2:
        with st.container(border=True):
            st.markdown('<div class="chart-title">💰 Termahal (Top 5)</div>', unsafe_allow_html=True)
            exp = filtered_df.sort_values("fee", ascending=False).head(5)[["place", "city", "fee", "rating"]]
            st.dataframe(exp.reset_index(drop=True), use_container_width=True, hide_index=True)
        
        # City comparison
        with st.container(border=True):
            st.markdown('<div class="chart-title">📊 Bandingkan Kota</div>', unsafe_allow_html=True)
            
            city_opts = sorted(filtered_df["city"].dropna().unique())
            if len(city_opts) >= 2:
                comp_col1, comp_col2 = st.columns(2)
                with comp_col1:
                    city_a = st.selectbox("Kota A", options=city_opts, index=0, key="comp_a")
                with comp_col2:
                    city_b = st.selectbox("Kota B", options=city_opts, index=min(1, len(city_opts)-1), key="comp_b")
                
                da = filtered_df[filtered_df["city"] == city_a]
                db = filtered_df[filtered_df["city"] == city_b]
                
                comp_data = pd.DataFrame({
                    "Metrik": ["Jumlah Tempat", "Avg Rating", "Avg Harga"],
                    city_a: [len(da), f"{da['rating'].mean():.2f}", f"Rp {da['fee'].mean():,.0f}"],
                    city_b: [len(db), f"{db['rating'].mean():.2f}", f"Rp {db['fee'].mean():,.0f}"]
                })
                st.dataframe(comp_data, use_container_width=True, hide_index=True)

# =========================
# 11. PAGE: INSIGHTS
# =========================
elif page == "📈 Insights":
    render_header()
    render_section_header("📈", "Insights & Analytics", "primary")
    
    # Heatmap
    with st.container(border=True):
        st.markdown('<div class="chart-title">🔥 Heatmap: Kota × Kategori</div>', unsafe_allow_html=True)
        
        pivot = filtered_df.groupby(["city", "category"])["place"].count().reset_index(name="count")
        
        if not pivot.empty:
            heat = alt.Chart(pivot).mark_rect().encode(
                x=alt.X("category:N", sort=alt.EncodingSortField(field="count", op="sum", order="descending"), title="Kategori"),
                y=alt.Y("city:N", sort=alt.EncodingSortField(field="count", op="sum", order="descending"), title="Kota"),
                color=alt.Color("count:Q", title="Jumlah", scale=alt.Scale(scheme="blues")),
                tooltip=["city", "category", "count"]
            ).properties(height=400)
            
            st.altair_chart(heat, use_container_width=True)
    
    # Bubble chart
    with st.container(border=True):
        st.markdown('<div class="chart-title">🫧 Bubble: Harga vs Rating per Kota</div>', unsafe_allow_html=True)
        
        agg_city = filtered_df.groupby("city").agg(
            avg_rating=("rating", "mean"),
            avg_fee=("fee", "mean"),
            count=("place", "count")
        ).reset_index()
        
        bubble = alt.Chart(agg_city).mark_circle(opacity=0.7).encode(
            x=alt.X("avg_fee:Q", title="Rata-rata Harga (IDR)"),
            y=alt.Y("avg_rating:Q", title="Rata-rata Rating"),
            size=alt.Size("count:Q", title="Jumlah Tempat", scale=alt.Scale(range=[100, 2000])),
            color=alt.Color("city:N", legend=None),
            tooltip=["city", "avg_fee", "avg_rating", "count"]
        ).properties(height=400)
        
        st.altair_chart(bubble, use_container_width=True)
    
    # Top categories bar
    with st.container(border=True):
        st.markdown('<div class="chart-title">🏷️ Top Kategori</div>', unsafe_allow_html=True)
        
        cat_counts = filtered_df.groupby("category")["place"].count().reset_index(name="count")
        cat_counts = cat_counts.sort_values("count", ascending=False).head(10)
        
        bar = alt.Chart(cat_counts).mark_bar(
            cornerRadiusTopRight=8,
            cornerRadiusBottomRight=8
        ).encode(
            x=alt.X("count:Q", title="Jumlah Tempat"),
            y=alt.Y("category:N", sort="-x", title=""),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="greens"), legend=None),
            tooltip=["category", "count"]
        ).properties(height=300)
        
        st.altair_chart(bar, use_container_width=True)
    
    # Word Cloud Section
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("☁️", "Word Cloud", "info")
    
    with st.container(border=True):
        st.markdown('<div class="chart-title">☁️ Word Cloud dari Teks</div>', unsafe_allow_html=True)
        
        text_cols = [c for c in ["deskripsi", "review", "ulasan", "place", "alamat"] if c in filtered_df.columns]
        
        if not text_cols:
            st.info("Tidak ada kolom teks (deskripsi/review/place/alamat) di dataset untuk membuat Word Cloud.")
        else:
            wc_col1, wc_col2 = st.columns([2, 1])
            
            with wc_col1:
                col_choice = st.selectbox("Pilih kolom teks", options=text_cols, key="wc_col")
            
            with wc_col2:
                max_words = st.slider("Jumlah kata maksimum", min_value=20, max_value=200, value=100, key="wc_max")
            
            stopword_col1, stopword_col2 = st.columns(2)
            with stopword_col1:
                stopword_en = st.checkbox("Gunakan stopwords Inggris", value=True, key="wc_en")
            with stopword_col2:
                stopword_id = st.checkbox("Gunakan stopwords Indonesia", value=True, key="wc_id")
            
            if st.button("🔍 Buat Word Cloud", use_container_width=True, key="wc_btn"):
                text = " ".join(filtered_df[col_choice].dropna().astype(str).tolist())
                
                if not text.strip():
                    st.warning("Tidak ada teks untuk kolom ini setelah filter.")
                else:
                    try:
                        from wordcloud import WordCloud, STOPWORDS
                        import io
                        
                        sw = set(STOPWORDS) if stopword_en else set()
                        if stopword_id:
                            id_sw = {
                                'dan', 'di', 'ke', 'yang', 'dari', 'untuk', 'pada', 'dengan', 'ada', 'ini', 'itu', 'sangat',
                                'atau', 'sebagai', 'akan', 'lebih', 'saja', 'lagi', 'juga', 'karena', 'oleh', 'bisa', 'dapat',
                                'adalah', 'tersebut', 'sudah', 'belum', 'hanya', 'seperti', 'saat', 'ketika', 'jika', 'maka',
                                'tempat', 'wisata', 'lokasi', 'area', 'kawasan', 'objek', 'destinasi'
                            }
                            sw = sw.union(id_sw)
                        
                        wc = WordCloud(
                            width=800, 
                            height=400, 
                            background_color="#1a1a2e",
                            colormap='cool',
                            stopwords=sw,
                            collocations=False, 
                            min_font_size=10, 
                            max_words=max_words
                        )
                        wc.generate(text)
                        img = wc.to_image()
                        st.image(img, use_container_width=True)
                        
                        # Download button
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        buf.seek(0)
                        st.download_button(
                            "⬇️ Download Word Cloud (PNG)", 
                            data=buf, 
                            file_name="wordcloud.png", 
                            mime="image/png"
                        )
                        
                    except ImportError:
                        st.warning("Library wordcloud tidak tersedia. Install dengan: `pip install wordcloud`")
                        
                        # Fallback: word frequency bar chart
                        import re
                        from collections import Counter
                        
                        txt = text.lower()
                        txt = re.sub(r"[^\w\s]", " ", txt)
                        txt = re.sub(r"\d+", " ", txt)
                        tokens = [t for t in txt.split() if len(t) > 2]
                        
                        sw = set()
                        if stopword_en:
                            sw = {'the', 'and', 'for', 'with', 'that', 'this', 'from', 'are', 'was', 'but', 'not', 'you', 'have'}
                        if stopword_id:
                            sw = sw.union({'dan', 'di', 'ke', 'yang', 'dari', 'untuk', 'pada', 'dengan', 'ada', 'ini', 'itu'})
                        
                        filtered_tokens = [t for t in tokens if t not in sw]
                        cnt = Counter(filtered_tokens)
                        top = cnt.most_common(max_words)
                        df_wc = pd.DataFrame(top, columns=["word", "count"])
                        
                        chart = alt.Chart(df_wc.head(30)).mark_bar().encode(
                            x=alt.X("count:Q", title="Frekuensi"),
                            y=alt.Y("word:N", sort='-x', title="Kata"),
                            color=alt.Color("count:Q", scale=alt.Scale(scheme="blues"), legend=None),
                            tooltip=["word", "count"]
                        ).properties(height=400)
                        
                        st.altair_chart(chart, use_container_width=True)


# =========================
# 12. PAGE: RECOMMENDER
# =========================
elif page == "🎯 Recommender":
    render_header()
    render_section_header("🎯", "Recommender - Temukan Tempat Serupa", "primary")
    
    st.markdown("""
    <p style="color: var(--neutral-500); margin-bottom: 1.5rem;">
        Pilih tempat referensi dan temukan destinasi serupa berdasarkan kategori, lokasi, harga, dan karakteristik lainnya.
    </p>
    """, unsafe_allow_html=True)
    
    col_select, col_num = st.columns([3, 1])
    
    with col_select:
        ref_place_name = st.selectbox(
            "🔍 Pilih Tempat Referensi",
            options=filtered_df['place'].tolist(),
            key="recommender_ref"
        )
    
    with col_num:
        top_n = st.slider("Jumlah Hasil", 3, 20, 10, key="recommender_n")
    
    if st.button("🔍 Cari Tempat Serupa", use_container_width=True, type="primary"):
        with st.spinner("🔄 Mencari tempat serupa..."):
            df_reset = filtered_df.reset_index(drop=True)
            try:
                ref_idx = df_reset[df_reset['place'] == ref_place_name].index[0]
                similar_df = get_similar_places(ref_idx, df_reset, top_n=top_n)
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {str(e)}")
                similar_df = None
        
        if similar_df is not None and not similar_df.empty:
            # Show reference place
            ref_place = filtered_df[filtered_df['place'] == ref_place_name].iloc[0]
            
            st.markdown(f"""
            <div style="padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: var(--radius-xl); color: white; margin: 1.5rem 0;">
                <p style="opacity: 0.8; margin: 0 0 0.5rem 0; font-size: 0.875rem;">📍 TEMPAT REFERENSI</p>
                <h2 style="margin: 0 0 0.5rem 0;">{ref_place['place']}</h2>
                <p style="opacity: 0.9; margin: 0;">
                    {ref_place['city']} • {ref_place['category']} • 
                    ⭐ {f"{ref_place['rating']:.1f}" if pd.notna(ref_place['rating']) else 'N/A'} • 
                    Rp {f"{ref_place['fee']:,.0f}" if pd.notna(ref_place['fee']) else '0'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.success(f"✅ Ditemukan {len(similar_df)} tempat serupa!")
            
            # Display results using Streamlit components
            for rank, (_, row) in enumerate(similar_df.iterrows(), 1):
                with st.container(border=True):
                    col_rank, col_content = st.columns([0.5, 5])
                    
                    with col_rank:
                        st.markdown(f"""
                        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 1rem;">{rank}</div>
                        """, unsafe_allow_html=True)
                    
                    with col_content:
                        st.markdown(f"**{row['place']}**")
                        st.caption(f"📍 {row['city']} • {row['category']}")
                        
                        # Rating and price
                        rating_str = f"⭐ {row['rating']:.1f}" if pd.notna(row['rating']) else "⭐ N/A"
                        fee_str = f"💰 Rp {row['fee']:,.0f}" if pd.notna(row['fee']) else "💰 Gratis"
                        st.markdown(f"{rating_str} &nbsp;&nbsp; {fee_str}")
                        
                        # Description
                        desc = row.get('deskripsi', None) if 'deskripsi' in row.index else None
                        if desc and pd.notna(desc) and str(desc).strip():
                            desc_text = str(desc)[:250] + "..." if len(str(desc)) > 250 else str(desc)
                            st.info(f"📝 {desc_text}")
                        
                        # Similarity bar
                        score_pct = int(row['score'] * 100)
                        st.progress(row['score'], text=f"Kemiripan: {score_pct}%")
                        
                        # Reasons - styled badges
                        if row['reasons']:
                            reasons_badges = []
                            for r in row['reasons'][:4]:
                                reason_str = str(r).replace("✓ ", "")
                                # Add appropriate emoji based on reason type
                                if "Kategori" in reason_str:
                                    reasons_badges.append(f"🏷️ {reason_str}")
                                elif "Kota" in reason_str:
                                    reasons_badges.append(f"📍 {reason_str}")
                                elif "Rating" in reason_str:
                                    reasons_badges.append(f"⭐ {reason_str}")
                                elif "harga" in reason_str.lower() or "gratis" in reason_str.lower():
                                    reasons_badges.append(f"💰 {reason_str}")
                                elif "Fasilitas" in reason_str:
                                    reasons_badges.append(f"🏢 {reason_str}")
                                elif "Suasana" in reason_str:
                                    reasons_badges.append(f"🌿 {reason_str}")
                                elif "deskripsi" in reason_str.lower() or "Tema" in reason_str:
                                    reasons_badges.append(f"📝 {reason_str}")
                                else:
                                    reasons_badges.append(f"✨ {reason_str}")
                            
                            st.markdown(f"""
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                                {"".join([f'<span style="background: rgba(99, 102, 241, 0.2); color: #a5b4fc; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.8rem; border: 1px solid rgba(99, 102, 241, 0.3);">{badge}</span>' for badge in reasons_badges])}
                            </div>
                            """, unsafe_allow_html=True)
        
        elif similar_df is not None:
            render_empty_state(
                "🔍",
                "Tidak Ada Hasil",
                "Tidak ditemukan tempat serupa. Coba pilih tempat referensi lain atau ubah filter."
            )

# =========================
# 13. PAGE: PERSONALIZED PICKS
# =========================
elif page == "💡 Personalized":
    render_header()
    render_section_header("💡", "Personalized Picks - Rekomendasi untuk Anda", "success")
    
    st.markdown("""
    <p style="color: var(--neutral-500); margin-bottom: 1.5rem;">
        Atur preferensi Anda untuk mendapatkan rekomendasi tempat wisata yang paling sesuai.
    </p>
    """, unsafe_allow_html=True)
    
    # Preference controls
    pref_col1, pref_col2, pref_col3 = st.columns(3)
    
    with pref_col1:
        kota_pref = st.multiselect(
            "🏙️ Kota Pilihan",
            options=sorted(df["city"].unique()),
            help="Kosongkan untuk semua kota"
        )
    
    with pref_col2:
        kategori_pref = st.multiselect(
            "🏷️ Kategori Favorit",
            options=sorted(df["category"].unique()),
            help="Kosongkan untuk semua kategori"
        )
    
    with pref_col3:
        min_rating_pref = st.slider(
            "⭐ Minimal Rating",
            min_value=0.0,
            max_value=5.0,
            value=3.5,
            step=0.1
        )
    
    max_budget_pref = st.slider(
        "💰 Budget Maksimal (IDR)",
        min_value=0,
        max_value=int(df["fee"].max()) if pd.notna(df["fee"].max()) else 500000,
        value=int(df["fee"].quantile(0.75)) if pd.notna(df["fee"].quantile(0.75)) else 100000,
        step=5000,
        format="Rp %d"
    )
    
    st.markdown("---")
    
    # Apply preferences
    rec_df = df.copy()
    
    if kota_pref:
        rec_df = rec_df[rec_df["city"].isin(kota_pref)]
    
    if kategori_pref:
        rec_df = rec_df[rec_df["category"].isin(kategori_pref)]
    
    rec_df = rec_df[
        (rec_df["rating"].fillna(0) >= min_rating_pref) &
        (rec_df["fee"].fillna(rec_df["fee"].max()) <= max_budget_pref)
    ]
    
    if rec_df.empty:
        render_empty_state(
            "😔",
            "Tidak Ada Hasil",
            "Tidak ada tempat yang cocok dengan preferensi Anda. Coba ubah kriteria pencarian."
        )
    else:
        # Calculate scores
        rec_df = rec_df.copy()
        rec_df['score_rating'] = rec_df['rating'].fillna(0) / 5.0
        
        max_fee_val = rec_df['fee'].max()
        if pd.isna(max_fee_val) or max_fee_val == 0:
            max_fee_val = 1.0
        rec_df['score_value'] = 1 - (rec_df['fee'].fillna(max_fee_val) / max_fee_val)
        
        rec_df['combined_score'] = (rec_df['score_rating'] * 0.6) + (rec_df['score_value'] * 0.4)
        rec_df = rec_df.sort_values('combined_score', ascending=False)
        
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--success-500); color: white; border-radius: var(--radius-lg); margin-bottom: 1.5rem; text-align: center;">
            <strong>✨ Ditemukan {len(rec_df)} tempat yang cocok dengan preferensi Anda!</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Top 3 picks
        st.markdown('<p style="font-weight: 600; color: var(--neutral-700); margin-bottom: 1rem;">🏆 Top 3 Pilihan Terbaik</p>', unsafe_allow_html=True)
        
        top3_cols = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (_, row) in enumerate(rec_df.head(3).iterrows()):
            with top3_cols[i]:
                score_pct = int(row['combined_score'] * 100)
                st.markdown(f"""
                <div class="place-card" style="border-top: 4px solid var(--primary-500);">
                    <div class="place-card-content">
                        <div style="font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">{medals[i]}</div>
                        <span class="place-card-category">{row['category']}</span>
                        <div class="place-card-title">{row['place']}</div>
                        <div class="place-card-location">📍 {row['city']}</div>
                        <div class="place-card-meta">
                            <span class="place-card-rating">⭐ {f"{row['rating']:.1f}" if pd.notna(row['rating']) else 'N/A'}</span>
                            <span class="place-card-price">Rp {f"{row['fee']:,.0f}" if pd.notna(row['fee']) else '0'}</span>
                        </div>
                        <div class="similarity-bar" style="margin-top: 0.75rem;">
                            <div class="similarity-bar-fill" style="width: {score_pct}%;"></div>
                        </div>
                        <div style="font-size: 0.75rem; color: var(--neutral-500); margin-top: 0.25rem; text-align: center;">Skor: {score_pct}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Full list
        st.markdown('<p style="font-weight: 600; color: var(--neutral-700); margin-bottom: 1rem;">📋 Daftar Lengkap</p>', unsafe_allow_html=True)
        
        display_df = rec_df[["place", "city", "category", "rating", "fee"]].copy()
        display_df["Skor"] = (rec_df["combined_score"] * 100).astype(int).astype(str) + "%"
        
        st.dataframe(
            display_df.reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
        
        # Random pick
        st.markdown("<br>", unsafe_allow_html=True)
        col_rand, col_result = st.columns([1, 3])
        
        with col_rand:
            if st.button("🎲 Pilih Acak", use_container_width=True):
                random_row = rec_df.sample(1).iloc[0]
                st.session_state['random_pick'] = random_row
        
        if 'random_pick' in st.session_state:
            row = st.session_state['random_pick']
            with col_result:
                st.success(f"**{row['place']}** • {row['city']} • {row['category']} • ⭐ {row['rating']:.1f} • Rp {row['fee']:,.0f}")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: var(--neutral-400);">
    <p style="margin: 0;">🗺️ Dashboard Wisata Indonesia</p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
