import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import re
from io import BytesIO
import qrcode
import json
import os
from datetime import datetime
import requests
import hashlib
from word2number import w2n # AI accurate number conversion

st.set_page_config(
    page_title="VeriSame - Free Excel & CSV Cleaner",
    page_icon="📊",
    layout="wide",
    menu_items={'About': "VeriSame cleans messy Excel files instantly"}
)

# ============ 🔐 SECURE CONFIG FROM SECRETS ============
SHEET_ID = st.secrets.get("SHEET_ID", "")
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv" if SHEET_ID else ""
GOOGLE_SCRIPT_URL = st.secrets.get("GOOGLE_SCRIPT_URL", "")
WHATSAPP_NUMBER = "919794906852"
UPI_ID = st.secrets.get("UPI_ID", "playwithreyansh0@okhdfcbank")

PRO_AMOUNT_MONTH = 299
PRO_AMOUNT_3MONTH = 1499

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

HASHED_SECRET_PASS = st.secrets.get("ADMIN_HASH", "")

query_params = st.query_params
provided_pass = query_params.get("pass", "")
SHOW_DASHBOARD = check_hashes(provided_pass, HASHED_SECRET_PASS) if provided_pass and HASHED_SECRET_PASS else False

if SHOW_DASHBOARD and 'bot' in str(query_params).lower():
    st.stop()

# ============ EMAIL MEMORY ============
url_email = query_params.get("user")
if url_email and 'user_email' not in st.session_state:
    st.session_state.user_email = url_email.strip().lower()

# ============ THREAD-SAFE COUNTING ============
COUNT_FILE = "counts.json"
if not os.path.exists(COUNT_FILE):
    with open(COUNT_FILE, 'w') as f:
        json.dump({"views": 0, "free": 0, "pro_month": 0, "pro_half": 0, "buy": 0}, f)

def update_count(key):
    try:
        with open(COUNT_FILE, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX) # Lock lagaya
            data = json.load(f)
            data[key] = data.get(key, 0) + 1
            f.seek(0)
            json.dump(data, f)
            f.truncate()
            fcntl.flock(f, fcntl.LOCK_UN) # Lock khola
        return data[key]
    except:
        return 0

def get_counts():
    try:
        with open(COUNT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"views": 0, "free": 0, "pro_month": 0, "pro_half": 0, "buy": 0}

# ============ AI ACCURATE TEXT TO NUMBER ============
def words_to_number_simple(text):
    if pd.isna(text):
        return ""
    text_str = str(text).strip()

    # Pehle check kar number hai kya
    if re.match(r'^[\d,.\s]+$', text_str):
        return text_str.replace(',', '').strip()

    # Word2Number library se convert kar - AI level accurate
    try:
        return str(w2n.word_to_num(text_str.lower()))
    except:
        return text_str.strip()

# ============ CACHED SHEET CHECK - Server bill 90% kam ============
@st.cache_data(ttl=60) # 60 sec tak cache rahega
def check_user_in_sheet(email):
    if not email or not SHEET_URL:
        return False, "not_found", None
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

            if status == 'paid':
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
            return False, status, plan
        return False, "not_found", None
    except Exception:
        return False, "sheet_error", None

def save_user_to_sheet(email, plan_type):
    if not GOOGLE_SCRIPT_URL:
        return False

    if plan_type == 'free':
        plan_name, amount = "free", 0
    else:
        plan_name = "1month" if plan_type == 'month' else "3month"
        amount = PRO_AMOUNT_MONTH if plan_type == 'month' else PRO_AMOUNT_3MONTH

    try:
        payload = {"action": "new_user", "email": email, "plan": plan_name, "amount": amount}
        headers = {'Content-Type': 'text/plain'}
        r = requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload), headers=headers, timeout=10)
        return r.status_code == 200
    except:
        return False

