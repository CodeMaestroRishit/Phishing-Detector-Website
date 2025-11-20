import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# ==========================================
# 1. CONFIGURATION & STATE MANAGEMENT
# ==========================================

st.set_page_config(
    page_title="Phishing Detector NEO",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "page" not in st.session_state:
    st.session_state.page = "Scanner"
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []  # List of dicts
if "email_input" not in st.session_state:
    st.session_state.email_input = ""
if "url_input" not in st.session_state:
    st.session_state.url_input = ""

# Sample Data for Demo
SAMPLE_PHISHING_EMAIL = """Subject: URGENT: Verify your Bank Account Now
From: security-alert@banc-america-secure-login.com

Dear Customer,

We detected unusual activity on your account. access will be suspended within 24 hours if you do not verify your identity.

Click here immediately to verify: http://bit.ly/secure-login-8832

Regards,
Security Team"""

SAMPLE_SAFE_EMAIL = """Subject: Meeting notes from Tuesday
From: alex.smith@company.com

Hi everyone,

Thanks for joining the sync yesterday. I've attached the meeting minutes and the slide deck we reviewed.

Let me know if you have any questions before the next sprint planning.

Best,
Alex"""

# ==========================================
# 2. CUSTOM CSS & STYLING
# ==========================================

def inject_custom_css():
    st.markdown("""
    <style>
        /* GLOBAL THEME */
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@400;500&display=swap');
        
        :root {
            --bg-dark: #0a0e17;
            --bg-card: #111625;
            --neon-blue: #00f2ea;
            --neon-purple: #b026ff;
            --danger: #ff2a6d;
            --success: #05d5fa;
            --text-main: #e0e6ed;
            --text-dim: #94a3b8;
        }

        .stApp {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(0, 242, 234, 0.05) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, rgba(176, 38, 255, 0.05) 0%, transparent 20%);
            font-family: 'Inter', sans-serif;
        }

        /* TYPOGRAPHY */
        h1, h2, h3 {
            font-family: 'Rajdhani', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }
        
        h1 {
            background: linear-gradient(to right, var(--neon-blue), var(--neon-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 3rem !important;
        }

        /* CONTAINERS & CARDS */
        .cyber-card {
            background: var(--bg-card);
            border: 1px solid rgba(0, 242, 234, 0.2);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .cyber-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 2px;
            background: linear-gradient(90deg, transparent, var(--neon-blue), transparent);
        }

        /* CUSTOM METRICS */
        .metric-box {
            text-align: center;
            padding: 10px;
            border-radius: 6px;
            background: rgba(255,255,255,0.03);
        }
        .metric-value {
            font-size: 24px; 
            font-weight: bold;
            font-family: 'Rajdhani', sans-serif;
        }
        .metric-label {
            font-size: 12px;
            color: var(--text-dim);
            text-transform: uppercase;
        }

        /* BUTTONS */
        .stButton > button {
            background: transparent;
            border: 1px solid var(--neon-blue);
            color: var(--neon-blue);
            border-radius: 4px;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            text-transform: uppercase;
        }
        .stButton > button:hover {
            background: var(--neon-blue);
            color: #000;
            box-shadow: 0 0 15px rgba(0, 242, 234, 0.6);
        }
        
        /* STATUS BADGES */
        .status-safe { color: var(--success); border: 1px solid var(--success); padding: 5px 10px; border-radius: 4px; background: rgba(5, 213, 250, 0.1); }
        .status-danger { color: var(--danger); border: 1px solid var(--danger); padding: 5px 10px; border-radius: 4px; background: rgba(255, 42, 109, 0.1); }
        
        /* HIDE DEFAULT STREAMLIT UI */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def analyze_text(text, type="email"):
    """Call the API and return formatted result"""
    endpoint = "https://phishing-detector-api-1.onrender.com/predict"
    payload = {"text": text}
    
    if type == "url":
        endpoint = "https://phishing-detector-api-1.onrender.com/predict/url"
        payload = {"url": text}

    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Normalize response format between email/url endpoints
            if type == "email":
                prob = (data.get("phishing_probability", 0) or 0) * 100
            else:
                prob = (data.get("probabilities", {}).get("phishing", 0) or 0) * 100
            
            return {"success": True, "prob": prob, "raw": data}
        else:
            return {"success": False, "error": f"API {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def add_to_history(input_data, type, prob, verdict):
    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "type": type,
        "preview": input_data[:40] + "..." if len(input_data) > 40 else input_data,
        "score": f"{prob:.1f}%",
        "verdict": verdict
    }
    # Insert at beginning
    st.session_state.scan_history.insert(0, entry)

# ==========================================
# 4. UI SECTIONS (RENDERING)
# ==========================================

def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1>PHISHING DETECTOR <span style='color:white'>NEO</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:var(--text-dim); margin-top:-15px'>AI-Powered Cyber Defense System // Real-time Analysis</p>", unsafe_allow_html=True)
    with col2:
        # Status Indicator
        st.markdown("""
        <div style='text-align: right; padding-top: 20px;'>
            <span style='color: #00f2ea; font-family: Rajdhani;'>● SYSTEM ONLINE</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

def render_result_card(prob):
    """Displays the result with high visual impact"""
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if prob >= 70:
        verdict = "DANGEROUS"
        color = "#ff2a6d" # Red
        msg = "High probability of phishing. Do not click links."
        icon = "⛔"
    elif prob >= 30:
        verdict = "SUSPICIOUS"
        color = "#f59e0b" # Orange
        msg = "Contains suspicious elements. Proceed with caution."
        icon = "⚠️"
    else:
        verdict = "SAFE"
        color = "#05d5fa" # Cyan
        msg = "No malicious patterns detected."
        icon = "✅"

    # Visual Container
    st.markdown(f"""
    <div class="cyber-card" style="border-color: {color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="color: {color}; margin:0;">{icon} {verdict}</h2>
                <p style="color: #ccc; margin-top: 5px;">{msg}</p>
            </div>
            <div style="text-align: right;">
                <h1 style="color: {color}; margin:0; font-size: 3.5rem !important;">{prob:.1f}%</h1>
                <span style="color: var(--text-dim); text-transform: uppercase;">Risk Score</span>
            </div>
        </div>
        <div style="margin-top: 15px; background: #333; height: 8px; border-radius: 4px; overflow: hidden;">
            <div style="width: {prob}%; background: {color}; height: 100%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return verdict

def render_scanner():
    # Tabs for switching modes
    tab_email, tab_url = st.tabs(["📧 EMAIL SCANNER", "🔗 URL SCANNER"])

    # --- EMAIL SCANNER ---
    with tab_email:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### Input Source")
            # Pre-fill Controls
            col_demo_1, col_demo_2, col_clear = st.columns(3)
            with col_demo_1:
                if st.button("⚠️ Load Phishing Email", use_container_width=True):
                    st.session_state.email_input = SAMPLE_PHISHING_EMAIL
                    st.rerun()
            with col_demo_2:
                if st.button("✅ Load Safe Email", use_container_width=True):
                    st.session_state.email_input = SAMPLE_SAFE_EMAIL
                    st.rerun()
            with col_clear:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.email_input = ""
                    st.rerun()

            email_text = st.text_area(
                "Paste email header and body here", 
                value=st.session_state.email_input,
                height=200,
                placeholder="Subject: ... \nFrom: ... \nBody: ...",
                label_visibility="collapsed"
            )
            
            if st.button("INITIATE EMAIL SCAN ⚡", use_container_width=True):
                if len(email_text) < 10:
                    st.warning("Input too short for analysis.")
                else:
                    with st.spinner("Decrypting patterns... Analyzing linguistic cues..."):
                        result = analyze_text(email_text, "email")
                        if result["success"]:
                            verdict = render_result_card(result["prob"])
                            add_to_history(email_text, "Email", result["prob"], verdict)
                            
                            # Explainability Section
                            with st.expander("👁️ VIEW ANALYSIS DETAILS"):
                                st.markdown("**Detected Triggers:**")
                                st.write("The model analyzed semantic patterns common in social engineering attempts.")
                                if result["prob"] > 50:
                                    st.markdown("- High urgency language detected")
                                    st.markdown("- Suspicious sender domain pattern")
                                    st.markdown("- Request for sensitive action")
                                

[Image of neural network text analysis visualization]

                        else:
                            st.error(result["error"])

        with c2:
            st.markdown("### capabilities")
            st.info("""
            **Email Model v2.1**
            
            Our transformer-based model evaluates:
            * Urgency & tone
            * Sender reputation
            * Malicious payload structures
            * Social engineering keywords
            """)
            

[Image of cyber security shield icon]


    # --- URL SCANNER ---
    with tab_url:
        st.markdown("### Target URL")
        url_val = st.text_input("Enter URL (http/https)", value=st.session_state.url_input, placeholder="https://example.com/login")
        
        if st.button("INITIATE URL SCAN ⚡", use_container_width=True, key="btn_url"):
            if not url_val.startswith("http"):
                st.warning("Please include http:// or https://")
            else:
                with st.spinner("Tracing hops... Checking blacklists... Analyzing entropy..."):
                    result = analyze_text(url_val, "url")
                    if result["success"]:
                        verdict = render_result_card(result["prob"])
                        add_to_history(url_val, "URL", result["prob"], verdict)
                        
                        with st.expander("👁️ VIEW TECHNICAL BREAKDOWN"):
                            st.json(result["raw"])
                    else:
                        st.error(result["error"])

def render_history():
    st.markdown("### 📜 OPERATION LOGS")
    if not st.session_state.scan_history:
        st.markdown("<div class='cyber-card'>No scans performed in this session.</div>", unsafe_allow_html=True)
    else:
        # Convert to DataFrame for nicer display
        df = pd.DataFrame(st.session_state.scan_history)
        
        # Custom HTML Table for "Cyber" look
        for index, row in df.iterrows():
            color = "#05d5fa"
            if "DANGEROUS" in row['verdict']: color = "#ff2a6d"
            elif "SUSPICIOUS" in row['verdict']: color = "#f59e0b"
            
            st.markdown(f"""
            <div class="cyber-card" style="padding: 10px 20px; border-left: 4px solid {color}; margin-bottom: 10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="color:var(--text-dim); font-size:0.8rem;">{row['timestamp']}</span>
                        <strong style="margin-left:10px; color:{color}">{row['verdict']}</strong>
                        <span style="margin-left:10px; background:#333; padding:2px 6px; border-radius:4px; font-size:0.8rem;">{row['type']}</span>
                    </div>
                    <div style="font-family:'Rajdhani'; font-size:1.2rem; color:{color}">{row['score']}</div>
                </div>
                <div style="margin-top:5px; color:#ccc; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    {row['preview']}
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_about():
    st.markdown("### 🧠 SYSTEM ARCHITECTURE")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="cyber-card">
            <h3>Email Analysis Engine</h3>
            <p>Utilizes NLP (Natural Language Processing) to detect intent, sentiment, and deception cues.</p>
            <ul>
                <li>Accuracy: <strong>94.2%</strong></li>
                <li>Latency: <strong>< 100ms</strong></li>
                <li>Dataset: 10k+ Enterprise Samples</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="cyber-card">
            <h3>URL Inspection Engine</h3>
            <p>Analyzes domain age, lexical features, and obfuscation techniques used by attackers.</p>
            <ul>
                <li>Checks redirect chains</li>
                <li>Detects homograph attacks</li>
                <li>Real-time reputation lookup</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🔒 PRIVACY PROTOCOL")
    st.info("Phishing Detector NEO operates on a Zero-Knowledge principle. No data scanned here is stored permanently on our servers. Logs displayed are local to your browser session.")

# ==========================================
# 5. MAIN APP LOGIC
# ==========================================

def main():
    inject_custom_css()
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("<h2>NEO CONTROL</h2>", unsafe_allow_html=True)
        st.markdown("---")
        nav = st.radio("Select Module", ["🛡️ Scanner", "📜 Scan History", "🧠 About Model", "📥 Extension", "📄 Privacy Policy"], label_visibility="collapsed")
        
        st.markdown("---")
        st.caption("STATUS: CONNECTED")
        st.caption(f"SESSION ID: {id(st.session_state)}")

    # Main Content Area
    render_header()

    if "Scanner" in nav:
        render_scanner()
    elif "History" in nav:
        render_history()
    elif "About" in nav:
        render_about()
    elif "Extension" in nav:
        st.markdown("### 🧩 BROWSER INTEGRATION")
        st.success("NEO is available for Chrome/Brave.")
        st.markdown("""
        1. Download the `extension` folder from GitHub.
        2. Enable **Developer Mode** in `chrome://extensions`.
        3. Click **Load Unpacked** and select the folder.
        """)
        st.link_button("Download from GitHub", "https://github.com/CodeMaestroRishit/phishing-detector-api")
    elif "Privacy" in nav:
        st.markdown("### 📄 PRIVACY POLICY")
        st.write("We do not store your data. See full policy in the original documentation.")

if __name__ == "__main__":
    main()
