import streamlit as st
import json, os, io
import pandas as pd
import re
from datetime import datetime, timedelta

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
ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "sherni_admin")

# 🎵 BACKGROUND MUSIC SYSTEM INTEGRATION
MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" 

st.markdown(f"""
    <iframe src="{MUSIC_URL}" allow="autoplay" style="display:none" id="iframeAudio"></iframe>
    <audio autoplay loop volume="0.3" style="display:none;">
        <source src="{MUSIC_URL}" type="audio/mp3">
    </audio>
""", unsafe_allow_html=True)

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

# ROBUST WORD-TO-NUMBER CONVERSION
def words_to_num(s):
    if pd.isna(s): return s
    s_str = str(s).lower().strip()
    if s_str.isdigit(): 
        return int(s_str)
    try:
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

T = {
    "title":"VeriSame","subtitle":"The Fastest Way to Clean Your Data","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"MONTHLY","pro6_title":"6 MONTHS",
    "free_feat":["1000 Rows Limit","CSV & Excel Export","4 Free Tools Built-in","30s Processing","Email Support"],
    "pro_feat":["Unlimited Rows","CSV + Excel Export","10 Premium AI Tools","3s Speed","Priority Support","No Watermark","Lifetime Updates"],
    "email_label":"Enter your email address","continue_btn":"Verify & Continue","upload_tab":"📤 Upload File","sample_tab":"🎯 Try Demo",
    "upload_text":"Drop CSV, Excel or JSON file here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview",
    "tools_menu":"AI Studio","back_btn":"← Back","download_title":"Export Data",
    "paid_msg":"Step 1: Pay via UPI QR Code. Step 2: Click 'Customer I Paid' button. Step 3: Admin will approve and unlock download.",
    "upi_text":"Scan QR to Pay ₹{amount}","paid_btn":"Customer I Paid ₹{amount}","wait_approval":"⏳ Waiting for Admin Approval... Click I Paid after payment",
    "download_success":"🎉 Download Ready!","tab1":"Date & Nulls","tab2":"Email & Phone","tab3":"Text Tools",
    "tool1":"Smart Date Converter","tool2":"AI Fill Nulls","tool3":"Email Validator","tool4":"Phone Formatter","tool5":"Case Converter",
    "tool6":"Remove Symbols","tool7":"Bulk Rename","tool8":"Remove Duplicates","tool9":"Trim Spaces","tool10":"Spell Check",
    "select_col":"Select Columns","select_case":"Choose Case Type","apply_btn":"Apply","success":"Apply is completed! Your data has been successfully updated.",
    "admin_title":"👑 Sherni Admin Panel 👑","admin_pending":"User Databases & Requests","admin_approve_btn":"Mark Paid - Unlock Customer Download",
    "admin_user":"Customer Email","admin_plan":"Plan","admin_expiry":"Valid Till","delete_btn":"Delete User","download_csv":"Download as CSV","download_excel":"Download as Excel"
}

# ANTI-DARK MODE ENFORCED GLOSSY CSS WITH LARGE ORIGINAL FRONT LAYOUT
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}

.stApp {
    background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 25%, #d8b4fe 50%, #c084fc 75%, #a855f7 100%) !important; 
    background-size: 400% 400% !important; 
    animation: aurora 20s ease infinite !important; 
    padding-top: 0.1rem !important;
}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}

.block-container {
    background: rgba(255,255,255,0.97) !important; 
    backdrop-filter: blur(30px) saturate(200%) !important; 
    border-radius: 30px !important; 
    padding: 2.5rem !important; 
    max-width: 1240px; 
    margin: 1.5rem auto !important; 
    box-shadow: 0 40px 80px rgba(147,51,234,0.18) !important; 
    border: 2px solid rgba(255,255,255,0.7) !important;
}

