import streamlit as st
import json, os, io
import pandas as pd
import re
from datetime import datetime, timedelta
import difflib 

# Safe imports to completely avoid Streamlit Deployment Crashes
try:
    import qrcode
except Exception:
    qrcode = None

try:
    import openpyxl
except Exception:
    openpyxl = None

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
ADMIN_PASS = st.secrets["ADMIN_PASSWORD"]

DB_FILE = "orders.json"

# SECURE DB OPERATIONS WITH ERROR HANDLING
def save_db(d):
    try:
        with open(DB_FILE,"w") as f: json.dump(d, f, indent=2)
    except Exception as e:
        st.error(f"Database Save Error: {str(e)}")

def load_db():
    if not os.path.exists(DB_FILE):
        save_db({})
    try:
        with open(DB_FILE,"r") as f:
            return json.load(f)
    except Exception:
        return {}

# ROBUST WORD-TO-NUMBER CONVERSION
def words_to_num(s):
    if pd.isna(s): return s
    s_str = str(s).lower().strip()
    if s_str.isdigit(): 
        return int(s_str)
    try:
        if float(s_str): return float(s_str)
    except ValueError:
        pass
        
    num_words = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,'hundred':100,'thousand':1000,'lakh':100000,'crore':10000000}
    total = 0; current = 0
    words = re.findall(r'\w+', s_str)
    if not words: return s
    has_num_word = False
    for word in words:
        if word in num_words:
            has_num_word = True
            val = num_words[word]
            if val >= 100:
                current = max(1, current) * val
                if val >= 1000: total += current; current = 0
            else: current += val
    return total + current if has_num_word and (total + current > 0) else s

T = {
    "title":"VeriSame","subtitle":"The Fastest Way to Clean Your Data","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"MONTHLY","pro6_title":"6 MONTHS",
    "free_feat":["1000 Rows Lifetime","CSV Export","3 Basic Tools","30s Processing","Email Support"],
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
    "admin_title":"Sherni Admin Panel","admin_pending":"User Databases & Requests","admin_approve_btn":"Mark Paid - Unlock Customer Download",
    "admin_user":"Customer Email","admin_plan":"Plan","admin_expiry":"Valid Till","delete_btn":"Delete User","download_csv":"Download as CSV","download_excel":"Download as Excel"
}

