import streamlit as st
import google.generativeai as genai
import json, os, io, qrcode
import pandas as pd
import re
from datetime import datetime, timedelta

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ===== VERISAME CHAT AI SETUP - GEMINI-PRO WALA =====
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    MODEL = genai.GenerativeModel(
        model_name="gemini-pro", # <-- YAHI BADLAV HAI, FREE ME CHALEGA
        system_instruction="""Tera naam VeriSame Chat AI hai. Tu VeriSame app ka official AI hai.
        Teri 2 kaam hain:
        1. Data Science Expert: CSV, Excel, Pandas, SQL, data cleaning sab ka baap. User ka data dekh ke bol kya saaf karna hai + code de.
        2. General Dost: Math, GK, cricket, duniya ki har basic cheez pata hai. 28x36 puchhe to 1008 bol de.
        Rules: HAMESHA Hinglish me baat kar. Har reply 'Bhai' se start kar. Technical terms English me rakh. Mana mat karna general sawal pe."""
    )
else:
    MODEL = None

if "vsai_messages" not in st.session_state:
    st.session_state.vsai_messages = []
# ===== AI SETUP END =====

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
ADMIN_PASS = "Sherni@123"
DB_FILE = "orders.json"

def save_db(d):
    with open(DB_FILE,"w") as f: json.dump(d, f, indent=2)

