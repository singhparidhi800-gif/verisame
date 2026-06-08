import streamlit as st
import json, os, io, qrcode
import pandas as pd
import re
from datetime import datetime, timedelta

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
    "English": {"title":"VeriSame","tagline":"The Fastest Way to Clean Your Data","pro_banner":"💎 UNLOCK 10 PREMIUM AI TOOLS","free_title":"FREE FOREVER","pro1_title":"MONTHLY PLAN","pro6_title":"6 MONTHS PLAN","free_feat":["1000 Rows Lifetime","CSV + Excel Export","2 Basic Tools","30s Processing","Email Support"],"pro_feat":["Unlimited Rows","CSV + Excel Export","10 Premium AI Tools","3s Speed","Priority Support","No Watermark","Free Updates"],"email_label":"Enter your email to start","continue_btn":"Continue →","upload_tab":"📤 Upload File","sample_tab":"🧪 Try Demo","upload_text":"Drag & Drop CSV, Excel or JSON here","sample_btn":"Load Sample Data","summary_title":"📊 Live Summary","rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Preview - First 10 Rows","tools_menu":"⚡ AI Studio","back_btn":"⬅️ Back to Plans","download_title":"📥 Export Clean Data","paid_msg":"Step 1: Scan QR & Pay. Step 2: Click I Paid. Step 3: Sherani will approve. Step 4: Download unlocks","upi_text":"Scan QR to Pay","paid_btn":"✓ I Have Paid ₹{amount}","success_msg":"Payment request sent! Wait for Sherani approval","download_success":"Download completed successfully! 🎉","locked":"🔒 PRO ONLY - Upgrade to unlock","tab1":"📅 Date & Nulls","tab2":"📧 Email & Phone","tab3":"✨ Text AI","tool1":"1. Smart Date","tool2":"2. AI Fill","tool3":"3. Email Validator","tool4":"4. Phone Formatter","tool5":"5. Case Converter","tool6":"6. Remove Symbols","tool7":"7. Bulk Rename","tool8":"8. Remove Duplicates","tool9":"9. Trim Spaces","tool10":"10. Spell Check","select_col":"Select Columns","select_case":"Choose Case","apply_btn":"Apply","success":"Applied! ✅","expiry_warn":"⚠️ EXPIRES IN {days} DAYS! RENEW NOW","pro_active":"🔥 Plan Active\n📅 Valid Till: {date}\n⏰ {days} days left","free_plan":"🆓 FREE Plan - Lifetime","expired":"⚠️ PLAN EXPIRED! PAY AGAIN","delete_btn":"🗑️ Delete","admin_title":"🔐 Sherani Secret Dashboard","admin_pending":"Pending Approvals","admin_approve_btn":"✅ Approve","admin_user":"Customer","admin_plan":"Plan","admin_expiry":"Valid Till","admin_status":"Status","language":"🌐 Language"},
    "Hindi": {"title":"VeriSame","tagline":"Data Saaf Karne Ka Sabse Fast Tareeka","pro_banner":"💎 10 PREMIUM AI TOOLS KHOLO","free_title":"FREE HAMESHA","pro1_title":"MONTHLY PLAN","pro6_title":"6 MONTH PLAN","free_feat":["1000 Row Lifetime","CSV + Excel Export","2 Basic Tools","30 Sec Processing","Email Support"],"pro_feat":["Unlimited Rows","CSV + Excel Export","10 Saare AI Tools","3 Sec Speed","Priority Support","No Watermark","Free Updates"],"email_label":"Email daalo shuru karne ke liye","continue_btn":"Aage →","upload_tab":"📤 File Upload","sample_tab":"🧪 Demo Data","upload_text":"CSV, Excel ya JSON yahan drag karo","sample_btn":"Sample Data Load","summary_title":"📊 Live Summary","rows":"Total Row","clean":"Saaf Row","dups":"Duplicate Hate","empty":"Khali Cell Thik","preview":"Preview - Sirf 10 Rows","tools_menu":"⚡ AI Studio","back_btn":"⬅️ Wapas Plans","download_title":"📥 Download Karo","paid_msg":"Step 1: QR Scan karke Pay karo. Step 2: I Paid dabao. Step 3: Sherani approve karegi. Step 4: Download khulega","upi_text":"QR Scan Karo","paid_btn":"✓ Pay Kar Diya ₹{amount}","success_msg":"Request bhej di! Sherani approve karegi","download_success":"Download ho gaya! 🎉","locked":"🔒 PRO ONLY - Upgrade Karo","tab1":"📅 Date & Khali","tab2":"📧 Email & Phone","tab3":"✨ Text AI","tool1":"1. Date Thik","tool2":"2. AI Fill","tool3":"3. Email Check","tool4":"4. Phone Saaf","tool5":"5. Case Badlo","tool6":"6. Symbol Hatao","tool7":"7. Naam Badlo","tool8":"8. Duplicate Hatao","tool9":"9. Space Saaf","tool10":"10. Spelling Thik","select_col":"Column Chuno","select_case":"Case Chuno","apply_btn":"Lagao","success":"Ho Gaya! ✅","expiry_warn":"⚠️ {days} DIN ME KHATAM! ABHI RENEW KARO","pro_active":"🔥 Plan Active\n📅 Valid Till: {date}\n⏰ {days} din bache","free_plan":"🆓 FREE Plan - Lifetime","expired":"⚠️ PLAN EXPIRE! DOBARA PAYMENT KARO","delete_btn":"🗑️ Delete","admin_title":"🔐 Sherani Secret Dashboard","admin_pending":"Pending Approvals","admin_approve_btn":"✅ Approve Karo","admin_user":"Customer","admin_plan":"Plan","admin_expiry":"Valid Till","admin_status":"Status","language":"🌐 Language"}
}

