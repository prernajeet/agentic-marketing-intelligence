"""
utils/styling.py
Premium design system for the Agentic Marketing Intelligence dashboard.
Provides glassmorphism cards, animated KPI metrics, gradient headers,
Inter/Outfit Google Fonts, and dark-mode ready CSS variables.
"""

import streamlit as st

PREMIUM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ── Root Tokens ──────────────────────────────────────────── */
:root {
  --bg:          #0a0f1e;
  --bg-card:     rgba(255,255,255,0.05);
  --bg-card-hov: rgba(255,255,255,0.09);
  --border:      rgba(255,255,255,0.10);
  --border-hov:  rgba(255,255,255,0.20);
  --text:        #e2e8f0;
  --text-muted:  #94a3b8;
  --primary:     #6366f1;
  --primary-glow:#818cf8;
  --accent:      #06b6d4;
  --accent2:     #a855f7;
  --success:     #10b981;
  --warning:     #f59e0b;
  --danger:      #ef4444;
  --radius:      14px;
  --radius-sm:   8px;
  --shadow:      0 8px 32px rgba(0,0,0,0.4);
  --font:        'Inter', sans-serif;
  --font-head:   'Outfit', sans-serif;
}

/* ── Global Reset & Base ───────────────────────────────────── */
html, body, [class*="css"] {
  font-family: var(--font) !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

/* Hide Streamlit default chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .css-1d391kg,
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Page Header ──────────────────────────────────────────── */
.page-header {
  background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.10) 50%, rgba(6,182,212,0.10) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem 2.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}
.page-header::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 200px; height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%);
}
.page-header h1 {
  font-family: var(--font-head) !important;
  font-size: 2.2rem !important;
  font-weight: 800 !important;
  background: linear-gradient(135deg, #fff 0%, var(--primary-glow) 50%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.4rem 0 !important;
}
.page-header p {
  color: var(--text-muted) !important;
  font-size: 1rem;
  margin: 0;
}

/* ── Glass Cards ──────────────────────────────────────────── */
.glass-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: var(--shadow);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  margin-bottom: 1rem;
}
.glass-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.5);
  border-color: var(--border-hov);
}

/* ── KPI / Metric Cards ───────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  transition: transform 0.25s, box-shadow 0.25s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,0.45); }
.kpi-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0;
  height: 3px; width: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 0 0 var(--radius) var(--radius);
}
.kpi-label  { font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
.kpi-value  { font-family: var(--font-head); font-size: 2rem; font-weight: 700; color: #fff; }
.kpi-delta  { font-size: 0.82rem; margin-top: 0.3rem; }
.kpi-delta.pos { color: var(--success); }
.kpi-delta.neg { color: var(--danger); }

/* ── Champion Banner ──────────────────────────────────────── */
.champion-banner {
  background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(168,85,247,0.15) 100%);
  border: 1px solid rgba(99,102,241,0.4);
  border-radius: var(--radius);
  padding: 1.4rem 1.8rem;
  margin: 1rem 0;
  display: flex; align-items: center; gap: 1rem;
}
.champion-banner .trophy { font-size: 2.5rem; }
.champion-banner h3 { margin: 0; font-family: var(--font-head); font-weight: 700; font-size: 1.2rem; }
.champion-banner p  { margin: 0.2rem 0 0 0; color: var(--text-muted); font-size: 0.9rem; }

/* ── Section Headers ─────────────────────────────────────── */
.section-header {
  display: flex; align-items: center; gap: 0.7rem;
  margin: 2rem 0 1rem 0;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--border);
}
.section-header span { font-family: var(--font-head); font-size: 1.3rem; font-weight: 700; }
.section-header .badge {
  background: linear-gradient(135deg, var(--primary), var(--accent2));
  border-radius: 20px;
  padding: 0.2rem 0.75rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ── Tables ──────────────────────────────────────────────── */
.stDataFrame { border-radius: var(--radius); overflow: hidden; }
[data-testid="stDataFrame"] table {
  background: var(--bg-card) !important;
  border-radius: var(--radius) !important;
}
[data-testid="stDataFrame"] th {
  background: rgba(99,102,241,0.2) !important;
  color: var(--text) !important;
  font-family: var(--font-head) !important;
  font-weight: 600 !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent2) 100%) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  transition: opacity 0.2s, transform 0.2s !important;
}
.stButton > button:hover {
  opacity: 0.88 !important;
  transform: translateY(-1px) !important;
}

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card) !important;
  border-radius: var(--radius-sm) !important;
  gap: 2px;
}
.stTabs [data-baseweb="tab"] {
  color: var(--text-muted) !important;
  font-family: var(--font) !important;
  font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--primary), var(--accent2)) !important;
  color: #fff !important;
  border-radius: var(--radius-sm) !important;
}

/* ── Alerts / Info boxes ─────────────────────────────────── */
.stAlert, .stInfo, .stSuccess, .stWarning, .stError {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
}

/* ── Input Fields ─────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
}

/* ── Spinner ─────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ── Metrics ─────────────────────────────────────────────── */
[data-testid="stMetricValue"] { color: #fff !important; font-family: var(--font-head) !important; font-size: 1.8rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.82rem !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; font-weight: 600 !important; }

/* ── Expander ─────────────────────────────────────────────── */
.streamlit-expanderHeader {
  background: var(--bg-card) !important;
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  font-weight: 600 !important;
}
"""


def apply_premium_styling():
    """Inject the full premium CSS design system. Call once at the top of each page."""
    st.markdown(f"<style>{PREMIUM_CSS}</style>", unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    """Render the gradient animated page header without leading markdown indentation."""
    apply_premium_styling()
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    html = f'<div class="page-header"><h1>{icon} {title}</h1>{sub_html}</div>'
    st.html(html)


def kpi_card(label: str, value: str, delta: str = "", positive: bool = True):
    """Render a single glass KPI card as a flat HTML string."""
    delta_cls = "pos" if positive else "neg"
    delta_icon = "▲" if positive else "▼"
    delta_html = f'<div class="kpi-delta {delta_cls}">{delta_icon} {delta}</div>' if delta else ""
    return f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{delta_html}</div>'


def kpi_row(cards: list):
    """Render a row of KPI cards inside a grid as a flat HTML string."""
    inner = "".join(kpi_card(**c) for c in cards)
    st.html(f'<div class="kpi-grid">{inner}</div>')


def section_header(icon: str, title: str, badge: str = ""):
    """Render a styled section header with optional badge."""
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    st.html(f'<div class="section-header"><span>{icon} {title}</span>{badge_html}</div>')


def champion_banner(model_name: str, auc: float, task: str = "Churn Prediction"):
    """Render a champion model highlight banner as a flat HTML string."""
    html = (
        f'<div class="champion-banner">'
        f'<div class="trophy">🏆</div>'
        f'<div>'
        f'<h3>Champion Model: {model_name}</h3>'
        f'<p>{task} · ROC-AUC: <strong>{auc*100:.1f}%</strong></p>'
        f'</div>'
        f'</div>'
    )
    st.html(html)


def glass_card(content_html: str):
    """Wrap arbitrary HTML in a glassmorphism card as a flat HTML string."""
    st.html(f'<div class="glass-card">{content_html}</div>')

