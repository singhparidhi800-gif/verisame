import streamlit as st
import json, os, io, qrcode, hashlib
import pandas as pd
import re
from datetime import datetime, timedelta

st.markdown('<meta name="google-site-verification" content="r1wzMau1uinP14S7qbYJcmve44Ih7SEO-MdK9TZjW9A" />', unsafe_allow_html=True)
st.set_page_config(page_title="VeriSame Pro", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
ADMIN_PASS = hashlib.sha256("Sherni@123".encode()).hexdigest()
DB_FILE = "orders.json"

if not os.path.exists(DB_FILE): json.dump({}, open(DB_FILE,"w"))
def save_db(d): json.dump(d, open(DB_FILE,"w"), indent=2)
@st.cache_data
def load_db():
    with open(DB_FILE,"r") as f: return json.load(f)

def words_to_num(s):
    if pd.isna(s): return s
    s = str(s).lower().strip()
    if s.isdigit(): return int(s)
    num_words = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,'hundred':100,'thousand':1000,'lakh':100000,'crore':10000000}
    total = 0; current = 0
    for word in re.findall(r'\w+', s):
        if word in num_words:
            val = num_words[word]
            if val >= 100:
                current = max(1, current) * val
                if val >= 1000: total += current; current = 0
            else: current += val
    return total + current if total + current > 0 else s

T = {
    "title":"VeriSame Pro","tagline":"Enterprise Data Cleaning Suite","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"MONTHLY PLAN","pro6_title":"6 MONTHS PLAN",
    "free_feat":["1000 Rows Lifetime","CSV + Excel Export","2 Basic Tools","30s Processing","Email Support"],
    "pro_feat":["Unlimited Rows","CSV + Excel Export","10 Premium AI Tools","3s Speed","Priority Support","No Watermark","Free Updates"],
    "email_label":"Enter your email to start","continue_btn":"Continue →","upload_tab":"Upload File","sample_tab":"Try Demo",
    "upload_text":"Drop CSV, Excel or JSON here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Preview - First 10 Rows",
    "tools_menu":"AI Studio","back_btn":"Back to Plans","download_title":"Export Clean Data",
    "paid_msg":"Step 1: Scan QR & Pay. Step 2: Click I Paid. Step 3: Admin will approve. Step 4: Download unlocks",
    "upi_text":"Scan QR to Pay","paid_btn":"✓ I Have Paid ₹{amount}","success_msg":"Payment request sent! Wait for approval",
    "download_success":"Download completed successfully!","locked":"PRO ONLY - Upgrade to unlock",
    "tab1":"Date & Nulls","tab2":"Email & Phone","tab3":"Text AI","tool1":"1. Smart Date","tool2":"2. AI Fill","tool3":"3. Email Validator",
    "tool4":"4. Phone Formatter","tool5":"5. Case Converter","tool6":"6. Remove Symbols","tool7":"7. Bulk Rename","tool8":"8. Remove Duplicates",
    "tool9":"9. Trim Spaces","tool10":"10. Spell Check","select_col":"Select Columns","select_case":"Choose Case","apply_btn":"Apply","success":"Applied! ✓",
    "expiry_warn":"EXPIRES IN {days} DAYS! RENEW NOW","pro_active":"Plan Active\nValid Till: {date}\n{days} days left","free_plan":"FREE Plan - Lifetime",
    "expired":"PLAN EXPIRED! PAY AGAIN","admin_title":"Admin Dashboard","admin_pending":"Pending Approvals","admin_approve_btn":"Approve",
    "admin_user":"Customer","admin_plan":"Plan","admin_expiry":"Valid Till","admin_status":"Status"
}