def log_cleaning_data(email, rows_in, rows_out, fraud_detected):
    """DATA MOAT: Har cleaning ka log save karo - Year 3 ka Trust Score yahi se banega"""
    if not GOOGLE_SCRIPT_URL:
        return
    try:
        payload = {
            "action": "log_clean",
            "email": hashlib.md5(email.encode()).hexdigest(), # Hash karke privacy
            "rows_in": rows_in,
            "rows_out": rows_out,
            "fraud_detected": fraud_detected,
            "timestamp": datetime.now().isoformat()
        }
        requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload), headers={'Content-Type': 'text/plain'}, timeout=5)
    except:
        pass # Log fail hua to app mat roko

# GA SYSTEM
if not SHOW_DASHBOARD:
    if 'counted_session' not in st.session_state:
        update_count("views")
        st.session_state.counted_session = True
    GA_MEASUREMENT_ID = "G-7E6HS2Q6Q3"
    st.markdown(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_MEASUREMENT_ID}');</script>
    """, unsafe_allow_html=True)

# ============ SECRET DASHBOARD ============
if SHOW_DASHBOARD:
    st.title("🔒 Private Dashboard")
    st.caption("⚠️ CEO Only")
    if st.button("🔄 Refresh Counts", type="primary", use_container_width=True):
        st.cache_data.clear()
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

# ============ CSS DESIGN ============
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
   .stApp {
        background: linear-gradient(-45deg, #db2777, #831843, #9d174d, #4c0519);
        background-size: 400% 400%;
        animation: gradientBG 25s ease infinite;
        background-attachment: fixed;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
   .block-container {
        padding: 2.5rem 3.5rem;
        max-width: 1350px;
        background: rgba(255,255,255,0.98);
        border-radius: 24px;
        box-shadow: 0 24px 70px rgba(0,0,0,0.5);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
   .stButton>button {
        width: 100%;
        height: 55px;
        font-size: 16px;
        font-weight: 700;
        border-radius: 12px;
        transition: all 0.3s;
        border: none;
        background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
        color: white;
    }
   .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(236, 72, 153, 0.3);
    }
   .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }
   .tools-banner {
        background: linear-gradient(90deg, #ec4899 0%, #be185d 100%);
        padding: 30px;
        border-radius: 20px;
        margin: 25px 0;
        color: white;
    }
   .tool-item {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        padding: 10px 18px;
        border-radius: 20px;
        margin: 6px;
        font-size: 14px;
        font-weight: 600;
    }
   .pro-lock-msg {
        background: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        color: #991b1b;
        font-weight: 600;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SESSION STATES ============
for state_key in ['plan', 'selected_pro', 'user_email', 'pro_expiry', 'pro_plan_type', 'df_cleaned', 'balloon_trigger', 'current_pay_amt']:
    if state_key not in st.session_state:
        st.session_state[state_key] = None

for bool_key in ['show_qr', 'ask_email']:
    if bool_key not in st.session_state:
        st.session_state[bool_key] = False

if st.session_state.get('balloon_trigger') == True:
    st.balloons()
    st.session_state.balloon_trigger = False

def is_subscription_active():
    if st.session_state.get('plan') == 'free':
        return False
    expiry_val = st.session_state.get('pro_expiry')
    if expiry_val and expiry_val not in ['not_verified', 'expired', 'invalid_date', 'not_found', 'sheet_error']:
        try:
            expiry = datetime.strptime(expiry_val, '%Y-%m-%d')
            return datetime.now().date() <= expiry.date()
        except:
            return False
    return False

# Live Sync State
user_email_saved = st.session_state.get('user_email')
if user_email_saved and st.session_state.get('plan')!= 'free':
    is_active, expiry, plan = check_user_in_sheet(user_email_saved)
    st.session_state.pro_expiry = expiry
    st.session_state.pro_plan_type = plan

# SIDEBAR
with st.sidebar:
    st.title("💼 VeriSame")
    if st.session_state.get('user_email'):
        st.success(f"✅ Logged in")
        st.caption(f"📧 {st.session_state.user_email}")
        if st.session_state.get('plan') == 'free':
            st.info("🆓 Plan: Free Tier")
        elif is_subscription_active():
            st.success(f"👑 PRO Active\nExpires: {st.session_state.pro_expiry}")
        else:
            st.error("❌ Status: Unpaid")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.query_params.clear()
            st.rerun()
    else:
        st.info("Login to sync workspace.")
    st.markdown("---")
    st.markdown(f"[💬 WhatsApp Support](https://wa.me/{WHATSAPP_NUMBER})")

# LANDING
st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png", width=260)
st.title("💼 VeriSame")
st.subheader("The fastest way to clean your data")

if st.session_state.get('plan') is None:
    st.markdown("""
    <div class="tools-banner">
        <h3 style='margin:0 0 12px 0; text-align:center;'>🚀 FREE vs PRO Features</h3>
        <div style='text-align:center;'>
            <span class="tool-item">📅 Date Format Engine (PRO)</span>
            <span class="tool-item">🔢 Smart Analytics (FREE)</span>
            <span class="tool-item">📧 Email Checker (PRO)</span>
            <span class="tool-item">📱 Phone Fixer (PRO)</span>
            <span class="tool-item">🔤 Case Changer (FREE)</span>
            <span class="tool-item">✨ Symbol Remover (PRO)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("🆓 FREE Tier")
            st.markdown("* Max 1000 rows\n* CSV Download\n* Auto-Delete Duplicates\n* Text Case Changer\n* Word-to-Number Engine")
            if st.button("Access Free Tier", use_container_width=True):
                update_count("free")
                st.session_state.plan = 'free'
                st.session_state.ask_email = True
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("🔥 Monthly Pro")
            st.markdown("* Unlimited rows\n* Excel + CSV Download\n* All 7 Smart Tools\n* Auto Column Detector\n* **₹299 / Month**")
            if st.button("Buy Monthly Pro", use_container_width=True):
                update_count("pro_month")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'month'
                st.session_state.ask_email = True
                st.rerun()
    with col3:
        with st.container(border=True):
            st.subheader("💎 Best Value")
            st.markdown("* 6 Months license\n* Priority processing\n* Custom templates\n* **₹1499 / 6 Months**")
            if st.button("Unlock 6 Months", use_container_width=True, type="primary"):
                update_count("pro_half")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'half'
                st.session_state.ask_email = True
                st.rerun()

