import streamlit as st
import streamlit.components.v1 as components
import time
import pandas as pd
from io import BytesIO

# SEO ke liye - Sabse pehle yahi aana chahiye
st.set_page_config(
    page_title="Verisame - Free Excel & CSV Data Cleaner",
    page_icon="🧹",
    layout="wide"
)

st.title("Verisame")
st.write("Verisame is a free online tool to clean, convert and filter Excel & CSV files instantly. No login needed.")

# Google Tag Manager - For Search Console Verification
components.html("""
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id=GTM-5CJ665XZ';f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-5CJ665XZ');</script>
<!-- End Google Tag Manager -->
""", height=0)

st.markdown("""
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5CJ665XZ"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
""", unsafe_allow_html=True)

# ===== SECRET ADMIN SETTINGS =====
ADMIN_USER = "Reyansh"
from io import BytesIO
import time

# ===== SECRET ADMIN SETTINGS =====
ADMIN_USER = "Reyansh"
ADMIN_SECRET = "Reyansh123"  # ← Ye tera secret password hai. Change kar sakta hai

# ===== VISITOR TRACKING =====
if 'visitor_count' not in st.session_state:
    st.session_state.visitor_count = 0
if 'pro_clicks' not in st.session_state:
    st.session_state.pro_clicks = 0
if 'free_users' not in st.session_state:
    st.session_state.free_users = 0

# Count every new visitor
if 'counted' not in st.session_state:
    st.session_state.visitor_count += 1
    st.session_state.counted = True

# ===== ADMIN DASHBOARD =====
params = st.query_params
if params.get("admin") == ADMIN_USER and params.get("key") == ADMIN_SECRET:
    st.title("🔐 Admin Dashboard - VeriSame Pro")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Visitors", st.session_state.visitor_count)
    col2.metric("PRO Button Clicks", st.session_state.pro_clicks)
    col3.metric("FREE Users", st.session_state.free_users)
    
    st.write("**App Link:** `https://verisame-pro-reyansh.streamlit.app`")
    st.write("**Your Data Cleaning App:** Safe hai, alag chal raha hai ✅")
    st.stop()

# ===== MAIN APP UI =====
st.set_page_config(page_title="VeriSame Pro", page_icon="💼", layout="wide")

lang = st.selectbox("Language", ["English", "हिंदी"], label_visibility="collapsed")

if lang == "English":
    st.title("💼 Welcome to VeriSame Pro")
    st.subheader("The Fastest Way to Clean Your Data")
else:
    st.title("💼 VeriSame Pro में आपका स्वागत है")
    st.subheader("आपका डेटा साफ करने का सबसे तेज़ तरीका")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🆓 FREE Plan" if lang == "English" else "🆓 फ्री प्लान")
    st.write("✅ Up to 1000 Rows" if lang == "English" else "✅ 1000 Rows तक")
    st.write("✅ Text to Number Converter" if lang == "English" else "✅ टेक्स्ट से नंबर कन्वर्टर")
    st.write("✅ 1000 Rows Download" if lang == "English" else "✅ 1000 Rows डाउनलोड")
    st.write("⏳ 30 Second Wait" if lang == "English" else "⏳ 30 सेकंड इंतजार")
    
    if st.button("Use FREE", use_container_width=True):
        st.session_state.free_users += 1
        st.info("FREE mode activated. Upload CSV file to start." if lang == "English" else "FREE मोड चालू। शुरू करने के लिए CSV फाइल अपलोड करें।")

with col2:
    st.subheader("💎 PRO Plan - ₹2999 Lifetime" if lang == "English" else "💎 प्रो प्लान - ₹2999 लाइफटाइम")
    st.write("✅ Unlimited Rows" if lang == "English" else "✅ अनलिमिटेड Rows")
    st.write("✅ Date Fixer + Smart Fill" if lang == "English" else "✅ डेट फिक्सर + स्मार्ट फिल")
    st.write("✅ Excel Export" if lang == "English" else "✅ एक्सेल एक्सपोर्ट")
    st.write("⚡ 3 Second Speed" if lang == "English" else "⚡ 3 सेकंड स्पीड")
    
    if st.button("🚀 Use PRO", type="primary", use_container_width=True):
        st.session_state.pro_clicks += 1
        st.success("PRO mode activated!" if lang == "English" else "PRO मोड चालू!")

st.divider()
st.caption("🔒 Security: Your data is deleted immediately after processing." if lang == "English" else "🔒 सुरक्षा: आपका डेटा प्रोसेसिंग के तुरंत बाद हटा दिया जाता है।")
