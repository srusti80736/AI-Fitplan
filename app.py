import streamlit as st
import streamlit.components.v1 as components
import json
import re
from prompt_builder import build_prompt, build_adjustment_prompt 
from model_api import query_model 
from diet_builder import build_diet_prompt
from auth import generate_otp, create_jwt, verify_jwt, hash_password, verify_password
from database import init_database, user_exists, register_user, get_user_by_email, update_user_profile
from email_utils import send_otp_email  
from dotenv import load_dotenv

load_dotenv()
init_database()

st.set_page_config(page_title="FitPlan AI", layout="wide", page_icon="⚡")

# --- MASTER UI STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    /* ── RESET ── */
    header { visibility: hidden; }
    #MainMenu, footer { visibility: hidden; }
    * { box-sizing: border-box; }

    /* ── LIGHT BASE ── */
    .stApp {
        background-color: #F5F0E8;
        background-image:
            radial-gradient(ellipse 70% 50% at 10% 0%, rgba(180,120,80,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 90% 100%, rgba(160,100,60,0.06) 0%, transparent 55%);
        background-attachment: fixed;
        font-family: 'DM Sans', sans-serif;
        color: #1A1410;
    }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1410 0%, #2A1F18 100%) !important;
        border-right: 1px solid rgba(200,160,100,0.2) !important;
    }
    section[data-testid="stSidebar"] * { color: #D4C4A8 !important; }
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid rgba(200,160,100,0.25) !important;
        color: #C8A064 !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
        padding: 10px 16px !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(200,160,100,0.1) !important;
        border-color: #C8A064 !important;
        color: #E8C87A !important;
        transform: translateX(4px) !important;
    }

    /* ── GLOBAL BUTTONS ── */
    .stButton > button {
        background: #1A1410 !important;
        color: #F5F0E8 !important;
        font-family: 'DM Mono', monospace !important;
        font-weight: 500 !important;
        font-size: 11px !important;
        letter-spacing: 2.5px !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 14px 32px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 12px rgba(26,20,16,0.2) !important;
    }
    .stButton > button:hover {
        background: #2A1F18 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(26,20,16,0.3) !important;
    }

    /* ── LOGIN PAGE BUTTONS (HIGHER SPECIFICITY) ── */
    .stTabs [data-baseweb="tab-panel"] .stButton > button,
    .stTabs .stButton > button {
        color: #FFFFFF !important;
        background: #1A1410 !important;
        border: 2px solid #C8A064 !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-panel"] .stButton > button:hover,
    .stTabs .stButton > button:hover {
        color: #FFFFFF !important;
        background: #2A1F18 !important;
        border-color: #E8C87A !important;
    }

    /* ── INPUTS ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: #FFFFFF !important;
        border: 1px solid rgba(26,20,16,0.25) !important;
        border-radius: 4px !important;
        color: #1A1410 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9A8070 !important;
        opacity: 0.8 !important;
    }
    
    .stNumberInput > div > div > input::placeholder {
        color: #9A8070 !important;
        opacity: 0.8 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stMultiSelect > div > div:focus {
        border-color: #C8A064 !important;
        box-shadow: 0 0 0 3px rgba(200,160,100,0.2) !important;
        outline: none !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background: #FFFFFF !important;
    }
    
    .stSelectbox [role="listbox"] {
        background: #FFFFFF !important;
    }
    
    .stMultiSelect [data-baseweb="multi_select"] input {
        color: #1A1410 !important;
    }
    
    label {
        color: #3A2A1A !important;
        font-size: 11px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        font-family: 'DM Mono', monospace !important;
        font-weight: 600 !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] button {
        color: #1A1410 !important;
        font-weight: 700 !important;
        background: transparent !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #C8A064 !important;
        background: rgba(200,160,100,0.1) !important;
    }
    
    .stTabs p {
        color: #1A1410 !important;
    }

    /* ── TAB CONTENT AND BUTTONS ── */
    .stTabs [data-baseweb="tab-panel"] {
        background: #F5F0E8 !important;
    }

    .stTabs [data-baseweb="tab-panel"] * {
        color: #1A1410 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] .stMarkdown,
    .stTabs [data-baseweb="tab-panel"] .stText {
        color: #1A1410 !important;
    }

    /* Buttons inside tabs */
    .stTabs [data-baseweb="tab-panel"] .stButton > button {
        background: #1A1410 !important;
        color: #FFFFFF !important;
        border: 2px solid #C8A064 !important;
        font-weight: 600 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .stTabs [data-baseweb="tab-panel"] .stButton > button:hover {
        background: #2A1F18 !important;
        color: #FFFFFF !important;
        border-color: #E8C87A !important;
    }

    /* Ensure all text in buttons is visible */
    .stTabs [data-baseweb="tab-panel"] button div {
        color: #FFFFFF !important;
    }

    /* ── ALERTS / MESSAGES ── */
    .stAlert {
        color: #1A1410 !important;
        background: rgba(245,240,232,0.9) !important;
        border: 1px solid #C8A064 !important;
        border-radius: 6px !important;
    }
    
    .stSuccess {
        color: #1A1410 !important;
        background: rgba(200,160,100,0.1) !important;
        border-color: #C8A064 !important;
    }
    
    .stError {
        color: #1A1410 !important;
        background: rgba(220,53,69,0.1) !important;
        border-color: #DC3545 !important;
    }

    /* ── DROPDOWN / SELECT OPTIONS ── */
    [data-baseweb="select"] div {
        color: #1A1410 !important;
    }
    
    [data-baseweb="menu"] li {
        color: #1A1410 !important;
    }
    
    /* ── SUCCESS / ERROR MESSAGES ── */
    .stSuccess, .stError, .stWarning, .stInfo {
        color: #1A1410 !important;
    }

    /* ══ SPLASH SCREEN ══ */
    .splash-overlay {
        position: fixed;
        inset: 0;
        z-index: 9999;
        background: #1A0A0A;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        animation: splashExit 0.8s ease-in-out 3.8s forwards;
    }
    @keyframes splashExit {
        0%   { opacity: 1; transform: scale(1); pointer-events: auto; }
        100% { opacity: 0; transform: scale(1.04); pointer-events: none; visibility: hidden; }
    }

    /* Film grain */
    .splash-grain {
        position: absolute;
        inset: -50%;
        width: 200%; height: 200%;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
        opacity: 0.055;
        animation: grainShift 0.1s steps(1) infinite;
        pointer-events: none;
        z-index: 1;
        mix-blend-mode: overlay;
    }
    @keyframes grainShift {
        0%  { transform: translate(0,0) rotate(0deg); }
        20% { transform: translate(-3%,2%) rotate(0.5deg); }
        40% { transform: translate(2%,-3%) rotate(-0.3deg); }
        60% { transform: translate(-2%,3%) rotate(0.4deg); }
        80% { transform: translate(3%,-1%) rotate(-0.5deg); }
    }

    /* Poster background */
    .splash-bg {
        position: absolute;
        inset: 0;
        background:
            radial-gradient(ellipse 130% 100% at 65% 50%, #8B1818 0%, #5A0808 30%, #200505 65%, #0D0303 100%);
    }
    .splash-bg::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(125deg, transparent 25%, rgba(255,180,150,0.05) 50%, transparent 72%);
    }

    /* Floating big title */
    .splash-title {
        position: relative;
        z-index: 2;
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-weight: 900;
        font-style: italic;
        color: #F0E6DC;
        line-height: 0.88;
        letter-spacing: -1px;
        animation: titleFloat 5s ease-in-out infinite, titleReveal 1.4s cubic-bezier(0.16,1,0.3,1) forwards;
        opacity: 0;
        text-shadow: 0 8px 80px rgba(0,0,0,0.7);
    }
    .splash-title .t1 {
        display: block;
        font-size: clamp(68px, 12vw, 160px);
        color: #F0E2D8;
    }
    .splash-title .t2 {
        display: block;
        font-size: clamp(36px, 6vw, 80px);
        color: rgba(220,180,130,0.65);
        font-weight: 400;
        letter-spacing: 6px;
        margin: 8px 0;
    }
    .splash-title .t3 {
        display: block;
        font-size: clamp(68px, 12vw, 160px);
        color: #F0E2D8;
    }

    @keyframes titleFloat {
        0%, 100% { transform: translateY(0) rotate(-0.2deg); }
        50%       { transform: translateY(-12px) rotate(0.2deg); }
    }
    @keyframes titleReveal {
        from { opacity: 0; transform: translateY(60px) scale(0.94); filter: blur(8px); }
        to   { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
    }

    .splash-year {
        position: absolute;
        top: 36px; right: 44px;
        z-index: 3;
        font-family: 'Playfair Display', serif;
        font-size: 16px;
        font-weight: 700;
        color: rgba(220,180,130,0.4);
        letter-spacing: 4px;
        writing-mode: vertical-rl;
        animation: fadeUp 1.2s ease 0.8s forwards;
        opacity: 0;
    }
    .splash-sub {
        position: relative;
        z-index: 2;
        margin-top: 36px;
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        letter-spacing: 6px;
        color: rgba(200,160,100,0.6);
        text-transform: uppercase;
        animation: fadeUp 1.2s ease 1.2s forwards;
        opacity: 0;
    }
    .splash-skip {
        position: absolute;
        bottom: 52px;
        z-index: 3;
        font-family: 'DM Mono', monospace;
        font-size: 9px;
        letter-spacing: 4px;
        color: rgba(200,160,100,0.45);
        text-transform: uppercase;
        cursor: pointer;
        border: 1px solid rgba(200,160,100,0.18);
        padding: 9px 22px;
        border-radius: 2px;
        background: transparent;
        transition: all 0.3s ease;
        animation: fadeUp 1s ease 1.8s forwards;
        opacity: 0;
    }
    .splash-skip:hover {
        color: rgba(220,180,130,0.9);
        border-color: rgba(200,160,100,0.45);
        background: rgba(200,160,100,0.06);
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── SECTION HEADINGS ── */
    .section-title {
        font-family: 'Playfair Display', serif;
        font-size: 48px;
        font-weight: 900;
        font-style: italic;
        color: #1A1410;
        position: relative;
        display: inline-block;
        animation: slideInLeft 0.6s ease forwards;
        line-height: 1;
    }
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -8px; left: 0;
        width: 50%; height: 2px;
        background: linear-gradient(90deg, #C8A064, transparent);
        border-radius: 2px;
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    /* ── LOGIN ── */
    .login-logo {
        font-family: 'Playfair Display', serif;
        font-size: 58px;
        font-weight: 900;
        font-style: italic;
        color: #1A1410;
        text-align: center;
        margin-bottom: 6px;
    }
    .login-sub {
        text-align: center;
        font-family: 'DM Mono', monospace;
        font-size: 9px;
        letter-spacing: 4px;
        color: #A09080;
        text-transform: uppercase;
        margin-bottom: 40px;
    }

    /* ── STAT CARDS ── */
    .stat-card {
        background: #FFFFFF;
        border: 1px solid rgba(26,20,16,0.08);
        border-radius: 8px;
        padding: 28px 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 2px 16px rgba(26,20,16,0.06);
        min-width: 160px; /* ensure wider box for longer names */
    }
    @keyframes shimmer {
        0%   { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .stat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(26,20,16,0.12); }
    .stat-val-big {
        font-family: 'Playfair Display', serif;
        font-size: 42px; font-weight: 900;
        color: #1A1410; line-height: 1.1; margin-bottom: 4px;
        white-space: normal !important;
        word-break: break-word;
    }
    .stat-label-big {
        font-family: 'DM Mono', monospace;
        font-size: 9px; letter-spacing: 3px; color: #A09080; text-transform: uppercase;
    }

    /* ── ASSESSMENT BANNER ── */
    .assessment-card {
        background: #1A1410; border-radius: 8px;
        padding: 28px 32px; margin-bottom: 32px;
        position: relative; overflow: hidden;
    }
    .assessment-card::before {
        content: ''; position: absolute;
        top: 0; left: 0; bottom: 0; width: 4px;
        background: linear-gradient(180deg, #C8A064, #E8D4A0);
    }
    .assessment-card h2 {
        font-family: 'Playfair Display', serif;
        font-size: 34px; font-weight: 900; font-style: italic;
        color: #F5F0E8; margin-bottom: 6px;
    }
    .assessment-card p {
        font-family: 'DM Mono', monospace;
        font-size: 10px; letter-spacing: 2px; color: #C8A064; text-transform: uppercase;
    }

    /* ── DAY / PLAN CARDS ── */
    .day-container {
        background: #FFFFFF;
        border: 1px solid rgba(26,20,16,0.08); border-radius: 8px;
        padding: 32px; margin-bottom: 20px;
        transition: box-shadow 0.3s ease, transform 0.3s ease;
        box-shadow: 0 2px 12px rgba(26,20,16,0.05);
        animation: cardRise 0.7s cubic-bezier(0.16,1,0.3,1) both;
    }
    @keyframes cardRise {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .day-container:hover { box-shadow: 0 8px 32px rgba(26,20,16,0.1); transform: translateY(-2px); }
    .day-container:nth-child(1) { animation-delay: 0.05s; }
    .day-container:nth-child(2) { animation-delay: 0.10s; }
    .day-container:nth-child(3) { animation-delay: 0.15s; }
    .day-container:nth-child(4) { animation-delay: 0.20s; }
    .day-container:nth-child(5) { animation-delay: 0.25s; }

    .day-header {
        font-family: 'Playfair Display', serif;
        font-size: 26px; font-weight: 700; font-style: italic; color: #1A1410;
        margin-bottom: 20px; padding-bottom: 14px;
        border-bottom: 1px solid rgba(26,20,16,0.08);
        display: flex; align-items: center; gap: 12px;
    }
    .item-row {
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 0; border-bottom: 1px solid rgba(26,20,16,0.05);
        transition: padding-left 0.2s ease;
    }
    .item-row:last-child { border-bottom: none; }
    .item-row:hover { padding-left: 8px; }
    .ex-name {
        flex: 2; font-weight: 500; color: #2A1F18; font-size: 14px;
        font-family: 'DM Sans', sans-serif; display: flex; align-items: center; gap: 10px;
    }
    .ex-bullet {
        display: inline-block; width: 5px; height: 5px;
        background: #C8A064; border-radius: 50%; flex-shrink: 0;
    }
    .stat-group { display: flex; gap: 8px; flex: 1.5; justify-content: flex-end; }
    .stat-pill {
        text-align: center; min-width: 70px;
        background: #F5F0E8; padding: 8px 10px; border-radius: 4px;
        border: 1px solid rgba(26,20,16,0.08); transition: all 0.2s ease;
    }
    .stat-pill:hover { background: #EDE4D4; border-color: #C8A064; }
    .stat-val {
        color: #1A1410; font-weight: 600; font-size: 12px; display: block;
        font-family: 'DM Mono', monospace;
    }
    .stat-label {
        font-size: 8px; color: #A09080; text-transform: uppercase;
        letter-spacing: 1px; display: block; margin-top: 2px; font-family: 'DM Mono', monospace;
    }

    /* ── SIDEBAR LOGO ── */
    .sidebar-logo {
        font-family: 'Playfair Display', serif;
        font-size: 28px; font-weight: 900; font-style: italic; color: #F5F0E8 !important; margin-bottom: 4px;
    }
    .sidebar-user {
        font-family: 'DM Mono', monospace; font-size: 9px; color: #6A5A4A !important;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;
    }

    /* ── DIVIDERS ── */
    .neon-divider {
        height: 1px; background: linear-gradient(90deg, transparent, rgba(200,160,100,0.4), transparent);
        border: none; margin: 20px 0;
    }
    .light-divider {
        height: 1px; background: linear-gradient(90deg, transparent, rgba(26,20,16,0.15), transparent);
        border: none; margin: 24px 0;
    }

    /* ── DOWNLOAD ── */
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid rgba(26,20,16,0.25) !important;
        color: #1A1410 !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 10px !important; letter-spacing: 2px !important;
        border-radius: 4px !important; box-shadow: none !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(26,20,16,0.04) !important; border-color: #C8A064 !important;
    }

    .stAlert { border-radius: 6px !important; }

    .badge-pulse {
        display: inline-block; background: #1A1410; color: #C8A064;
        font-family: 'DM Mono', monospace; font-size: 9px;
        letter-spacing: 3px; text-transform: uppercase; padding: 5px 14px; border-radius: 2px;
    }
    .tagline {
        font-family: 'DM Mono', monospace; font-size: 10px;
        letter-spacing: 4px; color: #A09080; text-transform: uppercase; margin-top: 8px;
    }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #F5F0E8; }
    ::-webkit-scrollbar-thumb { background: rgba(26,20,16,0.15); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #C8A064; }
    .stSpinner > div { border-top-color: #C8A064 !important; }
    </style>

    <!-- SPLASH SCREEN -->
    <div class="splash-overlay" id="splashScreen">
        <div class="splash-bg"></div>
        <div class="splash-grain"></div>
        <div class="splash-year">2026</div>
        <div class="splash-title">
            <span class="t1">Personalised</span>
            <span class="t2">— fitness —</span>
            <span class="t3">Plan</span>
        </div>
        <div class="splash-sub">Intelligence · Performance · Results</div>
        <button class="splash-skip" onclick="skipSplash()">Enter &rarr;</button>
    </div>

    <script>
    function skipSplash() {
        var s = document.getElementById('splashScreen');
        if (!s) return;
        s.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        s.style.opacity = '0';
        s.style.transform = 'scale(1.04)';
        s.style.pointerEvents = 'none';
        setTimeout(function(){ s.style.display = 'none'; }, 620);
    }
    setTimeout(skipSplash, 3800);
    </script>
""", unsafe_allow_html=True)


# --- UTILITY FUNCTIONS ---
def parse_plan_to_json(text):
    sections = []
    parts = re.split(r'(Day \d+:.*)', text)
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            content = parts[i+1].strip()
            items = []
            for line in content.split('\n'):
                if line.strip().startswith(('-', '*')):
                    main_part = line.strip('- *').split('|')[0].split(':')[0].strip()
                    items.append({
                        "name": main_part,
                        "val1": "3 sets",
                        "val2": "10 reps",
                        "val3": "60s"
                    })
            sections.append({"header": header, "items": items})
    return sections

def parse_diet_plan(text):
    """Parse dietary plan to extract days and meals with time, calories, and dishes."""
    days_data = []
    
    # Split by Day pattern
    day_pattern = r'Day (\d+)'
    day_matches = list(re.finditer(day_pattern, text))
    
    if not day_matches:
        return days_data
    
    for idx, day_match in enumerate(day_matches):
        day_num = int(day_match.group(1))
        
        # Get content until next day or end of text
        content_start = day_match.end()
        content_end = day_matches[idx + 1].start() if idx + 1 < len(day_matches) else len(text)
        day_content = text[content_start:content_end].strip()
        
        meals = []
        meal_names = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        
        # Split content by newlines and process each line
        for line in day_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains a meal name
            meal_name = None
            for name in meal_names:
                if name.lower() in line.lower():
                    meal_name = name
                    break
            
            if meal_name:
                # Remove meal name from the start
                meal_content = re.sub(rf'^{meal_name}[:\-\s]*', '', line, flags=re.IGNORECASE).strip()
                
                # Extract time from parentheses or standalone time pattern
                time = "--:--"
                time_match = re.search(r'\(?(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\)?', meal_content)
                if not time_match:
                    time_match = re.search(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b', meal_content)
                    
                if time_match:
                    time = time_match.group(1).strip()
                
                # Extract calories - look for pattern: comma, space, number (with or without kcal)
                calories = "-- kcal"
                cal_match = re.search(r',\s*(\d+)\s*(?:kcal|cal|calories)?', meal_content, re.IGNORECASE)
                if cal_match:
                    cal_value = cal_match.group(1)
                    calories = f"{cal_value} kcal"
                
                # Extract dish name
                dish = meal_content
                
                # Clean up
                dish = re.sub(r'\(?(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\)?', '', dish)
                dish = re.sub(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b', '', dish)
                dish = re.sub(r',\s*\d+\s*(?:kcal|cal|calories)?', '', dish, flags=re.IGNORECASE)
                dish = re.sub(r'Meal\s+Name\s*:\s*', '', dish, flags=re.IGNORECASE)
                dish = re.sub(r'[\-\|]', '', dish)
                dish = ' '.join(dish.split()).strip()
                dish = dish.rstrip(',-:')
                
                if len(dish) > 30:
                    words = [w for w in dish.split() if len(w) > 1]
                    dish = ' '.join(words[:3])
                
                if dish and dish.lower() not in ['', 'none', 'n/a']:
                    meals.append({
                        "meal": meal_name,
                        "time": time,
                        "calories": calories,
                        "dish": dish
                    })
        
        if meals:
            days_data.append({
                "day": day_num,
                "meals": meals
            })
    
    return days_data[:5]

def render_diet_cards(diet_data):
    """Render dietary plan as cards with Day, Time, Calories, and Dish."""
    for day_info in diet_data:
        day_num = day_info["day"]
        st.markdown(f"""
        <div class="day-container">
            <div class="day-header">◆ Day {day_num}</div>
        """, unsafe_allow_html=True)
        
        for meal in day_info["meals"]:
            st.markdown(f"""
            <div class="item-row">
                <div class="ex-name"><span class="ex-bullet"></span>{meal['meal']}</div>
                <div class="stat-group">
                    <div class="stat-pill"><span class="stat-val">{meal['time']}</span><span class="stat-label">TIME</span></div>
                    <div class="stat-pill"><span class="stat-val">{meal['calories']}</span><span class="stat-label">CALORIES</span></div>
                    <div class="stat-pill" title="{meal['dish']}"><span class="stat-val">{meal['dish']}</span><span class="stat-label">DISH</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)


def parse_diet_plan(text):
    """Parse dietary plan to extract days and meals with time, calories, and dishes."""
    days_data = []
    
    # Split by Day pattern
    day_pattern = r'Day (\d+)'
    day_matches = list(re.finditer(day_pattern, text))
    
    if not day_matches:
        return days_data
    
    for idx, day_match in enumerate(day_matches):
        day_num = int(day_match.group(1))
        
        # Get content until next day or end of text
        content_start = day_match.end()
        content_end = day_matches[idx + 1].start() if idx + 1 < len(day_matches) else len(text)
        day_content = text[content_start:content_end].strip()
        
        meals = []
        meal_names = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        
        # Split content by newlines and process each line
        for line in day_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains a meal name
            meal_name = None
            for name in meal_names:
                if name.lower() in line.lower():
                    meal_name = name
                    break
            
            if meal_name:
                # Remove meal name from the start
                meal_content = re.sub(rf'^{meal_name}[:\-\s]*', '', line, flags=re.IGNORECASE).strip()
                
                # Extract time from parentheses or standalone time pattern
                time = "--:--"
                time_match = re.search(r'\(?(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\)?', meal_content)
                if time_match:
                    time = time_match.group(1).strip()
                
                # Extract calories - look for pattern: comma, space, number (with or without kcal)
                # Pattern like: "Something, 500" or "Something, 500 kcal"
                calories = "-- kcal"
                cal_match = re.search(r',\s*(\d+)\s*(?:kcal|cal|calories)?', meal_content, re.IGNORECASE)
                if cal_match:
                    cal_value = cal_match.group(1)
                    calories = f"{cal_value} kcal"
                
                # Extract dish name - remove everything except the main dish description
                dish = meal_content
                
                # Remove time patterns
                dish = re.sub(r'\(?(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\)?', '', dish)
                
                # Remove calories (with or without kcal keyword)
                dish = re.sub(r',\s*\d+\s*(?:kcal|cal|calories)?', '', dish, flags=re.IGNORECASE)
                
                # Remove "Meal Name:" prefix if it exists
                dish = re.sub(r'Meal\s+Name\s*:\s*', '', dish, flags=re.IGNORECASE)
                
                # Remove extra punctuation and spaces
                dish = re.sub(r'[\-\|]', '', dish)
                dish = ' '.join(dish.split())
                dish = dish.strip()
                
                # Remove trailing comma or special chars
                dish = dish.rstrip(',-:')
                
                # Limit to first meaningful words
                if len(dish) > 30:
                    words = [w for w in dish.split() if len(w) > 1]
                    dish = ' '.join(words[:3])
                
                if dish and dish.lower() not in ['', 'none', 'n/a']:
                    meals.append({
                        "meal": meal_name,
                        "time": time,
                        "calories": calories,
                        "dish": dish
                    })
        
        if meals:
            days_data.append({
                "day": day_num,
                "meals": meals
            })
    
    return days_data[:5]  # Limit to 5 days


def render_diet_cards(diet_data):
    """Render dietary plan as cards with Day, Time, Calories, and Dish."""
    for day_info in diet_data:
        day_num = day_info["day"]
        st.markdown(f"""
        <div class="day-container">
            <div class="day-header">◆ Day {day_num}</div>
        """, unsafe_allow_html=True)
        
        for meal in day_info["meals"]:
            st.markdown(f"""
            <div class="item-row">
                <div class="ex-name"><span class="ex-bullet"></span>{meal['meal']}</div>
                <div class="stat-group">
                    <div class="stat-pill"><span class="stat-val">{meal['time']}</span><span class="stat-label">TIME</span></div>
                    <div class="stat-pill"><span class="stat-val">{meal['calories']}</span><span class="stat-label">CALORIES</span></div>
                    <div class="stat-pill" title="{meal['dish']}"><span class="stat-val">{meal['dish']}</span><span class="stat-label">DISH</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_cards(data, label1, label2, label3):
    for section in data:
        # Check if this is a rest day
        is_rest_day = 'rest day' in section['header'].lower() or (len(section['items']) == 1 and 'rest' in section['items'][0]['name'].lower())
        
        if is_rest_day:
            st.markdown(f"""
            <div class="day-container" style="border-color: rgba(0,255,100,0.3); background: rgba(0,255,100,0.05);">
                <div class="day-header" style="color: #00FF64;">🛋️ {section['header']}</div>
                <div style="text-align: center; padding: 40px 20px; color: #8AA898; font-style: italic;">
                    Take it easy today! Focus on recovery, light stretching, or active rest activities like walking.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="day-container">
                <div class="day-header">◆ {section['header']}</div>
            """, unsafe_allow_html=True)
            for item in section['items']:
                st.markdown(f"""
                <div class="item-row">
                    <div class="ex-name"><span class="ex-bullet"></span>{item['name']}</div>
                    <div class="stat-group">
                        <div class="stat-pill"><span class="stat-val">{item['val1']}</span><span class="stat-label">{label1}</span></div>
                        <div class="stat-pill"><span class="stat-val">{item['val2']}</span><span class="stat-label">{label2}</span></div>
                        <div class="stat-pill"><span class="stat-val">{item['val3']}</span><span class="stat-label">{label3}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# --- SESSION STATE ---
for key, val in [("otp", None), ("authenticated", False), ("token", None),
                 ("user_email", None),
                 ("page", "dashboard"), ("user_data", None),
                 ("workout_plan", None), ("diet_plan", None),
                 ("edit_mode", False),
                 ("temp_signup_name", None), ("temp_signup_email", None), ("temp_signup_password", None)]:
    if key not in st.session_state:
        st.session_state[key] = val


# ══════════════════════════════════════════
# PHASE 1: LOGIN
# ══════════════════════════════════════════
if not st.session_state.authenticated:
    st.markdown("""
        <div style='text-align:center; padding: 60px 0 0;'>
            <div class='login-logo'>FitPlan AI</div>
            <div class='login-sub'>⚡ Intelligence-Powered Fitness ⚡</div>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        # Toggle between Sign In and Sign Up
        tab1, tab2 = st.tabs(["SIGN IN", "SIGN UP"])
        
        # ═══════════════════════════════════════
        # SIGN IN TAB
        # ═══════════════════════════════════════
        with tab1:
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            signin_email = st.text_input("Email Address", placeholder="your@email.com", key="signin_email", label_visibility="collapsed")
            signin_password = st.text_input("Password", placeholder="Enter your password", type="password", key="signin_password", label_visibility="collapsed")
            
            if st.button("🔓 Sign In →", use_container_width=True, key="signin_btn"):
                if signin_email and signin_password:
                    user = get_user_by_email(signin_email)
                    if user and verify_password(signin_password, user["password_hash"]):
                        st.session_state.token = create_jwt(user["email"], user["name"])
                        st.session_state.authenticated = True
                        st.session_state.user_email = user["email"]
                        # load profile if exists and attach email
                        if user.get("profile"):
                            profile = user["profile"]
                            profile["email"] = user["email"]
                            st.session_state.user_data = profile
                        st.success("✓ Welcome back!")
                        st.rerun()
                    else:
                        st.error("✗ Invalid email or password")
                else:
                    st.error("Please enter both email and password")
        
        # ═══════════════════════════════════════
        # SIGN UP TAB
        # ═══════════════════════════════════════
        with tab2:
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            signup_name = st.text_input("Full Name", placeholder="Your full name", key="signup_name", label_visibility="collapsed")
            signup_email = st.text_input("Email Address", placeholder="your@email.com", key="signup_email", label_visibility="collapsed")
            signup_password = st.text_input("Password", placeholder="Create a password", type="password", key="signup_password", label_visibility="collapsed")
            
            if st.button("📧 Send OTP →", use_container_width=True, key="otp_btn"):
                if signup_name and signup_email and signup_password:
                    if user_exists(signup_email):
                        st.error("✗ Email already registered")
                    else:
                        otp = generate_otp()
                        st.session_state.otp = otp
                        st.session_state.temp_signup_name = signup_name
                        st.session_state.temp_signup_email = signup_email
                        st.session_state.temp_signup_password = signup_password
                        try:
                            send_otp_email(signup_email, otp)
                            st.success("✓ OTP sent to your email")
                            st.info(f"*(For testing, since emails are delayed: The OTP is **{otp}**)*")
                        except Exception as e:
                            st.error(f"✗ Email delivery failed: {str(e)}")
                else:
                    st.error("Please fill all fields")
            
            if st.session_state.otp and st.session_state.temp_signup_email:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                otp_in = st.text_input("OTP Code", placeholder="6-digit code", type="password", key="otp_input", label_visibility="collapsed")
                if st.button("✅ Complete Sign Up →", use_container_width=True, key="verify_btn"):
                    if str(otp_in).strip() == str(st.session_state.otp).strip():
                        # Register the user
                        password_hash = hash_password(st.session_state.temp_signup_password)
                        if register_user(st.session_state.temp_signup_name, st.session_state.temp_signup_email, password_hash):
                            st.session_state.token = create_jwt(st.session_state.temp_signup_email, st.session_state.temp_signup_name)
                            st.session_state.authenticated = True
                            st.session_state.user_email = st.session_state.temp_signup_email
                            # Clear temp data
                            st.session_state.otp = None
                            st.session_state.temp_signup_name = None
                            st.session_state.temp_signup_email = None
                            st.session_state.temp_signup_password = None
                            st.success("✓ Account created successfully!")
                            st.rerun()
                        else:
                            st.error("✗ Registration failed")
                    else:
                        st.error("✗ Invalid OTP code")


# ══════════════════════════════════════════
# PHASE 2: MAIN APP
# ══════════════════════════════════════════
else:
    decoded = verify_jwt(st.session_state.token)
    if not decoded:
        st.session_state.authenticated = False
        st.error("Session expired. Please log in again.")
        st.rerun()

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown(f"""
            <div class='sidebar-logo'>FitPlan AI</div>
            <div class='sidebar-user'>◈ {decoded['email']}</div>
        """, unsafe_allow_html=True)
        st.markdown("<hr class='neon-divider'>", unsafe_allow_html=True)

        if st.button("◈ Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"; st.rerun()
        if st.button("◈ Workout Plan", use_container_width=True):
            st.session_state.page = "result" if st.session_state.workout_plan else "input"; st.rerun()
        if st.button("◈ Dietary Plan", use_container_width=True):
            st.session_state.page = "diet"; st.rerun()

        st.markdown("<hr class='neon-divider'>", unsafe_allow_html=True)

        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.page = "input"
            st.session_state.edit_mode = True
            st.rerun()
        if st.button("⏻ Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.otp = None; st.rerun()

    # ══ DASHBOARD ══
    if st.session_state.page == "dashboard":
        st.markdown("""
            <div style='padding:20px 0 10px;'>
                <div style='font-family:"Playfair Display",serif;font-size:clamp(52px,8vw,96px);font-weight:900;font-style:italic;color:#1A1410;line-height:0.9;'>
                    Your<br><span style="color:#C8A064;">Command</span><br>Centre
                </div>
                <div class='tagline' style='margin-top:16px;'>— powered by ai · built for athletes</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr class='light-divider'>", unsafe_allow_html=True)

        if st.session_state.user_data:
            d = st.session_state.user_data
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="stat-card"><div class="stat-val-big">{d["name"][:6]}</div><div class="stat-label-big">Athlete</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat-card"><div class="stat-val-big">{d["bmi"]:.1f}</div><div class="stat-label-big">BMI Index</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-card"><div class="stat-val-big" style="color:{d["color"]};font-size:30px;">{d["status"]}</div><div class="stat-label-big">Status</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="stat-card"><div class="stat-val-big">✓</div><div class="stat-label-big">{d["goal"]}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # 🏆 PROGRESS & XP SYSTEM 🏆
            total_xp = 0
            history = d.get("workout_history", [])
            if history:
                total_xp = sum([entry.get("xp", 100) for entry in history])
                
            level = (total_xp // 500) + 1
            progress_to_next = total_xp % 500
            progress_percent = progress_to_next / 500.0
            
            st.markdown(f"""
                <div style='background:#FFFFFF; border:1px solid rgba(26,20,16,0.08); border-radius:8px; padding:24px 32px; box-shadow:0 2px 12px rgba(26,20,16,0.05); margin-bottom: 24px;'>
                    <h3 style='margin:0 0 10px 0; color:#1A1410;'>🏆 Athlete Level {level}</h3>
                    <p style='color:#6A5A4A; font-family:"DM Mono", monospace; font-size:14px; margin:0 0 15px 0;'>Total Experience: {total_xp} XP</p>
            """, unsafe_allow_html=True)
            
            st.progress(progress_percent)
            st.markdown(f"<p style='font-size:12px; color:#A09080; text-align:right; margin-top:5px;'>{500 - progress_to_next} XP to Level {level + 1}</p></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid rgba(26,20,16,0.08);border-radius:8px;padding:28px 32px;box-shadow:0 2px 12px rgba(26,20,16,0.05);'>
                    <span class='badge-pulse'>Active Plan</span>
                    <p style='font-family:DM Sans,sans-serif;color:#6A5A4A;margin-top:16px;font-size:15px;line-height:1.8;'>
                        Your personalised AI fitness program is live. Navigate using the sidebar to view 
                        your <strong style='color:#1A1410'>Workout Plan</strong> or 
                        <strong style='color:#C8A064'>Dietary Plan</strong>.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='section-title' style='font-size:24px;'>Daily Intel Check-In</div>", unsafe_allow_html=True)
            check_in_text = st.text_input("How are you feeling today?", placeholder="E.g. My legs are super sore, or I only slept 4 hours...", label_visibility="collapsed")
            if st.button("⚡ Sync & Adjust Plan", use_container_width=True):
                if check_in_text and st.session_state.workout_plan:
                    with st.spinner("Analyzing biometric feedback and adjusting your plan..."):
                        adj_prompt = build_adjustment_prompt(st.session_state.workout_plan, check_in_text)
                        st.session_state.workout_plan = query_model(adj_prompt)
                        st.session_state.user_data["workout_plan"] = st.session_state.workout_plan
                        if st.session_state.authenticated and st.session_state.user_email:
                            update_user_profile(st.session_state.user_email, st.session_state.user_data)
                        st.success("✓ Plan updated in real-time based on your feedback!")
                elif not st.session_state.workout_plan:
                    st.error("Generate a workout plan first to use the AI Coach!")
                else:
                    st.error("Please enter your current condition.")
        else:
            st.markdown("""
                <div style='text-align:center;padding:80px 40px;'>
                    <div style='font-family:"Playfair Display",serif;font-size:72px;font-weight:900;font-style:italic;color:rgba(26,20,16,0.06);'>No Data Yet</div>
                    <p style='font-family:"DM Mono",monospace;font-size:10px;letter-spacing:3px;color:#A09080;text-transform:uppercase;margin-top:-12px;'>
                        Generate a workout plan to see your stats
                    </p>
                </div>
            """, unsafe_allow_html=True)

    # ══ INPUT ══
    elif st.session_state.page == "input":
        if st.session_state.edit_mode:
            st.markdown("<div class='section-title'>Edit Your Profile</div>", unsafe_allow_html=True)
            st.markdown("<div class='tagline' style='margin-bottom:32px;margin-top:12px;'>— update your information</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='section-title'>Build Your Profile</div>", unsafe_allow_html=True)
            st.markdown("<div class='tagline' style='margin-bottom:32px;margin-top:12px;'>— tell us about yourself</div>", unsafe_allow_html=True)

        # Get existing data for editing
        existing_data = st.session_state.user_data if st.session_state.edit_mode and st.session_state.user_data else {}
        
        with st.container():
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1: name = st.text_input("Full Name", value=existing_data.get("name", ""))
            with c2: gender = st.selectbox("Gender", ["Male", "Female"], 
                                         index=["Male", "Female"].index(existing_data.get("gender", "Male")) if existing_data.get("gender") in ["Male", "Female"] else 0)
            with c3: age = st.number_input("Age", min_value=1, value=int(existing_data.get("age", 19)))

            h, w = st.columns(2)
            with h: height = st.number_input("Height (cm)", value=float(existing_data.get("height", 170.0)))
            with w: weight = st.number_input("Weight (kg)", value=float(existing_data.get("weight", 70.0)))

            goal = st.selectbox("Training Goal", ["Build Muscle", "Weight Loss", "Strength", "Flexibility"],
                              index=["Build Muscle", "Weight Loss", "Strength", "Flexibility"].index(existing_data.get("goal", "Build Muscle")) if existing_data.get("goal") in ["Build Muscle", "Weight Loss", "Strength", "Flexibility"] else 0)
            level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"],
                               index=["Beginner", "Intermediate", "Advanced"].index(existing_data.get("level", "Beginner")) if existing_data.get("level") in ["Beginner", "Intermediate", "Advanced"] else 0)
            equip = st.multiselect("Available Equipment",
                ["Dumbbells", "Kettlebells", "Pull-up Bar", "Resistance Bands", "Yoga Mat", "No Equipment"],
                default=existing_data.get("equip", []))

        st.markdown("<br>", unsafe_allow_html=True)
        button_text = "Update Profile →" if st.session_state.edit_mode else "Generate Complete Plan →"
        if st.button(button_text):
            prompt, bmi, status, color = build_prompt(name, gender, age, height, weight, goal, level, equip)
            prompt += "\nFormat: Day X: [Name]\n- [Exercise]: [Sets], [Reps], [Rest]"
            with st.spinner("AI is engineering your plan..."):
                st.session_state.workout_plan = query_model(prompt)
                st.session_state.user_data = {"name": name, "gender": gender, "age": age, "height": height, "weight": weight, 
                                            "bmi": bmi, "status": status, "color": color, "goal": goal, "level": level, "equip": equip}
                # if user logged in, persist profile to DB
                if st.session_state.authenticated and st.session_state.user_email:
                    try:
                        update_user_profile(st.session_state.user_email, st.session_state.user_data)
                    except Exception:
                        pass
                st.session_state.page = "result"
                st.session_state.edit_mode = False  # Reset edit mode
                st.rerun()

    # ══ RESULT ══
    elif st.session_state.page == "result":
        d = st.session_state.user_data
        st.markdown(f"""
            <div class='assessment-card'>
                <h2>◆ {d['name']}'s Program</h2>
                <p>BMI {d['bmi']:.2f} &nbsp;·&nbsp; {d['status']} &nbsp;·&nbsp; {d['goal']}</p>
            </div>
        """, unsafe_allow_html=True)

        st.download_button("↓ Export Workout Plan", st.session_state.workout_plan, file_name="workout_plan.txt")
        st.markdown("<br>", unsafe_allow_html=True)

        plan_json = parse_plan_to_json(st.session_state.workout_plan)
        if plan_json:
            # LIVE WORKOUT LAUNCHER
            st.markdown("""
                <div style='background:rgba(200,160,100,0.05); padding: 20px; border-radius:8px; border:1px solid rgba(200,160,100,0.2); margin-bottom: 20px;'>
                    <h3 style='margin-top:0; color:#1A1410;'>⚡ Live Workout Mode</h3>
                    <p style='color:#6A5A4A; font-size:14px;'>Select a day to enter the immersive tracking environment.</p>
                </div>
            """, unsafe_allow_html=True)
            day_names = [s['header'] for s in plan_json if 'rest' not in s['header'].lower()]
            if day_names:
                col1, col2 = st.columns([3, 1])
                with col1:
                    selected_day = st.selectbox("Select Training Day:", day_names, label_visibility="collapsed")
                with col2:
                    if st.button("START LIVE →", use_container_width=True):
                        st.session_state.current_live_workout = next(s for s in plan_json if s['header'] == selected_day)
                        st.session_state.page = "live_workout"
                        st.rerun()
            st.markdown("<hr class='light-divider'>", unsafe_allow_html=True)

            render_cards(plan_json, "SETS", "REPS", "REST")
        else:
            st.markdown(f"""
                <div class='day-container'>
                    <pre style='color:#6A5A4A;font-family:DM Sans;white-space:pre-wrap;font-size:14px;line-height:1.8;'>
{st.session_state.workout_plan}
                    </pre>
                </div>
                </div>
            """, unsafe_allow_html=True)

    # ══ LIVE WORKOUT TRACKER ══
    elif st.session_state.page == "live_workout":
        day_data = st.session_state.current_live_workout
        st.markdown(f"<div class='section-title'>⚡ {day_data['header']} - Live Server</div>", unsafe_allow_html=True)
        st.markdown("<div class='tagline' style='margin-bottom:32px;margin-top:12px;'>— crush this session</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("← Cancel Stop", use_container_width=True):
                st.session_state.get("workout_just_finished", False)
                st.session_state.page = "result"
                st.rerun()

        st.markdown("<hr class='light-divider'>", unsafe_allow_html=True)
        
        # Real-time Rest Timer using custom HTML/JS
        components.html("""
        <div style="text-align: center; font-family: 'DM Sans', sans-serif; background: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid rgba(26,20,16,0.08);">
            <div style="font-size: 14px; letter-spacing: 2px; color: #A09080; text-transform: uppercase;">Recovery Timer</div>
            <div id="timer" style="font-size: 64px; font-weight: 900; color: #1A1410; margin: 10px 0; font-variant-numeric: tabular-nums;">00:00</div>
            <div>
                <button onclick="startTimer(30)" style="padding: 12px 24px; background: #f4f4f4; color: #1A1410; border: none; border-radius: 8px; cursor: pointer; margin: 5px; font-weight: bold; transition: all 0.2s;">30s Rest</button>
                <button onclick="startTimer(60)" style="padding: 12px 24px; background: #C8A064; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 5px; font-weight: bold; box-shadow: 0 2px 8px rgba(200,160,100,0.4);">60s Rest</button>
                <button onclick="startTimer(90)" style="padding: 12px 24px; background: #1A1410; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 5px; font-weight: bold;">90s Rest</button>
            </div>
            <script>
                let interval;
                function startTimer(duration) {
                    clearInterval(interval);
                    let timer = duration, minutes, seconds;
                    document.getElementById('timer').style.color = '#1A1410';
                    interval = setInterval(function () {
                        minutes = parseInt(timer / 60, 10);
                        seconds = parseInt(timer % 60, 10);
                        minutes = minutes < 10 ? "0" + minutes : minutes;
                        seconds = seconds < 10 ? "0" + seconds : seconds;
                        document.getElementById('timer').textContent = minutes + ":" + seconds;
                        if (--timer < 0) {
                            clearInterval(interval);
                            document.getElementById('timer').textContent = "GO!";
                            document.getElementById('timer').style.color = '#2ecc71';
                        }
                    }, 1000);
                }
            </script>
        </div>
        """, height=220)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📋 Exercise Checklist", unsafe_allow_html=True)
        
        all_done = True
        for idx, item in enumerate(day_data['items']):
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.7); padding: 16px 20px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #C8A064; display: flex; align-items: center;">
                <div style="flex-grow: 1; font-family: 'DM Sans'; font-size: 18px; font-weight: 500; color: #1A1410;">
                    {item['name']}
                </div>
                <div style="font-family: 'DM Mono'; font-size: 14px; color: #6A5A4A; background: #f4f4f4; padding: 4px 12px; border-radius: 20px;">
                    {item['val1']} · {item['val2']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            done = st.checkbox("Mark Completed", key=f"ex_{idx}")
            if not done:
                all_done = False

        st.markdown("<br><hr class='light-divider'>", unsafe_allow_html=True)
        
        if st.session_state.get("workout_just_finished"):
            st.success("🎉 Activity successfully logged to your athlete profile! XP Granted.")
            if st.button("Return to Command Centre →", use_container_width=True):
                st.session_state.workout_just_finished = False
                st.session_state.page = "dashboard"
                st.rerun()
        else:
            if st.button("🏁 Finish Workout & Sync Profile", use_container_width=True):
                if all_done:
                    st.balloons()
                    if "workout_history" not in st.session_state.user_data:
                        st.session_state.user_data["workout_history"] = []
                    import datetime
                    st.session_state.user_data["workout_history"].append({
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "day": day_data['header'],
                        "xp": 100
                    })
                    if st.session_state.authenticated and st.session_state.user_email:
                        update_user_profile(st.session_state.user_email, st.session_state.user_data)
                    st.session_state.workout_just_finished = True
                    st.rerun()
                else:
                    st.warning("⚠️ Please check off all exercises before finishing!")

    # ══ DIET ══
    elif st.session_state.page == "diet":
        st.markdown("<div class='section-title'>Nutrition Protocol</div>", unsafe_allow_html=True)
        st.markdown("<div class='tagline' style='margin-bottom:32px;margin-top:12px;'>— fuel your performance</div>", unsafe_allow_html=True)

        if st.session_state.user_data:
            d = st.session_state.user_data
            st.markdown(f"""
                <div class='assessment-card'>
                    <h2>◆ {d['name']}'s Nutrition Plan</h2>
                    <p>BMI {d['bmi']:.2f} &nbsp;·&nbsp; {d['status']} &nbsp;·&nbsp; {d['goal']}</p>
                </div>
            """, unsafe_allow_html=True)

            if not st.session_state.diet_plan:
                d_prompt = build_diet_prompt(d["name"], "User", 20, 170, 70, d["goal"])
                with st.spinner("Formulating your nutrition plan..."):
                    st.session_state.diet_plan = query_model(d_prompt)

            st.download_button("↓ Export Diet Plan", st.session_state.diet_plan, file_name="diet_plan.txt")
            st.markdown("<br>", unsafe_allow_html=True)

            diet_data = parse_diet_plan(st.session_state.diet_plan)
            if diet_data and len(diet_data[0]["meals"]) > 0:
                render_diet_cards(diet_data)
            else:
                st.markdown(f"""
                    <div class='day-container'>
                        <pre style='color:#6A5A4A;font-family:DM Sans;white-space:pre-wrap;font-size:14px;line-height:1.8;'>
{st.session_state.diet_plan}
                    </pre>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='text-align:center;padding:80px 40px;'>
                    <div style='font-family:"Playfair Display",serif;font-size:56px;font-weight:900;font-style:italic;color:rgba(26,20,16,0.06);'>No Profile</div>
                    <p style='font-family:"DM Mono",monospace;font-size:10px;letter-spacing:3px;color:#A09080;text-transform:uppercase;margin-top:-10px;'>
                        Generate a workout plan first
                    </p>
                </div>
            """, unsafe_allow_html=True)
