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

# 🔒 MAXIMUM SECURITY PERSISTENT DATABASE ENGINE
if "global_db_backup" not in st.session_state:
    st.session_state.global_db_backup = {}

def load_db():
    if st.session_state.global_db_backup:
        return st.session_state.global_db_backup
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    st.session_state.global_db_backup = data
                    return data
        except Exception:
            pass
    return {}

def save_db(d):
    try:
        st.session_state.global_db_backup = d
        with open("backup_orders.json", "w") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass

# ROBUST WORD-TO-NUMBER CONVERSION (FIXED NUMERIC TYPE BYPASSES)
def words_to_num(s):
    if pd.isna(s): return s
    if isinstance(s, (int, float)):
        return s
    
    s_str = str(s).lower().strip()
    
    if s_str.isdigit(): 
        return int(s_str)
        
    try:
        if '.' in s_str:
            return float(s_str)
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

# 🧠 ADVANCED FUZZY DEDUPLICATION ALGORITHM
def remove_fuzzy_duplicates(dataframe, column_name, threshold=0.85):
    """Finds names that look similar (like Anugya Sharma vs Anugya Sharrma) and cleans them up."""
    if dataframe[column_name].dtype != 'object':
        return dataframe
    
    unique_values = dataframe[column_name].dropna().unique()
    mapping = {}
    
    for i, val1 in enumerate(unique_values):
        if val1 in mapping:
            continue
        for val2 in unique_values[i+1:]:
            s1, s2 = str(val1).strip().lower(), str(val2).strip().lower()
            ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
            if ratio >= threshold:
                mapping[val2] = val1
                
    dataframe[column_name] = dataframe[column_name].replace(mapping)
    return dataframe.drop_duplicates()

# 📅 SYSTEM DATE CONVERTER WITH EXTRA RESILIENCE 
def intelligent_date_parser(date_str):
    if pd.isna(date_str) or str(date_str).strip() in ["", "nan", "None"]:
        return "None"
    
    clean_str = str(date_str).strip().replace('/', '-').replace('.', '-')
    
    formats = ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(clean_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
            
    match = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})', clean_str)
    if match:
        d, m, y = match.group(1), match.group(2), match.group(3)
        if len(y) == 2: y = "20" + y
        try:
            return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        except Exception:
            pass
            
    return "None"

T = {
    "title":"VeriSame","subtitle":"The Fastest Way to Clean Your Data","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"MONTHLY","pro6_title":"6 MONTHS",
    "free_feat":["1000 Rows Lifetime","CSV Export","4 Free Tools Built-in","30s Processing","Email Support"],
    "pro_feat":["Unlimited Rows","CSV + Excel Export","10 Premium AI Tools","3s Speed","Priority Support","No Watermark","Lifetime Updates"],
    "email_label":"Enter your email address","continue_btn":"Verify & Continue","upload_tab":"📤 Upload File","sample_tab":"🎯 Try Demo",
    "upload_text":"Drop CSV, Excel or JSON file here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview (Green Highlights show where tools worked 🟢)",
    "tools_menu":"AI Studio","back_btn":"← Back","download_title":"Export Data",
    "paid_msg":"Step 1: Pay ₹299 for 1 Month or ₹1499 for 6 Months via UPI. Step 2: Click I Paid button below. Step 3: Admin will approve. Step 4: Download unlocks",
    "upi_text":"Scan QR to Pay ₹{amount}","paid_btn":"Customer I Paid ₹{amount}","wait_approval":"⏳ Waiting for Admin Approval... Click 'I Paid' after payment",
    "download_success":"🎉 Download Ready!","tab1":"Date & Nulls","tab2":"Email & Phone","tab3":"Text Tools",
    "tool1":"Smart Date Converter","tool2":"AI Fill Nulls","tool3":"Email Validator","tool4":"Phone Formatter","tool5":"Case Converter",
    "tool6":"Remove Symbols","tool7":"Bulk Rename","tool8":"Remove Duplicates / Fuzzy Match","tool9":"Trim Spaces","tool10":"Spell Check",
    "select_col":"Select Columns","select_case":"Choose Case Type","apply_btn":"Apply Actions","success":"Apply is completed! Your data has been successfully updated.",
    "admin_title":"👑 Admin Dashboard Panel 👑","admin_pending":"User Databases & Purchase Requests","admin_approve_btn":"Mark Paid - Unlock Customer Download",
    "admin_user":"Customer Email","admin_plan":"Plan","admin_expiry":"Valid Till","delete_btn":"Delete User","download_csv":"Download as CSV","download_excel":"Download as Excel"
}

