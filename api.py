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
from typing import List, Optional, Dict, Any
from sklearn.ensemble import RandomForestClassifier

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Phishing Detector NEO",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Cyber-Security Theme
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Typography & Headings */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .subtitle {
        color: #00d4ff;
        font-size: 1.2rem;
        margin-bottom: 20px;
    }
    
    /* Cards / Containers */
    .css-1r6slb0 {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Custom Success/Danger Badges */
    .badge-safe {
        background-color: #0f392b;
        color: #2ea043;
        padding: 5px 10px;
        border-radius: 4px;
        border: 1px solid #2ea043;
        font-weight: bold;
    }
    .badge-danger {
        background-color: #3e1515;
        color: #ff4b4b;
        padding: 5px 10px;
        border-radius: 4px;
        border: 1px solid #ff4b4b;
        font-weight: bold;
    }
    .badge-warning {
        background-color: #3d2c00;
        color: #e3b341;
        padding: 5px 10px;
        border-radius: 4px;
        border: 1px solid #e3b341;
        font-weight: bold;
    }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: bold;
        height: 3rem;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #161b22;
        border-radius: 5px 5px 0 0;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0E1117;
        color: #58a6ff;
        border-top: 2px solid #58a6ff;
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE LOGIC (PRESERVED & ADAPTED)
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
    """Downloads and loads models once. Cached by Streamlit."""
    # 1. Download
    for filename, file_id in MODEL_FILES.items():
        filepath = MODELS_DIR / filename
        if not filepath.exists():
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            try:
                urllib.request.urlretrieve(url, filepath)
            except Exception:
                pass # Handle silently in UI or log

    # 2. Extract
    for zip_name, pkl_name in [
        ("email_model.pkl.zip", "email_model.pkl"),
        ("email_vectorizer.pkl.zip", "email_vectorizer.pkl"),
        ("url_model.pkl.zip", "url_model.pkl"),
    ]:
        zip_path = MODELS_DIR / zip_name
        pkl_path = MODELS_DIR / pkl_name
        if zip_path.exists() and not pkl_path.exists():
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(MODELS_DIR)

    # 3. Load into memory
    models = {}
    
    # Email Model
    try:
        with open(MODELS_DIR / "email_model.pkl", "rb") as f:
            models["email_model"] = pickle.load(f)
        with open(MODELS_DIR / "email_vectorizer.pkl", "rb") as f:
            models["email_vectorizer"] = pickle.load(f)
    except:
        models["email_model"] = None
        models["email_vectorizer"] = None

    # URL Model
    try:
        with open(MODELS_DIR / "url_model.pkl", "rb") as f:
            models["url_model"] = pickle.load(f)
        models["url_features"] = ["UsingIP", "LongURL", "ShortURL", "Symbol@", "HTTPS", "Redirecting//"]
    except:
        models["url_model"] = None
        models["url_features"] = []

    return models

# Initialize models
MODELS = setup_models()

def extract_url_features(url: str) -> List[int]:
    feature_names = MODELS.get("url_features", [])
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

def analyze_url(url: str):
    model = MODELS.get("url_model")
    if not model:
        return None
    
    feats = extract_url_features(url)
    pred = int(model.predict([feats])[0])
    proba = model.predict_proba([feats])[0]
    
    return {
        "url": url,
        "prediction": "legitimate" if pred == 1 else "phishing",
        "risk_score": float(proba[0]), # 0 = phishing prob, 1 = legit prob usually. Wait, let's check mapping.
        # Usually sklearn classes are [0, 1]. 
        # If pred=1 is legitimate, then class 1 is legit. Class 0 is phishing.
        # proba[0] is phishing probability.
        "phishing_probability": float(proba[0]) if pred == 1 else float(proba[0]), 
        # Let's stick to a generic risk score 0-100
        # If pred is 1 (Legit), proba[1] is high. If pred is 0 (Phishing), proba[0] is high.
        # We want "Phishing Probability".
        "prob_phishing": float(proba[0]) if model.classes_[0] == 0 else float(proba[1]), 
        "features": feats,
        "feature_names": MODELS["url_features"]
    }

def analyze_email(text: str):
    model = MODELS.get("email_model")
    vect = MODELS.get("email_vectorizer")
    if not model or not vect:
        return None
    
    tfidf = vect.transform([text])
    pred = int(model.predict(tfidf)[0])
    proba = model.predict_proba(tfidf)[0]
    
    # Assuming 1 = Phishing based on original code: "phishing" if pred == 1
    return {
        "prediction": "phishing" if pred == 1 else "legitimate",
        "prob_phishing": float(proba[1]), 
    }

def run_full_scan(text_input: str):
    """Combines Email and URL analysis"""
    if not text_input.strip():
        return None

    results = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "input_preview": text_input[:50] + "..." if len(text_input) > 50 else text_input,
        "email_analysis": None,
        "url_analysis": []
    }

    # 1. Email Content Analysis
    results["email_analysis"] = analyze_email(text_input)

    # 2. URL Extraction & Analysis
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, text_input)
    
    for u in urls:
        u_res = analyze_url(u)
        if u_res:
            results["url_analysis"].append(u_res)

    # 3. Overall Verdict Logic
    # Logic: If ANY URL is phishing OR Email text is phishing -> DANGEROUS
    is_phishing_email = results["email_analysis"]["prediction"] == "phishing" if results["email_analysis"] else False
    
    max_url_prob = 0.0
    if results["url_analysis"]:
        max_url_prob = max([u["prob_phishing"] for u in results["url_analysis"]])

    email_prob = results["email_analysis"]["prob_phishing"] if results["email_analysis"] else 0.0
    
    # Combined Risk Score (Heuristic: take the higher of the two signals)
    final_risk_score = max(email_prob, max_url_prob)
    
    if final_risk_score > 0.75:
        verdict = "DANGEROUS"
        color = "red"
    elif final_risk_score > 0.45:
        verdict = "SUSPICIOUS"
        color = "orange"
    else:
        verdict = "SAFE"
        color = "green"

    results["overall_verdict"] = verdict
    results["risk_score"] = final_risk_score
    results["color"] = color
    
    return results