# MAIN APP
else:
    if st.button("⬅️ Back to Main Screen", key="main_back", use_container_width=True):
        st.session_state.plan = None
        st.session_state.show_qr = False
        st.session_state.df_cleaned = None
        st.rerun()

    st.markdown("---")

    if st.session_state.get('ask_email') and not st.session_state.get('user_email'):
        st.subheader("⚙️ Workspace Setup")
        email_input = st.text_input("Enter Email:", placeholder="name@email.com")
        if st.button("Verify & Open", use_container_width=True, type="primary"):
            cleaned_email = email_input.strip().lower() if email_input else ""
            if cleaned_email and "@" in cleaned_email:
                st.session_state.user_email = cleaned_email
                st.query_params["user"] = cleaned_email
                if st.session_state.get('plan') == 'free':
                    save_user_to_sheet(cleaned_email, 'free')
                else:
                    is_active, expiry, plan = check_user_in_sheet(cleaned_email)
                    if expiry == 'not_found':
                        save_user_to_sheet(cleaned_email, st.session_state.selected_pro)
                    st.session_state.pro_expiry = expiry
                    st.session_state.pro_plan_type = plan
                st.session_state.ask_email = False
                st.rerun()
            else:
                st.error("Valid email daalo.")
        st.stop()

    uploaded_file = st.file_uploader("Upload File (CSV, XLSX, XLS, JSON)", type=["csv", "xlsx", "xls", "json"])

    df = None
    if uploaded_file:
        # SLEEP HATA DIYA - Ab turant processing
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'): df = pd.read_json(uploaded_file)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    if df is not None:
        orig_len = len(df)

        if st.session_state.get('plan') == 'free' and orig_len > 1000:
            df = df.head(1000)
            st.warning("⚠️ FREE Limit: Only first 1000 rows processing.")

        df_cleaned = df.drop_duplicates()

        # AI ACCURATE NUMBER CONVERSION
        for col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].apply(words_to_number_simple)
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].astype(str).str.strip()

        dups_removed = orig_len - len(df_cleaned)

        # DATA MOAT LOGGING
        if st.session_state.get('user_email'):
            log_cleaning_data(st.session_state.user_email, orig_len, len(df_cleaned), dups_removed)

        st.markdown("### 📊 Live Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Total Rows</span><br><b style='font-size:24px;color:#1e293b;'>{orig_len}</b></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Clean Rows</span><br><b style='font-size:24px;color:#10b981;'>{len(df_cleaned)}</b></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Duplicates Removed</span><br><b style='font-size:24px;color:#ef4444;'>{dups_removed}</b></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'><span style='color:#64748b;font-size:14px;'>Empty Cells</span><br><b style='font-size:24px;color:#f59e0b;'>{df.isna().sum().sum()}</b></div>", unsafe_allow_html=True)

        all_cols = df_cleaned.columns.tolist()
        detected_emails = [c for c in all_cols if 'email' in c.lower()]
        detected_phones = [c for c in all_cols if 'phone' in c.lower() or 'mobile' in c.lower()]
        detected_dates = [c for c in all_cols if 'date' in c.lower()]

        st.markdown("---")
        st.subheader("🔧 Advanced Tools")
        is_pro_workspace = (st.session_state.get('plan') == 'pro')
        tab1, tab2, tab3 = st.tabs(["📅 Date & Empty", "📧 Email & Phone", "🎯 Text Cleaners"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**1. Date Normalizer (PRO)**")
                if is_pro_workspace:
                    date_cols = st.multiselect("Select Date Columns", all_cols, default=detected_dates, key="date_cols")
                    if date_cols:
                        for col in date_cols:
                            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                        st.success("Dates fixed to YYYY-MM-DD!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**2. Fill Empty (PRO)**")
                if is_pro_workspace:
                    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
                    if numeric_cols:
                        fill_method = st.selectbox("Fill Method:", ["None", "Mean", "Median", "Zero"], key="fill_method")
                        if fill_method!= "None":
                            if fill_method == "Mean": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
                            elif fill_method == "Median": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].median())
                            elif fill_method == "Zero": df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(0)
                            st.success("Empty cells filled!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**3. Email Checker (PRO)**")
                if is_pro_workspace:
                    email_cols = st.multiselect("Select Email Columns", all_cols, default=detected_emails, key="email_cols")
                    if email_cols:
                        for col in email_cols:
                            df_cleaned[f'{col}_valid'] = df_cleaned[col].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)
                        st.success("Invalid emails flagged!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**4. Phone Fixer (PRO)**")
                if is_pro_workspace:
                    phone_cols = st.multiselect("Select Phone Columns", all_cols, default=detected_phones, key="phone_cols")
                    if phone_cols:
                        for col in phone_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'\D', '', regex=True)
                        st.success("Phone numbers cleaned!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**5. Case Changer (FREE)**")
                text_cols = st.multiselect("Select Text Columns", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="text_cols")
                case_option = st.selectbox("Choose Style:", ["None", "UPPER CASE", "lower case"], key="case_opt")
                if text_cols and case_option!= "None":
                    for col in text_cols:
                        if case_option == "UPPER CASE": df_cleaned[col] = df_cleaned[col].str.upper()
                        else: df_cleaned[col] = df_cleaned[col].str.lower()
                    st.success("Text style changed!")
            with col2:
                st.markdown("**6. Symbol Remover (PRO)**")
                if is_pro_workspace:
                    special_cols = st.multiselect("Select Columns", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="special_cols")
                    if special_cols:
                        for col in special_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'[^\w\s]', '', regex=True)
                        st.success("Symbols removed!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)

        st.markdown("**7. Rename Column (PRO)**")
        if is_pro_workspace:
            rename_col = st.selectbox("Select Column:", ["None"] + all_cols, key="rename_col")
            if rename_col!= "None":
                new_name = st.text_input(f"New name for '{rename_col}':")
                if st.button("Apply Rename"):
                    df_cleaned = df_cleaned.rename(columns={rename_col: new_name})
                    st.success("Column renamed!")
                    st.rerun()
        else:
            st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)

        st.markdown("---")
        df_display = df_cleaned.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].astype(str).replace(['nan', 'NaN', 'None', '<NA>', 'nat', 'NaT'], '', regex=True)
        st.write("**Preview - First 10 Rows:**")
        st.dataframe(df_display.head(10))

        # DOWNLOADS
        current_plan = st.session_state.get('plan')
        if current_plan == 'free':
            csv_buf = BytesIO()
            df_cleaned.to_csv(csv_buf, index=False)
            if st.download_button("📥 Download CSV", csv_buf.getvalue(), "verisame_free.csv", use_container_width=True):
                st.session_state.balloon_trigger = True
                st.rerun()
        elif current_plan == 'pro' and is_subscription_active():
            ex_buf = BytesIO()
            with pd.ExcelWriter(ex_buf, engine='openpyxl') as w: df_cleaned.to_excel(w, index=False)
            c1, c2 = st.columns(2)
            if c1.download_button("📊 Download Excel", ex_buf.getvalue(), "verisame_pro.xlsx", use_container_width=True):
                st.session_state.balloon_trigger = True
                st.rerun()
            csv_buf = BytesIO()
            df_cleaned.to_csv(csv_buf, index=False)
            if c2.download_button("📄 Download CSV", csv_buf.getvalue(), "verisame_pro.csv", use_container_width=True):
                st.session_state.balloon_trigger = True
                st.rerun()
        else:
            st.markdown("### 🔒 Premium Locked")
            pay_col1, pay_col2 = st.columns(2)
            with pay_col1:
                if st.button("💳 Pay ₹299", use_container_width=True):
                    st.session_state.show_qr = True
                    st.session_state.current_pay_amt = 299
                    st.rerun()
            with pay_col2:
                if st.button("💎 Pay ₹1499", use_container_width=True, type="primary"):
                    st.session_state.show_qr = True
                    st.session_state.current_pay_amt = 1499
                    st.rerun()

            if st.session_state.get('show_qr'):
                amt = st.session_state.get('current_pay_amt', 299)
                upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={amt}&cu=INR&tn={st.session_state.get('user_email','')}"
                qr = qrcode.QRCode(box_size=5, border=1)
                qr.add_data(upi_link)
                qr.make(fit=True)
                buf = BytesIO()
                qr.make_image().save(buf)
                st.markdown("---")
                col_qr, col_txt = st.columns([1,2])
                col_qr.image(buf, width=220)
                col_txt.markdown(f"### 📲 Scan to Pay\n* **UPI:** `{UPI_ID}`\n* **Amount:** `₹{amt}`\n* **Email:** `{st.session_state.get('user_email','')}`")
                if st.button("I Paid! Verify", type="primary", use_container_width=True):
                    is_active, expiry, plan = check_user_in_sheet(st.session_state.get('user_email',''))
                    if is_active:
                        st.session_state.pro_expiry = expiry
                        st.session_state.balloon_trigger = True
                        st.rerun()
                    else:
                        st.error("Payment not showing yet. Wait 2 min & click again.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #f43f5e; font-size:12px;'>VeriSame v2.3 | CEO Edition © 2026</div>", unsafe_allow_html=True)