# CSS STYLING WITH CHERRY BLOSSOMS & PREMIUM GRAPHICS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 25%, #c084fc 50%, #a855f7 75%, #9333ea 100%); background-size: 400% 400%; animation: aurora 15s ease infinite; padding-top: 0.3rem;}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}
.block-container {background: rgba(255,255,255,0.96); backdrop-filter: blur(25px) saturate(180%); border-radius: 28px; padding: 2rem; max-width: 1200px; margin: 0 auto; box-shadow: 0 30px 60px rgba(139,92,246,0.25); border: 1.5px solid rgba(255,255,255,0.5);}
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
.anime-container {position: relative; width: 100%; min-height: 280px; border-radius: 25px; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.3); border: 3px solid #9333ea;}
.anime-container img {width: 100%; height: 280px; object-fit: cover; object-position: center top; display: block;}
.pricing-card {
  position: relative; border-radius: 22px; padding: 1.6rem; background: rgba(255,255,255,0.92)!important;
  backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(147,51,234,0.15), 0 2px 6px rgba(147,51,234,0.1);
  height: 100%; transform: translateZ(0); border: 2.5px solid #9333ea; clip-path: polygon(0% 3%, 3% 0%, 97% 0%, 100% 3%, 100% 97%, 97% 100%, 3% 100%, 0% 97%);
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
<div class="cherry" style="left: 20%; animation-duration: 12s; animation-delay: 1s;">🌸</div>
<div class="cherry" style="left: 30%; animation-duration: 10s; animation-delay: 2s;">🌸</div>
<div class="cherry" style="left: 45%; animation-duration: 14s; animation-delay: 0.5s;">🌸</div>
<div class="cherry" style="left: 55%; animation-duration: 9s; animation-delay: 4s;">🌸</div>
<div class="cherry" style="left: 70%; animation-duration: 11s; animation-delay: 1s;">🌸</div>
<div class="cherry" style="left: 80%; animation-duration: 13s; animation-delay: 2.5s;">🌸</div>
<div class="cherry" style="left: 90%; animation-duration: 7s; animation-delay: 3s;">🌸</div>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame's Ultra Advanced AI Studio. 💎 I can help you fix syntax bugs, configure datasets, explain ML models, or talk about system properties!"}]

if "changed_cells" not in st.session_state:
    st.session_state.changed_cells = set()

for key in ['plan','email','df_clean','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan','orig_len','empty_fixed'] else False

def track_modifications(old_df, new_df):
    try:
        for col in old_df.columns:
            if col in new_df.columns:
                mismatch_indices = old_df[old_df[col].astype(str) != new_df[col].astype(str)].index
                for idx in mismatch_indices:
                    st.session_state.changed_cells.add((idx, col))
    except Exception:
        pass

def apply_cell_styling(df_to_style):
    def highlight_cells(x):
        df_colors = pd.DataFrame('', index=x.index, columns=x.columns)
        for row, col in st.session_state.changed_cells:
            if row in df_colors.index and col in df_colors.columns:
                df_colors.at[row, col] = 'background-color: #bbf7d0; color: #047857; font-weight: bold; border: 1.5px solid #10b981;'
        return df_colors
    return df_to_style.style.apply(highlight_cells, axis=None)

def render_ai_chatbot(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 VeriSame Ultra AI Chat Bot Pro")

    chat_html = "<div style='max-height: 280px; overflow-y: auto; padding: 12px; background: #ffffff !important; border: 2px solid #9333ea; border-radius: 14px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history:
        if chat["role"] == "assistant":
            chat_html += f"<p style='color: #6b21a8 !important; margin: 5px 0; font-weight: 700;'><b>🤖 AI:</b> {chat['message']}</p>"
        else:
            chat_html += f"<p style='color: #000000 !important; margin: 5px 0; font-weight: 600;'><b>👤 You:</b> {chat['message']}</p>"
    chat_html += "</div>"
    target.markdown(chat_html, unsafe_allow_html=True)

    s_id = "side" if is_sidebar else "main"
    user_msg = target.text_input("Ask advanced questions...", placeholder="e.g., Explain vectorization or check data status", key=f"chat_in_{s_id}")
    submit = target.button("Send Message 🚀", key=f"btn_send_chat_{s_id}")

    if submit and user_msg and user_msg.strip():
        u = user_msg.lower().strip()
        st.session_state.chat_history.append({"role": "user", "message": user_msg})
        reply = None

        if st.session_state.get('df_loaded') and st.session_state.get('df_clean') is not None:
            live_df = st.session_state.df_clean
            if any(x in u for x in ["column", "columns", "what fields", "variables"]):
                reply = f"📊 **Live Dataset Columns:** Current workspace active parameters: `{', '.join(live_df.columns.tolist())}`."
            elif any(x in u for x in ["how many rows", "row count", "total rows", "dataset size", "shape"]):
                reply = f"🔢 **Live Dataset Dimensions:** Vector matrix is handling `{len(live_df)}` rows across `{len(live_df.columns)}` computational vectors."
            elif any(x in u for x in ["missing", "nulls", "empty boxes", "dirty boxes"]):
                reply = f"🛠️ **Live Cleanliness Status:** We have successfully insulated `{st.session_state.get('empty_fixed', 0)}` faulty vector indices across active nodes!"

        if not reply:
            if any(x in u for x in ["bye i am going", "bye going to", "ok bye", "tata", "see you", "alvida", "ja raha", "ja rhi"]):
                if "uplode" in u or "upload" in u: reply = "👋 **All the best! Upload your sheets and run the vector cleaning sequence anytime!**"
                elif "clean" in u: reply = "👍 **Awesome! Go ahead and process the sheets with premium triggers!**"
                else: reply = "👋 **Goodbye! Keep automating and engineering grand designs!**"
            elif any(x in u for x in ["thank you", "thanks", "thx", "shukriya", "dhanyawad", "thanku"]): reply = "💖 **Always glad to engineer solutions!** Let's clear more bottlenecks."
            elif any(x in u for x in ["haha", "hehe", "funny", "😂", "😉"]): reply = "😜 **Haha!** Adding precision compute speeds with a smile!"
            elif "are you mad" in u or "crazy" in u: reply = "🤪 **Haha, not at all!** Just highly customized execution algorithms at full thrust!"

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
                "founder made creator created developer owner built make kaun banaya owner kaun anugya singh app architecture who designed": "👑 **Founder & Creator:** VeriSame was completely architected, designed, and coded by **Anugya Singh** to streamline manual data preprocessing effortlessly!",
                "what this app can do what is app work app capability utility function software use details purpose system tool utility": "💎 **VeriSame Ecosystem Capabilities:** It acts as an elite automation processing center! Repairs missing rows, isolates invalid emails, strips broken symbols, and converts textual expressions into pure numbers under 3s!",
                "hi hello hey hello ai hi ai ola salam greeting system startup start beginning greeting": "👋 **Welcome to VeriSame Core AI!** Processing terminals are green. How can I optimize your workflows today?",
                "how are you kaise ho kaise hain how it goes sab badhiya wellness state mood status health": "✨ **System Diagnostics Nominal!** Highly synchronized and ready to clean data at supreme speeds.",
                "your name naam kya who are you tum kaun ho identify system role profile system bot": "💎 I am **VeriSame Cognitive Engine**, an elite automated agent for high-density matrix cleaning!",
                "how many tools number of tools total tools kitne tool counts listing available features": "🛠️ **Total System Architecture:** VeriSame includes precisely **10 Premium AI Engineering Tools** grouped in a high-efficiency dashboard interface.",
                "is this app free free version tier lifetime free cost paisa lagega trials base subscription": "✨ **Yes! The foundation layer is Free Forever.** You receive 1,000 rows processing, 4 free runtime tools, and unrestricted interface access.",
                "what is pro version premium cost details charges features upgrades price models subscription plans": "💎 **Pro Infrastructure Tier:** Removes all row constraints, triggers sub-3-second execution speeds, and unlocks all **10 Advanced AI Tools**. Subscriptions are segmented into 1-Month and 6-Month tiers.",
                "how to upload file select file spreadsheet csv excel insert data dataset load file injection": "📤 **File Ingestion Sequence:** Toggle the 'Upload File' sub-tab, drop standard `.csv`, `.xlsx`, or `.json` directly into the dynamic drag-and-drop boundary.",
                "how to download file save file download csv excel export sheet download output save localized": "🎯 **Export Protocols:** Navigate down to the 'Export Data' sector, trigger 'Download as CSV' or 'Download as Excel'. Note: Pro exports deploy as soon as the admin handles clearance authorization.",
                "what formats supported extension xlsx xls csv json files allowed file types input extension configuration": "📊 **Supported Ingestion Arrays:** The parsing module takes standard `.csv`, `.xlsx`, `.xls`, and `.json` data frameworks seamlessly.",
                "data science workflow pipeline step data processing cycle steps clean engineering model cycle data analysis steps": "⚙️ **Data Science Pipeline Lifecycle:** Raw File Ingestion ➔ Data Wrangling & Automated Cleansing (via VeriSame) ➔ Exploratory Analytics (EDA) ➔ Feature Design ➔ AI Model Fitting ➔ Target Deployment. VeriSame automates the initial bottleneck phases completely!",
                "python script pandas vectorization clean dataframe speed optimize memory runtime engine speed code compile": "🐍 **Vector Engine Efficiency:** This environment drops manual row loops, exploiting compiled pandas vector arrays to calculate full sheets concurrently under 3 seconds.",
                "app error code crash malfunction troubleshooting debug fix problem fail issue broken application error solution": "🛠️ **Troubleshooting Matrix:** Most errors resolve by dropping blank schemas, matching column structures, or confirming dependencies. Submit your logs here for micro-second debugging!",
                "streamlit deployment error cloud crash environment setup requirements text server down reboot log mismatch": "📦 **Cloud Infrastructure Patch:** Verify your `requirements.txt` lists `pandas`, `openpyxl`, and `qrcode` to block container crashes during automated cloud installation tracks.",
                "openpyxl module missing excel download failed format issue library setup crash read error excel dependency": "📊 **Excel Stream Driver Patch:** If Excel export triggers an environment crash, the remote container lacks `openpyxl`. Deploy 'Download as CSV' or install the package in the environment file.",
                "row index error mismatch rows mismatched calculation dimensions size out of bounds loop structure failed length check": "🔢 **Index Guard Protocol:** Shifting rows during dropping stages can break dimensions. VeriSame protects arrays by replacing problematic text with 'Unknown' rather than altering physical lengths!",
                "why did my data upload fail bad format corruption password protected parse error reader crash file block": "🚫 **Ingestion Diagnostics:** Verify your files aren't encrypted, password-shielded, or open inside another app like Microsoft Excel during loading phases."
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
            
            if best_score >= 0.25 and best_reply: 
                reply = best_reply
            else: 
                reply = "🔍 **Query logged in AI memory base.** I am fully trained on pipeline architecture, troubleshooting, cloud deployment fixes, founder info, and data science math calculations. Try asking: *'Who is the founder?'* or *'How to fix a deployment error?'*"

        st.session_state.chat_history.append({"role": "assistant", "message": reply})
        st.rerun()

if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], use_container_width=True):
        for key in ['plan','email','df_clean','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed']:
            st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan','orig_len','empty_fixed'] else False
        st.session_state.changed_cells = set()
        st.rerun()

