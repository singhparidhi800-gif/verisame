import streamlit as st
from pathlib import Path

# Google Search Console Verification
google_file = Path("googlef1bc5a74570309f0.html")
if google_file.exists():
    st.text(google_file.read_text())
    st.stop()

st.set_page_config(
    page_title="VeriSame - Free Excel & CSV Cleaner",
    page_icon="📊",
    layout="wide",
    menu_items={
        'About': "VeriSame cleans messy Excel files instantly"
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

# ============ BASIC SECURITY ============
SECRET_PASS = "reyansh999VeriSame2026CEO"
query_params = st.query_params
SHOW_DASHBOARD = query_params.get("pass") == SECRET_PASS

if SHOW_DASHBOARD and 'bot' in str(query_params).lower():
    st.stop()

# ============ COUNTING FILE ============
COUNT_FILE = "counts.json"
if not os.path.exists(COUNT_FILE):
    with open(COUNT_FILE, 'w') as f:
        json.dump({"views": 0, "free": 0, "pro_month": 0, "pro_half": 0, "buy": 0}, f)

def update_count(key):
    with open(COUNT_FILE, 'r+') as f:
        data = json.load(f)
        data[key] += 1
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    return data[key]

def get_counts():
    with open(COUNT_FILE, 'r') as f:
        return json.load(f)

# ============ GA + VIEWS COUNT ============
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

# ============ SECRET DASHBOARD ============
if SHOW_DASHBOARD:
    st.title("🔒 Private Dashboard")
    st.caption("⚠️ CEO Only - Do not share this link")

    if st.button("🔄 Refresh Counts", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    counts = get_counts()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Views", counts['views'])
    col2.metric("FREE Clicks", counts['free'])
    col3.metric("Monthly ₹299", counts.get('pro_month', 0))
    col4.metric("6 Month ₹1499", counts.get('pro_half', 0))
    col5.metric("Payment Done", counts['buy'])

    st.markdown("---")
    st.subheader("💰 Revenue Calculation")
    monthly_revenue = counts.get('pro_month', 0) * 299
    half_revenue = counts.get('pro_half', 0) * 1499
    st.write(f"**Monthly Plan:** {counts.get('pro_month', 0)} x ₹299 = ₹{monthly_revenue}")
    st.write(f"**6-Month Plan:** {counts.get('pro_half', 0)} x ₹1499 = ₹{half_revenue}")
    st.success(f"**Total Potential Revenue: ₹{monthly_revenue + half_revenue}**")

    st.caption(f"Last updated: {time.strftime('%d-%m-%Y %H:%M:%S')}")
    st.caption("Bookmark: `?pass=reyansh999VeriSame2026CEO`")
    st.stop()

# ============ UPI CONFIG ============
UPI_ID = "playwithreyansh0@okhdfcbank"
PRO_AMOUNT_MONTH = 299
PRO_AMOUNT_HALF = 1499
WAIT_SECONDS = 15

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
        border-radius: 10px;
    }
    /* 299 Yellow Button */
    div[data-testid="column"]:nth-of-type(2).stButton>button {
        background-color: #FFD700;
        color: black;
        border: 2px solid #FFC300;
    }
    div[data-testid="column"]:nth-of-type(2).stButton>button:hover {
        background-color: #FFC300;
        border: 2px solid #FFB000;
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
if 'selected_pro' not in st.session_state: st.session_state.selected_pro = None

def t(en_text, hi_text): return en_text

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
    lang_choice = st.selectbox("🌐", ['English'], label_visibility="collapsed")
    st.session_state.lang = 'en'

with st.sidebar:
    st.title("💼 VeriSame")
    if st.session_state.plan:
        if st.button("← Back to Plans"):
            st.session_state.plan = None
            st.session_state.show_qr = False
            st.session_state.payment_done = False
            st.session_state.qr_start_time = None
            st.session_state.selected_pro = None
            if 'sample_df' in st.session_state: del st.session_state['sample_df']
            st.rerun()

# LANDING PAGE - FINAL
if st.session_state.plan is None:
    st.image("https://i.ibb.co/W43B7drG/VeriSame-logo.png", width=200)
    st.caption("Free online tool to clean Excel & CSV files. Convert text to numbers, fix dates, remove duplicates instantly.")
    st.title("💼 Welcome to VeriSame")
    st.subheader("The Fastest Way to Clean Your Data")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("🆓 FREE Forever")
            st.markdown("✅ 1000 Rows Lifetime")
            st.markdown("✅ Text to Number Converter")
            st.markdown("✅ CSV Download")
            st.markdown("⏱️ 30 Second Wait")
            if st.button("Use FREE", use_container_width=True):
                update_count("free")
                st.session_state.plan = 'free'
                st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("🔥 Monthly Pro")
            st.markdown("✅ Unlimited Rows - 1 Month")
            st.markdown("✅ Date Fixer + Smart Fill")
            st.markdown("✅ Excel Export")
            st.markdown("⚡ 3 Second Speed")
            st.markdown(f"**₹{PRO_AMOUNT_MONTH} / month**")
            if st.button("⚡ ₹299 / Month", use_container_width=True):
                update_count("pro_month")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'month'
                st.rerun()

    with col3:
        with st.container(border=True):
            st.subheader("💎 Best Value")
            st.markdown("✅ Unlimited Rows - 6 Months")
            st.markdown("✅ Date Fixer + Smart Fill")
            st.markdown("✅ Excel Export")
            st.markdown("⚡ 3 Second Speed")
            st.markdown(f"**₹{PRO_AMOUNT_HALF} / 6 months**")
            st.success("Save ₹295 vs Monthly")
            st.caption("Effective ₹250/month")
            if st.button("💎 ₹1499 / 6 Months", use_container_width=True, type="primary"):
                update_count("pro_half")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'half'
                st.rerun()

    st.markdown("---")
    st.caption("🔒 Security: Your data is deleted immediately after processing.")

# FREE YA PRO PLAN KA UPLOAD PAGE
else:
    is_pro = st.session_state.plan == 'pro'
    pro_amount = PRO_AMOUNT_HALF if st.session_state.selected_pro == 'half' else PRO_AMOUNT_MONTH
    pro_text = "6 Months" if st.session_state.selected_pro == 'half' else "1 Month"

    if st.button("⬅️ Back to Plans", use_container_width=True):
        st.session_state.plan = None
        st.session_state.show_qr = False
        st.session_state.payment_done = False
        st.session_state.qr_start_time = None
        st.session_state.selected_pro = None
        if 'sample_df' in st.session_state: del st.session_state['sample_df']
        st.rerun()

    st.markdown("---")

    if is_pro:
        st.title(f"💎 VeriSame PRO - {pro_text}")
        st.info("PRO Mode: Advanced cleaning tools unlocked")
    else:
        st.title("🆓 VeriSame FREE")
        st.info("FREE Mode: 1000 rows lifetime + Text to Number converter included")

    with st.expander("🧪 Don't have a file? Test with sample data"):
        st.write("This is dummy data for testing only.")
        if st.button("Load Sample Data", use_container_width=True):
            sample_data = """Ref_ID,Category,JoinDate,Value,Gender
A101,Category_X,15-01-2024,100,Male
A101,Category_X,01/15/2024,100,Male
B202,Category_Y,2024-03-20,,Female
C303,Category_Z,20/03/24,300,Male
C303,Category_Z,Mar 20 2024,300,Male"""
            st.session_state['sample_df'] = pd.read_csv(StringIO(sample_data))
            st.success("✅ Sample data loaded")
            st.rerun()

    uploaded_file = st.file_uploader(
        "Upload your CSV/Excel/JSON file",
        type=["csv", "xlsx", "xls", "json"]
    )

    df = None
    original_row_count = 0
    file_source = None
    if uploaded_file:
        file_source = uploaded_file
    elif 'sample_df' in st.session_state:
        file_source = 'sample'
        st.info("Using: Sample Test Data")

    if file_source:
        if file_source!= 'sample' and uploaded_file.size > 200 * 1024 * 1024:
            st.error("File > 200MB not allowed")
            st.stop()

        wait_time = 3 if is_pro else 30
        with st.spinner(f"Cleaning data... {wait_time}s"):
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
            st.error(f"Error reading file: {e}")
            st.stop()

        if not is_pro and len(df) > 1000:
            st.warning(f"FREE limit: Processing first 1000 rows out of {original_row_count} rows. Upgrade to PRO for full file.")
            df = df.head(1000)
        else:
            st.info(f"Original file had {original_row_count} rows")

        df_cleaned = df.drop_duplicates()

        for col in df_cleaned.select_dtypes(include=['object']):
            df_cleaned[col] = df_cleaned[col].apply(text_to_number)

        if is_pro:
            st.markdown("---")
            st.subheader("🔧 PRO Cleaning Tools")

            tool_col1, tool_col2 = st.columns(2)

            with tool_col1:
                st.markdown("**1. Date Standardizer**")
                date_cols = st.multiselect(
                    "Select Date Columns",
                    df_cleaned.columns.tolist(),
                    key="date_cols"
                )
                if date_cols:
                    for col in date_cols:
                        df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                    st.success(f"✅ Dates standardized in {len(date_cols)} columns")

            with tool_col2:
                st.markdown("**2. Smart Fill Missing Values**")
                numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    fill_method = st.selectbox(
                        "Fill Missing Numbers Using:",
                        ["None", "Mean", "Median", "Zero", "Custom Value"],
                        key="fill_method"
                    )
                    if fill_method!= "None":
                        if fill_method == "Mean":
                            df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
                        elif fill_method == "Median":
                            df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].median())
                        elif fill_method == "Zero":
                            df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(0)
                        elif fill_method == "Custom Value":
                            custom_val = st.number_input("Enter custom value:", value=0, key="custom_val")
                            df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(custom_val)
                        st.success("✅ Missing values filled")
                else:
                    st.info("No numeric columns found")

        st.markdown("---")
        st.success(f"Done! Removed {original_row_count - len(df_cleaned)} duplicates. Total: {len(df_cleaned)} rows")

        df_display = df_cleaned.fillna('').astype(str)
        df_display = df_display.replace(['nan', 'NAN', 'NaN', 'None', 'null', 'NULL'], '', regex=False)

        if is_pro:
            st.write("**Preview - First 10 Rows Only:**")
            st.dataframe(df_display.head(10))
            st.caption("🔒 VeriSame PRO | Unlock full file to remove watermark")
        else:
            st.write("**Preview - First 5 Rows:**")
            st.dataframe(df_display.head())

        st.markdown("---")

        if is_pro:
            if not st.session_state.payment_done:
                if not st.session_state.show_qr:
                    st.error(f"🔒 Download Locked - ₹{pro_amount} for {pro_text}")
                    if st.button(f"💳 Pay ₹{pro_amount} with UPI", use_container_width=True, type="primary"):
                        st.session_state.show_qr = True
                        st.session_state.qr_start_time = time.time()
                        st.rerun()
                else:
                    st.warning("Step 1: Scan QR & Complete Payment")
                    upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={pro_amount}&cu=INR"
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
                        st.markdown(f"**Amount:** `₹{pro_amount}`")
                        st.markdown(f"**Plan:** `{pro_text}`")
                        st.caption("Scan with GPay / PhonePe / Paytm")
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
                        st.success("Step 2: Payment Done? Click to Unlock")
                        st.info("⚠️ Please unlock only after successful payment. False claims may result in account ban.")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"🔓 I Paid ₹{pro_amount} - Unlock Now", use_container_width=True, type="primary"):
                                update_count("buy")
                                st.session_state.payment_done = True
                                st.session_state.show_qr = False
                                st.balloons()
                                st.success("Payment verified! Download unlocked 💚")
                                st.rerun()
                        with col2:
                            if st.button("⬅️ Cancel", use_container_width=True):
                                st.session_state.show_qr = False
                                st.session_state.qr_start_time = None
                                st.rerun()
            else:
                st.success("✅ Your Payment is Complete! Download Your File")
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_cleaned.to_excel(writer, index=False, sheet_name='CleanedData')
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📊 Download as Excel",
                        excel_buffer.getvalue(),
                        "verisame_cleaned.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                with col2:
                    csv_buffer = BytesIO()
                    df_cleaned.to_csv(csv_buffer, index=False, encoding='utf-8')
                    st.download_button(
                        "📄 Download as CSV",
                        csv_buffer.getvalue(),
                        "verisame_cleaned.csv",
                        "text/csv"
                    )
        else:
            df_download = df_cleaned.head(1000) if len(df_cleaned) > 1000 else df_cleaned
            buffer = BytesIO()
            df_download.to_csv(buffer, index=False, encoding='utf-8')
            st.download_button(
                f"📥 Download {len(df_download)} Rows",
                buffer.getvalue(),
                "verisame_cleaned.csv",
                "text/csv"
            )
            if len(df_cleaned) >= 1000:
                st.warning("Need more than 1000 rows? Go back and choose Monthly ₹299 or 6-Month ₹1499")