# CSS STYLING WITH CHERRY BLOSSOMS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=400;500;600;700;800;900&display=swap');
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
  position: relative; border-radius: 22px; padding: 1.6rem; background: rgba(255,255,255,0.88)!important;
  backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(147,51,234,0.15), 0 2px 6px rgba(147,51,234,0.1);
  height: 100%; transform: translateZ(0); border: 2px solid #9333ea; clip-path: polygon(0% 3%, 3% 0%, 97% 0%, 100% 3%, 100% 97%, 97% 100%, 3% 100%, 0% 97%);
}
.pricing-card:hover {transform: translateY(-8px) scale(1.01); box-shadow: 0 20px 40px rgba(147,51,234,0.25), 0 8px 16px rgba(147,51,234,0.15);}
.pricing-card h2 {font-size: 1.4rem!important; color: #6b21a8!important; margin-bottom: 0.5rem!important; font-weight: 700;}
.pricing-card h1 {font-size: 2.6rem!important; color: #6b21a8!important; margin: 0.5rem 0!important; font-weight: 800; -webkit-text-fill-color: #6b21a8!important;}
.pricing-card p {color: #000!important; font-size: 0.95rem!important; margin-bottom: 0.4rem!important;}

.stButton>button {
    border-radius: 14px !important; 
    font-weight: 700 !important; 
    background: linear-gradient(90deg, #9333ea, #a855f7) !important; 
    color: white !important; 
    border: none !important; 
    padding: 13px 26px !important; 
    width: 100% !important; 
    box-shadow: 0 5px 18px rgba(147,51,234,0.4) !important; 
    transition: all 0.3s !important; 
    cursor: pointer !important; 
    font-size: 1rem !important; 
    margin-top: 1rem !important;
}
.stButton>button:hover {transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 10px 28px rgba(147,51,234,0.5) !important;}

.pro-banner {background: linear-gradient(135deg, #7e22ce, #a855f7, #d946ef); padding: 1.6rem; border-radius: 22px; color: white!important; text-align: center; margin: 1rem 0; border: 2px solid #9333ea; box-shadow: 0 8px 20px rgba(147,51,234,0.3);}
.pro-banner h2 {color: white!important;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.95); padding: 9px 17px; border-radius: 28px; margin: 4px; font-weight: 700; border: 2px solid #9333ea; color: #000!important; font-size: 0.92rem;}
div[data-testid="stTabs"] button p {color: #000!important; font-weight: 700!important; font-size: 1rem!important;}
div[data-testid="stTabs"] button[aria-selected="true"] p {color: #6b21a8!important; font-weight: 800!important; border-bottom: 3px solid #9333ea;}
div[data-testid="stTabs"] button {background: rgba(255,255,255,0.7)!important; backdrop-filter: blur(5px); border-radius: 12px; margin-right: 8px; border: 2px solid #9333ea;}
.stAlert,.stInfo,.stSuccess,.stError {color: #000!important; font-weight: 600!important; background: rgba(255,255,255,0.8)!important; backdrop-filter: blur(5px); border-radius: 12px; border: 2px solid #9333ea;}
.stDataFrame {background: rgba(255,255,255,0.9)!important;}
.stFileUploader {background: rgba(255,255,255,0.8)!important; border: 2px dashed #9333ea;}

input[data-testid="stTextInputRootElement"], div[data-testid="stTextInput"] input {
    background-color: #ffffff !important; 
    color: #000000 !important; 
    -webkit-text-fill-color: #000000 !important; 
    border: 2px solid #9333ea !important; 
    border-radius: 11px !important;
    font-weight: 600 !important;
}

.cherry {position: fixed; top: -10vh; color: #FFB7C5; font-size: 20px; animation: fall linear infinite; z-index: 9999; pointer-events: none;}
@keyframes fall {0%{transform: translateY(0vh) translateX(0vw) rotate(0deg); opacity: 1;} 100%{transform: translateY(110vh) translateX(10vw) rotate(360deg); opacity: 0;}}
</style>
<div class="cherry" style="left: 10%; animation-duration: 8s;">🌸</div>
<div class="cherry" style="left: 30%; animation-duration: 10s; animation-delay: 2s;">🌸</div>
<div class="cherry" style="left: 50%; animation-duration: 9s; animation-delay: 4s;">🌸</div>
<div class="cherry" style="left: 70%; animation-duration: 11s; animation-delay: 1s;">🌸</div>
<div class="cherry" style="left: 90%; animation-duration: 7s; animation-delay: 3s;">🌸</div>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame's Smart AI Studio. 💎 Ask me anything about our workflows, specific tools, safety, calculations, or data science utilities!"}]

for key in ['plan','email','df_clean','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan','orig_len','empty_fixed'] else False

# 🤖 AI CHATBOT STUDIO WITH EXPANDED KNOWLEDGE BASE
def render_ai_chatbot(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 VeriSame Live AI Chat Studio")

    chat_html = "<div style='max-height: 260px; overflow-y: auto; padding: 12px; background: #ffffff !important; border: 2px solid #9333ea; border-radius: 14px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history:
        if chat["role"] == "assistant":
            chat_html += f"<p style='color: #6b21a8 !important; margin: 5px 0; font-weight: 700;'><b>🤖 AI:</b> {chat['message']}</p>"
        else:
            chat_html += f"<p style='color: #000000 !important; margin: 5px 0; font-weight: 600;'><b>👤 You:</b> {chat['message']}</p>"
    chat_html += "</div>"
    target.markdown(chat_html, unsafe_allow_html=True)

    s_id = "side" if is_sidebar else "main"
    user_msg = target.text_input("Ask a question...", placeholder="e.g., What this app can do?", key=f"chat_in_{s_id}")
    submit = target.button("Send Message 🚀", key=f"btn_send_chat_{s_id}")

    if submit and user_msg and user_msg.strip():
        u = user_msg.lower().strip()
        st.session_state.chat_history.append({"role": "user", "message": user_msg})
        reply = None

        if any(x in u for x in ["bye i am going", "bye going to", "ok bye", "tata", "see you"]):
            if "uplode" in u or "upload" in u: reply = "👋 **All the best, buddy! Go ahead and upload your files to clean them up instantly!**"
            elif "clean" in u: reply = "👍 **Awesome! Go smash those data errors and make your dataset perfect!**"
            else: reply = "👋 **Goodbye! Have a productive session ahead!**"
        elif any(x in u for x in ["thank you", "thanks", "thx"]): reply = "💖 **You are most welcome!** Making your data pipeline seamless is exactly what I'm built for."
        elif any(x in u for x in ["haha", "hehe", "funny", "😂", "😉"]): reply = "😜 **Haha!** Data cleaning can be boring, but our conversations don't have to be!"
        elif "are you mad" in u or "crazy" in u: reply = "🤪 **Haha, not at all!** I'm just hyper-engineered to clear errors at supersonic speeds!"
        elif any(x in u for x in ["alvida", "ja raha hu", "ja rhi hu", "bye bhai"]): reply = "👋 **बाय-बाय दोस्त!** जाओ और अपने डेटा को एकदम कड़क चमकाओ।"
        elif any(x in u for x in ["shukriya", "dhanyawad", "thanku bhai"]): reply = "💖 **बहुत-बहुत स्वागत है तुम्हारा!** मुझे तुम्हारी मदद करके बेहद ख़ुशी हुई।"

        if not reply:
            math_clean = u.replace('x', '*')
            match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', math_clean)
            if match:
                try:
                    n1, op, n2 = int(match.group(1)), match.group(2), int(match.group(3))
                    if op == '+': res = n1 + n2
                    elif op == '-': res = n1 - n2
                    elif op == '*': res = n1 * n2
                    elif op == '/': res = n1 / n2 if n2 != 0 else "Error"
                    reply = f"🔢 **Math Calculator Engine:** \nResult: `{res}`"
                except Exception: pass

        if not reply:
            knowledge_map = {
                "what this app can do what is app work app capability utility function software use details": "💎 **VeriSame App Capability:** This app functions as an automated data-cleaning pipeline! It repairs empty boxes, formats dates, filters emails, and converts word numbers into clean integers under 3 seconds!",
                "hi hello hey hello ai hi ai ola salam greeting system startup": "👋 **Hello there!** Welcome to VeriSame! How can I speed up your workflows today?",
                "how are you kaise ho kaise hain how it goes sab badhiya wellness state": "✨ **I am doing fantastic!** Completely ready to smash data errors under 3 seconds.",
                "your name naam kya who are you tum kaun ho identify system role profile": "💎 I am **VeriSame Engine AI**, a hyper-customized data assistant!",
                "founder made creator created developer owner built make kaun banaya owner kaun anugya sing": "👑 **Founder & Creator:** VeriSame was architected and developed by **Anugya Singh** to eliminate manual data cleaning frustration.",
                "how many tools number of tools total tools kitne tool counts": "🛠️ **Total Tools:** VeriSame features exactly **10 Data-Cleaning Tools**!",
                "is this app free free version tier lifetime free cost paisa lagega": "✨ **Yes, the base tier is Free Forever!** You get 1,000 rows processing, 3 basic pipeline tools.",
                "what is pro version premium cost details charges features upgrades": "💎 **Pro Plan:** Unlocks absolute unlimited rows, lightning-fast 3-second vector speed, and all **10 premium AI tools**!",
                "how to upload file select file spreadsheet csv excel insert data dataset load": "📤 **File Upload Steps:** Go to the 'Upload File' tab, drag and drop your `.csv`, `.xlsx`, or `.json` file.",
                "how to download file save file download csv excel export sheet download output": "🎯 **Downloading Data:** Scroll down to 'Export Data' section, choose 'Download as CSV' or 'Download as Excel'.",
                "what formats supported extension xlsx xls csv json files allowed file types": "📊 **Supported Extensions:** VeriSame handles `.csv`, `.xlsx`, `.xls`, and `.json` structures.",
                "data science workflow pipeline step data processing cycle steps clean engineering": "⚙️ **Data Science Workflow:** Raw Data ➔ Data Cleaning (using VeriSame!) ➔ Exploratory Data Analysis (EDA) ➔ Feature Engineering ➔ Machine Learning Training ➔ Model Deployment. VeriSame automates the initial 40% of manual cleaning time!",
                "python script pandas vectorization clean dataframe speed optimize memory runtime": "🐍 **Python Engine:** This application uses highly optimized vector operations via the `pandas` library instead of iterative loops, ensuring full table computation executes in under 3 seconds.",
                "tool 1 smart date converter conversion custom mixed parsing check": "📅 **Tool 1 (Smart Date):** Automatically standardizes inconsistent strings (like `12/05/2024` and `2023-11-02`) into uniform, system-ready structures seamlessly.",
                "tool 2 ai fill nulls blank data empty records missing values values fill": "🔮 **Tool 2 (AI Fill Nulls):** Smart data-type detection engine. It inserts specific fallbacks like numeric `0` for financial variables and `Unknown` for descriptive text structures.",
                "backend database orders json dynamic data security structure layout details encryption": "🛡️ **Backend Architecture:** VeriSame uses an explicit context isolation gate tied to a local persistent structural storage (`orders.json`). Admin actions require authenticated high-entropy password clearance."
            }
            best_score = 0.0
            best_reply = None
            user_words = u.split()
            for key_string, answer_text in knowledge_map.items():
                key_words = key_string.split()
                matched_words = sum(1 for w in user_words if w in key_words)
                word_ratio = matched_words / max(1, len(user_words))
                seq_ratio = difflib.SequenceMatcher(None, u, key_string).ratio()
                final_score = (word_ratio * 0.7) + (seq_ratio * 0.3)
                if final_score > best_score:
                    best_score = final_score
                    best_reply = answer_text
            
            if best_score >= 0.30 and best_reply: 
                reply = best_reply
            else: 
                reply = "🔍 **Query logged in AI memory base.** I am fully trained on pipeline architecture, tools description, code security, and foundational data calculations. Try asking: *'What is the data science workflow?'* or *'How does tool 2 work?'*"

        st.session_state.chat_history.append({"role": "assistant", "message": reply})
        st.rerun()

if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], use_container_width=True):
        for key in ['plan','email','df_clean','payment_clicked','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed']:
            st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan','orig_len','empty_fixed'] else False
        st.rerun()

if st.session_state.email:
    user = load_db().get(st.session_state.email, {})
    st.sidebar.success(f"📧 {st.session_state.email}")
    render_ai_chatbot(is_sidebar=True)
    if user.get("plan"):
        exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days
        st.session_state.plan = user.get("plan")
        st.session_state.amt = user.get("amt", 0)
        st.session_state.days = user.get("days", 0)
        st.session_state.admin_approved = user.get("status") == "PAID" and days_left > 0
        if user.get("plan") == "free": st.sidebar.info("Plan: FREE LIFETIME ✨")
        elif days_left > 0: st.sidebar.info(f"Plan: {user['plan'].upper()}\nValid Till: {user['expiry']}\n{days_left} days left")

col1, col2, col3 = st.columns([1.1, 2.2, 1.7])
with col1: st.markdown("""<div class="logo-float" style="width: 100%; min-height: 280px; display: flex; align-items: center; justify-content: center;"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width: 100%; height: auto; max-height: 280px; object-fit: contain;"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='margin-top: 5px; margin-bottom: 5px;'>VeriSame</h1>", unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{T["subtitle"]}</div>', unsafe_allow_html=True)
with col3: st.markdown("""<div class="anime-container"><img src="https://i.postimg.cc/8zdnX54g/IMG-20260609-WA0012.jpg"></div>""", unsafe_allow_html=True)
st.markdown(f"<div class='pro-banner'><h2>💎 {T['pro_banner']}</h2><div>{''.join([f"<span class='tool-chip'>{tool}</span>" for tool in ['Smart Date','AI Fill','Email AI','Phone AI','Case','Clean','Rename','Dedup','Trim','Spell']])}</div></div>", unsafe_allow_html=True)

# 🔒 HIGHLY SECURE ADMIN ROUTING & GATEWAY PANEL (FIXED ROUTING GLITCH)
if "admin" in st.query_params and st.query_params["admin"] == ADMIN_PASS:
    st.title(T['admin_title'])
    data = load_db()
    st.subheader(T['admin_pending'])
    if data:
        for email, info in list(data.items()):
            if "@" not in email: continue
            amt = info.get('amt', 0)
            status = info.get('status', 'PENDING')
            plan_text = f"PRO Monthly ₹299" if amt == 299 else f"PRO 6M ₹1499" if amt == 1499 else "FREE Plan"
            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                status_color = "🟢 PAID UNLOCKED" if status == "PAID" else "⏳ PENDING APPROVAL"
                st.markdown(f"""<div class='pricing-card'><b>{T['admin_user']}:</b> {email}<br><b>{T['admin_plan']}:</b> {plan_text}<br><b>Status:</b> {status_color}<br><b>{T['admin_expiry']}:</b> {info.get('expiry','N/A')}</div>""", unsafe_allow_html=True)
            with col2:
                if status == "PENDING":
                    if st.button(T['admin_approve_btn'], key=f"verify_{email}", type="primary", use_container_width=True):
                        data[email]["status"] = "PAID"
                        save_db(data); st.success(f"✓ {email} unlocked!"); st.balloons(); st.rerun()
                else: st.button("✓ Already Active", key=f"active_{email}", disabled=True, use_container_width=True)
            with col3:
                if st.button(T['delete_btn'], key=f"delete_{email}", use_container_width=True):
                    del data[email]; save_db(data); st.error(f"✓ {email} deleted"); st.rerun()
    else: st.info("No records found in database.")
    st.stop()

elif "admin" in st.query_params and st.query_params["admin"] != ADMIN_PASS:
    st.error("🔒 Unauthorized Access Detected. Admin Routing Halted.")
    st.stop()

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        col1,col2,col3 = st.columns(3, gap="medium")
        with col1:
            st.markdown(f"""<div class='pricing-card'><h2>{T['free_title']}</h2><h1>FREE</h1><p>Lifetime</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['free_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan = "free"; st.rerun()
        with col2:
            st.markdown(f"""<div class='pricing-card' style='border: 3px solid #9333ea; box-shadow:0 15px 35px rgba(147,51,234,0.3)'><p>⭐ POPULAR</p><h2>{T['pro1_title']}</h2><h1>₹299</h1><p>30 Days - All Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"; st.session_state.amt = PRO_1M; st.session_state.days = 30; st.rerun()
        with col3:
            st.markdown(f"""<div class='pricing-card'><h2>{T['pro6_title']}</h2><h1>₹1499</h1><p>180 Days - All Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro+", key="btn_pro6", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"; st.session_state.amt = PRO_6M; st.session_state.days = 180; st.rerun()
        
        render_ai_chatbot(is_sidebar=False)
    else:
        st.markdown(f"<h2>Enter your email to continue with {st.session_state.selected_plan.upper()}</h2>", unsafe_allow_html=True)
        email_input = st.text_input(T['email_label'], placeholder="your@email.com").lower().strip()
        if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
            if "@" in email_input and "." in email_input:
                st.session_state.email = email_input
                st.session_state.email_entered = True
                data = load_db()
                
                # FIX GLITCH: Force update configuration state if user switches from Free to Pro
                if email_input in data:
                    if st.session_state.selected_plan == "pro" and data[email_input]["plan"] == "free":
                        days = 30 if st.session_state.amt == 299 else 180
                        data[email_input]["plan"] = "pro"
                        data[email_input]["status"] = "PENDING"
                        data[email_input]["amt"] = st.session_state.amt
                        data[email_input]["days"] = days
                        data[email_input]["expiry"] = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                        save_db(data)
                    st.session_state.plan = data[email_input]["plan"]
                    st.session_state.amt = data[email_input].get("amt", 299)
                    st.rerun()
                else:
                    st.session_state.plan = st.session_state.selected_plan
                    if st.session_state.selected_plan == "free":
                        expiry = (datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                        data[email_input] = {"plan":"free","status":"PAID","amt":0,"expiry":expiry,"created":str(datetime.now())}
                        save_db(data); st.balloons(); st.rerun()
                    else:
                        days = 30 if st.session_state.amt == 299 else 180
                        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                        data[email_input] = {"plan":"pro","status":"PENDING","amt":st.session_state.amt,"days":days,"expiry":expiry,"created":str(datetime.now())}
                        save_db(data); st.rerun()
            else: st.error("Valid email required")
        st.stop()
else:
    # DATA LOADING & CLEANING PIPELINE ENGINE
    tab1,tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    df = None
    with tab1:
        # ALLOW MULTIPLE FILES IN THE UPLOADER GRID INTERFACE
        file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"], accept_multiple_files=True)
        if file:
            try: 
                df_list = []
                for f in file:
                    sub_df = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f) if f.name.endswith(("xlsx","xls")) else pd.read_json(f)
                    df_list.append(sub_df)
                df = pd.concat(df_list, ignore_index=True) if df_list else None
            except Exception as e: st.error(f"Error reading file: {str(e)}")
    with tab2:
        if st.button(T['sample_btn'], use_container_width=True):
            df = pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT SINGH"],"Email":["RAHUL@GMAIL.COM","bad@","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["one hundred","250","two thousand five hundred"]})

    if df is not None:
        if 'df_loaded' not in st.session_state or not st.session_state.df_loaded:
            st.session_state.df_clean = df.copy()
            orig_len = len(df)
            df_clean = st.session_state.df_clean.drop_duplicates()
            for col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                if any(k in col.lower() for k in ['salary','amount','price','paisa']): 
                    df_clean[col] = df_clean[col].apply(words_to_num)
            st.session_state.df_clean = df_clean
            st.session_state.df_loaded = True
            st.session_state.orig_len = orig_len
            st.session_state.empty_fixed = int(df.isna().sum().sum())
        
        try:
            if st.session_state.get('df_clean') is not None:
                df_clean = st.session_state.df_clean
                orig_len = st.session_state.orig_len

                st.markdown(f"<h2>{T['summary_title']}</h2>", unsafe_allow_html=True)
                c1,c2,c3,c4 = st.columns(4)
                with c1: st.metric(T['rows'], orig_len)
                with c2: st.metric(T['clean'], len(df_clean))
                with c3: st.metric(T['dups'], orig_len-len(df_clean))
                with c4: st.metric(T['empty'], st.session_state.empty_fixed)

                st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
                st.caption(T['preview'])
                st.dataframe(df_clean.head(10), use_container_width=True, height=300)

                all_cols = df_clean.columns.tolist()
                is_pro = st.session_state.plan == "pro"
                is_free = st.session_state.plan == "free"
                is_paid = st.session_state.admin_approved

                tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
                with tab1:
                    st.write(f"**{T['tool1']}** ✅ Free + Pro")
                    date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date")
                    if st.button(T['apply_btn'], key="btn_date", use_container_width=True):
                        for col in date_cols: 
                            try:
                                converted = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', format='mixed', dayfirst=True)
                                st.session_state.df_clean[col] = converted.dt.strftime('%Y-%m-%d').fillna("None")
                            except Exception: pass
                        st.success(T['success']); st.rerun()

                    # STRICT BLOCK FOR FREE USERS: LOCKING PREMIUM TOOLS
                    st.write(f"**{T['tool2']}** {'🔓 Unlocked ✅' if is_pro and is_paid else '🔒 PRO EXCLUSIVE (Locked for Free)'}")
                    fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=is_free or not is_paid)
                    if st.button(T['apply_btn'], key="btn_fill", use_container_width=True, disabled=is_free or not is_paid):
                        for col in fill_cols:
                            sample = str(st.session_state.df_clean[col].dropna().iloc[0]).lower() if not st.session_state.df_clean[col].dropna().empty else ""
                            if sample.isdigit() or '.' in sample: fill_val = "0"
                            elif '@' in sample: fill_val = "missing@email.com"
                            else: fill_val = "Unknown"
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].fillna(fill_val).replace(["nan", "None", "", " "], fill_val)
                        st.success(T['success']); st.rerun()

                with tab2:
                    st.write(f"**{T['tool3']}** {'🔓 Unlocked ✅' if is_pro and is_paid else '🔒 PRO EXCLUSIVE (Locked for Free)'}")
                    email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=is_free or not is_paid)
                    if st.button(T['apply_btn'], key="btn_email", use_container_width=True, disabled=is_free or not is_paid):
                        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                        for col in email_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower().str.strip().apply(lambda x: x if re.match(pattern, x) else "Invalid Email")
                        st.success(T['success']); st.rerun()

                    st.write(f"**{T['tool4']}** {'🔓 Unlocked ✅' if is_pro and is_paid else '🔒 PRO EXCLUSIVE (Locked for Free)'}")
                    phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=is_free or not is_paid)
                    if st.button(T['apply_btn'], key="btn_phone", use_container_width=True, disabled=is_free or not is_paid):
                        for col in phone_cols: 
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x)))
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: x[-10:] if len(x) >= 10 else x)
                        st.success(T['success']); st.rerun()

                with tab3:
                    st.write(f"**{T['tool5']}** ✅ Free + Pro")
                    case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
                    case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
                    if st.button(T['apply_btn'], key="btn_case", use_container_width=True):
                        for col in case_cols: 
                            if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.upper()
                            elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower()
                            else: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.title()
                        st.success(T['success']); st.rerun()

                    st.write(f"**{T['tool6']}** {'🔓 Unlocked ✅' if is_pro and is_paid else '🔒 PRO EXCLUSIVE (Locked for Free)'}")
                    spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec", disabled=is_free or not is_paid)
                    if st.button(T['apply_btn'], key="btn_spec", use_container_width=True, disabled=is_free or not is_paid):
                        for col in spec_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9\s.,₹$@\-+]', '', x))
                        st.success(T['success']); st.rerun()

                    st.write(f"**{T['tool7']}** {'🔓 Unlocked ✅' if is_pro and is_paid else '🔒 PRO EXCLUSIVE (Locked for Free)'}")
                    old = st.selectbox("Old column name", all_cols, key="sel_old", disabled=is_free or not is_paid)
                    new = st.text_input("New column name", key="inp_new", disabled=is_free or not is_paid)
                    if st.button(T['apply_btn'], key="btn_rename", use_container_width=True, disabled=is_free or not is_paid) and new:
                        st.session_state.df_clean.rename(columns={old: new}, inplace=True)
                        st.success(T['success']); st.rerun()

                    st.write(f"**{T['tool8']}** ✅ Free + Pro")
                    if st.button(T['apply_btn'], key="btn_dedup", use_container_width=True):
                        st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                        st.success(T['success']); st.rerun()

                    st.write(f"**{T['tool9']}** ✅ Free + Pro")
                    trim_cols = st.multiselect(T['select_col'], all_cols, key="ms_trim")
                    if st.button(T['apply_btn'], key="btn_trim", use_container_width=True):
                        for col in trim_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                        st.success(T['success']); st.rerun()

                    st.write(f"**{T['tool10']}** {'🔓 Unlocked ✅' if is_pro and is_paid else '🔒 PRO EXCLUSIVE (Locked for Free)'}")
                    spell_cols = st.multiselect(T['select_col'], all_cols, key="ms_spell", disabled=is_free or not is_paid)
                    if st.button(T['apply_btn'], key="btn_spell", use_container_width=True, disabled=is_free or not is_paid):
                        typo_dict = {"teh":"the","recieve":"receive","goverment":"government","managment":"management","colum":"column","datset":"dataset","salery":"salary","amout":"amount","phne":"phone","emil":"email","addres":"address","nam":"name","infomation":"information"}
                        def fix_typos(text):
                            words = str(text).split()
                            return " ".join([typo_dict.get(w.lower(), w) for w in words])
                        for col in spell_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(fix_typos).astype(str).str.title()
                        st.success(T['success']); st.rerun()

                st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
                if st.session_state.show_balloon: st.balloons(); st.session_state.show_balloon = False

                if st.session_state.plan == "free":
                    col1, col2 = st.columns(2)
                    csv = st.session_state.df_clean.to_csv(index=False).encode()
                    if col1.download_button(T['download_csv'], csv, "verisame_clean.csv", mime="text/csv", key="dl_csv_free", use_container_width=True):
                        st.session_state.show_balloon = True; st.rerun()
                elif st.session_state.plan == "pro":
                    if not is_paid:
                        st.warning(T['wait_approval'])
                        st.markdown(f"### {T['upi_text'].format(amount=st.session_state.amt)}")
                        if qrcode is not None:
                            upi_link = f"upi://pay?pa={UPI}&pn=VeriSame&am={st.session_state.amt}&cu=INR"
                            qr = qrcode.make(upi_link); buf = io.BytesIO(); qr.save(buf, format="PNG")
                            st.image(buf.getvalue(), width=220)
                        else:
                            st.info(f"Send payment directly to UPI ID: {UPI}")
                        if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary", use_container_width=True):
                            st.session_state.payment_clicked = True; st.rerun()
                    else:
                        col1, col2 = st.columns(2)
                        csv = st.session_state.df_clean.to_csv(index=False).encode()
                        if col1.download_button(T['download_csv'], csv, "verisame_pro.csv", mime="text/csv", key="dl_csv_paid", use_container_width=True):
                            st.session_state.show_balloon = True; st.rerun()
                        try:
                            if openpyxl is not None:
                                excel = io.BytesIO()
                                st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                                if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_pro.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_paid", use_container_width=True):
                                    st.session_state.show_balloon = True; st.rerun()
                        except Exception: pass
        except Exception: pass

    if not st.session_state.plan and not st.session_state.email_entered:
        pass
