import streamlit as st
import json, os, io
import pandas as pd
import time
import re
from datetime import datetime, timedelta

# ============ LANGUAGE DICTIONARY ============
LANG = {
    "English": {
        "title": "VeriSame", "subtitle": "The Fastest Way to Clean Your Data",
        "pro_banner": "🚀 PRO Includes 7 Advanced Tools",
        "free": "FREE Forever", "pro1": "Monthly Pro", "pro6": "Best Value",
        "free_feat": ["✓ 1000 Rows Lifetime", "✓ CSV Download", "✓ 5 Basic Tools", "✓ 30 Second Wait"],
        "pro_feat": ["✓ Unlimited Rows", "✓ Excel + CSV Export", "✓ All 7 PRO Tools", "✓ 3 Second Speed"],
        "email": "Enter your email to continue", "continue": "Continue",
        "upload": "Upload your file", "sample": "Try sample data",
        "tools_menu": "🛠️ Advanced Tools Menu", "preview": "Preview first 10 rows",
        "download": "Download clean file", "paid": "Payment pending. Admin will verify soon",
        "upi": "Pay via UPI", "paid_btn": "I have paid",
        "back": "⬅️ Back to plans", "rows": "Total rows", "clean": "Clean rows",
        "dups": "Duplicates removed", "empty": "Empty cells", "apply": "Apply", "success": "Done!",
        "locked": "🔒 PRO Feature - Upgrade to unlock",
        "tab1": "📅 Date & Empty Boxes", "tab2": "📧 Email & Phone", "tab3": "✨ Advanced Text Cleaners",
        "tool1": "1. Auto Date Normalizer (PRO)", "tool2": "2. Smart Fill Missing (PRO)",
        "tool3": "3. Email Validator (PRO)", "tool4": "4. Phone Formatter (PRO)",
        "tool5": "5. Text Case Converter (FREE)", "tool6": "6. Remove Special Chars (PRO)",
        "tool7": "7. Column Renamer (PRO)",
        "select_col": "Select columns", "select_case": "Select case type"
    },
    "Hindi": {
        "title": "VeriSame", "subtitle": "Data Saaf Karne Ka Sabse Fast Tareeka",
        "pro_banner": "🚀 PRO me 7 Advanced Tools",
        "free": "FREE Hamesha", "pro1": "Monthly Pro", "pro6": "Best Deal",
        "free_feat": ["✓ 1000 Row Lifetime", "✓ Sirf CSV Download", "✓ 5 Basic Tools", "✓ 30 Sec Wait"],
        "pro_feat": ["✓ Unlimited Row", "✓ Excel + CSV Export", "✓ 7 Saare PRO Tools", "✓ 3 Sec Speed"],
        "email": "Aage badhne ke liye email daalo", "continue": "Aage badho",
        "upload": "Apna file daalo", "sample": "Sample data try karo",
        "tools_menu": "🛠️ Advanced Tools Menu", "preview": "Sirf pehle 10 row dikhenge",
        "download": "Saaf file download karo", "paid": "Payment pending. Admin jaldi verify karega",
        "upi": "UPI se paise bhejo", "paid_btn": "Maine paise bhej diye",
        "back": "⬅️ Wapas plans pe", "rows": "Total row", "clean": "Saaf row",
        "dups": "Duplicate hate", "empty": "Khali cell", "apply": "Lagao", "success": "Ho gaya!",
        "locked": "🔒 PRO Feature hai. Upgrade karo",
        "tab1": "📅 Date & Khali Box", "tab2": "📧 Email & Phone", "tab3": "✨ Text Saaf Karo",
        "tool1": "1. Date Format Thik Karo (PRO)", "tool2": "2. Khali Box Bhardo (PRO)",
        "tool3": "3. Email Check Karo (PRO)", "tool4": "4. Phone Number Saaf Karo (PRO)",
        "tool5": "5. Bade Chote Akshar (FREE)", "tool6": "6. Bad Symbol Hatao (PRO)",
        "tool7": "7. Column Naam Badlo (PRO)",
        "select_col": "Column chuno", "select_case": "Case chuno"
    }
}

# ============ DB ============
DB, COUNT_FILE = "orders.json", "counts.json"
for f in [DB, COUNT_FILE]:
    if not os.path.exists(f):
        json.dump({} if f==DB else {"views":0,"free":0,"pro":0}, open(f,"w"))
def save_db(d): json.dump(d, open(DB,"w"))
def load_db(): return json.load(open(DB))
def update_count(k): c=json.load(open(COUNT_FILE)); c[k]=c.get(k,0)+1; json.dump(c, open(COUNT_FILE,"w"))

