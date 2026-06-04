import streamlit as st
import json, os, io, qrcode
import pandas as pd
import time, re
from datetime import datetime, timedelta
from PIL import Image

# ============ CONFIG ============
st.set_page_config(page_title="VeriSame Pro", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
ADMIN_PASS = "Sherni@123"
DB_FILE, COUNT_FILE = "orders.json", "counts.json"

for f in [DB_FILE, COUNT_FILE]:
    if not os.path.exists(f):
        json.dump({} if f==DB_FILE else {"views":0,"free":0,"pro":0}, open(f,"w"))

def save_db(d): json.dump(d, open(DB_FILE,"w"), indent=2)
def load_db(): return json.load(open(DB_FILE))
def update_count(k):
    c=json.load(open(COUNT_FILE)); c[k]=c.get(k,0)+1; json.dump(c, open(COUNT_FILE,"w"))

# ============ WORD TO NUMBER ============
def words_to_num(s):
    if pd.isna(s): return s
    s = str(s).lower().strip()
    if s.isdigit(): return int(s)
    num_words = {
        'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,
        'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,
        'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,
        'hundred':100,'thousand':1000,'lakh':100000,'crore':10000000
    }
    total = 0; current = 0
    for word in re.findall(r'\w+', s):
        if word in num_words:
            val = num_words[word]
            if val >= 100:
                current = max(1, current) * val
                if val >= 1000: total += current; current = 0
            else: current += val
    return total + current if total + current > 0 else s

# ============ LANGUAGE ============
LANG = {
    "English": {
        "title": "VeriSame Pro", "tagline": "AI-Powered Data Cleaning in 3 Seconds",
        "pro_banner": "🚀 UNLOCK 7 PREMIUM AI TOOLS",
        "free_title": "FREE FOREVER", "pro1_title": "PRO MONTHLY", "pro6_title": "PRO 6 MONTHS - 50% OFF",
        "free_feat": ["1000 Rows Lifetime", "CSV Export Only", "6 Basic Cleaning Tools", "Words → Numbers Auto", "30s Processing Delay", "Email Support"],
        "pro_feat": ["Unlimited Rows Forever", "CSV + Excel Export", "All 7 Premium AI Tools", "3s Lightning Speed", "Priority Email Support", "No Watermark", "Future Updates Free"],
        "email_label": "Enter your email", "continue_btn": "Continue →",
        "upload_tab": "📤 Upload Your File", "sample_tab": "🧪 Try Demo Data",
        "upload_text": "Drag & Drop CSV, Excel or JSON here",
        "sample_btn": "Load Messy Sample Data",
        "summary_title": "📊 Real-Time Cleaning Summary",
        "rows": "Total Rows", "clean": "Clean Rows", "dups": "Duplicates Removed", "empty": "Empty Cells Fixed",
        "preview": "Live Preview - First 10 Rows",
        "tools_menu": "⚡ Premium Data Cleaning Studio",
        "back_btn": "⬅️ Back to Plans",
        "download_title": "📥 Export Clean Data",
        "paid_msg": "Payment Verification Pending",
        "upi_text": "Scan QR Code to Pay Instantly",
        "paid_btn": "✓ I Have Paid ₹{amount}",
        "success_msg": "Payment request sent! Admin will verify in 2 minutes",
        "locked": "🔒 PRO FEATURE - Upgrade to Unlock",
        "tab1": "📅 Date & Null Handling", "tab2": "📧 Email & Phone Tools", "tab3": "✨ Text AI Tools",
        "tool1": "1. Smart Date Normalizer", "tool2": "2. AI Smart Fill Missing",
        "tool3": "3. Email Validator & Cleaner", "tool4": "4. Phone Number Formatter",
        "tool5": "5. Advanced Case Converter", "tool6": "6. Special Character Remover",
        "tool7": "7. Bulk Column Renamer", "tool8": "8. Words to Numbers AI",
        "select_col": "Select Columns", "select_case": "Choose Case Type",
        "apply_btn": "Apply Tool", "success": "Applied Successfully! ✅",
        "expiry_warn": "⚠️ Your PRO plan expires in {days} days! Renew now to avoid interruption",
        "pro_active": "🔥 PRO Active\n📅 Valid till {date}\n⏰ {days} days left",
        "free_plan": "🆓 FREE Plan\nLifetime free",
        "expired": "⚠️ PRO Expired!\nPlease pay again"
    },
    "Hindi": {
        "title": "VeriSame Pro", "tagline": "AI se Data Saaf Karo Sirf 3 Second me",
        "pro_banner": "🚀 7 PREMIUM AI TOOLS KHOLO",
        "free_title": "FREE HAMESHA", "pro1_title": "PRO MONTHLY", "pro6_title": "PRO 6 MONTH - 50% OFF",
        "free_feat": ["1000 Row Lifetime", "Sirf CSV Export", "6 Basic Saaf Karne Wale Tools", "Shabd → Number Auto", "30 Sec Processing Delay", "Email Support"],
        "pro_feat": ["Unlimited Rows Hamesha", "CSV + Excel Export", "7 Saare Premium AI Tools", "3 Sec Lightning Speed", "Priority Email Support", "No Watermark", "Future Update Free"],
        "email_label": "Email daalo", "continue_btn": "Aage Badho →",
        "upload_tab": "📤 File Upload Karo", "sample_tab": "🧪 Demo Data Try Karo",
        "upload_text": "CSV, Excel ya JSON yahan drag karo",
        "sample_btn": "Ganda Sample Data Load Karo",
        "summary_title": "📊 Live Cleaning Summary",
        "rows": "Total Row", "clean": "Saaf Row", "dups": "Duplicate Hate", "empty": "Khali Cell Thik Hue",
        "preview": "Live Preview - Pehle 10 Row",
        "tools_menu": "⚡ Premium Data Saaf Karne Ka Studio",
        "back_btn": "⬅️ Wapas Plans Pe",
        "download_title": "📥 Saaf Data Download Karo",
        "paid_msg": "Payment Verify Hona Baaki Hai",
        "upi_text": "QR Scan Karke Turant Pay Karo",
        "paid_btn": "✓ Maine Pay Kar Diya ₹{amount}",
        "success_msg": "Request bhej di! Admin 2 min me verify karega",
        "locked": "🔒 PRO FEATURE - Upgrade Karo",
        "tab1": "📅 Date & Khali Box", "tab2": "📧 Email & Phone Tools", "tab3": "✨ Text AI Tools",
        "tool1": "1. Date Format Thik Karo", "tool2": "2. AI se Khali Box Bhardo",
        "tool3": "3. Email Check aur Saaf Karo", "tool4": "4. Phone Number Saaf Karo",
        "tool5": "5. Bade Chote Akshar", "tool6": "6. Bad Symbol Hatao",
        "tool7": "7. Column Naam Bulk Badlo", "tool8": "8. Shabd se Number AI",
        "select_col": "Column Chuno", "select_case": "Case Type Chuno",
        "apply_btn": "Tool Lagao", "success": "Ho Gaya! ✅",
        "expiry_warn": "⚠️ Aapka PRO plan {days} din me khatam ho raha hai! Abhi renew karo",
        "pro_active": "🔥 PRO Active\n📅 {date} tak valid\n⏰ {days} din bache",
        "free_plan": "🆓 FREE Plan\nHamesha ke liye free",
        "expired": "⚠️ PRO Expire ho gaya!\nDobara payment karo"
    }
}

# ============ CSS AURA ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%); background-size: 400% 400%; animation: gradientShift 20s ease infinite;}
@keyframes gradientShift {0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}}
.block-container {background: rgba(255,255,255,0.97); backdrop-filter: blur(20px); border-radius: 32px; padding: 3rem 4rem; box-shadow: 0 30px 90px rgba(0,0,0,0.3);}
h1 {font-weight: 800!important; background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem!important;}
.pro-banner {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 24px; color: white; text-align: center; margin: 30px 0;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.25); padding: 10px 20px; border-radius: 50px; margin: 6px; font-weight: 600;}
.pricing-card {border: 3px solid transparent; border-radius: 24px; padding: 30px; background: white; box-shadow: 0 10px 40px rgba(0,0,0,0.1);}
.pricing-card:hover {transform: translateY(-10px); box-shadow: 0 20px 60px rgba(102,126,234,0.3); border-color: #667eea;}
.metric-card {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 16px; text-align: center;}
.stButton>button {border-radius: 12px; font-weight: 600; transition: all 0.3s; border: none;}
.stButton>button:hover {transform: scale(1.05);}
</style>
""", unsafe_allow_html=True)

# ============ SESSION ============
if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'plan' not in st.session_state: st.session_state.plan = None
if 'email' not in st.session_state: st.session_state.email = ""
if 'df_clean' not in st.session_state: st.session_state.df_clean = None
if 'show_balloon' not in st.session_state: st.session_state.show_balloon = False

# ============ SIDEBAR ============
lang = st.sidebar.selectbox("🌐 Language / भाषा", ["English", "Hindi"], index=0 if st.session_state.lang=="English" else 1, key="lang_select")
st.session_state.lang = lang
T = LANG[st.session_state.lang]

# Email + Expiry sidebar me - EMAIL GAYAB NAHI HOGA
if st.session_state.email:
    user = load_db().get(st.session_state.email,{})
    st.sidebar.success(f"📧 {st.session_state.email}")

    if user.get("plan") == "pro":
        exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days

        if days_left > 0:
            st.sidebar.info(T['pro_active'].format(date=user['expiry'], days=days_left))
            if days_left <= 5:
                st.sidebar.warning(T['expiry_warn'].format(days=days_left))
        else:
            st.sidebar.error(T['expired'])
            st.session_state.plan = None

    elif user.get("plan") == "free":
        st.sidebar.info(T['free_plan'])

    if st.sidebar.button(T['back_btn'], key="btn_back_side"):
        st.session_state.plan = None
        st.session_state.email = ""
        st.session_state.df_clean = None
        st.rerun()

# ============ HEADER ============
col_logo, col_title = st.columns([1,4])
with col_logo: st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png", width=250)
with col_title:
    st.title(T['title'])
    st.markdown(f"### {T['tagline']}")

st.markdown(f"<div class='pro-banner'><h2>{T['pro_banner']}</h2><div><span class='tool-chip'>📅 Smart Date</span><span class='tool-chip'>🤖 AI Fill</span><span class='tool-chip'>📧 Email AI</span><span class='tool-chip'>📱 Phone AI</span><span class='tool-chip'>🔤 Text Case</span><span class='tool-chip'>✨ Clean Symbols</span><span class='tool-chip'>✏️ Bulk Rename</span><span class='tool-chip'>🔢 Words→Number</span></div></div>", unsafe_allow_html=True)

# ============ ADMIN ============
if st.query_params.get("admin") == ADMIN_PASS:
    st.title("🔐 Admin Control Panel")
    data = load_db()
    pending = [e for e,i in data.items() if i["status"]=="PENDING"]
    st.metric("Pending Verifications", len(pending))
    for email,info in data.items():
        if info["status"]=="PENDING":
            c1,c2,c3 = st.columns([3,2,1])
            c1.write(f"📧 **{email}**")
            c2.write(f"Plan: {info['plan'].upper()} | ₹{info['amt']} | Exp: {info['expiry']}")
            if c3.button("✅ Approve", key=f"admin_{email}", type="primary"):
                data[email]["status"]="PAID"; save_db(data); st.rerun()
    st.stop()

# ============ PLAN CARDS ============
if st.session_state.plan is None:
    col1,col2,col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center'>{T['free_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center'>₹0</h1>", unsafe_allow_html=True)
        for f in T['free_feat']: st.write(f"✓ {f}")
        if st.button("Start FREE", key="btn_free", use_container_width=True, type="primary"):
            update_count("free"); st.session_state.plan="free"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<style>div[data-testid='stButton'] button[kind='primary'] {background: red;}</style>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='pricing-card' style='border-color:#667eea'>", unsafe_allow_html=True)
        st.markdown("⭐ MOST POPULAR")
        st.markdown(f"<h2 style='text-align:center'>{T['pro1_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center'>₹{PRO_1M}</h1>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.write(f"✓ {f}")
        if st.button(f"Get PRO Monthly", key="btn_pro1", use_container_width=True, type="primary"):
            update_count("pro"); st.session_state.plan="pro"; st.session_state.amt=PRO_1M; st.session_state.days=30; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center'>{T['pro6_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center'>₹{PRO_6M}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:green'>Save ₹295</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.write(f"✓ {f}")
        if st.button(f"Get PRO 6 Months", key="btn_pro6", use_container_width=True, type="primary"):
            update_count("pro"); st.session_state.plan="pro"; st.session_state.amt=PRO_6M; st.session_state.days=180; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ============ MAIN APP ============
else:
    if not st.session_state.email:
        st.session_state.email = st.text_input(T['email_label']).lower().strip()
        if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
            if "@" in st.session_state.email and "." in st.session_state.email:
                data = load_db()
                if st.session_state.email not in data:
                    expiry = (datetime.now()+timedelta(days=st.session_state.get("days",0))).strftime("%Y-%m-%d")
                    data[st.session_state.email] = {"plan":st.session_state.plan,"status":"PENDING","amt":st.session_state.get("amt",0),"expiry":expiry,"created":str(datetime.now())}
                    save_db(data)
                st.rerun()
            else: st.error("Valid email daalo")
        st.stop()

    tab1,tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    df = None

    with tab1:
        file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"])
        if file:
            with st.spinner("🤖 AI Processing... 3 seconds"):
                time.sleep(3)
                if file.name.endswith(".csv"): df = pd.read_csv(file)
                elif file.name.endswith(("xlsx","xls")): df = pd.read_excel(file)
                else: df = pd.read_json(file)

    with tab2:
        if st.button(T['sample_btn'], key="btn_sample"):
            df = pd.DataFrame({
                "Joining Date": ["12/5/2024", "2024-01-15", "", "15-03-2023"],
                "Full Name": [" RAHUL KUMAR ", "priya sharma", "RAHUL KUMAR", "AMIT SINGH"],
                "Email Address": ["RAHUL@GMAIL.COM", "bad email@", "priya@email.com", ""],
                "Phone No": ["98765-43210", "9123 456 789", "000123", "+91 99887 76655"],
                "Salary": ["one hundred", "250", "thirty five", "two thousand five hundred"]
            })

    if df is not None:
        st.session_state.df_clean = df.copy()
        orig_len = len(df)
        if st.session_state.plan=="free" and orig_len>1000:
            st.session_state.df_clean = st.session_state.df_clean.head(1000)
            st.warning("⚠️ Free: Only first 1000 rows")

        df_clean = st.session_state.df_clean.drop_duplicates()
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)
            if any(k in col.lower() for k in ['salary','amount','price','cost']):
                df_clean[col] = df_clean[col].apply(words_to_num)
        st.session_state.df_clean = df_clean

        st.markdown(f"<h2>{T['summary_title']}</h2>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f"<div class='metric-card'><h3>{orig_len}</h3><p>{T['rows']}</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><h3>{len(df_clean)}</h3><p>{T['clean']}</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><h3>{orig_len-len(df_clean)}</h3><p>{T['dups']}</p></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='metric-card'><h3>{df.isna().sum().sum()}</h3><p>{T['empty']}</p></div>", unsafe_allow_html=True)

        st.dataframe(df_clean.head(10), use_container_width=True, height=350)
        st.caption(T['preview'])

        st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
        all_cols = df_clean.columns.tolist()
        is_pro = st.session_state.plan=="pro" and load_db().get(st.session_state.email,{}).get("status")=="PAID"

        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])

        with tab1:
            st.write(f"**{T['tool1']}**")
            if is_pro:
                date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date")
                if st.button(T['apply_btn'], key="btn_date"):
                    for col in date_cols:
                        st.session_state.df_clean[col] = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                    st.success(T['success']); st.rerun()
            else: st.info(T['locked'])

            st.write(f"**{T['tool2']}**")
            if is_pro:
                fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill")
                if st.button(T['apply_btn'], key="btn_fill"):
                    st.session_state.df_clean[fill_cols] = st.session_state.df_clean[fill_cols].fillna("N/A")
                    st.success(T['success']); st.rerun()
            else: st.info(T['locked'])

        with tab2:
            st.write(f"**{T['tool3']}**")
            if is_pro:
                email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email")
                if st.button(T['apply_btn'], key="btn_email"):
                    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    for col in email_cols:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).lower() if re.match(pattern,str(x)) else "")
                    st.success(T['success']); st.rerun()
            else: st.info(T['locked'])

            st.write(f"**{T['tool4']}**")
            if is_pro:
                phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone")
                if st.button(T['apply_btn'], key="btn_phone"):
                    for col in phone_cols:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'\D','',regex=True)
                    st.success(T['success']); st.rerun()
            else: st.info(T['locked'])

        with tab3:
            st.write(f"**{T['tool5']}**")
            case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase","Lowercase","Title Case"], key="sel_case")
            if st.button(T['apply_btn'], key="btn_case"):
                for col in case_cols:
                    if case_opt=="Uppercase": st.session_state.df_clean[col]=st.session_state.df_clean[col].str.upper()
                    elif case_opt=="Lowercase": st.session_state.df_clean[col]=st.session_state.df_clean[col].str.lower()
                    else: st.session_state.df_clean[col]=st.session_state.df_clean[col].str.title()
                st.success(T['success']); st.rerun()

            st.write(f"**{T['tool6']}**")
            if is_pro:
                spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec")
                if st.button(T['apply_btn'], key="btn_spec"):
                    for col in spec_cols:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'[^a-zA-Z0-9\s@.]','',regex=True)
                    st.success(T['success']); st.rerun()
            else: st.info(T['locked'])

            st.write(f"**{T['tool7']}**")
            if is_pro:
                old = st.selectbox("Old name", all_cols, key="sel_old")
                new = st.text_input("New name", key="inp_new")
                if st.button(T['apply_btn'], key="btn_rename") and new:
                    st.session_state.df_clean.rename(columns={old:new}, inplace=True)
                    st.success(T['success']); st.rerun()
            else: st.info(T['locked'])

        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
        user = load_db().get(st.session_state.email,{})

        # PAID USER KO QR NAHI DIKHEGA - SIDHA DOWNLOAD
        if st.session_state.plan=="free" or user.get("status")=="PAID":
            col1,col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()

            if col1.download_button("📄 Download CSV", csv, "clean_data.csv", key="dl_csv"):
                st.session_state.show_balloon = True

            if is_pro:
                excel = io.BytesIO()
                st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                if col2.download_button("📊 Download Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel"):
                    st.session_state.show_balloon = True

            # BALLOON FIX - session_state se
            if st.session_state.show_balloon:
                st.balloons()
                st.session_state.show_balloon = False
        else:
            st.error(f"🔒 {T['paid_msg']}")
            st.markdown(f"### {T['upi_text']}")
            upi_link = f"upi://pay?pa={UPI}&pn=VeriSame%20Pro&am={st.session_state.amt}&cu=INR"
            qr = qrcode.make(upi_link)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), width=280)
            st.code(UPI)
            if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary"):
                st.success(T['success_msg'])
