import streamlit as st
import pandas as pd
import time
import numpy as np
import re
from io import BytesIO, StringIO

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
    section[data-testid="stSidebar"].stRadio > div {padding: 10px 5px 10px 5px;}
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
    }
    @media (max-width: 768px) {
   .stButton>button {height: 55px; font-size: 16px;}
    }
    </style>
""", unsafe_allow_html=True)

try:
    RAZORPAY_LINK = st.secrets.get("RAZORPAY_LINK", "https://wa.me/919794906852")
    RAZORPAY_LINK_USD = st.secrets.get("RAZORPAY_LINK_USD", "https://wa.me/919794906852")
    WHATSAPP_NO = st.secrets.get("WHATSAPP_NO", "919794906852")
except Exception:
    RAZORPAY_LINK = "https://wa.me/919794906852"
    RAZORPAY_LINK_USD = "https://wa.me/919794906852"
    WHATSAPP_NO = "919794906852"

if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if 'plan' not in st.session_state:
    st.session_state.plan = None

def t(en_text, hi_text):
    return en_text if st.session_state.lang == 'en' else hi_text

# ============ FEATURE: TEXT TO NUMBER CONVERTER ============
def text_to_number(text):
    """Convert SIXTY THOUSAND to 60000, FIVE HUNDRED to 500 etc - FREE + PRO both"""
    if pd.isna(text):
        return text
    
    text = str(text).strip().upper()
    
    # If already number, return as is
    if re.match(r'^[\d,.\s]+$', text):
        return text.replace(',', '').strip()
    
    number_words = {
        'ZERO': 0, 'ONE': 1, 'TWO': 2, 'THREE': 3, 'FOUR': 4, 'FIVE': 5,
        'SIX': 6, 'SEVEN': 7, 'EIGHT': 8, 'NINE': 9, 'TEN': 10,
        'ELEVEN': 11, 'TWELVE': 12, 'THIRTEEN': 13, 'FOURTEEN': 14, 'FIFTEEN': 15,
        'SIXTEEN': 16, 'SEVENTEEN': 17, 'EIGHTEEN': 18, 'NINETEEN': 19, 'TWENTY': 20,
        'THIRTY': 30, 'FORTY': 40, 'FIFTY': 50, 'SIXTY': 60, 'SEVENTY': 70,
        'EIGHTY': 80, 'NINETY': 90, 'HUNDRED': 100, 'THOUSAND': 1000, 'LAKH': 100000, 'MILLION': 1000000
    }
    
    words = text.split()
    total = 0
    current = 0
    
    for word in words:
        if word in number_words:
            val = number_words[word]
            if val >= 100:
                current = current * val if current else val
            else:
                current += val
        elif word == 'AND':
            continue
        else:
            # If word not in dictionary, return original
            return text
    
    total = current if current else total
    return str(total) if total > 0 else text

# ==================== LANGUAGE SELECTOR TOP RIGHT ME ====================
col1, col2, col3 = st.columns([6,2,2])
with col3:
    lang_choice = st.selectbox(
        "🌐",
        ['English', 'हिंदी'],
        index=0 if st.session_state.lang == 'en' else 1,
        label_visibility="collapsed",
        key="lang_selector"
    )
    st.session_state.lang = 'en' if lang_choice == 'English' else 'hi'

with st.sidebar:
    st.title("💼 VeriSame Pro")
    if st.session_state.plan:
        if st.button(t("← Back to Plans", "← Plans पे वापस")):
            st.session_state.plan = None
            if 'sample_df' in st.session_state:
                del st.session_state['sample_df']
            st.rerun()

# LANDING PAGE
if st.session_state.plan is None:
    st.title(t("💼 Welcome to VeriSame Pro", "💼 VeriSame Pro में आपका स्वागत है"))
    st.subheader(t("The Fastest Way to Clean Your Data", "आपका डेटा साफ करने का सबसे तेज तरीका"))
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("🆓 FREE Plan", "🆓 FREE Plan"))
        st.markdown(t("✅ Up to 1000 Rows", "✅ 1000 Rows तक"))
        st.markdown(t("✅ Text to Number Converter", "✅ Text to Number Converter"))
        st.markdown(t("✅ 100 Rows Download", "✅ 100 Rows Download"))
        st.markdown(t("⏱️ 30 Second Wait", "⏱️ 30 Second Wait"))
        if st.button("Use FREE", use_container_width=True):
            st.session_state.plan = 'free'
            st.rerun()

    with col2:
        st.subheader(t("💎 PRO Plan - ₹2999 / $36", "💎 PRO Plan - ₹2999 / $36"))
        st.markdown(t("✅ Unlimited Rows", "✅ Unlimited Rows"))
        st.markdown(t("✅ Date Fixer + Smart Fill", "✅ Date Fixer + Smart Fill"))
        st.markdown(t("✅ Excel Export", "✅ Excel Export"))
        st.markdown(t("⚡ 3 Second Speed", "⚡ 3 Second Speed"))
        if st.button("🚀 Use PRO", use_container_width=True, type="primary"):
            st.session_state.plan = 'pro'
            st.rerun()

    st.markdown("---")
    st.caption(t("🔒 Security: Your data is deleted immediately after processing.",
                 "🔒 Security: आपका डेटा प्रोसेस के बाद तुरंत डिलीट हो जाता है।"))

# FREE YA PRO PLAN KA UPLOAD PAGE
else:
    is_pro = st.session_state.plan == 'pro'

    if is_pro:
        st.title(t("💎 VeriSame PRO", "💎 VeriSame PRO"))
        st.info(t("PRO Mode: Advanced cleaning tools unlocked", "PRO Mode: Advanced cleaning tools unlocked"))
    else:
        st.title(t("🆓 VeriSame FREE", "🆓 VeriSame FREE"))
        st.info(t("FREE Mode: Up to 1000 rows, 100 download free. + Text to Number converter included",
                  "FREE Mode: 1000 rows तक, 100 download फ्री। + Text to Number converter included"))

    with st.expander(t("🧪 Don't have a file? Test with sample data", "🧪 फाइल नहीं है? सैंपल डेटा से टेस्ट करें")):
        st.write(t("This is dummy data for testing only.", "यह सिर्फ टेस्टिंग के लिए डमी डेटा है।"))
        if st.button(t("Load Sample Data", "सैंपल डेटा लोड करें"), use_container_width=True):
            sample_data = """Ref_ID,Category,JoinDate,Value,Gender
