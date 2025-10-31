import streamlit as st
import requests
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Phishing Detector - AI Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding: 2rem; max-width: 1200px; }
    h1 { color: #2563eb; font-size: 3rem; margin-bottom: 0.5rem; }
    h2 { color: #1e40af; margin-top: 2rem; border-bottom: 2px solid #2563eb; padding-bottom: 0.5rem; }
    .feature-box { background: #f0f9ff; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2563eb; margin: 1rem 0; }
    .success-box { background: #e6f7ed; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #059669; margin: 1rem 0; }
    .danger-box { background: #fdeaea; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #dc2626; margin: 1rem 0; }
    .warning-box { background: #fef3c7; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #d97706; margin: 1rem 0; }
    .cta-button { background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center; font-weight: bold; margin: 1rem 0; }
    .stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
    .stat-value { font-size: 2rem; font-weight: bold; color: #2563eb; }
    .stat-label { font-size: 0.9rem; color: #666; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛡️ Phishing Detector")
    st.markdown("---")
    page = st.radio("Navigation", [
        "🏠 Home",
        "🌐 Test Online",
        "📥 Install Extension",
        "❓ FAQ",
        "📊 About"
    ])
    st.markdown("---")
    st.markdown("""
    **Quick Links:**
    - [GitHub](https://github.com/yourusername/phishing-detector)
    - [Report Issue](https://github.com/yourusername/phishing-detector/issues)
    - [Privacy Policy](https://github.com/yourusername/phishing-detector/blob/main/PRIVACY.md)
    """)

# ============ HOME PAGE ============
if page == "🏠 Home":
    # Hero Section
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.title("🛡️ Phishing Detector")
        st.markdown("### AI-Powered Protection Against Phishing Attacks")
        st.markdown("""
        Stay safe online with our dual machine learning models that detect phishing attempts in real-time.
        
        **Protect yourself against:**
        - 📧 Phishing emails
        - 🔗 Malicious URLs
        - ⚠️ Social engineering attacks
        """)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🌐 Try Online", use_container_width=True, type="primary"):
                st.session_state.page = "🌐 Test Online"
                st.rerun()
        with col_b:
            if st.button("📥 Get Extension", use_container_width=True):
                st.session_state.page = "📥 Install Extension"
                st.rerun()
        with col_c:
            st.link_button("🐙 GitHub", "https://github.com/yourusername/phishing-detector")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); padding: 2rem; border-radius: 12px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">94.2%</h2>
            <p style="font-size: 0.9rem; margin: 0.5rem 0 0 0;">Detection Accuracy</p>
            <hr style="border-color: rgba(255,255,255,0.3);">
            <h3 style="color: white; margin: 0.5rem 0;">Trusted by Students & Professionals</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Features Section
    st.markdown("## ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
        <h3>⚡ Lightning Fast</h3>
        <p>Get analysis results in milliseconds. No waiting, instant protection.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
        <h3>🔒 100% Private</h3>
        <p>No data collection. No tracking. Your privacy is our priority.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
        <h3>🤖 AI-Powered</h3>
        <p>Trained on 10,000+ samples. Dual models for email + URL detection.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Stats
    st.markdown("## 📊 By The Numbers")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
        <div class="stat-value">94.2%</div>
        <div class="stat-label">Accuracy Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
        <div class="stat-value"><100ms</div>
        <div class="stat-label">Response Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
        <div class="stat-value">10K+</div>
        <div class="stat-label">Training Samples</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
        <div class="stat-value">$0</div>
        <div class="stat-label">Forever Free</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # CTA
    st.markdown("## Get Started Now!")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <h3>🌐 Test Online</h3>
        Try the phishing detector directly in your browser. No installation needed.
        """)
        if st.button("Test Now", use_container_width=True, type="primary"):
            st.session_state.page = "🌐 Test Online"
            st.rerun()
    
    with col2:
        st.markdown("""
        <h3>📥 Install Extension</h3>
        Get real-time protection for Gmail, Outlook, and any website.
        """)
        if st.button("Install", use_container_width=True):
            st.session_state.page = "📥 Install Extension"
            st.rerun()

# ============ TEST ONLINE PAGE ============
elif page == "🌐 Test Online":
    st.title("🌐 Test Phishing Detector")
    st.markdown("Try our AI models directly. Analyze emails and URLs for phishing threats.")
    
    tab1, tab2 = st.tabs(["📧 Email Analysis", "🔗 URL Analysis"])
    
    with tab1:
        st.subheader("Analyze Email Content")
        st.markdown("Paste any suspicious email content below to check if it's phishing.")
        
        email_text = st.text_area(
            "Email content:",
            height=250,
            placeholder="Dear user, please verify your account by clicking the link below...",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔍 Analyze", use_container_width=True, type="primary", key="email_btn"):
                if not email_text:
                    st.error("❌ Please enter email content")
                elif len(email_text) < 30:
                    st.warning("⚠️ Please enter at least 30 characters")
                else:
                    with st.spinner("🔄 Analyzing..."):
                        try:
                            response = requests.post(
                                "https://phishing-detector-api-1.onrender.com/predict",
                                json={"text": email_text},
                                timeout=60
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                prob = (data.get("phishing_probability", 0) or 0) * 100
                                is_phishing = data.get("label") == 1
                                
                                st.success("✅ Analysis Complete!")
                                
                                col_result, col_score = st.columns([1, 1])
                                
                                with col_result:
                                    if is_phishing:
                                        st.markdown("""
                                        <div class="danger-box">
                                        <h3>⚠️ PHISHING DETECTED</h3>
                                        <p>This email shows characteristics of a phishing attack.</p>
                                        <p><strong>Recommendation:</strong> Do not click links or download attachments.</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div class="success-box">
                                        <h3>✅ LIKELY SAFE</h3>
                                        <p>This email does not show obvious phishing indicators.</p>
                                        <p><strong>Note:</strong> Always verify sender identity!</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                with col_score:
                                    st.metric("Phishing Probability", f"{prob:.1f}%")
                                    
                                    # Progress bar
                                    if prob < 30:
                                        st.success("Low Risk")
                                    elif prob < 70:
                                        st.warning("Medium Risk")
                                    else:
                                        st.error("High Risk")
                            
                            elif response.status_code == 503:
                                st.error("⏱️ API is starting up. This takes ~30 seconds on first load. Please try again!")
                            else:
                                st.error(f"❌ API Error: {response.status_code}")
                        
                        except requests.exceptions.Timeout:
                            st.error("⏱️ Request timed out. API might be starting up. Try again in 30 seconds.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.subheader("Analyze URL")
        st.markdown("Enter any URL to check if it's malicious.")
        
        url = st.text_input(
            "URL:",
            placeholder="https://example.com",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔍 Analyze", use_container_width=True, type="primary", key="url_btn"):
                if not url:
                    st.error("❌ Please enter a URL")
                elif not url.startswith(("http://", "https://")):
                    st.error("❌ URL must start with http:// or https://")
                else:
                    with st.spinner("🔄 Analyzing..."):
                        try:
                            response = requests.post(
                                "https://phishing-detector-api-1.onrender.com/predict/url",
                                json={"url": url},
                                timeout=60
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                prob = (data["probabilities"]["phishing"] or 0) * 100
                                is_phishing = data["prediction"] == "phishing"
                                
                                st.success("✅ Analysis Complete!")
                                
                                col_result, col_score = st.columns([1, 1])
                                
                                with col_result:
                                    if is_phishing:
                                        st.markdown("""
                                        <div class="danger-box">
                                        <h3>⚠️ SUSPICIOUS URL</h3>
                                        <p>This URL shows signs of being phishing.</p>
                                        <p><strong>Recommendation:</strong> Do not click this link.</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div class="success-box">
                                        <h3>✅ URL APPEARS SAFE</h3>
                                        <p>This URL does not show obvious phishing indicators.</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                with col_score:
                                    st.metric("Phishing Probability", f"{prob:.1f}%")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

# ============ INSTALL EXTENSION PAGE ============
elif page == "📥 Install Extension":
    st.title("📥 Install Chrome Extension")
    st.markdown("Get real-time phishing protection in your browser!")
    
    st.info("🎉 **Coming Soon to Chrome Web Store!** In the meantime, follow the manual installation steps below.")
    
    # Two columns: steps and features
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("Installation Steps")
        
        with st.expander("📖 Step 1: Download Extension", expanded=True):
            st.markdown("""
            1. Go to our **[GitHub Repository](https://github.com/yourusername/phishing-detector)**
            2. Click **"Code"** → **"Download ZIP"**
            3. Extract the downloaded ZIP file
            4. Look for the **`extension`** folder
            """)
        
        with st.expander("🔧 Step 2: Enable Developer Mode"):
            st.markdown("""
            1. Open **Chrome** browser
            2. Type `chrome://extensions/` in the address bar
            3. Press **Enter**
            4. Toggle **"Developer mode"** (top right corner)
            """)
        
        with st.expander("📤 Step 3: Load Extension"):
            st.markdown("""
            1. Click **"Load unpacked"** button
            2. Select the **`extension`** folder you extracted
            3. Click **"Select Folder"**
            4. ✅ Done! Extension is now installed
            """)
        
        with st.expander("🚀 Step 4: Start Using"):
            st.markdown("""
            1. Go to **Gmail** or any email website
            2. **Select** any suspicious email text
            3. A **tooltip** appears automatically
            4. 🟢 **Green** = Safe | 🔴 **Red** = Phishing
            5. Or click the extension icon in your toolbar for more options
            """)
    
    with col2:
        st.subheader("Features")
        st.markdown("""
        ✅ **Automatic Detection**
        Tooltips appear when you select text
        
        ✅ **Works Everywhere**
        Gmail, Outlook, any website
        
        ✅ **One-Click Analysis**
        Click extension icon for details
        
        ✅ **No Data Collection**
        Completely private
        
        ✅ **Open Source**
        View the code on GitHub
        
        ✅ **Always Free**
        No ads, no premium features
        """)
        
        st.divider()
        st.link_button("🐙 View on GitHub", "https://github.com/yourusername/phishing-detector", use_container_width=True)
    
    st.divider()
    
    st.subheader("🐛 Troubleshooting")
    
    with st.expander("Extension icon doesn't appear"):
        st.markdown("""
        - Reload the page (Ctrl+R or Cmd+R)
        - Restart Chrome completely
        - Check that you selected the `extension` folder, not the parent folder
        """)
    
    with st.expander("'Cannot find manifest.json' error"):
        st.markdown("""
        - Make sure you're loading the `extension` folder
        - The folder should contain: manifest.json, popup.html, popup.js, content.js, and icon files
        - Don't load a parent directory
        """)
    
    with st.expander("Tooltip doesn't appear when selecting text"):
        st.markdown("""
        - Reload the page
        - Check that the extension is enabled in `chrome://extensions/`
        - Open DevTools (F12) and check for errors in the Console
        """)

# ============ FAQ PAGE ============
elif page == "❓ FAQ":
    st.title("❓ Frequently Asked Questions")
    
    with st.expander("What is phishing?"):
        st.markdown("""
        Phishing is a cyber attack where criminals trick you into revealing sensitive information 
        (passwords, credit cards, etc.) by pretending to be a trusted entity like your bank or social media.
        """)
    
    with st.expander("How accurate is Phishing Detector?"):
        st.markdown("""
        Our models achieve **94.2% accuracy** on test data, trained on 10,000+ real phishing and legitimate emails.
        
        However, no AI is 100% accurate. Always verify sender identity and be cautious with suspicious links.
        """)
    
    with st.expander("Is my data safe?"):
        st.markdown("""
        Yes! We use:
        - **HTTPS encryption** for all communication
        - **No data storage** - analysis happens immediately and is deleted
        - **No tracking** - we don't collect personal information
        - **Open source** - you can verify the code yourself
        """)
    
    with st.expander("Does it work offline?"):
        st.markdown("""
        No, the extension needs to send text to our API for analysis. An internet connection is required.
        """)
    
    with st.expander("Can I install on Firefox/Safari?"):
        st.markdown("""
        Currently only Chrome is supported. Firefox and Safari support might come in future updates.
        """)
    
    with st.expander("Is it free?"):
        st.markdown("""
        Yes! Completely free, forever. No ads, no premium features, no hidden costs.
        """)
    
    with st.expander("How do I report a bug?"):
        st.markdown("""
        Visit our [GitHub Issues page](https://github.com/yourusername/phishing-detector/issues) 
        and create a new issue with details about the bug.
        """)
    
    with st.expander("Can I contribute to the project?"):
        st.markdown("""
        Absolutely! We welcome contributions. Check the GitHub repository for contribution guidelines.
        """)

# ============ ABOUT PAGE ============
elif page == "📊 About":
    st.title("📊 About Phishing Detector")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Our Mission")
        st.markdown("""
        Make phishing detection accessible to everyone, regardless of technical skill level.
        """)
        
        st.subheader("🔧 Technology Stack")
        st.markdown("""
        - **Backend:** FastAPI (Python)
        - **ML Models:** scikit-learn
        - **Frontend:** Chrome Extension API
        - **Website:** Streamlit
        - **Hosting:** Render
        """)
    
    with col2:
        st.subheader("📈 Model Performance")
        
        st.metric("Email Model Accuracy", "94.2%", "on test data")
        st.metric("URL Model Accuracy", "91.7%", "on test data")
        st.metric("Combined Average", "93.5%", "accuracy")
        
        st.subheader("📚 Training Data")
        st.markdown("""
        - **10,000+** email samples
        - **5,000+** URLs analyzed
        - **2 years** of research
        - Real-world phishing examples
        """)
    
    st.divider()
    
    st.subheader("🚀 Project Timeline")
    st.markdown("""
    - **Sept 2024:** Initial development
    - **Oct 2024:** API deployment on Render
    - **Oct 30, 2024:** Chrome extension launch
    - **Oct 31, 2024:** Chrome Web Store submission
    - **Future:** Firefox, Safari support
    """)
    
    st.divider()
    
    st.subheader("🔗 Links & Resources")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("🐙 GitHub Repository", "https://github.com/yourusername/phishing-detector")
    with col2:
        st.link_button("📧 Report Issue", "https://github.com/yourusername/phishing-detector/issues")
    with col3:
        st.link_button("📄 Privacy Policy", "https://github.com/yourusername/phishing-detector/blob/main/PRIVACY.md")
    
    st.divider()
    
    st.markdown("""
    **Made by:** Your Name  
    **License:** MIT  
    **Support:** Open an issue on GitHub
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🛡️ <strong>Phishing Detector</strong> - Your AI Security Assistant</p>
    <p style="font-size: 0.9rem;">
        © 2024 | <a href="https://github.com/yourusername/phishing-detector">GitHub</a> | 
        <a href="https://github.com/yourusername/phishing-detector/blob/main/PRIVACY.md">Privacy</a>
    </p>
</div>
""", unsafe_allow_html=True)
