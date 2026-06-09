import streamlit as st
import json, os, io, qrcode, hashlib, random
import pandas as pd
import re
from datetime import datetime, timedelta

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
ADMIN_PASS_HASH = hashlib.sha256("Sherni@123".encode()).hexdigest()
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
    "title":"VeriSame","tagline":"Intelligent Data Cleaning Platform","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"MONTHLY","pro6_title":"6 MONTHS",
    "free_feat":["1000 Rows Lifetime","CSV + Excel Export","2 Basic Tools","30s Processing","Email Support"],
    "pro_feat":["Unlimited Rows","CSV + Excel Export","10 Premium AI Tools","3s Speed","Priority Support","No Watermark","Lifetime Updates"],
    "email_label":"Enter Email for OTP Verification","continue_btn":"Verify & Continue","upload_tab":"Upload File","sample_tab":"Try Demo",
    "upload_text":"Drop CSV, Excel or JSON here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview",
    "tools_menu":"AI Studio","back_btn":"← Back","download_title":"Export Data",
    "paid_msg":"Step 1: Pay via UPI. Step 2: Click I Paid. Step 3: Admin Approval. Step 4: Download Unlocks",
    "upi_text":"Scan to Pay","paid_btn":"I Have Paid ₹{amount}","success_msg":"Payment Submitted! Awaiting Approval",
    "download_success":"Download Ready!","locked":"Upgrade to Pro to Unlock","tab1":"Date & Nulls","tab2":"Email & Phone","tab3":"Text Tools",
    "tool1":"Smart Date","tool2":"AI Fill Nulls","tool3":"Email Validator","tool4":"Phone Formatter","tool5":"Case Converter",
    "tool6":"Remove Symbols","tool7":"Bulk Rename","tool8":"Remove Duplicates","tool9":"Trim Spaces","tool10":"Spell Check",
    "select_col":"Select Columns","select_case":"Choose Case","apply_btn":"Apply","success":"Applied Successfully!",
    "expiry_warn":"Expires in {days} days!","pro_active":"Plan Active\nValid Till: {date}\n{days} days left","free_plan":"FREE Plan Active",
    "expired":"Plan Expired","admin_title":"Sherani Admin Panel","admin_pending":"Pending Approvals","admin_approve_btn":"Verify & Approve",
    "admin_user":"Email","admin_plan":"Plan","admin_expiry":"Valid Till","admin_status":"Status","download_btn":"Download Now"
}

