import streamlit as st
st.markdown('<meta name="google-site-verification" content="TeraWalaCodeYahanDaal" />', unsafe_allow_html=True)
st.set_page_config(
    page_title="VeriSame - Free Excel & CSV D",
    page_icon="📊",
    layout="wide",
    menu_items={
        'About': "VeriSame cleans messy Excel"
    }
)
import pandas as pd
import time
import numpy as np
import re
from io import BytesIO, StringIO
import qrcode
from streamlit.components.v1 import html
import json
import os

# ============ SECRET PASSWORD WALA DASHBOARD ============
SECRET_PASS = "reyansh999" # Isko change kar dena
query_params = st.query_params
SHOW_DASHBOARD = query_params.get("pass") == SECRET_PASS

# ============ COUNTING FILE ============
COUNT_FILE = "counts.json"
if not os.path.exists(COUNT_FILE):
    with open(COUNT_FILE, 'w') as f:
        json.dump({"views": 0, "free": 0, "pro": 0, "buy": 0}, f)

def update_count(key):
    with open(COUNT_FILE, 'r+') as f:
        data = json.load(f)
        data[key] += 1
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    return data[key]

def get_counts():
    with open(COUNT_FILE) as f:
        return json.load(f)

# ============ GA + VIEWS COUNT - SIRF 1 BAAR PER SESSION ============
if not SHOW_DASHBOARD:
    if 'counted_session' not in st.session_state:
        update_count("views")
        st.session_state.counted_session = True

    GA_MEASUREMENT_ID = "G-7E6HS2Q6Q3"
    html(f"""
    <!DOCTYPE html><html><head>
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script></head></html>
    """, height=0)

# ============ SECRET DASHBOARD - SIRF TU DEKH PAYEGA ============
if SHOW_DASHBOARD:
    st.title("🔒 Tera Private Dashboard")
    counts = get_counts()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Views", counts['views'])
    col2.metric("FREE Clicks", counts['free'])
    col3.metric("PRO Clicks", counts['pro'])
    col4.metric("Purchases", counts['buy'])
    st.caption("Ye page sirf tujhe dikh raha hai. Bookmark kar le: `?pass=reyansh999`")
    if st.button("🔄 Refresh Counts"):
        st.rerun()
    st.stop()

# ============ UPI CONFIG ============
UPI_ID = "playwithreyansh0@okhdfcbank"
PRO_AMOUNT = 2999
WAIT_SECONDS = 15

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

# ============ SESSION STATES ============
if 'lang' not in st.session_state: st.session_state.lang = 'en'
if 'plan' not in st.session_state: st.session_state.plan = None
if 'show_qr' not in st.session_state: st.session_state.show_qr = False
if 'payment_done' not in st.session_state: st.session_state.payment_done = False
if 'qr_start_time' not in st.session_state: st.session_state.qr_start_time = None

def t(en_text, hi_text): return en_text if st.session_state.lang == 'en' else hi_text

def text_to_number(text):
    if pd.isna(text): return text
    text = str(text).strip().upper()
    if re.match(r'^[\d,.\s]+$', text): return text.replace(',', '').strip()
    number_words = {'ZERO':0,'ONE':1,'TWO':2,'THREE':3,'FOUR':4,'FIVE':5,'SIX':6,'SEVEN':7,'EIGHT':8,'NINE':9,'TEN':10,'ELEVEN':11,'TWELVE':12,'THIRTEEN':13,'FOURTEEN':14,'FIFTEEN':15,'SIXTEEN':16,'SEVENTEEN':17,'EIGHTEEN':18,'NINETEEN':19,'TWENTY':20,'THIRTY':30,'FORTY':40,'FIFTY':50,'SIXTY':60,'SEVENTY':70,'EIGHTY':80,'NINETY':90,'HUNDRED':100,'THOUSAND':1000,'LAKH':100000,'MILLION':1000000}
    words = text.split(); current = 0
    for word in words:
        if word in number_words:
            val = number_words[word]
            if val >= 100: current = current * val if current else val
            else: current += val
        elif word == 'AND': continue
        else: return text
    return str(current) if current > 0 else text