# BEAUTIFUL ANIME PINK PURPLE CSS + DROPDOWN FIX
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Poppins:wght@400;600;700&display=swap');
html, body, [class*="css"], p, div, span, label, h1, h2, h3, h4, h5, h6 {font-family: 'Poppins', sans-serif; color: #FFFFFF!important;}
.stApp {background: radial-gradient(circle at 20% 50%, rgba(255,20,147,0.4) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(138,43,226,0.4) 0%, transparent 50%), linear-gradient(135deg, #0D001A 0%, #1A0033 50%, #0D001A 100%); animation: auraGlow 6s ease-in-out infinite;}
@keyframes auraGlow {0%,100% {filter: brightness(1) hue-rotate(0deg);} 50% {filter: brightness(1.3) hue-rotate(30deg);}}
.stApp::before {content: '✨💎⭐🌸🦋'; position: fixed; top: 8%; left: 3%; font-size: 35px; opacity: 0.9; animation: animeFloat 10s ease-in-out infinite; z-index: 9999; letter-spacing: 50px;}
.stApp::after {content: '⚡🔮🌟💖🌹'; position: fixed; bottom: 8%; right: 3%; font-size: 45px; opacity: 0.8; animation: animeFloat 13s ease-in-out infinite reverse; z-index: 9999; letter-spacing: 50px;}
@keyframes animeFloat {0% {transform: translateY(0px) rotate(0deg) scale(1);} 25% {transform: translateY(-70px) rotate(90deg) scale(1.3);} 50% {transform: translateY(-140px) rotate(180deg) scale(1.5);} 75% {transform: translateY(-70px) rotate(270deg) scale(1.3);} 100% {transform: translateY(0px) rotate(360deg) scale(1);}}
.block-container {background: rgba(25,0,50,0.9); backdrop-filter: blur(30px) saturate(200%); border-radius: 60px; padding: 4.5rem; box-shadow: 0 0 100px rgba(255,20,147,0.6), inset 0 0 50px rgba(255,255,255,0.1); border: 3px solid rgba(255,20,147,0.7); position: relative; z-index: 1;}
h1 {font-family: 'Orbitron', sans-serif; font-weight: 900!important; background: linear-gradient(90deg, #FFFFFF, #FFB6C1, #E0AAFF, #FF69B4, #FFD700, #FFFFFF); background-size: 500% 500%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 5.5rem!important; text-shadow: 0 0 60px rgba(255,255,255,0.8); animation: textGlow 3s ease-in-out infinite, gradientShift 4s ease infinite;}
@keyframes gradientShift {0%,100% {background-position: 0% 50%;} 50% {background-position: 100% 50%;}}
@keyframes textGlow {0%,100% {filter: brightness(1) drop-shadow(0 0 25px rgba(255,255,255,0.6));} 50% {filter: brightness(1.5) drop-shadow(0 0 50px rgba(255,182,193,0.9));}}
[data-testid="stImage"] img {width: 1000px!important; max-width: 100%!important; height: auto!important; filter: drop-shadow(0 0 50px rgba(255,20,147,1)); animation: logoFloat 4s ease-in-out infinite;}
@keyframes logoFloat {0%,100% {transform: translateY(0px) scale(1) rotateY(0deg);} 50% {transform: translateY(-20px) scale(1.1) rotateY(8deg);}}
.pricing-card h1 {font-size: 2.8rem!important; white-space: nowrap!important; overflow: hidden; letter-spacing: -1px; margin: 12px 0;}
.pricing-card p {text-align: center!important; color: #FFB6C1!important; font-weight: 700; min-height: 28px; margin-top: 12px; font-size: 18px;}
[data-testid="stFileUploader"] {background: rgba(255,255,255,0.98)!important; border-radius: 18px!important; border: 3px solid rgba(255,20,147,0.6)!important;}
[data-testid="stFileUploader"] * {color: #000!important; font-weight: 600;}
[data-testid="stFileUploader"] label {color: #FFFFFF!important;}
div[data-baseweb="select"] {z-index: 99999!important; position: relative;}
.stMultiSelect > div > div {background: rgba(255,255,255,0.98)!important; border-radius: 15px!important; border: 3px solid rgba(255,20,147,0.7)!important;}
.stMultiSelect [data-baseweb="select"] * {color: #000!important; font-weight: 700!important; font-size: 16px;}
.stMultiSelect [data-baseweb="tag"] {background: linear-gradient(90deg, #FF1493, #BA55D3)!important; color: white!important; border-radius: 20px!important;}
.stMultiSelect [data-baseweb="tag"] * {color: white!important; font-weight: 700;}
ul[data-baseweb="menu"] {z-index: 99999!important; position: fixed!important; background: white!important; border-radius: 15px!important; box-shadow: 0 15px 50px rgba(255,20,147,0.6)!important; max-height: 350px!important; overflow-y: auto!important; border: 2px solid #FF1493;}
ul[data-baseweb="menu"] li {color: #000!important; background: white!important; font-weight: 700!important; padding: 14px 18px!important; cursor: pointer; font-size: 16px;}
ul[data-baseweb="menu"] li:hover {background: linear-gradient(90deg, rgba(255,20,147,0.3), rgba(186,85,211,0.3))!important;}
.stSelectbox > div > div {background: rgba(255,255,255,0.98)!important; color: #000!important; border-radius: 12px!important; border: 2px solid #FF1493;}
.stSelectbox > div > div > div {color: #000!important; font-weight: 700;}
.expiry-alert {background: linear-gradient(90deg, #FF0000, #FF1493, #FFD700, #FF1493, #FF0000); background-size: 400% 400%; color: white!important; padding: 25px; border-radius: 25px; text-align: center; font-weight: 900; font-size: 20px; box-shadow: 0 0 50px rgba(255,0,0,0.9); animation: redAlert 1s ease-in-out infinite, gradientShift 2s ease infinite; border: 4px solid #FFD700;}
@keyframes redAlert {0%,100% {transform: scale(1); box-shadow: 0 0 50px rgba(255,0,0,0.9);} 50% {transform: scale(1.08); box-shadow: 0 0 80px rgba(255,0,0,1);}}
.pro-banner {background: linear-gradient(135deg, rgba(255,20,147,0.4) 0%, rgba(138,43,226,0.4) 100%); backdrop-filter: blur(20px); padding: 70px; border-radius: 50px; color: #FFFFFF!important; text-align: center; margin: 60px 0; box-shadow: 0 0 100px rgba(255,20,147,0.7); border: 3px solid rgba(255,20,147,0.8); animation: bannerPulse 4s ease-in-out infinite;}
@keyframes bannerPulse {0%,100% {box-shadow: 0 0 100px rgba(255,20,147,0.6);} 50% {box-shadow: 0 0 160px rgba(255,20,147,1);}}
.pricing-card {border: 3px solid rgba(255,20,147,0.7); border-radius: 50px; padding: 45px; background: rgba(35,0,70,0.95); backdrop-filter: blur(20px); height: 100%; display: flex; flex-direction: column; justify-content: space-between; animation: card3D 5s ease-in-out infinite; transform-style: preserve-3d;}
@keyframes card3D {0%,100% {transform: perspective(1200px) rotateX(6deg) translateZ(0px);} 50% {transform: perspective(1200px) rotateX(0deg) translateZ(30px);}}
.tool-chip {display: inline-block; background: linear-gradient(90deg, rgba(255,255,255,0.15), rgba(255,182,193,0.15)); backdrop-filter: blur(15px); padding: 18px 32px; border-radius: 70px; margin: 14px; font-weight: 800; border: 2px solid rgba(255,20,147,0.8); color: #FFFFFF!important; animation: chipRotate 3s ease-in-out infinite; box-shadow: 0 8px 30px rgba(255,20,147,0.6); font-size: 16px;}
@keyframes chipRotate {0%,100% {transform: rotateY(0deg) scale(1);} 50% {transform: rotateY(20deg) scale(1.08);}}
.stButton>button {border-radius: 25px; font-weight: 800; background: linear-gradient(90deg, #FF1493, #DA70D6, #BA55D3, #FF69B4, #FF1493); background-size: 400% 400%; color: #FFFFFF!important; border: none; font-size: 18px; padding: 16px 32px; width: 100%; box-shadow: 0 10px 35px rgba(255,20,147,0.8); animation: buttonGlow 2s ease-in-out infinite, gradientShift 3s ease infinite; letter-spacing: 1px;}
@keyframes buttonGlow {0%,100% {box-shadow: 0 10px 35px rgba(255,20,147,0.8);} 50% {box-shadow: 0 25px 60px rgba(255,20,147,1);}}
.download-msg {background: linear-gradient(90deg, #FF1493, #BA55D3, #FFD700, #FF1493); background-size: 300% 300%; color: white!important; padding: 30px; border-radius: 25px; margin-top: 25px; text-align: center; font-weight: 800; font-size: 21px; box-shadow: 0 15px 50px rgba(255,20,147,0.9); animation: pulse 2s ease-in-out infinite, gradientShift 2s ease infinite;}
.locked-tool {opacity: 0.4; pointer-events: none; filter: grayscale(0.9);}
.admin-card {background: rgba(40,0,80,0.95); padding: 25px; border-radius: 25px; margin: 15px 0; border: 3px solid #FF1493; box-shadow: 0 0 40px rgba(255,20,147,0.5);}
</style>
""", unsafe_allow_html=True)

# SESSION - EMAIL YAAD RAHEGA
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

# LANGUAGE SELECT TOP RIGHT
lang_col = st.columns([8,2])[1]
with lang_col:
    lang = st.selectbox(T['language'] if 'language' in T else "🌐 Language", ["English", "Hindi"], index=0 if st.session_state.lang=="English" else 1, key="lang_top")
    st.session_state.lang = lang
T = LANG[st.session_state.lang]

# BACK BUTTON SIDEBAR
if st.session_state.plan is not None or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], key="btn_back_side"):
        st.session_state.plan = None; st.session_state.email = ""; st.session_state.df_clean = None; st.session_state.payment_clicked = False; st.session_state.sample_loaded = False; st.session_state.email_entered = False
        st.rerun()

# EMAIL YAAD RAKHO - EXPIRED NA HO TO PLAN ACTIVE
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

# ANIME CHARACTER + LOGO
col_anime, col_logo, col_title = st.columns([1,2,4])
with col_anime:
    st.image("https://i.ibb.co/Vps2R8np/anime-girl-pink-hair-beautiful-anime-girl.png", width=220)
with col_logo:
    st.image("https://i.ibb.co/W43B7drG/VeriSame-1.png")
with col_title:
    st.title(T['title']); st.markdown(f"### {T['tagline']}")

st.markdown(f"<div class='pro-banner'><h2>{T['pro_banner']}</h2><div><span class='tool-chip'>📅 Smart Date</span><span class='tool-chip'>📈 AI Fill</span><span class='tool-chip'>📧 Email AI</span><span class='tool-chip'>📱 Phone AI</span><span class='tool-chip'>🔤 Case</span><span class='tool-chip'>🧹 Clean</span><span class='tool-chip'>✏️ Rename</span><span class='tool-chip'>🗑️ Dedup</span><span class='tool-chip'>✂️ Trim</span><span class='tool-chip'>📝 Spell</span></div></div>", unsafe_allow_html=True)

# ADMIN PANEL - SHERANI KE LIYE - EMAIL NAHI DALNA PADEGA
if st.query_params.get("admin") == ADMIN_PASS:
    st.title(T['admin_title'])
    st.warning("⚠️ Sirf Sherani dekh sakti hai")

    data = load_db()
    pending = {e:i for e,i in data.items() if i.get("status")=="PENDING" and "@" in e}

    st.metric(T['admin_pending'], len(pending))

    if pending:
        st.subheader("⏳ Pending Payments - Bas Approve Daba")
        for email,info in pending.items():
            amt = info.get('amt',0)
            days = 30 if amt==299 else 180
            plan_text = f"PRO {T['pro1_title']} ₹299 - {days} din" if amt==299 else f"PRO {T['pro6_title']} ₹1499 - {days} din"

            col1, col2, col3 = st.columns([4,3,2])
            with col1:
                st.markdown(f"<div class='admin-card'><b>{T['admin_user']}:</b> {email}<br><b>{T['admin_plan']}:</b> {plan_text}<br><b>{T['admin_expiry']}:</b> {info['expiry']}<br><b>{T['admin_status']}:</b> {info['status']}</div>", unsafe_allow_html=True)
            with col2:
                st.write("")
            with col3:
                if st.button(T['admin_approve_btn'], key=f"approve_{email}", type="primary", use_container_width=True):
                    data[email]["status"] = "PAID"
                    save_db(data)
                    st.success(f"✅ {email} approved! Customer ab download kar sakta hai")
                    st.balloons()
                    st.rerun()

    st.markdown("---")
    st.subheader("📊 All Users - FREE/PRO Sab")
    all_users = {e:i for e,i in data.items() if "@" in e}
    for email,info in all_users.items():
        status = info.get('status','N/A')
        plan = info.get('plan','free')
        amt = info.get('amt',0)
        expiry = info.get('expiry','N/A')

        if plan == "free": badge = "🆓 FREE"; color = "gray"
        elif amt == 299: badge = "📊 PRO 1M"; color = "green"
        else: badge = "📈 PRO 6M"; color = "gold"

        status_color = "lightgreen" if status=="PAID" else "orange"
        st.markdown(f"<div style='background:rgba(40,0,80,0.9);padding:20px;border-radius:20px;margin:10px 0;border-left:8px solid {color};color:white'><b>{email}</b> | {badge} | Status: <span style='color:{status_color};font-weight:800'>{status}</span> | Valid: {expiry}</div>", unsafe_allow_html=True)
    st.stop()

# PLANS
if st.session_state.plan is None:
    col1,col2,col3 = st.columns(3, gap="large")
    with col1:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>🆓 {T['free_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center'>FREE</h1>", unsafe_allow_html=True)
        st.markdown("<p>Lifetime</p>", unsafe_allow_html=True)
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
        st.markdown("<div class='pricing-card' style='border-color:#FF1493;box-shadow:0 0 60px rgba(255,20,147,0.8)'>", unsafe_allow_html=True)
        st.markdown("⭐ MOST POPULAR")
        st.markdown(f"<h2>📊 {T['pro1_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center'>₹{PRO_1M}</h1>", unsafe_allow_html=True)
        st.markdown("<p>Valid for 1 Month - 30 Days</p>", unsafe_allow_html=True)
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
        st.markdown("<p>Valid for 6 Months - 180 Days</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.write(f"✓ {f}")
        st.markdown("<div style='margin-top:auto'>", unsafe_allow_html=True)
        if st.button(f"Get 6 Months", key="btn_pro6", use_container_width=True, type="primary"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_6M; st.session_state.days=180
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

else:
    if not st.session_state.email_entered:
        email_input = st.text_input(T['email_label']).lower().strip()
        if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
            if "@" in email_input and "." in email_input:
                st.session_state.email = email_input
                st.session_state.email_entered = True

                # CHECK KARO PEHLE SE PLAN HAI KYA
                data = load_db()
                if email_input in data and data[email_input].get("status")=="PAID":
                    exp_date = datetime.strptime(data[email_input]["expiry"], "%Y-%m-%d")
                    if exp_date > datetime.now():
                        st.session_state.plan = data[email_input]["plan"]
                        st.session_state.amt = data[email_input].get("amt", 0)
                        st.success(f"Welcome back! Plan active hai till {data[email_input]['expiry']}")

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
                "Salary":["one hundred","250","two thousand five hundred","one hundred"],
                "City":["mumbai","DELHI","bangalore","chennai"]
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
        with c1: st.metric(T['rows'], orig_len)
        with c2: st.metric(T['clean'], len(df_clean))
        with c3: st.metric(T['dups'], orig_len-len(df_clean))
        with c4: st.metric(T['empty'], df.isna().sum().sum())

        st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
        st.caption(T['preview'])
        st.dataframe(df_clean.head(10), use_container_width=True, height=380)

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
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(
                        lambda x: str(x).lower() if re.match(pattern, str(x)) else ""
                    )
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
                    if case_opt == "Uppercase":
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].str.upper()
                    elif case_opt == "Lowercase":
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].str.lower()
                    else:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].str.title()
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
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(
                        lambda x: str(x).replace("teh", "the").replace("recieve", "receive").title()
                    )
                st.success(T['success'])

        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)

        # BALLOON + DOWNLOAD SUCCESS MSG
        if st.session_state.show_balloon:
            st.balloons()
            st.session_state.show_balloon = False
        if st.session_state.show_download_msg:
            st.markdown(f"<div class='download-msg'>{T['download_success']}</div>", unsafe_allow_html=True)
            st.session_state.show_download_msg = False

        # FREE PLAN - SIRF 2 TOOLS + DOWNLOAD
        if st.session_state.plan == "free":
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button("📄 Download CSV", csv, "clean_data.csv", key="dl_csv_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True

            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button("📊 Download Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True

        # PRO PENDING - QR -> I PAID -> SHERANI APPROVE -> DOWNLOAD
        elif user.get("status")!= "PAID":
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
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                data[st.session_state.email] = {
                    "plan": "pro",
                    "status": "PENDING",
                    "amt": st.session_state.amt,
                    "expiry": expiry,
                    "created": str(datetime.now())
                }
                save_db(data)
                st.session_state.payment_clicked = True
                st.success(T['success_msg'])

            if st.session_state.payment_clicked:
                st.info("⏳ Sherani approval ka wait kar rahe hain...")

        # PRO PAID - ADMIN APPROVE KE BAAD HI DOWNLOAD + BALLOON
        else:
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button("📄 Download CSV", csv, "clean_data.csv", key="dl_csv_paid"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True

            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button("📊 Download Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_paid"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
