import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import pandas as pd
import time
import numpy as np
import re
from io import BytesIO
import qrcode
import json
import os
from datetime import datetime, timedelta

# ============ FIREBASE CONNECT ============

@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            key = st.secrets["firebase"]["private_key"]
            key = key.replace('\\n', '\n').replace('"', '').strip()

            cred_dict = dict(st.secrets["firebase"])
            cred_dict["private_key"] = key

            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase Error: {e}")
            st.stop()
    return firestore.client()

db = init_firebase()

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

# ============ 🔐 CONFIG ============
WHATSAPP_NUMBER = "919794906852"
UPI_ID = "playwithreyansh0@okhdfcbank"
PRO_AMOUNT_MONTH = 299
PRO_AMOUNT_6MONTH = 1499

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
        "eighty": "80", "ninety": "90", "hundred": "100"
    }

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

# ============ FIRESTORE FUNCTIONS ============
def check_user_in_firestore(email):
    if not email:
        return False, "not_found", None
    try:
        doc_ref = db.collection("users").document(email.lower().strip())
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            status = str(data.get('status', '')).strip().lower()
            expiry_str = str(data.get('expiry_date', ''))
            plan = str(data.get('plan', ''))
            if status == 'paid':
                try:
                    expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
                    if datetime.now().date() <= expiry_date.date():
                        return True, expiry_str, plan
                    else:
                        return False, "expired", plan
                except:
                    return False, "invalid_date", plan
            return False, status, plan
        return False, "not_found", None
    except Exception:
        return False, "firestore_error", None

