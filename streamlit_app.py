import streamlit as st
from pathlib import Path
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

# ============ CONFIG - DIRECT LIKHA HAI ============
SHEET_ID = "1qwXIK_CLS32Rt4g21QeMs_fmVXK66Mxl0Z7IHBCU8nQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxtz-CV6D5lTUWCb12newzOqSRg0I-INIKXZETmR7MtxHWjQfIIbYHoaAiatZz_13w/exec"
WHATSAPP_NUMBER = "919794906852"

# ============ UPI CONFIG ============
UPI_ID = "playwithreyansh0@okhdfcbank"
PRO_AMOUNT_MONTH = 299
PRO_AMOUNT_3MONTH = 1499
WAIT_SECONDS = 25

# ============ BASIC SECURITY ============
SECRET_PASS = "reyansh999VeriSame2026CEO"
query_params = st.query_params
SHOW_DASHBOARD = query_params.get("pass") == SECRET_PASS

if SHOW_DASHBOARD and 'bot' in str(query_params).lower():
    st.stop()

# ============ EMAIL MEMORY ============
url_email = query_params.get("user")
if url_email and 'user_email' not in st.session_state:
    st.session_state.user_email = url_email.strip().lower()

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
    num_dict = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
        "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14", "fifteen": "15",
        "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19", "twenty": "20",
        "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
        "eighty": "80", "ninety": "90"
    }
    text_str = text_str.replace("-", " ")
    parts = text_str.split()
    if len(parts) == 2 and parts[0] in num_dict and parts[1] in num_dict:
        val1 = int(num_dict[parts[0]])
        val2 = int(num_dict[parts[1]])
        if "twenty" in parts[0] or "thirty" in parts[0]:
            return str(val1 + val2)
    if text_str in num_dict:
        return num_dict[text_str]
    if re.match(r'^[\d,.\s]+$', text_str):
        return text_str.replace(',', '').strip()
    return str(text).strip()

# ============ SUBSCRIPTION FUNCTIONS ============
@st.cache_data(ttl=10)
def check_user_in_sheet(email):
    if not email: return False, "not_found", None
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
                for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']:
                    try:
                        expiry_date = datetime.strptime(expiry_str, fmt)
                        if datetime.now().date() <= expiry_date.date():
                            return True, expiry_date.strftime('%Y-%m-%d'), plan
                        else:
                            return False, "expired", plan
                    except:
                        continue
            return False, status, plan
        return False, "not_found", None
    except:
        return False, "sheet_error", None

def save_user_to_sheet(email, plan_type):
    if plan_type == 'free':
        plan_name = "free"
        amount = 0
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

