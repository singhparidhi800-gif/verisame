import streamlit as st
import pandas as pd
import time
import hashlib
from io import BytesIO

st.set_page_config(
    page_title="VeriSame Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

GA_MEASUREMENT_ID = "G-7E6HS2Q6Q3"

st.markdown(f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_MEASUREMENT_ID}');
</script>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
  .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

try:
    PRO_USERS_RAW = st.secrets.get("PRO_USERS", "")
    RAZORPAY_LINK = st.secrets.get("RAZORPAY_LINK", "https://wa.me/919794906852")
    WHATSAPP_NO = st.secrets.get("WHATSAPP_NO", "919794906852")
except Exception:
    st.error("Security Error: Secrets not configured.")
    st.stop()

PRO_USERS = [u.strip().lower() for u in PRO_USERS_RAW.split(",") if u.strip()]
email = st.query_params.get("email", "").strip().lower()
is_paid_pro = email in PRO_USERS and email!= ""

if 'page' not in st.session_state:
    st.session_state.page = 'landing'

# --- 6. LANGUAGE: ENGLISH DEFAULT ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

def t(en_text, hi_text):
    return en_text if st.session_state.lang == 'en' else hi_text

def run_app(is_pro, is_paid):
    st.markdown("---")
    uploaded_file = st.file_uploader(
        t("Upload your file", "अपनी फाइल अपलोड करो"),
        type=["csv", "xlsx", "xls"],
        key=f"uploader_{is_pro}_{is_paid}"
    )

    if uploaded_file:
        if uploaded_file.size > 200 * 1024:
            st.error(t("File > 200MB", "File > 200MB"))
            st.stop()

        wait_time = 3 if is_pro else 30
        with st.spinner(t(f"Processing... {wait_time}s", f"Processing... {wait_time}s")):
            time.sleep(wait_time)

        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        except Exception:
            st.error(t("File Error", "File Error"))
            st.stop()

        if not is_pro and len(df) > 1000:
            st.error(t("FREE limit: 1000 rows", "FREE limit: 1000 rows"))
            st.stop()

        df_cleaned = df.drop_duplicates()
        for col in df_cleaned.select_dtypes(include=['object']):
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip()

        st.success(t(f"Cleaned! Removed {len(df) - len(df_cleaned)} duplicates. Total Rows: {len(df_cleaned)}",
                     f"Cleaned! {len(df) - len(df_cleaned)} duplicates हटे। Total Rows: {len(df_cleaned)}"))

        st.write(t("**Preview - First 5 Rows:**", "**Preview - First 5 Rows:**"))
        st.dataframe(df_cleaned.head())

        if is_pro and not is_paid:
            st.error(t("🔒 Download Locked! Buy PRO ₹2999", "🔒 Download Locked! PRO खरीदें ₹2999"))
            st.link_button(t("🚀 Buy PRO Now", "🚀 अभी PRO खरीदें"), RAZORPAY_LINK)
        else:
            if not is_pro and len(df_cleaned) > 100:
                df_download = df_cleaned.head(100)
                st.warning(t("Only 100 rows in FREE", "FREE में सिर्फ 100 rows"))
            else:
                df_download = df_cleaned

            buffer = BytesIO()
            df_download.to_csv(buffer, index=False, encoding='utf-8')
            st.download_button(
                t("📥 Download Cleaned File", "📥 Download Cleaned File"),
                buffer.getvalue(),
                "verisame_cleaned.csv",
                "text/csv"
            )

with st.sidebar:
    st.title("💼 VeriSame Pro")
    lang_choice = st.radio("Language / भाषा", ['English', 'हिंदी'],
                           index=0 if st.session_state.lang == 'en' else 1)
    st.session_state.lang = 'en' if lang_choice == 'English' else 'hi'

    if st.session_state.page!= 'landing':
        if st.button(t("🏠 Back to Home", "🏠 Home पे वापस जाएं")):
            st.session_state.page = 'landing'
            st.rerun()

if st.session_state.page == 'landing':
    st.title(t("💼 Welcome to VeriSame Pro", "💼 VeriSame Pro में आपका स्वागत है"))
    st.markdown(t(
        "### The Fastest Way to Clean Your Data",
        "### डेटा क्लीनिंग का सबसे तेज़ तरीका"
    ))
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(t("🆓 FREE Plan", "🆓 FREE Plan"))
        st.write(t("✅ Up to 1000 Rows", "✅ 1000 Rows तक"))
        st.write(t("✅ 100 Rows Download", "✅ 100 Rows Download"))
        st.write(t("⏱️ 30 Second Wait", "⏱️ 30 सेकंड Wait"))
        if st.button(t("Use FREE", "FREE Use करें"), key="free_btn"):
            st.session_state.page = 'free'
            st.rerun()

    with col2:
        st.subheader(t("💎 PRO Plan - ₹2999", "💎 PRO Plan - ₹2999"))
        st.write(t("✅ Unlimited Rows", "✅ असीमित Rows"))
        st.write(t("✅ Unlimited Download", "✅ असीमित Download"))
        st.write(t("⚡ 3 Second Speed", "⚡ 3 सेकंड Speed"))
        st.write(t("🔒 Preview Free, Download Paid", "🔒 Preview Free, Download Paid"))

        if st.button(t("🚀 See PRO Features", "🚀 PRO Features देखें"), key="pro_btn"):
            st.session_state.page = 'pro_demo' if not is_paid_pro else 'pro'
            st.rerun()

elif st.session_state.page == 'free':
    st.title(t("🆓 FREE Plan - VeriSame", "🆓 FREE Plan - VeriSame"))
    st.info(t("Hello User! 👋 Welcome to FREE Plan",
              "Hello User! 👋 FREE प्लान में आपका स्वागत है"))
    run_app(is_pro=False, is_paid=False)

elif st.session_state.page == 'pro_demo':
    st.title(t("💎 PRO Demo - VeriSame", "💎 PRO Demo - VeriSame"))
    st.success(t("Hello Admin! 👋 PRO Demo. Upgrade to Download.",
                 "Hello Admin! 👋 PRO का Demo देखें। Download के लिए Upgrade करें।"))
    run_app(is_pro=True, is_paid=False)

elif st.session_state.page == 'pro':
    st.title(t("💎 PRO Plan - VeriSame", "💎 PRO Plan - VeriSame"))
    st.success(t(f"Hello Admin! 👋 Paid Pro Active: {email}",
                 f"Hello Admin! 👋 Paid Pro Active: {email}"))
    st.balloons()
    run_app(is_pro=True, is_paid=True)

st.markdown("---")
st.caption(t(
    "🔒 Security: Your data is deleted immediately after processing.",
    "🔒 Security: आपका डेटा प्रोसेस के बाद तुरंत डिलीट हो जाता है।"
))
