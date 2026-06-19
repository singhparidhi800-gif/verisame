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

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
ADMIN_PASSWORD = "sherni_power"  # Aapka admin password

# 🎵 PEACEFUL AUDIO & INTERACTIVE BUTTON SOUND ENGINE
BACKGROUND_MUSIC = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"
CLICK_SOUND = "https://assets.mixkit.co/active_storage/sfx/2571/2571-84.wav"

st.markdown(f"""
    <audio id="bgMusic" autoplay>
        <source src="{BACKGROUND_MUSIC}" type="audio/mp3">
    </audio>
    <audio id="clickSound" src="{CLICK_SOUND}" preload="auto"></audio>

    <script>
        var bg = document.getElementById("bgMusic");
        if(bg) {{
            bg.volume = 0.20;
            setTimeout(function() {{
                bg.pause();
            }}, 20000); // 20 Seconds Auto-Stop
        }}

        function playClick() {{
            var snd = document.getElementById("clickSound");
            if(snd) {{
                snd.currentTime = 0;
                snd.volume = 0.4;
                snd.play();
            }}
        }}

        document.addEventListener("DOMContentLoaded", function() {{
            const targetNode = document.body;
            const config = {{ childList: true, subtree: true }};
            const callback = function(mutationsList, observer) {{
                let buttons = document.querySelectorAll("button");
                buttons.forEach(function(btn) {{
                    if (!btn.hasAttribute("data-click-bound")) {{
                        btn.setAttribute("data-click-bound", "true");
                        btn.addEventListener("click", playClick);
                    }}
                }});
            }};
            const observer = new MutationObserver(callback);
            observer.observe(targetNode, config);
        }});
    </script>
""", unsafe_allow_html=True)

# DATABASE MANAGEMENT
if "global_db_backup" not in st.session_state:
    st.session_state.global_db_backup = {}

def load_db():
    if st.session_state.global_db_backup: return st.session_state.global_db_backup
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    st.session_state.global_db_backup = data
                    return data
        except Exception: pass
    return {}

def save_db(d):
    try:
        st.session_state.global_db_backup = d
        with open("backup_orders.json", "w") as f: json.dump(d, f, indent=2)
    except Exception: pass

def words_to_num(s):
    if pd.isna(s): return s
    s_str = str(s).lower().strip()
    if s_str.isdigit(): return int(s_str)
    try: return float(s_str)
    except ValueError: pass
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
    "upload_text":"Drop CSV, Excel, JSON or Multiple Batch Files here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview",
    "tools_menu":"AI Studio","back_btn":"← Back","download_title":"Export Data",
    "paid_msg":"Step 1: Pay via UPI QR Code. Step 2: Click 'Customer I Paid' button.",
    "upi_text":"Scan QR to Pay ₹{amount}","paid_btn":"Customer I Paid ₹{amount}","wait_approval":"⏳ Waiting for Admin Approval... Click I Paid after payment",
    "download_success":"🎉 Download Ready!","tab1":"Date & Nulls","tab2":"Email & Phone","tab3":"Text Tools",
    "tool1":"Smart Date Converter","tool2":"AI Fill Nulls","tool3":"Email Validator","tool4":"Phone Formatter","tool5":"Case Converter",
    "tool6":"Remove Symbols","tool7":"Bulk Rename","tool8":"Remove Duplicates","tool9":"Trim Spaces","tool10":"Spell Check",
    "select_col":"Select Columns","select_case":"Choose Case Type","apply_btn":"Apply","success":"Apply is completed! Your data has been successfully updated.",
    "download_csv":"Download as CSV","download_excel":"Download as Excel"
}

# MOBILE RESPONSIVE & ANTI-CRASH STYLING
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}

.stApp {
    background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 25%, #d8b4fe 50%, #c084fc 75%, #a855f7 100%) !important; 
    background-size: 400% 400% !important; 
    animation: aurora 20s ease infinite !important;
}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}

