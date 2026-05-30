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

# ============ TEXT TO NUMBER ENGINE ============
def words_to_number_simple(text):
    if pd.isna(text): return ""
    text_str = str(text).strip().lower()
    
    # Common English words dictionary for numbers
    num_dict = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
        "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14", "fifteen": "15",
        "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19", "twenty": "20",
        "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
        "eighty": "80", "ninety": "90", "hundred": "100"
    }
    
    # Check for compound words like sixty four or sixty-four
    text_str = text_str.replace("-", " ")
    parts = text_str.split()
    
    if len(parts) == 2 and parts[0] in num_dict and parts[1] in num_dict:
        val1 = int(num_dict[parts[0]])
        val2 = int(num_dict[parts[1]])
        if "twenty" in parts[0] or "thirty" in parts[0] or "forty" in parts[0] or "fifty" in parts[0] or "sixty" in parts[0] or "seventy" in parts[0] or "eighty" in parts[0] or "ninety" in parts[0]:
            return str(val1 + val2)
            
    if text_str in num_dict:
        return num_dict[text_str]
        
    if re.match(r'^[\d,.\s]+$', text_str): 
        return text_str.replace(',', '').strip()
        
    return str(text).strip()

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
    st.caption("⚠️ CEO Only")
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
    st.success(f"**Total Revenue: ₹{monthly_revenue + half_revenue}**")
    st.markdown("---")
    try:
        users_df = pd.read_csv(SHEET_URL)
        st.dataframe(users_df, use_container_width=True)
    except:
        st.info("Google Sheet not connected.")
    st.stop()