A101,Category_X,15-01-2024,100,Male
A101,Category_X,01/15/2024,100,Male
B202,Category_Y,2024-03-20,,Female
C303,Category_Z,20/03/24,300,Male
C303,Category_Z,Mar 20 2024,300,Male"""
            st.session_state['sample_df'] = pd.read_csv(StringIO(sample_data))
            st.success(t("✅ Sample data loaded", "✅ सैंपल डेटा लोड हो गया"))
            st.rerun()

    uploaded_file = st.file_uploader(
        t("Upload your CSV/Excel/JSON file", "अपनी CSV/Excel/JSON फाइल अपलोड करो"),
        type=["csv", "xlsx", "xls", "json"]
    )

    df = None
    original_row_count = 0
    file_source = None
    if uploaded_file:
        file_source = uploaded_file
    elif 'sample_df' in st.session_state:
        file_source = 'sample'
        st.info(t("Using: Sample Test Data", "उपयोग: सैंपल टेस्ट डेटा"))

    if file_source:
        if file_source!= 'sample' and uploaded_file.size > 200 * 1024 * 1024:
            st.error(t("File > 200MB not allowed", "File > 200MB allowed नहीं"))
            st.stop()

        wait_time = 3 if is_pro else 30
        with st.spinner(t(f"Cleaning data... {wait_time}s", f"डेटा साफ हो रहा है... {wait_time}s")):
            time.sleep(wait_time)

        try:
            if file_source == 'sample':
                df = st.session_state['sample_df']
                original_row_count = len(df)
            else:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    df = pd.read_json(uploaded_file)
                original_row_count = len(df) # Store original count
        except Exception as e:
            st.error(t(f"Error reading file: {e}", f"File पढ़ने में Error: {e}"))
            st.stop()

        # ============ FREE LIMIT + ROW COUNT DISPLAY ============
        if not is_pro and len(df) > 1000:
            st.warning(t(f"FREE limit: Processing first 1000 rows out of {original_row_count} rows. Upgrade to PRO for full file.",
                         f"FREE limit: {original_row_count} में से सिर्फ पहली 1000 rows process होंगी। पूरी फाइल के लिए PRO लें।"))
            df = df.head(1000)
        else:
            st.info(t(f"Original file had {original_row_count} rows", f"Original file me {original_row_count} rows thi"))

        # ============ BASIC CLEANING ============
        df_cleaned = df.drop_duplicates()
        
        # ============ FEATURE: TEXT TO NUMBER FOR FREE + PRO BOTH ============
        for col in df_cleaned.select_dtypes(include=['object']):
            df_cleaned[col] = df_cleaned[col].apply(text_to_number)

        # ============ PRO FEATURES START ============
        if is_pro:
            st.markdown("---")
            st.subheader(t("🔧 PRO Cleaning Tools", "🔧 PRO Cleaning Tools"))

            # FEATURE 1: DATE STANDARDIZER
            date_cols = st.multiselect(
                t("1. Select Date Columns to Standardize", "1. Date वाले Columns चुनो"),
                df_cleaned.columns.tolist()
            )
            if date_cols:
                for col in date_cols:
                    df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                st.success(t(f"✅ Dates standardized in {len(date_cols)} columns", f"✅ {len(date_cols)} columns में Dates fix हुई"))

            # FEATURE 2: SMART FILL MISSING VALUES
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols and df_cleaned[numeric_cols].isnull().any().any():
                fill_method = st.selectbox(
                    t("2. Fill Missing Numeric Values Using:", "2. खाली Numbers कैसे भरें:"),
                    ["None", "Mean", "Median", "Zero", "Custom Value"]
                )
                if fill_method!= "None":
                    if fill_method == "Mean":
                        df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
                    elif fill_method == "Median":
                        df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].median())
                    elif fill_method == "Zero":
                        df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(0)
                    elif fill_method == "Custom Value":
                        custom_val = st.number_input("Enter custom value:", value=0)
                        df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(custom_val)
                    st.success(t("✅ Missing values filled", "✅ खाली जगह भर दी गई"))

        # ============ PRO FEATURES END ============

        st.markdown("---")
        st.success(t(f"Done! Removed {len(df) - len(df_cleaned)} duplicates. Total: {len(df_cleaned)} rows",
                     f"हो गया! {len(df) - len(df_cleaned)} duplicate हटे। Total: {len(df_cleaned)} rows"))

        # ============ FINAL NaN CLEANING - 200% GUARANTEE ============
        df_display = df_cleaned.fillna('').astype(str)
        df_display = df_display.replace(['nan', 'NAN', 'NaN', 'None', 'null', 'NULL'], '', regex=False)

        if is_pro:
            st.write(t("**Preview - First 10 Rows Only:**", "**प्रीव्यू - सिर्फ पहली 10 Rows:**"))
            st.dataframe(df_display.head(10))
            st.caption("🔒 VeriSame PRO | Unlock full file to remove watermark")
        else:
            st.write(t("**Preview - First 5 Rows:**", "**Preview - First 5 Rows:**"))
            st.dataframe(df_display.head())

        st.markdown("---")

        if is_pro:
            st.error(t("🔒 Full Download Locked: Pay to unlock", "🔒 फुल डाउनलोड लॉक्ड: अनलॉक करने के लिए पे करें"))

            tab1, tab2 = st.tabs(["🇮🇳 Pay in INR", "🌍 Pay in USD"])

            with tab1:
                st.markdown("**₹2,999 for Indian Users**")
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("💳 Pay ₹2999 Now", RAZORPAY_LINK, use_container_width=True)
                with col2:
                    wa_msg = f"Hi, I paid ₹2999 for VeriSame Pro. My file has {len(df_cleaned)} rows."
                    st.link_button("📱 Send Screenshot", f"https://wa.me/{WHATSAPP_NO}?text={wa_msg}", use_container_width=True)

            with tab2:
                st.markdown("**$36 for International Users**")
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("💳 Pay $36 Now", RAZORPAY_LINK_USD, use_container_width=True)
                with col2:
                    wa_msg_usd = f"Hi, I paid $36 for VeriSame Pro. My file has {len(df_cleaned)} rows."
                    st.link_button("📱 Send Screenshot", f"https://wa.me/{WHATSAPP_NO}?text={wa_msg_usd}", use_container_width=True)

            # FEATURE 4: EXCEL EXPORT - PRO ONLY
            st.markdown("---")
            st.subheader(t("📥 Download Cleaned File", "📥 साफ फाइल डाउनलोड करो"))

            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_cleaned.to_excel(writer, index=False, sheet_name='CleanedData')

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    t("📊 Download as Excel", "📊 Excel में डाउनलोड"),
                    excel_buffer.getvalue(),
                    "verisame_cleaned.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            with col2:
                csv_buffer = BytesIO()
                df_cleaned.to_csv(csv_buffer, index=False, encoding='utf-8')
                st.download_button(
                    t("📄 Download as CSV", "📄 CSV में डाउनलोड"),
                    csv_buffer.getvalue(),
                    "verisame_cleaned.csv",
                    "text/csv"
                )

        else:
            df_download = df_cleaned.head(100) if len(df_cleaned) > 100 else df_cleaned
            buffer = BytesIO()
            df_download.to_csv(buffer, index=False, encoding='utf-8')
            st.download_button(
                t(f"📥 Download {len(df_download)} Rows", f"📥 {len(df_download)} Rows Download करें"),
                buffer.getvalue(),
                "verisame_cleaned.csv",
                "text/csv"
            )
            if len(df_cleaned) >= 100:
                st.warning(t("Need full file? Go back and use PRO Plan ₹2999/$36",
                             "पूरी फाइल चाहिए? वापस जाके PRO Plan ₹2999/$36 use करें"))                                    