/* Original Large Front Header Section Layout */
.hero-wrapper {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 30px;
    margin-bottom: 40px;
    background: white;
    padding: 35px;
    border-radius: 32px;
    box-shadow: 0 20px 50px rgba(147,51,234,0.08);
}
.hero-left { display: flex; align-items: center; gap: 25px; flex: 1; min-width: 320px; }
.hero-logo img { width: 110px; height: auto; border-radius: 24px; }
.hero-text h1 { font-size: 4.2rem !important; font-weight: 900 !important; margin: 0 !important; color: #4c1d95 !important; line-height: 1.1; }
.hero-text p { font-size: 1.4rem !important; margin-top: 8px !important; color: #6b7280 !important; font-weight: 500; }
.hero-anime img { width: 100%; max-width: 260px; height: auto; border-radius: 28px; object-fit: cover; }

/* Pricing Cards Bada Size */
.pricing-card {
    position: relative; border-radius: 28px; padding: 2.5rem; background: linear-gradient(145deg, #ffffff, #fefeff)!important;
    backdrop-filter: blur(15px); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    box-shadow: 0 20px 40px rgba(147,51,234,0.08);
    height: 100%; border: 2.5px solid #e9d5ff !important;
    margin-bottom: 25px;
}
.pricing-card h2 {font-size: 1.8rem!important; color: #6d28d9!important; margin-bottom: 0.8rem!important; font-weight: 800;}
.pricing-card h1 {font-size: 3.8rem!important; color: #4c1d95!important; margin: 0.8rem 0!important; font-weight: 900;}
.pricing-card p {font-size: 1.1rem!important; color: #4b5563;}

.stButton>button {
    border-radius: 20px !important; 
    font-weight: 800 !important; 
    background: linear-gradient(90deg, #7c3aed, #a855f7) !important; 
    color: white !important; 
    border: none !important; 
    padding: 16px 32px !important; 
    width: 100% !important; 
    box-shadow: 0 10px 25px rgba(124,58,237,0.3) !important; 
    font-size: 1.2rem !important;
}

.qr-container {
    background: #ffffff;
    padding: 20px;
    border-radius: 24px;
    border: 3px solid #a855f7;
    text-align: center;
    margin: 20px auto;
    max-width: 260px;
    box-shadow: 0 15px 35px rgba(147,51,234,0.15);
}

.cherry {position: fixed; top: -10vh; color: #FFB7C5; font-size: 22px; animation: fall linear infinite; z-index: 9999; pointer-events: none;}
@keyframes fall {0%{transform: translateY(0vh) translateX(0vw) rotate(0deg); opacity: 1;} 100%{transform: translateY(110vh) translateX(10vw) rotate(360deg); opacity: 0;}}
</style>
<div class="cherry" style="left: 15%; animation-duration: 8s;">🌸</div>
<div class="cherry" style="left: 45%; animation-duration: 10s; animation-delay: 2s;">🌸</div>
<div class="cherry" style="left: 75%; animation-duration: 9s; animation-delay: 4s;">🌸</div>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame's Smart AI Studio. 💎 Ask me anything about our workflows, specific tools, safety, troubleshooting errors, or data science utilities!"}]

for key in ['plan','email','df_clean','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan','orig_len','empty_fixed'] else False

# AI CHATBOT STUDIO ENGINE (STRICT ENGLISH ENFORCED)
def render_ai_chatbot(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 VeriSame Live AI Chat Studio")

    chat_html = "<div style='max-height: 240px; overflow-y: auto; padding: 12px; background: #ffffff !important; border: 2px solid #7c3aed; border-radius: 16px; margin-bottom: 12px;'>"
    for chat in st.session_state.chat_history:
        if chat["role"] == "assistant":
            chat_html += f"<p style='color: #6d28d9 !important; margin: 4px 0; font-weight: 700;'><b>🤖 AI:</b> {chat['message']}</p>"
        else:
            chat_html += f"<p style='color: #111827 !important; margin: 4px 0; font-weight: 600;'><b>👤 You:</b> {chat['message']}</p>"
    chat_html += "</div>"
    target.markdown(chat_html, unsafe_allow_html=True)

    s_id = "side" if is_sidebar else "main"
    user_msg = target.text_input("Ask a question...", placeholder="e.g., How does Tool 4 work?", key=f"chat_in_{s_id}")
    submit = target.button("Send Message 🚀", key=f"btn_send_chat_{s_id}")

    if submit and user_msg and user_msg.strip():
        u = user_msg.lower().strip()
        st.session_state.chat_history.append({"role": "user", "message": user_msg})
        reply = None

        if "tool 1" in u or "date converter" in u or "smart date" in u:
            reply = "📅 **Tool 1: Smart Date Converter (FREE)**\n\n**Function:** This utility transforms mixed or incorrectly formatted dates inside selected columns into a single standardized format (`YYYY-MM-DD`)."
        elif "tool 2" in u or "fill null" in u or "ai fill" in u:
            reply = "🔒 **Tool 2: AI Fill Nulls (PRO ONLY)**\n\n**Function:** This tool intelligently inspects blank or empty cells (NaN/Null) across data records and updates them based on contextual attributes."
        elif "tool 3" in u or "email validator" in u or "email ai" in u:
            reply = "🔒 **Tool 3: Email Validator (PRO ONLY)**\n\n**Function:** Validates structure patterns for emails across records, automatically replacing faulty inputs with an `Invalid Email` flag."
        elif "tool 4" in u or "phone formatter" in u or "phone ai" in u:
            reply = "🔒 **Tool 4: Phone Formatter (PRO ONLY)**\n\n**Function:** Strips out unwanted characters, spaces, and formatting flags to preserve a clean **10-digit mobile number**."
        elif "tool 5" in u or "case converter" in u:
            reply = "🔠 **Tool 5: Case Converter (FREE)**\n\n**Function:** Instantly normalizes layout configurations by converting text inputs into **UPPERCASE**, **lowercase**, or **Title Case** layouts."
        elif "tool 6" in u or "remove symbol" in u:
            reply = "🔒 **Tool 6: Remove Symbols (PRO ONLY)**\n\n**Function:** Removes unwanted junk data characters and special symbols while keeping essential currency parameters safe."
        elif "tool 7" in u or "bulk rename" in u or "rename column" in u:
            reply = "🔒 **Tool 7: Bulk Rename (PRO ONLY)**\n\n**Function:** Dynamically renames specific tracking attributes and header configurations inside the file."
        elif "tool 8" in u or "remove duplicate" in u or "dedup" in u:
            reply = "🔁 **Tool 8: Remove Duplicates (FREE)**\n\n**Function:** Scans structural duplicates and immediately purges duplicate entries to retain unique row indices."
        elif "tool 9" in u or "trim space" in u or "trimming" in u:
            reply = "✂️ **Tool 9: Trim Spaces (FREE)**\n\n**Function:** Trims annoying trailing and leading white spaces from target strings automatically."
        elif "tool 10" in u or "spell check" in u:
            reply = "🔒 **Tool 10: Spell Check (PRO ONLY)**\n\n**Function:** Cross-checks core structures to dynamically fix common typographical or spelling mistakes."
        elif any(x in u for x in ["thank you", "thanks", "thx"]): reply = "💖 **You are most welcome!** Happy to optimize your data workflow."
        elif any(x in u for x in ["hi", "hello", "hey"]): reply = "👋 **Hello there!** Welcome to VeriSame! How can I speed up your workflows today?"

        if not reply:
            knowledge_map = {
                "founder made creator created developer owner built make kaun banaya owner kaun anugya singh app architecture who designed": "👑 **Founder & Creator:** VeriSame was architected, designed, and developed entirely by **Anugya Singh**!",
                "what this app can do what is app work app capability utility function software use details purpose system tool utility": "💎 **VeriSame App Capability:** This app functions as an automated data-cleaning pipeline! It repairs empty boxes, formats dates, filters emails, and converts word numbers into clean integers under 3 seconds!"
            }
            best_score = 0.0
            best_reply = None
            user_words = u.split()
            for key_string, answer_text in knowledge_map.items():
                key_words = key_string.split()
                matched_words = sum(1 for w in user_words if w in key_words)
                word_ratio = matched_words / max(1, len(user_words))
                if word_ratio > best_score:
                    best_score = word_ratio
                    best_reply = answer_text
            if best_score >= 0.25 and best_reply: reply = best_reply
            else: reply = "🔍 I can assist you with our pipelines or features (Tool 1 to Tool 10). Simply specify a tool name or ask a question!"

        st.session_state.chat_history.append({"role": "assistant", "message": reply})
        st.rerun()

if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], use_container_width=True):
        for key in ['plan','email','df_clean','payment_clicked','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed']:
            st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan','orig_len','empty_fixed'] else False
        st.rerun()

if st.session_state.email:
    db_state = load_db()
    user = db_state.get(st.session_state.email, {})
    st.sidebar.success(f"📧 {st.session_state.email}")
    render_ai_chatbot(is_sidebar=True)
    
    if st.session_state.plan == "free": 
        st.sidebar.markdown("<div style='background-color:#E8F5E9; padding:12px; border-radius:8px; border-left:5px solid #2E7D32;'><b>Plan: FREE FOREVER</b><br><span style='font-size:12px; color:#4CAF50;'>4 Free Tools Only</span></div>", unsafe_allow_html=True)
    else:
        exp_date = datetime.strptime(user.get("expiry", (datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d")), "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days
        st.session_state.admin_approved = user.get("status") == "PAID" and days_left > 0
        st.sidebar.info(f"Plan: PRO VERSION\nValid Till: {user.get('expiry')}\n{days_left} days left")

# BADA FRONT BANNER WITH NO EXTRA PADDING BREAKS
st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-left">
        <div class="hero-logo">
            <img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" alt="VeriSame Logo">
        </div>
        <div class="hero-text">
            <h1>VeriSame</h1>
            <p>{T["subtitle"]}</p>
        </div>
    </div>
    <div class="hero-anime">
        <img src="https://i.postimg.cc/8zdnX54g/IMG-20260609-WA0012.jpg" alt="Anime Banner">
    </div>
</div>
""", unsafe_allow_html=True)

# PLAN SETUP INTERFACE
if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        col1,col2,col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f"""<div class='pricing-card'><h2>{T['free_title']}</h2><h1>FREE</h1><p>Lifetime</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['free_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan = "free"; st.rerun()
        with col2:
            st.markdown(f"""<div class='pricing-card' style='border: 3px solid #7c3aed;'><p>⭐ POPULAR</p><h2>{T['pro1_title']}</h2><h1>₹299</h1><p>30 Days</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"; st.session_state.amt = PRO_1M; st.session_state.days = 30; st.rerun()
        with col3:
            st.markdown(f"""<div class='pricing-card'><h2>{T['pro6_title']}</h2><h1>₹1499</h1><p>180 Days</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
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
                
                if st.session_state.selected_plan == "free":
                    st.session_state.plan = "free"
                    expiry = (datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                    data[email_input] = {"plan":"free","status":"PAID","amt":0,"expiry":expiry,"created":str(datetime.now())}
                    save_db(data); st.rerun()
                else:
                    st.session_state.plan = "pro"
                    days = 30 if st.session_state.amt == 299 else 180
                    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                    data[email_input] = {"plan":"pro","status":"PENDING","amt":st.session_state.amt,"days":days,"expiry":expiry,"created":str(datetime.now())}
                    save_db(data); st.rerun()
            else: st.error("Valid email required")
        st.stop()
else:
    # CORE CLEANING PIPELINE ENGINE
    tab1,tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    df = None
    with tab1:
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
        orig_len = len(df)
        is_free = (st.session_state.plan == "free")
        
        if is_free and orig_len > 1000:
            st.error(f"⚠️ Limits Exceeded: Free Plan allows up to 1000 rows only. Your dataset has {orig_len} rows. Please upgrade to use unlimited row parsing.")
            st.stop()

        if 'df_loaded' not in st.session_state or not st.session_state.df_loaded:
            st.session_state.df_clean = df.copy()
            df_clean = st.session_state.df_clean.drop_duplicates()
            for col in df_clean.columns:
                if df_clean[col].dtype == object:
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
                st.dataframe(df_clean.head(10), use_container_width=True, height=260)

                all_cols = df_clean.columns.tolist()
                tab1_ui, tab2_ui, tab3_ui = st.tabs([T['tab1'], T['tab2'], T['tab3']])
                
                with tab1_ui:
                    with st.container():
                        st.write(f"**{T['tool1']}** ✅ Unlocked (Free + Pro)")
                        date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date")
                        if st.button(T['apply_btn'], key="btn_date", use_container_width=True):
                            for col in date_cols: 
                                try:
                                    try: converted = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', format='mixed', dayfirst=True)
                                    except TypeError: converted = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', dayfirst=True)
                                    st.session_state.df_clean[col] = converted.dt.strftime('%Y-%m-%d').fillna("None")
                                except Exception: pass
                            st.success(T['success'])

                    with st.container():
                        st.write(f"**{T['tool2']}** {'🔒 Locked (Pro Plan Only)' if is_free else '✅ Unlocked'}")
                        fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=is_free)
                        if st.button(T['apply_btn'], key="btn_fill", use_container_width=True, disabled=is_free):
                            for col in fill_cols:
                                sample = str(st.session_state.df_clean[col].dropna().iloc[0]).lower() if not st.session_state.df_clean[col].dropna().empty else ""
                                fill_val = "0" if (sample.isdigit() or '.' in sample) else "missing@email.com" if '@' in sample else "Unknown"
                                st.session_state.df_clean[col] = st.session_state.df_clean[col].fillna(fill_val).replace(["nan", "None", "", " "], fill_val)
                            st.success(T['success'])

                with tab2_ui:
                    with st.container():
                        st.write(f"**{T['tool3']}** {'🔒 Locked (Pro Plan Only)' if is_free else '✅ Unlocked'}")
                        email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=is_free)
                        if st.button(T['apply_btn'], key="btn_email", use_container_width=True, disabled=is_free):
                            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                            for col in email_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower().str.strip().apply(lambda x: x if re.match(pattern, x) else "Invalid Email")
                            st.success(T['success'])

                    with st.container():
                        st.write(f"**{T['tool4']}** {'🔒 Locked (Pro Plan Only)' if is_free else '✅ Unlocked'}")
                        phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=is_free)
                        if st.button(T['apply_btn'], key="btn_phone", use_container_width=True, disabled=is_free):
                            for col in phone_cols: 
                                st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x)))
                                st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: x[-10:] if len(x) >= 10 else x)
                            st.success(T['success'])

                with tab3_ui:
                    with st.container():
                        st.write(f"**{T['tool5']}** ✅ Unlocked (Free + Pro)")
                        case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
                        case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
                        if st.button(T['apply_btn'], key="btn_case", use_container_width=True):
                            for col in case_cols: 
                                if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.upper()
                                elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower()
                                else: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.title()
                            st.success(T['success'])

                    with st.container():
                        st.write(f"**{T['tool6']}** {'🔒 Locked (Pro Plan Only)' if is_free else '✅ Unlocked'}")
                        spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec", disabled=is_free)
                        if st.button(T['apply_btn'], key="btn_spec", use_container_width=True, disabled=is_free):
                            for col in spec_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9\s.,₹$@\-+]', '', x))
                            st.success(T['success'])

                    with st.container():
                        st.write(f"**{T['tool7']}** {'🔒 Locked (Pro Plan Only)' if is_free else '✅ Unlocked'}")
                        old = st.selectbox("Old column name", all_cols, key="sel_old", disabled=is_free)
                        new = st.text_input("New column name", key="inp_new", disabled=is_free)
                        if st.button(T['apply_btn'], key="btn_rename", use_container_width=True, disabled=is_free) and new:
                            st.session_state.df_clean.rename(columns={old: new}, inplace=True)
                            st.success(T['success'])

                    with st.container():
                        st.write(f"**{T['tool8']}** ✅ Unlocked (Free + Pro)")
                        if st.button(T['apply_btn'], key="btn_dedup", use_container_width=True):
                            st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                            st.success(T['success'])

                    with st.container():
                        st.write(f"**{T['tool9']}** ✅ Unlocked (Free + Pro)")
                        trim_cols = st.multiselect(T['select_col'], all_cols, key="ms_trim")
                        if st.button(T['apply_btn'], key="btn_trim", use_container_width=True):
                            for col in trim_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                            st.success(T['success'])

                    with st.container():
                        st.write(f"**{T['tool10']}** {'🔒 Locked (Pro Plan Only)' if is_free else '✅ Unlocked'}")
                        spell_cols = st.multiselect(T['select_col'], all_cols, key="ms_spell", disabled=is_free)
                        if st.button(T['apply_btn'], key="btn_spell", use_container_width=True, disabled=is_free):
                            typo_dict = {"teh":"the","recieve":"receive","goverment":"government","managment":"management","colum":"column"}
                            def fix_typos(text):
                                words = str(text).split()
                                return " ".join([typo_dict.get(w.lower(), w) for w in words])
                            for col in spell_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(fix_typos).astype(str).str.title()
                            st.success(T['success'])

                st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
                if st.session_state.show_balloon: st.balloons(); st.session_state.show_balloon = False

                # DOWNLOAD & PAYMENT SYSTEM (AUTOMATIC QR GENERATOR ENABLED)
                if is_free:
                    col1, col2 = st.columns(2)
                    csv = st.session_state.df_clean.to_csv(index=False).encode()
                    if col1.download_button(T['download_csv'], csv, "verisame_free.csv", mime="text/csv", key="dl_csv_free", use_container_width=True): st.session_state.show_balloon = True
                    if openpyxl is not None:
                        excel = io.BytesIO()
                        st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                        if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_free.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_free", use_container_width=True): st.session_state.show_balloon = True
                else:
                    if not st.session_state.admin_approved:
                        st.warning(T['wait_approval'])
                        
                        # ✨ DYNAMIC UPI QR CODE
                        if qrcode is not None:
                            pay_url = f"upi://pay?pa={UPI}&pn=VeriSamePro&am={st.session_state.amt}&cu=INR"
                            qr = qrcode.QRCode(version=1, box_size=10, border=2)
                            qr.add_data(pay_url)
                            qr.make(fit=True)
                            img = qr.make_image(fill_color="black", back_color="white")
                            
                            buf = io.BytesIO()
                            img.save(buf, format="PNG")
                            
                            st.markdown(f"<div class='qr-container'><p style='color:#7c3aed !important; margin-bottom:10px;'>Scan QR to Pay ₹{st.session_state.amt}</p></div>", unsafe_allow_html=True)
                            st.image(buf.getvalue(), width=220, use_column_width=False)
                        else:
                            st.info(f"Send payment directly to UPI ID: {UPI}")
                            
                        if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary", use_container_width=True):
                            data = load_db()
                            if st.session_state.email in data: data[st.session_state.email]["status"] = "PENDING"
                            save_db(data)
                            st.success("🚀 Request logged live in Admin Panel!")
                    else:
                        col1, col2 = st.columns(2)
                        csv = st.session_state.df_clean.to_csv(index=False).encode()
                        if col1.download_button(T['download_csv'], csv, "verisame_pro.csv", mime="text/csv", key="dl_csv_paid", use_container_width=True): st.session_state.show_balloon = True
                        if openpyxl is not None:
                            excel = io.BytesIO()
                            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                            if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_pro.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_paid", use_container_width=True): st.session_state.show_balloon = True
        except Exception: pass
