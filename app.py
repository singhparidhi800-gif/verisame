import streamlit as st
import streamlit.components.v1 as components
import time
import pandas as pd
from io import BytesIO

# SEO + Page Config - SIRF 1 BAAR
st.set_page_config(page_title="VeriSame Pro", page_icon="💼", layout="wide")

st.title("VeriSame")
st.write("Verisame is a free online tool to clean, convert and filter Excel & CSV files instantly. No login needed.")

# Google Tag Manager
components.html("""
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id=GTM-5CJ665XZ';f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-5CJ665XZ');</script>
<!-- End Google Tag Manager -->
""", height=0)

# ===== SECRET ADMIN SETTINGS =====
ADMIN_USER = "Reyansh"
ADMIN_SECRET = "Reyansh123"

# ===== VISITOR TRACKING =====
if 'visitor_count' not in st.session_state:
    st.session_state.visitor_count = 0
if 'pro_clicks' not in st.session_state:
    st.session_state.pro_clicks = 0
if 'free_users' not in st.session_state:
    st.session_state.free_users = 0

if 'counted' not in st.session_state:
    st.session_state.visitor_count += 1
    st.session_state.counted = True

# ===== ADMIN DASHBOARD - YE PEHLE CHECK HOGA =====
params = st.query_params
if params.get("admin") == ADMIN_USER and params.get("key") == ADMIN_SECRET:
    st.title("🔐 Admin Dashboard - VeriSame Pro")
    st.divider()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Visitors", st.session_state.visitor_count)
    col2.metric("PRO Button Clicks", st.session_state.pro_clicks)
    col3.metric("FREE Users", st.session_state.free_users)

    st.write("**App Link:** `https://verisame.streamlit.app`")
    st.write("**Your Data Cleaning App:** Safe hai, alag chal raha hai ✅")
    st.stop()

# ===== MAIN APP UI =====
# Baaki ka Verisame wala code yaha likh