# BEAUTIFUL GLASSMORPHISM CSS - PURPLE PINK AURORA
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #667eea 100%); background-size: 400% 400%; animation: aurora 15s ease infinite; padding-top: 0.5rem;}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}
.block-container {background: rgba(255,255,255,0.85); backdrop-filter: blur(20px) saturate(180%); border-radius: 24px; padding: 2rem; max-width: 1100px; margin: 0 auto; box-shadow: 0 25px 50px rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.3);}
h1 {font-weight: 800!important; background: linear-gradient(90deg, #7C3AED, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem!important; margin-bottom: 0.3rem!important;}
h2, h3 {color: #581C87!important; font-weight: 700!important; margin-top: 1rem!important; margin-bottom: 0.6rem!important;}
.stMarkdown p {color: #6B7280!important; margin-bottom: 0.3rem!important;}
.pricing-card {border: 1.5px solid rgba(236,72,153,0.3); border-radius: 20px; padding: 1.5rem; background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(124,58,237,0.1);}
.pricing-card:hover {transform: translateY(-6px); box-shadow: 0 20px 40px rgba(236,72,153,0.25); border-color: #EC4899;}
.pricing-card h2 {font-size: 1.3rem!important; color: #581C87!important; margin-bottom: 0.5rem!important;}
.pricing-card h1 {font-size: 2.5rem!important; background: linear-gradient(90deg, #7C3AED, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0.5rem 0!important;}
.stButton>button {border-radius: 12px; font-weight: 600; background: linear-gradient(90deg, #8B5CF6, #EC4899); color: white!important; border: none; padding: 12px 24px; width: 100%; box-shadow: 0 4px 15px rgba(139,92,246,0.4); transition: all 0.3s;}
.stButton>button:hover {transform: translateY(-3px); box-shadow: 0 8px 25px rgba(236,72,153,0.5);}
.stFileUploader {border-radius: 16px; border: 2px dashed #C084FC; background: rgba(250,245,255,0.8);}
.stDataFrame {border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(139,92,246,0.1);}
.pro-banner {background: linear-gradient(135deg, rgba(124,58,237,0.9), rgba(236,72,153,0.9)); backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 20px; color: white!important; text-align: center; margin: 1rem 0; border: 1px solid rgba(255,255,255,0.3);}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px); padding: 8px 16px; border-radius: 25px; margin: 4px; font-weight: 600; border: 1px solid rgba(255,255,255,0.3); color: white!important; font-size: 0.9rem;}
.download-msg {background: linear-gradient(90deg, #7C3AED, #EC4899); color: white!important; padding: 16px; border-radius: 12px; margin-top: 1rem; text-align: center; font-weight: 600; box-shadow: 0 8px 20px rgba(236,72,153,0.4);}
.admin-card {background: rgba(255,255,255,0.95); padding: 1.2rem; border-radius: 16px; margin: 0.6rem 0; border: 1.5px solid rgba(236,72,153,0.3); box-shadow: 0 4px 12px rgba(124,58,237,0.08);}
.locked-section {opacity: 0.4; filter: blur(2px); pointer-events: none;}
.element-container {margin-bottom: 0.4rem!important;}
.anime-float {position: fixed; bottom: 20px; right: 20px; z-index: 999; opacity: 0.7;}
</style>
""", unsafe_allow_html=True)

# SESSION
for key in ['plan','email','df_clean','show_balloon','show_download_msg','payment_clicked','amt','sample_loaded','email_entered','otp','otp_verified']:
    if key not in st.session_state: st.session_state[key] = None if key in ['plan','email','df_clean','otp'] else False

# BACK BUTTON
if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn']):
        for key in ['plan','email','df_clean','payment_clicked','sample_loaded','email_entered','otp','otp_verified']:
            st.session_state[key] = None if key in ['plan','email','df_clean','otp'] else False
        st.rerun()

# EMAIL + OTP SECURITY
if st.session_state.email and not st.session_state.otp_verified:
    user = load_db().get(st.session_state.email,{})
    st.sidebar.success(f"📧 {st.session_state.email}")
    if user.get("plan") == "pro":
        exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days
        if days_left > 0:
            st.session_state.plan = "pro"
            st.session_state.amt = user.get("amt", 299)
            st.sidebar.info(T['pro_active'].format(date=user['expiry'], days=days_left))
        else:
            st.sidebar.error(T['expired'])
            st.session_state.plan = None

# HEADER + ANIME FLOAT
col1, col2 = st.columns([1,5])
with col1:
    st.image("https://i.ibb.co/Vps2R8np/anime-girl-pink-hair-beautiful-anime-girl.png", width=100)
with col2:
    st.title(T['title'])
    st.markdown(f"**{T['tagline']}**")

st.markdown(f"<div class='pro-banner'><h2>💎 {T['pro_banner']}</h2><div>{''.join([f"<span class='tool-chip'>{tool}</span>" for tool in ['Smart Date','AI Fill','Email AI','Phone AI','Case','Clean','Rename','Dedup','Trim','Spell']])}</div></div>", unsafe_allow_html=True)

# SHERANI ADMIN PANEL - IMPROVED
if st.query_params.get("admin"):
    input_hash = hashlib.sha256(st.query_params.get("admin").encode()).hexdigest()
    if input_hash == ADMIN_PASS_HASH:
        st.title(T['admin_title'])
        data = load_db()
        pending = {e:i for e,i in data.items() if i.get("status")=="PENDING" and "@" in e}
        st.metric(T['admin_pending'], len(pending))

        if pending:
            st.subheader("⏳ Pending Verifications")
            for email,info in pending.items():
                amt = info.get('amt',0)
                days = 30 if amt==299 else 180
                plan_text = f"PRO Monthly ₹299 - {days}d" if amt==299 else f"PRO 6M ₹1499 - {days}d"
                col1, col2, col3 = st.columns([4,2,1])
                with col1:
                    st.markdown(f"<div class='admin-card'><b>{T['admin_user']}:</b> {email}<br><b>{T['admin_plan']}:</b> {plan_text}<br><b>{T['admin_expiry']}:</b> {info['expiry']}</div>", unsafe_allow_html=True)
                with col3:
                    if st.button(T['admin_approve_btn'], key=f"approve_{email}", type="primary"):
                        data[email]["status"] = "PAID"
                        save_db(data)
                        st.success(f"✓ {email} Verified!")
                        st.balloons()
                        st.rerun()

        st.markdown("---")
        st.subheader("📊 All Users")
        all_users = {e:i for e,i in data.items() if "@" in e}
        for email,info in all_users.items():
            status = info.get('status','N/A')
            plan = info.get('plan','free')
            amt = info.get('amt',0)
            expiry = info.get('expiry','N/A')
            badge = "FREE" if plan == "free" else f"PRO ₹{amt}"
            color = "#7C3AED" if status=="PAID" else "#EC4899"
            st.markdown(f"<div class='admin-card'><b>{email}</b> | {badge} | Status: <span style='color:{color};font-weight:600'>{status}</span> | {expiry}</div>", unsafe_allow_html=True)
        st.stop()

# PLANS
if st.session_state.plan is None:
    col1,col2,col3 = st.columns(3, gap="small")
    with col1:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>{T['free_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<h1>FREE</h1>", unsafe_allow_html=True)
        st.markdown("<p>Lifetime</p>", unsafe_allow_html=True)
        for f in T['free_feat']: st.markdown(f"✓ {f}")
        if st.button("Start Free", key="btn_free"):
            st.session_state.plan="free"; st.session_state.amt=0; st.session_state.email_entered=True
            data = load_db()
            expiry = (datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
            data["guest_free"] = {"plan":"free","status":"PAID","amt":0,"expiry":expiry,"created":str(datetime.now())}
            save_db(data)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='pricing-card' style='border-color:#EC4899;box-shadow:0 12px 30px rgba(236,72,153,0.3)'>", unsafe_allow_html=True)
        st.markdown("⭐ POPULAR")
        st.markdown(f"<h2>{T['pro1_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1>₹{PRO_1M}</h1>", unsafe_allow_html=True)
        st.markdown("<p>30 Days</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.markdown(f"✓ {f}")
        if st.button("Get Pro", key="btn_pro1"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_1M; st.session_state.days=30
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='pricing-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>{T['pro6_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1>₹{PRO_6M}</h1>", unsafe_allow_html=True)
        st.markdown("<p>180 Days</p>", unsafe_allow_html=True)
        for f in T['pro_feat']: st.markdown(f"✓ {f}")
        if st.button("Get Pro+", key="btn_pro6"):
            st.session_state.plan="pro"; st.session_state.amt=PRO_6M; st.session_state.days=180
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
else:
    if not st.session_state.email_entered:
        email_input = st.text_input(T['email_label']).lower().strip()
        if st.button(T['continue_btn'], type="primary"):
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
            else: st.error("Valid email required")
        st.stop()

    tab1,tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    df = None
    with tab1:
        file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"])
        if file:
            df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file) if file.name.endswith(("xlsx","xls")) else pd.read_json(file)
    with tab2:
        if st.button(T['sample_btn']):
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
        user = load_db().get(st.session_state.email,{})
        is_paid = user.get("status")=="PAID" and st.session_state.plan=="pro"

        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
        with tab1:
            st.write(f"**{T['tool1']}**")
            date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date", disabled=not is_paid)
            if not is_paid: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_date", disabled=not is_paid):
                for col in date_cols: st.session_state.df_clean[col] = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')
                st.success(T['success'])

            st.write(f"**{T['tool2']}**")
            fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=not is_paid)
            if not is_paid: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_fill", disabled=not is_paid):
                st.session_state.df_clean[fill_cols] = st.session_state.df_clean[fill_cols].fillna("N/A")
                st.success(T['success'])

        with tab2:
            st.write(f"**{T['tool3']}**")
            email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=not is_paid)
            if not is_paid: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_email", disabled=not is_paid):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in email_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).lower() if re.match(pattern, str(x)) else "")
                st.success(T['success'])

            st.write(f"**{T['tool4']}**")
            phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=not is_paid)
            if not is_paid: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_phone", disabled=not is_paid):
                for col in phone_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'\D', '', regex=True)
                st.success(T['success'])

        with tab3:
            st.write(f"**{T['tool5']}**")
            case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
            if st.button(T['apply_btn'], key="btn_case"):
                for col in case_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].str.upper() if case_opt == "Uppercase" else st.session_state.df_clean[col].str.lower() if case_opt == "Lowercase" else st.session_state.df_clean[col].str.title()
                st.success(T['success'])

            st.write(f"**{T['tool6']}**")
            spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec", disabled=not is_paid)
            if not is_paid: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_spec", disabled=not is_paid):
                for col in spec_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'[^a-zA-Z0-9\s@.]', '', regex=True)
                st.success(T['success'])

            st.write(f"**{T['tool7']}**")
            old = st.selectbox("Old name", all_cols, key="sel_old", disabled=not is_paid)
            new = st.text_input("New name", key="inp_new", disabled=not is_paid)
            if not is_paid: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_rename", disabled=not is_paid) and new:
                st.session_state.df_clean.rename(columns={old: new}, inplace=True)
                st.success(T['success'])

            st.write(f"**{T['tool8']}**")
            if st.button(T['apply_btn'], key="btn_dedup", disabled=not is_paid):
                st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                st.success(T['success'])
            if not is_paid: st.caption(f"🔒 {T['locked']}")

            st.write(f"**{T['tool9']}**")
            trim_cols = st.multiselect(T['select_col'], all_cols, key="ms_trim")
            if st.button(T['apply_btn'], key="btn_trim"):
                for col in trim_cols:
                    st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip()
                st.success(T['success'])

            st.write(f"**{T['tool10']}**")
            spell_cols = st.multiselect(T['select_col'], all_cols, key="ms_spell", disabled=not is_paid)
            if not is_paid: st.caption(f"🔒 {T['locked']}")
            if st.button(T['apply_btn'], key="btn_spell", disabled=not is_paid):
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

        # DOWNLOAD LOGIC - SIRF PAID KE BAAD HI KHULEGA
        if st.session_state.plan == "free":
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button(T['download_btn'] + " CSV", csv, "clean_data.csv", key="dl_csv_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button(T['download_btn'] + " Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_free"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
        elif not is_paid:
            st.error(f"🔒 {T['paid_msg']}")
            st.markdown(f"### {T['upi_text']}")
            upi_link = f"upi://pay?pa={UPI}&pn=VeriSame&am={st.session_state.amt}&cu=INR"
            qr = qrcode.make(upi_link)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), width=200)
            st.code(UPI)
            if st.button(T['paid_btn'].format(amount=st.session_state.amt), type="primary"):
                data = load_db()
                days = 30 if st.session_state.amt == 299 else 180
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                data[st.session_state.email] = {"plan": "pro", "status": "PENDING", "amt": st.session_state.amt, "expiry": expiry, "created": str(datetime.now())}
                save_db(data)
                st.session_state.payment_clicked = True
                st.success(T['success_msg'])
        else:
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button(T['download_btn'] + " CSV", csv, "clean_data.csv", key="dl_csv_paid"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button(T['download_btn'] + " Excel", excel.getvalue(), "clean_data.xlsx", key="dl_excel_paid"):
                st.session_state.show_balloon = True
                st.session_state.show_download_msg = True
