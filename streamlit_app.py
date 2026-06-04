import streamlit as st
import json, os, io, qrcode
import pandas as pd
import re
from datetime import datetime, timedelta

st.set_page_config(page_title="VeriSame Pro", page_icon="💜", layout="wide", initial_sidebar_state="expanded")

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
ADMIN_PASS = "Sherni@123"
DB_FILE = "orders.json"

if not os.path.exists(DB_FILE): json.dump({}, open(DB_FILE,"w"))
def save_db(d): json.dump(d, open(DB_FILE,"w"), indent=2)
def load_db(): return json.load(open(DB_FILE))

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

LANG = {
    "English": {"title":"VeriSame Pro","tagline":"AI-Powered Data Cleaning","pro_banner":"💜 UNLOCK 7 PREMIUM AI TOOLS","free_title":"FREE FOREVER","pro1_title":"PRO MONTHLY","pro6_title":"PRO 6 MONTHS","free_feat":["1000 Rows Lifetime","CSV Export Only","6 Basic Tools","Words → Numbers","30s Processing","Email Support"],"pro_feat":["Unlimited Rows","CSV + Excel Export","7 Premium AI Tools","3s Speed","Priority Support","No Watermark","Free Updates"],"email_label":"Enter your email","continue_btn":"Continue →","upload_tab":"📤 Upload File","sample_tab":"🧪 Try Demo","upload_text":"Drag & Drop CSV, Excel or JSON here","sample_btn":"Load Sample Data","summary_title":"📊 Live Summary","rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Preview - First 10 Rows","tools_menu":"⚡ Premium Studio","back_btn":"⬅️ Back to Plans","download_title":"📥 Export Clean Data","paid_msg":"Complete payment first, then click I Paid to unlock download","upi_text":"Scan QR to Pay","paid_btn":"✓ I Have Paid ₹{amount}","success_msg":"Payment request sent! Download unlocked below","download_success":"Download completed successfully! ✅","locked":"🔒 PRO - Upgrade","tab1":"📅 Date & Nulls","tab2":"📧 Email & Phone","tab3":"✨ Text AI","tool1":"1. Smart Date","tool2":"2. AI Fill","tool3":"3. Email Validator","tool4":"4. Phone Formatter","tool5":"5. Case Converter","tool6":"6. Remove Symbols","tool7":"7. Bulk Rename","select_col":"Select Columns","select_case":"Choose Case","apply_btn":"Apply","success":"Applied! ✅","expiry_warn":"⚠️ PRO expires in {days} days!","pro_active":"🔥 PRO Active\n📅 Till {date}\n⏰ {days} days left","free_plan":"🆓 FREE Plan","expired":"⚠️ PRO Expired!"},
    "Hindi": {"title":"VeriSame Pro","tagline":"AI se Data Saaf","pro_banner":"💜 7 PREMIUM AI TOOLS KHOLO","free_title":"FREE HAMESHA","pro1_title":"PRO MONTHLY","pro6_title":"PRO 6 MONTH","free_feat":["1000 Row Lifetime","Sirf CSV Export","6 Basic Tools","Shabd → Number","30 Sec Processing","Email Support"],"pro_feat":["Unlimited Rows","CSV + Excel Export","7 Saare AI Tools","3 Sec Speed","Priority Support","No Watermark","Free Updates"],"email_label":"Email daalo","continue_btn":"Aage →","upload_tab":"📤 File Upload","sample_tab":"🧪 Demo Data","upload_text":"CSV, Excel ya JSON yahan drag karo","sample_btn":"Sample Data Load","summary_title":"📊 Live Summary","rows":"Total Row","clean":"Saaf Row","dups":"Duplicate Hate","empty":"Khali Cell Thik","preview":"Preview - Sirf 10 Rows","tools_menu":"⚡ Premium Studio","back_btn":"⬅️ Wapas Plans","download_title":"📥 Download Karo","paid_msg":"Pehle payment karo, phir I Paid dabao download khul jayega","upi_text":"QR Scan Karo","paid_btn":"✓ Pay Kar Diya ₹{amount}","success_msg":"Request bhej di! Ab niche download khul gaya","download_success":"Download ho gaya! ✅","locked":"🔒 PRO - Upgrade Karo","tab1":"📅 Date & Khali","tab2":"📧 Email & Phone","tab3":"✨ Text AI","tool1":"1. Date Thik","tool2":"2. AI Fill","tool3":"3. Email Check","tool4":"4. Phone Saaf","tool5":"5. Case Badlo","tool6":"6. Symbol Hatao","tool7":"7. Naam Badlo","select_col":"Column Chuno","select_case":"Case Chuno","apply_btn":"Lagao","success":"Ho Gaya! ✅","expiry_warn":"⚠️ PRO {days} din me khatam!","pro_active":"🔥 PRO Active\n📅 {date} tak\n⏰ {days} din bache","free_plan":"🆓 FREE Plan","expired":"⚠️ PRO Expire!"}
}

