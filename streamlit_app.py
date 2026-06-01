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

# ============ CONFIG - DIRECT, NO SECRETS ============
SHEET_ID = "1qwXIK_CLS32Rt4g21QeMs_fmVXK66Mxl0Z7IHBCU8nQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxtz-CV6D5lTUWCb12newzOqSRg0I-INIKXZETmR7MtxHWjQfIIbYHoaAiatZz_13w/exec"
WHATSAPP_NUMBER = "919794906852"

# ============ UPI CONFIG ============
UPI_ID = "playwithreyansh0@okhdfcbank"
PRO_AMOUNT_MONTH = 299
PRO_AMOUNT_3MONTH = 1499
WAIT_SECONDS = 25

# ============ BASIC SECURITY - DIRECT PASS ============
SECRET_PASS = "reyansh999VeriSame2026CEO"
query_params = st.query_params
SHOW_DASHBOARD = query_params.get("pass") == SECRET_PASS

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
    with open(COUNT_FILE, 'r+') as f:
        data = json.load(f)
        data[key] = data.get(key, 0) + 1
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    return data[key]

def get_counts():
    with open(COUNT_FILE, 'r') as f:
        return json.load(f)

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

            if status == 'verification_pending':
                return False, "verification_pending", plan
            if status == 'rejected':
                return False, "rejected", plan
            if status!= 'paid':
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
        payload = {
            "action": "new_user",
            "email": email,
            "plan": plan_name,
            "amount": amount
        }
        headers = {'Content-Type': 'text/plain'}
        r = requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload), headers=headers, timeout=10)
        if r.status_code == 200 and "success" in r.text.lower():
            return True
        else:
            st.error(f"Sheet Error: {r.text}")
            return False
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False

# ============ GA + VIEWS COUNT ============
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
        st.caption("💡 IMPORTANT: Delete old duplicate rows. Keep only latest.")
    except:
        st.info("Google Sheet not connected.")
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
if 'show_pay_button' not in st.session_state: st.session_state.show_pay_button = False
if 'df_cleaned' not in st.session_state: st.session_state.df_cleaned = None
if 'pro_status_checked' not in st.session_state: st.session_state.pro_status_checked = False
if 'payment_log_done' not in st.session_state: st.session_state.payment_log_done = False

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
        st.caption(f"📧 Email: {st.session_state.user_email}")

        if is_subscription_active():
            st.caption(f"PRO till: {st.session_state.pro_expiry}")
            plan_text = "1 Month" if st.session_state.pro_plan_type == '1month' else "6 Months"
            st.caption(f"Plan: {plan_text}")
        elif st.session_state.pro_expiry == 'verification_pending':
            st.warning("⏳ Verification Pending")
            st.caption("Admin will activate in 5-10 min")
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.session_state.pro_status_checked = False
                st.rerun()
        elif st.session_state.pro_expiry == 'rejected':
            st.error("❌ Payment Not Found")
        else:
            st.info("PRO inactive - Complete payment")

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
        st.info("Login to get PRO access")

    st.markdown("---")
    st.markdown("### 📞 Need Help?")
    st.markdown(f"[💬 WhatsApp Support](https://wa.me/{WHATSAPP_NUMBER})")

# MAIN APP
st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png", width=260)
st.title("💼 VeriSame")
st.subheader("The fastest way to clean your data")

if st.session_state.plan is None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🆓 FREE Tier")
        st.write("Max 1000 rows limit")
        st.write("CSV Download only")
        if st.button("Access Free Tier", use_container_width=True):
            update_count("free")
            st.session_state.plan = 'free'
            st.session_state.ask_email = True
            st.rerun()
    with col2:
        st.subheader("🔥 Monthly Pro")
        st.write("Unlimited rows")
        st.write("Excel + CSV Download")
        st.write("₹299 / Month")
        if st.button("Buy Monthly Pro", use_container_width=True):
            update_count("pro_month")
            st.session_state.plan = 'pro'
            st.session_state.selected_pro = 'month'
            st.session_state.ask_email = True
            st.rerun()
    with col3:
        st.subheader("💎 Best Value")
        st.write("6 Months license")
        st.write("All Smart Tools")
        st.write("₹1499 / 6 Months")
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

    if st.session_state.ask_email and not st.session_state.user_email:
        st.subheader("⚙️ Enter Your Email")
        email_input = st.text_input("Email:", placeholder="name@email.com")
        if st.button("Verify & Continue", type="primary", use_container_width=True):
            if email_input and "@" in email_input:
                st.session_state.user_email = email_input.strip().lower()
                st.query_params["user"] = st.session_state.user_email

                if st.session_state.plan == 'free':
                    save_user_to_sheet(st.session_state.user_email, 'free')
                else:
                    save_user_to_sheet(st.session_state.user_email, st.session_state.selected_pro)

                st.session_state.ask_email = False
                st.success("Email saved! Upload file now.")
                st.rerun()
            else:
                st.error("Valid email daalo")
        st.stop()

    uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx", "xls"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.success(f"File loaded: {len(df)} rows")
        st.dataframe(df.head(10))

        csv_buf = BytesIO()
        df.to_csv(csv_buf, index=False)
        st.download_button("📥 Download CSV", csv_buf.getvalue(), "cleaned.csv")

# FOOTER
st.markdown("---")
st.markdown("<div style='text-align: center; color: #667eea;'>VeriSame v2.2 © 2026</div>", unsafe_allow_html=True)
