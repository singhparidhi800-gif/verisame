import streamlit as st
import pandas as pd
import time
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
    RAZORPAY_LINK = st.secrets.get("RAZORPAY_LINK", "https://wa.me/919794906852")
    WHATSAPP_NO = st.secrets.get("WHATSAPP_NO", "919794906852")
except Exception:
    RAZORPAY_LINK = "https://wa.me/919794906852"
    WHATSAPP_NO = "919794906852"

if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if 'plan' not in st.session_state:
    st.session_state.plan = None

def t(en_text, hi_text):
    return en_text if st.session_state.lang == 'en' else hi_text

with st.sidebar:
    st.title("💼 VeriSame Pro")
    lang_choice = st.radio("Language / भाषा", ['English', 'हिंदी'],
                           index=0 if st.session_state.lang == 'en' else 1)
    st.session_state.lang = 'en' if lang_choice == 'English' else 'hi'
    
    if st.session_state.plan:
        if st.button(t("← Back to Plans", "← Plans पे वापस")):
            st.session_state.plan = None
            st.rerun()

# LANDING PAGE - WAISE KA WAISA JAISE SCREENSHOT ME HAI
if st.session_state.plan is None:
    st.title(t("💼 Welcome to VeriSame Pro", "💼 VeriSame Pro में आपका स्वागत है"))
    st.subheader(t("The Fastest Way to Clean Your Data", "आपका डेटा साफ करने का सबसे तेज तरीका"))
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("🆓 FREE Plan", "🆓 FREE Plan"))
        st.markdown(t("✅ Up to 1000 Rows", "✅ 1000 Rows तक"))
        st.markdown(t("✅ 100 Rows Download", "✅ 100 Rows Download"))
        st.markdown(t("⏱️ 30 Second Wait", "⏱️ 30 Second Wait"))
        if st.button("Use FREE", use_container_width=True):
            st.session_state.plan = 'free'
            st.rerun()
            
    with col2:
        st.subheader(t("💎 PRO Plan - ₹2999", "💎 PRO Plan - ₹2999"))
        st.markdown(t("✅ Unlimited Rows", "✅ Unlimited Rows"))
        st.markdown(t("✅ Unlimited Download", "✅ Unlimited Download"))
        st.markdown(t("⚡ 3 Second Speed", "⚡ 3 Second Speed"))
        st.markdown(t("🔒 Preview Free, Download Paid", "🔒 Preview Free, Download Paid"))
        if st.button("🚀 Use PRO", use_container_width=True):
            st.session_state.plan = 'pro'
            st.rerun()
    
    st.markdown("---")
    st.caption(t("🔒 Security: Your data is deleted immediately after processing.",
                 "🔒 Security: आपका डेटा प्रोसेस के बाद तुरंत डिलीट हो जाता है।"))

# FREE YA PRO PLAN KA UPLOAD PAGE - DONO SAME
else:
    is_pro = st.session_state.plan == 'pro'
    
    if is_pro:
        st.title(t("💎 VeriSame PRO", "💎 VeriSame PRO"))
        st.info(t("PRO Mode: Upload unlimited rows. Pay ₹2999 to download full file.", 
                  "PRO Mode: Unlimited rows अपलोड करें। पूरी फाइल डाउनलोड के लिए ₹2999 दें।"))
    else:
        st.title(t("🆓 VeriSame FREE", "🆓 VeriSame FREE"))
        st.info(t("FREE Mode: Up to 1000 rows, 100 download free.", 
                  "FREE Mode: 1000 rows तक, 100 download फ्री।"))

    uploaded_file = st.file_uploader(
        t("Upload your CSV/Excel file", "अपनी CSV/Excel फाइल अपलोड करो"),
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file:
        if uploaded_file.size > 200 * 1024:
            st.error(t("File > 200MB not allowed", "File > 200MB allowed नहीं"))
            st.stop()

        wait_time = 3 if is_pro else 30
        with st.spinner(t(f"Cleaning data... {wait_time}s", f"डेटा साफ हो रहा है... {wait_time}s")):
            time.sleep(wait_time)

        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        except Exception:
            st.error(t("Error reading file", "File पढ़ने में Error"))
            st.stop()

        if not is_pro and len(df) > 1000:
            st.error(t("FREE limit: 1000 rows only. Use PRO for bigger files.", 
                       "FREE limit: सिर्फ 1000 rows. बड़ी फाइल के लिए PRO use करें।"))
            st.stop()

        df_cleaned = df.drop_duplicates()
        for col in df_cleaned.select_dtypes(include=['object']):
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip()

        st.success(t(f"Done! Removed {len(df) - len(df_cleaned)} duplicates. Total: {len(df_cleaned)} rows",
                     f"हो गया! {len(df) - len(df_cleaned)} duplicate हटे। Total: {len(df_cleaned)} rows"))

        st.write(t("**Preview - First 5 Rows:**", "**Preview - First 5 Rows:**"))
        st.dataframe(df_cleaned.head())

        st.markdown("---")
        
        if is_pro:
            # PRO PLAN - DOWNLOAD LOCKED HAI
            st.error(t("🔒 Download Locked: Pay ₹2999 to unlock full file", 
                       "🔒 Download Locked: पूरी फाइल के लिए ₹2999 दें"))
            st.markdown(t("**Steps:** 1. Click Pay Now → 2. Send screenshot on WhatsApp → 3. Get file",
                          "**Steps:** 1. Pay Now दबाएं → 2. Screenshot WhatsApp करें → 3. फाइल पाएं"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.link_button(t("💳 Pay ₹2999 Now", "💳 अभी ₹2999 Pay करें"), RAZORPAY_LINK, use_container_width=True)
            with col2:
                wa_msg = t("Hi, I paid ₹2999 for VeriSame Pro. My file has " + str(len(df_cleaned)) + " rows.",
                           "Hi, मैंने VeriSame Pro के ₹2999 pay कर दिए। मेरी फाइल में " + str(len(df_cleaned)) + " rows हैं।")
                st.link_button(t("📱 Send Screenshot on WhatsApp", "📱 WhatsApp पर Screenshot भेजें"), 
                               f"https://wa.me/{WHATSAPP_NO}?text={wa_msg}", use_container_width=True)
        else:
            # FREE PLAN - 100 ROWS DOWNLOAD
            df_download = df_cleaned.head(100) if len(df_cleaned) > 100 else df_cleaned
            buffer = BytesIO()
            df_download.to_csv(buffer, index=False, encoding='utf-8')
            st.download_button(
                t(f"📥 Download {len(df_download)} Rows", f"📥 {len(df_download)} Rows Download करें"),
                buffer.getvalue(),
                "verisame_cleaned.csv",
                "text/csv"
            )
            if len(df_cleaned) > 100:
                st.warning(t("Need full file? Go back and use PRO Plan ₹2999", 
                             "पूरी फाइल चाहिए? वापस जाके PRO Plan ₹2999 use करें"))