UPI, PRO_1M, PRO_6M, ADMIN_PASS = "playwithreyansh0@okhdfcbank", 299, 1499, "Sherni@123"
st.set_page_config(page_title="VeriSame", layout="wide")

# ============ CSS FOR PURPLE DESIGN ============
st.markdown("""
<style>
.stApp {background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c); background-size: 400% 400%; animation: gradient 15s ease infinite;}
@keyframes gradient {0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}}
.block-container {background: rgba(255,255,255,0.98); border-radius: 24px; padding: 2rem 3rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3);}
.pro-banner {background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 20px; color: white; text-align: center; margin: 20px 0;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px; margin: 5px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# ============ LANGUAGE ============
lang = st.sidebar.selectbox("Language / भाषा", ["English", "Hindi"])
T = LANG[lang]

st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png", width=200)
st.title(f"💼 {T['title']}")
st.subheader(T['subtitle'])

# ============ ADMIN ============
if st.query_params.get("admin") == ADMIN_PASS:
    st.title("🔒 Admin Panel")
    data = load_db()
    for email,info in data.items():
        if info["status"]=="PENDING":
            c1,c2 = st.columns([4,1])
            c1.write(f"📧 {email} | {info['plan']} | ₹{info['amt']}")
            if c2.button("Mark PAID", key=email, type="primary"):
                data[email]["status"]="PAID"; save_db(data); st.rerun()
    st.stop()

if 'plan' not in st.session_state: st.session_state.plan = None
if 'email' not in st.session_state: st.session_state.email = ""

# ============ PLAN CARDS WITH PURPLE BANNER ============
if st.session_state.plan is None:
    st.markdown(f"<div class='pro-banner'><h3>{T['pro_banner']}</h3><div><span class='tool-chip'>📅 Date Standardizer</span><span class='tool-chip'>📊 SmartFill Missing</span><span class='tool-chip'>📧 Email Validator</span><span class='tool-chip'>📱 Phone Formatter</span><span class='tool-chip'>🔤 Text Case Converter</span><span class='tool-chip'>✨ Remove Special Chars</span><span class='tool-chip'>✏️ Column Renamer</span></div></div>", unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader(f"🆓 {T['free']}")
            for f in T['free_feat']: st.write(f)
            if st.button("Use FREE", use_container_width=True):
                update_count("free"); st.session_state.plan="free"; st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader(f"🔥 {T['pro1']}")
            for f in T['pro_feat']: st.write(f)
            st.write(f"**₹{PRO_1M}/month**")
            if st.button(f"₹{PRO_1M}/Month", use_container_width=True, type="primary"):
                update_count("pro"); st.session_state.plan="pro"; st.session_state.amt=PRO_1M; st.session_state.days=30; st.rerun()
    with col3:
        with st.container(border=True):
            st.subheader(f"💎 {T['pro6']}")
            for f in T['pro_feat']: st.write(f)
            st.write(f"**₹{PRO_6M}/6 months**")
            if st.button(f"₹{PRO_6M}/6 Months", use_container_width=True, type="primary"):
                update_count("pro"); st.session_state.plan="pro"; st.session_state.amt=PRO_6M; st.session_state.days=180; st.rerun()

# ============ MAIN APP ============
else:
    if not st.session_state.email:
        st.session_state.email = st.text_input(T['email']).lower().strip()
        if st.button(T['continue'], type="primary", use_container_width=True):
            if "@" in st.session_state.email:
                data = load_db()
                if st.session_state.email not in data:
                    expiry = (datetime.now()+timedelta(days=st.session_state.get("days",0))).strftime("%Y-%m-%d")
                    data[st.session_state.email] = {"plan":st.session_state.plan,"status":"PENDING","amt":st.session_state.get("amt",0),"expiry":expiry}
                    save_db(data)
                st.rerun()
            else: st.error("Valid email daalo")
        st.stop()

    if st.button(T['back']): st.session_state.clear(); st.rerun()

    tab1,tab2 = st.tabs([f"📁 {T['upload']}", f"🧪 {T['sample']}"])
    df = None
    with tab1:
        file = st.file_uploader(T['upload'], type=["csv","xlsx","xls","json"])
        if file:
            with st.spinner("3 sec processing..."):
                time.sleep(3)
                if file.name.endswith(".csv"): df = pd.read_csv(file)
                elif file.name.endswith(("xlsx","xls")): df = pd.read_excel(file)
                else: df = pd.read_json(file)
    with tab2:
        if st.button(T['sample']):
            df = pd.DataFrame({
                "Joining Date": ["12/5/2024", "2024-01-15", "", "bad date"],
                "Name": [" RAHUL ", "priya sharma", "RAHUL", "Amit@123"],
                "Email": ["RAHUL@GMAIL.COM", "bad@", "priya@email.com", ""],
                "Phone": ["98765-43210", "9123 456 789", "000", ""],
                "Amount": ["one hundred", "250", "thirty five", "500"]
            })

    if df is not None:
        orig_len = len(df)
        if st.session_state.plan=="free" and orig_len>1000:
            df = df.head(1000); st.warning("Free: only first 1000 rows")

        # FREE BASIC CLEAN
        df_clean = df.drop_duplicates()
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)

        st.subheader("📊 Live Summary")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric(T['rows'], orig_len)
        c2.metric(T['clean'], len(df_clean))
        c3.metric(T['dups'], orig_len-len(df_clean))
        c4.metric(T['empty'], df.isna().sum().sum())
        st.dataframe(df_clean.head(10), use_container_width=True)
        st.caption(T['preview'])

        # ============ 3 TABS TOOL MENU EXACT LIKE SCREENSHOT ============
        st.divider()
        st.subheader(T['tools_menu'])
        all_cols = df_clean.columns.tolist()
        is_pro = st.session_state.plan=="pro" and load_db().get(st.session_state.email,{}).get("status")=="PAID"

        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])

        with tab1:
            st.write(f"**{T['tool1']}**")
            if is_pro:
                date_cols = st.multiselect(T['select_col'], all_cols, key="date")
                if st.button(T['apply'], key="date"):
                    for col in date_cols: df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                    st.success("Dates fixed to standard YYYY-MM-DD format!")
            else: st.info(T['locked'])

            st.write(f"**{T['tool2']}**")
            if is_pro:
                fill_cols = st.multiselect(T['select_col'], all_cols, key="fill")
                if st.button(T['apply'], key="fill"):
                    df_clean[fill_cols] = df_clean[fill_cols].fillna("N/A")
                    st.success(T['success'])
            else: st.info(T['locked'])

        with tab2:
            st.write(f"**{T['tool3']}**")
            if is_pro:
                email_cols = st.multiselect(T['select_col'], all_cols, key="email")
                if st.button(T['apply'], key="email"):
                    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    for col in email_cols: df_clean[col] = df_clean[col].apply(lambda x: x.lower() if re.match(pattern,str(x)) else "")
                    st.success("Invalid emails removed!")
            else: st.info(T['locked'])

            st.write(f"**{T['tool4']}**")
            if is_pro:
                phone_cols = st.multiselect(T['select_col'], all_cols, key="phone")
                if st.button(T['apply'], key="phone"):
                    for col in phone_cols: df_clean[col] = df_clean[col].str.replace(r'\D','',regex=True)
                    st.success(T['success'])
            else: st.info(T['locked'])

        with tab3:
            st.write(f"**{T['tool5']}**")
            case_cols = st.multiselect(T['select_col'], all_cols, key="case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase","Lowercase","Title Case"])
            if st.button(T['apply'], key="case"):
                for col in case_cols:
                    if case_opt=="Uppercase": df_clean[col]=df_clean[col].str.upper()
                    elif case_opt=="Lowercase": df_clean[col]=df_clean[col].str.lower()
                    else: df_clean[col]=df_clean[col].str.title()
                st.success(T['success'])

            st.write(f"**{T['tool6']}**")
            if is_pro:
                spec_cols = st.multiselect(T['select_col'], all_cols, key="spec")
                if st.button(T['apply'], key="spec"):
                    for col in spec_cols: df_clean[col] = df_clean[col].str.replace(r'[^a-zA-Z0-9\s@.]','',regex=True)
                    st.success(T['success'])
            else: st.info(T['locked'])

            st.write(f"**{T['tool7']}**")
            if is_pro:
                old = st.selectbox("Old name", all_cols)
                new = st.text_input("New name")
                if st.button(T['apply'], key="rename") and new:
                    df_clean.rename(columns={old:new}, inplace=True)
                    st.success(T['success'])
            else: st.info(T['locked'])

        # ============ DOWNLOAD + BALLOON ============
        st.divider()
        st.subheader(f"📥 {T['download']}")
        user = load_db().get(st.session_state.email,{})

        if st.session_state.plan=="free" or user.get("status")=="PAID":
            col1,col2 = st.columns(2)
            csv = df_clean.to_csv(index=False).encode()
            if col1.download_button("Download CSV", csv, "clean_data.csv"):
                st.balloons()

            if is_pro:
                excel = io.BytesIO()
                df_clean.to_excel(excel, index=False)
                if col2.download_button("Download Excel", excel.getvalue(), "clean_data.xlsx"):
                    st.balloons()
        else:
            st.error(f"🔒 {T['paid']}")
            st.code(UPI)
            if st.button(f"{T['paid_btn']} ₹{st.session_state.amt}"):
                st.success("Request sent! Admin verify karega")
