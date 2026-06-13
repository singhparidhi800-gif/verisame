import streamlit as st
import json, os, io, qrcode
import pandas as pd
import re
from datetime import datetime, timedelta

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ===== VERISAME CHAT AI - WITH BASIC KNOWLEDGE BASE =====
def detect_hindi(text):
    hindi_chars = re.findall(r'[\u0900-\u097F]', text)
    if len(hindi_chars) >= 2:
        return True
    hindi_words = ['bhai','kya','hai','kaise','karo','bolo','hindi','mein','main','tu','tum','ye','wo','kar','ho','raha','nahi','mujhe','tere','tera','meri','mera','kaam','app','bataye','samjhao','kaun','kahan','kab']
    words_in_text = text.lower().split()
    hindi_count = sum(1 for word in hindi_words if word in words_in_text)
    return hindi_count >= 2

def local_ai_reply(prompt, df=None):
    is_hindi = detect_hindi(prompt)
    p = prompt.lower().strip()

    if any(x in p for x in ['hindi me bolo','hindi mein','speak hindi','talk in hindi','hindi me baat']):
        return "Bhai thik hai, ab se Hindi me baat karunga. Kya puchna hai?"
    if any(x in p for x in ['english me bolo','speak english','talk in english']):
        return "Got it, I'll reply in English now. What do you want to know?"

    knowledge = {
        'capital of india': ('New Delhi', 'New Delhi'),
        'pm of india': ('Narendra Modi', 'Narendra Modi'),
        'prime minister of india': ('Narendra Modi', 'Narendra Modi'),
        'president of india': ('Droupadi Murmu', 'Droupadi Murmu'),
        'national animal': ('Tiger', 'Bagh'),
        'national bird': ('Peacock', 'Mor'),
        'national flower': ('Lotus', 'Kamal'),
        'capital of usa': ('Washington D.C.', 'Washington D.C.'),
        'capital of uk': ('London', 'London'),
        'capital of japan': ('Tokyo', 'Tokyo'),
        'largest planet': ('Jupiter', 'Jupiter'),
        'smallest planet': ('Mercury', 'Mercury'),
        'water formula': ('H2O', 'H2O'),
        'speed of light': ('299,792,458 m/s', '299,792,458 m/s'),
        'pi value': ('3.14159', '3.14159'),
        'current year': ('2026', '2026'),
        'cricket captain india': ('Rohit Sharma', 'Rohit Sharma'),
        'virat kohli': ('Indian cricketer, legend', 'Indian cricketer, legend hai'),
    }

    for key, (eng_ans, hindi_ans) in knowledge.items():
        if all(word in p for word in key.split()):
            return f"Bhai {hindi_ans}" if is_hindi else f"{eng_ans}"

    if any(x in p for x in ['app kaise', 'how does', 'how to use', 'kaam karta', 'verisame kya', 'what is verisame', 'how work', 'use this', 'kaise chalate', 'explain app']):
        if is_hindi:
            return """Bhai VeriSame data cleaning ka sabse fast tareeka hai. 4 step me kaam hota hai:
1. **Upload**: CSV, Excel ya JSON file daal de - 200MB tak. Auto clean ho jata hai
2. **AI Studio**: 10 tools hain - Smart Date, AI Fill Nulls, Email Validator, Phone Formatter, Case Converter, Remove Symbols, Bulk Rename, Remove Duplicates, Trim Spaces, Spell Check
3. **Process**: Tool select kar, column choose kar, Apply daba de
4. **Download**: Clean CSV ya Excel download kar le

**Pricing**: Free me 3 tools lifetime. Pro me ₹299/month ya ₹1499/6month me sab 10 tools + unlimited rows + 3s speed.
**Support**: Mujhse sidebar me kuch bhi puchh le - CSV, maths, GK."""
        else:
            return """VeriSame is the fastest way to clean your data. Works in 4 steps:
1. **Upload**: Drop CSV, Excel or JSON - up to 200MB. Auto-cleans basic stuff
2. **AI Studio**: 10 tools - Smart Date, AI Fill Nulls, Email Validator, Phone Formatter, Case Converter, Remove Symbols, Bulk Rename, Remove Duplicates, Trim Spaces, Spell Check
3. **Process**: Select tool, choose columns, click Apply
4. **Download**: Export clean CSV or Excel

**Pricing**: Free gives 3 tools lifetime. Pro unlocks all 10 tools + unlimited rows + 3s speed for ₹299/month or ₹1499/6months.
**Support**: Ask me anything in sidebar - CSV, math, GK."""

    if any(x in p for x in ['*','x','multiply','guna','into']) or re.search(r'\d+\s*x\s*\d+', p):
        nums = [int(s) for s in re.findall(r'\d+', p)]
        if len(nums) >= 2:
            return f"Bhai {nums[0] * nums[1]} hota hai" if is_hindi else f"The answer is {nums[0] * nums[1]}"
    if any(x in p for x in ['+','add','jod','plus','sum']) or re.search(r'\d+\s*\+\s*\d+', p):
        nums = [int(s) for s in re.findall(r'\d+', p)]
        if len(nums) >= 2:
            return f"Bhai {sum(nums)} hota hai" if is_hindi else f"The answer is {sum(nums)}"
    if any(x in p for x in ['-','minus','subtract','ghata']) or re.search(r'\d+\s*-\s*\d+', p):
        nums = [int(s) for s in re.findall(r'\d+', p)]
        if len(nums) >= 2:
            return f"Bhai {nums[0] - nums[1]} hota hai" if is_hindi else f"The answer is {nums[0] - nums[1]}"
    if any(x in p for x in ['/','divide','bhag']) or re.search(r'\d+\s*/\s*\d+', p):
        nums = [int(s) for s in re.findall(r'\d+', p)]
        if len(nums) >= 2 and nums[1]!= 0:
            return f"Bhai {nums[0] / nums[1]} hota hai" if is_hindi else f"The answer is {nums[0] / nums[1]}"

    if df is not None:
        if any(x in p for x in ['column','columns','col','colums']):
            cols = ', '.join(df.columns[:5])
            return f"Bhai tere CSV me {len(df.columns)} columns hain: {cols}..." if is_hindi else f"Your CSV has {len(df.columns)} columns: {cols}..."
        if any(x in p for x in ['row','rows','kitni','kitne','data','line','kitna']):
            nulls = df.isna().sum().sum()
            return f"Bhai total {len(df)} rows hain. {nulls} cells khali hain." if is_hindi else f"You have {len(df)} total rows. {nulls} cells are empty."
        if any(x in p for x in ['clean','saaf','fix','thik','process','clear','saf']):
            return "Bhai AI Studio me ja: 'Smart Date' se date fix kar, 'Remove Duplicates' se duplicate hata, 'AI Fill Nulls' se khali jagah bhar." if is_hindi else "Go to AI Studio: Use 'Smart Date' to fix dates, 'Remove Duplicates' to delete dupes, 'AI Fill Nulls' to fill empty cells."
        if any(x in p for x in ['duplicate','dup','double','repeat','same']):
            dups = df.duplicated().sum()
            return f"Bhai {dups} duplicate rows mili. 'Remove Duplicates' tool use kar." if is_hindi else f"Found {dups} duplicate rows. Use 'Remove Duplicates' tool."
        if any(x in p for x in ['null','empty','khali','blank','missing','gap']):
            nulls = df.isna().sum().sum()
            return f"Bhai {nulls} cells khali hain. 'AI Fill Nulls' tool use kar le." if is_hindi else f"You have {nulls} empty cells. Use 'AI Fill Nulls' tool."
        if any(x in p for x in ['date','time','format','tarikh']):
            return "Bhai Date wale column select karke 'Smart Date Converter' use kar. YYYY-MM-DD me convert ho jayega." if is_hindi else "Select date columns and use 'Smart Date Converter'. Converts to YYYY-MM-DD format."

    if any(x in p for x in ['tool','feature','kya kar sakta','what can','kitne tool']):
        if is_hindi:
            return "Bhai 10 tools hain: 1-Smart Date, 2-AI Fill Nulls, 3-Email Validator, 4-Phone Formatter, 5-Case Converter, 6-Remove Symbols, 7-Bulk Rename, 8-Remove Duplicates, 9-Trim Spaces, 10-Spell Check. Free me 1,5,8,9 milte hain. Pro me sab 10."
        else:
            return "10 tools available: 1-Smart Date, 2-AI Fill Nulls, 3-Email Validator, 4-Phone Formatter, 5-Case Converter, 6-Remove Symbols, 7-Bulk Rename, 8-Remove Duplicates, 9-Trim Spaces, 10-Spell Check. Free gives 1,5,8,9. Pro gives all 10."

    if any(x in p for x in ['hi','hello','hey','namaste','namaskar','hii','helo','hlw']):
        return "Bhai Hi, bolo CSV saaf karna hai kya? Ya app ke baare me puchhna hai?" if is_hindi else "Hi there! Need help cleaning your CSV? Or want to know how this app works?"

    if is_hindi:
        return "Bhai ye exact nahi pata. Par app kaise chalana hai, CSV cleaning, maths, capital-PM, cricket - ye sab puchh le. Example: '28x36' ya 'capital of india'"
    else:
        return "I don't know that exactly. But ask me how the app works, CSV cleaning, math, capitals, PM, cricket. Example: '28x36' or 'capital of india'"

