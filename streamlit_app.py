import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components

# Google Search Console Verification
google_file = Path("googlef1bc5a74570309f0.html")
if google_file.exists():
    st.text(google_file.read_text())
    st.stop()

st.set_page_config(
    page_title="VeriSame - Free Excel & CSV Cleaner",
    page_icon="📊",
    layout="wide",
    menu_items={'About': "VeriSame cleans messy Excel files instantly"}
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
from datetime import datetime, timedelta
import requests

# ============ CONFIG ============
SHEET_ID = "1qwXIK_CLS32Rt4g21QeMs_fmVXK66Mxl0Z7IHBCU8nQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrgvFCfKGsYLitbVYwsh0tA2ih-BORqz7S9J2wc4BZtxshAQjjVylXuklAL4nDS4p-/exec"

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

# ============ SUBSCRIPTION FUNCTIONS ============
def check_user_in_sheet(email):
    try:
        df = pd.read_csv(SHEET_URL)
        user_row = df[df['email'] == email]
        if not user_row.empty:
            expiry_str = user_row.iloc[0]['expiry_date']
            if expiry_str in ['pending', 'verify_karo', 'rejected']:
                return False, expiry_str, user_row.iloc[0]['plan']
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
            if datetime.now() < expiry_date:
                return True, expiry_str, user_row.iloc[0]['plan']
        return False, None, None
    except:
        return False, None, None

def save_user_to_sheet(email, plan_type):
    plan_name = "1month" if plan_type == 'month' else "6months"
    try:
        requests.post(GOOGLE_SCRIPT_URL, json={"action": "new_user", "email": email, "plan": plan_name}, timeout=5)
    except:
        pass
    st.session_state.pro_plan_type = plan_type
    st.session_state.user_email = email

def mark_payment_done(email):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json={"action": "payment_done", "email": email}, timeout=5)
    except:
        pass

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
    st.markdown("---")
    st.subheader("📊 PRO Users List - Email + Status + Plan")
    try:
        users_df = pd.read_csv(SHEET_URL)
        st.dataframe(users_df, use_container_width=True)
        st.caption("💡 Payment verify karne ke liye: expiry_date column me 'verify_karo' ko 'approved' me badal de. Script auto date set kar dega.")
    except:
        st.info("Google Sheet connect nahi hua.")
    st.stop()

# ============ UPI CONFIG ============
UPI_ID = "playwithreyansh0@okhdfcbank"
PRO_AMOUNT_MONTH = 299
PRO_AMOUNT_HALF = 1499
WAIT_SECONDS = 25

