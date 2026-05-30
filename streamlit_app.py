import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components
import pandas as pd
import time
import numpy as np
import re
from io import BytesIO, StringIO
import qrcode
import json
import os
from datetime import datetime
import requests
import hashlib

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

# ============ 🔐 ULTRA SECURITY CONFIG ============
SHEET_ID = st.secrets.get("SHEET_ID", "1qwXIK_CLS32Rt4g21QeMs_fmVXK66Mxl0Z7IHBCU8nQ")
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
GOOGLE_SCRIPT_URL = st.secrets.get("GOOGLE_SCRIPT_URL", "https://script.google.com/macros/s/AKfycbxtz-CV6D5lTUWCb12newzOqSRg0I-INIKXZETmR7MtxHWjQfIIbYHoaAiatZz_13w/exec")
WHATSAPP_NUMBER = "919794906852"

UPI_ID = st.secrets.get("UPI_ID", "playwithreyansh0@okhdfcbank")
PRO_AMOUNT_MONTH = 299
PRO_AMOUNT_3MONTH = 1499
WAIT_SECONDS = 5 

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

HASHED_SECRET_PASS = "e2b0cc3dbb1fa74dfa1d82dd8f0cf4bf4911d9cb422fa1b490d1bfbe246ba62b"

query_params = st.query_params
provided_pass = query_params.get("pass", "")
SHOW_DASHBOARD = check_hashes(provided_pass, HASHED_SECRET_PASS) if provided_pass else False

if SHOW_DASHBOARD and 'bot' in str(query_params).lower():
    st.stop()

# ============ EMAIL MEMORY ============
url_email = query_params.get("user")
if url_email and 'user_email' not in st.session_state:
    st.session_state.user_email = url_email.strip()

# ============ COUNTING FILE ============
COUNT_FILE = "counts.json"
if not os.path.exists(COUNT_FILE):
    with open(COUNT_FILE, 'w') as f:
        json.dump({"views": 0, "free": 0, "pro_month": 0, "pro_half": 0, "buy": 0}, f)

def update_count(key):
    try:
        with open(COUNT_FILE, 'r+') as f:
            data = json.load(f)
            data[key] = data.get(key, 0) + 1
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        return data[key]
    except:
        return 0

def get_counts():
    try:
        with open(COUNT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"views": 0, "free": 0, "pro_month": 0, "pro_half": 0, "buy": 0}

# ============ SUBSCRIPTION FUNCTIONS ============
@st.cache_data(ttl=10)
def check_user_in_sheet(email):
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip().str.lower()
        df['email'] = df['email'].str.strip().str.lower()
        user_rows = df[df['email'] == email.lower().strip()]

        if not user_rows.empty:
            user_row = user_rows.iloc[-1]
            status = str(user_row['status']).strip().lower()
            expiry_str = str(user_row['expiry_date']).strip()
            plan = str(user_row['plan']).strip()

            if status == 'verification_pending':
                return False, "verification_pending", plan
            if status == 'rejected':
                return False, "rejected", plan
            if status != 'paid':
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
    plan_name = "1month" if plan_type == 'month' else "3month"
    amount = PRO_AMOUNT_MONTH if plan_type == 'month' else PRO_AMOUNT_3MONTH
    try:
        payload = {"action": "new_user", "email": email, "plan": plan_name, "amount": amount}
        headers = {'Content-Type': 'text/plain'}
        r = requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload), headers=headers, timeout=10)
        return r.status_code == 200 and "success" in r.text.lower()
    except:
        return False

def request_payment_verification(email):
    try:
        payload = {"action": "payment_request", "email": email}
        headers = {'Content-Type': 'text/plain'}
        requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload), headers=headers, timeout=5)
    except:
        pass

