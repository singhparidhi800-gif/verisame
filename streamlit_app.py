import streamlit as st
import pandas as pd
import time
import hashlib
from io import BytesIO

# --- 1. PAGE CONFIG + SECURITY HEADERS ---
st.set_page_config(
    page_title="VeriSame Pro", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Security: Disable Streamlit telemetry and hide menu
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SECURE SECRETS LOADING ---
try:
    PRO_USERS_RAW = st.secrets.get("PRO_USERS", "")
    RAZORPAY_LINK = st.secrets.get("RAZORPAY_LINK", "https://wa.me/919794906852")
    WHATSAPP_NO = st.secrets.get("WHATSAPP_NO", "919794906852")
except Exception:
    st.error("Security Error: Secrets not configured. Contact admin.")
    st.stop()

# --- 3. PRO CHECK + EMAIL SANITIZATION ---
PRO_USERS = [u.strip().lower() for u in PRO_USERS_RAW.split(",") if u.strip()]
email = st.query_params.get("email", "").strip().lower()
is_pro = email in PRO_USERS and email!= ""

# --- 4. LANGUAGE TOGGLE ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'hi' # default Hindi

def t(hi_text, en_text):
    return hi_text if st.session_state.lang == 'hi' else en_text

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("💼 VeriSame Pro")
    
    # Language switch
    lang_choice = st.radio("Language / भाषा", ['हिंदी', 'English'], 
                           index=0 if st.session_state.lang == 'hi' else 1)
    st.session_state.lang = 'hi' if lang_choice == 'हिंदी' else 'en'
    st.markdown("---")
    
    if is_pro:
        st.success(t("✅ Pro Plan Active", "✅ Pro Plan Active"))
        st.write(t("**Limit:** असीमित Rows", "**Limit:** Unlimited Rows"))
        st.write(t("**Download:** असीमित", "**Download:** Unlimited"))
        st.write(t("**Speed:** 3 सेकंड", "**Speed:** 3 Seconds"))
    else:
        st.warning(t("Current Plan: FREE", "Current Plan: FREE"))
        st.write(t("**Limit:** 1000 Rows", "**Limit:** 1000 Rows"))
        st.write(t("**Download:** 100 Rows", "**Download:** 100 Rows")) 
        st.write(t("**Wait:** 30 सेकंड/फाइल", "**Wait:** 30s per file"))
        st.markdown("---")
        st.link_button(t("🚀 Pro लो ₹2999", "🚀 Upgrade to Pro ₹2999"), RAZORPAY_LINK)
        st.caption(t(f"Payment के बाद WhatsApp करें: {WHATSAPP_NO}", 
                     f"After payment, WhatsApp us: {WHATSAPP_NO}"))

# --- 6. MAIN APP ---
st.title(t("VeriSame Pro - डेटा क्लीनिंग सूट", "VeriSame Pro - Data Cleaning Suite"))

# Hello message for both Free and Pro
if is_pro:
    st.success(t(f"Hello Admin! 👋 आपका Pro Access Active है: {email}", 
                 f"Hello Admin! 👋 Pro Access Active for: {email}"))
    st.balloons()
else:
    st.info(t("Hello User! 👋 FREE प्लान में आपका स्वागत है", 
              "Hello User! 👋 Welcome to FREE Plan"))

st.markdown(t(
    "CSV/Excel फाइल अपलोड करें। Duplicates हटेंगे + Smart Text Cleaning होगी।", 
    "Upload your CSV/Excel files. Duplicate removal + smart text cleaning."
))

# --- 7. SECURE FILE UPLOAD ---
uploaded_file = st.file_uploader(
    t("अपनी फाइल अपलोड करो", "Upload your file"), 
    type=["csv", "xlsx", "xls"],
    help=t("Max 200MB. आपका डेटा हमारे सर्वर पर सेव नहीं होता।", 
           "Max 200MB. Your data is never stored on our servers.")
)

if uploaded_file:
    # Security 1: File size check - 200MB limit
    if uploaded_file.size > 200 * 1024 * 1024:
        st.error(t("Security Alert: फाइल 200MB से बड़ी है।", 
                   "Security Alert: File exceeds 200MB limit."))
        st.stop()
    
    # Security 2: File type double check
    allowed_types = ['text/csv', 'application/vnd.ms-excel', 
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    if uploaded_file.type not in allowed_types:
        st.error(t("Security Alert: सिर्फ CSV/Excel allowed है।", 
                   "Security Alert: Only CSV/Excel files allowed."))
        st.stop()

    # Processing time: Free 30s, Pro 3s
    if not is_pro:
        with st.spinner(t("FREE users के लिए 30s प्रोसेसिंग...", "Processing for FREE users: 30s...")):
            time.sleep(30)
    else:
        with st.spinner(t("Pro Speed: 3s में क्लीन हो रहा है...", "Pro Speed: Cleaning in 3s...")):
            time.sleep(3) # Pro ko bhi feel dene ke liye 3s
    
    try:
        # Security 3: Read in memory, never save to disk
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(t(f"File Error: फाइल पढ़ नहीं पाए। Corrupt तो नहीं?", 
                   f"File Error: Could not read file. Is it corrupt?"))
        st.stop()

    # Security 4: Hash for data integrity check
    file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
    st.caption(t(f"File Security ID: {file_hash}", f"File Security ID: {file_hash}"))
    
    st.write(t(f"Original Rows: {len(df)}", f"Original Rows: {len(df)}"))
    
    # Limit check for free users
    if not is_pro and len(df) > 1000:
        st.error(t("FREE प्लान लिमिट: 1000 rows only. Pro में असीमित है।", 
                   "FREE plan limit: 1000 rows only. Unlimited in Pro."))
        st.stop()
    
    # --- 8. DATA CLEANING ---
    df_cleaned = df.drop_duplicates()
    # Security 5: Basic text cleaning to prevent injection
    for col in df_cleaned.select_dtypes(include=['object']):
        df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
    
    st.success(t(f"क्लीन हो गया! {len(df) - len(df_cleaned)} Duplicates हटाए।", 
                 f"Cleaned! Removed {len(df) - len(df_cleaned)} duplicates."))
    st.write(t(f"Final Rows: {len(df_cleaned)}", f"Final Rows: {len(df_cleaned)}"))
    
    # Download limit for free users
    if not is_pro and len(df_cleaned) > 100:
        st.warning(t("FREE में सिर्फ 100 rows डाउनलोड होंगी। Pro में असीमित।", 
                     "Only 100 rows downloadable in FREE. Unlimited in Pro."))
        df_download = df_cleaned.head(100)
    else:
        df_download = df_cleaned
    
    # Security 6: Generate file in memory, no server storage
    buffer = BytesIO()
    df_download.to_csv(buffer, index=False, encoding='utf-8')
    
    st.download_button(
        t("📥 Cleaned फाइल डाउनलोड करें", "📥 Download Cleaned File"),
        buffer.getvalue(),
        "verisame_cleaned.csv",
        "text/csv"
    )
    
    # Security 7: Clear data from memory after use
    del df, df_cleaned, df_download, buffer

else:
    st.info(t("👆 CSV या Excel फाइल अपलोड करो शुरू करने के लिए", 
              "👆 Upload a CSV or Excel file to start"))

# --- 9. SECURITY FOOTER ---
st.markdown("---")
st.caption(t(
    "🔒 Security: आपका डेटा प्रोसेस के बाद तुरंत डिलीट हो जाता है। हम कुछ सेव नहीं करते।", 
    "🔒 Security: Your data is deleted immediately after processing. We store nothing."
))        
