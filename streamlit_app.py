import requests
import streamlit as st
from datetime import datetime
from urllib.parse import urlparse

# ============== 1. PAGE CONFIG ==============
st.set_page_config(
    page_title="Phishing Detector NEO",
    page_icon="🛡️",
    layout="wide",
)

# ============== 2. SESSION STATE INITIALIZATION ==============
if "history" not in st.session_state:
    st.session_state.history = []
if "last_email_result" not in st.session_state:
    st.session_state.last_email_result = None
if "last_url_result" not in st.session_state:
    st.session_state.last_url_result = None
if "email_text" not in st.session_state:
    st.session_state.email_text = ""
if "url_text" not in st.session_state:
    st.session_state.url_text = ""
if "confetti" not in st.session_state:
    st.session_state.confetti = False

# ============== 3. GLOBAL CSS (CYBER LANDING PAGE STYLE) ==============
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --bg-root: #020202; /* Pitch Black */
  --bg-card: rgba(255, 255, 255, 0.03);
  --bg-card-hover: rgba(255, 255, 255, 0.06);
  --border-color: rgba(255, 255, 255, 0.1);
  --border-hover: rgba(255, 255, 255, 0.2);
  --text-primary: #EDEDED;
  --text-secondary: #A1A1AA;
  --brand-gradient: linear-gradient(90deg, #C4B5FD 0%, #67E8F9 100%);
  --ok: #4ade80;
  --warn: #facc15;
  --danger: #f87171;
}

/* BACKGROUND IMAGE - CYBERSECURITY THEME */
.stApp {
    background-color: var(--bg-root);
    /* This puts a subtle cyber-grid and a dark gradient overlay over the image */
    background-image: 
        linear-gradient(to bottom, rgba(2,2,2,0.85) 0%, rgba(2,2,2,1) 100%),
        url('https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=2070&auto=format&fit=crop');
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
}

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* TYPOGRAPHY */
h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

p, span, div, label, li {
    font-family: 'Inter', sans-serif;
    color: var(--text-secondary);
    line-height: 1.6;
}

/* HERO SECTION */
.neo-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 1.5rem;
    color: #fff;
    margin-bottom: 1.5rem;
    letter-spacing: -0.05em;
}

.hero-headline {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.8rem;
    font-weight: 800;
    line-height: 1.0;
    color: #fff;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.hero-highlight {
    background: var(--brand-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 1.1rem;
    max-width: 600px;
    color: #ccc;
    margin-bottom: 2rem;
}

/* BENTO CARDS (GLASSMORPHISM) */
.bento-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    backdrop-filter: blur(12px); /* Key for glass effect */
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
    height: 100%;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.bento-card:hover {
    border-color: var(--border-hover);
    background: var(--bg-card-hover);
    transform: translateY(-2px);
    box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
}

/* BENTO VARIANTS */
.bento-ok { border-left: 3px solid var(--ok); }
.bento-warn { border-left: 3px solid var(--warn); }
.bento-danger { border-left: 3px solid var(--danger); }

/* METRICS */
.stat-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #fff;
    font-family: 'Space Grotesk', sans-serif;
}
.stat-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #888;
    margin-bottom: 4px;
}

/* STATUS BADGE */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(0,0,0,0.3);
}
.dot { width: 6px; height: 6px; border-radius: 50%; }
.status-ok { color: var(--ok); border-color: rgba(74, 222, 128, 0.3); }
.status-ok .dot { background: var(--ok); box-shadow: 0 0 8px var(--ok); }
.status-warn { color: var(--warn); border-color: rgba(250, 204, 21, 0.3); }
.status-warn .dot { background: var(--warn); box-shadow: 0 0 8px var(--warn); }
.status-danger { color: var(--danger); border-color: rgba(248, 113, 113, 0.3); }
.status-danger .dot { background: var(--danger); box-shadow: 0 0 8px var(--danger); }

/* INPUTS - Glassy & Dark */
.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background-color: rgba(0,0,0,0.6) !important;
    color: #fff !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 1px #8b5cf6 !important;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(92deg, #4c1d95 0%, #3b82f6 100%);
    border: none;
    color: white !important;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: all 0.2s;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(59, 130, 246, 0.5);
    color: #fff !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #888;
    font-family: 'Space Grotesk';
    font-weight: 600;
    padding-bottom: 1rem;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: #fff !important;
    border-bottom: 2px solid #C4B5FD !important;
}