.block-container {
    background: rgba(255,255,255,0.98) !important; 
    backdrop-filter: blur(20px) !important; 
    border-radius: 24px !important; 
    padding: 1.5rem !important; 
    max-width: 1200px; 
    margin: 1rem auto !important; 
    box-shadow: 0 30px 60px rgba(147,51,234,0.15) !important;
}

/* BRAND HEADER */
.hero-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 30px;
    background: #ffffff;
    padding: 24px;
    border-radius: 24px;
    box-shadow: 0 15px 35px rgba(147,51,234,0.06);
    border: 1.5px solid #f3e8ff;
}
.hero-left { display: flex; align-items: center; gap: 20px; flex: 1; }
.hero-logo img { width: 90px !important; height: auto; filter: drop-shadow(0px 8px 16px rgba(124,58,237,0.2)); }
.hero-text h1 { font-size: 3.2rem !important; font-weight: 900 !important; margin: 0 !important; color: #4c1d95 !important; }
.hero-text p { font-size: 1.1rem !important; margin: 4px 0 0 0 !important; color: #6b7280 !important; font-weight: 500; }
.hero-anime-right img { width: 140px; height: 140px; border-radius: 20px; object-fit: cover; box-shadow: 0 10px 25px rgba(147,51,234,0.12); }

/* PREMIUM BOX */
.tools-showcase-container {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    padding: 25px 20px; border-radius: 24px; color: white; text-align: center; margin-bottom: 25px;
}
.tools-showcase-container h3 { font-size: 1.5rem !important; font-weight: 850 !important; margin: 0 0 15px 0 !important; color: white !important; }
.badge-flex-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 15px; }
.tool-pill-badge { background: rgba(255, 255, 255, 0.2); padding: 6px 14px; border-radius: 50px; font-weight: 700; font-size: 0.85rem; color: white !important; }
.features-footer-text { font-size: 0.85rem; font-weight: 600; opacity: 0.95; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px; margin-top: 5px; color: #fff8ff; }

/* PRICING ROBUST CARD */
.pricing-card-wrapper {
    background: #ffffff; border: 2px solid #e9d5ff; border-radius: 24px; padding: 20px; text-align: center; margin-bottom: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.02);
}
.pricing-card-wrapper h2 { font-size: 1.3rem !important; color: #6d28d9 !important; font-weight: 800; margin: 0; }
.pricing-card-wrapper h1 { font-size: 2.5rem !important; color: #4c1d95 !important; font-weight: 900; margin: 5px 0; white-space: nowrap; }
.pricing-card-wrapper p { font-size: 0.95rem !important; color: #4b5563; margin: 0 0 12px 0; }
.feature-list { text-align: left; margin: 10px auto; max-width: 200px; font-size: 0.85rem; color: #4b5563; line-height: 1.6; }

.stButton>button {
    border-radius: 16px !important; font-weight: 800 !important; background: linear-gradient(90deg, #7c3aed, #a855f7) !important; 
    color: white !important; border: none !important; padding: 12px 24px !important; width: 100% !important; box-shadow: 0 8px 20px rgba(124,58,237,0.25) !important;
}

/* ADMIN PANEL DESIGN */
.admin-header { background: #4c1d95; color: white; padding: 15px; border-radius: 12px; font-weight: bold; margin-bottom: 20px; text-align:center;}
</style>
""", unsafe_allow_html=True)

# SIDEBAR ADMIN PANEL AUTHENTICATION SYSTEM
st.sidebar.markdown("### 👑 Sherni Admin Panel")
admin_pass = st.sidebar.text_input("Admin Security Password", type="password", key="admin_secret_key")

# Load State Keys
for key in ['plan','email','df_clean','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed','alert_triggered']:
    if key not in st.session_state: st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan','orig_len','empty_fixed'] else False

# -----------------------------------------------------------------
# 🚨 CASE 1: ADMIN PANEL ACTIVATED (Completely hides the frontend app)
# -----------------------------------------------------------------
if admin_pass == ADMIN_PASSWORD:
    st.markdown("<div class='admin-header'>🐆 WELCOME TO SHERNI ADMIN DATABASE MANAGEMENT PANEL 🐆</div>", unsafe_allow_html=True)
    
    db_state = load_db()
    
    if not db_state:
        st.info("Abhi tak database mein koi bhi users/orders nahi hain.")
    else:
        st.markdown("### 🕒 Active Customer Orders List & Status")
        
        # Iterating database seamlessly
        for user_email, info in list(db_state.items()):
            # Creating unique rows with action buttons
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([2, 1, 1.5, 1.5, 2])
                
                c1.markdown(f"**Email:** `{user_email}`")
                c2.markdown(f"**Plan:** `{info.get('plan','').upper()}`")
                c3.markdown(f"**Date:** {info.get('created','').split('.')[0]}")
                
                status = info.get("status", "PENDING")
                if status == "PAID":
                    c4.markdown("🟢 <span style='color:green;font-weight:bold;'>PAID / UNLOCKED</span>", unsafe_allow_html=True)
                    c5.write("Already Active")
                else:
                    c4.markdown("🔴 <span style='color:red;font-weight:bold;'>PENDING (I Paid)</span>", unsafe_allow_html=True)
                    # Simple Activation Button right in front of user details
                    if c5.button(f"Unlock Pro Now", key=f"unlock_{user_email}"):
                        db_state[user_email]["status"] = "PAID"
                        # Extra dynamic boost: Give it 30 or 180 days from current moment
                        days_to_add = info.get("days", 30)
                        db_state[user_email]["expiry"] = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
                        save_db(db_state)
                        st.success(f"Verified! {user_email} has been upgraded to PRO successfully!")
                        st.rerun()
                st.markdown("<hr style='margin:10px 0; opacity:0.2;'>", unsafe_allow_html=True)
    st.stop() # Prevents VeriSame App execution on Admin Mode

# -----------------------------------------------------------------
# 💻 CASE 2: REGULAR VERISAME APP FRONTEND INTERFACE
# -----------------------------------------------------------------
if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], use_container_width=True):
        for key in ['plan','email','df_clean','payment_clicked','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed','alert_triggered']:
            st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan','orig_len','empty_fixed'] else False
        st.rerun()

if st.session_state.email:
    db_state = load_db()
    user = db_state.get(st.session_state.email, {})
    st.sidebar.success(f"📧 {st.session_state.email}")
    
    # Check live approval inside client machine from dynamic DB
    if user.get("status") == "PAID":
        st.session_state.admin_approved = True

    if user.get("plan") == "free": 
        st.sidebar.markdown("<div style='background-color:#E8F5E9; padding:12px; border-radius:8px;'><b>Plan: FREE FOREVER</b></div>", unsafe_allow_html=True)
    else:
        if st.session_state.admin_approved:
            exp_date = datetime.strptime(user.get("expiry", (datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d")), "%Y-%m-%d")
            days_left = max(0, (exp_date - datetime.now()).days)
            st.sidebar.info(f"Plan: PRO VERSION\nValid Till: {user.get('expiry')}\n{days_left} days left")
        else:
            st.sidebar.warning("Plan: PRO (Waiting Admin Sync)")

# ⚡ LIVE BRAND NEW HEADER LAYOUT
st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-left">
        <div class="hero-logo">
            <img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" alt="Big VeriSame Logo">
        </div>
        <div class="hero-text">
            <h1>VeriSame</h1>
            <p>{T["subtitle"]}</p>
        </div>
    </div>
    <div class="hero-anime-right">
        <img src="https://i.postimg.cc/8zdnX54g/IMG-20260609-WA0012.jpg" alt="Anime Art Placement">
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        
        # 💎 10 TOOLS BANNER BOX
        st.markdown(f"""
        <div class="tools-showcase-container">
            <h3>💎 {T["pro_banner"]} 💎</h3>
            <div class="badge-flex-grid">
                <span class="tool-pill-badge">Smart Date</span>
                <span class="tool-pill-badge">AI Fill</span>
                <span class="tool-pill-badge">Email AI</span>
                <span class="tool-pill-badge">Phone AI</span>
                <span class="tool-pill-badge">Case</span>
                <span class="tool-pill-badge">Clean</span>
                <span class="tool-pill-badge">Rename</span>
                <span class="tool-pill-badge">Dedup</span>
                <span class="tool-pill-badge">Trim</span>
                <span class="tool-pill-badge">Spell</span>
            </div>
            <div class="features-footer-text">
                🎵 Peaceful 20s Welcome Track Active • 🧠 Interactive Audio Effects Enabled On UI Action Buttons
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f"""<div class='pricing-card-wrapper'><h2>{T['free_title']}</h2><h1>FREE</h1><p>Lifetime</p><div class='feature-list'>{''.join([f'<div>✓ {f}</div>' for f in T['free_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan = "free"; st.rerun()
        with col2:
            st.markdown(f"""<div class='pricing-card-wrapper' style='border-color: #7c3aed;'><h2>{T['pro1_title']}</h2><h1>₹299</h1><p>30 Days</p><div class='feature-list'>{''.join([f'<div>✓ {f}</div>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"; st.session_state.amt = PRO_1M; st.session_state.days = 30; st.rerun()
        with col3:
            st.markdown(f"""<div class='pricing-card-wrapper'><h2>{T['pro6_title']}</h2><h1>₹1499</h1><p>180 Days</p><div class='feature-list'>{''.join([f'<div>✓ {f}</div>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro+", key="btn_pro6", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"; st.session_state.amt = PRO_6M; st.session_state.days = 180; st.rerun()
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
                    expiry = (datetime.now() + timedelta(days=st.session_state.days)).strftime("%Y-%m-%d")
                    data[email_input] = {"plan":"pro","status":"PENDING","amt":st.session_state.amt,"days":st.session_state.days,"expiry":expiry,"created":str(datetime.now())}
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
                    sub_df = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f) if f.name.endswith(("xlsx","xls")) else pd.read_json(f)
                    df_list.append(sub_df)
                df = pd.concat(df_list, ignore_index=True) if df_list else None
            except Exception as e: st.error(f"Error: {str(e)}")
    with tab2:
        if st.button(T['sample_btn'], use_container_width=True):
            df = pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT SINGH"],"Email":["RAHUL@GMAIL.COM","bad@","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["one hundred","250","two thousand five hundred"]})

    if df is not None:
        orig_len = len(df)
        is_free = (st.session_state.plan == "free")
        
        if is_free and orig_len > 1000:
            st.error("⚠️ Limits Exceeded: Free Plan allows up to 1000 rows only.")
            st.stop()

        if 'df_loaded' not in st.session_state or not st.session_state.df_loaded:
            st.session_state.df_clean = df.copy()
            df_clean = st.session_state.df_clean.drop_duplicates()
            for col in df_clean.columns:
                if df_clean[col].dtype == object:
                    df_clean[col] = df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                if any(k in col.lower() for k in ['salary','amount','price']): df_clean[col] = df_clean[col].apply(words_to_num)
            st.session_state.df_clean = df_clean
            st.session_state.df_loaded = True
            st.session_state.orig_len = orig_len
            st.session_state.empty_fixed = int(df.isna().sum().sum())
        
        df_clean = st.session_state.df_clean
        orig_len = st.session_state.orig_len

        st.markdown(f"<h2>{T['summary_title']}</h2>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric(T['rows'], orig_len)
        with c2: st.metric(T['clean'], len(df_clean))
        with c3: st.metric(T['dups'], orig_len-len(df_clean))
        with c4: st.metric(T['empty'], st.session_state.empty_fixed)

        # 📊 DYNAMIC VISUALIZATION CHART METRIC
        chart_data = pd.DataFrame({
            'Data Categories': ['Original Loaded Rows', 'Clean Valid Rows', 'Purged Duplicates'],
            'Count Records': [orig_len, len(df_clean), (orig_len - len(df_clean))]
        })
        st.bar_chart(data=chart_data, x='Data Categories', y='Count Records', color='#7c3aed')

        st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
        st.dataframe(df_clean.head(10), use_container_width=True, height=220)

        all_cols = df_clean.columns.tolist()
        tab1_ui, tab2_ui, tab3_ui = st.tabs([T['tab1'], T['tab2'], T['tab3']])
        
        with tab1_ui:
            st.write(f"**{T['tool1']}** ✅ Free")
            date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date")
            if st.button(T['apply_btn'], key="btn_date"):
                for col in date_cols:
                    try:
                        converted = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', format='mixed', dayfirst=True)
                        st.session_state.df_clean[col] = converted.dt.strftime('%Y-%m-%d').fillna("None")
                    except Exception: pass
                st.success(T['success'])

            st.write(f"**{T['tool2']}** {'🔒 Pro' if is_free else '✅ Unlocked'}")
            fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_fill", disabled=is_free):
                for col in fill_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].fillna("Unknown")
                st.success(T['success'])

        with tab2_ui:
            st.write(f"**{T['tool3']}** {'🔒 Pro' if is_free else '✅ Unlocked'}")
            email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_email", disabled=is_free):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in email_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: x if re.match(pattern, x.strip()) else "Invalid Email")
                st.success(T['success'])

            st.write(f"**{T['tool4']}** {'🔒 Pro' if is_free else '✅ Unlocked'}")
            phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_phone", disabled=is_free):
                for col in phone_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x))[-10:])
                st.success(T['success'])

        with tab3_ui:
            st.write(f"**{T['tool5']}** ✅ Free")
            case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"])
            if st.button(T['apply_btn'], key="btn_case"):
                for col in case_cols:
                    if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.upper()
                    elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower()
                    else: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.title()
                st.success(T['success'])

            st.write(f"**{T['tool8']}** ✅ Free")
            if st.button("Purge Duplicates Now", key="btn_dedup"):
                st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                st.success(T['success'])

        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
        if is_free:
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            st.download_button(T['download_csv'], csv, "verisame_free.csv", mime="text/csv")
        else:
            if not st.session_state.admin_approved:
                st.warning(T['wait_approval'])
                if qrcode is not None:
                    pay_url = f"upi://pay?pa={UPI}&pn=VeriSamePro&am={st.session_state.amt}&cu=INR"
                    qr = qrcode.QRCode(version=1, box_size=6, border=2)
                    qr.add_data(pay_url)
                    qr.make(fit=True)
                    buf = io.BytesIO()
                    qr.make_image().save(buf, format="PNG")
                    st.image(buf.getvalue(), width=180)
                
                # 💬 LIVE REAL-TIME WHATSAPP INSTANT LINK TRIGGER
                wa_msg = f"Hello Admin, I have paid ₹{st.session_state.amt} for VeriSame Pro Plan. Please approve my email ID: {st.session_state.email}"
                wa_url = f"https://wa.me/919876543210?text={wa_msg.replace(' ', '%20')}" 
                
                st.markdown(f' <a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366 !important; color:white; border-radius:12px; padding:12px; border:none; font-weight:bold; width:100%; cursor:pointer;">💬 Send Payment Alert on WhatsApp</button></a>', unsafe_allow_html=True)
                
                if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary"):
                    st.success("Payment log updated! Waiting for admin manual verification sync.")
            else:
                csv = st.session_state.df_clean.to_csv(index=False).encode()
                st.download_button(T['download_csv'], csv, "verisame_pro.csv", mime="text/csv")
