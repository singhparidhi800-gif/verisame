import streamlit as st
import json, os, io, qrcode
import pandas as pd
import re
from datetime import datetime, timedelta

# GOOGLE VERIFICATION TAG
st.markdown('<meta name="google-site-verification" content="r1wzMau1uinP14S7qbYJcmve44Ih7SEO-MdK9TZjW9A" />', unsafe_allow_html=True)

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
ADMIN_PASS = "Sherni@123"
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

LANG = {
    "English": {"title":"VeriSame","tagline":"The Fastest Way to Clean Your Data","pro_banner":"💎 UNLOCK 9 PREMIUM AI TOOLS","free_title":"FREE FOREVER","pro1_title":"MONTHLY PLAN","pro6_title":"6 MONTHS PLAN","free_feat":["1000 Rows Lifetime","CSV + Excel Export","Basic Tools","30s Processing","Email Support"],"pro_feat":["Unlimited Rows","CSV + Excel Export","9 Premium AI Tools","3s Speed","Priority Support","No Watermark","Free Updates"],"email_label":"Enter your email to start","continue_btn":"Continue →","upload_tab":"📤 Upload File","sample_tab":"🧪 Try Demo","upload_text":"Drag & Drop CSV, Excel or JSON here","sample_btn":"Load Sample Data","summary_title":"📊 Live Summary","rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Preview - First 10 Rows","tools_menu":"⚡ AI Studio","back_btn":"⬅️ Back to Plans","download_title":"📥 Export Clean Data","paid_msg":"Step 1: Scan QR & Pay. Step 2: Click I Paid. Step 3: Admin approves. Step 4: Download unlocks","upi_text":"Scan QR to Pay","paid_btn":"✓ I Have Paid ₹{amount}","success_msg":"Payment request sent! Admin will approve soon","download_success":"Download completed successfully! 🎉","locked":"🔒 PRO - Upgrade","tab1":"📅 Date & Nulls","tab2":"📧 Email & Phone","tab3":"✨ Text AI","tool1":"1. Smart Date","tool2":"2. AI Fill","tool3":"3. Email Validator","tool4":"4. Phone Formatter","tool5":"5. Case Converter","tool6":"6. Remove Symbols","tool7":"7. Bulk Rename","tool8":"8. Remove Duplicates","tool9":"9. Trim Spaces","select_col":"Select Columns","select_case":"Choose Case","apply_btn":"Apply","success":"Applied! ✅","expiry_warn":"⚠️ Your plan expires in {days} days! Renew now","pro_active":"🔥 Plan Active\n📅 Till {date}\n⏰ {days} days left","free_plan":"🆓 FREE Plan","expired":"⚠️ Plan Expired! Please pay again","delete_btn":"🗑️ Delete"},
    "Hindi": {"title":"VeriSame","tagline":"Data Saaf Karne Ka Sabse Fast Tareeka","pro_banner":"💎 9 PREMIUM AI TOOLS KHOLO","free_title":"FREE HAMESHA","pro1_title":"MONTHLY PLAN","pro6_title":"6 MONTH PLAN","free_feat":["1000 Row Lifetime","CSV + Excel Export","Basic Tools","30 Sec Processing","Email Support"],"pro_feat":["Unlimited Rows","CSV + Excel Export","9 Saare AI Tools","3 Sec Speed","Priority Support","No Watermark","Free Updates"],"email_label":"Email daalo shuru karne ke liye","continue_btn":"Aage →","upload_tab":"📤 File Upload","sample_tab":"🧪 Demo Data","upload_text":"CSV, Excel ya JSON yahan drag karo","sample_btn":"Sample Data Load","summary_title":"📊 Live Summary","rows":"Total Row","clean":"Saaf Row","dups":"Duplicate Hate","empty":"Khali Cell Thik","preview":"Preview - Sirf 10 Rows","tools_menu":"⚡ AI Studio","back_btn":"⬅️ Wapas Plans","download_title":"📥 Download Karo","paid_msg":"Step 1: QR Scan karke Pay karo. Step 2: I Paid dabao. Step 3: Admin approve karega. Step 4: Download khulega","upi_text":"QR Scan Karo","paid_btn":"✓ Pay Kar Diya ₹{amount}","success_msg":"Request bhej di! Admin approve karega","download_success":"Download ho gaya! 🎉","locked":"🔒 PRO - Upgrade Karo","tab1":"📅 Date & Khali","tab2":"📧 Email & Phone","tab3":"✨ Text AI","tool1":"1. Date Thik","tool2":"2. AI Fill","tool3":"3. Email Check","tool4":"4. Phone Saaf","tool5":"5. Case Badlo","tool6":"6. Symbol Hatao","tool7":"7. Naam Badlo","tool8":"8. Duplicate Hatao","tool9":"9. Space Saaf","select_col":"Column Chuno","select_case":"Case Chuno","apply_btn":"Lagao","success":"Ho Gaya! ✅","expiry_warn":"⚠️ Aapka plan {days} din me khatam! Abhi renew karo","pro_active":"🔥 Plan Active\n📅 {date} tak\n⏰ {days} din bache","free_plan":"🆓 FREE Plan","expired":"⚠️ Plan Expire! Dobara payment karo","delete_btn":"🗑️ Delete"}
}