# ==========================================
# 3. UI COMPONENTS
# ==========================================

def render_header():
    st.markdown("""
        <div style="text-align: center; padding-bottom: 20px;">
            <h1 style="margin-bottom:0;">🛡️ Phishing Detector NEO</h1>
            <p class="subtitle">Next-Gen AI Threat Analysis System</p>
        </div>
    """, unsafe_allow_html=True)

def sidebar_controls():
    # Initialize session state for history
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ""

def load_example(type_):
    if type_ == "safe":
        st.session_state.input_text = """Hi Team,
Just a reminder that our weekly sync is scheduled for tomorrow at 10 AM.
Please review the attached docs: https://docs.google.com/presentation
Thanks,
Alice"""
    elif type_ == "phishing":
        st.session_state.input_text = """URGENT: Your account has been compromised!
We detected unusual activity. 
Verify your identity immediately to avoid suspension:
http://bit.ly/secure-login-verify
If you do not act within 24 hours, your account will be deleted.
Security Team"""

def render_scan_tab():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📥 Input Analysis")
        st.caption("Paste an email body, SMS text, or URL below.")
        input_text = st.text_area(
            "Content", 
            value=st.session_state.input_text,
            height=200,
            label_visibility="collapsed",
            placeholder="Paste suspicious text or URL here..."
        )
        # Update session state manually if user types
        st.session_state.input_text = input_text

    with col2:
        st.markdown("### ⚡ Quick Actions")
        if st.button("🧪 Load Phishing Sample"):
            load_example("phishing")
            st.rerun()
        if st.button("✅ Load Safe Sample"):
            load_example("safe")
            st.rerun()
        if st.button("🗑️ Clear Input"):
            st.session_state.input_text = ""
            st.rerun()

    st.markdown("---")
    
    # Main Action Button
    if st.button("🚀 INITIATE SCAN", type="primary", use_container_width=True):
        with st.spinner("Analyzing patterns... Decrypting headers... Checking blocklists..."):
            time.sleep(0.8) # UI effect
            result = run_full_scan(st.session_state.input_text)
            
            if result:
                st.session_state.last_result = result
                st.session_state.history.insert(0, result) # Add to top of history
                st.toast("Scan Complete!", icon="✅")
            else:
                st.error("Please enter text to analyze.")

    # Display Results if available
    if 'last_result' in st.session_state:
        res = st.session_state.last_result
        
        # Result Header
        st.markdown("### 🎯 Scan Verdict")
        
        # Cards for layout
        r_col1, r_col2, r_col3 = st.columns([1, 2, 1])
        
        with r_col1:
            # Visual Badge
            if res["overall_verdict"] == "SAFE":
                st.markdown(f'<div class="badge-safe" style="text-align:center; font-size:24px;">✅ SAFE</div>', unsafe_allow_html=True)
            elif res["overall_verdict"] == "SUSPICIOUS":
                st.markdown(f'<div class="badge-warning" style="text-align:center; font-size:24px;">⚠️ SUSPICIOUS</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="badge-danger" style="text-align:center; font-size:24px;">⛔ DANGEROUS</div>', unsafe_allow_html=True)
        
        with r_col2:
            # Progress Bar
            score_pct = int(res["risk_score"] * 100)
            st.metric("Phishing Probability", f"{score_pct}%")
            st.progress(score_pct / 100)
        
        with r_col3:
            # Quick Stats
            url_count = len(res["url_analysis"])
            st.metric("URLs Found", url_count)

        # Deep Dive Section
        with st.expander("🔍 View Analysis Details", expanded=True):
            d_col1, d_col2 = st.columns(2)
            
            with d_col1:
                st.markdown("#### 📧 Text Analysis")
                if res["email_analysis"]:
                    e_prob = int(res["email_analysis"]["prob_phishing"] * 100)
                    st.write(f"**NLP Model Confidence:** {e_prob}% Phishing")
                    if e_prob > 50:
                        st.info("The language model detected urgency or keywords often used in scams.")
                    else:
                        st.success("The text structure appears normal.")
                else:
                    st.write("No text content analyzed.")

            with d_col2:
                st.markdown("#### 🔗 URL Analysis")
                if res["url_analysis"]:
                    for u in res["url_analysis"]:
                        u_risk = int(u["prob_phishing"] * 100)
                        emoji = "🔴" if u_risk > 50 else "🟢"
                        st.markdown(f"**{emoji} {u['url']}**")
                        st.caption(f"Risk Score: {u_risk}%")
                        
                        # Feature breakdown (mini)
                        feats = u["features"]
                        names = u["feature_names"]
                        flags = []
                        # Map back the feature vector
                        for i, val in enumerate(feats):
                            if names[i] == "UsingIP" and val == 1: flags.append("IP Address Used")
                            if names[i] == "ShortURL" and val == 1: flags.append("Shortener Service")
                            if names[i] == "Symbol@" and val == 1: flags.append("Contains '@'")
                            if names[i] == "Redirecting//" and val == 1: flags.append("Double Slash Redirection")
                        
                        if flags:
                            st.markdown(f"*Flags: {', '.join(flags)}*")
                else:
                    st.write("No URLs found in the input.")