# ============ CSS DESIGN (PINK PREMIUM THEME) ============
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
   .stApp {{
        background: linear-gradient(-45deg, #db2777, #831843, #9d174d, #4c0519);
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
        background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
        color: white;
    }}
   .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(236, 72, 153, 0.3);
    }}
    .metric-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }}
   .tools-banner {{
        background: linear-gradient(90deg, #ec4899 0%, #be185d 100%);
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
for state_key in ['plan', 'selected_pro', 'user_email', 'pro_expiry', 'pro_plan_type', 'df_cleaned', 'balloon_trigger']:
    if state_key not in st.session_state: st.session_state[state_key] = None

for bool_key in ['show_qr', 'payment_done', 'ask_email', 'show_pay_button', 'pro_status_checked', 'payment_log_done']:
    if bool_key not in st.session_state in st.session_state: st.session_state[bool_key] = False

if 'qr_start_time' not in st.session_state: st.session_state.qr_start_time = None

# Smart Balloons State Checker
if st.session_state.balloon_trigger == True:
    st.balloons()
    st.session_state.balloon_trigger = False

def is_subscription_active():
    if st.session_state.pro_expiry and st.session_state.pro_expiry not in ['not_verified', 'expired', 'invalid_date', 'not_found', 'sheet_error', 'verification_pending', 'rejected']:
        try:
            expiry = datetime.strptime(st.session_state.pro_expiry, '%Y-%m-%d')
            return datetime.now().date() <= expiry.date()
        except:
            return False
    return False

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
st.title("💼 VeriSame")
st.subheader("The fastest way to clean your data")

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
        <h3 style='margin:0 0 12px 0; text-align:center;'>🚀 FREE vs PRO Features List</h3>
        <div style='text-align:center;'>
            <span class="tool-item">📅 Date Format Engine (PRO)</span>
            <span class="tool-item">🔢 Smart Live Analytics (FREE/PRO)</span>
            <span class="tool-item">📧 Email Format Checker (PRO)</span>
            <span class="tool-item">📱 Phone Number Fixer (PRO)</span>
            <span class="tool-item">🔤 Capital/Small Letters (FREE/PRO)</span>
            <span class="tool-item">✨ Bad Symbol Remover (PRO)</span>
            <span class="tool-item">✏️ Change Column Name (PRO)</span>
            <span class="tool-item">🔢 English Words to Numbers Fixer (FREE/PRO)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("🆓 FREE Tier")
            st.markdown("• Max 1000 rows limit\n• CSV File Download only\n• Auto-Delete Duplicates\n• Text Case Changer\n• Extra Space Cleaner\n• **Auto Word-to-Number Engine (e.g. sixty four ➡️ 64)**\n• 15 Seconds processing wait")
            if st.button("Access Free Tier", use_container_width=True):
                update_count("free")
                st.session_state.plan = 'free'
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("🔥 Monthly Pro")
            st.markdown("• Unlimited rows & size\n• Download Excel + CSV formats\n• Access all 7 Smart Tools\n• Automatic Column Detector\n• Super fast processing\n• **₹299 / Month**")
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
            st.markdown("• 6 Months complete license\n• Access all 7 Smart Tools\n• Priority processing queue\n• Custom template memory\n• **₹1499 / 6 Months**")
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

    if st.button("⬅️ Back to Main Screen", key="main_back", use_container_width=True):
        st.session_state.plan = None
        st.session_state.show_qr = False
        st.session_state.qr_start_time = None
        st.session_state.df_cleaned = None
        st.rerun()

    st.markdown("---")

    if st.session_state.plan == 'pro':
        if st.session_state.ask_email and not st.session_state.user_email:
            st.title(f"💎 Identity Setup - {pro_text}")
            email_input = st.text_input("Enter Your Registered Email:", placeholder="name@email.com")
            if st.button("Login & Continue", use_container_width=True, type="primary"):
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
                    st.error("Please enter a valid email format.")
            st.stop()

        if is_subscription_active():
            st.success(f"🔒 Account Active: {st.session_state.user_email} (PRO Plan Unlocked)")
        elif st.session_state.pro_expiry == 'verification_pending':
            st.warning("⏳ Payment verification in progress. Please wait 5 minutes.")
            if st.button("🔄 Check Payment Status Again", use_container_width=True):
                st.session_state.pro_status_checked = False
                st.rerun()
            st.stop()
        else:
            st.error("⚠️ Plan Inactive / Awaiting Verification.")

    uploaded_file = st.file_uploader("Upload Your File Here (CSV, XLSX, XLS, JSON)", type=["csv", "xlsx", "xls", "json"])

    df = None
    if uploaded_file:
        wait_time = 3 if is_pro_user else 15
        with st.spinner(f"🧬 Cleaning and scanning rows... Please wait ({wait_time}s)"):
            time.sleep(wait_time)
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'): df = pd.read_json(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()

    if df is not None:
        orig_len = len(df)
        
        if not is_pro_user and orig_len > 1000:
            df = df.head(1000)
            st.warning("⚠️ FREE Tier Limit Active: Processing only the first 1000 rows.")
        
        df_cleaned = df.drop_duplicates()
        
        # Apply strict cleaning and word-to-number transformation (FREE & PRO)
        for col in df_cleaned.columns:
            # Convert text words like 'sixty four' to real numbers 64
            df_cleaned[col] = df_cleaned[col].apply(words_to_number_simple)
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].astype(str).str.strip()

        dups_removed = orig_len - len(df_cleaned)
        
        # ================= 📊 LIVE DATA ANALYTICS DASHBOARD =================
        st.markdown("### 📊 Live File Summary")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Total Uploaded Rows</span><br><b style='font-size:24px;color:#1e293b;'>{orig_len}</b></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Clean Rows Left</span><br><b style='font-size:24px;color:#10b981;'>{len(df_cleaned)}</b></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Deleted Duplicate Rows</span><br><b style='font-size:24px;color:#ef4444;'>{dups_removed}</b></div>", unsafe_allow_html=True)
        with c4:
            missing_cells = df.isna().sum().sum()
            st.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Empty Boxes Found</span><br><b style='font-size:24px;color:#f59e0b;'>{missing_cells}</b></div>", unsafe_allow_html=True)

        all_cols = df_cleaned.columns.tolist()
        detected_emails = [c for c in all_cols if 'email' in c.lower() or 'mail' in c.lower()]
        detected_phones = [c for c in all_cols if 'phone' in c.lower() or 'mobile' in c.lower() or 'contact' in c.lower()]
        detected_dates = [c for c in all_cols if 'date' in c.lower() or 'time' in c.lower()]

        st.markdown("---")
        st.subheader("🔧 Advanced Tools Menu")
        
        tab1, tab2, tab3 = st.tabs(["📅 Date & Empty Boxes", "📧 Email & Phone", "🎯 Advanced Text Cleaners"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**1. Auto Date Normalizer (PRO)**")
                if is_pro_user:
                    date_cols = st.multiselect("Select Date Columns", all_cols, default=detected_dates, key="date_cols")
                    if date_cols:
                        for col in date_cols:
                            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                        st.success("Dates fixed to standard YYYY-MM-DD format!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to auto-fix messy Date formats.</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**2. Fill Empty Boxes (PRO)**")
                if is_pro_user:
                    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
                    if numeric_cols:
                        fill_method = st.selectbox("Fill Empty Boxes Method:", ["None", "Mean", "Median", "Zero"], key="fill_method")
                        if fill_method != "None":
                            if fill_method == "Mean": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
                            elif fill_method == "Median": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].median())
                            elif fill_method == "Zero": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(0)
                            st.success("Empty boxes filled completely!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to fill empty cells automatically.</div>", unsafe_allow_html=True)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**3. Email Format Checker (PRO)**")
                if is_pro_user:
                    email_cols = st.multiselect("Select Email Columns", all_cols, default=detected_emails, key="email_cols")
                    if email_cols:
                        for col in email_cols:
                            df_cleaned[f'{col}_valid_log'] = df_cleaned[col].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)
                        st.success("Invalid emails flagged successfully!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to detect fake/wrong emails.</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**4. Phone Number Fixer (PRO)**")
                if is_pro_user:
                    phone_cols = st.multiselect("Select Phone Columns", all_cols, default=detected_phones, key="phone_cols")
                    if phone_cols:
                        for col in phone_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'\D', '', regex=True)
                        st.success("Fixed phone numbers formats.")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to clean phone number spacing.</div>", unsafe_allow_html=True)

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**5. Capital/Small Letters (FREE / PRO)**")
                text_cols = st.multiselect("Select Text Columns", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="text_cols")
                case_option = st.selectbox("Choose Style:", ["None", "UPPER CASE", "lower case"], key="case_opt")
                if text_cols and case_option != "None":
                    for col in text_cols:
                        if case_option == "UPPER CASE": df_cleaned[col] = df_cleaned[col].str.upper()
                        elif case_option == "lower case": df_cleaned[col] = df_cleaned[col].str.lower()
                    st.success("Text style transformed!")
            with col2:
                st.markdown("**6. Bad Symbol Remover (PRO)**")
                if is_pro_user:
                    special_cols = st.multiselect("Select Columns to Clean", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="special_cols")
                    if special_cols:
                        for col in special_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'[^\w\s]', '', regex=True)
                        st.success("Emojis and bad symbols removed!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to remove emojis and bad icons.</div>", unsafe_allow_html=True)

        st.markdown("**7. Change Column Name (PRO)**")
        if is_pro_user:
            rename_col = st.selectbox("Select Column to Rename:", ["None"] + all_cols, key="rename_col")
            if rename_col != "None":
                new_name = st.text_input(f"Enter new name for '{rename_col}':")
                if st.button("Apply Name Change"):
                    df_cleaned = df_cleaned.rename(columns={rename_col: new_name})
                    st.success("Column name updated!")
                    st.rerun()
        else:
            st.markdown("<div class='pro-lock-msg'>🔒 Locked Feature: Upgrade to PRO to rename columns instantly.</div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # ================= 🛡️ STRICT ANTI-NAN GRID FIXER =================
        df_display = df_cleaned.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].astype(str).replace(['nan', 'NaN', 'None', '<NA>', 'nat', 'NaT'], '', regex=True)
            
        st.write("**Data Output Preview:**")
        st.dataframe(df_display.head(10 if is_pro_user else 5))

        # ================= 📥 BALLOONS ON DOWNLOAD IMPLEMENTATION =================
        if st.session_state.plan == 'pro':
            is_active, expiry, plan = check_user_in_sheet(st.session_state.user_email)
            if is_active:
                st.success("⚡ PRO Network Access Granted")
                ex_buf = BytesIO()
                with pd.ExcelWriter(ex_buf, engine='openpyxl') as w: df_cleaned.to_excel(w, index=False)
                c1, c2 = st.columns(2)
                
                # Excel Download Button
                if c1.download_button("📊 Download Cleaned Excel (.xlsx)", ex_buf.getvalue(), "verisame_pro.xlsx", use_container_width=True):
                    st.session_state.balloon_trigger = True
                    st.rerun()
                    
                csv_buf = BytesIO()
                df_cleaned.to_csv(csv_buf, index=False)
                # CSV Download Button
                if c2.download_button("📄 Download Cleaned CSV (.csv)", csv_buf.getvalue(), "verisame_pro.csv", use_container_width=True):
                    st.session_state.balloon_trigger = True
                    st.rerun()
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
                col2.markdown(f"**UPI ID:** `{UPI_ID}`\n\n**Price:** `₹{pro_amount}`\n\n**Verification Key:** `{st.session_state.user_email}`")
                
                if st.button("Verify Complete Payment Ledger Entry", type="primary", use_container_width=True):
                    update_count("buy")
                    request_payment_verification(st.session_state.user_email)
                    st.session_state.pro_expiry = 'verification_pending'
                    st.session_state.show_qr = False
                    st.rerun()
            else:
                if st.button("💳 Activate Premium Version", type="primary", use_container_width=True):
                    st.session_state.show_qr = True
                    st.rerun()
        
        else:
            csv_buf = BytesIO()
            df_cleaned.to_csv(csv_buf, index=False)
            if st.download_button("📥 Download Cleaned CSV File", csv_buf.getvalue(), "verisame_free.csv", use_container_width=True):
                st.session_state.balloon_trigger = True
                st.rerun()
            st.info("💡 Upgrade to PRO to download Excel (.xlsx) files and unlock unlimited row uploads.")

# FOOTER SYSTEM SIGNALS
st.markdown("---")
st.markdown("<div style='text-align: center; color: #f43f5e; font-size:12px;'>VeriSame Suite v1.7 | Pink Premium Edition © 2026</div>", unsafe_allow_html=True)