def load_db():
    if not os.path.exists(DB_FILE):
        save_db({})
    with open(DB_FILE,"r") as f:
        return json.load(f)

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
    "title":"VeriSame","subtitle":"The Fastest Way to Clean Your Data","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"MONTHLY","pro6_title":"6 MONTHS",
    "free_feat":["1000 Rows Lifetime","CSV + Excel Export","3 Basic Tools","30s Processing","Email Support"],
    "pro_feat":["Unlimited Rows","CSV + Excel Export","10 Premium AI Tools","3s Speed","Priority Support","No Watermark","Lifetime Updates"],
    "email_label":"Enter your email address","continue_btn":"Verify & Continue","upload_tab":"📤 Upload File","sample_tab":"🎯 Try Demo",
    "upload_text":"Drop CSV, Excel or JSON file here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview",
    "tools_menu":"AI Studio","back_btn":"← Back","download_title":"Export Data",
    "paid_msg":"Step 1: Pay ₹299 for 1 Month or ₹1499 for 6 Months via UPI. Step 2: Click I Paid button below. Step 3: Admin will approve. Step 4: Download unlocks",
    "upi_text":"Scan QR to Pay ₹{amount}","paid_btn":"Customer I Paid ₹{amount}","wait_approval":"⏳ Waiting for Admin Approval... Click I Paid after payment",
    "download_success":"🎉 Download Ready!","tab1":"Date & Nulls","tab2":"Email & Phone","tab3":"Text Tools",
    "tool1":"Smart Date Converter","tool2":"AI Fill Nulls","tool3":"Email Validator","tool4":"Phone Formatter","tool5":"Case Converter",
    "tool6":"Remove Symbols","tool7":"Bulk Rename","tool8":"Remove Duplicates","tool9":"Trim Spaces","tool10":"Spell Check",
    "select_col":"Select Columns","select_case":"Choose Case Type","apply_btn":"Apply","success":"Applied Successfully!",
    "admin_title":"Sherni Admin Panel","admin_pending":"Pending Approvals","admin_approve_btn":"Mark Paid - Unlock Customer Download",
    "admin_user":"Customer Email","admin_plan":"Plan","admin_expiry":"Valid Till","delete_btn":"Delete User","download_csv":"Download as CSV","download_excel":"Download as Excel",
    "expiry_warning":"⚠️ WARNING: Plan expires in {days} days! Renew now to avoid data loss"
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 25%, #c084fc 50%, #a855f7 75%, #9333ea 100%); background-size: 400% 400%; animation: aurora 15s ease infinite; padding-top: 0.3rem;}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}
.block-container {background: rgba(255,255,255,0.95); backdrop-filter: blur(25px) saturate(180%); border-radius: 28px; padding: 2rem; max-width: 1200px; margin: 0 auto; box-shadow: 0 30px 60px rgba(139,92,246,0.2); border: 1.5px solid rgba(255,255,255,0.4);}
@media (max-width: 768px) {
.block-container {padding: 1rem!important; border-radius: 20px!important;}
h1 {font-size: 2.2rem!important;}
.pricing-card {margin-bottom: 20px!important;}
}
h1,h2,h3,p,span,label,div,li {color: #000!important; font-weight: 600!important;}
h1 {font-weight: 800!important; font-size: 3.2rem!important; margin-bottom: 0.2rem!important; background: linear-gradient(90deg, #6b21a8, #9333ea, #c084fc, #a855f7, #6b21a8); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 3s linear infinite;}
@keyframes shine {0%{background-position: 0% center;} 100%{background-position: 200% center;}}
.subtitle {text-align: left; color: #000!important; font-size: 1.1rem!important; font-weight: 600!important; margin-bottom: 1rem!important;}
.logo-float {animation: float 3s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.anime-container {position: relative; width: 100%; min-height: 280px; border-radius: 25px; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.3);}
.anime-container img {width: 100%; height: 280px; object-fit: cover; object-position: center top; display: block;}
.pricing-card {
  position: relative;
  border-radius: 22px;
  padding: 1.6rem;
  background: rgba(255,255,255,0.88)!important;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(147,51,234,0.15), 0 2px 6px rgba(147,51,234,0.1);
  height: 100%;
  transform: translateZ(0);
  border: 2px solid #9333ea;
  clip-path: polygon(0% 3%, 3% 0%, 97% 0%, 100% 3%, 100% 97%, 97% 100%, 3% 100%, 0% 97%);
}
.pricing-card:hover {
  transform: translateY(-8px) scale(1.01);
  box-shadow: 0 20px 40px rgba(147,51,234,0.25), 0 8px 16px rgba(147,51,234,0.15);
}
.pricing-card h2 {font-size: 1.4rem!important; color: #6b21a8!important; margin-bottom: 0.5rem!important; font-weight: 700;}
.pricing-card h1 {font-size: 2.6rem!important; color: #6b21a8!important; margin: 0.5rem 0!important; font-weight: 800; -webkit-text-fill-color: #6b21a8!important;}
.pricing-card p {color: #000!important; font-size: 0.95rem!important; margin-bottom: 0.4rem!important;}
.stButton>button {border-radius: 14px; font-weight: 700; background: linear-gradient(90deg, #9333ea, #a855f7); color: white!important; border: none; padding: 13px 26px; width: 100%; box-shadow: 0 5px 18px rgba(147,51,234,0.4); transition: all 0.3s; cursor: pointer; font-size: 1rem!important; margin-top: 1rem;}
.stButton>button:hover {transform: translateY(-3px) scale(1.02); box-shadow: 0 10px 28px rgba(147,51,234,0.5);}
.stButton>button:disabled {background: #e0e0e0!important; color: #999!important; border: 2px dashed #ccc!important; cursor: not-allowed; box-shadow: none;}
.pro-banner {background: linear-gradient(135deg, #7e22ce, #a855f7, #d946ef); padding: 1.6rem; border-radius: 22px; color: white!important; text-align: center; margin: 1rem 0; border: 2px solid #9333ea; box-shadow: 0 8px 20px rgba(147,51,234,0.3);}
.pro-banner h2 {color: white!important;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.95); padding: 9px 17px; border-radius: 28px; margin: 4px; font-weight: 700; border: 2px solid #9333ea; color: #000!important; font-size: 0.92rem;}
div[data-testid="stTabs"] button p {color: #000!important; font-weight: 700!important; font-size: 1rem!important;}
div[data-testid="stTabs"] button[aria-selected="true"] p {color: #6b21a8!important; font-weight: 800!important; border-bottom: 3px solid #9333ea;}
div[data-testid="stTabs"] button {background: rgba(255,255,255,0.7)!important; backdrop-filter: blur(5px); border-radius: 12px; margin-right: 8px; border: 2px solid #9333ea;}
.stAlert,.stInfo,.stSuccess,.stError {color: #000!important; font-weight: 600!important; background: rgba(255,255,255,0.8)!important; backdrop-filter: blur(5px); border-radius: 12px; border: 2px solid #9333ea;}
.stDataFrame {background: rgba(255,255,255,0.9)!important;}
.stFileUploader {background: rgba(255,255,255,0.8)!important; border: 2px dashed #9333ea;}
.cherry {position: fixed; top: -10vh; color: #FFB7C5; font-size: 20px; animation: fall linear infinite; z-index: 9999; pointer-events: none;}
@keyframes fall {0%{transform: translateY(0vh) translateX(0vw) rotate(0deg); opacity: 1;} 100%{transform: translateY(110vh) translateX(10vw) rotate(360deg); opacity: 0;}}
</style>
<div class="cherry" style="left: 10%; animation-duration: 8s;">🌸</div>
<div class="cherry" style="left: 30%; animation-duration: 10s; animation-delay: 2s;">🌸</div>
<div class="cherry" style="left: 50%; animation-duration: 9s; animation-delay: 4s;">🌸</div>
<div class="cherry" style="left: 70%; animation-duration: 11s; animation-delay: 1s;">🌸</div>
<div class="cherry" style="left: 90%; animation-duration: 7s; animation-delay: 3s;">🌸</div>
""", unsafe_allow_html=True)

for key in ['plan','email','df_clean','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan'] else False

if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], use_container_width=True):
        for key in ['plan','email','df_clean','payment_clicked','sample_loaded','email_entered','days','selected_plan','admin_approved']:
            st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan'] else False
        st.rerun()

if st.session_state.email:
    user = load_db().get(st.session_state.email,{})
    st.sidebar.success(f"📧 {st.session_state.email}")

    # ===== SIDEBAR VERISAME CHAT AI - ASLI ERROR DIKHEGA =====
    if MODEL:
        st.sidebar.divider()
        st.sidebar.markdown("## 🤖 VeriSame Chat AI")
        st.sidebar.caption("CSV saaf karwao ya 28x36 puchho")
        sidebar_q = st.sidebar.text_area("Quick Doubt:", height=150, key="sidebar_ai_q")
        if st.sidebar.button("Ask AI", use_container_width=True, key="sidebar_ai_btn"):
            if sidebar_q:
                with st.sidebar:
                    with st.spinner("Socho..."):
                        try:
                            context = ""
                            if 'df_clean' in st.session_state and st.session_state.df_clean is not None:
                                context = f"\n\nUser ka current CSV:\nColumns: {list(st.session_state.df_clean.columns)}\nFirst 2 rows:\n{st.session_state.df_clean.head(2).to_string()}"
                            resp = MODEL.generate_content(sidebar_q + context)
                            st.success(f"**AI:** {resp.text}")
                        except Exception as e:
                            st.error(f"Gemini Error: {str(e)}") # ASLI ERROR
    # ===== SIDEBAR AI END =====

    if user.get("plan"):
        exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days
        st.session_state.plan = user.get("plan")
        st.session_state.amt = user.get("amt", 0)
        st.session_state.days = user.get("days", 0)
        st.session_state.admin_approved = user.get("status") == "PAID"

        if user.get("plan") == "free":
            st.sidebar.info("Plan: FREE LIFETIME")
        elif days_left <= 5 and days_left > 0:
            st.sidebar.error(T['expiry_warning'].format(days=days_left))
        elif days_left > 0:
            st.sidebar.info(f"Plan: {user['plan'].upper()}\nValid Till: {user['expiry']}\n{days_left} days left")
        else:
            st.sidebar.error("Plan Expired")
            st.session_state.admin_approved = False

col1, col2, col3 = st.columns([1.1, 2.2, 1.7])
with col1:
    st.markdown("""<div class="logo-float" style="width: 100%; min-height: 280px; display: flex; align-items: center; justify-content: center;"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width: 100%; height: auto; max-height: 280px; object-fit: contain;"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='margin-top: 5px; margin-bottom: 5px;'>VeriSame</h1>", unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{T["subtitle"]}</div>', unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="anime-container"><img src="https://i.postimg.cc/8zdnX54g/IMG-20260609-WA0012.jpg"></div>""", unsafe_allow_html=True)
st.markdown(f"<div class='pro-banner'><h2>💎 {T['pro_banner']}</h2><div>{''.join([f"<span class='tool-chip'>{tool}</span>" for tool in ['Smart Date','AI Fill','Email AI','Phone AI','Case','Clean','Rename','Dedup','Trim','Spell']])}</div></div>", unsafe_allow_html=True)

if st.query_params.get("admin"):
    admin_pass = st.query_params.get("admin")
    if admin_pass == ADMIN_PASS:
        st.title(T['admin_title'])
        data = load_db()
        pending = {e:i for e,i in data.items() if i.get("status")=="PENDING" and "@" in e}
        st.metric(T['admin_pending'], len(pending))
        if pending:
            st.subheader("⏳ Pending Approvals - Customer ne I Paid dabaya")
            for email,info in pending.items():
                amt = info.get('amt',0)
                days = 30 if amt==299 else 180
                plan_text = f"PRO Monthly ₹299 - {days} days" if amt==299 else f"PRO 6M ₹1499 - {days} days"
                col1, col2, col3 = st.columns([4,2,2])
                with col1:
                    st.markdown(f"<div class='pricing-card'><b>{T['admin_user']}:</b> {email}<br><b>{T['admin_plan']}:</b> {plan_text}<br><b>{T['admin_expiry']}:</b> {info['expiry']}</div>", unsafe_allow_html=True)
                with col2:
                    if st.button(T['admin_approve_btn'], key=f"verify_{email}", type="primary", use_container_width=True):
                        data[email]["status"] = "PAID"
                        save_db(data)
                        st.success(f"✓ {email} ko unlock kar diya! Ab download kar payega")
                        st.balloons()
                        st.rerun()
                with col3:
                    if st.button(T['delete_btn'], key=f"delete_{email}", use_container_width=True):
                        del data[email]
                        save_db(data)
                        st.error(f"✓ {email} deleted")
                        st.rerun()
        st.markdown("---")
        st.subheader("📊 All Users - Security Log")
        all_users = {e:i for e,i in data.items() if "@" in e}
        for email,info in all_users.items():
            status_color = "#059669" if info.get('status')=="PAID" else "#DC2626"
            status_text = "PAID - Download Unlocked" if info.get('status')=="PAID" else "PENDING - Waiting for approval"
            col1, col2 = st.columns([6,2])
            with col1:
                st.markdown(f"<div class='pricing-card'><b>{email}</b> | Plan: {info.get('plan','free').upper()} | ₹{info.get('amt',0)} | <span style='color:{status_color};font-weight:700'>{status_text}</span><br>Expiry: {info.get('expiry','N/A')}</div>", unsafe_allow_html=True)
            with col2:
                if st.button(T['delete_btn'], key=f"delete_all_{email}", use_container_width=True):
                    del data[email]
                    save_db(data)
                    st.error(f"✓ {email} deleted")
                    st.rerun()
        st.stop()

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        col1,col2,col3 = st.columns(3, gap="medium")
        with col1:
            st.markdown(f"""
            <div class='pricing-card'>
                <h2>{T['free_title']}</h2>
                <h1>FREE</h1>
                <p>Lifetime</p>
                <div>
                    {''.join([f'<p>✓ {f}</p>' for f in T['free_feat']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan = "free"
                st.rerun()

        with col2:
            st.markdown(f"""
            <div class='pricing-card' style='border: 3px solid #9333ea; box-shadow:0 15px 35px rgba(147,51,234,0.3)'>
                <p>⭐ POPULAR</p>
                <h2>{T['pro1_title']}</h2>
                <h1>₹299</h1>
                <p>30 Days - All Tools</p>
                <div>
                    {''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}
                </div>
            """, unsafe_allow_html=True)
            if st.button("Get Pro", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"
                st.session_state.amt = PRO_1M
                st.session_state.days = 30
                st.rerun()

        with col3:
            st.markdown(f"""
            <div class='pricing-card'>
                <h2>{T['pro6_title']}</h2>
                <h1>₹1499</h1>
                <p>180 Days - All Tools</p>
                <div>
                    {''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}
                </div>
            """, unsafe_allow_html=True)
            if st.button("Get Pro+", key="btn_pro6", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"
                st.session_state.amt = PRO_6M
                st.session_state.days = 180
                st.rerun()
    else:
        st.markdown(f"<h2>Enter your email to continue with {st.session_state.selected_plan.upper()}</h2>", unsafe_allow_html=True)
        email_input = st.text_input(T['email_label'], placeholder="your@email.com").lower().strip()
        if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
            if "@" in email_input and "." in email_input:
                st.session_state.email = email_input
                st.session_state.email_entered = True
                st.session_state.plan = st.session_state.selected_plan
                data = load_db()
                if st.session_state.selected_plan == "free":
                    expiry = (datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                    data[email_input] = {"plan":"free","status":"PAID","amt":0,"expiry":expiry,"created":str(datetime.now())}
                    save_db(data)
                    st.balloons()
                    st.rerun()
                else:
                    days = 30 if st.session_state.amt == 299 else 180
                    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                    data[email_input] = {"plan":"pro","status":"PENDING","amt":st.session_state.amt,"days":days,"expiry":expiry,"created":str(datetime.now())}
                    save_db(data)
                    st.rerun()
            else: st.error("Valid email required")
        st.stop()
else:
    tab1,tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    df = None
    with tab1:
        file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"])
        if file:
            try:
                df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file) if file.name.endswith(("xlsx","xls")) else pd.read_json(file)
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    with tab2:
        if st.button(T['sample_btn'], use_container_width=True):
            df = pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT SINGH"],"Email":["RAHUL@GMAIL.COM","bad@","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["one hundred","250","two thousand five hundred"]})

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
        st.dataframe(df_clean.head(10), use_container_width=True, height=300)

        all_cols = df_clean.columns.tolist()
        is_pro = st.session_state.plan == "pro"
        is_free = st.session_state.plan == "free"

        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
        with tab1:
            st.write(f"**{T['tool1']}** ✅ Free + Pro")
            date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date")
            if st.button(T['apply_btn'], key="btn_date", use_container_width=True):
                for col in date_cols: st.session_state.df_clean[col] = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool2']}** {'🔓 Pro Tool - Always Unlocked' if is_pro else 'Pro Only'}")
            fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_fill", use_container_width=True, disabled=is_free):
                st.session_state.df_clean[fill_cols] = st.session_state.df_clean[fill_cols].fillna("N/A")
                st.success(T['success'])
                st.rerun()
            if is_free:
                st.info("Unlock in Pro - ₹299 or ₹1499")

        with tab2:
            st.write(f"**{T['tool3']}** {'🔓 Pro Tool - Always Unlocked' if is_pro else '🔒 Pro Only'}")
            email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_email", use_container_width=True, disabled=is_free):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in email_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).lower() if re.match(pattern, str(x)) else "")
                st.success(T['success'])
                st.rerun()
            if is_free:
                st.info("Unlock in Pro - ₹299 or ₹1499")

            st.write(f"**{T['tool4']}** {'🔓 Pro Tool - Always Unlocked' if is_pro else '🔒 Pro Only'}")
            phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_phone", use_container_width=True, disabled=is_free):
                for col in phone_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'\D', '', regex=True)
                st.success(T['success'])
                st.rerun()
            if is_free:
                st.info("Unlock in Pro - ₹299 or ₹1499")

        with tab3:
            st.write(f"**{T['tool5']}** ✅ Free + Pro")
            case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
            if st.button(T['apply_btn'], key="btn_case", use_container_width=True):
                for col in case_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].str.upper() if case_opt == "Uppercase" else st.session_state.df_clean[col].str.lower() if case_opt == "Lowercase" else st.session_state.df_clean[col].str.title()
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool6']}** {'🔓 Pro Tool - Always Unlocked' if is_pro else '🔒 Pro Only'}")
            spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_spec", use_container_width=True, disabled=is_free):
                for col in spec_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'[^a-zA-Z0-9\s@.]', '', regex=True)
                st.success(T['success'])
                st.rerun()
            if is_free:
                st.info("Unlock in Pro - ₹299 or ₹1499")

            st.write(f"**{T['tool7']}** {'🔓 Pro Tool - Always Unlocked' if is_pro else '🔒 Pro Only'}")
            old = st.selectbox("Old column name", all_cols, key="sel_old", disabled=is_free)
            new = st.text_input("New column name", key="inp_new", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_rename", use_container_width=True, disabled=is_free) and new:
                st.session_state.df_clean.rename(columns={old: new}, inplace=True)
                st.success(T['success'])
                st.rerun()
            if is_free:
                st.info("Unlock in Pro - ₹299 or ₹1499")

            st.write(f"**{T['tool8']}** ✅ Free + Pro")
            if st.button(T['apply_btn'], key="btn_dedup", use_container_width=True):
                st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool9']}** ✅ Free + Pro")
            trim_cols = st.multiselect(T['select_col'], all_cols, key="ms_trim")
            if st.button(T['apply_btn'], key="btn_trim", use_container_width=True):
                for col in trim_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip()
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool10']}** {'🔓 Pro Tool - Always Unlocked' if is_pro else '🔒 Pro Only'}")
            spell_cols = st.multiselect(T['select_col'], all_cols, key="ms_spell", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_spell", use_container_width=True, disabled=is_free):
                for col in spell_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).replace("teh", "the").replace("recieve", "receive").title())
                st.success(T['success'])
                st.rerun()
            if is_free:
                st.info("Unlock in Pro - ₹299 or ₹1499")

        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)

        if st.session_state.show_balloon:
            st.balloons()
            st.session_state.show_balloon = False

        if st.session_state.plan == "free":
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button(T['download_csv'], csv, "verisame_clean.csv", mime="text/csv", key="dl_csv_free", use_container_width=True):
                st.session_state.show_balloon = True
                st.success("Downloaded! Check your Downloads folder")
                st.rerun()
            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_clean.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_free", use_container_width=True):
                st.session_state.show_balloon = True
                st.success("Downloaded! Check your Downloads folder")
                st.rerun()

        elif st.session_state.plan == "pro":
            if not st.session_state.admin_approved:
                st.warning(T['wait_approval'])
                st.markdown(f"### {T['upi_text'].format(amount=st.session_state.amt)}")
                upi_link = f"upi://pay?pa={UPI}&pn=VeriSame&am={st.session_state.amt}&cu=INR"
                qr = qrcode.make(upi_link)
                buf = io.BytesIO()
                qr.save(buf, format="PNG")
                st.image(buf.getvalue(), width=220)
                st.code(UPI)
                if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary", use_container_width=True):
                    st.session_state.payment_clicked = True
                    st.info("Payment clicked. Sherni verify karegi tab download unlock hoga")
                    st.rerun()
            else:
                col1, col2 = st.columns(2)
                csv = st.session_state.df_clean.to_csv(index=False).encode()
                if col1.download_button(T['download_csv'], csv, "verisame_pro.csv", mime="text/csv", key="dl_csv_paid", use_container_width=True):
                    st.session_state.show_balloon = True
                    st.success("Pro Download Success! Check your Downloads folder")
                    st.rerun()
                excel = io.BytesIO()
                st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_pro.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_paid", use_container_width=True):
                    st.session_state.show_balloon = True
                    st.success("Pro Download Success! Check your Downloads folder")
                    st.rerun()

        # ===== FIRST PAGE BOTTOM VERISAME CHAT AI - GEMINI-PRO WALA =====
        st.divider()
        st.markdown("### 🤖 VeriSame Chat AI - Tera Data ka Dost")
        st.caption("CSV saaf karwao, 28x36 puchho, sab bata dega")
        
        if not MODEL:
            st.warning("API Key missing bhai. Streamlit Secrets me GEMINI_API_KEY daal de.")
        else:
            # Chat history dikhao
            for msg in st.session_state.vsai_messages:
                with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
                    st.write(msg["content"])
            
            # Input box - ye bada dikhega
            if prompt := st.chat_input("Yaha likh bhai... CSV ke baare me ya 28x36"):
                st.session_state.vsai_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user", avatar="👤"):
                    st.write(prompt)
                
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("VeriSame Chat AI soch raha hai..."):
                        try:
                            # Agar CSV upload hai to context de do
                            context = ""
                            if 'df_clean' in st.session_state and st.session_state.df_clean is not None:
                                context = f"\n\nUser ka current CSV data:\nColumns: {list(st.session_state.df_clean.columns)}\nFirst 3 rows:\n{st.session_state.df_clean.head(3).to_string()}"
                            
                            full_prompt = prompt + context
                            response = MODEL.generate_content(full_prompt)
                            ai_text = response.text
                            st.write(ai_text)
                            st.session_state.vsai_messages.append({"role": "assistant", "content": ai_text})
                        except Exception as e:
                            error_msg = f"Gemini Error: {str(e)}"  # <-- YAHI BADLAV HAI
                            st.error(error_msg)
                            st.session_state.vsai_messages.append({"role": "assistant", "content": error_msg})
        # ===== BOTTOM AI END =====