# PINK PURPLE + WHITE TEXT + ULTRA ANIMATION + LOGO FIX
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"], p, div, span, label, h1, h2, h3, h4, h5, h6 {font-family: 'Poppins', sans-serif; color: #FFFFFF!important;}

.stApp {
    background: radial-gradient(circle at 20% 50%, rgba(255,20,147,0.25) 0%, transparent 50%),
                radial-gradient(circle at 80% 50%, rgba(138,43,226,0.25) 0%, transparent 50%),
                linear-gradient(135deg, #0D001A 0%, #1A0033 50%, #0D001A 100%);
    animation: auraGlow 6s ease-in-out infinite;
}

@keyframes auraGlow {
    0%,100% {filter: brightness(1) hue-rotate(0deg);}
    50% {filter: brightness(1.2) hue-rotate(20deg);}
}

/* FLOATING PARTICLES + STARS */
.stApp::before {
    content: '✨';
    position: fixed;
    top: 10%;
    left: 5%;
    font-size: 30px;
    opacity: 0.7;
    animation: starFloat 15s linear infinite;
    z-index: 0;
}
.stApp::after {
    content: '💎';
    position: fixed;
    bottom: 10%;
    right: 5%;
    font-size: 40px;
    opacity: 0.6;
    animation: starFloat 20s linear infinite reverse;
    z-index: 0;
}

@keyframes starFloat {
    0% {transform: translateY(0px) rotate(0deg);}
    50% {transform: translateY(-100px) rotate(180deg);}
    100% {transform: translateY(0px) rotate(360deg);}
}

.block-container {
    background: rgba(20,0,40,0.85);
    backdrop-filter: blur(25px) saturate(180%);
    border-radius: 50px;
    padding: 4rem;
    box-shadow: 0 0 80px rgba(255,20,147,0.4),
                inset 0 0 40px rgba(255,255,255,0.05);
    border: 2px solid rgba(255,20,147,0.5);
    position: relative;
    z-index: 1;
}

/* WHITE TEXT EVERYWHERE */
h1, h2, h3, p, label, div, span {
    color: #FFFFFF!important;
}

h1 {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900!important;
    background: linear-gradient(90deg, #FFFFFF, #FFB6C1, #E0AAFF, #FFFFFF);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 5rem!important;
    text-shadow: 0 0 50px rgba(255,255,255,0.6);
    animation: textGlow 3s ease-in-out infinite;
}

@keyframes textGlow {
    0%,100% {filter: brightness(1);}
    50% {filter: brightness(1.3);}
}

/* LOGO 1000PX FORCE - CSS SE BADA */
[data-testid="stImage"] img {
    width: 1000px!important;
    max-width: 100%!important;
    height: auto!important;
    filter: drop-shadow(0 0 30px rgba(255,20,147,0.8));
    animation: logoFloat 4s ease-in-out infinite;
}

@keyframes logoFloat {
    0%,100% {transform: translateY(0px) scale(1);}
    50% {transform: translateY(-15px) scale(1.05);}
}

.pricing-card h1 {
    font-size: 3.2rem!important;
    white-space: nowrap;
    margin: 10px 0;
}

.pricing-card p {
    text-align: center!important;
    color: #FFB6C1!important;
    font-weight: 700;
    min-height: 25px;
    margin-top: 10px;
}

.pro-banner {
    background: linear-gradient(135deg, rgba(255,20,147,0.3) 0%, rgba(138,43,226,0.3) 100%);
    backdrop-filter: blur(15px);
    padding: 60px;
    border-radius: 45px;
    color: #FFFFFF!important;
    text-align: center;
    margin: 50px 0;
    box-shadow: 0 0 80px rgba(255,20,147,0.5);
    border: 2px solid rgba(255,20,147,0.6);
    position: relative;
    overflow: hidden;
    animation: bannerPulse 4s ease-in-out infinite;
}

@keyframes bannerPulse {
    0%,100% {box-shadow: 0 0 80px rgba(255,20,147,0.5);}
    50% {box-shadow: 0 0 120px rgba(255,20,147,0.8);}
}

.pro-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% {transform: translateX(-100%) translateY(-100%) rotate(45deg);}
    100% {transform: translateX(100%) translateY(100%) rotate(45deg);}
}

/* 3D BOUNCE CARDS */
.pricing-card {
    border: 2px solid rgba(255,20,147,0.5);
    border-radius: 45px;
    padding: 40px;
    background: rgba(30,0,60,0.85);
    backdrop-filter: blur(15px);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    animation: card3D 5s ease-in-out infinite;
    transform-style: preserve-3d;
}

.pricing-card:nth-child(2) {animation-delay: 0.3s;}
.pricing-card:nth-child(3) {animation-delay: 0.6s;}

@keyframes card3D {
    0%,100% {transform: perspective(1000px) rotateX(5deg) translateZ(0px);}
    50% {transform: perspective(1000px) rotateX(0deg) translateZ(20px);}
}

.tool-chip {
    display: inline-block;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    padding: 16px 28px;
    border-radius: 60px;
    margin: 12px;
    font-weight: 700;
    border: 1px solid rgba(255,20,147,0.6);
    color: #FFFFFF!important;
    animation: chipRotate 3s ease-in-out infinite;
    box-shadow: 0 5px 20px rgba(255,20,147,0.4);
}

@keyframes chipRotate {
    0%,100% {transform: rotateY(0deg);}
    50% {transform: rotateY(10deg);}
}

.stButton>button {
    border-radius: 22px;
    font-weight: 700;
    background: linear-gradient(90deg, #FF1493, #DA70D6, #BA55D3, #FF1493);
    background-size: 300% 300%;
    color: #FFFFFF!important;
    border: none;
    font-size: 17px;
    padding: 14px 28px;
    width: 100%;
    box-shadow: 0 8px 25px rgba(255,20,147,0.6);
    animation: buttonGlow 2s ease-in-out infinite, gradientShift 3s ease infinite;
}

@keyframes buttonGlow {
    0%,100% {box-shadow: 0 8px 25px rgba(255,20,147,0.6);}
    50% {box-shadow: 0 15px 40px rgba(255,20,147,0.9);}
}

@keyframes gradientShift {
    0%,100% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
}

.download-msg {
    background: linear-gradient(90deg, #FF1493, #BA55D3, #FF1493);
    background-size: 200% 200%;
    color: white!important;
    padding: 25px;
    border-radius: 20px;
    margin-top: 20px;
    text-align: center;
    font-weight: 700;
    font-size: 19px;
    box-shadow: 0 10px 40px rgba(255,20,147,0.7);
    animation: pulse 2s ease-in-out infinite, gradientShift 2s ease infinite;
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
if 'sample_loaded' not in st.session_state: st.session_state.sample_loaded = False
if 'email_entered' not in st.session_state: st.session_state.email_entered = False

lang = st.sidebar.selectbox("🌐 Language", ["English", "Hindi"], index=0 if st.session_state.lang=="English" else 1, key="lang_select")
st.session_state.lang = lang
T = LANG[st.session_state.lang]

# BACK BUTTON SIDEBAR ME
if st.session_state.plan is not None or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], key="btn_back_side"):
        st.session_state.plan = None; st.session_state.email = ""; st.session_state.df_clean = None; st.session_state.payment_clicked = False; st.session_state.sample_loaded = False; st.session_state.email_entered = False
        st.rerun()

if st.session_state.email:
    user = load_db().get(st.session_state.email,{})
    st.sidebar.success(f"📧 {st.session_state.email}")

    if user.get("plan") == "pro":
        exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days

        if 0 < days_left <= 5:
            st.sidebar.warning(T['expiry_warn'].format(days=days_left))
            st.sidebar.info(T['pro_active'].format(date=user['expiry'], days=days_left))
        elif days_left > 5:
            st.sidebar.info(T['pro_active'].format(date=user['expiry'], days=days_left))
        else:
            st.sidebar.error(T['expired'])
            st.session_state.plan = None
            st.session_state.payment_clicked = False

    elif user.get("plan") == "free":
        st.sidebar.info(T['free_plan'])

# LOGO - CSS SE 1000PX FORCE HOGA
col_logo, col_title = st.columns([1,4])
with col_logo: st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png")
with col_title: st.title(T['title']); st.markdown(f"### {T['tagline']}")

st.markdown(f"<div class='pro-banner'><h2>{T['pro_banner']}</h2><div><span class='tool-chip'>📅 Smart Date</span><span class='tool-chip'>📈 AI Fill</span><span class='tool-chip'>📧 Email AI</span><span class='tool-chip'>📱 Phone AI</span><span class='tool-chip'>🔤 Case</span><span class='tool-chip'>🧹 Clean</span><span class='tool-chip'>✏️ Rename</span><span class='tool-chip'>🗑️ Dedup</span><span class='tool-chip'>✂️ Trim</span></div></div>", unsafe_allow_html=True)

# ADMIN
if st.query_params.get("admin") == ADMIN_PASS:
    st.title("🔐 Admin Panel")
    data = load_db()
    pending = [e for e,i in data.items() if i.get("status")=="PENDING" and "@" in e]
    st.metric("Pending Verifications", len(pending))
    all_users = [e for e in data.keys() if "@" in e]
    st.subheader(f"📧 Total Users: {len(all_users)}")
    for email in all_users:
        info = data.get(email,{})
        plan = info.get('plan','free')
        amt = info.get('amt',0)
        if plan == "free": plan_text = "FREE"; price_text = "FREE"; badge = "🆓"; duration = "Lifetime"
        elif amt == 299: plan_text = "MONTHLY"; price_text = "₹299"; badge = "📊"; duration = "1 Month"
        else: plan_text = "6 MONTHS"; price_text = "₹1499"; badge = "📈"; duration = "6 Months"
        st.markdown(f"<div style='background:rgba(40,0,80,0.9);padding:20px;border-radius:20px;margin:10px 0;border:2px solid #FF1493;color:white'>{badge} <b>Email:</b> {email} | <b>Plan:</b> {plan_text} | <b>Price:</b> {price_text} | <b>Status:</b> {info.get('status','N/A')}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("⏳ Pending Approvals")
    for email,info in data.items():
        if info.get("status")=="PENDING" and "@" in email:
            c1,c2,c3 = st.columns([3,2,1])
            amt = info.get('amt',0)
            if amt==299: plan_text="MONTHLY"; price_text="₹299"; badge="📊"
            else: plan_text="6 MONTHS"; price_text="₹1499"; badge="📈"
            c1.markdown(f"<div style='background:rgba(40,0,80,0.9);padding:20px;border-radius:20px;color:white'>{badge} <b>{email}</b></div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='background:rgba(40,0,80,0.9);padding:20px;border-radius:20px;color:white'><b>Plan:</b> {plan_text} | <b>{price_text}</b></div>", unsafe_allow_html=True)
            if c3.button("✅ Approve", key=f"admin_{email}", type="primary"):
                data[email]["status"]="PAID"; save_db(data); st.success("Approved"); st.rerun()
    st.stop()

# PLANS
if st.session_state.plan is None:
    col1,col2,col3 = st.columns(3, gap="large")
    with col1:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>🆓 {T['free_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center'>FREE</h1>", unsafe_allow_html=True)
        st.markdown("<p></p>", unsafe_allow_html=True)
        for f in T['free_feat']: st.write(f"✓ {f}")
        st.markdown("<div style='margin-top:auto'>", unsafe_allow_html=True)
        if st.button("Start FREE", key="btn_free", use_container_width=True, type="primary"):
            st.session_state.plan="free"; st.session_state.amt=0
            data = load_db()
            expiry = (datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
            data[st.session_state.email] = {"plan":"free","status":"PAID","amt":0,"expiry":expiry,"created":str(datetime.now())}
            save_db(data)
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='pricing-card' style='border-color:#FF1493'>", unsafe_allow_html=True)
        st.markdown("⭐ MOST POPULAR")
        st.markdown(f"<h2>📊 {T['pro1_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center'>₹{PRO_1M}</h1>", unsafe_allow_html=True)
        st.markdown("<p>Valid for 1 Month</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.write(f"✓ {f}")
        st.markdown("<div style='margin-top:auto'>", unsafe_allow_html=True)
        if st.button(f"Get Monthly", key="btn_pro1", use_container_width=True, type="primary"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_1M; st.session_state.days=30
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>📈 {T['pro6_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center'>₹{PRO_6M}</h1>", unsafe_allow_html=True)
        st.markdown("<p>Valid for 6 Months</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.write(f"✓ {f}")
        st.markdown("<div style='margin-top:auto'>", unsafe_allow_html=True)
        if st.button(f"Get 6 Months", key="btn_pro6", use_container_width=True, type="primary"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_6M; st.session_state.days=180
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

else:
    # EMAIL PEHLE
    if not st.session_state.email_entered:
        email_input = st.text_input(T['email_label']).lower().strip()
        if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
            if "@" in email_input and "." in email_input:
                st.session_state.email = email_input
                st.session_state.email_entered = True
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
            st.session_state.sample_loaded = False

    with tab2:
        if st.button(T['sample_btn'], key="btn_sample"):
            df = pd.DataFrame({
                "Date":["12/5/2024","","15-03-2023","12/5/2024"],
                "Name":[" RAHUL KUMAR ","priya sharma","AMIT SINGH"," RAHUL KUMAR "],
                "Email":["RAHUL@GMAIL.COM","bad email@","priya@email.com",""],
                "Phone":["98765-43210","9123 456 789","000123","+91 99887 76655"],
                "Salary":["one hundred","250","two thousand five hundred","one hundred"]
            })
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
                st.success(T['success'])

            st.write(f"**{T['tool2']}**")
            fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_fill", disabled=not is_pro):
                st.session_state.df_clean[fill_cols] = st.session_state.df_clean[fill_cols].fillna("N/A")
                st.success(T['success'])

        with tab2:
            st.write(f"**{T['tool3']}**")
            email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_email", disabled=not is_pro):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in email_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).lower() if re.match(pattern,str(x)) else "")
                st.success(T['success'])

            st.write(f"**{T['tool4']}**")
            phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_phone", disabled=not is_pro):
                for col in phone_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'\D','',regex=True)
                st.success(T['success'])

        with tab3:
            st.write(f"**{T['tool5']}**")
            case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase","Lowercase","Title Case"], key="sel_case")
            if st.button(T['apply_btn'], key="btn_case"):
                for col in case_cols:
                    if case_opt=="Uppercase": st.session_state.df_clean[col]=st.session_state.df_clean[col].str.upper()
                    elif case_opt=="Lowercase": st.session_state.df_clean[col]=st.session_state.df_clean[col].str.lower()
                    else: st.session_state.df_clean[col]=st.session_state.df_clean[col].str.title()
                st.success(T['success'])

            st.write(f"**{T['tool6']}**")
            spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_spec", disabled=not is_pro):
                for col in spec_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'[^a-zA-Z0-9\s@.]','',regex=True)
                st.success(T['success'])

            st.write(f"**{T['tool7']}**")
            old = st.selectbox("Old name", all_cols, key="sel_old", disabled=not is_pro)
            new = st.text_input("New name", key="inp_new", disabled=not is_pro)
            if st.button(T['apply_btn'], key="btn_rename", disabled=not is_pro) and new:
                st.session_state.df_clean.rename(columns={old:new}, inplace=True)
                st.success(T['success'])

            st.write(f"**{T['tool8']}**")
            if st.button(T['apply_btn'], key="btn_dedup", disabled=not is_pro):
                st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                st.success(T['success'])

            st.write(f"**{T['tool9']}**")
            trim_cols = st.multiselect(T['select_col'], all_cols, key="ms_trim")
            if st.button(T['apply_btn'], key="btn_trim"):
                for col in trim_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip()
                st.success(T['success'])

        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)

        # BALLOON SIRF DOWNLOAD KE BAAD
        if st.session_state.show_balloon:
            st.balloons()
            st.session_state.show_balloon = False
        if st.session_state.show_download_msg:
            st.markdown(f"<div class='download-msg'>{T['download_success']}</div>", unsafe_allow_html=True)
            st.session_state.show_download_msg = False

        # FREE PLAN - BALLOON DOWNLOAD KE BAAD
        if st.session_state.plan=="free":
            col1,col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button("📄 Download CSV", csv, "clean_data.csv", key="dl_csv_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True

            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button("📊 Download Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True

        # PRO PENDING - QR -> I PAID -> ADMIN APPROVE -> DOWNLOAD
        elif user.get("status")!="PAID":
            st.error(f"🔒 {T['paid_msg']}")
            st.markdown(f"### {T['upi_text']}")
            upi_link = f"upi://pay?pa={UPI}&pn=VeriSame&am={st.session_state.amt}&cu=INR"
            qr = qrcode.make(upi_link)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), width=280)
            st.code(UPI)

            if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary"):
                data = load_db()
                days = 30 if st.session_state.amt == 299 else 180
                expiry = (datetime.now()+timedelta(days=days)).strftime("%Y-%m-%d")
                data[st.session_state.email] = {"plan":"pro","status":"PENDING","amt":st.session_state.amt,"expiry":expiry,"created":str(datetime.now())}
                save_db(data)
                st.session_state.payment_clicked = True
                st.success(T['success_msg'])

            # I PAID KE BAAD BHI DOWNLOAD TAB TAK NAHI JAB TAK ADMIN APPROVE NA KARE
            if st.session_state.payment_clicked:
                st.info("⏳ Admin approval ka wait kar rahe hain...")

        # PRO PAID - ADMIN APPROVE KE BAAD HI DOWNLOAD + BALLOON
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