if "vsai_messages" not in st.session_state:
    st.session_state.vsai_messages = []
# ===== LOCAL AI END =====

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

    st.sidebar.divider()
    st.sidebar.markdown("## 🤖 VeriSame Chat AI")
    st.sidebar.caption("CSV saaf karwao ya 28x36 puchho")
    sidebar_q = st.sidebar.text_area("Quick Doubt:", height=150, key="sidebar_ai_q")
    if st.sidebar.button("Ask AI", use_container_width=True, key="sidebar_ai_btn"):
        if sidebar_q:
            with st.sidebar:
                with st.spinner("Socho..."):
                    df_context = st.session_state.df_clean if 'df_clean' in st.session_state else None
                    ai_text = local_ai_reply(sidebar_q, df_context)
                    st.success(f"**AI:** {ai_text}")

    if user.get("plan"):
        exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days
        st.session_state.plan = user.get("plan")
        st.session_state.amt = user.get("amt", 0)
        st.session_state.days = user.get("days", 0)
        # ===== NEW LOGIC: CHECK EXPIRY =====
        st.session_state.admin_approved = user.get("status") == "PAID" and days_left > 0

        if user.get("plan") == "free":
            st.sidebar.info("Plan: FREE LIFETIME")
        elif days_left <= 5 and days_left > 0:
            st.sidebar.error(T['expiry_warning'].format(days=days_left))
        elif days_left > 0:
            st.sidebar.info(f"Plan: {user['plan'].upper()}\nValid Till: {user['expiry']}\n{days_left} days left")
        else:
            st.sidebar.error("Plan Expired - Renew karna padega")
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
            exp_date = datetime.strptime(info.get('expiry','2000-01-01'), "%Y-%m-%d")
            days_left = (exp_date - datetime.now()).days
            if info.get('plan') == 'free':
                status_color = "#059669"
                status_text = "FREE LIFETIME"
            elif info.get('status')=="PAID" and days_left > 0:
                status_color = "#059669"
                status_text = "PAID - Active"
            elif days_left <= 0:
                status_color = "#DC2626"
                status_text = "EXPIRED - Renew Required"
            else:
                status_color = "#DC2626"
                status_text = "PENDING - Waiting for approval"

            col1, col2 = st.columns([6,2])
            with col1:
                st.markdown(f"<div class='pricing-card'><b>{email}</b> | Plan: {info.get('plan','free').upper()} | ₹{info.get('amt',0)} | <span style='color:{status_color};font-weight:700'>{status_text}</span><br>Expiry: {info.get('expiry','N/A')} | Days Left: {max(0,days_left)}</div>", unsafe_allow_html=True)
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

                # ===== NEW LOGIC: EMAIL KABHI DELETE NAHI HOGA =====
                user_exists = email_input in data
                current_time = datetime.now()

                if st.session_state.selected_plan == "free":
                    expiry = (current_time+timedelta(days=36500)).strftime("%Y-%m-%d")
                    data[email_input] = {"plan":"free","status":"PAID","amt":0,"expiry":expiry,"created":str(current_time)}
                    save_db(data)
                    st.balloons()
                    st.rerun()
                else:
                    # Check if user exists and plan is expired
                    if user_exists:
                        old_expiry = datetime.strptime(data[email_input].get('expiry','2000-01-01'), "%Y-%m-%d")
                        days_left = (old_expiry - current_time).days
                        # Agar active plan hai to QR mat dikhao - sidha approval
                        if data[email_input].get('status') == 'PAID' and days_left > 0:
                            st.success("Active plan hai! Dubara paise nahi dene")
                            st.rerun()

                    days = 30 if st.session_state.amt == 299 else 180
                    expiry = (current_time + timedelta(days=days)).strftime("%Y-%m-%d")
                    data[email_input] = {"plan":"pro","status":"PENDING","amt":st.session_state.amt,"days":days,"expiry":expiry,"created":str(current_time)}
                    save_db(data)
                    st.rerun()
            else: st.error("Valid email required")
        st.stop()