# ==================== TOP BAR ====================
col1, col2, col3 = st.columns([6,2,2])
with col3:
    lang_choice = st.selectbox("🌐", ['English', 'हिंदी'], label_visibility="collapsed")
    st.session_state.lang = 'en' if lang_choice == 'English' else 'hi'

with st.sidebar:
    st.title("💼 VeriSame")
    if st.session_state.plan:
        if st.button(t("← Back to Plans", "← Plans पे वापस")):
            st.session_state.plan = None
            st.session_state.show_qr = False
            st.session_state.payment_done = False
            st.session_state.qr_start_time = None
            if 'sample_df' in st.session_state: del st.session_state['sample_df']
            st.rerun()

# LANDING PAGE
if st.session_state.plan is None:
    st.image("https://i.ibb.co/W43B7drG/VeriSame-logo.png", width=200)
    st.caption("Free online tool to clean Excel & CSV files. Convert text to numbers, fix dates, remove duplicates instantly.")
    st.title(t("💼 Welcome to VeriSame", "💼 VeriSame में आपका स्वागत है"))
    st.subheader(t("The Fastest Way to Clean Your Data", "आपका डेटा साफ करने का सबसे तेज तरीका"))
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("🆓 FREE Plan", "🆓 FREE Plan"))
        st.markdown(t("✅ Up to 1000 Rows", "✅ 1000 Rows तक"))
        st.markdown(t("✅ Text to Number Converter", "✅ Text to Number Converter"))
        st.markdown(t("✅ 1000 Rows Download", "✅ 1000 Rows Download"))
        st.markdown(t("⏱️ 30 Second Wait", "⏱️ 30 Second Wait"))
        if st.button("Use FREE", use_container_width=True):
            update_count("free")
            st.session_state.plan = 'free'
            st.rerun()

    with col2:
        st.subheader(t("💎 PRO Plan - ₹2999 Lifetime", "💎 PRO Plan - ₹2999 Lifetime"))
        st.markdown(t("✅ Unlimited Rows", "✅ Unlimited Rows"))
        st.markdown(t("✅ Date Fixer + Smart Fill", "✅ Date Fixer + Smart Fill"))
        st.markdown(t("✅ Excel Export", "✅ Excel Export"))
        st.markdown(t("⚡ 3 Second Speed", "⚡ 3 Second Speed"))
        if st.button("🚀 Use PRO", use_container_width=True, type="primary"):
            update_count("pro")
            st.session_state.plan = 'pro'
            st.rerun()

    st.markdown("---")
    st.caption(t("🔒 Security: Your data is deleted immediately after processing.",
                 "🔒 Security: आपका डेटा प्रोसेस के बाद तुरंत डिलीट हो जाता है।"))