# PURPLE PINK PROFESSIONAL CSS - TIGHT SPACING
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], p, div, span, label, h1, h2, h3, h4, h5, h6 {font-family: 'Inter', sans-serif; color: #2D1B4E!important;}
.stApp {background: linear-gradient(135deg, #1A0033 0%, #2D1B69 50%, #1A0033 100%); padding-top: 0.5rem;}
.block-container {background: rgba(255,255,255,0.98); backdrop-filter: blur(20px); border-radius: 20px; padding: 1.8rem 2rem; max-width: 1200px; margin: 0 auto; box-shadow: 0 20px 60px rgba(138,43,226,0.3); border: 2px solid rgba(219,39,119,0.2);}
h1 {font-weight: 800!important; background: linear-gradient(90deg, #8B5CF6, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem!important; margin-bottom: 0.3rem!important; letter-spacing: -1px;}
h2, h3 {color: #2D1B4E!important; font-weight: 700!important; margin-top: 1.2rem!important; margin-bottom: 0.8rem!important; font-size: 1.4rem!important;}
.stMarkdown p {color: #6B7280!important; font-size: 1rem; margin-bottom: 0.3rem!important;}
[data-testid="stImage"] img {max-height: 70px; width: auto!important;}
.pricing-card {border: 2px solid #E9D5FF; border-radius: 16px; padding: 1.5rem 1.2rem; background: linear-gradient(180deg, #FAF5FF 0%, #FFFFFF 100%); height: 100%; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(139,92,246,0.1);}
.pricing-card:hover {transform: translateY(-4px); box-shadow: 0 12px 24px rgba(219,39,119,0.25); border-color: #EC4899;}
.pricing-card h2 {font-size: 1.2rem!important; margin-bottom: 0.4rem!important; color: #581C87!important;}
.pricing-card h1 {font-size: 2.2rem!important; background: linear-gradient(90deg, #8B5CF6, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0.4rem 0!important;}
.pricing-card p {font-size: 0.85rem!important; color: #7C3AED!important; margin-bottom: 0.8rem!important; font-weight: 500;}
.stButton>button {border-radius: 10px; font-weight: 600; background: linear-gradient(90deg, #8B5CF6, #EC4899); color: white!important; border: none; font-size: 0.95rem; padding: 10px 20px; width: 100%; box-shadow: 0 4px 12px rgba(139,92,246,0.4); transition: all 0.2s;}
.stButton>button:hover {transform: translateY(-2px); box-shadow: 0 8px 20px rgba(219,39,119,0.5); background: linear-gradient(90deg, #7C3AED, #DB2777);}
.stFileUploader {border-radius: 12px; border: 2px dashed #C084FC; background: #FAF5FF;}
.stMultiSelect,.stSelectbox {margin-bottom: 0.8rem!important;}
.stMultiSelect > div > div {border-radius: 8px; border: 1.5px solid #D8B4FE;}
.stDataFrame {border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(139,92,246,0.1); border: 1px solid #E9D5FF;}
.expiry-alert {background: linear-gradient(90deg, #DC2626, #EC4899); color: white!important; padding: 10px; border-radius: 8px; text-align: center; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.8rem;}
.pro-banner {background: linear-gradient(135deg, #581C87, #831843); padding: 1.5rem; border-radius: 16px; color: white!important; text-align: center; margin: 1rem 0;}
.pro-banner h2 {color: white!important; margin: 0!important; font-size: 1.4rem;}
.tool-chip {display: inline-block; background: rgba(236,72,153,0.15); backdrop-filter: blur(10px); padding: 6px 14px; border-radius: 20px; margin: 3px; font-weight: 600; border: 1px solid rgba(219,39,119,0.4); color: white!important; font-size: 0.85rem;}
.download-msg {background: linear-gradient(90deg, #7C3AED, #EC4899); color: white!important; padding: 14px; border-radius: 8px; margin-top: 0.8rem; text-align: center; font-weight: 600;}
.admin-card {background: #FAF5FF; padding: 1rem; border-radius: 12px; margin: 0.6rem 0; border: 1.5px solid #E9D5FF;}
.element-container {margin-bottom: 0.4rem!important;}
.stTabs [data-baseweb="tab-list"] {gap: 8px;}
.stTabs [data-baseweb="tab"] {background: #F3E8FF; border-radius: 8px; padding: 8px 16px;}
</style>
""", unsafe_allow_html=True)

# SESSION
if 'plan' not in st.session_state: st.session_state.plan = None
if 'email' not in st.session_state: st.session_state.email = ""
if 'df_clean' not in st.session_state: st.session_state.df_clean = None
if 'show_balloon' not in st.session_state: st.session_state.show_balloon = False
if 'show_download_msg' not in st.session_state: st.session_state.show_download_msg = False
if 'payment_clicked' not in st.session_state: st.session_state.payment_clicked = False
if 'amt' not in st.session_state: st.session_state.amt = 0
if 'sample_loaded' not in st.session_state: st.session_state.sample_loaded = False
if 'email_entered' not in st.session_state: st.session_state.email_entered = False

# BACK BUTTON
if st.session_state.plan is not None or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], key="btn_back_side"):
        st.session_state.plan = None; st.session_state.email = ""; st.session_state.df_clean = None; st.session_state.payment_clicked = False; st.session_state.sample_loaded = False; st.session_state.email_entered = False
        st.rerun()

# EMAIL CHECK
if st.session_state.email:
    user = load_db().get(st.session_state.email,{})
    st.sidebar.success(f"📧 {st.session_state.email}")
    if user.get("plan") == "pro":
        exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days
        if days_left > 0:
            st.session_state.plan = "pro"
            st.session_state.amt = user.get("amt", 299)
            if 0 < days_left <= 5:
                st.sidebar.markdown(f"<div class='expiry-alert'>⚠️ {T['expiry_warn'].format(days=days_left)}</div>", unsafe_allow_html=True)
            st.sidebar.info(T['pro_active'].format(date=user['expiry'], days=days_left))
        else:
            st.sidebar.error(T['expired'])
            st.session_state.plan = None
            st.session_state.payment_clicked = False
    elif user.get("plan") == "free":
        st.session_state.plan = "free"
        st.sidebar.info(T['free_plan'])

# HEADER - ANIME + LOGO TIGHT
col1, col2 = st.columns([1,4])
with col1:
    st.image("https://i.ibb.co/Vps2R8np/anime-girl-pink-hair-beautiful-anime-girl.png", width=110)
with col2:
    st.title(T['title'])
    st.markdown(f"**{T['tagline']}**")

# PRO BANNER - PURPLE PINK NO BLUE BOX
st.markdown(f"<div class='pro-banner'><h2>💎 {T['pro_banner']}</h2><div><span class='tool-chip'>Smart Date</span><span class='tool-chip'>AI Fill</span><span class='tool-chip'>Email AI</span><span class='tool-chip'>Phone AI</span><span class='tool-chip'>Case</span><span class='tool-chip'>Clean</span><span class='tool-chip'>Rename</span><span class='tool-chip'>Dedup</span><span class='tool-chip'>Trim</span><span class='tool-chip'>Spell</span></div></div>", unsafe_allow_html=True)

# ADMIN - SECURITY HASHED
if st.query_params.get("admin"):
    input_hash = hashlib.sha256(st.query_params.get("admin").encode()).hexdigest()
    if input_hash == ADMIN_PASS:
        st.title(T['admin_title'])
        st.warning("⚠️ Authorized Access Only")
        data = load_db()
        pending = {e:i for e,i in data.items() if i.get("status")=="PENDING" and "@" in e}
        st.metric(T['admin_pending'], len(pending))
        if pending:
            for email,info in pending.items():
                amt = info.get('amt',0)
                days = 30 if amt==299 else 180
                plan_text = f"PRO Monthly ₹299 - {days} days" if amt==299 else f"PRO 6 Months ₹1499 - {days} days"
                col1, col2 = st.columns([4,1])
                with col1:
                    st.markdown(f"<div class='admin-card'><b>{T['admin_user']}:</b> {email}<br><b>{T['admin_plan']}:</b> {plan_text}<br><b>{T['admin_expiry']}:</b> {info['expiry']}</div>", unsafe_allow_html=True)
                with col2:
                    if st.button(T['admin_approve_btn'], key=f"approve_{email}", type="primary"):
                        data[email]["status"] = "PAID"
                        save_db(data)
                        st.success(f"✓ {email} approved!")
                        st.balloons()
                        st.rerun()
        st.markdown("---")
        st.subheader("All Users")
        all_users = {e:i for e,i in data.items() if "@" in e}
        for email,info in all_users.items():
            status = info.get('status','N/A')
            plan = info.get('plan','free')
            amt = info.get('amt',0)
            expiry = info.get('expiry','N/A')
            badge = "FREE" if plan == "free" else f"PRO ₹{amt}"
            status_color = "#7C3AED" if status=="PAID" else "#EC4899"
            st.markdown(f"<div class='admin-card'><b>{email}</b> | {badge} | Status: <span style='color:{status_color};font-weight:600'>{status}</span> | Valid: {expiry}</div>", unsafe_allow_html=True)
        st.stop()

# PLANS - TIGHT PURPLE PINK
if st.session_state.plan is None:
    col1,col2,col3 = st.columns(3, gap="small")
    with col1:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>{T['free_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<h1>FREE</h1>", unsafe_allow_html=True)
        st.markdown("<p>Lifetime Access</p>", unsafe_allow_html=True)
        for f in T['free_feat']: st.markdown(f"✓ {f}")
        if st.button("Start FREE", key="btn_free", type="primary"):
            st.session_state.plan="free"; st.session_state.amt=0
            data = load_db()
            expiry = (datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
            data[st.session_state.email] = {"plan":"free","status":"PAID","amt":0,"expiry":expiry,"created":str(datetime.now())}
            save_db(data)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='pricing-card' style='border-color:#EC4899;box-shadow:0 8px 24px rgba(219,39,119,0.3)'>", unsafe_allow_html=True)
        st.markdown("⭐ MOST POPULAR")
        st.markdown(f"<h2>{T['pro1_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1>₹{PRO_1M}</h1>", unsafe_allow_html=True)
        st.markdown("<p>Valid for 30 Days</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.markdown(f"✓ {f}")
        if st.button(f"Get Monthly", key="btn_pro1", type="primary"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_1M; st.session_state.days=30
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>{T['pro6_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1>₹{PRO_6M}</h1>", unsafe_allow_html=True)
        st.markdown("<p>Valid for 180 Days</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.markdown(f"✓ {f}")
        if st.button(f"Get 6 Months", key="btn_pro6", type="primary"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_6M; st.session_state.days=180
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
else:
    if not st.session_state.email_entered:
        email_input = st.text_input(T['email_label']).lower().strip()
        if st.button(T['continue_btn'], key="btn_continue", type="primary"):
            if "@" in email_input and "." in email_input:
                st.session_state.email = email_input
                st.session_state.email_entered = True
                data = load_db()
                if email_input in data and data[email_input].get("status")=="PAID":
                    exp_date = datetime.strptime(data[email_input]["expiry"], "%Y-%m-%d")
                    if exp_date > datetime.now():
                        st.session_state.plan = data[email_input]["plan"]
                        st.session_state.amt = data[email_input].get("amt", 0)
                st.rerun()
            else: st.error("Enter valid email")
        st.stop()

    tab1,tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    df = None
    with tab1:
        file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"])
        if file:
            if file.name.endswith(".csv"): df = pd.read_csv(file)
            elif file.name.endswith(("xlsx","xls")): df = pd.read_excel(file)
            else: df = pd.read_json(file)
            st.session_state.sample_loaded = False
    with tab2:
        if st.button(T['sample_btn'], key="btn_sample"):
            df = pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT SINGH"],"Email":["RAHUL@GMAIL.COM","bad email@","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["one hundred","250","two thousand five hundred"]})
            st.session_state.sample_loaded = True

    if df is not None:
        st.session_state.df_clean = df.copy()
        orig_len = len(df)
        df_clean = st.session_state.df_clean.drop_duplicates()
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
            if any(k in col.lower() for k in ['salary','amount','price']): df_clean[col] = df_clean[col].apply(words_to_num)
        st.session_state.df_clean = df_clean

        st.markdown(f"<h2>{T['summary_title']}</h2>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric(T['rows'], orig_len)
        with c2: st.metric(T['clean'], len(df_clean))
        with c3: st.metric(T['dups'], orig_len-len(df_clean))
        with c4: st.metric(T['empty'], df.isna().sum().sum())

        st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
        st.caption(T['preview'])
        st.dataframe(df_clean.head(10), use_container_width=True, height=320)

        all_cols = df_clean.columns.tolist()
        user = load_db().get(st.session_state.email,{})
        is_pro = st.session_state.plan=="pro" and user.get("status")=="PAID"

        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
        with tab1:
            st.write(f"**{T['tool1']}**")
            date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date", disabled=not is_pro)
            if not is_pro: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_date", disabled=not is_pro):
                for col in date_cols: st.session_state.df_clean[col] = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                st.success(T['success'])

            st.write(f"**{T['tool2']}**")
            fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=not is_pro)
            if not is_pro: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_fill", disabled=not is_pro):
                st.session_state.df_clean[fill_cols] = st.session_state.df_clean[fill_cols].fillna("N/A")
                st.success(T['success'])

        with tab2:
            st.write(f"**{T['tool3']}**")
            email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=not is_pro)
            if not is_pro: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_email", disabled=not is_pro):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in email_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).lower() if re.match(pattern, str(x)) else "")
                st.success(T['success'])

            st.write(f"**{T['tool4']}**")
            phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=not is_pro)
            if not is_pro: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_phone", disabled=not is_pro):
                for col in phone_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'\D', '', regex=True)
                st.success(T['success'])

        with tab3:
            st.write(f"**{T['tool5']}**")
            case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
            if st.button(T['apply_btn'], key="btn_case"):
                for col in case_cols:
                    if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].str.upper()
                    elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].str.lower()
                    else: st.session_state.df_clean[col] = st.session_state.df_clean[col].str.title()
                st.success(T['success'])

            st.write(f"**{T['tool6']}**")
            spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec", disabled=not is_pro)
            if not is_pro: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_spec", disabled=not is_pro):
                for col in spec_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'[^a-zA-Z0-9\s@.]', '', regex=True)
                st.success(T['success'])

            st.write(f"**{T['tool7']}**")
            old = st.selectbox("Old name", all_cols, key="sel_old", disabled=not is_pro)
            new = st.text_input("New name", key="inp_new", disabled=not is_pro)
            if not is_pro: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_rename", disabled=not is_pro) and new:
                st.session_state.df_clean.rename(columns={old: new}, inplace=True)
                st.success(T['success'])

            st.write(f"**{T['tool8']}**")
            if st.button(T['apply_btn'], key="btn_dedup", disabled=not is_pro):
                st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                st.success(T['success'])
            if not is_pro: st.caption(f"🔒 {T['locked']}")

            st.write(f"**{T['tool9']}**")
            trim_cols = st.multiselect(T['select_col'], all_cols, key="ms_trim")
            if st.button(T['apply_btn'], key="btn_trim"):
                for col in trim_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip()
                st.success(T['success'])

            st.write(f"**{T['tool10']}**")
            spell_cols = st.multiselect(T['select_col'], all_cols, key="ms_spell", disabled=not is_pro)
            if not is_pro: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_spell", disabled=not is_pro):
                for col in spell_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).replace("teh", "the").replace("recieve", "receive").title())
                st.success(T['success'])

        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
        if st.session_state.show_balloon:
            st.balloons()
            st.session_state.show_balloon = False
        if st.session_state.show_download_msg:
            st.markdown(f"<div class='download-msg'>{T['download_success']}</div>", unsafe_allow_html=True)
            st.session_state.show_download_msg = False

        if st.session_state.plan == "free":
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button("Download CSV", csv, "clean_data.csv", key="dl_csv_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button("Download Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
        elif user.get("status")!= "PAID":
            st.error(f"🔒 {T['paid_msg']}")
            st.markdown(f"### {T['upi_text']}")
            upi_link = f"upi://pay?pa={UPI}&pn=VeriSame&am={st.session_state.amt}&cu=INR"
            qr = qrcode.make(upi_link)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), width=220)
            st.code(UPI)
            if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary"):
                data = load_db()
                days = 30 if st.session_state.amt == 299 else 180
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                data[st.session_state.email] = {"plan": "pro", "status": "PENDING", "amt": st.session_state.amt, "expiry": expiry, "created": str(datetime.now())}
                save_db(data)
                st.session_state.payment_clicked = True
                st.success(T['success_msg'])
            if st.session_state.payment_clicked:
                st.info("⏳ Waiting for admin approval...")
        else:
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button("Download CSV", csv, "clean_data.csv", key="dl_csv_paid"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button("Download Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_paid"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