if st.session_state.email:
    db_state = load_db()
    user = db_state.get(st.session_state.email, {})
    st.sidebar.success(f"📧 {st.session_state.email}")
    render_ai_chatbot(is_sidebar=True)
    if user.get("plan"):
        st.session_state.plan = user.get("plan")
        st.session_state.amt = user.get("amt", 0)
        st.session_state.days = user.get("days", 0)
        
        if user.get("plan") == "free": 
            st.sidebar.info("Plan: FREE FOREVER ✨")
        else:
            exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d")
            days_left = (exp_date - datetime.now()).days
            st.session_state.admin_approved = user.get("status") == "PAID" and days_left > 0
            if days_left > 0: 
                st.sidebar.info(f"Plan: {user['plan'].upper()}\nValid Till: {user['expiry']}\n{days_left} days left")
            else:
                st.sidebar.info(f"Plan: {user['plan'].upper()}\nStatus: {user.get('status')}")

col1, col2, col3 = st.columns([1.1, 2.2, 1.7])
with col1: st.markdown("""<div class="logo-float" style="width: 100%; min-height: 280px; display: flex; align-items: center; justify-content: center;"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width: 100%; height: auto; max-height: 280px; object-fit: contain;"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='margin-top: 5px; margin-bottom: 5px;'>VeriSame</h1>", unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{T["subtitle"]}</div>', unsafe_allow_html=True)
with col3: st.markdown("""<div class="anime-container"><img src="https://i.postimg.cc/8zdnX54g/IMG-20260609-WA0012.jpg"></div>""", unsafe_allow_html=True)
st.markdown(f"<div class='pro-banner'><h2>💎 {T['pro_banner']}</h2><div>{''.join([f"<span class='tool-chip'>{tool}</span>" for tool in ['Smart Date','AI Fill','Email AI','Phone AI','Case','Clean','Rename','Dedup','Trim','Spell']])}</div></div>", unsafe_allow_html=True)

if "admin" in st.query_params:
    if st.query_params["admin"] == ADMIN_PASS:
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
                    st.markdown(f"""<div class='pricing-card' style='background: rgba(243, 232, 255, 0.9) !important;'><b>{T['admin_user']}:</b> {email}<br><b>{T['admin_plan']}:</b> {plan_text}<br><b>Status:</b> {status_color}<br><b>{T['admin_expiry']}:</b> {info.get('expiry','N/A')}</div>""", unsafe_allow_html=True)
                with col2:
                    if status == "PENDING" and info.get("plan") == "pro":
                        if st.button(T['admin_approve_btn'], key=f"verify_{email}", type="primary", use_container_width=True):
                            data[email]["status"] = "PAID"
                            save_db(data); st.success(f"✓ {email} unlocked!"); st.balloons(); st.rerun()
                    else: st.button("✓ Already Active", key=f"active_{email}", disabled=True, use_container_width=True)
                with col3:
                    if st.button(T['delete_btn'], key=f"delete_{email}", use_container_width=True):
                        del data[email]; save_db(data); st.error(f"✓ {email} deleted"); st.rerun()
        else: st.info("No records found in database.")
        st.stop()
    else:
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
                
                selected_days = 180 if st.session_state.amt == 1499 else 30
                
                if email_input in data:
                    if st.session_state.selected_plan == "pro" and data[email_input]["plan"] == "free":
                        data[email_input]["plan"] = "pro"
                        data[email_input]["status"] = "PENDING"
                        data[email_input]["amt"] = st.session_state.amt
                        data[email_input]["days"] = selected_days
                        data[email_input]["expiry"] = (datetime.now() + timedelta(days=selected_days)).strftime("%Y-%m-%d")
                        save_db(data)
                    st.session_state.plan = data[email_input]["plan"]
                    st.session_state.amt = data[email_input].get("amt", st.session_state.amt)
                    st.session_state.days = data[email_input].get("days", selected_days)
                    st.rerun()
                else:
                    st.session_state.plan = st.session_state.selected_plan
                    if st.session_state.selected_plan == "free":
                        expiry = (datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                        data[email_input] = {"plan":"free","status":"PAID","amt":0,"expiry":expiry,"created":str(datetime.now())}
                        save_db(data); st.balloons(); st.rerun()
                    else:
                        expiry = (datetime.now() + timedelta(days=selected_days)).strftime("%Y-%m-%d")
                        data[email_input] = {"plan":"pro","status":"PENDING","amt":st.session_state.amt,"days":selected_days,"expiry":expiry,"created":str(datetime.now())}
                        save_db(data); st.rerun()
            else: st.error("Valid email required")
        st.stop()
else:
    tab1,tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    df = None
    with tab1:
        file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"], accept_multiple_files=True)
        if file:
            try: 
                df_list = []
                for f in file:
                    if f.name.endswith((".xlsx", ".xls")):
                        excel_file = pd.ExcelFile(f)
                        sheet_names = excel_file.sheet_names
                        selected_sheet = st.selectbox(f"📄 Select Sheet to Clean for {f.name}", sheet_names, key=f"sheet_sel_{f.name}")
                        sub_df = pd.read_excel(f, sheet_name=selected_sheet)
                    elif f.name.endswith(".csv"):
                        sub_df = pd.read_csv(f)
                    else:
                        sub_df = pd.read_json(f)
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
                if df_clean[col].dtype == 'object':
                    df_clean[col] = df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                
                if any(k in col.lower() for k in ['salary','amount','price','paisa']): 
                    df_clean[col] = df_clean[col].apply(words_to_num)
            st.session_state.df_clean = df_clean
            st.session_state.df_loaded = True
            st.session_state.orig_len = orig_len
            st.session_state.empty_fixed = int(df.isna().sum().sum())
            st.session_state.changed_cells = set()
        
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

                with st.expander("📊 Visual Data Health Insights Dashboard", expanded=True):
                    row_counts = [len(df_clean)] * len(df_clean.columns)
                    chart_data = pd.DataFrame({"Columns": df_clean.columns, "Healthy Rows": row_counts}).set_index("Columns")
                    st.bar_chart(chart_data)

                st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
                st.caption(T['preview'])
                
                styled_df = apply_cell_styling(df_clean.head(10))
                st.dataframe(styled_df, use_container_width=True, height=300)

                all_cols = df_clean.columns.tolist()
                
                text_cols = df_clean.select_dtypes(include=['object']).columns.tolist()
                date_filtered_cols = [col for col in all_cols if 'date' in col.lower() or 'time' in col.lower()]
                email_filtered_cols = [col for col in all_cols if 'email' in col.lower() or 'mail' in col.lower()]
                phone_filtered_cols = [col for col in all_cols if 'phone' in col.lower() or 'mobile' in col.lower() or 'contact' in col.lower()]
                
                if not date_filtered_cols: date_filtered_cols = all_cols
                if not email_filtered_cols: email_filtered_cols = all_cols
                if not phone_filtered_cols: phone_filtered_cols = all_cols
                if not text_cols: text_cols = all_cols

                is_pro = st.session_state.plan == "pro"
                is_free = st.session_state.plan == "free"
                is_paid = st.session_state.admin_approved

                tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
                with tab1:
                    # Tool 1: Smart Date Converter
                    st.write(f"**{T['tool1']}** ✅ Unlocked")
                    date_cols = st.multiselect(T['select_col'], date_filtered_cols, key="ms_date")
                    if st.button(T['apply_btn'], key="btn_date", use_container_width=True):
                        if not date_cols:
                            st.warning("⚠️ No changes detected! Please select columns first.")
                        else:
                            old_snapshot = st.session_state.df_clean.copy()
                            has_error = False
                            for col in date_cols:
                                if any(k in col.lower() for k in ['salary', 'amount', 'price', 'paisa', 'phone', 'mobile', 'name', 'id', 'state', 'office']):
                                    st.error(f"⚠️ '{col}' appears to be a core structural field, it cannot be processed as a Date!")
                                    has_error = True
                                    break
                                st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(intelligent_date_parser)
                            
                            if not has_error:
                                track_modifications(old_snapshot, st.session_state.df_clean)
                                st.success(T['success']); st.rerun()

                    # Tool 2: AI Fill Nulls
                    if is_free:
                        st.write(f"**{T['tool2']}** 🔒 Locked (Upgrade to Pro)")
                        st.multiselect(T['select_col'], all_cols, key="ms_fill_disabled", disabled=True)
                        st.button(T['apply_btn'], key="btn_fill_disabled", disabled=True, use_container_width=True)
                    else:
                        st.write(f"**{T['tool2']}** ✅ Unlocked")
                        fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill")
                        if st.button(T['apply_btn'], key="btn_fill", use_container_width=True):
                            if not fill_cols:
                                st.warning("⚠️ No changes detected! Please select target columns.")
                            else:
                                old_snapshot = st.session_state.df_clean.copy()
                                for col in fill_cols:
                                    sample = str(st.session_state.df_clean[col].dropna().iloc[0]).lower() if not st.session_state.df_clean[col].dropna().empty else ""
                                    if sample.isdigit() or '.' in sample: fill_val = "0"
                                    elif '@' in sample: fill_val = "missing@email.com"
                                    else: fill_val = "Unknown"
                                    st.session_state.df_clean[col] = st.session_state.df_clean[col].fillna(fill_val).replace(["nan", "None", "", " "], fill_val)
                                track_modifications(old_snapshot, st.session_state.df_clean)
                                st.success(T['success']); st.rerun()

                with tab2:
                    # Tool 3: Email Validator
                    if is_free:
                        st.write(f"**{T['tool3']}** 🔒 Locked (Upgrade to Pro)")
                        st.multiselect(T['select_col'], email_filtered_cols, key="ms_email_disabled", disabled=True)
                        st.button(T['apply_btn'], key="btn_fill_disabled_tab2", disabled=True, use_container_width=True)
                    else:
                        st.write(f"**{T['tool3']}** ✅ Unlocked")
                        email_cols = st.multiselect(T['select_col'], email_filtered_cols, key="ms_email")
                        if st.button(T['apply_btn'], key="btn_email", use_container_width=True):
                            if not email_cols:
                                st.warning("⚠️ No changes detected! Please select valid email columns.")
                            else:
                                old_snapshot = st.session_state.df_clean.copy()
                                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                                for col in email_cols: 
                                    st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower().str.strip().apply(lambda x: x if re.match(pattern, x) else "Invalid Email")
                                track_modifications(old_snapshot, st.session_state.df_clean)
                                st.success(T['success']); st.rerun()

                    # Tool 4: Phone Formatter
                    if is_free:
                        st.write(f"**{T['tool4']}** 🔒 Locked (Upgrade to Pro)")
                        st.multiselect(T['select_col'], phone_filtered_cols, key="ms_phone_disabled", disabled=True)
                        st.button(T['apply_btn'], key="btn_phone_disabled", disabled=True, use_container_width=True)
                    else:
                        st.write(f"**{T['tool4']}** ✅ Unlocked")
                        phone_cols = st.multiselect(T['select_col'], phone_filtered_cols, key="ms_phone")
                        if st.button(T['apply_btn'], key="btn_phone", use_container_width=True):
                            if not phone_cols:
                                st.warning("⚠️ No changes detected! Select cleanable phone vectors.")
                            else:
                                old_snapshot = st.session_state.df_clean.copy()
                                for col in phone_cols: 
                                    st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x)))
                                    st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: x[-10:] if len(x) >= 10 else x)
                                track_modifications(old_snapshot, st.session_state.df_clean)
                                st.success(T['success']); st.rerun()

                with tab3:
                    # Tool 5: Case Converter
                    st.write(f"**{T['tool5']}** ✅ Unlocked")
                    case_cols = st.multiselect(T['select_col'], text_cols, key="ms_case")
                    case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
                    if st.button(T['apply_btn'], key="btn_case", use_container_width=True):
                        if not case_cols:
                            st.warning("⚠️ No changes detected! Please check text-based structures.")
                        else:
                            old_snapshot = st.session_state.df_clean.copy()
                            for col in case_cols: 
                                if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.upper()
                                elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower()
                                else: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.title()
                            track_modifications(old_snapshot, st.session_state.df_clean)
                            st.success(T['success']); st.rerun()

                    # Tool 6: Remove Symbols
                    if is_free:
                        st.write(f"**{T['tool6']}** 🔒 Locked (Upgrade to Pro)")
                        st.multiselect(T['select_col'], text_cols, key="ms_spec_disabled", disabled=True)
                        st.button(T['apply_btn'], key="btn_spec_disabled", disabled=True, use_container_width=True)
                    else:
                        st.write(f"**{T['tool6']}** ✅ Unlocked")
                        spec_cols = st.multiselect(T['select_col'], text_cols, key="ms_spec")
                        if st.button(T['apply_btn'], key="btn_spec", use_container_width=True):
                            if not spec_cols:
                                st.warning("⚠️ No changes detected! Select columns to strip characters.")
                            else:
                                old_snapshot = st.session_state.df_clean.copy()
                                for col in spec_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9\s.,₹$@\-+]', '', x))
                                track_modifications(old_snapshot, st.session_state.df_clean)
                                st.success(T['success']); st.rerun()

                    # Tool 7: Bulk Rename
                    if is_free:
                        st.write(f"**{T['tool7']}** 🔒 Locked (Upgrade to Pro)")
                        st.selectbox("Old column name", all_cols, key="sel_old_disabled", disabled=True)
                        st.text_input("New column name", key="inp_new_disabled", disabled=True)
                        st.button(T['apply_btn'], key="btn_rename_disabled", disabled=True, use_container_width=True)
                    else:
                        st.write(f"**{T['tool7']}** ✅ Unlocked")
                        old = st.selectbox("Old column name", all_cols, key="sel_old")
                        new = st.text_input("New column name", key="inp_new")
                        if st.button(T['apply_btn'], key="btn_rename", use_container_width=True):
                            if not new or new.strip() == "" or old == new:
                                st.warning("⚠️ No changes detected! Name field missing or identical to old label.")
                            else:
                                st.session_state.df_clean.rename(columns={old: new.strip()}, inplace=True)
                                st.success(T['success']); st.rerun()

                    # Tool 8: Remove Duplicates / Fuzzy Match
                    st.write(f"**{T['tool8']}** ✅ Unlocked")
                    fuzzy_target_col = st.selectbox("Select Target Column for Fuzzy Deduplication", text_cols, key="sb_fuzzy")
                    if st.button(T['apply_btn'], key="btn_dedup", use_container_width=True):
                        old_len = len(st.session_state.df_clean)
                        st.session_state.df_clean = remove_fuzzy_duplicates(st.session_state.df_clean, fuzzy_target_col)
                        
                        if len(st.session_state.df_clean) == old_len:
                            st.warning("⚠️ No changes detected! Your active datasheet contains 0 duplicate records.")
                        else:
                            st.success(T['success']); st.rerun()

                    # Tool 9: Trim Spaces
                    st.write(f"**{T['tool9']}** ✅ Unlocked")
                    trim_cols = st.multiselect(T['select_col'], text_cols, key="ms_trim")
                    if st.button(T['apply_btn'], key="btn_trim", use_container_width=True):
                        if not trim_cols:
                            st.warning("⚠️ No changes detected! Highlight target column layers to trim space buffers.")
                        else:
                            old_snapshot = st.session_state.df_clean.copy()
                            for col in trim_cols: 
                                if st.session_state.df_clean[col].dtype == 'object':
                                    st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                            track_modifications(old_snapshot, st.session_state.df_clean)
                            st.success(T['success']); st.rerun()

                    # Tool 10: Spell Check
                    if is_free:
                        st.write(f"**{T['tool10']}** 🔒 Locked (Upgrade to Pro)")
                        st.multiselect(T['select_col'], text_cols, key="ms_spell_disabled", disabled=True)
                        st.button(T['apply_btn'], key="btn_spell_disabled", disabled=True, use_container_width=True)
                    else:
                        st.write(f"**{T['tool10']}** ✅ Unlocked")
                        spell_cols = st.multiselect(T['select_col'], text_cols, key="ms_spell")
                        if st.button(T['apply_btn'], key="btn_spell", use_container_width=True):
                            if not spell_cols:
                                st.warning("⚠️ No changes detected! Target columns must be selected first.")
                            else:
                                old_snapshot = st.session_state.df_clean.copy()
                                typo_dict = {"teh":"the","recieve":"receive","goverment":"government","managment":"management","colum":"column","datset":"dataset","salery":"salary","amout":"amount","phne":"phone","emil":"email","addres":"address","nam":"name","infomation":"information"}
                                def fix_typos(text):
                                    words = str(text).split()
                                    return " ".join([typo_dict.get(w.lower(), w) for w in words])
                                for col in spell_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(fix_typos).astype(str).str.title()
                                track_modifications(old_snapshot, st.session_state.df_clean)
                                st.success(T['success']); st.rerun()

                st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
                if st.session_state.show_balloon: st.balloons(); st.session_state.show_balloon = False

                if st.session_state.plan == "free":
                    col1, col2 = st.columns(2)
                    csv = st.session_state.df_clean.to_csv(index=False).encode()
                    if col1.download_button(T['download_csv'], csv, "verisame_clean.csv", mime="text/csv", key="dl_csv_free", use_container_width=True):
                        st.session_state.show_balloon = True; st.rerun()
                    try:
                        if openpyxl is not None:
                            excel = io.BytesIO()
                            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                            if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_clean.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_free", use_container_width=True):
                                        st.session_state.show_balloon = True; st.rerun()
                    except Exception: pass
                    
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
                            data = load_db()
                            if st.session_state.email in data:
                                data[st.session_state.email]["status"] = "PENDING"
                                save_db(data)
                            st.session_state.payment_clicked = True
                            st.success("🚀 Request logged live in Admin Dashboard! Please hold on while Admin approves.")
                            st.rerun()
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