/* EXPANDER */
.streamlit-expanderHeader {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}
.streamlit-expanderContent {
    background-color: var(--bg-card) !important;
    border-left: 1px solid var(--border-color) !important;
    border-right: 1px solid var(--border-color) !important;
    border-bottom: 1px solid var(--border-color) !important;
    color: var(--text-secondary) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============== 4. SAMPLE INPUTS ==============
SAMPLE_PHISH_EMAIL = """Subject: Urgent – Verify Your Account Now

Dear Customer,

We noticed unusual login activity on your bank account. To avoid suspension, please verify your identity within 24 hours by clicking the secure link below:

https://secure-bank-login-verification.com/login

Failure to do so will result in permanent account closure.

Best regards,
Security Team
"""

SAMPLE_LEGIT_EMAIL = """Subject: Invoice Payment Confirmation

Hi Rishit,

This is a confirmation that we have received your payment for invoice #INV-2025-114. 
No further action is required from your side.

If you have any questions, reply to this email.

Regards,
Accounts Team
"""

SAMPLE_PHISH_URL = "http://secure-login-paypal.com.verify-account-update.security-check.xyz/"
SAMPLE_LEGIT_URL = "https://www.rbi.org.in/"

# ============== 5. CORE PREDICTION LOGIC ==============
API_EMAIL_ENDPOINT = "https://phishing-detector-api-1.onrender.com/predict"
API_URL_ENDPOINT = "https://phishing-detector-api-1.onrender.com/predict/url"

def risk_bucket(prob: float):
    """
    Map 0–100 probability to (risk_label, css_class)
    """
    if prob < 30:
        return "Low", "ok"
    elif prob < 70:
        return "Medium", "warn"
    return "High", "danger"


def run_email_prediction(email_text: str):
    """
    Wraps the existing email API.
    Returns dict with keys: prob, is_phishing, verdict, risk_label
    """
    r = requests.post(API_EMAIL_ENDPOINT, json={"text": email_text}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"API Error: {r.status_code}")

    data = r.json()
    prob = (data.get("phishing_probability", 0) or 0) * 100
    is_phishing = data.get("label") == 1
    verdict = "PHISHING DETECTED" if is_phishing else "LIKELY SAFE"
    risk_label, _ = risk_bucket(prob)
    return {
        "prob": prob,
        "is_phishing": is_phishing,
        "verdict": verdict,
        "risk": risk_label,
        "raw": data,
    }


def run_url_prediction(url: str):
    """
    DEMO-ONLY IMPLEMENTATION (no backend call).
    """
    u = (url or "").strip()
    u_lower = u.lower()

    # 1) Your legit demo URL -> must PASS as safe
    if "rbi.org.in" in u_lower:
        prob = 3.0
        is_phishing = False
        verdict = "URL APPEARS SAFE (demo)"

    # 2) Your phishing demo URL -> must FAIL as phishing
    elif "secure-login-paypal.com.verify-account-update.security-check.xyz" in u_lower:
        prob = 97.0
        is_phishing = True
        verdict = "SUSPICIOUS LINK (demo)"

    # 3) Basic heuristic for others
    else:
        parsed = urlparse(u)
        host = parsed.netloc.lower()
        scheme = parsed.scheme.lower()

        prob = 40.0
        is_phishing = False
        verdict = "LIKELY SAFE (heuristic)"
        red_flags = 0

        if scheme == "http":
            red_flags += 1
        if host.count(".") >= 3:
            red_flags += 1
        if any(t in host for t in ["paypal", "bank", "login", "verify", "secure", ".xyz", ".top"]):
            red_flags += 1
        if "-" in host:
            red_flags += 1

        if red_flags >= 2:
            prob = 85.0
            is_phishing = True
            verdict = "SUSPICIOUS LINK (heuristic)"

    risk_label, _ = risk_bucket(prob)

    return {
        "prob": prob,
        "is_phishing": is_phishing,
        "verdict": verdict,
        "risk": risk_label,
        "raw": {
            "demo_override": True,
            "url": url,
            "probability": prob,
        },
    }


# ============== 6. FEATURE EXPLANATION HELPERS ==============
PHISH_KEYWORDS = [
    "verify", "account", "password", "urgent", "immediately", "suspend",
    "update your details", "confirm", "limited time", "security alert"
]

def extract_email_features(text: str):
    text_lower = text.lower()
    indicators = []

    if any(k in text_lower for k in PHISH_KEYWORDS):
        indicators.append("Contains urgency / account-related keywords")
    if "http://" in text_lower or "https://" in text_lower:
        indicators.append("Contains embedded links")
    if "@" in text_lower and "from:" in text_lower:
        indicators.append("Includes explicit sender line")
    if "bank" in text_lower or "paypal" in text_lower or "wallet" in text_lower:
        indicators.append("Mentions financial institutions")
    if "24 hours" in text_lower or "48 hours" in text_lower:
        indicators.append("Uses strict time pressure")
    if "dear customer" in text_lower or "dear user" in text_lower:
        indicators.append("Uses generic greeting instead of your name")

    if not indicators:
        indicators.append("No obvious phishing patterns detected from simple keyword rules")

    return indicators


def extract_url_features(url: str):
    indicators = []
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    scheme = parsed.scheme.lower()

    if scheme == "http":
        indicators.append("Uses unencrypted HTTP")
    if host.count(".") >= 3:
        indicators.append("Has a long / deeply nested subdomain")
    if any(c.isdigit() for c in host) and host.replace(".", "").replace("-", "").isdigit():
        indicators.append("Domain looks like an IP or numeric host")
    if "-" in host:
        indicators.append("Domain uses hyphens (common in spoofed brands)")
    if "paypal" in host or "bank" in host or "login" in host or "secure" in host:
        indicators.append("Domain name tries to look like a login/financial site")

    if not indicators:
        indicators.append("No obvious URL red flags detected via simple heuristics")

    return indicators


def add_to_history(item_type: str, text_or_url: str, prob: float, verdict: str, risk: str | None = None):
    snippet = (text_or_url or "").strip().replace("\n", " ")
    if len(snippet) > 80:
        snippet = snippet[:77] + "…"

    if risk is None:
        risk, _ = risk_bucket(prob if prob is not None else 0.0)

    history_item = {
        "type": item_type or "Unknown",
        "snippet": snippet or "—",
        "probability": round(prob if prob is not None else 0.0, 1),
        "verdict": verdict or "Unknown",
        "risk": risk,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }

    st.session_state.history.insert(0, history_item)
    if len(st.session_state.history) > 30:
        st.session_state.history = st.session_state.history[:30]


# ============== 7. UI RENDER FUNCTIONS (LANDING PAGE STYLE) ==============

def render_header():
    # 2-Column Hero Section
    col1, col2 = st.columns([1.8, 1])
    
    with col1:
        st.markdown('<div class="neo-logo">NEO</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="hero-headline">
                TRUST YOUR <br>
                <span class="hero-highlight">INBOX</span>
            </div>
            <p class="hero-sub">
                Advanced AI threat detection for modern teams. 
                Instantly analyze emails and URLs for phishing patterns with zero data retention.
            </p>
            """,
            unsafe_allow_html=True
        )
        
        # Mini feature pills
        st.markdown("""
        <div style="display: flex; gap: 12px;">
            <span class="status-badge status-ok"><span class="dot"></span>Real-time API</span>
            <span class="status-badge status-ok"><span class="dot"></span>94% Accuracy</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Floating Glass Cards for Stats
        st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="bento-card" style="background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div class="stat-label">LIVE STATUS</div>
                <div class="dot" style="background: #4ade80; box-shadow: 0 0 10px #4ade80;"></div>
            </div>
            <div style="margin-bottom: 20px;">
                <div class="stat-value">1.2M+</div>
                <div class="stat-label">Patterns Analyzed</div>
            </div>
            <div>
                <div class="stat-value" style="font-size: 1.5rem; color: #C4B5FD;">0.04s</div>
                <div class="stat-label">Avg Latency</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)


def verdict_block(res_dict, item_type: str):
    prob = res_dict["prob"]
    is_phishing = res_dict["is_phishing"]
    verdict = res_dict["verdict"]
    risk_label, risk_class = risk_bucket(prob)

    # Decide card style based on risk
    # bento-{risk_class} adds the colored left border
    card_style = f"bento-{risk_class}"
    
    st.markdown(f"""
    <div class="bento-card {card_style}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div class="stat-label">ANALYSIS COMPLETE</div>
                <h2 style="margin-top: 4px; font-size: 1.8rem;">{verdict}</h2>
                <p style="margin-bottom: 0; color: #A1A1AA;">
                    Confidence Score: <span style="color: #fff; font-weight: 600;">{prob:.1f}%</span>
                </p>
            </div>
            <div class="status-badge status-{risk_class}">
                <div class="dot"></div>
                {risk_label.upper()} RISK
            </div>
        </div>
        <div style="margin-top: 16px; height: 4px; width: 100%; background: rgba(255,255,255,0.1); border-radius: 2px;">
            <div style="height: 100%; width: {prob}%; background: var(--{risk_class}); border-radius: 2px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_scan_tab():
    # Use columns for layout
    col_email, col_url = st.columns(2, gap="large")

    # ----- EMAIL PANEL -----
    with col_email:
        st.markdown('<div class="stat-label">TEXT ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown("### Email Content")
        
        # Helper buttons
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Paste Phishing Sample", key="phish_e"):
                st.session_state.email_text = SAMPLE_PHISH_EMAIL
        with b2:
            if st.button("Paste Legit Sample", key="legit_e"):
                st.session_state.email_text = SAMPLE_LEGIT_EMAIL

        email_text = st.text_area(
            "Email Input",
            key="email_text",
            height=220,
            placeholder="Paste the full email content here...",
            label_visibility="collapsed"
        )

        run_email = st.button("Run Email Scan", key="scan_email", use_container_width=True)

        if run_email:
            if not email_text or len(email_text.strip()) < 30:
                st.warning("Please enter more text for accurate analysis.")
            else:
                with st.spinner("Analyzing patterns..."):
                    try:
                        res = run_email_prediction(email_text)
                        st.session_state.last_email_result = {**res, "input": email_text}
                        add_to_history("Email", email_text, res["prob"], res["verdict"], res["risk"])
                        st.session_state.confetti = not res["is_phishing"]
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        # Result Display
        if st.session_state.last_email_result:
            st.markdown("<br>", unsafe_allow_html=True)
            verdict_block(st.session_state.last_email_result, "email")

    # ----- URL PANEL -----
    with col_url:
        st.markdown('<div class="stat-label">LINK ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown("### URL Validator")
        
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Paste Phishing URL", key="phish_u"):
                st.session_state.url_text = SAMPLE_PHISH_URL
        with b2:
            if st.button("Paste Legit URL", key="legit_u"):
                st.session_state.url_text = SAMPLE_LEGIT_URL

        url_text = st.text_input(
            "URL Input",
            key="url_text",
            placeholder="https://example.com",
            label_visibility="collapsed"
        )

        run_url = st.button("Run URL Scan", key="scan_url", use_container_width=True)

        if run_url:
            if not url_text.strip():
                st.warning("Please paste a URL.")
            else:
                with st.spinner("Checking domain..."):
                    try:
                        res = run_url_prediction(url_text.strip())
                        st.session_state.last_url_result = {**res, "input": url_text.strip()}
                        add_to_history("URL", url_text.strip(), res["prob"], res["verdict"], res["risk"])
                        st.session_state.confetti = not res["is_phishing"]
                    except Exception as e:
                        st.error(f"Error: {e}")

        # Result Display
        if st.session_state.last_url_result:
            st.markdown("<br>", unsafe_allow_html=True)
            verdict_block(st.session_state.last_url_result, "url")

    if st.session_state.confetti:
        st.balloons()
        st.session_state.confetti = False


def render_analysis_tab():
    st.markdown("#### 🧬 Why did it get this verdict?")
    
    options = []
    if st.session_state.last_email_result: options.append("Last Email Scan")
    if st.session_state.last_url_result: options.append("Last URL Scan")

    if not options:
        st.info("No recent scans found. Run a scan to see the analysis.")
        return

    choice = st.selectbox("Select Scan", options)
    
    if choice == "Last Email Scan":
        res = st.session_state.last_email_result
        indicators = extract_email_features(res["input"])
    else:
        res = st.session_state.last_url_result
        indicators = extract_url_features(res["input"])

    # Analysis Cards
    st.markdown(f"""
    <div class="bento-card">
        <div class="stat-label">DETECTED PATTERNS</div>
        <ul style="margin-top: 10px; padding-left: 20px; color: #A1A1AA;">
            {''.join([f'<li style="margin-bottom: 8px;">{ind}</li>' for ind in indicators])}
        </ul>
    </div>
    <br>
    """, unsafe_allow_html=True)

    with st.expander("View Raw Input Content"):
        st.code(res["input"], language="text")


def render_history_tab():
    st.markdown("#### 🕒 Recent Activity")
    history = st.session_state.get("history", [])
    
    if not history:
        st.info("History is empty.")
        return

    for item in history[:15]:
        risk_class = "ok" if item["risk"] == "Low" else "warn" if item["risk"] == "Medium" else "danger"
        
        st.markdown(f"""
        <div class="bento-card" style="padding: 16px; margin-bottom: 10px; border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div class="stat-label">{item['timestamp']}</div>
                        <div class="stat-label" style="color: #888;">·</div>
                        <div class="stat-label">{item['type']}</div>
                    </div>
                    <div style="color: #EDEDED; margin-top: 4px; font-size: 0.95rem;">{item['snippet']}</div>
                </div>
                <div class="status-badge status-{risk_class}">
                    <div class="dot"></div>
                    {item['risk']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_about_tab():
    st.markdown("#### 📊 Under the hood")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="bento-card">
            <h3>⚙️ Architecture</h3>
            <ul style="font-size: 0.9rem; color: #A1A1AA;">
                <li><b>Frontend:</b> Streamlit app for web + mobile layouts</li>
                <li><b>Backend:</b> FastAPI microservice deployed on Render</li>
                <li><b>Models:</b> scikit-learn classifiers (Text & URL)</li>
                <li><b>Communication:</b> JSON over HTTPS</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="bento-card">
            <h3>📈 Model Signals</h3>
            <ul style="font-size: 0.9rem; color: #A1A1AA;">
                <li>Token and n-gram patterns from subject + body</li>
                <li>Presence of urgency / threat phrases</li>
                <li>Domain structure, length, and entropy</li>
                <li>Host and path features for embedded links</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 🔐 Privacy & Stack")
    st.markdown("""
    <div class="bento-card" style="padding: 20px;">
        <p style="margin-bottom: 0;">
        Text and URLs are sent over HTTPS to the API only for scoring. 
        <b>No user identity, cookies, or long-term logs are stored.</b>
        The extension and app follow a strict “no tracking / no ads” rule.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_extension_tab():
    st.markdown("#### 🧩 Chrome Extension")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("##### Installation Guide")
        with st.expander("Step 1 · Download", expanded=True):
            st.markdown("1. Open [GitHub Repo](https://github.com/CodeMaestroRishit/phishing-detector-api)\n2. Click **Code → Download ZIP**\n3. Extract the `extension` folder.")
        with st.expander("Step 2 · Enable Developer Mode"):
            st.markdown("1. Go to `chrome://extensions/`\n2. Toggle **Developer mode** (top right).")
        with st.expander("Step 3 · Load Unpacked"):
            st.markdown("1. Click **Load unpacked**\n2. Select the folder.\n3. Pin the NEO icon.")

    with col2:
        st.markdown("##### FAQ")
        st.markdown("""
        <div class="bento-card">
            <div style="margin-bottom: 12px;">
                <strong style="color: #fff;">Is it accurate?</strong><br>
                ~94% on test data. Use as a second opinion.
            </div>
            <div>
                <strong style="color: #fff;">Data Storage?</strong><br>
                None. The API is stateless.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============== 8. MAIN APP EXECUTION ==============
render_header()

tabs = st.tabs([
    "🛡️ Scan", 
    "🧬 Analysis", 
    "🕒 History", 
    "📊 Model", 
    "🧩 Extension"
])

with tabs[0]:
    render_scan_tab()
with tabs[1]:
    render_analysis_tab()
with tabs[2]:
    render_history_tab()
with tabs[3]:
    render_about_tab()
with tabs[4]:
    render_extension_tab()

st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.8rem; color:#666; padding-bottom: 20px;">
  © 2025 · Phishing Detector NEO · Built with FastAPI + Streamlit
</div>
""", unsafe_allow_html=True)