# SOBER PURPLE-PINK + SIDE HIRE MOTI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}

.stApp {
    background: linear-gradient(135deg, #E8E2F3 0%, #F3E8F7 50%, #E8E2F3 100%);
    background-size: 300% 300%;
    animation: aura 20s ease infinite;
}
@keyframes aura {0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}}

/* Side hire moti pearls */
.stApp::before {
    content: '◊ ◊';
    position: fixed;
    left: 20px;
    top: 10%;
    font-size: 24px;
    color: #9B59B6;
    opacity: 0.3;
    writing-mode: vertical-rl;
    letter-spacing: 40px;
    animation: float 15s ease-in-out infinite;
    z-index: 999;
}
.stApp::after {
    content: '◊ ◊';
    position: fixed;
    right: 20px;
    top: 10%;
    font-size: 24px;
    color: #9B59B6;
    opacity: 0.3;
    writing-mode: vertical-rl;
    letter-spacing: 40px;
    animation: float 15s ease-in-out infinite reverse;
    z-index: 999;
}
@keyframes float {0%,100%{transform: translateY(0px)} 50%{transform: translateY(30px)}}

.block-container {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(20px);
    border-radius: 40px;
    padding: 3.5rem;
    box-shadow: 0 30px 80px rgba(155,89,182,0.2);
    border: 2px solid rgba(230,230,250,0.8);
    position: relative;
    z-index: 1;
}