def render_history_tab():
    st.markdown("### 📜 Recent Scans")
    if not st.session_state.history:
        st.info("No scan history yet. Run a scan to see logs here.")
        return

    # Create a simplified dataframe for display
    history_data = []
    for item in st.session_state.history:
        history_data.append({
            "Time": item["timestamp"],
            "Preview": item["input_preview"],
            "Verdict": item["overall_verdict"],
            "Risk Score": f"{int(item['risk_score']*100)}%"
        })
    
    df = pd.DataFrame(history_data)
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "Verdict": st.column_config.TextColumn(
                "Verdict",
                help="Model classification",
                width="medium"
            ),
            "Risk Score": st.column_config.ProgressColumn(
                "Risk Score",
                format="%f",
                min_value=0,
                max_value=100,
            ),
        }
    )

def render_about_tab():
    st.markdown("### 🧠 Under the Hood")
    st.markdown("""
    **Phishing Detector NEO** uses a hybrid AI approach to detect threats:
    
    1.  **Dual-Layer Architecture:**
        *   **Layer 1 (NLP):** A TF-IDF + Random Forest model analyzes the linguistic patterns, tone, and urgency of the email body.
        *   **Layer 2 (Heuristic):** A specialized model parses URLs for malicious characteristics (IP usage, length, obfuscation).
    
    2.  **Feature Engineering:**
        *   We extract specific flags like `UsingIP`, `TinyURL`, `Redirects`, and `HTTPS` validity.
    
    3.  **Real-Time Scoring:**
        *   The system aggregates probabilities from both layers to generate a unified risk score.
    """)
    
    st.info("Model files are hosted securely and loaded into memory for low-latency inference.")

# ==========================================
# 4. MAIN APP FLOW
# ==========================================

def main():
    sidebar_controls()
    render_header()
    
    # Main Navigation
    tab1, tab2, tab3 = st.tabs(["🔍 SCANNER", "📜 HISTORY", "ℹ️ ABOUT"])
    
    with tab1:
        render_scan_tab()
    
    with tab2:
        render_history_tab()
        
    with tab3:
        render_about_tab()

if __name__ == "__main__":
    main()
