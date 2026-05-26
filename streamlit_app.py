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
import json
import os
from datetime import datetime, timedelta
import requests

# ============ CONFIG ============
SHEET_ID = "1qwXIK_CLS32Rt4g21QeMs_fmVXK66Mxl0Z7IHBCU8nQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxdVnCZi91JhBR4L9kt2H1KbpOoxiWNqNXGcoth459Q486m84tjSYzlFYkHC3Fl7AXbZg/exec"
WHATSAPP_NUMBER = "919794906852"

# ============ UPI CONFIG ============
UPI_ID = "playwithreyansh0@okhdfcbank"
PRO_AMOUNT_MONTH = 299
PRO_AMOUNT_HALF = 1499
WAIT_SECONDS = 25

# ============ BASIC SECURITY ============
SECRET_PASS = "reyansh999VeriSame2026CEO"
query_params = st.query_params
SHOW_DASHBOARD = query_params.get("pass") == SECRET_PASS

if SHOW_DASHBOARD and 'bot' in str(query_params).lower():
    st.stop()

# ============ EMAIL MEMORY - SIRF URL SE ✅ ============
url_email = query_params.get("user")
if url_email and 'user_email' not in st.session_state:
    st.session_state.user_email = url_email.strip()

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

# ============ SUBSCRIPTION FUNCTIONS - FIXED ✅ ============
@st.cache_data(ttl=10)
def check_user_in_sheet(email):
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip().str.lower()
        df['email'] = df['email'].str.strip().str.lower()
        user_rows = df[df['email'] == email.lower().strip()]

        if not user_rows.empty:
            user_row = user_rows.iloc[-1]
            status = str(user_row['status']).strip()
            expiry_str = str(user_row['expiry_date']).strip()
            plan = str(user_row['plan']).strip()

            if status == 'Verification_Pending':
                return False, "verification_pending", plan

            if status!= 'Paid':
                return False, "not_verified", plan

            if expiry_str.lower() in ['pending', 'verify_karo', 'rejected', 'nan', '']:
                return False, "not_verified", plan

            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    expiry_date = datetime.strptime(expiry_str, fmt)
                    if datetime.now().date() <= expiry_date.date():
                        return True, expiry_date.strftime('%Y-%m-%d'), plan
                    else:
                        return False, "expired", plan
                except:
                    continue
            return False, "invalid_date", plan
        return False, "not_found", None
    except Exception as e:
        return False, "sheet_error", None

def save_user_to_sheet(email, plan_type):
    plan_name = "1month" if plan_type == 'month' else "6months"
    amount = PRO_AMOUNT_MONTH if plan_type == 'month' else PRO_AMOUNT_HALF
    try:
        payload = {
            "action": "new_user",
            "email": email,
            "plan": plan_name,
            "amount": amount
        }
        headers = {'Content-Type': 'text/plain'}
        requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload), headers=headers, timeout=5)
    except Exception as e:
        st.error(f"Sheet me save nahi hua: {e}")

def request_payment_verification(email):
    try:
        payload = {"action": "payment_request", "email": email}
        headers = {'Content-Type': 'text/plain'}
        requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload), headers=headers, timeout=5)
    except:
        pass