def save_user_to_firestore(email, plan_type):
    if plan_type == 'free':
        plan_name = "free"
        amount = 0
        days = 0
    else:
        plan_name = "1month" if plan_type == 'month' else "6month"
        amount = PRO_AMOUNT_MONTH if plan_type == 'month' else PRO_AMOUNT_6MONTH
        days = 30 if plan_type == 'month' else 180

    expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    try:
        doc_ref = db.collection("users").document(email.lower().strip())
        doc_ref.set({
            "email": email.lower().strip(),
            "plan": plan_name,
            "amount": amount,
            "status": "paid" if plan_type!= 'free' else "free",
            "expiry_date": expiry_date,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        st.error(f"Firestore Error: {e}")
        return False

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
        users_ref = db.collection("users").stream()
        users_list = [doc.to_dict() for doc in users_ref]
        if users_list:
            df_users = pd.DataFrame(users_list)
            st.dataframe(df_users, use_container_width=True)

            # ============ PAID BUTTON ADD KIYA ============
            st.subheader("🔥 Payment Verify Karo")
            for user in users_list:
                if user.get('status') == 'pending':
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.write(f"📧 {user['email']} | Plan: {user['plan']} | ₹{user['amount']}")
                    with col2:
                        if st.button(f"Paid Karo", key=user['email']):
                            db.collection("users").document(user['email']).update({
                                "status": "paid",
                                "expiry_date": (datetime.now() + timedelta(days=30 if user['plan']=='1month' else 180)).strftime('%Y-%m-%d')
                            })
                            st.success(f"{user['email']} verified!")
                            st.rerun()
        else:
            st.info("Abhi koi user register nahi hua")
    except:
        st.error("Firestore connect nahi ho pa raha")
    st.stop()

# ============ CSS DESIGN ============
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
        transition: all 0.3s ease;
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
for state_key in ['plan', 'selected_pro', 'user_email', 'pro_expiry', 'pro_plan_type', 'df_cleaned', 'balloon_trigger', 'current_pay_amt', 'show_qr']:
    if state_key not in st.session_state:
        st.session_state[state_key] = None

for bool_key in ['ask_email']:
    if bool_key not in st.session_state:
        st.session_state[bool_key] = False

if st.session_state.get('balloon_trigger') == True:
    st.balloons()
    st.session_state.balloon_trigger = False

def is_subscription_active():
    if st.session_state.get('plan') == 'free':
        return False
    expiry_val = st.session_state.get('pro_expiry')
    if expiry_val and expiry_val not in ['not_verified', 'expired', 'invalid_date', 'not_found', 'firestore_error', 'verification_pending', 'rejected']:
        try:
            expiry = datetime.strptime(expiry_val, '%Y-%m-%d')
            return datetime.now().date() <= expiry.date()
        except:
            return False
    return False

user_email_saved = st.session_state.get('user_email')
current_plan_saved = st.session_state.get('plan')

if user_email_saved and current_plan_saved!= 'free':
    is_active, expiry, plan = check_user_in_firestore(user_email_saved)
    st.session_state.pro_expiry = expiry
    st.session_state.pro_plan_type = plan

# SIDEBAR STATUS
with st.sidebar:
    st.title("💼 VeriSame")
    if st.session_state.get('user_email'):
        st.success(f"✅ Logged in")
        st.caption(f"📧 {st.session_state.user_email}")
        if st.session_state.get('plan') == 'free':
            st.info("🆓 Plan: Free Tier")
        elif is_subscription_active():
            st.success(f"👑 PRO Status: Active\n(Expires: {st.session_state.pro_expiry})")
        elif st.session_state.get('pro_expiry') == 'verification_pending':
            st.warning("⏳ Status: Verification Pending")
        else:
            st.error("❌ Status: Testing Mode (Unpaid)")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.query_params.clear()
            st.rerun()
    else:
        st.info("Login to sync workspace environments.")
    st.markdown("---")
    st.markdown(f"[💬 WhatsApp Support](https://wa.me/{WHATSAPP_NUMBER})")

# LANDING GRAPHICS
st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png", width=260)
st.title("💼 VeriSame")
st.subheader("The fastest way to clean your data")

if st.session_state.get('plan') is None:
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
            st.markdown("""
            * Max 1000 rows limit
            * CSV File Download only
            * Auto-Delete Duplicates
            * Text Case Changer
            * Extra Space Cleaner
            * Auto Word-to-Number Engine
            * 3 Seconds instant processing wait
            """)
            if st.button("Access Free Tier", use_container_width=True):
                update_count("free")
                st.session_state.plan = 'free'
                st.session_state.ask_email = True
                st.balloons() # FREE me balloon
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("🔥 Monthly Pro")
            st.markdown("""
            * Unlimited rows & size
            * Download Excel + CSV formats
            * Access all 7 Smart Tools
            * Automatic Column Detector
            * Super fast 3s processing
            * **₹299 / Month**
            """)
            if st.button("Buy Monthly Pro", use_container_width=True):
                update_count("pro_month")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'month'
                st.session_state.current_pay_amt = PRO_AMOUNT_MONTH
                st.session_state.show_qr = True
                st.session_state.ask_email = True
                st.rerun()
    with col3:
        with st.container(border=True):
            st.subheader("💎 Best Value")
            st.markdown("""
            * 6 Months complete license
            * Access all 7 Smart Tools
            * Priority processing queue
            * Custom template memory
            * Super fast 3s processing
            * **₹1499 / 6 Months**
            """)
            if st.button("Unlock 6 Months", use_container_width=True, type="primary"):
                update_count("pro_half")
                st.session_state.plan = 'pro'
                st.session_state.selected_pro = 'half'
                st.session_state.current_pay_amt = PRO_AMOUNT_6MONTH
                st.session_state.show_qr = True
                st.session_state.ask_email = True
                st.rerun()

# REALTIME PIPELINE CONTROLLER
else:
    if st.button("⬅️ Back to Main Screen", key="main_back", use_container_width=True):
        st.session_state.plan = None
        st.session_state.show_qr = False
        st.session_state.df_cleaned = None
        st.rerun()

    st.markdown("---")

    if st.session_state.get('ask_email') and not st.session_state.get('user_email'):
        st.subheader("⚙️ Workspace Environment Setup")
        email_input = st.text_input("Enter Your Account Email Id To Continue:", placeholder="name@email.com")
        if st.button("Verify & Open Workspace", use_container_width=True, type="primary"):
            cleaned_email = email_input.strip().lower() if email_input else ""
            if cleaned_email and "@" in cleaned_email and "." in cleaned_email:
                st.session_state.user_email = cleaned_email
                st.query_params["user"] = cleaned_email
                save_user_to_firestore(cleaned_email, st.session_state.get('plan', 'free'))
                is_active, expiry, plan = check_user_in_firestore(cleaned_email)
                st.session_state.pro_expiry = expiry
                st.session_state.pro_plan_type = plan
                st.session_state.ask_email = False
                st.rerun()
            else:
                st.error("Please insert a valid email address.")
        st.stop()

    uploaded_file = st.file_uploader("Upload Your File Here (CSV, XLSX, XLS, JSON)", type=["csv", "xlsx", "xls", "json"])

    df = None
    if uploaded_file:
        with st.spinner("🧬 Synchronizing clean rows database engine... Please wait (3s)"):
            time.sleep(3)
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'): df = pd.read_json(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()

    if df is not None:
        orig_len = len(df)

        if st.session_state.get('plan') == 'free' and orig_len > 1000:
            df = df.head(1000)
            st.warning("⚠️ FREE Tier Limit Active: Processing only the first 1000 rows.")

        df_cleaned = df.drop_duplicates()

        for col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].apply(words_to_number_simple)
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].astype(str).str.strip()

        dups_removed = orig_len - len(df_cleaned)

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

        is_pro_workspace = (st.session_state.get('plan') == 'pro')
        tab1, tab2, tab3 = st.tabs(["📅 Date & Empty Boxes", "📧 Email & Phone", "🎯 Advanced Text Cleaners"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**1. Auto Date Normalizer (PRO)**")
                if is_pro_workspace:
                    date_cols = st.multiselect("Select Date Columns", all_cols, default=detected_dates, key="date_cols")
                    if date_cols:
                        for col in date_cols:
                            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                        st.success("Dates fixed to standard YYYY-MM-DD format!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature - Upgrade karo</div>", unsafe_allow_html=True)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**2. Email Format Checker (PRO)**")
                if is_pro_workspace:
                    email_cols = st.multiselect("Select Email Columns", all_cols, default=detected_emails, key="email_cols")
                    if email_cols:
                        for col in email_cols:
                            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                            df_cleaned[col] = df_cleaned[col].apply(lambda x: x if re.match(pattern, str(x)) else "")
                        st.success("Invalid emails removed!")
                else:
                    st.markdown("<div class='pro-lock-msg'>🔒 PRO Feature - Upgrade karo</div>", unsafe_allow_html=True)

        with tab3:
            st.markdown("**3. Capital/Small Letters (FREE)**")
            case_option = st.selectbox("Select Case", ["Uppercase", "Lowercase", "Title Case"])
            case_cols = st.multiselect("Select Columns", all_cols, key="case_cols")
            if st.button("Apply Case Change"):
                for col in case_cols:
                    if case_option == "Uppercase":
                        df_cleaned[col] = df_cleaned[col].str.upper()
                    elif case_option == "Lowercase":
                        df_cleaned[col] = df_cleaned[col].str.lower()
                    else:
                        df_cleaned[col] = df_cleaned[col].str.title()
                st.success("Case changed!")

        st.markdown("---")
        st.subheader("📥 Download Cleaned File")

        # ============ PAYMENT LOCK LAGAYA ============
        is_paid, expiry, plan = check_user_in_firestore(st.session_state.get('user_email'))

        if st.session_state.get('plan') == 'free':
            csv = df_cleaned.to_csv(index=False).encode('utf-8')
            if st.download_button("Download CSV", csv, "cleaned_data.csv", "text/csv"):
                st.balloons()

        elif is_paid:
            col1, col2 = st.columns(2)
            with col1:
                csv = df_cleaned.to_csv(index=False).encode('utf-8')
                if st.download_button("Download CSV", csv, "cleaned_data.csv", "text/csv"):
                    st.balloons()
            with col2:
                output = BytesIO()
                df_cleaned.to_excel(output, index=False)
                if st.download_button("Download Excel", output.getvalue(), "cleaned_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
                    st.balloons()
        else:
            st.error("🔒 Pehle payment complete karo")
            amt = st.session_state.get('current_pay_amt', 299)
            if st.button(f"Pay ₹{amt} Now"):
                st.session_state.show_qr = True
                st.rerun()

        # ============ QR CODE POPUP ============
        if st.session_state.get('show_qr') and st.session_state.get('user_email'):
            st.markdown("---")
            st.subheader("💳 UPI se Payment Karo")
            amt = st.session_state.get('current_pay_amt', 299)
            st.warning(f"₹{amt} Pay karo. Payment ke baad 'I Paid' dabana")

            upi_link = f"upi://pay?pa={UPI_ID}&am={amt}&cu=INR&tn=VeriSame Pro"
            qr_img = qrcode.make(upi_link)
            st.image(qr_img, width=250)
            st.code(UPI_ID)

            if st.button("I Paid ✅"):
                doc_ref = db.collection("users").document(st.session_state.user_email)
                doc_ref.set({
                    "email": st.session_state.user_email,
                    "plan": st.session_state.selected_pro,
                    "amount": amt,
                    "status": "pending",
                    "timestamp": str(datetime.now())
                }, merge=True)
                st.success("Payment request bheja gaya! Ab main verify karke unlock karungi. 5 min ruk 🕐")
                st.session_state.show_qr = False
                st.rerun()

        st.session_state.df_cleaned = df_cleaned