# GA SYSTEM
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
    st.caption("⚠️ CEO Only - Secure Encrypted Mode")
    if st.button("🔄 Refresh Counts", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    counts = get_counts()
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Views", counts.get('views', 0))
    col2.metric("FREE Clicks", counts.get('free', 0))
    col3.metric("Monthly ₹299", counts.get('pro_month', 0))
    col4.metric("6 Month ₹1499", counts.get('pro_half', 0))
    col5.metric("Payment Done", counts.get('buy', 0))
    st.markdown("---")
    st.subheader("💰 Revenue Calculation")
    monthly_revenue = counts.get('pro_month', 0) * 299
    half_revenue = counts.get('pro_half', 0) * 1499
    st.write(f"**Monthly Plan:** {counts.get('pro_month', 0)} x ₹299 = ₹{monthly_revenue}")
    st.write(f"**6-Month Plan:** {counts.get('pro_half', 0)} x ₹1499 = ₹{half_revenue}")
    st.success(f"**Total Potential Revenue: ₹{monthly_revenue + half_revenue}**")
    st.markdown("---")
    try:
        users_df = pd.read_csv(SHEET_URL)
        st.dataframe(users_df, use_container_width=True)
    except:
        st.info("Google Sheet not connected.")
    st.stop()

# ============ CSS DESIGN ============
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
   .stApp {{
        background: linear-gradient(-45deg, #1e293b, #0f172a, #1e1b4b, #0f172a);
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
        padding: 2.5rem 3.5rem;
        max-width: 1350px;
        background: rgba(255,255,255,0.98);
        border-radius: 24px;
        box-shadow: 0 24px 70px rgba(0,0,0,0.5);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }}
   .stButton>button {{
        width: 100%;
        height: 55px;
        font-size: 16px;
        font-weight: 700;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        border: none;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
    }}
   .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(124, 58, 237, 0.3);
    }}
    .metric-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }}
   .tools-banner {{
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        padding: 30px;
        border-radius: 20px;
        margin: 25px 0;
        color: white;
    }}
   .tool-item {{
        display: inline-block;
        background: rgba(255,255,255,0.15);
        padding: 10px 18px;
        border-radius: 20px;
        margin: 6px;
        font-size: 14px;
        font-weight: 600;
    }}
    .pro-lock-msg {{
        background: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        color: #991b1b;
        font-weight: 600;
        margin-bottom: 15px;
    }}
    </style>