# ============ GA + VIEWS COUNT - FIXED ✅ ============
if not SHOW_DASHBOARD:
    if 'counted_session' not in st.session_state:
        update_count("views")
        st.session_state.counted_session = True
    GA_MEASUREMENT_ID = "G-7E6HS2Q6Q3"
    st.markdown(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """, unsafe_allow_html=True)

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
        st.caption("💡 IMPORTANT: Purane duplicate rows delete kar de. Sirf latest date wali rakho.")
    except:
        st.info("Google Sheet connect nahi hua.")
    st.stop()

# ============ CSS ============
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
   .stApp {{
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradientBG 25s ease infinite;
        background-attachment: fixed;
    }}
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
   .block-container {{
        padding: 2rem 3rem;
        max-width: 1300px;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }}
   .stButton>button {{
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 15px;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-transform: uppercase;
    }}
   .stButton>button:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }}
    div[data-testid="column"]:nth-of-type(1) > div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)!important;
        border: none!important;
        border-radius: 25px!important;
        padding: 20px;
    }}
    div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)!important;
        border: none!important;
        border-radius: 25px!important;
        padding: 20px;
    }}
    div[data-testid="column"]:nth-of-type(3) > div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)!important;
        border: 4px solid #ff6b6b!important;
        border-radius: 25px!important;
        padding: 20px;
        transform: scale(1.03);
    }}
   .tools-banner {{
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 35px;
        border-radius: 25px;
        margin: 30px 0;
        color: white;
    }}
   .tool-item {{
        display: inline-block;
        background: rgba(255,255,255,0.25);
        padding: 12px 20px;
        border-radius: 30px;
        margin: 8px;
        font-size: 15px;
        font-weight: 700;
    }}
   .help-float {{
        position: fixed;
        bottom: 35px;
        right: 35px;
        z-index: 9999;
    }}
   .help-float a {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 70px;
        height: 70px;
        background: #25D366;
        border-radius: 50%;
        box-shadow: 0 8px 30px rgba(37,211,102,0.6);
        text-decoration: none;
        font-size: 35px;
    }}
    </style>
    <div class="help-float">
        <a href="https://wa.me/{WHATSAPP_NUMBER}?text=Hi%20VeriSame%20Team,%20I%20need%20help" target="_blank">💬</a>
    </div>
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
if 'show_pay_button' not in st.session_state: st.session_state.show_pay_button = False
if 'df_cleaned' not in st.session_state: st.session_state.df_cleaned = None
if 'pro_status_checked' not in st.session_state: st.session_state.pro_status_checked = False
if 'payment_log_done' not in st.session_state: st.session_state.payment_log_done = False

def is_subscription_active():
    if st.session_state.pro_expiry and st.session_state.pro_expiry not in ['not_verified', 'expired', 'invalid_date', 'not_found', 'sheet_error', 'verification_pending']:
        try:
            expiry = datetime.strptime(st.session_state.pro_expiry, '%Y-%m-%d')
            return datetime.now().date() <= expiry.date()
        except:
            return False
    return False

def text_to_number(text):
    if pd.isna(text): return text
    text = str(text).strip().upper()
    if re.match(r'^[\d,.\s]+$', text): return text.replace(',', '').strip()
    return text

# 👇 SIDEBAR ME EMAIL + LOGOUT FIX KIYA
with st.sidebar:
    st.title("💼 VeriSame")

    if st.session_state.user_email:
        st.success(f"✅ Logged in")
        st.caption(f"📧 Email: {st.session_state.user_email}")

        if is_subscription_active():
            st.caption(f"PRO till: {st.session_state.pro_expiry}")
            plan_text = "1 Month" if st.session_state.pro_plan_type == '1month' else "6 Months"
            st.caption(f"Plan: {plan_text}")
        elif st.session_state.pro_expiry == 'verification_pending':
            st.warning("⏳ Verification Pending")
            st.caption("Admin 5-10 min me activate kar dega")
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.session_state.pro_status_checked = False
                st.rerun()
        else:
            st.info("PRO inactive - Payment karo")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_email = None
            st.session_state.pro_expiry = None
            st.session_state.pro_plan_type = None
            st.session_state.payment_done = False
            st.session_state.pro_status_checked = False
            st.session_state.payment_log_done = False
            st.session_state.plan = None
            st.query_params.clear()
            st.success("Logged out successfully!")
            time.sleep(1)
            st.rerun()
    else:
        st.info("Login karo PRO lene ke liye")

    st.markdown("---")
    st.markdown("### 📞 Need Help?")
    st.markdown(f"[💬 WhatsApp Chat](https://wa.me/{WHATSAPP_NUMBER})")
    st.markdown("📧 support@verisame.com")
    st.markdown("---")

    if st.session_state.plan:
        if st.button("← Back to Plans"):
            st.session_state.plan = None
            st.session_state.show_qr = False
            st.session_state.qr_start_time = None
            st.session_state.selected_pro = None
            st.session_state.ask_email = False
            st.session_state.payment_done = False
            st.session_state.show_pay_button = False
            st.session_state.df_cleaned = None
            st.session_state.payment_log_done = False
            if 'sample_df' in st.session_state: del st.session_state['sample_df']
            st.rerun()

# LANDING PAGE
st.image("https://i.ibb.co/W43B7drG/VeriSame-logo.png", width=300)
st.title("💼 Welcome to VeriSame")
st.subheader("The Fastest Way to Clean Your Data")

if st.session_state.plan is None:
    if st.session_state.user_email and not st.session_state.pro_status_checked:
        is_active, expiry, plan = check_user_in_sheet(st.session_state.user_email)
        st.session_state.pro_expiry = expiry
        st.session_state.pro_plan_type = plan
        st.session_state.pro_status_checked = True
        if is_active:
            st.session_state.plan = 'pro'
            st.session_state.payment_done = True
            st.session_state.selected_pro = 'month' if plan == '1month' else 'half'
            st.rerun()

    st.markdown("""
    <div class="tools-banner">
        <h3 style='margin:0 0 15px 0; text-align:center;'>🚀 PRO Includes 7 Advanced Tools</h3>
        <div style='text-align:center;'>
            <span class="tool-item">📅 Date Standardizer</span>
            <span class="tool-item">🔢 Smart Fill Missing</span>
            <span class="tool-item">📧 Email Validator</span>
            <span class="tool-item">📱 Phone Formatter</span>
            <span class="tool-item">🔤 Text Case Converter</span>
            <span class="tool-item">✨ Remove Special Chars</span>
            <span class="tool-item">✏️ Column Renamer</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("🆓 FREE Forever")
            st.markdown("✅ 1000 Rows Lifetime")
            st.markdown("✅ CSV Download")
            st.markdown("✅ 5 Basic Tools")
            st.markdown("⏱️ 30 Second Wait")
            if st.button("Use FREE", use_container_width=True):
                update_count("free")
                st.session_state.plan = 'free'
                st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("🔥 Monthly Pro")
            st.markdown("✅ Unlimited Rows - 1 Month")
            st.markdown("✅ Excel + CSV Export")
            st.markdown("✅ All 7 PRO Tools")
            st.markdown("⚡ 3 Second Speed")
            st.markdown(f"**₹{PRO_AMOUNT_MONTH} / month**")
            if st.button("⚡ ₹299 / Month", use_container_width=True):
                update_count("pro_month")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'month'
                st.session_state.ask_email = True
                st.session_state.pro_status_checked = False
                st.rerun()

    with col3:
        with st.container(border=True):
            st.subheader("💎 Best Value")
            st.markdown("✅ Unlimited Rows - 6 Months")
            st.markdown("✅ Excel + CSV Export")
            st.markdown("✅ All 7 PRO Tools")
            st.markdown("⚡ 3 Second Speed")
            st.markdown(f"**₹{PRO_AMOUNT_HALF} / 6 months**")
            st.success("Save ₹295 vs Monthly")
            if st.button("💎 ₹1499 / 6 Months", use_container_width=True, type="primary"):
                update_count("pro_half")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'half'
                st.session_state.ask_email = True
                st.session_state.pro_status_checked = False
                st.rerun()

# UPLOAD PAGE
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
        st.session_state.show_pay_button = False
        st.session_state.df_cleaned = None
        st.session_state.payment_log_done = False
        if 'sample_df' in st.session_state: del st.session_state['sample_df']
        st.rerun()

    st.markdown("---")

    if is_pro:
        if st.session_state.ask_email and not st.session_state.user_email:
            st.title(f"💎 VeriSame PRO - {pro_text}")
            st.warning("Enter your email once.")
            email_input = st.text_input("Enter your email:", placeholder="yourname@gmail.com", key="pro_email_input")
            if st.button("Continue", use_container_width=True, type="primary"):
                if email_input and "@" in email_input:
                    st.session_state.user_email = email_input.strip()
                    st.query_params["user"] = email_input.strip()

                    is_active, expiry, plan = check_user_in_sheet(email_input.strip())
                    st.session_state.pro_expiry = expiry
                    st.session_state.pro_plan_type = plan
                    st.session_state.pro_status_checked = True

                    if is_active:
                        st.session_state.payment_done = True
                        st.session_state.ask_email = False
                        st.session_state.selected_pro = 'month' if plan == '1month' else 'half'
                        st.success(f"Welcome back! PRO active till {expiry}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.session_state.ask_email = False
                        save_user_to_sheet(email_input.strip(), st.session_state.selected_pro)
                        st.success(f"Email saved: {email_input}")
                        st.rerun()
                else:
                    st.error("Please enter a valid email")
            st.stop()

        if is_subscription_active():
            plan_name = "1 Month" if st.session_state.pro_plan_type == '1month' else "6 Months"
            st.title(f"💎 VeriSame PRO - Active")
            st.success(f"✅ Welcome {st.session_state.user_email}")
            st.caption(f"PRO expires on: {st.session_state.pro_expiry}")
        elif st.session_state.pro_expiry == 'verification_pending':
            st.title(f"💎 VeriSame PRO - {pro_text}")
            st.warning("⏳ **Verification Pending**")
            st.info(f"Logged in as: {st.session_state.user_email}")
            st.write("Aapka payment request mil gaya hai. Admin 5-10 minute me verify karke activate kar dega.")
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.session_state.pro_status_checked = False
                st.rerun()
            st.stop()
        else:
            st.title(f"💎 VeriSame PRO - {pro_text}")
            st.info(f"Logged in as: {st.session_state.user_email}")
    else:
        st.title("🆓 VeriSame FREE")

    if is_pro and not st.session_state.user_email:
        st.stop()

    with st.expander("🧪 Don't have a file? Test with sample data"):
        if st.button("Load Sample Data", use_container_width=True):
            sample_data = """Ref_ID,Category,JoinDate,Value,Gender,Email,Phone
A101,Category_X,15-01-2024,100,Male,test@mail.com,9876543210
B202,Category_Y,2024-03-20,,Female,invalid-email,12345
A101,Category_X,15-01-2024,100,Male,test@mail.com,9876543210
C303,Category_Z,01/04/2024,200,MALE,another@test.in,9988776655"""
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
        if file_source!= 'sample' and uploaded_file.size > 200 * 1024 * 1024:
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
            st.subheader("🔧 PRO Cleaning Tools - 7 Advanced Features")
            tab1, tab2, tab3 = st.tabs(["📅 Dates & Numbers", "📧 Email & Phone", "🎯 Advanced"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**1. Date Standardizer**")
                    date_cols = st.multiselect("Select Date Columns", df_cleaned.columns.tolist(), key="date_cols")
                    if date_cols:
                        for col in date_cols:
                            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                        st.success(f"✅ Dates standardized")
                with col2:
                    st.markdown("**2. Smart Fill Missing**")
                    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
                    if numeric_cols:
                        fill_method = st.selectbox("Fill Numbers Using:", ["None", "Mean", "Median", "Zero", "Custom"], key="fill_method")
                        if fill_method!= "None":
                            if fill_method == "Mean":
                                df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
                            elif fill_method == "Median":
                                df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].median())
                            elif fill_method == "Zero":
                                df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(0)
                            elif fill_method == "Custom":
                                custom_val = st.number_input("Custom value:", value=0, key="custom_val")
                                df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(custom_val)
                            st.success("✅ Missing filled")

            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**3. Email Validator**")
                    email_cols = st.multiselect("Email Columns", df_cleaned.columns.tolist(), key="email_cols")
                    if email_cols:
                        for col in email_cols:
                            df_cleaned[f'{col}_valid'] = df_cleaned[col].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)
                        st.success(f"✅ Email validated")
                with col2:
                    st.markdown("**4. Phone Formatter**")
                    phone_cols = st.multiselect("Phone Columns", df_cleaned.columns.tolist(), key="phone_cols")
                    if phone_cols:
                        for col in phone_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'\D', '', regex=True)
                        st.success(f"✅ Phone cleaned")

            with tab3:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**5. Text Case Converter**")
                    text_cols = st.multiselect("Text Columns", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="text_cols")
                    case_option = st.selectbox("Convert to:", ["None", "UPPERCASE", "lowercase", "Title Case"], key="case_opt")
                    if text_cols and case_option!= "None":
                        for col in text_cols:
                            if case_option == "UPPERCASE":
                                df_cleaned[col] = df_cleaned[col].str.upper()
                            elif case_option == "lowercase":
                                df_cleaned[col] = df_cleaned[col].str.lower()
                            elif case_option == "Title Case":
                                df_cleaned[col] = df_cleaned[col].str.title()
                        st.success(f"✅ Text converted")
                with col2:
                    st.markdown("**6. Remove Special Chars**")
                    special_cols = st.multiselect("Columns to Clean", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="special_cols")
                    if special_cols:
                        for col in special_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'[^\w\s]', '', regex=True)
                        st.success(f"✅ Special chars removed")

            st.markdown("**7. Column Renamer**")
            rename_col = st.selectbox("Select column to rename:", ["None"] + df_cleaned.columns.tolist(), key="rename_col")
            if rename_col!= "None":
                new_name = st.text_input(f"New name for '{rename_col}':", key="new_name")
                if st.button("Rename Column"):
                    df_cleaned = df_cleaned.rename(columns={rename_col: new_name})
                    st.success(f"✅ Renamed to '{new_name}'")
                    st.rerun()

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
            st.dataframe(df_display.head(5))

        st.markdown("---")
        st.session_state.df_cleaned = df_cleaned

        if is_pro:
            is_active, expiry, plan = check_user_in_sheet(st.session_state.user_email)
            st.session_state.pro_expiry = expiry
            st.session_state.pro_plan_type = plan

            user_has_month = plan == '1month'
            user_has_half = plan == '6months'
            selected_is_month = st.session_state.selected_pro == 'month'
            selected_is_half = st.session_state.selected_pro == 'half'

            if is_active and user_has_month and selected_is_half:
                st.warning("⚠️ You have 1 Month plan active. To upgrade to 6 Months, please pay ₹1499.")
                st.session_state.payment_done = False

            if is_active and ((user_has_month and selected_is_month) or (user_has_half)):
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

                plan_duration = "1 Month" if st.session_state.pro_plan_type == '1month' else "6 Months"
                st.info(f"🎉 You purchased {plan_duration} plan. PRO active till {st.session_state.pro_expiry}")

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
                upi_link = f"upi://pay?pa={UPI_ID}&pn=Abha%20Singh&am={pro_amount}&cu=INR&tn={st.session_state.user_email}"
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
                    st.markdown(f"**Support:** [WhatsApp](https://wa.me/{WHATSAPP_NUMBER})")

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
                        if st.button(f"🔓 I Paid ₹{pro_amount} - Verify Karo", use_container_width=True, type="primary"):
                            update_count("buy")
                            request_payment_verification(st.session_state.user_email)
                            st.session_state.payment_done = False
                            st.session_state.show_qr = False
                            st.session_state.show_pay_button = False
                            st.session_state.payment_log_done = False
                            st.success("Request submit! Admin 5-10 min me verify karke activate kar dega")
                            st.balloons()
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Cancel", use_container_width=True):
                            st.session_state.show_qr = False
                            st.session_state.qr_start_time = None
                            st.session_state.show_pay_button = True
                            st.session_state.payment_log_done = False
                            st.rerun()
                st.stop()

            else:
                st.info("💰 Payment Required to Download Full File")
                st.warning(f"Your cleaned file is ready with {len(df_cleaned)} rows")
                if st.button(f"💳 Pay ₹{pro_amount} to Download - {pro_text}", use_container_width=True, type="primary"):
                    st.session_state.show_qr = True
                    st.session_state.qr_start_time = time.time()
                    st.session_state.show_pay_button = False
                    st.session_state.payment_log_done = False
                    st.rerun()

        else:
            df_download = df_cleaned.head(1000) if len(df_cleaned) > 1000 else df_cleaned
            buffer = BytesIO()
            df_download.to_csv(buffer, index=False, encoding='utf-8')
            st.download_button(f"📥 Download {len(df_download)} Rows", buffer.getvalue(), "verisame_cleaned.csv", "text/csv")
            if len(df_cleaned) >= 1000:
                st.warning("Need more than 1000 rows? Go back and choose Monthly ₹299 or 6-Month ₹1499")
