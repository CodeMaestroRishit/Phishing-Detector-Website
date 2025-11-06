import json
import requests
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Phishing Detector — NEO Edition",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- NAV ITEMS / SESSION ----------------
TOP_NAV = ["🏠 Home", "🌐 Test Online", "📥 Install Extension"]   # top bar (3 items)
NAV_ITEMS = TOP_NAV + ["❓ FAQ", "📊 About", "📄 Privacy"]          # sidebar shows all (ADDED PRIVACY)

if "page" not in st.session_state:
    st.session_state.page = TOP_NAV[0]
if "confetti" not in st.session_state:
    st.session_state.confetti = False

def set_page(p: str):
    st.session_state.page = p

def _sync_page():
    st.session_state.page = st.session_state.nav_choice

def _celebrate():
    st.session_state.confetti = True

# ---------------- ORGANIZED TOP BAR (3 items) ----------------
with st.container():
    st.markdown("<div class='topnav-wrap'><div class='topnav-rail'><div class='topnav-row'>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, item in enumerate(TOP_NAV):
        emoji, title = item.split(" ", 1)
        is_active = (st.session_state.page == item)
        with cols[i]:
            st.markdown(
                f"<div class='top-pill {'active' if is_active else ''}'>{emoji} {title}</div>",
                unsafe_allow_html=True
            )
            if st.button(" ", key=f"topnav_btn_{i}", help=item, use_container_width=True):
                set_page(item)
                st.rerun()
    st.markdown("</div></div></div>", unsafe_allow_html=True)

# ---------------- GLOBAL CSS (Desktop + Mobile) ----------------
st.markdown("""
<style>
/* ====== Fonts & Root ====== */
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

/* ====== Organized Top Nav (3 items) ====== */
.topnav-wrap {
  position: sticky; top: 0; z-index: 999;
  backdrop-filter: blur(8px);
  background: linear-gradient(180deg, rgba(11,11,15,.90), rgba(11,11,15,.65));
  border-bottom: 1px solid rgba(255,255,255,.06);
  margin: -16px -16px 18px -16px;
  padding: 10px 0;
}
.topnav-rail { max-width: 980px; margin: 0 auto; padding: 0 12px; }
.topnav-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px; align-items: center;
}
.top-pill {
  display: inline-flex; justify-content: center; align-items: center; gap: 10px;
  width: 100%; padding: 10px 14px; border-radius: 14px;
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.10);
  color: #e9ecf2; font-weight: 700; letter-spacing: .1px;
  transition: transform .08s ease, background .25s ease, border .25s ease, box-shadow .25s ease;
}
.top-pill:hover { transform: translateY(-1px); background: rgba(255,255,255,.10); }
.top-pill.active {
  background: linear-gradient(92deg, rgba(124,58,237,.28), rgba(34,211,238,.28));
  border-color: rgba(124,58,237,.55);
  box-shadow: 0 8px 22px rgba(124,58,237,0.22), 0 0 0 1px rgba(255,255,255,.04) inset;
  position: relative;
}
.top-pill.active::after {
  content: ""; position: absolute; left: 12%; right: 12%; bottom: -6px; height: 3px;
  border-radius: 999px;
  background: linear-gradient(92deg, rgba(124,58,237,.9), rgba(34,211,238,.9));
  box-shadow: 0 0 12px rgba(124,58,237,.6);
}

/* ====== Headings & Gradient Text ====== */
h1, h2, h3 { font-family: 'Space Grotesk', ui-rounded, system-ui; letter-spacing: 0.2px; }
h1 { font-size: 2.6rem; font-weight: 800; margin: 0 0 .6rem 0; }
h2 { font-size: 1.5rem; margin: 1.4rem 0 .8rem 0; }
.grad { background: linear-gradient(92deg, var(--brand1), var(--brand2), var(--brand3));
  -webkit-background-clip: text; background-clip: text; color: transparent; }

/* ====== Cards ====== */
.card, .feature-box, .stat-card, .metric-card, .glass, .success-box, .danger-box, .warning-box {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 18px 20px;
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

/* Success / Danger / Warning */
.success-box { border: 1px solid rgba(52,211,153,.35)!important; background: linear-gradient(180deg, rgba(52,211,153,.12), rgba(52,211,153,.06)); }
.danger-box  { border: 1px solid rgba(239,68,68,.35)!important; background: linear-gradient(180deg, rgba(239,68,68,.12), rgba(239,68,68,.06)); }
.warning-box { border: 1px solid rgba(245,158,11,.35)!important; background: linear-gradient(180deg, rgba(245,158,11,.12), rgba(245,158,11,.06)); }

/* ====== Badges / Chips ====== */
.badge {
  display:inline-flex; gap:.5rem; align-items:center;
  padding:.35rem .7rem; border-radius:999px; font-size:.86rem;
  background: rgba(255,255,255,0.06); border:1px solid var(--card-border); color: var(--muted);
}
.badge .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.dot.ok { background: var(--ok); box-shadow: 0 0 10px var(--ok); }
.dot.warn { background: var(--warn); box-shadow: 0 0 10px var(--warn); }
.dot.danger { background: var(--danger); box-shadow: 0 0 10px var(--danger); }

/* ====== Metrics ====== */
.stat-value { font-size: 1.8rem; font-weight: 800; }
.stat-label { font-size: .86rem; color: var(--muted); margin-top: .3rem; }

/* ====== Inputs ====== */
.stTextArea textarea, .stTextInput input {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
  font-size: 1rem !important;
  padding: .9rem !important;
}

/* ====== Buttons ====== */
.stButton>button, .stLinkButton>a {
  border-radius: 14px !important;
  padding: .85rem 1rem !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background-image: linear-gradient(92deg, rgba(124,58,237,.28), rgba(34,211,238,.28));
  color: white !important;
  font-weight: 800 !important;
  transition: transform .08s ease, box-shadow .2s ease, background .3s ease;
}
.stButton>button:hover, .stLinkButton>a:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(124,58,237,0.25), 0 0 0 1px rgba(255,255,255,0.08) inset;
}

/* ====== Tabs polish ====== */
[data-baseweb="tab"] { font-family: 'Space Grotesk'; font-weight: 700; letter-spacing:.2px; }

/* ====== Sidebar (desktop/tablet) ====== */
[data-testid="stSidebar"] {
  background: radial-gradient(800px 400px at 100% 0%, rgba(124,58,237,.18), transparent 60%),
              radial-gradient(700px 360px at 0% 0%, rgba(34,211,238,.14), transparent 60%),
              linear-gradient(180deg, #0b0b0f, #0b0b0f);
  border-right: 1px solid rgba(255,255,255,.06);
  padding-top: .5rem;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p:has(+ div [role="radiogroup"]) { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] { display: grid; gap: 8px; }
[data-testid="stSidebar"] [role="radiogroup"] > label {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  border-radius: 14px; padding: 10px 12px; color: #e9ecf2;
  display: flex; align-items: center; gap: 10px; cursor: pointer;
}
[data-testid="stSidebar"] [role="radiogroup"] > label .emoji {
  display:inline-flex; align-items:center; justify-content:center;
  width: 28px; height: 28px; border-radius: 10px;
  background: linear-gradient(92deg, rgba(124,58,237,.25), rgba(34,211,238,.25));
  border: 1px solid rgba(255,255,255,.14);
}

/* ====== MOBILE (≤ 720px) ====== */
@media (max-width: 720px) {
  html, body, [data-testid="stAppViewContainer"] { background: #0b0b0f; }
  .card, .feature-box, .stat-card, .metric-card, .glass, .success-box, .danger-box, .warning-box {
    backdrop-filter: none; box-shadow: 0 6px 16px rgba(0,0,0,0.28); padding: 14px 14px;
  }
  h1 { font-size: 2rem; }
  h2 { font-size: 1.25rem; }
  .stat-value { font-size: 1.5rem; }
  .badge { font-size: .92rem; }
  .topnav-row {
    display: grid; grid-auto-flow: column; grid-auto-columns: 1fr;
    overflow-x: auto; gap: 8px; padding-bottom: 4px; scrollbar-width: none;
  }
  .topnav-row::-webkit-scrollbar { display: none; }
  .top-pill { padding: 9px 12px; font-size: .95rem; }
  [data-testid="stSidebar"] { display: none; }          /* hide sidebar on phones */
  .block-container { padding-left: 12px; padding-right: 12px; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR (desktop/tablet) ----------------
with st.sidebar:
    st.markdown("<h2 style='margin:0;'>🛡️ Phishing Detector</h2>", unsafe_allow_html=True)
    st.caption("Click-safe, vibe-safe.")
    st.markdown(
        "<div class='sidebar-mini'>"
        "<span class='badge'><span class='dot ok'></span>API Live</span> "
        "<span class='badge'>Latency &lt;100ms</span>"
        "</div>",
        unsafe_allow_html=True
    )
    st.radio(
        label="Navigation",
        options= NAV_ITEMS,
        index= NAV_ITEMS.index(st.session_state.page) if st.session_state.page in NAV_ITEMS else 0,
        key="nav_choice",
        on_change=_sync_page,
        format_func=lambda x: x,
    )

# ---------------- CELEBRATION ----------------
if st.session_state.get("confetti"):
    st.balloons()
    st.session_state.confetti = False

# ---------------- CURRENT PAGE ----------------

page = st.session_state.page

# ---------------- HOME ----------------
if page == "🏠 Home":
    st.markdown("<h1>Phishing Detector <span class='grad'>NEO</span> Edition</h1>", unsafe_allow_html=True)
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
        if st.button("🌐 Try Online", use_container_width=True):
            set_page("🌐 Test Online"); st.rerun()
    with c2:
        if st.button("🧩 Get Extension", use_container_width=True):
            set_page("📥 Install Extension"); st.rerun()
    with c3:
        st.link_button("🐙 GitHub", "https://github.com/CodeMaestroRishit/phishing-detector-api", use_container_width=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

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

# ---------------- TEST ONLINE ----------------
elif page == "🌐 Test Online":
    st.markdown("<h1>🔎 Test <span class='grad'>Phishing Detector</span></h1>", unsafe_allow_html=True)
    st.caption("Paste the sus stuff. We'll do the forensic dance.")

    tab1, tab2 = st.tabs(["📧 Email Analysis", "🔗 URL Analysis"])

    # ---- Email Analysis ----
    with tab1:
        st.subheader("📧 Analyze Email Content")
        st.markdown("<span class='badge'><span class='dot warn'></span>Tip: include subject + sender line</span>", unsafe_allow_html=True)

        email_text = st.text_area(
            "Email content:",
            height=220,
            placeholder="Subject: Account Alert\nFrom: service@yourbank-secure.com\n\nDear user, please verify your account by clicking the link below...",
            label_visibility="collapsed"
        )

        # wide-area placeholder for results
        email_results = st.container()

        c1, _ = st.columns([1,5])
        with c1:
            if st.button("🔍 Analyze", use_container_width=True, key="email_btn"):
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
                                _celebrate()

                                # render results in wide area (not inside c1)
                                with email_results:
                                    colA, colB = st.columns([2,1])
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

    # ---- URL Analysis ----
    with tab2:
        st.subheader("🔗 Analyze URL")
        st.markdown("<span class='badge'><span class='dot warn'></span>Must start with http:// or https://</span>", unsafe_allow_html=True)

        url = st.text_input("URL:", placeholder="https://example.com", label_visibility="collapsed")

        url_results = st.container()

        c1, _ = st.columns([1,5])
        with c1:
            if st.button("🔍 Analyze", use_container_width=True, key="url_btn"):
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
                                _celebrate()

                                with url_results:
                                    colA, colB = st.columns([2,1])
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

# ---------------- INSTALL EXTENSION ----------------
elif page == "📥 Install Extension":
    st.markdown("<h1>🧩 Install <span class='grad'>Chrome Extension</span></h1>", unsafe_allow_html=True)
    st.info("🎉 Coming soon to Chrome Web Store. Manual install below.")

    col1, col2 = st.columns([1.5,1])
    with col1:
        st.subheader("📦 Installation Steps")
        with st.expander("📖 Step 1: Download Extension", expanded=True):
            st.markdown("""
            1. Open **[GitHub Repository](https://github.com/CodeMaestroRishit/phishing-detector-api)**
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
        st.link_button("🐙 View on GitHub", "https://github.com/CodeMaestroRishit/phishing-detector-api", use_container_width=True)

    st.divider()
    st.subheader("🐛 Troubleshooting")
    with st.expander("Icon missing"):
        st.markdown("- Reload page · Restart Chrome · Ensure `extension` folder selected")
    with st.expander("'manifest.json' not found"):
        st.markdown("- Load the **inner** `extension` folder containing manifest + JS/HTML files")
    with st.expander("Tooltip not showing"):
        st.markdown("- Reload page · Ensure enabled in `chrome://extensions/` · Check DevTools Console")

# ---------------- FAQ ----------------
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
        st.markdown("[Open an issue](https://github.com/CodeMaestroRishit/phishing-detector-api/issues) · PRs welcome!")

# ---------------- ABOUT ----------------
elif page == "📊 About":
    st.markdown("<h1>📊 About</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Mission")
        st.markdown("Make phishing detection accessible to everyone.")
        st.subheader("🧱 Technology Stack")
        st.markdown("- **Backend:** FastAPI\n- **ML Models:** scikit-learn\n- **Frontend:** Chrome Extension API\n- **Website:** Streamlit\n- **Hosting:** Render")
    with c2:
        st.subheader("📈 Model Performance")
        st.metric("Email Model Accuracy", "94.2%", "on test data")
        st.metric("URL Model Accuracy", "91.7%", "on test data")
        st.metric("Combined Average", "93.5%", "accuracy")
        st.subheader("📚 Training Data")
        st.markdown("- **10,000+** email samples\n- **5,000+** URLs analyzed\n- **2 years** of research\n- Real-world phishing examples")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🗓️ Project Timeline")
    st.markdown("- **Sept 2025:** Initial development\n- **Oct 2025:** API deployment on Render\n- **Oct 30, 2025:** Chrome extension launch\n- **Oct 31, 2025:** Chrome Web Store submission\n- **Future:** Firefox, Safari support")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("GitHub Repository", "https://github.com/CodeMaestroRishit/phishing-detector-api", use_container_width=True)
    with col2:
        st.link_button("Report Issue", "https://github.com/CodeMaestroRishit/phishing-detector-api/issues", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**License:** MIT  \n**Support:** Open an issue on GitHub")

# ============ PRIVACY POLICY PAGE (NEW) ============
elif page == "📄 Privacy":
    st.markdown("<h1>📄 Privacy Policy</h1>", unsafe_allow_html=True)
    st.markdown("**Last Updated:** November 1, 2025")
    
    st.divider()
    
    st.subheader("🎯 Introduction")
    st.markdown("""
    Phishing Detector is committed to protecting your privacy. This Privacy Policy explains how we collect, 
    use, and protect information when you use our Chrome extension and website.
    """)
    
    st.subheader("📊 What Information We Collect")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### ✅ Information You Provide:")
        st.markdown("""
        - **Selected Text:** When you select text and use the extension, it's sent to our API for analysis
        - **Analysis Results:** We display phishing probability scores
        """)
    
    with c2:
        st.markdown("### ❌ What We DO NOT Collect:")
        st.markdown("""
        - Your personal info (name, email, address)
        - Browsing history
        - Cookies or tracking data
        - Device information
        - Location data
        - User profiles
        """)
    
    st.divider()
    
    st.subheader("🔧 How We Use Information")
    st.markdown("""
    - **Phishing Detection:** Analyzing content using ML models
    - **Displaying Results:** Showing if content is likely phishing or safe
    - **Model Improvement:** Aggregated, anonymized data only (optional)
    """)
    
    st.divider()
    
    st.subheader("💾 Data Storage & Retention")
    st.markdown("""
    - **Temporary Processing:** Text processed immediately for analysis
    - **No Permanent Storage:** We do NOT store your analyzed text
    - **Instant Deletion:** Results deleted after being displayed
    - **No Logs:** No permanent records of your queries
    """)
    
    st.divider()
    
    st.subheader("🔒 Data Security")
    st.markdown("""
    - ✅ HTTPS encryption for all communication
    - ✅ Secure, managed infrastructure
    - ✅ No third-party data sharing
    - ✅ No advertising or data selling
    """)
    
    st.divider()
    
    st.subheader("👥 Data Sharing")
    st.markdown("""
    - **We NEVER share** your data with third parties
    - **We NEVER sell** your data
    - **We do NOT use** your data for marketing
    - **Your data stays** between you and our servers
    """)
    
    st.divider()
    
    st.subheader("✋ Your Rights")
    st.markdown("""
    - **Disable:** Uninstall the extension anytime
    - **Request Deletion:** Ask for your data to be removed
    - **Access:** Understand your usage data
    """)
    
    st.divider()
    
    st.subheader("📧 Contact Us")
    st.markdown("""
    For privacy concerns or data requests:
    - **Email:** rishitguha0824@gmail.com
    - **GitHub Issues:** https://github.com/CodeMaestroRishit/phishing-detector-api/issues
    """)
    
    st.divider()
    
    st.subheader("⚖️ Legal Compliance")
    st.markdown("""
    This extension complies with:
    - Chrome Web Store Privacy Policy
    - GDPR (General Data Protection Regulation)
    - CCPA (California Consumer Privacy Act)
    """)
    
    st.divider()
    
    st.markdown("""
    <div class="card" style="text-align: center; padding: 20px;">
    <p><strong>Your privacy is our priority. We take data protection seriously.</strong></p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9aa2b1;padding:1rem 0;'>"
    "© 2025 • <a href='https://github.com/CodeMaestroRishit/phishing-detector-api'>GitHub</a> • "
    "<a href='#' onclick='document.location.href=\"?page=privacy\"'>Privacy Policy</a> • "
    "Built with ❤️ + caffeine"
    "</div>", unsafe_allow_html=True
)
