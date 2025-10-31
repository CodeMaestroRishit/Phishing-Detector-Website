import streamlit as st
import requests
from datetime import datetime
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Phishing Detector — GenZ Edition",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SESSION STATE NAV ----------
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# keep sidebar radio & session in sync
def set_page():
    st.session_state.page = st.session_state.nav_choice

# ---------- THEME / CSS ----------
st.markdown("""
<style>
/* Fonts */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root{
  --bg: #0b0b0f;
  --card: rgba(255,255,255,0.06);
  --card-border: rgba(255,255,255,0.15);
  --text: #f6f7fb;
  --muted: #b9bed3;
  --brand1: #7c3aed;
  --brand2: #22d3ee;
  --brand3: #f472b6;
  --ok: #34d399;
  --warn: #f59e0b;
  --danger: #ef4444;
}

html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at -10% 0%, rgba(124,58,237,0.18), transparent 60%),
              radial-gradient(900px 500px at 110% 10%, rgba(34,211,238,0.18), transparent 60%),
              linear-gradient(180deg, #0b0b0f 0%, #0b0b0f 100%);
  color: var(--text);
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

section.main > div { max-width: 1200px; margin: 0 auto; }

/* Headings */
h1, h2, h3 { font-family: 'Space Grotesk', ui-rounded, system-ui; letter-spacing: 0.2px; }
h1 { font-size: 2.8rem; font-weight: 700; margin: 0 0 .6rem 0; }
h2 { font-size: 1.6rem; margin: 1.6rem 0 .8rem 0; }

/* Gradient text */
.grad {
  background: linear-gradient(92deg, var(--brand1), var(--brand2), var(--brand3));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* Cards (glassmorphism) */
.card, .feature-box, .stat-card, .metric-card, .glass {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 18px 20px;
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

/* Chips & badges */
.badge {
  display:inline-flex; gap:.5rem; align-items:center;
  padding:.35rem .7rem; border-radius:999px; font-size:.82rem;
  background: rgba(255,255,255,0.06); border:1px solid var(--card-border); color: var(--muted);
}
.badge .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.dot.ok { background: var(--ok); box-shadow: 0 0 10px var(--ok); }
.dot.warn { background: var(--warn); box-shadow: 0 0 10px var(--warn); }
.dot.danger { background: var(--danger); box-shadow: 0 0 10px var(--danger); }

/* CTA buttons */
.stButton>button, .stLinkButton>a {
  border-radius: 12px !important;
  padding: .7rem 1rem !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background-image: linear-gradient(92deg, rgba(124,58,237,.25), rgba(34,211,238,.25));
  color: white !important;
  transition: transform .08s ease, box-shadow .2s ease, background .3s ease;
}
.stButton>button:hover, .stLinkButton>a:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(124,58,237,0.25), 0 0 0 1px rgba(255,255,255,0.08) inset;
}

/* Danger / success / warn */
.success-box { border: 1px solid rgba(52,211,153,.35)!important; background: linear-gradient(180deg, rgba(52,211,153,.12), rgba(52,211,153,.06)); border-radius:16px; padding:16px 18px; }
.danger-box { border: 1px solid rgba(239,68,68,.35)!important; background: linear-gradient(180deg, rgba(239,68,68,.12), rgba(239,68,68,.06)); border-radius:16px; padding:16px 18px; }
.warning-box { border: 1px solid rgba(245,158,11,.35)!important; background: linear-gradient(180deg, rgba(245,158,11,.12), rgba(245,158,11,.06)); border-radius:16px; padding:16px 18px; }

/* Stat value */
.stat-value { font-size: 1.9rem; font-weight: 700; }
.stat-label { font-size: .85rem; color: var(--muted); margin-top: .4rem; }

/* Tabs polish */
[data-baseweb="tab"] { font-family: 'Space Grotesk'; font-weight: 600; letter-spacing:.2px; }

/* Sidebar polish */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(124,58,237,.15), rgba(34,211,238,.1));
  border-right: 1px solid rgba(255,255,255,.08);
}
.sidebar-card { background: rgba(0,0,0,.15); border:1px solid rgba(255,255,255,.12); border-radius:14px; padding:14px; }

/* Inputs */
.stTextArea textarea, .stTextInput input {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
}

/* Small utility */
.kbd { padding:.2rem .45rem; border-radius:6px; border:1px solid rgba(255,255,255,.2); background:rgba(255,255,255,.06); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.sep { height: 8px; }
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:.2rem;'>🛡️ Phishing Detector</h2>", unsafe_allow_html=True)
    st.caption("Stay click-safe, stay vibe-safe.")
    st.markdown(
        f"<div class='sidebar-card'><span class='badge'><span class='dot ok'></span>API status: Live</span><div class='sep'></div>"
        f"<div class='badge'><span class='dot ok'></span>Latency: &lt;100ms</div></div>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.radio(
        "Navigation",
        ["🏠 Home", "🌐 Test Online", "📥 Install Extension", "❓ FAQ", "📊 About"],
        key="nav_choice",
        on_change=set_page
    )
    st.markdown("---")
    st.markdown("**Links:**  \n[GitHub](https://github.com/yourusername/phishing-detector) · [Report Issue](https://github.com/yourusername/phishing-detector/issues)")

page = st.session_state.page

# ---------- HOME ----------
if page == "🏠 Home":
    st.markdown("<h1>Phishing Detector <span class='grad'>Gen-Z</span> Edition</h1>", unsafe_allow_html=True)
    st.markdown("### ⚡ AI-powered, privacy-first, and ridiculously fast")

    st.markdown(
        "<div class='card'>"
        "<div class='badge'><span class='dot ok'></span>Real-time detection</div> "
        "<div class='badge'><span class='dot warn'></span>No tracking</div> "
        "<div class='badge'><span class='dot ok'></span>Open-source</div>"
        "</div>", unsafe_allow_html=True
    )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌐 Try Online", use_container_width=True, type="primary"):
            st.session_state.page = "🌐 Test Online"
            st.experimental_rerun()
    with c2:
        if st.button("🧩 Get Extension", use_container_width=True):
            st.session_state.page = "📥 Install Extension"
            st.experimental_rerun()
    with c3:
        st.link_button("🐙 GitHub", "https://github.com/yourusername/phishing-detector", use_container_width=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("<div class='stat-card'><div class='stat-value'>94.2%</div><div class='stat-label'>Accuracy</div></div>", unsafe_allow_html=True)
    with s2:
        st.markdown("<div class='stat-card'><div class='stat-value'>&lt;100ms</div><div class='stat-label'>Response Time</div></div>", unsafe_allow_html=True)
    with s3:
        st.markdown("<div class='stat-card'><div class='stat-value'>10K+</div><div class='stat-label'>Training Samples</div></div>", unsafe_allow_html=True)
    with s4:
        st.markdown("<div class='stat-card'><div class='stat-value'>$0</div><div class='stat-label'>Free Forever</div></div>", unsafe_allow_html=True)

    st.markdown("## ✨ Features")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("<div class='feature-box'><h3>⚡ Fast</h3><p>Instant vibes check for sus emails and links.</p></div>", unsafe_allow_html=True)
    with f2:
        st.markdown("<div class='feature-box'><h3>🕶️ Private</h3><p>No accounts. No logs. No ads.</p></div>", unsafe_allow_html=True)
    with f3:
        st.markdown("<div class='feature-box'><h3>🤖 Smart</h3><p>Dual models for email & URL detection.</p></div>", unsafe_allow_html=True)

# ---------- TEST ONLINE ----------
elif page == "🌐 Test Online":
    st.markdown("<h1>🔎 Test <span class='grad'>Phishing Detector</span></h1>", unsafe_allow_html=True)
    st.caption("Paste the sus stuff. We’ll do the forensic dance.")

    tab1, tab2 = st.tabs(["📧 Email Analysis", "🔗 URL Analysis"])

    # Email
    with tab1:
        st.subheader("📧 Analyze Email Content")
        st.markdown("<span class='badge'><span class='dot warn'></span>Tip: include subject + sender line</span>", unsafe_allow_html=True)
        email_text = st.text_area(
            "Email content:",
            height=250,
            placeholder="Subject: Account Alert\nFrom: service@yourbank-secure.com\n\nDear user, please verify your account by clicking the link below...",
            label_visibility="collapsed"
        )
        c1, _ = st.columns([1,5])
        with c1:
            if st.button("🔍 Analyze", use_container_width=True, type="primary", key="email_btn"):
                if not email_text:
                    st.error("❌ Please enter email content")
                elif len(email_text) < 30:
                    st.warning("⚠️ Please enter at least 30 characters")
                else:
                    with st.spinner("🔄 Analyzing…"):
                        try:
                            r = requests.post(
                                "https://phishing-detector-api-1.onrender.com/predict",
                                json={"text": email_text},
                                timeout=60
                            )
                            if r.status_code == 200:
                                data = r.json()
                                prob = (data.get("phishing_probability", 0) or 0) * 100
                                is_phishing = data.get("label") == 1

                                st.success("✅ Analysis Complete")
                                colA, colB = st.columns(2)

                                with colA:
                                    if is_phishing:
                                        st.markdown("""
                                        <div class="danger-box">
                                          <h3>🚨 PHISHING DETECTED</h3>
                                          <p>This email shows strong phishing signals.</p>
                                          <p><b>Do not</b> click links or download attachments.</p>
                                        </div>""", unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div class="success-box">
                                          <h3>🟢 LIKELY SAFE</h3>
                                          <p>No obvious phishing indicators found.</p>
                                          <p><b>Still verify</b> the sender before action.</p>
                                        </div>""", unsafe_allow_html=True)

                                with colB:
                                    st.metric("Phishing Probability", f"{prob:.1f}%")
                                    if prob < 30:
                                        st.markdown("<div class='badge'><span class='dot ok'></span>Risk: Low</div>", unsafe_allow_html=True)
                                    elif prob < 70:
                                        st.markdown("<div class='badge'><span class='dot warn'></span>Risk: Medium</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("<div class='badge'><span class='dot danger'></span>Risk: High</div>", unsafe_allow_html=True)

                            elif r.status_code == 503:
                                st.error("⏱️ API cold start — try again in a bit.")
                            else:
                                st.error(f"❌ API Error: {r.status_code}")
                        except requests.exceptions.Timeout:
                            st.error("⏱️ Request timed out. Try again shortly.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

    # URL
    with tab2:
        st.subheader("🔗 Analyze URL")
        st.markdown("<span class='badge'><span class='dot warn'></span>Must start with http:// or https://</span>", unsafe_allow_html=True)
        url = st.text_input("URL:", placeholder="https://example.com", label_visibility="collapsed")
        c1, _ = st.columns([1,5])
        with c1:
            if st.button("🔍 Analyze", use_container_width=True, type="primary", key="url_btn"):
                if not url:
                    st.error("❌ Please enter a URL")
                elif not url.startswith(("http://", "https://")):
                    st.error("❌ URL must start with http:// or https://")
                else:
                    with st.spinner("🔄 Analyzing…"):
                        try:
                            r = requests.post(
                                "https://phishing-detector-api-1.onrender.com/predict/url",
                                json={"url": url},
                                timeout=60
                            )
                            if r.status_code == 200:
                                data = r.json()
                                prob = (data["probabilities"]["phishing"] or 0) * 100
                                is_phishing = data["prediction"] == "phishing"

                                st.success("✅ Analysis Complete")
                                colA, colB = st.columns(2)

                                with colA:
                                    if is_phishing:
                                        st.markdown("""
                                        <div class="danger-box">
                                          <h3>⚠️ SUSPICIOUS LINK</h3>
                                          <p>This URL looks phishy.</p>
                                          <p><b>Avoid</b> opening or entering credentials.</p>
                                        </div>""", unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div class="success-box">
                                          <h3>🟢 URL APPEARS SAFE</h3>
                                          <p>No obvious phishing patterns detected.</p>
                                        </div>""", unsafe_allow_html=True)

                                with colB:
                                    st.metric("Phishing Probability", f"{prob:.1f}%")
                                    if prob < 30:
                                        st.markdown("<div class='badge'><span class='dot ok'></span>Risk: Low</div>", unsafe_allow_html=True)
                                    elif prob < 70:
                                        st.markdown("<div class='badge'><span class='dot warn'></span>Risk: Medium</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("<div class='badge'><span class='dot danger'></span>Risk: High</div>", unsafe_allow_html=True)
                            else:
                                st.error(f"❌ API Error: {r.status_code}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

# ---------- INSTALL EXTENSION ----------
elif page == "📥 Install Extension":
    st.markdown("<h1>🧩 Install <span class='grad'>Chrome Extension</span></h1>", unsafe_allow_html=True)
    st.info("🎉 Coming soon to Chrome Web Store. Manual install below.")

    col1, col2 = st.columns([1.5,1])
    with col1:
        st.subheader("📦 Installation Steps")
        with st.expander("📖 Step 1: Download Extension", expanded=True):
            st.markdown("""
            1. Open **[GitHub Repository](https://github.com/yourusername/phishing-detector)**
            2. Click **Code → Download ZIP**
            3. Extract, open the **`extension`** folder
            """)
        with st.expander("🔧 Step 2: Enable Developer Mode"):
            st.markdown("""
            1. Open **Chrome**
            2. Go to `chrome://extensions/`
            3. Toggle **Developer mode**
            """)
        with st.expander("📤 Step 3: Load Unpacked"):
            st.markdown("""
            1. Click **Load unpacked**
            2. Select the **`extension`** folder
            3. Done ✅
            """)
        with st.expander("🚀 Step 4: Use It"):
            st.markdown("""
            - Select suspicious text in Gmail/any site → Tooltip pops
            - 🟢 Green = Safe · 🔴 Red = Phishing
            - Or click the extension icon
            """)

    with col2:
        st.subheader("✨ Features")
        st.markdown("""
        - ✅ **Auto detection** on select  
        - 🌍 **Works everywhere** (Gmail, Outlook, web)  
        - ⚡ **One-click analysis**  
        - 🕶️ **No data collection**  
        - 🧪 **Open source**  
        - 💸 **Always free**
        """)
        st.link_button("🐙 View on GitHub", "https://github.com/yourusername/phishing-detector", use_container_width=True)

    st.divider()
    st.subheader("🐛 Troubleshooting")
    with st.expander("Icon missing"):
        st.markdown("- Reload page · Restart Chrome · Ensure `extension` folder selected")
    with st.expander("'manifest.json' not found"):
        st.markdown("- Load the **inner** `extension` folder containing manifest + JS/HTML files")
    with st.expander("Tooltip not showing"):
        st.markdown("- Reload page · Ensure enabled in `chrome://extensions/` · Check DevTools Console")

# ---------- FAQ ----------
elif page == "❓ FAQ":
    st.markdown("<h1>❓ FAQ</h1>", unsafe_allow_html=True)
    with st.expander("What is phishing?"):
        st.markdown("Tricking you into sharing sensitive info by pretending to be someone legit.")
    with st.expander("How accurate is it?"):
        st.markdown("**94.2%** on test data across 10k+ samples. Still verify senders—no AI is perfect.")
    with st.expander("Is my data safe?"):
        st.markdown("- HTTPS, no storage, no tracking, open source.")
    with st.expander("Offline?"):
        st.markdown("Needs internet to query the API.")
    with st.expander("Firefox/Safari?"):
        st.markdown("Chrome first. Others later.")
    with st.expander("Free?"):
        st.markdown("Forever free. No ads.")
    with st.expander("Report a bug / contribute?"):
        st.markdown("[Open an issue](https://github.com/yourusername/phishing-detector/issues) · PRs welcome!")

# ---------- ABOUT ----------
elif page == "📊 About":
    st.markdown("<h1>📊 About</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Mission")
        st.markdown("Make phishing detection accessible to everyone.")
        st.subheader("🧱 Stack")
        st.markdown("- **Backend:** FastAPI\n- **ML:** scikit-learn\n- **Frontend:** Chrome Extension API\n- **Website:** Streamlit\n- **Hosting:** Render")
    with c2:
        st.subheader("📈 Model Performance")
        st.metric("Email Model", "94.2%", "accuracy")
        st.metric("URL Model", "91.7%", "accuracy")
        st.metric("Combined", "93.5%", "accuracy")
        st.subheader("📚 Training Data")
        st.markdown("- **10,000+** emails\n- **5,000+** URLs\n- **2 years** research")

    st.subheader("🗓️ Timeline")
    st.markdown("- **Sept 2024:** Initial dev\n- **Oct 2024:** API on Render\n- **Oct 30, 2024:** Extension launch\n- **Oct 31, 2024:** Store submission\n- **Future:** Firefox, Safari")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9aa2b1;padding:1rem 0;'>"
    "© 2024 • <a href='https://github.com/yourusername/phishing-detector'>GitHub</a> • Built with ❤️ + caffeine"
    "</div>", unsafe_allow_html=True
)