# ============ CSS - 299 + 1499 DONO RED ============
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
.pro-box {
        background-color: #ffebee!important;
        padding: 15px!important;
        border-radius: 10px!important;
        border: 3px solid #ff1744!important;
        box-shadow: 0 4px 8px rgba(255,23,68,0.3)!important;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SESSION STATES ============
if 'plan' not in st.session_state: st.session_state.plan = None
if 'show_qr' not in st.session_state: st.session_state.show_qr = False
if 'payment_done' not in st.session_state: st.session_state.payment_done = False
if 'qr_start_time' not in st.session_state: st.session_state.qr_start_time = None
if 'selected_pro' not in st.session_state: st.session_state.selected_pro = None
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'pro_expiry' not in st.session_state: st.session_state.pro_expiry = None
if 'pro_plan_type' not in st.session_state: st.session_state.pro_plan_type = None
if 'ask_email' not in st.session_state: st.session_state.ask_email = False

def is_subscription_active():
    if st.session_state.user_email and st.session_state.pro_expiry:
        if st.session_state.pro_expiry in ['pending', 'verify_karo', 'rejected']:
            return False
        try:
            expiry = datetime.strptime(st.session_state.pro_expiry, '%Y-%m-%d')
            return datetime.now() < expiry
        except:
            return False
    return False

def text_to_number(text):
    if pd.isna(text): return text
    text = str(text).strip().upper()
    if re.match(r'^[\d,.\s]+$', text): return text.replace(',', '').strip()
    return text

with st.sidebar:
    st.title("💼 VeriSame")
    if is_subscription_active():
        st.success(f"✅ PRO Active")
        st.caption(f"Email: {st.session_state.user_email}")
        st.caption(f"Till: {st.session_state.pro_expiry}")
        if st.button("🚪 Logout"):
            st.session_state.user_email = None
            st.session_state.pro_expiry = None
            st.session_state.pro_plan_type = None
            st.session_state.payment_done = False
            st.rerun()
    if st.session_state.plan:
        if st.button("← Back to Plans"):
            st.session_state.plan = None
            st.session_state.show_qr = False
            st.session_state.qr_start_time = None
            st.session_state.selected_pro = None
            st.session_state.ask_email = False
            st.session_state.payment_done = False
            if 'sample_df' in st.session_state: del st.session_state['sample_df']
            st.rerun()

# LANDING PAGE
if st.session_state.plan is None:
    if is_subscription_active():
        st.session_state.plan = 'pro'
        st.session_state.payment_done = True
        st.session_state.selected_pro = st.session_state.pro_plan_type
        st.rerun()

    st.image("https://i.ibb.co/W43B7drG/VeriSame-logo.png", width=200)
    st.title("💼 Welcome to VeriSame")
    st.subheader("The Fastest Way to Clean Your Data")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("🆓 FREE Forever")
            st.markdown("✅ 1000 Rows Lifetime")
            st.markdown("✅ CSV Download")
            st.markdown("⏱️ 30 Second Wait")
            if st.button("Use FREE", use_container_width=True):
                update_count("free")
                st.session_state.plan = 'free'
                st.rerun()

    with col2:
        # 299 WALA RED
        st.markdown('<div class="pro-box">', unsafe_allow_html=True)
        with st.container():
            st.subheader("🔥 Monthly Pro")
            st.markdown("✅ Unlimited Rows - 1 Month")
            st.markdown("✅ Excel Export")
            st.markdown("⚡ 3 Second Speed")
            st.markdown(f"**₹{PRO_AMOUNT_MONTH} / month**")
            if st.button("⚡ ₹299 / Month", use_container_width=True):
                update_count("pro_month")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'month'
                st.session_state.ask_email = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        # 1499 WALA BHI RED
        st.markdown('<div class="pro-box">', unsafe_allow_html=True)
        with st.container():
            st.subheader("💎 Best Value")
            st.markdown("✅ Unlimited Rows - 6 Months")
            st.markdown("✅ Excel Export")
            st.markdown("⚡ 3 Second Speed")
            st.markdown(f"**₹{PRO_AMOUNT_HALF} / 6 months**")
            st.success("Save ₹295 vs Monthly")
            if st.button("💎 ₹1499 / 6 Months", use_container_width=True, type="primary"):
                update_count("pro_half")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'half'
                st.session_state.ask_email = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# UPLOAD PAGE - BAaki sab same hai
else:
    is_pro = st.session_state.plan == 'pro'
    pro_amount = PRO_AMOUNT_HALF if st.session_state.selected_pro == 'half' else PRO_AMOUNT_MONTH
    pro_text = "6 Months" if st.session_state.selected_pro == 'half' else "1 Month"

    if st.button("⬅️ Back to Plans", use_container_width=True):
        st.session_state.plan = None
        st.session_state.show_qr = False
        st.session_state.qr_start_time = None
        st.session_state.selected_pro = None
        st.session_state.ask_email = False
        st.session_state.payment_done = False
        if 'sample_df' in st.session_state: del st.session_state['sample_df']
        st.rerun()

    st.markdown("---")

    if is_pro:
        if st.session_state.ask_email and not st.session_state.user_email:
            st.title(f"💎 VeriSame PRO - {pro_text}")
            st.warning("Enter your email before payment. One time only.")
            email_input = st.text_input("Enter your email:", placeholder="yourname@gmail.com", key="pro_email_input")
            if st.button("Data Cleaning", use_container_width=True, type="primary"):
                if email_input and "@" in email_input:
                    is_active, expiry, plan = check_user_in_sheet(email_input)
                    if is_active:
                        st.session_state.user_email = email_input
                        st.session_state.pro_expiry = expiry
                        st.session_state.pro_plan_type = plan
                        st.session_state.payment_done = True
                        st.session_state.ask_email = False
                        st.success(f"Welcome back! PRO active till {expiry}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.session_state.user_email = email_input
                        st.session_state.ask_email = False
                        st.session_state.show_qr = True
                        st.session_state.qr_start_time = time.time()
                        save_user_to_sheet(email_input, st.session_state.selected_pro)
                        st.success(f"Email saved: {email_input}")
                        st.rerun()
                else:
                    st.error("Please enter a valid email")
            st.stop()

        if is_subscription_active():
            st.title(f"💎 VeriSame PRO - Active")
            st.success(f"✅ Welcome {st.session_state.user_email}")
            st.caption(f"PRO expires on: {st.session_state.pro_expiry}")
        else:
            st.title(f"💎 VeriSame PRO - {pro_text}")
            st.info(f"Logged in as: {st.session_state.user_email}")
    else:
        st.title("🆓 VeriSame FREE")

    if is_pro and not st.session_state.user_email:
        st.stop()

    with st.expander("🧪 Don't have a file? Test with sample data"):
        if st.button("Load Sample Data", use_container_width=True):
            sample_data = """Ref_ID,Category,JoinDate,Value,Gender
A101,Category_X,15-01-2024,100,Male
B202,Category_Y,2024-03-20,,Female"""
            st.session_state['sample_df'] = pd.read_csv(StringIO(sample_data))
            st.success("✅ Sample data loaded")
            st.rerun()

    uploaded_file = st.file_uploader("Upload your CSV/Excel/JSON file", type=["csv", "xlsx", "xls", "json"])

    df = None
    original_row_count = 0
    file_source = None
    if uploaded_file:
        file_source = uploaded_file
    elif 'sample_df' in st.session_state:
        file_source = 'sample'
        st.info("Using: Sample Test Data")

    if file_source:
        if file_source!= 'sample' and uploaded_file.size > 200 * 1024:
            st.error("File > 200MB not allowed")
            st.stop()

        wait_time = 3 if is_pro else 30
        with st.spinner(f"Cleaning data... {wait_time}s"):
            time.sleep(wait_time)

        try:
            if file_source == 'sample':
                df = st.session_state['sample_df'].copy()
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
            st.warning(f"FREE limit: Processing first 1000 rows out of {original_row_count} rows.")
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
                date_cols = st.multiselect("Select Date Columns", df_cleaned.columns.tolist(), key="date_cols")
                if date_cols:
                    for col in date_cols:
                        df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                    st.success(f"✅ Dates standardized in {len(date_cols)} columns")
            with tool_col2:
                st.markdown("**2. Smart Fill Missing Values**")
                numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    fill_method = st.selectbox("Fill Missing Numbers Using:", ["None", "Mean", "Median", "Zero", "Custom Value"], key="fill_method")
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
            st.caption("🔒 VeriSame PRO")
        else:
            st.write("**Preview - First 5 Rows:**")
            st.dataframe(df_display.head())

        st.markdown("---")

        if is_pro:
            if is_subscription_active():
                st.success(f"✅ Download Unlocked till {st.session_state.pro_expiry}")
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_cleaned.to_excel(writer, index=False, sheet_name='CleanedData')
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📊 Download as Excel", excel_buffer.getvalue(), "verisame_cleaned.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                with col2:
                    csv_buffer = BytesIO()
                    df_cleaned.to_csv(csv_buffer, index=False, encoding='utf-8')
                    st.download_button("📄 Download as CSV", csv_buffer.getvalue(), "verisame_cleaned.csv", "text/csv")

            elif st.session_state.payment_done:
                st.title("🎉 Thank You for Payment!")
                st.success("✅ Your payment request is sent to CEO")
                st.info("⏳ VeriSame PRO will be activated within 5 minutes after verification")
                st.balloons()
                st.markdown("---")
                st.subheader("📥 Your Cleaned File Ready")
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_cleaned.to_excel(writer, index=False, sheet_name='CleanedData')
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📊 Download as Excel", excel_buffer.getvalue(), "verisame_cleaned.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                with col2:
                    csv_buffer = BytesIO()
                    df_cleaned.to_csv(csv_buffer, index=False, encoding='utf-8')
                    st.download_button("📄 Download as CSV", csv_buffer.getvalue(), "verisame_cleaned.csv", "text/csv")

            elif st.session_state.show_qr:
                st.warning("Step 1: Scan QR & Complete Payment")
                upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={pro_amount}&cu=INR&tn={st.session_state.user_email}"
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
                    st.markdown(f"**Email:** `{st.session_state.user_email}`")
                st.markdown("---")
                elapsed_time = time.time() - st.session_state.qr_start_time
                if elapsed_time < WAIT_SECONDS:
                    progress = int((elapsed_time / WAIT_SECONDS) * 100)
                    st.info("🔄 Waiting for payment...")
                    st.progress(progress)
                    st.caption(f"Please wait... {int(WAIT_SECONDS - elapsed_time)} seconds remaining")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.success("Step 2: Payment Done? Click to Unlock")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"🔓 I Paid ₹{pro_amount} - Activate PRO", use_container_width=True, type="primary"):
                            update_count("buy")
                            mark_payment_done(st.session_state.user_email)
                            st.session_state.payment_done = True
                            st.session_state.show_qr = False
                            st.balloons()
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Cancel", use_container_width=True):
                            st.session_state.show_qr = False
                            st.session_state.qr_start_time = None
                            st.session_state.ask_email = True
                            st.rerun()
                st.stop()
        else:
            df_download = df_cleaned.head(1000) if len(df_cleaned) > 1000 else df_cleaned
            buffer = BytesIO()
            df_download.to_csv(buffer, index=False, encoding='utf-8')
            st.download_button(f"📥 Download {len(df_download)} Rows", buffer.getvalue(), "verisame_cleaned.csv", "text/csv")
            if len(df_cleaned) >= 1000:
                st.warning("Need more than 1000 rows? Go back and choose Monthly ₹299 or 6-Month ₹1499")