# GA SYSTEM
if not SHOW_DASHBOARD:
    if 'counted_session' not in st.session_state:
        update_count("views")
        st.session_state.counted_session = True
    GA_MEASUREMENT_ID = "G-7E6HS2Q6Q3"
    st.markdown(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>window.dataLayer = window.dataLayer || [];function gtag(){{dataLayer.push(arguments);}}gtag('js', new Date());gtag('config', '{GA_MEASUREMENT_ID}');</script>
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
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
 .stApp {
        background: linear-gradient(-45deg, #db2777, #831843, #9d174d, #4c0519);
        background-size: 400% 400%; animation: gradientBG 25s ease infinite; background-attachment: fixed;
    }
    @keyframes gradientBG {0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; }}
 .block-container {
        padding: 2.5rem 3.5rem; max-width: 1350px; background: rgba(255,255,255,0.98);
        border-radius: 24px; box-shadow: 0 24px 70px rgba(0,0,0,0.5); margin-top: 2rem; margin-bottom: 2rem;
    }
 .stButton>button {
        width: 100%; height: 55px; font-size: 16px; font-weight: 700; border-radius: 12px;
        transition: all 0.3s ease; border: none; background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%); color: white;
    }
 .pro-lock-msg {
        background: #fef2f2; border-left: 5px solid #ef4444; padding: 15px; border-radius: 8px;
        color: #991b1b; font-weight: 600; margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SESSION STATES ============
for state_key in ['plan', 'selected_pro', 'user_email', 'pro_expiry', 'pro_plan_type', 'df_cleaned', 'balloon_trigger', 'current_pay_amt', 'show_qr']:
    if state_key not in st.session_state:
        st.session_state[state_key] = None if state_key not in ['show_qr'] else False
if 'ask_email' not in st.session_state: st.session_state.ask_email = False

if st.session_state.get('balloon_trigger') == True:
    st.balloons()
    st.session_state.balloon_trigger = False

def is_subscription_active():
    if st.session_state.get('plan') == 'free': return False
    expiry_val = st.session_state.get('pro_expiry')
    if expiry_val and expiry_val not in ['not_verified', 'expired', 'invalid_date', 'not_found', 'sheet_error']:
        try:
            expiry = datetime.strptime(expiry_val, '%Y-%m-%d')
            return datetime.now().date() <= expiry.date()
        except:
            return False
    return False

# SIDEBAR
with st.sidebar:
    st.title("💼 VeriSame")
    if st.session_state.get('user_email'):
        st.success(f"✅ Logged in")
        st.caption(f"📧 {st.session_state.user_email}")
        if st.session_state.get('plan') == 'free':
            st.info("🆓 Plan: Free Tier")
        elif is_subscription_active():
            st.success(f"👑 PRO Active\n(Expires: {st.session_state.pro_expiry})")
        else:
            st.error("❌ Status: Testing Mode")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.query_params.clear()
            st.rerun()
    else:
        st.info("Login to sync workspace")
    st.markdown("---")
    st.markdown(f"[💬 WhatsApp Support](https://wa.me/{WHATSAPP_NUMBER})")

# MAIN APP
st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png", width=260)
st.title("💼 VeriSame")
st.subheader("The fastest way to clean your data")

if st.session_state.get('plan') is None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🆓 FREE Tier")
        st.markdown("Max 1000 rows\nCSV Download\nAuto-Delete Duplicates\nText Case Changer")
        if st.button("Access Free Tier", use_container_width=True):
            update_count("free")
            st.session_state.plan = 'free'
            st.session_state.ask_email = True
            st.rerun()
    with col2:
        st.subheader("🔥 Monthly Pro ₹299")
        st.markdown("Unlimited rows\nExcel + CSV\nAll 7 Smart Tools\nFast processing")
        if st.button("Buy Monthly Pro", use_container_width=True):
            update_count("pro_month")
            st.session_state.plan = 'pro'
            st.session_state.selected_pro = 'month'
            st.session_state.ask_email = True
            st.rerun()
    with col3:
        st.subheader("💎 6 Months ₹1499")
        st.markdown("6 Months license\nAll Tools\nPriority processing")
        if st.button("Unlock 6 Months", use_container_width=True, type="primary"):
            update_count("pro_half")
            st.session_state.plan = 'pro'
            st.session_state.selected_pro = 'half'
            st.session_state.ask_email = True
            st.rerun()

else:
    if st.button("⬅️ Back to Main Screen", use_container_width=True):
        st.session_state.plan = None
        st.session_state.show_qr = False
        st.rerun()

    if st.session_state.get('ask_email') and not st.session_state.get('user_email'):
        st.subheader("⚙️ Enter Email")
        email_input = st.text_input("Email Id:", placeholder="name@email.com")
        if st.button("Verify & Open Workspace", type="primary", use_container_width=True):
            cleaned_email = email_input.strip().lower() if email_input else ""
            if cleaned_email and "@" in cleaned_email:
                st.session_state.user_email = cleaned_email
                st.query_params["user"] = cleaned_email
                if st.session_state.get('plan') == 'free':
                    save_user_to_sheet(cleaned_email, 'free')
                else:
                    save_user_to_sheet(cleaned_email, st.session_state.selected_pro)
                is_active, expiry, plan = check_user_in_sheet(cleaned_email)
                st.session_state.pro_expiry = expiry
                st.session_state.pro_plan_type = plan
                st.session_state.ask_email = False
                st.rerun()
            else:
                st.error("Valid email daalo")
        st.stop()

    uploaded_file = st.file_uploader("Upload Your File (CSV, XLSX, XLS, JSON)", type=["csv", "xlsx", "xls", "json"])
    if uploaded_file:
        with st.spinner("Processing... 3 seconds"):
            time.sleep(3)
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
            else: df = pd.read_json(uploaded_file)
        except:
            st.error("File read error")
            st.stop()

        orig_len = len(df)
        if st.session_state.get('plan') == 'free' and orig_len > 1000:
            df = df.head(1000)
            st.warning("FREE Limit: Only first 1000 rows")

        df_cleaned = df.drop_duplicates()
        for col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].apply(words_to_number_simple)

        st.markdown("### 📊 Live Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Rows", orig_len)
        c2.metric("Clean Rows", len(df_cleaned))
        c3.metric("Duplicates Removed", orig_len - len(df_cleaned))

        all_cols = df_cleaned.columns.tolist()
        is_pro = (st.session_state.get('plan') == 'pro') and is_subscription_active()

        st.markdown("---")
        st.subheader("🔧 7 Smart Tools")

        tab1, tab2, tab3 = st.tabs(["Date & Empty", "Email & Phone", "Text Tools"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**1. Date Normalizer PRO**")
                if is_pro:
                    date_cols = st.multiselect("Select Date Columns", all_cols, key="date_cols")
                    if date_cols:
                        for col in date_cols:
                            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                        st.success("Dates fixed!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**2. Fill Empty Boxes PRO**")
                if is_pro:
                    num_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
                    if num_cols:
                        fill_method = st.selectbox("Fill Method:", ["None", "Mean", "Zero"], key="fill_method")
                        if fill_method!= "None":
                            df_cleaned[num_cols] = df_cleaned[num_cols].fillna(0 if fill_method=="Zero" else df_cleaned[num_cols].mean())
                            st.success("Filled!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**3. Email Checker PRO**")
                if is_pro:
                    email_cols = st.multiselect("Select Email Columns", all_cols, key="email_cols")
                    if email_cols:
                        for col in email_cols:
                            df_cleaned[f'{col}_valid'] = df_cleaned[col].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)
                        st.success("Emails checked!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**4. Phone Fixer PRO**")
                if is_pro:
                    phone_cols = st.multiselect("Select Phone Columns", all_cols, key="phone_cols")
                    if phone_cols:
                        for col in phone_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'\D', '', regex=True)
                        st.success("Phones fixed!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**5. Text Case FREE**")
                text_cols = st.multiselect("Select Text Columns", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="text_cols")
                case_opt = st.selectbox("Style:", ["None", "UPPER", "lower"], key="case_opt")
                if text_cols and case_opt!= "None":
                    for col in text_cols:
                        df_cleaned[col] = df_cleaned[col].str.upper() if case_opt=="UPPER" else df_cleaned[col].str.lower()
                    st.success("Case changed!")
            with col2:
                st.markdown("**6. Symbol Remover PRO**")
                if is_pro:
                    spec_cols = st.multiselect("Clean Columns", df_cleaned.select_dtypes(include=['object']).columns.tolist(), key="spec_cols")
                    if spec_cols:
                        for col in spec_cols:
                            df_cleaned[col] = df_cleaned[col].astype(str).str.replace(r'[^\w\s]', '', regex=True)
                        st.success("Symbols removed!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)

        st.markdown("**7. Rename Column PRO**")
        if is_pro:
            rename_col = st.selectbox("Select Column:", ["None"] + all_cols, key="rename_col")
            new_name = st.text_input("New name:")
            if st.button("Rename"):
                if rename_col!= "None" and new_name:
                    df_cleaned = df_cleaned.rename(columns={rename_col: new_name})
                    st.success("Renamed!")
                    st.rerun()
        else:
            st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.dataframe(df_cleaned.head(10))

        # DOWNLOAD + PAYMENT
        if st.session_state.get('plan') == 'free':
            csv_buf = BytesIO()
            df_cleaned.to_csv(csv_buf, index=False)
            if st.download_button("📥 Download CSV", csv_buf.getvalue(), "verisame_free.csv", use_container_width=True):
                st.session_state.balloon_trigger = True
                st.rerun()
        elif is_pro:
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
                st.image(buf, width=220)
                st.markdown(f"**UPI ID:** `{UPI_ID}` | **Amount:** `₹{amt}`")
                if st.button("I Paid! Verify", type="primary", use_container_width=True):
                    is_active, expiry, plan = check_user_in_sheet(st.session_state.get('user_email',''))
                    if is_active:
                        st.session_state.pro_expiry = expiry
                        st.session_state.balloon_trigger = True
                        st.rerun()
                    else:
                        st.error("Payment pending. Wait 5 min then click again.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #f43f5e;'>VeriSame v2.2 © 2026</div>", unsafe_allow_html=True)
