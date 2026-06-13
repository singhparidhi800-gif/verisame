import streamlit as st
import json, os, io, qrcode
import pandas as pd
import re
from datetime import datetime, timedelta
import difflib  # 🧠 खुद से बेस्ट आंसर ढूंढने के लिए इंजन

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

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
    "admin_title":"Sherni Admin Panel","admin_pending":"User Databases & Requests","admin_approve_btn":"Mark Paid - Unlock Customer Download",
    "admin_user":"Customer Email","admin_plan":"Plan","admin_expiry":"Valid Till","delete_btn":"Delete User","download_csv":"Download as CSV","download_excel":"Download as Excel"
}

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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame's Smart AI Studio. 💎 Ask me anything about our workflows, specific tools, safety, calculations, or data science utilities!"}]

for key in ['plan','email','df_clean','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan'] else False

# 🔥 PERFECTED AI KNOWLEDGE BASE ENGINE (WITH HIGH-INTELLIGENCE FILTERING)
def render_ai_chatbot(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 VeriSame Live AI Chat Studio")
    
    chat_html = "<div style='max-height: 260px; overflow-y: auto; padding: 10px; background: rgba(255,255,255,0.9); border: 2px solid #9333ea; border-radius: 14px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history:
        if chat["role"] == "assistant":
            chat_html += f"<p style='color: #6b21a8 !important; margin: 5px 0;'><b>🤖 AI:</b> {chat['message']}</p>"
        else:
            chat_html += f"<p style='color: #000 !important; margin: 5px 0;'><b>👤 You:</b> {chat['message']}</p>"
    chat_html += "</div>"
    target.markdown(chat_html, unsafe_allow_html=True)
    
    with target.form(key=f"ai_chat_form_{'side' if is_sidebar else 'main'}", clear_on_submit=True):
        user_msg = st.text_input("Ask a question...", placeholder="e.g., Are all tools good? / App limits?", key=f"chat_in_{'side' if is_sidebar else 'main'}")
        submit = st.form_submit_button(label="Send Message 🚀")
        
        if submit and user_msg.strip():
            u = user_msg.lower().strip()
            st.session_state.chat_history.append({"role": "user", "message": user_msg})
            
            reply = None
            
            # 🧠 1. AUTONOMOUS DECISION-MAKING & INTENT COGNITION
            if any(w in u for w in ["all tools", "every tool", "tool good", "are tools safe", "best tool", "useful app", "worth it"]):
                reply = "💎 **Yes, absolutely! All 10 tools inside VeriSame are highly optimized and completely safe.** Every tool uses strict Python pandas vectorization to clean columns instantly without breaking other data rows. You can trust them 100% for corporate reporting inputs!"
                
            elif any(w in u for w in ["which plan", "should i buy", "free or pro", "best plan for me"]):
                reply = "🤔 **Decision Matrix Recommendation:**\n• If your file has **less than 1,000 rows** and you only need Date formatting, Case adjustment, or Duplicate removal, the **Free Lifetime Tier** is ideal.\n• If you deal with heavy datasets, phone validations, or blank rows, **upgrading to Pro (₹299/Month)** is the smartest decision to save time!"

            # 🔢 2. ADVANCED MATH CALCULATOR ENGINE (Handles 2*8, 2x8, 50+50 etc.)
            if not reply:
                math_clean = u.replace('x', '*')
                match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', math_clean)
                if match:
                    n1, op, n2 = int(match.group(1)), match.group(2), int(match.group(3))
                    if op == '+': res = n1 + n2
                    elif op == '-': res = n1 - n2
                    elif op == '*': res = n1 * n2
                    elif op == '/': res = n1 / n2 if n2 != 0 else "Error"
                    reply = f"🔢 **Math Calculator Engine:** \nExpression: `{n1} {op} {n2}` \n**Result:** `{res}`"

            # 📚 3. STRICT KNOWLEDGE BASE WITH INTELLIGENT THRESHOLD
            if not reply:
                knowledge_map = {
                    "hi hello hey hello ai hi ai ola salam": "👋 **Hello there!** Welcome to VeriSame! How can I speed up your dataset processing workflows today?",
                    "how are you kaise ho kaise hain how it goes sab badhiya": "✨ **I am doing fantastic!** Powered up, synchronized, and completely ready to smash data errors under 3 seconds.",
                    "your name naam kya who are you tum kaun ho identify": "💎 I am **VeriSame Engine AI**, a hyper-customized data assistant built to answer software queries and guide premium pipelines!",
                    "thank you thanks shukriya dhanyawad great app awesome nice app good job": "💖 **You are most welcome!** Making your data pipeline seamless is exactly what I live for.",
                    "joke chutkula make me laugh funny": "😂 **Data Science Special Joke:** Why did the Data Scientist break up with the Excel Sheet? *Because it had too many attachment issues!*",
                    "bye goodnight good night tata see you alvida exit": "👋 **Goodbye!** Remember to download your processed files before closing your volatile session state.",
                    "founder made creator created developer owner built make kaun banaya owner kaun anugya": "👑 **Founder & Creator:** VeriSame was architected and developed by **Anugya Singh** to eliminate manual data cleaning frustration.",
                    "size limit mb gb file size heavy file large file badi file capacity": "💾 **File Size Capacity:** VeriSame easily supports spreadsheet engines up to **50 Megabytes (MB)** seamlessly without any computational lag!",
                    "multiple together two tools both together ek sath ek saath saath me combination": "🔄 **Applying Multiple Tools:** Yes, you can pile adjustments! Choose your first column, click **Apply**, then select another tool/column and click Apply again before downloading.",
                    "hindi language bhasha multilingual other language script support": "🌍 **Language Stack Support:** Text operations like **Tool 8 (Remove Duplicates)** and **Tool 9 (Trim Spaces)** work completely perfectly on **Hindi text entries**!",
                    "disappear delete column safe column sequence order change data lost data loss": "🛡️ **Data Integrity Guarantee:** Applying transformations will **never** alter row sequence or drop unselected columns. Your data alignment stays 100% stable.",
                    "how long approval time how much time admin active kitni der kab hoga time lag": "⏳ **Admin Verification Time:** Standard transaction approvals are cross-referenced manually and fully activated within **10 to 30 minutes** maximum!",
                    "failed deducted money cut paisa kat stuck payment payment issue error payment": "💳 **Payment & Discrepancies:** Don't worry! Simply retain your **UPI Transaction Reference Number** and connect with email support to bypass manual wait queues.",
                    "real ai regex how smart technology backend python logic backend code": "🧠 **System Engine Architecture:** VeriSame operates on a highly optimized hybrid architecture combining vector computations via Python pandas and deep regular expressions.",
                    "safe safety secure privacy leak store data safe security surakshit chori": "🔒 **Data Privacy & Security:** Your files are **100% safe**. Rows are processed strictly in temporary volatile memory and are **never stored** on any database.",
                    "refund return money back paisa wapas cancel": "💸 **Refund Policy:** VeriSame does **not** support refund packages since it provides instant digital updates. Please test via our Free Tier first.",
                    "crash error not working stuck slow bug kharab chal nahi raha": "🛠️ **Troubleshooting Guide:** 1. Ensure file is `.csv`, `.xlsx`, or `.json`. 2. Confirm headers do not contain duplicate label names. 3. Try refreshing.",
                    "csv vs excel difference between csv what is csv excel difference": "📊 **CSV vs Excel:** • **CSV:** Lightweight plain text format preferred for Machine Learning model feeds. • **Excel:** Heavy spreadsheet layout best for manual business reporting.",
                    "free vs pro compare why pro pro benefits difference plan": "💎 **Plan Breakdown:** • **Free:** Caps at 1,000 rows & 3 basic tools. • **Pro:** Unlocks **Unlimited Dataset Rows**, 3s processing speed, and all **10 premium automation tools**.",
                    "contact support help email support complaint customer care baat karni": "📧 **Support Channels:** Drop a query directly to our developer team via standard email support. Responses process within 12-24 hours.",
                    "salary job scope career future earn money data science": "🚀 **Data Science Scope:** Data Science roles offer premium packages ranging from ₹12 Lakhs to ₹25+ Lakhs annually in India. Preprocessing automation is an essential step!",
                    "tool 1 date converter date ai calendar tool": "📅 **Tool 1: Smart Date Converter (FREE & PRO)** Unifies chaotic date layouts cleanly into the standardized 'YYYY-MM-DD' layout automatically.",
                    "tool 2 fill nulls null ai empty ai blank ai missing ai": "🔓 **Tool 2: AI Fill Nulls (PRO ONLY)** Automatically fills structural blank spaces using logical tokens like 'N/A' or `0` integers.",
                    "tool 3 email validator email ai mail ai": "📧 **Tool 3: Email Validator & Cleaner (PRO ONLY)** Verifies structure blocks, extracts bad domains, and retains purely functional emails.",
                    "tool 4 phone formatter phone ai contact ai mobile ai number ai": "📞 **Tool 4: Phone Formatter (PRO ONLY)** Strips alphabetic noise and hyphens, leaving beautifully structured pure numerical digits.",
                    "tool 5 case converter case ai text case caps ai": "🔠 **Tool 5: Case Converter (FREE & PRO)** Safely alters column text layouts into absolute Uppercase, Lowercase, or Title Case formats.",
                    "tool 6 remove symbols symbol ai noise ai character ai": "🔣 **Tool 6: Remove Symbols & Noise (PRO ONLY)** Slices off unreadable special character junk (like #, $, %, *) while protecting alpha-numeric parameters.",
                    "tool 7 bulk rename rename ai header ai column ai": "✏️ **Tool 7: Bulk Header Renamer (PRO ONLY)** Allows users to pick dataset titles instantly from a selector menu and type clean matching strings.",
                    "tool 8 remove duplicates duplicate ai dedup ai repeat ai copy ai": "🔥 **Tool 8: Remove Duplicates (FREE & PRO)** Drops repetitive row data chunks to optimize dataset footprint and keep exactly 1 primary record.",
                    "tool 9 trim spaces trim ai space ai gap ai": "✂️ **Tool 9: Trim Spaces & Gaps (FREE & PRO)** Eliminates hazardous trailing or leading whitespaces embedded inside database fields.",
                    "tool 10 spell check spell ai typo ai correct ai": "🧠 **Tool 10: Spell Check & Auto-Correct (PRO ONLY)** Maps logic to wipe out manual typos (e.g., fixing 'teh' to 'the'), ensuring high-end reporting quality.",
                    "how many tools number of tools total tools kitne tool": "🛠️ **Total Tools:** VeriSame features exactly **10 Data-Cleaning Tools** plus a special financial **Word-to-Number conversion algorithm**!"
                }

                best_ratio = 0.0
                best_key = None
                
                for keys in knowledge_map.keys():
                    words_in_key = keys.split()
                    user_words = u.split()
                    has_exact_keyword = any(uw in words_in_key for uw in user_words if len(uw) > 3)
                    
                    ratio = difflib.SequenceMatcher(None, u, keys).ratio()
                    word_matches = sum(1 for word in u.split() if word in keys)
                    bonus_ratio = (word_matches / max(1, len(u.split()))) * 0.4
                    final_score = ratio + bonus_ratio
                    
                    if has_exact_keyword:
                        final_score += 0.35
                    
                    if final_score > best_ratio:
                        best_ratio = final_score
                        best_key = keys
                
                if best_ratio >= 0.55 and best_key:
                    reply = knowledge_map[best_key]
                else:
                    reply = "🔍 **I couldn't find an exact match for that query.**\n\nAs VeriSame's Smart Assistant, you can ask me:\n• *Are all tools good? / Which plan should I buy?*\n• Simple math questions like *'50 * 5'*\n• Details about specific utilities like *'What is Tool 9 Trim?'*"
            
            st.session_state.chat_history.append({"role": "assistant", "message": reply})
            st.rerun()

if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button(T['back_btn'], use_container_width=True):
        for key in ['plan','email','df_clean','payment_clicked','sample_loaded','email_entered','days','selected_plan','admin_approved']:
            st.session_state[key] = None if key in ['plan','email','df_clean','days','selected_plan'] else False
        st.rerun()

# 🛡️ DATABASE & EMAIL COGNITION LOGIC
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
        st.session_state.admin_approved = user.get("status") == "PAID"

        if user.get("plan") == "free":
            st.sidebar.info("Plan: FREE LIFETIME ✨")
        elif days_left <= 5 and days_left > 0:
            # 🔥 🔴 RED COLOR WARNING FOR ENDING PLANS (5 Days Priority Tracker)
            st.sidebar.markdown(f"""
            <div style="background-color: #fee2e2; border: 2px solid #ef4444; padding: 12px; border-radius: 12px; color: #b91c1c !important;">
                ⚠️ <b>CRITICAL WARNING:</b> Your ₹{st.session_state.amt} plan is going to end in <b>{days_left} days</b>! Please renew now to avoid data loss.
            </div>
            """, unsafe_allow_html=True)
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

# 👑 SHERNI ADMIN CONTROL CENTER (EMAILS RETENTION FIX)
if st.query_params.get("admin"):
    admin_pass = st.query_params.get("admin")
    if admin_pass == ADMIN_PASS:
        st.title(T['admin_title'])
        data = load_db()
        
        # सभी यूजर्स का डेटा दिखाएं (चाहे Pending हो या Paid) ताकि लिस्ट से गायब न हो!
        st.subheader(T['admin_pending'])
        if data:
            for email, info in data.items():
                if "@" not in email: continue
                amt = info.get('amt', 0)
                status = info.get('status', 'PENDING')
                plan_text = f"PRO Monthly ₹299" if amt == 299 else f"PRO 6M ₹1499" if amt == 1499 else "FREE Plan"
                
                col1, col2, col3 = st.columns([4, 2, 2])
                with col1:
                    status_color = "🟢 PAID UNLOCKED" if status == "PAID" else "⏳ PENDING APPROVAL"
                    st.markdown(f"""
                    <div class='pricing-card'>
                        <b>{T['admin_user']}:</b> {email}<br>
                        <b>{T['admin_plan']}:</b> {plan_text}<br>
                        <b>Status:</b> {status_color}<br>
                        <b>{T['admin_expiry']}:</b> {info.get('expiry','N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    # अगर यूजर पहले से Paid नहीं है तभी अप्रूव करने का बटन दिखेगा
                    if status == "PENDING":
                        if st.button(T['admin_approve_btn'], key=f"verify_{email}", type="primary", use_container_width=True):
                            data[email]["status"] = "PAID"
                            save_db(data)
                            st.success(f"✓ {email} unlocked!")
                            st.balloons()
                            st.rerun()
                    else:
                        st.button("✓ Already Active", key=f"active_{email}", disabled=True, use_container_width=True)
                with col3:
                    if st.button(T['delete_btn'], key=f"delete_{email}", use_container_width=True):
                        del data[email]
                        save_db(data)
                        st.error(f"✓ {email} deleted")
                        st.rerun()
        else:
            st.info("No records found in database.")
        st.stop()

# 🛡️ LOGIN / SIGN-UP SESSION CHECKER
if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        col1,col2,col3 = st.columns(3, gap="medium")
        with col1:
            st.markdown(f"""<div class='pricing-card'><h2>{T['free_title']}</h2><h1>FREE</h1><p>Lifetime</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['free_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan = "free"
                st.rerun()
        with col2:
            st.markdown(f"""<div class='pricing-card' style='border: 3px solid #9333ea; box-shadow:0 15px 35px rgba(147,51,234,0.3)'><p>⭐ POPULAR</p><h2>{T['pro1_title']}</h2><h1>₹299</h1><p>30 Days - All Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"
                st.session_state.amt = PRO_1M
                st.session_state.days = 30
                st.rerun()
        with col3:
            st.markdown(f"""<div class='pricing-card'><h2>{T['pro6_title']}</h2><h1>₹1499</h1><p>180 Days - All Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro+", key="btn_pro6", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"
                st.session_state.amt = PRO_6M
                st.session_state.days = 180
                st.rerun()
        
        render_ai_chatbot(is_sidebar=False)
        
    else:
        st.markdown(f"<h2>Enter your email to continue with {st.session_state.selected_plan.upper()}</h2>", unsafe_allow_html=True)
        email_input = st.text_input(T['email_label'], placeholder="your@email.com").lower().strip()
        if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
            if "@" in email_input and "." in email_input:
                st.session_state.email = email_input
                st.session_state.email_entered = True
                
                # 🧠 पुराने रिकॉर्ड्स की मेमोरी चेक करने का मैकेनिज्म
                data = load_db()
                if email_input in data:
                    st.session_state.plan = data[email_input]["plan"]
                    st.session_state.amt = data[email_input].get("amt", 299)
                    st.rerun()
                else:
                    st.session_state.plan = st.session_state.selected_plan
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
            try: df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file) if file.name.endswith(("xlsx","xls")) else pd.read_json(file)
            except Exception as e: st.error(f"Error reading file: {str(e)}")
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

            st.write(f"**{T['tool2']}** {'🔓 Unlocked ✅' if is_pro and st.session_state.admin_approved else 'Pro Only'}")
            fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_fill", use_container_width=True, disabled=is_free):
                st.session_state.df_clean[fill_cols] = st.session_state.df_clean[fill_cols].fillna("N/A")
                st.success(T['success'])
                st.rerun()

        with tab2:
            st.write(f"**{T['tool3']}** {'🔓 Unlocked ✅' if is_pro and st.session_state.admin_approved else '🔒 Pro Only'}")
            email_cols = st.multiselect(T['select_col'], all_cols, key="ms_email", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_email", use_container_width=True, disabled=is_free):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in email_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).lower() if re.match(pattern, str(x)) else "")
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool4']}** {'🔓 Unlocked ✅' if is_pro and st.session_state.admin_approved else '🔒 Pro Only'}")
            phone_cols = st.multiselect(T['select_col'], all_cols, key="ms_phone", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_phone", use_container_width=True, disabled=is_free):
                for col in phone_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'\D', '', regex=True)
                st.success(T['success'])
                st.rerun()

        with tab3:
            st.write(f"**{T['tool5']}** ✅ Free + Pro")
            case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
            if st.button(T['apply_btn'], key="btn_case", use_container_width=True):
                for col in case_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].str.upper() if case_opt == "Uppercase" else st.session_state.df_clean[col].str.lower() if case_opt == "Lowercase" else st.session_state.df_clean[col].str.title()
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool6']}** {'🔓 Unlocked ✅' if is_pro and st.session_state.admin_approved else '🔒 Pro Only'}")
            spec_cols = st.multiselect(T['select_col'], all_cols, key="ms_spec", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_spec", use_container_width=True, disabled=is_free):
                for col in spec_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].str.replace(r'[^a-zA-Z0-9\s@.]', '', regex=True)
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool7']}** {'🔓 Unlocked ✅' if is_pro and st.session_state.admin_approved else '🔒 Pro Only'}")
 Old = st.selectbox("Old column name", all_cols, key="sel_old", disabled=is_free)
            new = st.text_input("New column name", key="inp_new", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_rename", use_container_width=True, disabled=is_free) and new:
                st.session_state.df_clean.rename(columns={old: new}, inplace=True)
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool8']}** ✅ Free + Pro")
            if st.button(T['apply_btn'], key="btn_dedup", use_container_width=True):
                st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool9']}** ✅ Free + Pro")
            trim_cols = st.multiselect(T['select_col'], all_cols, key="ms_trim")
            if st.button(T['apply_btn'], key="btn_trim", use_container_width=True):
                for col in trim_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip()
                st.success(T['success'])
                st.rerun()

            st.write(f"**{T['tool10']}** {'🔓 Unlocked ✅' if is_pro and st.session_state.admin_approved else '🔒 Pro Only'}")
            spell_cols = st.multiselect(T['select_col'], all_cols, key="ms_spell", disabled=is_free)
            if st.button(T['apply_btn'], key="btn_spell", use_container_width=True, disabled=is_free):
                for col in spell_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: str(x).replace("teh", "the").replace("recieve", "receive").title())
                st.success(T['success'])
                st.rerun()

        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
        if st.session_state.show_balloon:
            st.balloons()
            st.session_state.show_balloon = False

        if st.session_state.plan == "free":
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button(T['download_csv'], csv, "verisame_clean.csv", mime="text/csv", key="dl_csv_free", use_container_width=True):
                st.session_state.show_balloon = True
                st.rerun()
            excel = io.BytesIO()
            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
            if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_clean.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_free", use_container_width=True):
                st.session_state.show_balloon = True
                st.rerun()
        elif st.session_state.plan == "pro":
            # 🔓 अगर एडमिन से अप्रूव हो गया है, तो QR कोड मत दिखाओ, सीधे डाउनलोड ऑप्शन दो!
            if not st.session_state.admin_approved:
                st.warning(T['wait_approval'])
                st.markdown(f"### {T['upi_text'].format(amount=st.session_state.amt)}")
                upi_link = f"upi://pay?pa={UPI}&pn=VeriSame&am={st.session_state.amt}&cu=INR"
                qr = qrcode.make(upi_link)
                buf = io.BytesIO()
                qr.save(buf, format="PNG")
                st.image(buf.getvalue(), width=220)
                if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary", use_container_width=True):
                    st.session_state.payment_clicked = True
                    st.rerun()
            else:
                col1, col2 = st.columns(2)
                csv = st.session_state.df_clean.to_csv(index=False).encode()
                if col1.download_button(T['download_csv'], csv, "verisame_pro.csv", mime="text/csv", key="dl_csv_paid", use_container_width=True):
                    st.session_state.show_balloon = True
                    st.rerun()
                excel = io.BytesIO()
                st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_pro.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_paid", use_container_width=True):
                    st.session_state.show_balloon = True
                    st.rerun()