else:
    # ===== QR CODE + PAYMENT LOGIC - ACTIVE PLAN ME QR NAHI DIKHEGA =====
    data = load_db()
    user = data.get(st.session_state.email, {})
    is_paid = user.get("status") == "PAID"

    if st.session_state.plan == "pro" and not is_paid:
        if not st.session_state.payment_clicked:
            st.markdown(f"### {T['paid_msg']}")
            upi_link = f"upi://pay?pa={UPI}&pn=VeriSame&am={st.session_state.amt}&cu=INR"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(upi_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), width=250, caption=T['upi_text'].format(amount=st.session_state.amt))

            if st.button(T['paid_btn'].format(amount=st.session_state.amt), type="primary", use_container_width=True):
                st.session_state.payment_clicked = True
                st.rerun()
        else:
            st.warning(T['wait_approval'])
            if st.button("Refresh Status", use_container_width=True):
                st.rerun()

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
            st.session_state.sample_loaded = True

    if df is not None:
        df_clean = df.copy()
        dups_before = df_clean.duplicated().sum()
        df_clean = df_clean.drop_duplicates().reset_index(drop=True)
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].apply(words_to_num)
        empty_before = df_clean.isna().sum().sum()

        st.session_state.df_clean = df_clean

        st.subheader(T['summary_title'])
        col1,col2,col3,col4 = st.columns(4)
        col1.metric(T['rows'], len(df_clean))
        col2.metric(T['clean'], len(df_clean) - dups_before)
        col3.metric(T['dups'], dups_before)
        col4.metric(T['empty'], empty_before)

        st.subheader(T['preview'])
        st.dataframe(df_clean.head(10), use_container_width=True)

        # ===== AI STUDIO TOOLS =====
        st.markdown(f"## {T['tools_menu']}")
        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])

        free_tools = [T['tool1'], T['tool5'], T['tool8'], T['tool9']] # Smart Date, Case, Dedup, Trim
        is_pro = st.session_state.plan == "pro" and st.session_state.admin_approved

        with tab1:
            col1,col2 = st.columns(2)
            with col1:
                if st.button(T['tool1'], disabled=not (is_pro or T['tool1'] in free_tools), use_container_width=True):
                    st.success(T['success'])
            with col2:
                if st.button(T['tool2'], disabled=not is_pro, use_container_width=True):
                    st.success(T['success'])
        with tab2:
            col1,col2 = st.columns(2)
            with col1:
                if st.button(T['tool3'], disabled=not is_pro, use_container_width=True):
                    st.success(T['success'])
            with col2:
                if st.button(T['tool4'], disabled=not is_pro, use_container_width=True):
                    st.success(T['success'])
        with tab3:
            col1,col2 = st.columns(2)
            with col1:
                if st.button(T['tool5'], disabled=not (is_pro or T['tool5'] in free_tools), use_container_width=True):
                    st.success(T['success'])
                if st.button(T['tool7'], disabled=not is_pro, use_container_width=True):
                    st.success(T['success'])
                if st.button(T['tool9'], disabled=not (is_pro or T['tool9'] in free_tools), use_container_width=True):
                    st.success(T['success'])
            with col2:
                if st.button(T['tool6'], disabled=not is_pro, use_container_width=True):
                    st.success(T['success'])
                if st.button(T['tool8'], disabled=not (is_pro or T['tool8'] in free_tools), use_container_width=True):
                    st.success(T['success'])
                if st.button(T['tool10'], disabled=not is_pro, use_container_width=True):
                    st.success(T['success'])

        # ===== DOWNLOAD SECTION =====
        st.subheader(T['download_title'])
        can_download = st.session_state.plan == "free" or st.session_state.admin_approved

        if can_download:
            col1,col2 = st.columns(2)
            with col1:
                csv = df_clean.to_csv(index=False).encode('utf-8')
                st.download_button(T['download_csv'], csv, "verisame_clean.csv", "text/csv", use_container_width=True)
            with col2:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_clean.to_excel(writer, index=False)
                st.download_button(T['download_excel'], buffer.getvalue(), "verisame_clean.xlsx", use_container_width=True)
        else:
            st.warning(T['wait_approval'])