h1 {
    font-weight: 700!important;
    background: linear-gradient(90deg, #8E44AD, #9B59B6, #BB8FCE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.5rem!important;
}

.pro-banner {
    background: linear-gradient(135deg, #8E44AD 0%, #9B59B6 50%, #AF7AC5 100%);
    padding: 50px;
    border-radius: 35px;
    color: white;
    text-align: center;
    margin: 40px 0;
    box-shadow: 0 20px 60px rgba(142,68,173,0.3);
    border: 2px solid rgba(255,255,255,0.5);
}

.tool-chip {
    display: inline-block;
    background: rgba(255,255,255,0.3);
    backdrop-filter: blur(10px);
    padding: 12px 24px;
    border-radius: 50px;
    margin: 8px;
    font-weight: 600;
    border: 2px solid rgba(255,255,255,0.6);
    box-shadow: 0 8px 20px rgba(142,68,173,0.2);
}

.pricing-card {
    border: 3px solid #E8DAEF;
    border-radius: 35px;
    padding: 40px;
    background: white;
    box-shadow: 0 15px 50px rgba(155,89,182,0.15);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.4s;
}
.pricing-card:hover {
    transform: translateY(-15px);
    box-shadow: 0 25px 70px rgba(142,68,173,0.3);
    border-color: #9B59B6;
}

.metric-card {
    background: linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%);
    color: white;
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(142,68,173,0.3);
}

.stButton>button {
    border-radius: 18px;
    font-weight: 600;
    transition: all 0.3s;
    border: none;
    box-shadow: 0 8px 20px rgba(142,68,173,0.3);
    background: linear-gradient(90deg, #8E44AD, #9B59B6);
    color: white;
}
.stButton>button:hover {
    transform: scale(1.05) translateY(-2px);
    box-shadow: 0 12px 30px rgba(142,68,173,0.5);
}

.download-msg {
    background: linear-gradient(90deg, #27AE60, #58D68D);
    color: yellow;
    padding: 18px;
    border-radius: 15px;
    margin-top: 15px;
    text-align: center;
    font-weight: 600;
    animation: slideIn 0.5s;
    border: 2px solid rgba(255,255,255,0.5);
}
@keyframes slideIn {from {opacity: 0; transform: translateY(-10px);} to {opacity: 1; transform: translateY(0);}}

.admin-card {
    background: rgba(248,240,255,0.95);
    border-radius: 25px;
    padding: 25px;
    margin: 15px 0;
    border: 2px solid #E8DAEF;
    box-shadow: 0 10px 30px rgba(155,89,182,0.15);
}
</style>
""", unsafe_allow_html=True)

# SESSION
if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'plan' not in st.session_state: st.session_state.plan = None
if 'email' not in st.session_state: st.session_state.email = ""
if 'df_clean' not in st.session_state: st.session_state.df_clean = None
if 'show_balloon' not in st.session_state: st.session_state.show_balloon = False
if 'show_download_msg' not in st.session_state: st.session_state.show_download_msg = False
if 'payment_clicked' not in st.session_state: st.session_state.payment_clicked = False
if 'amt' not in st.session_state: st.session_state.amt = 0

lang = st.sidebar.selectbox("🌐 Language", ["English", "Hindi"], index=0 if st.session_state.lang=="English" else 1, key="lang_select")
st.session_state.lang = lang
T = LANG[st.session_state.lang]

if st.session_state.email:
    user = load_db().get(st.session_state.email,{})
    st.sidebar.success(f"📧 {st.session_state.email}")
    if user.get("plan") == "pro":
        exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days
        if days_left > 0:
            st.sidebar.info(T['pro_active'].format(date=user['expiry'], days=days_left))
            if days_left <= 5: st.sidebar.warning(T['expiry_warn'].format(days=days_left))
        else:
            st.sidebar.error(T['expired'])
            st.session_state.plan = None
    elif user.get("plan") == "free": st.sidebar.info(T['free_plan'])
    if st.sidebar.button(T['back_btn'], key="btn_back_side"):
        st.session_state.plan = None; st.session_state.email = ""; st.session_state.df_clean = None; st.session_state.payment_clicked = False; st.rerun()

col_logo, col_title = st.columns([1,4])
with col_logo: st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png", width=380)
with col_title: st.title(T['title']); st.markdown(f"### {T['tagline']}")

st.markdown(f"<div class='pro-banner'><h2>{T['pro_banner']}</h2><div><span class='tool-chip'>📅 Smart Date</span><span class='tool-chip'>🤖 AI Fill</span><span class='tool-chip'>📧 Email AI</span><span class='tool-chip'>📱 Phone AI</span><span class='tool-chip'>🔤 Case</span><span class='tool-chip'>✨ Clean</span><span class='tool-chip'>✏️ Rename</span></div></div>", unsafe_allow_html=True)

# ADMIN - EMAIL + PLAN + PRICE FIX
if st.query_params.get("admin") == ADMIN_PASS:
    st.title("🔐 Admin Panel - Sherni")
    data = load_db()
    pending = [e for e,i in data.items() if i.get("status")=="PENDING" and "@" in e]
    st.metric("Pending", len(pending))

    all_users = [e for e in data.keys() if "@" in e]
    st.subheader(f"📧 Total Users: {len(all_users)}")

    for email in all_users:
        info = data.get(email,{})
        plan = info.get('plan','free')
        amt = info.get('amt',0)
        if plan == "free": plan_text = "FREE"; price_text = "FREE"; badge = "🆓"
        elif amt == 299: plan_text = "PRO 299"; price_text = "₹299"; badge = "💎"
        else: plan_text = "PRO 1499"; price_text = "₹1499"; badge = "👑"
        st.markdown(f"<div class='admin-card'>{badge} <b>Email:</b> {email} | <b>Plan:</b> {plan_text} | <b>Price:</b> {price_text} | <b>Status:</b> {info.get('status','N/A')} | <b>Expiry:</b> {info.get('expiry','N/A')}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("⏳ Pending Approvals")
    for email,info in data.items():
        if info.get("status")=="PENDING" and "@" in email:
            c1,c2,c3 = st.columns([3,2,1])
            amt = info.get('amt',0)
            if info['plan']=="free": plan_text="FREE"; price_text="FREE"; badge="🆓"
            elif amt==299: plan_text="PRO 299"; price_text="₹299"; badge="💎"
            else: plan_text="PRO 1499"; price_text="₹1499"; badge="👑"
            c1.markdown(f"<div class='admin-card'>{badge} <b>{email}</b></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='admin-card'><b>Plan:</b> {plan_text} | <b>{price_text}</b> | <b>Exp:</b> {info['expiry']}</div>", unsafe_allow_html=True)
            if c3.button("✅ Approve", key=f"admin_{email}", type="primary"):
                data[email]["status"]="PAID"; save_db(data); st.rerun()
    st.stop()

# PLANS
if st.session_state.plan is None:
    col1,col2,col3 = st.columns(3, gap="large")
    with col1:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#8E44AD'>🆓 {T['free_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center'>FREE</h1>", unsafe_allow_html=True)
        for f in T['free_feat']: st.write(f"✓ {f}")
        st.markdown("<div style='margin-top:auto'>", unsafe_allow_html=True)
        if st.button("Start FREE", key="btn_free", use_container_width=True, type="primary"):
            st.session_state.plan="free"; st.session_state.amt=0; st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='pricing-card' style='border-color:#9B59B6'>", unsafe_allow_html=True)
        st.markdown("⭐ MOST POPULAR")
        st.markdown(f"<h2 style='text-align:center; color:#8E44AD'>💎 {T['pro1_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center'>₹{PRO_1M}</h1>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.write(f"✓ {f}")
        st.markdown("<div style='margin-top:auto'>", unsafe_allow_html=True)
        if st.button(f"Get PRO Monthly", key="btn_pro1", use_container_width=True, type="primary"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_1M; st.session_state.days=30; st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#8E44AD'>👑 {T['pro6_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center'>₹{PRO_6M}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#27AE60; font-weight:600'>Save ₹295</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.write(f"✓ {f}")
        st.markdown("<div style='margin-top:auto'>", unsafe_allow_html=True)
        if st.button(f"Get PRO 6 Months", key="btn_pro6", use_container_width=True, type="primary"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_6M; st.session_state.days=180; st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

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
            if file.name.endswith(".csv"): df = pd.read_csv(file)
            elif file.name.endswith(("xlsx","xls")): df = pd.read_excel(file)
            else: df = pd.read_json(file)
    with tab2:
        if st.button(T['sample_btn'], key="btn_sample"):
            df = pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":["RAHUL ","priya","AMIT"],"Email":["RAHUL@GMAIL.COM","bad@",""],"Phone":["98765-43210","9123 456",""],"Salary":["one hundred","250","two thousand"]})

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
        with c1: st.markdown(f"<div class='metric-card'><h3>{orig_len}</h3><p>{T['rows']}</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><h3>{len(df_clean)}</h3><p>{T['clean']}</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><h3>{orig_len-len(df_clean)}</h3><p>{T['dups']}</p></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='metric-card'><h3>{df.isna().sum().sum()}</h3><p>{T['empty']}</p></div>", unsafe_allow_html=True)

        st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
        st.caption(T['preview'])
        st.dataframe(df_clean.head(10), use_container_width=True, height=350)

        all_cols = df_clean.columns.tolist()
        user = load_db().get(st.session_state.email,{})
        is_pro = st.session_state.plan=="pro" and user.get("status")=="PAID"

        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
        with tab1:
            st.write(f"**{T['tool1']}**")
            date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_date", disabled=not is_pro):
                for col in date_cols: st.session_state.df_clean[col] = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                st.success(T['success']); st.rerun()
            if not is_pro: st.info(T['locked'])
            st.write(f"**{T['tool2']}**")
            fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_fill", disabled=not is_pro):
                st.session_state.df_clean[fill_cols] = st.session_state.df_clean[fill_cols].fillna("N/A")
                st.success(T['success']); st.rerun()
            if not is_pro: st.info(T['locked'])

        with tab2:
            st.write(f"**{T['tool3']}**")
            email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_email", disabled=not is_pro):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in email_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).lower() if re.match(pattern,str(x)) else "")
                st.success(T['success']); st.rerun()
            if not is_pro: st.info(T['locked'])
            st.write(f"**{T['tool4']}**")
            phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_phone", disabled=not is_pro):
                for col in phone_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'\D','',regex=True)
                st.success(T['success']); st.rerun()
            if not is_pro: st.info(T['locked'])

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
            spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_spec", disabled=not is_pro):
                for col in spec_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'[^a-zA-Z0-9\s@.]','',regex=True)
                st.success(T['success']); st.rerun()
            if not is_pro: st.info(T['locked'])
            st.write(f"**{T['tool7']}**")
            old = st.selectbox("Old name", all_cols, key="sel_old", disabled=not is_pro)
            new = st.text_input("New name", key="inp_new", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_rename", disabled=not is_pro) and new:
                st.session_state.df_clean.rename(columns={old:new}, inplace=True)
                st.success(T['success']); st.rerun()
            if not is_pro: st.info(T['locked'])

        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)

        if st.session_state.show_balloon:
            st.balloons()
            st.session_state.show_balloon = False
        if st.session_state.show_download_msg:
            st.markdown(f"<div class='download-msg'>{T['download_success']}</div>", unsafe_allow_html=True)
            st.session_state.show_download_msg = False

        # FREE PLAN
        if st.session_state.plan=="free":
            col1,col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button("📄 Download CSV", csv, "clean_data.csv", key="dl_csv_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True

        # PRO PENDING - QR PEHLE, I PAID DABAO TAB DOWNLOAD
        elif user.get("status")!="PAID":
            st.error(f"🔒 {T['paid_msg']}")
            st.markdown(f"### {T['upi_text']}")
            upi_link = f"upi://pay?pa={UPI}&pn=VeriSame%20Pro&am={st.session_state.amt}&cu=INR"
            qr = qrcode.make(upi_link)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), width=280)
            st.code(UPI)

            if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary"):
                st.session_state.payment_clicked = True
                st.success(T['success_msg'])
                st.rerun()

            # I PAID DABANE KE BAAD HI DOWNLOAD AAYEGA
            if st.session_state.payment_clicked:
                col1,col2 = st.columns(2)
                csv = st.session_state.df_clean.to_csv(index=False).encode()
                if col1.download_button("📄 Download CSV", csv, "clean_data.csv", key="dl_csv_pending"):
                    st.session_state.show_balloon = True
                    st.session_state.show_download_msg = True
                excel = io.BytesIO()
                st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                if col2.download_button("📊 Download Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_pending"):
                    st.session_state.show_balloon = True
                    st.session_state.show_download_msg = True

        # PRO PAID
        else:
            col1,col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button("📄 Download CSV", csv, "clean_data.csv", key="dl_csv_paid"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button("📊 Download Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_paid"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
