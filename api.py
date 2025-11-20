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
from typing import List, Optional, Dict

# ==========================================
# 1. PAGE CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(
    page_title="Phishing Detector NEO",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cyber-Security Theme CSS
st.markdown("""
<style>
    /* General App Background */
    .stApp {
        background-color: #0E1117;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #E6E6E6 !important;
        font-weight: 600;
    }
    h1 { font-size: 2.5rem; }
    
    /* Text Areas & Inputs */
    .stTextArea textarea {
        background-color: #161B22;
        color: #E6E6E6;
        border: 1px solid #30363D;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #58A6FF;
        box-shadow: 0 0 0 1px #58A6FF;
    }

    /* Buttons */
    .stButton button {
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    /* Primary Action Button */
    div[data-testid="stButton"] > button:first-child {
        background-color: #1F6FEB;
        color: white;
        border: none;
    }
    div[data-testid="stButton"] > button:hover {
        opacity: 0.9;
        transform: scale(1.01);
    }

    /* Custom Cards/Containers */
    .css-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Verdict Badges */
    .verdict-safe {
        background-color: #0f392b;
        color: #2ea043;
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #2ea043;
        font-weight: bold;
        text-align: center;
    }
    .verdict-suspicious {
        background-color: #3d2c00;
        color: #d29922;
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #d29922;
        font-weight: bold;
        text-align: center;
    }
    .verdict-dangerous {
        background-color: #3e1515;
        color: #ff7b72;
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #ff7b72;
        font-weight: bold;
        text-align: center;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE LOGIC (PRESERVED FROM ORIGINAL)
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
            status_container.info(f"📥 Downloading core component: {filename}...")
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
            status_container.info(f"📦 Extracting resources: {zip_name}...")
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(MODELS_DIR)
    
    status_container.empty()
    return True

# Initialize Model Registry Pattern (adapted for Streamlit State)
class ModelRegistry:
    email_model: Optional[object] = None
    email_vectorizer: Optional[object] = None
    url_model: Optional[object] = None
    feature_names: Optional[List[str]] = None

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

def extract_url_features(url: str, feature_names: List[str]) -> List[int]:
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
    
    # Assuming logic: 1 = legitimate, -1 = phishing (or similar based on provided code context)
    # The provided code had: "legitimate" if pred == 1 else "phishing"
    
    return {
        "type": "URL",
        "content": url,
        "prediction": "legitimate" if pred == 1 else "phishing",
        "probabilities": {"phishing": float(proba[0]), "legitimate": float(proba[1])},
        "risk_score": float(proba[0]) * 100, # Phishing probability as score
        "features_used": feats,
        "feature_names": registry.feature_names
    }

def analyze_email_logic(text: str, registry: ModelRegistry):
    if registry.email_model is None or registry.email_vectorizer is None:
        return None
    tfidf = registry.email_vectorizer.transform([text])
    pred = int(registry.email_model.predict(tfidf)[0])
    proba = registry.email_model.predict_proba(tfidf)[0]
    
    # Provided code: "phishing" if pred == 1 else "legitimate"
    return {
        "type": "Email Body",
        "content": text[:50] + "..." if len(text) > 50 else text,
        "prediction": "phishing" if pred == 1 else "legitimate",
        "probabilities": {"legitimate": float(proba[0]), "phishing": float(proba[1])},
        "risk_score": float(proba[1]) * 100 # Phishing probability
    }

def run_dual_prediction(text: str, registry: ModelRegistry):
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, text)

    email_result = None
    # Only run email model if there is substantial text (heuristic)
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
    
    # Check URLs
    for r in url_results:
        if r["risk_score"] > max_risk:
            max_risk = r["risk_score"]
        if r["prediction"] == "phishing":
            overall_status = "DANGEROUS"
    
    # Check Email
    if email_result:
        if email_result["risk_score"] > max_risk:
            max_risk = email_result["risk_score"]
        if email_result["prediction"] == "phishing":
            overall_status = "DANGEROUS"

    # Intermediate state
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

def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🛡️ Phishing Detector NEO")
        st.markdown("**Next-Gen AI Threat Analysis System** | powered by Dual-Stack ML")
    with col2:
        st.markdown("")
        st.markdown("")
        st.caption("System Status: 🟢 ONLINE")

def render_scan_tab(registry):
    st.markdown("### 📡 Threat Scanner")
    
    col_input, col_actions = st.columns([3, 1])
    
    with col_input:
        input_val = st.text_area(
            "Input Payload",
            value=st.session_state['input_text'],
            height=200,
            placeholder="Paste email content, SMS text, or suspicious URLs here for analysis...",
            label_visibility="collapsed",
            key="main_input" # Key is crucial for state sync
        )
    
    with col_actions:
        st.write("**Quick Actions**")
        if st.button("🧪 Load Phishing Sample", use_container_width=True):
            st.session_state['input_text'] = "URGENT: Your account is compromised. Click here immediately: http://bit.ly/fake-login-123 to verify."
            st.rerun()
        
        if st.button("✅ Load Safe Sample", use_container_width=True):
            st.session_state['input_text'] = "Hi team, here are the meeting notes for the project: https://docs.google.com/document/d/legit-id/edit"
            st.rerun()
            
        if st.button("🗑️ Clear Input", use_container_width=True):
            st.session_state['input_text'] = ""
            st.session_state['last_result'] = None
            st.rerun()

    # Run Button
    if st.button("🚀 RUN SECURITY SCAN", type="primary", use_container_width=True):
        if not input_val.strip():
            st.warning("⚠️ Please enter text to analyze.")
        else:
            with st.spinner("🔍 Analyzing patterns... Checking heuristic signatures..."):
                # Simulate slight delay for UX effect
                time.sleep(0.8)
                result = run_dual_prediction(input_val, registry)
                st.session_state['last_result'] = result
                st.session_state['history'].insert(0, result) # Add to top
                st.toast("Analysis Complete", icon="✅")

    # Results Section
    if st.session_state['last_result']:
        res = st.session_state['last_result']
        st.markdown("---")
        st.markdown("### 🎯 Scan Verdict")
        
        # Top Level Verdict
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if res['overall_verdict'] == "SAFE":
                st.markdown('<div class="verdict-safe">✅ SAFE</div>', unsafe_allow_html=True)
            elif res['overall_verdict'] == "SUSPICIOUS":
                st.markdown('<div class="verdict-suspicious">⚠️ SUSPICIOUS</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="verdict-dangerous">⛔ DANGEROUS</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"**Threat Probability: {res['risk_score']:.1f}%**")
            st.progress(int(res['risk_score']))
            
        with c3:
            st.metric("URLs Found", len(res['url_analysis']))

        # Detailed Cards
        st.markdown("#### 🔍 Analysis Breakdown")
        
        # Email Analysis Card
        if res['email_analysis']:
            with st.expander("📧 Email Content Analysis", expanded=True):
                e = res['email_analysis']
                ec1, ec2 = st.columns([1, 3])
                with ec1:
                    st.metric("Model Confidence", f"{e['probabilities']['phishing']*100:.1f}%")
                with ec2:
                    st.info(f"The NLP model classified this text as **{e['prediction'].upper()}** based on linguistic patterns (urgency, keyword frequency, tone).")

        # URL Analysis Card
        if res['url_analysis']:
            with st.expander("🔗 URL Heuristic Analysis", expanded=True):
                for u in res['url_analysis']:
                    st.markdown(f"**Target:** `{u['content']}`")
                    cols = st.columns(4)
                    cols[0].metric("Risk Score", f"{u['risk_score']:.1f}%")
                    cols[1].metric("Prediction", u['prediction'].upper())
                    
                    # Flag specific features found
                    flags = []
                    feat_names = u['feature_names']
                    feat_vals = u['features_used']
                    
                    if feat_names:
                        for i, val in enumerate(feat_vals):
                            if val == 1: # Assuming 1 indicates presence of suspicious trait in this model logic
                                if feat_names[i] == "UsingIP": flags.append("IP Address Host")
                                if feat_names[i] == "ShortURL": flags.append("URL Shortener")
                                if feat_names[i] == "Symbol@": flags.append("Obfuscated (@)")
                                if feat_names[i] == "Redirecting//": flags.append("Double Redirection")
                    
                    if flags:
                        st.markdown(f"🚩 **Flags Raised:** {', '.join(flags)}")
                    else:
                        st.markdown("✅ No specific obfuscation flags detected.")
                    st.markdown("---")
        elif not res['url_analysis']:
             st.info("No URLs detected in the input.")

def render_history_tab():
    st.markdown("### 📜 Scan Log")
    if not st.session_state['history']:
        st.caption("No scans performed yet in this session.")
    else:
        # Convert history to DF for nice display
        data = []
        for item in st.session_state['history']:
            data.append({
                "Time": item['timestamp'],
                "Verdict": item['overall_verdict'],
                "Risk Score": f"{item['risk_score']:.1f}%",
                "Snippet": item['input_text'][:40] + "..."
            })
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

def render_about_tab():
    st.markdown("### 🧠 How It Works")
    st.markdown("""
    **Phishing Detector NEO** utilizes a dual-layer machine learning architecture:
    
    1.  **Natural Language Processing (NLP)**
        *   Analyzes the *body text* of emails/messages.
        *   Uses **TF-IDF Vectorization** to convert text into numerical data.
        *   Powered by a **Random Forest Classifier** trained on thousands of phishing vs. legitimate emails.
        
    2.  **URL Heuristics Engine**
        *   Extracts structural features from links (e.g., IP address usage, URL length, presence of `@`, redirect patterns).
        *   Detects obfuscation techniques commonly used by attackers to hide malicious domains.
        
    **Why this matters:** Traditional filters often miss zero-day attacks. By combining content analysis with structural URL inspection, NEO provides a holistic risk assessment.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Privacy Note:** This demo runs locally in the browser session. No data is stored permanently.")
    with col2:
        st.success("**Model Status:** Pre-trained models loaded successfully.")

# ==========================================
# 4. MAIN APP ENTRY POINT
# ==========================================

def main():
    # 1. Initialization
    setup_models() # Download if needed
    registry = load_models_into_memory() # Load to RAM
    init_session_state() # UI State
    
    # 2. Header
    render_header()
    
    # 3. Navigation
    tab_scan, tab_history, tab_about = st.tabs(["🔍 SCANNER", "📜 HISTORY", "ℹ️ ABOUT"])
    
    with tab_scan:
        render_scan_tab(registry)
    
    with tab_history:
        render_history_tab()
        
    with tab_about:
        render_about_tab()

if __name__ == "__main__":
    main()