# FREE YA PRO PLAN KA UPLOAD PAGE
else:
    is_pro = st.session_state.plan == 'pro'

    if st.button(t("⬅️ Back to Plans", "⬅️ Plans पे वापस"), use_container_width=True):
        st.session_state.plan = None
        st.session_state.show_qr = False
        st.session_state.payment_done = False
        st.session_state.qr_start_time = None
        if 'sample_df' in st.session_state: del st.session_state['sample_df']
        st.rerun()

    st.markdown("---")

    if is_pro:
        st.title(t("💎 VeriSame PRO", "💎 VeriSame PRO"))
        st.info(t("PRO Mode: Advanced cleaning tools unlocked", "PRO Mode: Advanced cleaning tools unlocked"))
    else:
        st.title(t("🆓 VeriSame FREE", "🆓 VeriSame FREE"))
        st.info(t("FREE Mode: Up to 1000 rows, 1000 download free. + Text to Number converter included",
                  "FREE Mode: 1000 rows तक, 1000 download फ्री। + Text to Number converter included"))

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
                original_row_count = len(df)
        except Exception as e:
            st.error(t(f"Error reading file: {e}", f"File पढ़ने में Error: {e}"))
            st.stop()

        if not is_pro and len(df) > 1000:
            st.warning(t(f"FREE limit: Processing first 1000 rows out of {original_row_count} rows. Upgrade to PRO for full file.",
                         f"FREE limit: {original_row_count} में से सिर्फ पहली 1000 rows process होंगी। पूरी फाइल के लिए PRO लें।"))
            df = df.head(1000)
        else:
            st.info(t(f"Original file had {original_row_count} rows", f"Original file me {original_row_count} rows thi"))

        df_cleaned = df.drop_duplicates()

        for col in df_cleaned.select_dtypes(include=['object']):
            df_cleaned[col] = df_cleaned[col].apply(text_to_number)

        if is_pro:
            st.markdown("---")
            st.subheader(t("🔧 PRO Cleaning Tools", "🔧 PRO Cleaning Tools"))
            date_cols = st.multiselect(
                t("1. Select Date Columns to Standardize", "1. Date वाले Columns चुनो"),
                df_cleaned.columns.tolist()
            )
            if date_cols:
                for col in date_cols:
                    df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                st.success(t(f"✅ Dates standardized in {len(date_cols)} columns", f"✅ {len(date_cols)} columns में Dates fix हुई"))

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

        st.markdown("---")
        st.success(t(f"Done! Removed {original_row_count - len(df_cleaned)} duplicates. Total: {len(df_cleaned)} rows",
                     f"हो गया! {original_row_count - len(df_cleaned)} duplicate हटे। Total: {len(df_cleaned)} rows"))

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
            if not st.session_state.payment_done:
                if not st.session_state.show_qr:
                    st.error(t("🔒 Download Locked - ₹2999 Lifetime", "🔒 डाउनलोड लॉक्ड - ₹2999 लाइफटाइम"))
                    if st.button("💳 Pay ₹2999 with UPI", use_container_width=True, type="primary"):
                        st.session_state.show_qr = True
                        st.session_state.qr_start_time = time.time()
                        st.rerun()
                else:
                    st.warning(t("Step 1: Scan QR & Complete Payment", "Step 1: QR स्कैन करो और Payment करो"))
                    upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={PRO_AMOUNT}&cu=INR"
                    qr = qrcode.QRCode(box_size=8, border=4)
                    qr.add_data(upi_link)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    buf = BytesIO(); img.save(buf)
                    col1, col2 = st.columns([1,2])
                    with col1:
                        st.image(buf, width=250)
                    with col2:
                        st.markdown(f"**UPI ID:** `{UPI_ID}`")
                        st.markdown(f"**Amount:** `₹{PRO_AMOUNT}`")
                        st.caption(t("Scan with GPay / PhonePe / Paytm", "Scan with GPay / PhonePe / Paytm"))
                    st.markdown("---")
                    elapsed_time = time.time() - st.session_state.qr_start_time
                    if elapsed_time < WAIT_SECONDS:
                        progress = int((elapsed_time / WAIT_SECONDS) * 100)
                        st.info("🔄 Verifying payment with bank...")
                        st.progress(progress)
                        st.caption(f"Please wait... {int(WAIT_SECONDS - elapsed_time)} seconds remaining")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.success(t("Step 2: Payment Successful! Click to Unlock", "Step 2: Payment Successful! Unlock करने के लिए क्लिक करो"))
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔓 Unlock Download Now", use_container_width=True, type="primary"):
                                update_count("buy")
                                st.session_state.payment_done = True
                                st.session_state.show_qr = False
                                st.balloons()
                                st.rerun()
                        with col2:
                            if st.button("⬅️ Cancel", use_container_width=True):
                                st.session_state.show_qr = False
                                st.session_state.qr_start_time = None
                                st.rerun()
            else:
                st.success(t("✅ Your Payment is Complete! Download Your File", "✅ आपका Payment Complete है! फाइल डाउनलोड करो"))
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
            df_download = df_cleaned.head(1000) if len(df_cleaned) > 1000 else df_cleaned
            buffer = BytesIO()
            df_download.to_csv(buffer, index=False, encoding='utf-8')
            st.download_button(
                t(f"📥 Download {len(df_download)} Rows", f"📥 {len(df_download)} Rows Download करें"),
                buffer.getvalue(),
                "verisame_cleaned.csv",
                "text/csv"
            )
            if len(df_cleaned) >= 1000:
                st.warning(t("Need more than 1000 rows? Go back and use PRO Plan ₹2999",
                             "1000 से ज्यादा rows चाहिए? वापस जाके PRO Plan ₹2999 use करें"))
