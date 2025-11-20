import streamlit as st
import os
import re
import pickle
import pathlib
import urllib.request
import zipfile
import pandas as pd
import time
from datetime import datetime
from typing import List, Optional

# ==========================================
# 1. PAGE CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(
    page_title="Phishing Detector NEO",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cyber-Security Theme CSS (polished)
st.markdown("""
<style>
    /* Global */
    .stApp {
        background: radial-gradient(circle at top left, #151b28 0, #05060a 45%, #05060a 100%);
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #E6E6E6;
    }

    /* Make main content centered with max width */
    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #F5F5F5 !important;
        font-weight: 650;
    }
    h1 { font-size: 2.4rem; }
    h2 { font-size: 1.6rem; }

    /* hero subtitle */
    .hero-subtitle {
        color: #9ca3af;
        font-size: 0.95rem;
        margin-top: -0.25rem;
    }

    /* Text Areas & Inputs */
    .stTextArea textarea {
        background-color: #0b1120;
        color: #E6E6E6;
        border: 1px solid #1f2937;
        border-radius: 10px;
        font-size: 0.95rem;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 1px #3b82f6;
    }

    /* Buttons */
    .stButton button {
        border-radius: 999px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        font-size: 0.95rem;
        border: 1px solid transparent;
        transition: all 0.16s ease-in-out;
    }

    /* Primary Action Button (RUN SECURITY SCAN) */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #4f46e5);
        border: none;
    }
    .stButton button:hover {
        opacity: 0.96;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.35);
    }

    /* Custom Cards/Containers */
    .css-card {
        background: rgba(15,23,42,0.92);
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 20px 18px;
        margin-bottom: 16px;
    }

    .css-side-card {
        background: rgba(15,23,42,0.88);
        border-radius: 14px;
        border: 1px solid #111827;
        padding: 14px 14px 10px 14px;
    }

    /* Verdict Badges */
    .verdict-safe {
        background: rgba(16, 185, 129, 0.12);
        color: #22c55e;
        padding: 8px 18px;
        border-radius: 999px;
        border: 1px solid rgba(34,197,94,0.45);
        font-weight: 700;
        text-align: center;
        font-size: 0.9rem;
    }
    .verdict-suspicious {
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        padding: 8px 18px;
        border-radius: 999px;
        border: 1px solid rgba(251,191,36,0.45);
        font-weight: 700;
        text-align: center;
        font-size: 0.9rem;
    }
    .verdict-dangerous {
        background: rgba(239, 68, 68, 0.12);
        color: #f97373;
        padding: 8px 18px;
        border-radius: 999px;
        border: 1px solid rgba(248,113,113,0.55);
        font-weight: 700;
        text-align: center;
        font-size: 0.9rem;
    }

    /* History badges */
    .badge-safe {
        background: rgba(16, 185, 129, 0.14);
        color: #4ade80;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-suspicious {
        background: rgba(245, 158, 11, 0.16);
        color: #facc15;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-dangerous {
        background: rgba(239, 68, 68, 0.16);
        color: #fb7185;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Metrics section tweak */
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        color: #9ca3af;
    }

    /* Tabs styling light touch */
    button[data-baseweb="tab"] {
        border-radius: 999px !important;
        padding-top: 0.4rem;
        padding-bottom: 0.4rem;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-right: 0.3rem;
        font-size: 0.9rem;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE LOGIC (UNCHANGED FUNCTIONALLY)
# ==========================================

MODELS_DIR = pathlib.Path("trained_models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILES = {
    "email_model.pkl.zip": "1DXNw2o7x_sg_rQP1SYCyFUrqfwlZcgpe",
    "email_vectorizer.pkl.zip": "1-GeQFYkqf3nq0-xBdHYYagTqPidvU-_S",
    "url_model.pkl.zip": "1Isdoe_udMTBpEdlvNr2hSn1oQk4m6wG_",
}

@st.cache_resource
def setup_models():
    """Download and extract models. Cached to run only once."""
    status_container = st.empty()
    
    # Download
    for filename, file_id in MODEL_FILES.items():
        filepath = MODELS_DIR / filename
        if not filepath.exists():
            status_container.info(f"📥 Downloading core component: `{filename}` ...")
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            try:
                urllib.request.urlretrieve(url, filepath)
            except Exception as e:
                st.error(f"Failed to download {filename}: {e}")

    # Extract
    EXPECTED_PKLS = {
        "email_model.pkl": MODELS_DIR / "email_model.pkl",
        "email_vectorizer.pkl": MODELS_DIR / "email_vectorizer.pkl",
        "url_model.pkl": MODELS_DIR / "url_model.pkl",
    }
    
    for zip_name, pkl_name in [
        ("email_model.pkl.zip", "email_model.pkl"),
        ("email_vectorizer.pkl.zip", "email_vectorizer.pkl"),
        ("url_model.pkl.zip", "url_model.pkl"),
    ]:
        zip_path = MODELS_DIR / zip_name
        pkl_path = MODELS_DIR / pkl_name
        if zip_path.exists() and not pkl_path.exists():
            status_container.info(f"📦 Extracting resources: `{zip_name}` ...")
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(MODELS_DIR)
    
    status_container.empty()
    return True

# Initialize Model Registry Pattern
class ModelRegistry:
    email_model: Optional[object] = None
    email_vectorizer: Optional[object] = None
    url_model: Optional[object] = None
    feature_names: Optional[list] = None

@st.cache_resource
def load_models_into_memory():
    """Loads pickles into memory. Cached."""
    registry = ModelRegistry()
    
    # Load Email Model
    model_path = MODELS_DIR / "email_model.pkl"
    vectorizer_path = MODELS_DIR / "email_vectorizer.pkl"
    if model_path.exists() and vectorizer_path.exists():
        with open(model_path, "rb") as f:
            registry.email_model = pickle.load(f)
        with open(vectorizer_path, "rb") as f:
            registry.email_vectorizer = pickle.load(f)

    # Load URL Model
    url_pkl = MODELS_DIR / "url_model.pkl"
    if url_pkl.exists():
        with open(url_pkl, "rb") as f:
            registry.url_model = pickle.load(f)
        registry.feature_names = [
            "UsingIP", "LongURL", "ShortURL", "Symbol@", "HTTPS", "Redirecting//"
        ]
    
    return registry

# -------------------- Logic Functions --------------------

def extract_url_features(url: str, feature_names: list) -> list:
    features = [0] * len(feature_names)
    def set_feat(name: str, value: int) -> None:
        if name in feature_names:
            idx = feature_names.index(name)
            features[idx] = value

    ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    set_feat("UsingIP", 1 if re.search(ip_pattern, url) else -1)
    set_feat("LongURL", 1 if len(url) > 75 else -1)
    set_feat("ShortURL", 1 if any(d in url for d in ["bit.ly", "tinyurl", "t.co", "goo.gl"]) else -1)
    set_feat("Symbol@", 1 if "@" in url else -1)
    set_feat("HTTPS", 1 if url.lower().startswith("https") else -1)
    set_feat("Redirecting//", 1 if url.count("//") > 1 else -1)

    return features

def analyze_url_logic(url: str, registry: ModelRegistry):
    if registry.url_model is None:
        return None
    feats = extract_url_features(url, registry.feature_names)
    pred = int(registry.url_model.predict([feats])[0])
    proba = registry.url_model.predict_proba([feats])[0]
    
    return {
        "type": "URL",
        "content": url,
        "prediction": "legitimate" if pred == 1 else "phishing",
        "probabilities": {"phishing": float(proba[0]), "legitimate": float(proba[1])},
        "risk_score": float(proba[0]) * 100,  # Phishing probability as score
        "features_used": feats,
        "feature_names": registry.feature_names
    }

def analyze_email_logic(text: str, registry: ModelRegistry):
    if registry.email_model is None or registry.email_vectorizer is None:
        return None
    tfidf = registry.email_vectorizer.transform([text])
    pred = int(registry.email_model.predict(tfidf)[0])
    proba = registry.email_model.predict_proba(tfidf)[0]
    
    return {
        "type": "Email Body",
        "content": text[:50] + "..." if len(text) > 50 else text,
        "prediction": "phishing" if pred == 1 else "legitimate",
        "probabilities": {"legitimate": float(proba[0]), "phishing": float(proba[1])},
        "risk_score": float(proba[1]) * 100  # Phishing probability
    }

def run_dual_prediction(text: str, registry: ModelRegistry):
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, text)

    email_result = None
    if len(text.strip()) > 0:
        try:
            email_result = analyze_email_logic(text, registry)
        except Exception:
            pass

    url_results = []
    for u in urls:
        res = analyze_url_logic(u, registry)
        if res:
            url_results.append(res)

    # Determine Overall Verdict
    overall_status = "SAFE"
    max_risk = 0.0
    
    for r in url_results:
        if r["risk_score"] > max_risk:
            max_risk = r["risk_score"]
        if r["prediction"] == "phishing":
            overall_status = "DANGEROUS"
    
    if email_result:
        if email_result["risk_score"] > max_risk:
            max_risk = email_result["risk_score"]
        if email_result["prediction"] == "phishing":
            overall_status = "DANGEROUS"

    if overall_status == "SAFE" and max_risk > 40:
        overall_status = "SUSPICIOUS"

    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "input_text": text,
        "overall_verdict": overall_status,
        "risk_score": max_risk,
        "email_analysis": email_result,
        "url_analysis": url_results
    }

# ==========================================
# 3. UI COMPONENT FUNCTIONS
# ==========================================

def init_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'input_text' not in st.session_state:
        st.session_state['input_text'] = ""
    if 'last_result' not in st.session_state:
        st.session_state['last_result'] = None
    if 'stats' not in st.session_state:
        st.session_state['stats'] = {
            "total_scans": 0,
            "dangerous_count": 0,
            "last_verdict": "—"
        }

def verdict_badge_html(verdict: str) -> str:
    v = verdict.upper()
    if v == "SAFE":
        return '<span class="badge-safe">SAFE</span>'
    if v == "SUSPICIOUS":
        return '<span class="badge-suspicious">SUSPICIOUS</span>'
    return '<span class="badge-dangerous">DANGEROUS</span>'

def render_header():
    st.markdown("### 🛡️ Phishing Detector NEO")
    st.markdown(
        '<div class="hero-subtitle">'
        'Dual-layer ML engine for emails, SMS, and URLs — designed for security audits & demos.'
        '</div>',
        unsafe_allow_html=True
    )

    # Top stats bar
    stats = st.session_state['stats']
    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Scans (this session)", stats["total_scans"])
    with c2:
        st.metric("Dangerous Flags Raised", stats["dangerous_count"])
    with c3:
        st.metric("Last Verdict", stats["last_verdict"])

def render_scan_tab(registry: ModelRegistry):
    st.markdown("#### 📡 Real-Time Threat Scanner")

    # Main scanner layout
    left, right = st.columns([3, 1])
    
    with left:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        input_val = st.text_area(
            "Payload Input",
            value=st.session_state['input_text'],
            height=220,
            placeholder="Paste email content, SMS text, or suspicious URLs here…",
            label_visibility="collapsed",
            key="main_input"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with right:
        st.markdown('<div class="css-side-card">', unsafe_allow_html=True)
        st.markdown("**Quick Actions**")
        st.caption("Use samples to demo behaviour during judging.")
        if st.button("🧪 Load Phishing Sample", use_container_width=True):
            st.session_state['input_text'] = (
                "URGENT: Your account is compromised. Click here immediately: "
                "http://bit.ly/fake-login-123 to verify."
            )
            st.rerun()
        
        if st.button("✅ Load Safe Sample", use_container_width=True):
            st.session_state['input_text'] = (
                "Hi team, here are the meeting notes for the project: "
                "https://docs.google.com/document/d/legit-id/edit"
            )
            st.rerun()
            
        if st.button("🗑️ Clear Input", use_container_width=True):
            st.session_state['input_text'] = ""
            st.session_state['last_result'] = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Run Scan Button
    st.markdown("")
    run_col = st.container()
    with run_col:
        if st.button("🚀 RUN SECURITY SCAN", type="primary", use_container_width=True):
            if not input_val.strip():
                st.warning("⚠️ Paste some content or URL to analyze.")
            else:
                with st.spinner("🔍 Running NLP + URL heuristic analysis…"):
                    time.sleep(0.6)
                    result = run_dual_prediction(input_val, registry)
                    st.session_state['last_result'] = result
                    st.session_state['history'].insert(0, result)

                    # Update stats
                    st.session_state['stats']["total_scans"] += 1
                    st.session_state['stats']["last_verdict"] = result["overall_verdict"]
                    if result["overall_verdict"] == "DANGEROUS":
                        st.session_state['stats']["dangerous_count"] += 1

                    st.toast("Scan complete.", icon="✅")

    # Results Section
    if st.session_state['last_result']:
        res = st.session_state['last_result']
        st.markdown("---")
        st.markdown("#### 🎯 Scan Verdict")

        vc1, vc2, vc3 = st.columns([1, 2, 1])
        with vc1:
            if res['overall_verdict'] == "SAFE":
                st.markdown('<div class="verdict-safe">✅ SAFE</div>', unsafe_allow_html=True)
            elif res['overall_verdict'] == "SUSPICIOUS":
                st.markdown('<div class="verdict-suspicious">⚠️ SUSPICIOUS</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="verdict-dangerous">⛔ DANGEROUS</div>', unsafe_allow_html=True)
        
        with vc2:
            st.markdown(f"**Threat Probability:** `{res['risk_score']:.1f}%`")
            st.progress(int(res['risk_score']))
            
        with vc3:
            st.metric("URLs Detected", len(res['url_analysis']))

        # Breakdown
        st.markdown("")
        st.markdown("#### 🔍 Analysis Breakdown")

        # Email Analysis Card
        if res['email_analysis']:
            e = res['email_analysis']
            with st.expander("📧 Email / Text Content Analysis", expanded=True):
                ec1, ec2 = st.columns([1, 3])
                with ec1:
                    st.metric("Phishing Confidence", f"{e['probabilities']['phishing']*100:.1f}%")
                    st.caption(f"Verdict: **{e['prediction'].upper()}**")
                with ec2:
                    st.info(
                        "The NLP classifier flags phishing based on patterns like urgency, "
                        "credential requests, abnormal tone, and suspicious keywords."
                    )
                st.caption("Message snippet analyzed:")
                st.code(e["content"], language="text")

        # URL Analysis Card
        if res['url_analysis']:
            with st.expander("🔗 URL Heuristic & ML Analysis", expanded=True):
                for u in res['url_analysis']:
                    st.markdown(f"**Target URL:** `{u['content']}`")
                    cols = st.columns(3)
                    cols[0].metric("Risk Score", f"{u['risk_score']:.1f}%")
                    cols[1].metric("Prediction", u['prediction'].upper())
                    cols[2].metric("Phishing Prob.", f"{u['probabilities']['phishing']*100:.1f}%")

                    # Flag suspicious traits
                    flags = []
                    feat_names = u['feature_names']
                    feat_vals = u['features_used']
                    
                    if feat_names:
                        for i, val in enumerate(feat_vals):
                            if val == 1:
                                if feat_names[i] == "UsingIP": flags.append("Raw IP in domain")
                                if feat_names[i] == "ShortURL": flags.append("URL shortener used")
                                if feat_names[i] == "Symbol@": flags.append("Obfuscated '@' in path")
                                if feat_names[i] == "Redirecting//": flags.append("Multiple '//' redirections")
                                if feat_names[i] == "LongURL": flags.append("Very long URL")
                    
                    if flags:
                        st.markdown(f"🚩 **Flags Raised:** {', '.join(flags)}")
                    else:
                        st.markdown("✅ No obvious obfuscation traits detected.")
                    st.markdown("---")
        else:
            st.info("🔍 No URLs detected in the input. Only text/NLP analysis was applied.")

def render_history_tab():
    st.markdown("#### 📜 Session Scan Log")
    if not st.session_state['history']:
        st.caption("No scans yet. Run a security scan to populate history.")
        return

    # Convert history to DF for display
    data = []
    for item in st.session_state['history']:
        verdict = item['overall_verdict']
        badge = verdict_badge_html(verdict)
        data.append({
            "Time": item['timestamp'],
            "Verdict": badge,
            "Risk Score": f"{item['risk_score']:.1f}%",
            "Snippet": (item['input_text'][:60] + "…") if len(item['input_text']) > 60 else item['input_text'],
        })
    df = pd.DataFrame(data)

    # Use HTML for verdict badges
    st.write(
        df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

def render_about_tab():
    st.markdown("#### 🧠 Under the Hood: Detection Stack")
    st.markdown("""
**Phishing Detector NEO** runs a dual-layer pipeline:

1. **NLP Engine on Message Body**  
   - TF–IDF converts email / SMS text into numeric vectors.  
   - A trained **Random Forest** (or similar classifier) separates phishing vs. legitimate.  
   - It picks up urgency, threats, “verify now / reset password” patterns, and more.

2. **URL Heuristic + ML Engine**  
   - Extracts features such as:
       - Use of raw IP address instead of domain  
       - URL length and presence of shorteners (`bit.ly`, `tinyurl`, etc.)  
       - Extra `@` symbols or multiple `//` redirects  
   - A model predicts whether the URL itself looks legitimate vs. phishing.

By combining **content semantics** and **URL structure**, NEO is better at catching:
- New / zero-day style templates
- Short-link based scams
- Obfuscated login pages

> **Demo note:** This app is ideal for showing how AI can sit in front of existing mail gateways or browser extensions to give a second-opinion risk score.
    """)

    c1, c2 = st.columns(2)
    with c1:
        st.info("**Privacy:** This demo only processes text in your current session. No data is permanently stored.")
    with c2:
        st.success("**Model Status:** If the scanner runs without errors, all core models are loaded correctly.")

# ==========================================
# 4. MAIN APP ENTRY POINT
# ==========================================

def main():
    setup_models()                   # Download if needed
    registry = load_models_into_memory()  # Load to RAM
    init_session_state()             # UI State
    
    render_header()
    
    tab_scan, tab_history, tab_about = st.tabs(["🔍 Scanner", "📜 History", "ℹ️ About"])
    
    with tab_scan:
        render_scan_tab(registry)
    
    with tab_history:
        render_history_tab()
        
    with tab_about:
        render_about_tab()

if __name__ == "__main__":
    main()