""", unsafe_allow_html=True)

# ============ SESSION STATES ============
for state_key in ['plan', 'selected_pro', 'user_email', 'pro_expiry', 'pro_plan_type', 'df_cleaned']:
    if state_key not in st.session_state: st.session_state[state_key] = None

for bool_key in ['show_qr', 'payment_done', 'ask_email', 'show_pay_button', 'pro_status_checked', 'payment_log_done']:
    if bool_key not in st.session_state: st.session_state[bool_key] = False

if 'qr_start_time' not in st.session_state: st.session_state.qr_start_time = None

def is_subscription_active():
    if st.session_state.pro_expiry and st.session_state.pro_expiry not in ['not_verified', 'expired', 'invalid_date', 'not_found', 'sheet_error', 'verification_pending', 'rejected']:
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

# SIDEBAR
with st.sidebar:
    st.title("💼 VeriSame")
    if st.session_state.user_email:
        st.success(f"✅ Logged in")
        st.caption(f"📧 {st.session_state.user_email}")
        if is_subscription_active():
            st.caption(f"PRO active till: {st.session_state.pro_expiry}")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.query_params.clear()
            st.rerun()
    else:
        st.info("Login for PRO features")
    st.markdown("---")
    st.markdown(f"[💬 WhatsApp Support](https://wa.me/{WHATSAPP_NUMBER})")

# LANDING PAGE
st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png", width=260)
st.title("💼 VeriSame Studio")
st.subheader("The Professional Cloud Data Cleaner")

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
        <h3 style='margin:0 0 12px 0; text-align:center;'>🚀 FREE vs PRO System Capability Map</h3>
        <div style='text-align:center;'>
            <span class="tool-item">📅 Date Format Engine (PRO)</span>
            <span class="tool-item">🔢 Smart Analytics Reporter (FREE/PRO)</span>
            <span class="tool-item">📧 Regex Email Validator (PRO)</span>
            <span class="tool-item">📱 Phone Normalizer (PRO)</span>
            <span class="tool-item">🔤 String Case Standardizer (FREE/PRO)</span>
            <span class="tool-item">✨ Special Character Stripper (PRO)</span>
            <span class="tool-item">✏️ Column Hot-Swap Renamer (PRO)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("🆓 FREE Tier")
            st.markdown("• Up to 1000 rows limit\n• CSV Export only\n• Auto-Duplicate Filter\n• Basic Case Standardizer\n• Whitespace Trimmer\n• 15s process latency")
            if st.button("Access Free Tier", use_container_width=True):
                update_count("free")
                st.session_state.plan = 'free'
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("🔥 Monthly Pro")
            st.markdown("• Unlimited matrix depth\n• Native Excel + CSV Export\n• Complete 7 Tool Pack\n• Smart Auto-Detection\n• Instant cloud engine\n• **₹299 / Month**")
            if st.button("Buy Monthly Pro", use_container_width=True):
                update_count("pro_month")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'month'
                st.session_state.ask_email = True
                st.session_state.pro_status_checked = False
                st.rerun()
    with col3:
        with st.container(border=True):
            st.subheader("💎 Best Value")
            st.markdown("• 6 Month global license\n• Full business tool access\n• Dedicated priority engine\n• Custom template memory\n• **₹1499 / 6 Months**")
            if st.button("Unlock 6 Months", use_container_width=True, type="primary"):
                update_count("pro_half")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'half'
                st.session_state.ask_email = True
                st.session_state.pro_status_checked = False
                st.rerun()

# PROCESSING SEGMENT
else:
    is_pro_user = (st.session_state.plan == 'pro' and is_subscription_active())
    pro_amount = PRO_AMOUNT_3MONTH if st.session_state.selected_pro == 'half' else PRO_AMOUNT_MONTH
    pro_text = "6 Months License" if st.session_state.selected_pro == 'half' else "1 Month License"

    if st.button("⬅️ Return to Studio Mainframe", key="main_back", use_container_width=True):
        st.session_state.plan = None
        st.session_state.show_qr = False
        st.session_state.qr_start_time = None
        st.session_state.df_cleaned = None
        st.rerun()

    st.markdown("---")

    if st.session_state.plan == 'pro':
        if st.session_state.ask_email and not st.session_state.user_email:
            st.title(f"💎 Gateway Identity Setup - {pro_text}")
            email_input = st.text_input("Register Enterprise Email:", placeholder="username@domain.com")
            if st.button("Initialize Pipeline", use_container_width=True, type="primary"):
                cleaned_email = email_input.strip().lower() if email_input else ""
                if cleaned_email and "@" in cleaned_email and "." in cleaned_email:
                    st.session_state.user_email = cleaned_email
                    st.query_params["user"] = cleaned_email
                    is_active, expiry, plan = check_user_in_sheet(cleaned_email)
                    st.session_state.pro_expiry = expiry
                    st.session_state.pro_plan_type = plan
                    st.session_state.pro_status_checked = True

                    if is_active:
                        st.session_state.payment_done = True
                        st.session_state.ask_email = False
                        st.rerun()
                    else:
                        st.session_state.ask_email = False
                        save_user_to_sheet(cleaned_email, st.session_state.selected_pro)
                        st.rerun()
                else:
                    st.error("Invalid email string format detected.")
            st.stop()

        if is_subscription_active():
            st.success(f"🔒 Authenticated: {st.session_state.user_email} (PRO Plan Active)")
        elif st.session_state.pro_expiry == 'verification_pending':
            st.warning("⏳ Verification Protocol Initialized. Please stand by for admin verification (5 mins).")
            if st.button("🔄 Check Authorization Logs", use_container_width=True):
                st.session_state.pro_status_checked = False
                st.rerun()
            st.stop()
        else:
            st.error("⚠️ Plan Inactive / Awaiting Ledger Verification.")

    uploaded_file = st.file_uploader("Drop document format data matrix (CSV, XLSX, JSON)", type=["csv", "xlsx", "xls", "json"])

    df = None
    if uploaded_file:
        wait_time = 3 if is_pro_user else 15
        with st.spinner(f"🧬 Parsing matrix streams... ({wait_time}s)"):
            time.sleep(wait_time)
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'): df = pd.read_json(uploaded_file)
        except Exception as e:
            st.error(f"Matrix read failure: {e}")
            st.stop()

    if df is not None:
        orig_len = len(df)
        
        # Free account automatically cuts off at 1000 rows
        if not is_pro_user and orig_len > 1000:
            df = df.head(1000)
            st.warning("⚠️ FREE Tier Limit Active: Processing only first 1000 rows.")
        
        # Auto-clean duplicates and spaces for both
        df_cleaned = df.drop_duplicates()
        for col in df_cleaned.select_dtypes(include=['object']):
            df_cleaned[col] = df_cleaned[col].apply(text_to_number)
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip() # Whitespace Trimmer (FREE/PRO)

        dups_removed = orig_len - len(df_cleaned)
        
        # ================= 📊 LIVE DATA ANALYTICS DASHBOARD =================
        st.markdown("### 📊 Live Diagnostic Analytics")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Total Loaded Rows</span><br><b style='font-size:24px;color:#1e293b;'>{orig_len}</b></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Clean Extracted Rows</span><br><b style='font-size:24px;color:#10b981;'>{len(df_cleaned)}</b></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Auto-Removed Duplicates</span><br><b style='font-size:24px;color:#ef4444;'>{dups_removed}</b></div>", unsafe_allow_html=True)
        with c4:
            missing_cells = df_cleaned.isna().sum().sum()
            st.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Empty Matrix Cells</span><br><b style='font-size:24px;color:#f59e0b;'>{missing_cells}</b></div>", unsafe_allow_html=True)

        # Smart Auto-Detection Mapping
        all_cols = df_cleaned.columns.tolist()
        detected_emails = [c for c in all_cols if 'email' in c.lower() or 'mail' in c.lower()]
        detected_phones = [c for c in all_cols if 'phone' in c.lower() or 'mobile' in c.lower() or 'contact' in c.lower()]
        detected_dates = [c for c in all_cols if 'date' in c.lower() or 'time' in c.lower()]

        st.markdown("---")
        st.subheader("🔧 System Utility Toolkit")
        
        # Split into tabs where certain operations check for active PRO subscription
        tab1, tab2, tab3 = st.tabs(["📅 Formats & Math", "📧 Communications Array", "🎯 Advanced String Parsers"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**1. Intelligent Date Normalizer (PRO)**")
                if is_pro_user:
                    date_cols = st.multiselect("Select Target Columns", all_cols, default=detected_dates, key="date_cols")
                    if date_cols:
                        for col in date_cols:
                            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                        st.success("Target structures normalized to YYYY-MM-DD")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to automate mixed Date Formats.</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**2. Matrix Empty-Cell Filler (PRO)**")
                if is_pro_user:
                    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
                    if numeric_cols:
                        fill_method = st.selectbox("Imputation Variable Structure:", ["None", "Mean", "Median", "Zero"], key="fill_method")
                        if fill_method != "None":
                            if fill_method == "Mean": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
                            elif fill_method == "Median": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].median())
                            elif fill_method == "Zero": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(0)
                            st.success("Matrix cell imputation complete.")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to autofill missing/empty boxes with Mean/Median values.</div>", unsafe_allow_html=True)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**3. Email Format Engine (PRO)**")
                if is_pro_user:
                    email_cols = st.multiselect("Target Email Tracks", all_cols, default=detected_emails, key="email_cols")
                    if email_cols:
                        for col in email_cols:
                            df_cleaned[f'{col}_valid_log'] = df_cleaned[col].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)
                        st.success("Regular expression string analysis applied.")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to flag invalid email addresses instantly.</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**4. ISO Mobile Vector Normalizer (PRO)**")
                if is_pro_user:
                    phone_cols = st.multiselect("Target Mobile Vectors", all_cols, default=detected_phones, key="phone_cols")
                    if phone_cols:
                        for col in phone_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'\D', '', regex=True)
                        st.success("Stripped non-integer structures from phone blocks.")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to fix messy phone number styling.</div>", unsafe_allow_html=True)

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**5. Case Array Standardizer (FREE / PRO)**")
                # Available to everyone!
                text_cols = st.multiselect("Target Strings", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="text_cols")
                case_option = st.selectbox("Apply Case Standard:", ["None", "UPPER", "lower"], key="case_opt")
                if text_cols and case_option != "None":
                    for col in text_cols:
                        if case_option == "UPPER": df_cleaned[col] = df_cleaned[col].str.upper()
                        elif case_option == "lower": df_cleaned[col] = df_cleaned[col].str.lower()
                    st.success("Case transformations committed.")
            with col2:
                st.markdown("**6. Special Character Purge (PRO)**")
                if is_pro_user:
                    special_cols = st.multiselect("Target Matrix Blocks", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="special_cols")
                    if special_cols:
                        for col in special_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'[^\w\s]', '', regex=True)
                        st.success("Cleaned high-ascii symbols.")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to strip emojis, hashes, and broken symbols.</div>", unsafe_allow_html=True)

        st.markdown("**7. Realtime Hot-Swap Renamer (PRO)**")
        if is_pro_user:
            rename_col = st.selectbox("Target Node:", ["None"] + all_cols, key="rename_col")
            if rename_col != "None":
                new_name = st.text_input(f"Replace label '{rename_col}' with:")
                if st.button("Execute Label Swap"):
                    df_cleaned = df_cleaned.rename(columns={rename_col: new_name})
                    st.success("Column signature updated.")
                    st.rerun()
        else:
            st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to instantly swap column headers.</div>", unsafe_allow_html=True)

        st.markdown("---")
        df_display = df_cleaned.fillna('').astype(str).replace(['nan', 'NaN', 'None'], '', regex=False)
        st.write("**Processed Matrix Stream Output Preview:**")
        st.dataframe(df_display.head(10 if is_pro_user else 5))

        # ================= 📥 SECURE DOWNLOAD GATEWAYS =================
        if st.session_state.plan == 'pro':
            is_active, expiry, plan = check_user_in_sheet(st.session_state.user_email)
            if is_active:
                st.success("⚡ PRO Cloud Data Mainframe Pipe Unlocked")
                ex_buf = BytesIO()
                with pd.ExcelWriter(ex_buf, engine='openpyxl') as w: df_cleaned.to_excel(w, index=False)
                c1, c2 = st.columns(2)
                c1.download_button("📊 Fetch Production Excel (.xlsx)", ex_buf.getvalue(), "verisame_prod.xlsx", use_container_width=True)
                csv_buf = BytesIO()
                df_cleaned.to_csv(csv_buf, index=False)
                c2.download_button("📄 Fetch Standard CSV (.csv)", csv_buf.getvalue(), "verisame_prod.csv", use_container_width=True)
            elif st.session_state.show_qr:
                st.info("Render Gateway Signature Node")
                upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={pro_amount}&cu=INR&tn={st.session_state.user_email}"
                qr = qrcode.QRCode(box_size=5, border=1)
                qr.add_data(upi_link)
                qr.make(fit=True)
                buf = BytesIO()
                qr.make_image().save(buf)
                
                col1, col2 = st.columns([1,2])
                col1.image(buf, width=200)
                col2.markdown(f"**Gateway Asset Node:** `{UPI_ID}`\n\n**Fee Structure:** `₹{pro_amount}`\n\n**Identity Verification Key:** `{st.session_state.user_email}`")
                
                if st.button("Verify Complete Payment Ledger Entry", type="primary", use_container_width=True):
                    update_count("buy")
                    request_payment_verification(st.session_state.user_email)
                    st.session_state.pro_expiry = 'verification_pending'
                    st.session_state.show_qr = False
                    st.rerun()
            else:
                if st.button("💳 Provision Premium Network Node Access", type="primary", use_container_width=True):
                    st.session_state.show_qr = True
                    st.rerun()
        
        # Free Download Block (Only CSV, up to 1000 rows, no excel)
        else:
            csv_buf = BytesIO()
            df_cleaned.to_csv(csv_buf, index=False)
            st.download_button("📥 Extract Free Tier Analytics Matrix (CSV)", csv_buf.getvalue(), "verisame_free.csv", use_container_width=True)
            st.info("💡 Pro Tip: Upgrade to PRO to unlock premium Excel (.xlsx) formats and eliminate the 1,000-row pipeline limitation.")

# FOOTER SYSTEM SIGNALS
st.markdown("---")
st.markdown("<div style='text-align: center; color: #94a3b8; font-size:12px;'>VeriSame Data Matrix Suite v1.5 | Protected Pipeline Architecture © 2026</div>", unsafe_allow_html=True)
