import streamlit as st
import json, os, io, time
import pandas as pd
import re
from datetime import datetime, timedelta
import difflib 
import urllib.parse

# Safe imports for Groq API Integration
try:
    from groq import Groq
except Exception:
    Groq = None

# Safe imports to completely avoid Streamlit Deployment Crashes
try:
    import qrcode
except Exception:
    qrcode = None

try:
    import openpyxl
except Exception:
    openpyxl = None

# PDF Report Generation Dependency
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except Exception:
    SimpleDocTemplate = None

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

UPI_ID = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
FREE_ROW_LIMIT = 200

# Secure admin password retrieval from Streamlit secrets
ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "admin123")

# 🔒 PERSISTENT DATABASE LOGIC
def load_db():
    data = {}
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
        except Exception:
            pass
    elif "saved_orders" in st.secrets:
        try:
            data = json.loads(st.secrets["saved_orders"])
        except Exception:
            pass

    # Clean up legacy invalid 36500-day entries for Pro users
    if isinstance(data, dict):
        modified = False
        for email, info in data.items():
            if isinstance(info, dict) and info.get("plan") == "pro":
                if info.get("days", 0) > 180 or "2126" in str(info.get("expiry", "")):
                    amt = info.get("amt", 299)
                    exact_days = 180 if amt == 1499 else 30
                    info["days"] = exact_days
                    info["expiry"] = (datetime.now() + timedelta(days=exact_days)).strftime("%Y-%m-%d")
                    modified = True
        if modified:
            save_db(data)
        return data
    return {}

def save_db(d):
    try:
        with open("backup_orders.json", "w") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass

# ⏳ PROCESSING TIME SIMULATOR (Free = 30s, Pro = 3s)
def simulate_processing():
    if st.session_state.plan == "free":
        with st.spinner("⏳ Free Plan Active: Processing dataset (30s slowdown mode)..."):
            time.sleep(30)
    else:
        with st.spinner("⚡ Pro Plan Active: Fast AI processing (3s)..."):
            time.sleep(3)

# 💰 ADVANCED WORD-TO-NUMBER CONVERSION ENGINE
def words_to_num(s):
    if pd.isna(s): return s
    if isinstance(s, (int, float)): return s
    s_str = str(s).lower().strip().replace(',', '')
    if s_str.isdigit(): return int(s_str)
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
        elif word.isdigit():
            has_num_word = True
            current += int(word)
            
    return total + current if has_num_word and (total + current > 0) else s

# 🧠 FUZZY DEDUPLICATION ALGORITHM
def remove_fuzzy_duplicates(dataframe, column_name, threshold=0.85):
    if dataframe[column_name].dtype != 'object':
        return dataframe
    unique_values = dataframe[column_name].dropna().unique()
    if len(unique_values) > 1000:
        unique_values = unique_values[:1000]
    mapping = {}
    for i, val1 in enumerate(unique_values):
        if val1 in mapping: continue
        for val2 in unique_values[i+1:]:
            s1, s2 = str(val1).strip().lower(), str(val2).strip().lower()
            if difflib.SequenceMatcher(None, s1, s2).ratio() >= threshold:
                mapping[val2] = val1
    dataframe[column_name] = dataframe[column_name].replace(mapping)
    return dataframe.drop_duplicates()

# 📅 SYSTEM DATE CONVERTER
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

# FUNCTION TO GENERATE CLEAN PDF AUDIT REPORT
def generate_pdf_report(orig_len, clean_len, empty_fixed, df):
    if SimpleDocTemplate is None: return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#6b21a8'), spaceAfter=15)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=11, textColor=colors.HexColor('#4b5563'), spaceAfter=25)
    
    story.append(Paragraph("VeriSame - AI Data Audit Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Account: {st.session_state.get('email', 'Guest')}", sub_style))
    story.append(Spacer(1, 10))
    
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#1f2937'), spaceAfter=8)
    metric_data = [
        [Paragraph("<b>Metric Parameter</b>", text_style), Paragraph("<b>Value Counts</b>", text_style)],
        [Paragraph("Total Ingested Rows", text_style), Paragraph(str(orig_len), text_style)],
        [Paragraph("Clean Post-Processed Rows", text_style), Paragraph(str(clean_len), text_style)],
        [Paragraph("Duplicate Rows Extracted", text_style), Paragraph(str(orig_len - clean_len), text_style)],
        [Paragraph("Empty/Null Cells Fixed", text_style), Paragraph(str(empty_fixed), text_style)]
    ]
    t1 = Table(metric_data, colWidths=[250, 200])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#9333ea')),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#c084fc'))
    ]))
    story.append(t1)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# GROQ API HELPER FUNCTION
def query_groq_ai(prompt_text, system_instruction="You are VeriSame AI assistant."):
    groq_key = st.secrets.get("GROQ_API_KEY", None)
    if not groq_key or Groq is None: return None
    try:
        client = Groq(api_key=groq_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.5,
            max_tokens=400
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.session_state["groq_last_error"] = str(e)
        return None

T = {
    "title":"VeriSame","subtitle":"The Fastest Way to Clean Your Data","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"1 MONTH","pro6_title":"6 MONTHS",
    "free_feat":["200 Rows Limit","CSV Export","4 Free Tools Built-in","30s Processing Delay","Email Support"],
    "pro_feat":["Unlimited Rows","CSV + Excel Export","10 Premium AI Tools","3s Instant Speed","Priority Support","No Watermark","PDF Audit Reports"],
    "email_label":"Enter your email address","continue_btn":"Verify & Continue","upload_tab":"📤 Upload File","sample_tab":"🎯 Try Demo",
    "upload_text":"Drop CSV, Excel or JSON file here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview (Green Highlights show modified data cells 🟢)",
    "tools_menu":"AI Studio","back_btn":"← Back","download_title":"Export Data Workspace",
    "paid_msg":"Pay via UPI and submit approval request below.",
    "upi_text":"Scan QR or Click Link to Pay ₹{amount}","paid_btn":"Customer I Paid ₹{amount}","wait_approval":"⏳ Waiting for Admin Approval...",
    "download_success":"🎉 Download Ready!","tab1":"Date & Nulls","tab2":"Email & Phone","tab3":"Text Tools",
    "tool1":"Smart Date Converter","tool2":"AI Fill Nulls","tool3":"Email Validator","tool4":"Phone Formatter","tool5":"Case Converter",
    "tool6":"Remove Symbols","tool7":"Bulk Rename","tool8":"Remove Duplicates / Fuzzy Match","tool9":"Trim Spaces","tool10":"Spell Check",
    "select_col":"Select Columns","select_case":"Choose Case Type","apply_btn":"Apply Actions","success":"Apply is completed! Your data has been successfully updated.",
    "admin_title":"👑 Admin Dashboard Panel 👑","admin_pending":"User Databases & Purchase Requests","admin_approve_btn":"Mark Paid - Unlock Customer Download",
    "admin_user":"Customer Email","admin_plan":"Plan","admin_expiry":"Valid Till","delete_btn":"Delete User","download_csv":"Download as CSV","download_excel":"Download as Excel"
}

# CSS STYLING
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 25%, #c084fc 50%, #a855f7 75%, #9333ea 100%); background-size: 400% 400%; animation: aurora 15s ease infinite; padding-top: 0.3rem;}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}
.block-container {background: rgba(255,255,255,0.96); backdrop-filter: blur(25px) saturate(180%); border-radius: 28px; padding: 2rem; max-width: 1200px; margin: 0 auto; box-shadow: 0 30px 60px rgba(139,92,246,0.25); border: 1.5px solid rgba(255,255,255,0.5);}
h1,h2,h3,p,span,label,div,li {color: #000!important; font-weight: 600!important;}
h1 {font-weight: 800!important; font-size: 3.2rem!important; margin-bottom: 0.2rem!important; background: linear-gradient(90deg, #6b21a8, #9333ea, #c084fc, #a855f7, #6b21a8); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.subtitle {text-align: left; color: #4b5563!important; font-size: 1.1rem!important; font-weight: 500!important; margin-top: 6px!important; margin-bottom: 1rem!important;}
.tagline-badge {display: inline-block; padding: 6px 16px; background: linear-gradient(135deg, #9333ea, #6b21a8); color: #ffffff !important; font-weight: 700 !important; font-size: 0.95rem; border-radius: 20px; letter-spacing: 0.4px; box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3); vertical-align: middle; margin-left: 12px;}
.logo-float {animation: float 3s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.pricing-card {position: relative; border-radius: 22px; padding: 1.6rem; background: rgba(255,255,255,0.92)!important; transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(147,51,234,0.15); border: 2.5px solid #9333ea;}
.stButton>button {border-radius: 14px !important; font-weight: 700 !important; background: linear-gradient(90deg, #9333ea, #a855f7) !important; color: white !important; border: none !important; padding: 13px 26px !important; width: 100% !important; box-shadow: 0 5px 18px rgba(147,51,234,0.4) !important;}
.pro-banner {background: linear-gradient(135deg, #7e22ce, #a855f7, #d946ef); padding: 1.6rem; border-radius: 22px; color: white!important; text-align: center; margin: 1rem 0;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.95); padding: 9px 17px; border-radius: 28px; margin: 4px; border: 2px solid #9333ea; color: #000!important;}
.red-alert-banner {background-color: #fee2e2; border: 2px solid #ef4444; border-radius: 14px; padding: 14px; margin-bottom: 15px; color: #991b1b !important; font-weight: 700 !important;}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame AI Studio. 💎 How can I help you clean or optimize your dataset today?"}]

if "changed_cells" not in st.session_state:
    st.session_state.changed_cells = set()

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# SETUP CORE SESSION STATE CAPABILITIES
for key in ['plan','email','df_clean','df_original','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed','last_upload_sig','reset_announced','last_apply_msg']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['plan','email','df_clean','df_original','days','selected_plan','orig_len','empty_fixed','last_upload_sig','last_apply_msg'] else False

# RELIABLE MODIFICATION TRACKING ACROSS ALL TOOLS
def track_modifications(old_df, new_df):
    try:
        for col in old_df.columns:
            if col in new_df.columns:
                s_old = old_df[col].astype(str).fillna("")
                s_new = new_df[col].astype(str).fillna("")
                diff_mask = s_old != s_new
                for idx in old_df[diff_mask].index:
                    st.session_state.changed_cells.add((idx, col))
    except Exception:
        pass

# 🟢 PERSISTENT GREEN HIGHLIGHT LOGIC FOR ALL MODIFIED DATA CELLS
def apply_cell_styling(df_to_style):
    def highlight_cells(x):
        df_colors = pd.DataFrame('', index=x.index, columns=x.columns)
        for row, col in st.session_state.changed_cells:
            if row in df_colors.index and col in df_colors.columns:
                df_colors.at[row, col] = 'background-color: #bbf7d0; color: #047857; font-weight: bold; border: 1.5px solid #10b981;'
        return df_colors
    return df_to_style.style.apply(highlight_cells, axis=None)

# 🧠 AI CHATBOT ENGINE
def render_ai_chatbot(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 VeriSame Core AI Chat Bot")
    chat_html = "<div style='max-height: 280px; overflow-y: auto; padding: 12px; background: #ffffff !important; border: 2px solid #9333ea; border-radius: 14px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history:
        if chat["role"] == "assistant":
            chat_html += f"<p style='color: #6b21a8 !important; margin: 5px 0; font-weight: 700;'><b>🤖 AI:</b> {chat['message']}</p>"
        else:
            chat_html += f"<p style='color: #000000 !important; margin: 5px 0; font-weight: 600;'><b>👤 You:</b> {chat['message']}</p>"
    chat_html += "</div>"
    target.markdown(chat_html, unsafe_allow_html=True)

    s_id = "side" if is_sidebar else "main"
    user_msg = target.text_input("Ask advanced questions...", placeholder="Ask about tools, pricing, actions...", key=f"chat_in_{s_id}")
    submit = target.button("Send Message 🚀", key=f"btn_send_chat_{s_id}")

    if submit and user_msg and user_msg.strip():
        u = user_msg.lower().strip()
        st.session_state.chat_history.append({"role": "user", "message": user_msg})
        reply = query_groq_ai(user_msg)
        if not reply:
            reply = "I am VeriSame Assistant! Ask me about tool capabilities, row limits, or subscription options."
        st.session_state.chat_history.append({"role": "assistant", "message": reply})
        st.rerun()

if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button("🚪 Logout Workspace / Exit", use_container_width=True):
        for key in ['plan','email','df_clean','df_original','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed','last_upload_sig','reset_announced','last_apply_msg']:
            st.session_state[key] = None if key in ['plan','email','df_clean','df_original','days','selected_plan','orig_len','empty_fixed','last_upload_sig','last_apply_msg'] else False
        st.session_state.changed_cells = set()
        st.session_state.uploaded_files = {}
        st.rerun()

days_left_global = None
if st.session_state.email:
    db_state = load_db()
    user = db_state.get(st.session_state.email, {})
    st.sidebar.success(f"📧 {st.session_state.email}")
    render_ai_chatbot(is_sidebar=True)
    
    if user.get("plan"):
        # AUTOMATIC PLAN EXPIRY CHECK
        if user.get("plan") == "pro" and user.get("expiry"):
            try:
                exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d").date()
                today = datetime.now().date()
                days_left_global = (exp_date - today).days
                if days_left_global <= 0:
                    user["plan"] = "free"
                    user["status"] = "PAID"
                    user["amt"] = 0
                    db_state[st.session_state.email] = user
                    save_db(db_state)
                    st.sidebar.warning("⚠️ Your PRO plan has expired! Reverted to Free mode.")
                    days_left_global = 0
            except Exception:
                pass

        st.session_state.plan = user.get("plan")
        st.session_state.amt = user.get("amt", 0)
        
        if user.get("plan") == "free": 
            st.sidebar.info("Plan: FREE FOREVER ✨ (200 Rows Limit)")
        else:
            st.session_state.admin_approved = user.get("status") == "PAID" and (days_left_global is None or days_left_global > 0)
            if days_left_global is not None and days_left_global > 0: 
                st.sidebar.info(f"Plan: PRO ({user.get('amt', 299)})\nValid Till: {user.get('expiry')}\n{days_left_global} days left")
                # 🚨 RED ALERT IF 5 DAYS OR LESS REMAINING
                if days_left_global <= 5:
                    st.sidebar.markdown(f"""<div style='background-color: #fee2e2; border: 2px solid #ef4444; border-radius: 12px; padding: 10px; margin-top: 10px;'><p style='color: #dc2626 !important; font-weight: 800; margin: 0;'>🚨 Plan Expiring in {days_left_global} Days!</p></div>""", unsafe_allow_html=True)

# 🎨 HEADER LAYOUT WITH TAGLINE BESIDE LOGO
col1, col2 = st.columns([1.2, 3.8])
with col1: 
    st.markdown("""<div class="logo-float" style="width: 100%; min-height: 240px; display: flex; align-items: center; justify-content: center;"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width: 100%; height: auto; max-height: 240px; object-fit: contain;"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="margin-top: 15px;">
        <h1 style='margin-bottom: 0px; display: inline-block; vertical-align: middle;'>VeriSame</h1>
        <span class="tagline-badge">Clean logic. Clear result</span>
        <div class="subtitle">The Fastest Way to Clean Your Data</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<div class='pro-banner'><h2>💎 {T['pro_banner']}</h2><div>{''.join([f'<span class=\"tool-chip\">{tool}</span>' for tool in ['Smart Date','AI Fill','Email AI','Phone AI','Case','Clean','Rename','Dedup','Trim','Spell']])}</div></div>", unsafe_allow_html=True)

# 🚨 SHOW RED DASHBOARD WARNING BANNER IF PLAN EXPIRES IN <= 5 DAYS
if days_left_global is not None and 0 < days_left_global <= 5:
    st.markdown(f"""
    <div class="red-alert-banner">
        🚨 <b>CRITICAL NOTICE:</b> Your VeriSame Pro Plan is expiring in <b>{days_left_global} days</b>! Please renew your plan to ensure uninterrupted dataset cleaning services.
    </div>
    """, unsafe_allow_html=True)

# 👑 ADMIN SECRET DASHBOARD PANEL (?admin=admin123)
if "admin" in st.query_params:
    if st.query_params.get("admin") == ADMIN_PASS:
        st.title(T['admin_title'])
        data = load_db()
        st.subheader(T['admin_pending'])

        if data:
            for email, info in list(data.items()):
                if "@" not in email: continue
                amt = info.get('amt', 0)
                status = info.get('status', 'PENDING')
                plan_text = f"PRO Monthly ₹299 (30 Days)" if amt == 299 else f"PRO ₹1499 (180 Days)" if amt == 1499 else "FREE Plan"
                col1, col2, col3 = st.columns([4, 2, 2])
                with col1:
                    status_color = "🟢 PAID UNLOCKED" if status == "PAID" else "⏳ PENDING APPROVAL"
                    st.markdown(f"""<div class='pricing-card' style='background: rgba(243, 232, 255, 0.9) !important;'><b>{T['admin_user']}:</b> {email}<br><b>{T['admin_plan']}:</b> {plan_text}<br><b>Status:</b> {status_color}<br><b>{T['admin_expiry']}:</b> {info.get('expiry','N/A')}</div>""", unsafe_allow_html=True)
                with col2:
                    if status == "PENDING" and info.get("plan") == "pro":
                        if st.button(T['admin_approve_btn'], key=f"verify_{email}", type="primary", use_container_width=True):
                            data[email]["status"] = "PAID"
                            user_amt = data[email].get("amt", 299)
                            exact_days = 180 if user_amt == 1499 else 30
                            data[email]["days"] = exact_days
                            data[email]["expiry"] = (datetime.now() + timedelta(days=exact_days)).strftime("%Y-%m-%d")
                            save_db(data); st.success(f"✓ {email} unlocked for {exact_days} days!"); st.balloons(); st.rerun()
                    else: st.button("✓ Active User", key=f"active_{email}", disabled=True, use_container_width=True)
                with col3:
                    if st.button(T['delete_btn'], key=f"delete_{email}", use_container_width=True):
                        del data[email]; save_db(data); st.error(f"✓ {email} deleted"); st.rerun()
        else: st.info("No records found in database.")
        st.stop()
    else:
        st.error("🔒 Unauthorized Access Detected. Admin Routing Halted.")
        st.stop()

# 💰 PRICING SELECTION WORKFLOW
if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        col1,col2,col3 = st.columns(3, gap="medium")
        with col1:
            st.markdown(f"""<div class='pricing-card'><h2>{T['free_title']}</h2><h1>FREE</h1><p>Lifetime (200 Rows Limit)</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['free_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan = "free"; st.rerun()
        with col2:
            st.markdown(f"""<div class='pricing-card' style='border: 3px solid #9333ea; box-shadow:0 15px 35px rgba(147,51,234,0.3)'><p>⭐ POPULAR</p><h2>{T['pro1_title']}</h2><h1>₹299</h1><p>1 Month (30 Days) - All Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro (1 Month / 30 Days)", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"; st.session_state.amt = PRO_1M; st.session_state.days = 30; st.rerun()
        with col3:
            st.markdown(f"""<div class='pricing-card'><h2>{T['pro6_title']}</h2><h1>₹1499</h1><p>6 Months (180 Days) - All Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro+ (6 Months / 180 Days)", key="btn_pro6", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"; st.session_state.amt = PRO_6M; st.session_state.days = 180; st.rerun()
        
        render_ai_chatbot(is_sidebar=False)
    else:
        st.markdown(f"<h2>Enter your email to continue with {st.session_state.selected_plan.upper()}</h2>", unsafe_allow_html=True)
        email_input = st.text_input(T['email_label'], placeholder="your@email.com").lower().strip()
        
        c_left, c_right = st.columns(2)
        with c_left:
            if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
                if "@" in email_input and "." in email_input:
                    st.session_state.email = email_input
                    st.session_state.email_entered = True
                    data = load_db()
                    selected_days = 180 if st.session_state.amt == 1499 else 30
                    
                    if email_input in data:
                        data[email_input]["plan"] = st.session_state.selected_plan
                        if st.session_state.selected_plan == "free":
                            data[email_input]["status"] = "PAID"
                            data[email_input]["amt"] = 0
                            data[email_input]["days"] = 36500
                            data[email_input]["expiry"] = "Lifetime"
                        else:
                            if data[email_input].get("status") != "PAID":
                                data[email_input]["status"] = "PENDING"
                                data[email_input]["amt"] = st.session_state.amt
                                data[email_input]["days"] = selected_days
                                data[email_input]["expiry"] = (datetime.now() + timedelta(days=selected_days)).strftime("%Y-%m-%d")
                        save_db(data)
                        st.session_state.plan = data[email_input]["plan"]
                        st.session_state.amt = data[email_input].get("amt", st.session_state.amt)
                        st.rerun()
                    else:
                        st.session_state.plan = st.session_state.selected_plan
                        if st.session_state.selected_plan == "free":
                            data[email_input] = {"plan":"free","status":"PAID","amt":0,"days":36500,"expiry":"Lifetime","created":str(datetime.now())}
                            save_db(data); st.balloons(); st.rerun()
                        else:
                            expiry = (datetime.now() + timedelta(days=selected_days)).strftime("%Y-%m-%d")
                            data[email_input] = {"plan":"pro","status":"PENDING","amt":st.session_state.amt,"days":selected_days,"expiry":expiry,"created":str(datetime.now())}
                            save_db(data); st.rerun()
                else: st.error("Valid email required")
        with c_right:
            if st.button("← Go Back to Plans", key="back_to_plans", use_container_width=True):
                st.session_state.selected_plan = None
                st.rerun()
        st.stop()
else:
    tab1,tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    
    with tab1:
        file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"], accept_multiple_files=True)
        if file:
            current_files = [f.name for f in file]
            sheet_selections = {}
            for f in file:
                if f.name.endswith((".xlsx", ".xls")):
                    try:
                        excel_file = pd.ExcelFile(f)
                        sheet_names = excel_file.sheet_names
                        selected_sheet = st.selectbox(f"📄 Select Sheet for {f.name}", sheet_names, key=f"sheet_sel_{f.name}")
                        sheet_selections[f.name] = selected_sheet
                    except Exception:
                        pass
            
            upload_sig = f"{current_files}-{list(sheet_selections.values())}"
            
            if st.session_state.get("last_upload_sig") != upload_sig:
                try: 
                    st.session_state.uploaded_files = {}
                    for f in file:
                        if f.name.endswith((".xlsx", ".xls")):
                            sheet = sheet_selections.get(f.name, 0)
                            sub_df = pd.read_excel(f, sheet_name=sheet)
                        elif f.name.endswith(".csv"):
                            sub_df = pd.read_csv(f)
                        else:
                            sub_df = pd.read_json(f)
                            
                        # 🔒 STRICT ENFORCEMENT OF 200 ROW LIMIT ON FREE TIER
                        if st.session_state.plan == "free" and len(sub_df) > FREE_ROW_LIMIT:
                            sub_df = sub_df.iloc[:FREE_ROW_LIMIT]
                            st.warning(f"⚠️ Free Plan Notice: Dataset capped at {FREE_ROW_LIMIT} rows. Upgrade to Pro for unlimited row processing.")

                        df_clean_init = sub_df.copy().drop_duplicates()
                        for col in df_clean_init.columns:
                            if df_clean_init[col].dtype == 'object':
                                df_clean_init[col] = df_clean_init[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                            if any(k in col.lower() for k in ['salary','amount','price','paisa']): 
                                df_clean_init[col] = df_clean_init[col].apply(words_to_num)
                        
                        st.session_state.uploaded_files[f.name] = {
                            "original": sub_df.copy(),
                            "clean": df_clean_init,
                            "orig_len": len(sub_df),
                            "empty_fixed": int(sub_df.isna().sum().sum()),
                            "changed_cells": set()
                        }
                    st.session_state.last_upload_sig = upload_sig
                except Exception as e: 
                    st.error(f"Error reading file: {str(e)}")
                    
    with tab2:
        if st.button(T['sample_btn'], use_container_width=True):
            sample_df = pd.DataFrame({
                "Date":["12/5/2024","","15-03-2023"],
                "Name":[" RAHUL KUMAR ","priya sharma","AMIT SINGH"],
                "Email":["RAHUL@GMAIL.COM","bad@gmai.com","priya@email.com"],
                "Phone":["98765-43210","9123 456 789","000123"],
                "Salary":["one hundred","250","two thousand five hundred"]
            })
            
            df_clean = sample_df.copy().drop_duplicates()
            for col in df_clean.columns:
                if df_clean[col].dtype == 'object':
                    df_clean[col] = df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                if any(k in col.lower() for k in ['salary','amount','price','paisa']): 
                    df_clean[col] = df_clean[col].apply(words_to_num)
                    
            st.session_state.uploaded_files = {
                "sample_data.csv": {
                    "original": sample_df.copy(),
                    "clean": df_clean,
                    "orig_len": len(sample_df),
                    "empty_fixed": int(sample_df.isna().sum().sum()),
                    "changed_cells": set()
                }
            }
            st.session_state.last_upload_sig = None
            st.toast("Sample data loaded successfully! 🎯")
            st.rerun()

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        file_keys = list(st.session_state.uploaded_files.keys())
        st.markdown("### 📁 File Selection Workspace")
        selected_file = st.selectbox("Choose which file to clean:", file_keys, key="active_file_selector")
        
        st.session_state.df_clean = st.session_state.uploaded_files[selected_file]["clean"]
        st.session_state.df_original = st.session_state.uploaded_files[selected_file]["original"]
        st.session_state.orig_len = st.session_state.uploaded_files[selected_file]["orig_len"]
        st.session_state.empty_fixed = st.session_state.uploaded_files[selected_file]["empty_fixed"]
        st.session_state.changed_cells = st.session_state.uploaded_files[selected_file]["changed_cells"]
        st.session_state.df_loaded = True

        df_clean = st.session_state.df_clean
        orig_len = st.session_state.orig_len

        st.markdown(f"<h2>{T['summary_title']}</h2>", unsafe_allow_html=True)
        
        # 🔄 MASTER RESET
        if st.button("🔄 Reset Dataset to Original State", type="secondary", use_container_width=True):
            if st.session_state.df_original is not None:
                st.session_state.df_clean = st.session_state.df_original.copy()
                st.session_state.changed_cells = set()
                for k in ["ms_date", "ms_fill", "ms_email", "ms_phone", "ms_case", "ms_spec", "sb_fuzzy", "ms_trim", "ms_spell"]:
                    if k in st.session_state: del st.session_state[k]
                st.session_state["reset_announced"] = True
                st.session_state["last_apply_msg"] = None
                st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.df_clean
                st.session_state.uploaded_files[selected_file]["changed_cells"] = set()
                st.rerun()

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric(T['rows'], orig_len)
        with c2: st.metric(T['clean'], len(df_clean))
        with c3: st.metric(T['dups'], max(0, orig_len-len(df_clean)))
        with c4: st.metric(T['empty'], st.session_state.empty_fixed)

        st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
        st.caption(T['preview'])
        
        styled_df = apply_cell_styling(df_clean.head(10))
        st.dataframe(styled_df, use_container_width=True, height=280)

        if st.session_state.get("reset_announced"):
            st.success("🔄 Success: Dataset reset to raw original state!")
            st.session_state["reset_announced"] = False

        if st.session_state.get("last_apply_msg"):
            st.success(st.session_state["last_apply_msg"])

        all_cols = df_clean.columns.tolist()
        text_cols = df_clean.select_dtypes(include=['object']).columns.tolist()
        date_filtered_cols = [col for col in all_cols if 'date' in col.lower() or 'time' in col.lower()] or all_cols
        email_filtered_cols = [col for col in all_cols if 'email' in col.lower() or 'mail' in col.lower()] or all_cols
        phone_filtered_cols = [col for col in all_cols if 'phone' in col.lower() or 'mobile' in col.lower()] or all_cols
        if not text_cols: text_cols = all_cols

        is_pro = st.session_state.plan == "pro"
        is_free = st.session_state.plan == "free"
        
        db_data = load_db()
        user_info = db_data.get(st.session_state.email, {})
        is_paid = user_info.get("status") == "PAID"

        # 🚀 MULTI-TOOL PROCESSING HUB
        st.markdown("<div style='background: #faf5ff; padding:15px; border-radius:14px; border:2px dashed #a855f7; margin-bottom:15px;'>", unsafe_allow_html=True)
        st.markdown("### ⚡ Execute All Tools Simultaneously")
        
        if st.button("🚀 Execute All Configured AI Tools Simultaneously", key="global_apply_btn", type="primary", use_container_width=True):
            simulate_processing()
            old_snapshot = st.session_state.df_clean.copy()
            tools_run = []
            
            # 1. Date
            if st.session_state.get("ms_date"):
                tools_run.append(T['tool1'])
                for col in st.session_state["ms_date"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(intelligent_date_parser)
            # 2. Nulls
            if not is_free and st.session_state.get("ms_fill"):
                tools_run.append(T['tool2'])
                for col in st.session_state["ms_fill"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].fillna("Unknown")
            # 3. Email
            if not is_free and st.session_state.get("ms_email"):
                tools_run.append(T['tool3'])
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in st.session_state["ms_email"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower().str.strip().str.replace("gmai.com", "gmail.com")
            # 4. Phone
            if not is_free and st.session_state.get("ms_phone"):
                tools_run.append(T['tool4'])
                for col in st.session_state["ms_phone"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x))[-10:])
            # 5. Case
            if st.session_state.get("ms_case"):
                tools_run.append(T['tool5'])
                case_opt = st.session_state.get("sel_case", "Uppercase")
                for col in st.session_state["ms_case"]:
                    if col in st.session_state.df_clean.columns:
                        if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.upper()
                        elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower()
                        else: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.title()
            # 6. Symbols
            if not is_free and st.session_state.get("ms_spec"):
                tools_run.append(T['tool6'])
                for col in st.session_state["ms_spec"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9\s.,₹$@\-+]', '', x))
            # 8. Fuzzy Duplicates
            if st.session_state.get("sb_fuzzy"):
                tools_run.append(T['tool8'])
                st.session_state.df_clean = remove_fuzzy_duplicates(st.session_state.df_clean, st.session_state["sb_fuzzy"])
            # 9. Trim
            if st.session_state.get("ms_trim"):
                tools_run.append(T['tool9'])
                for col in st.session_state["ms_trim"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

            track_modifications(old_snapshot, st.session_state.df_clean)
            st.session_state["last_apply_msg"] = f"🎉 Successfully applied tools: {', '.join(tools_run) if tools_run else 'None selected'}!"
            st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.df_clean
            st.session_state.uploaded_files[selected_file]["changed_cells"] = st.session_state.changed_cells
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # TABBED TOOL CONTROLS
        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
        with tab1:
            st.write(f"**{T['tool1']}** ✅ Unlocked")
            date_cols = st.multiselect(T['select_col'], date_filtered_cols, key="ms_date")
            if st.button(T['apply_btn'], key="btn_date", use_container_width=True):
                if date_cols:
                    simulate_processing()
                    old_snapshot = st.session_state.df_clean.copy()
                    for col in date_cols:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(intelligent_date_parser)
                    track_modifications(old_snapshot, st.session_state.df_clean)
                    st.session_state["last_apply_msg"] = T['success']
                    st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.df_clean
                    st.rerun()

            st.markdown("---")
            if is_free:
                st.write(f"**{T['tool2']}** 🔒 Locked (Upgrade to Pro)")
            else:
                st.write(f"**{T['tool2']}** ✅ Unlocked")
                fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill")
                if st.button(T['apply_btn'], key="btn_fill", use_container_width=True):
                    if fill_cols:
                        simulate_processing()
                        old_snapshot = st.session_state.df_clean.copy()
                        for col in fill_cols:
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].fillna("Unknown")
                        track_modifications(old_snapshot, st.session_state.df_clean)
                        st.session_state["last_apply_msg"] = T['success']
                        st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.df_clean
                        st.rerun()

        with tab2:
            if is_free:
                st.write(f"**{T['tool3']}** 🔒 Locked (Upgrade to Pro)")
            else:
                st.write(f"**{T['tool3']}** ✅ Unlocked")
                email_cols = st.multiselect(T['select_col'], email_filtered_cols, key="ms_email")
                if st.button(T['apply_btn'], key="btn_email", use_container_width=True):
                    if email_cols:
                        simulate_processing()
                        old_snapshot = st.session_state.df_clean.copy()
                        for col in email_cols:
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower().str.strip().str.replace("gmai.com", "gmail.com")
                        track_modifications(old_snapshot, st.session_state.df_clean)
                        st.session_state["last_apply_msg"] = T['success']
                        st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.df_clean
                        st.rerun()

        with tab3:
            st.write(f"**{T['tool5']}** ✅ Unlocked")
            case_cols = st.multiselect(T['select_col'], text_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
            if st.button(T['apply_btn'], key="btn_case", use_container_width=True):
                if case_cols:
                    simulate_processing()
                    old_snapshot = st.session_state.df_clean.copy()
                    for col in case_cols:
                        if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.upper()
                        elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower()
                        else: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.title()
                    track_modifications(old_snapshot, st.session_state.df_clean)
                    st.session_state["last_apply_msg"] = T['success']
                    st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.df_clean
                    st.rerun()

        # 📥 EXPORT WORKSPACE & QR CODE PAYMENT SECTION
        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
        
        if st.session_state.plan == "free":
            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            col1.download_button(T['download_csv'], csv, f"verisame_free_{selected_file}.csv", mime="text/csv", key="dl_csv_free", use_container_width=True)
            if openpyxl is not None:
                excel = io.BytesIO()
                st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                col2.download_button(T['download_excel'], excel.getvalue(), f"verisame_free_{selected_file}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_free", use_container_width=True)
            
        elif st.session_state.plan == "pro":
            if not is_paid:
                st.warning(T['wait_approval'])
                
                # 💸 DYNAMIC UPI QR GENERATOR WITH AUTO-FILLED AMOUNT
                pay_amt = st.session_state.amt if st.session_state.amt else 299
                upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={pay_amt}&cu=INR"
                
                st.markdown(f"### 💳 Payment Instructions for PRO Plan (₹{pay_amt})")
                
                col_qr, col_pay_info = st.columns([1, 2])
                with col_qr:
                    if qrcode is not None:
                        try:
                            qr = qrcode.make(upi_link)
                            buf = io.BytesIO()
                            qr.save(buf, format="PNG")
                            st.image(buf.getvalue(), width=220, caption=f"Scan to Pay ₹{pay_amt}")
                        except Exception:
                            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={urllib.parse.quote(upi_link)}"
                            st.image(qr_url, width=220, caption=f"Scan to Pay ₹{pay_amt}")
                    else:
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={urllib.parse.quote(upi_link)}"
                        st.image(qr_url, width=220, caption=f"Scan to Pay ₹{pay_amt}")

                with col_pay_info:
                    st.markdown(f"**Step 1:** Scan the QR code or click the direct UPI button below.")
                    st.markdown(f"**UPI ID:** `{UPI_ID}`")
                    st.link_button(f"📲 Tap Here to Open UPI App & Pay ₹{pay_amt}", upi_link, use_container_width=True)
                    st.markdown("---")
                    st.markdown("**Step 2:** After payment completion, click the button below to notify Admin.")
                    
                    if st.button(T['paid_btn'].format(amount=pay_amt), key="btn_paid", type="primary", use_container_width=True):
                        data = load_db()
                        selected_days = 180 if pay_amt == 1499 else 30
                        data[st.session_state.email] = {
                            "plan": "pro",
                            "amt": pay_amt,
                            "days": selected_days,
                            "expiry": (datetime.now() + timedelta(days=selected_days)).strftime("%Y-%m-%d"),
                            "status": "PENDING"
                        }
                        save_db(data)
                        st.success("🚀 Request sent to Secret Admin Panel! Once approved, your downloads will unlock.")
                        st.rerun()
            else:
                col1, col2, col3 = st.columns(3)
                csv = st.session_state.df_clean.to_csv(index=False).encode()
                col1.download_button(T['download_csv'], csv, f"verisame_pro_{selected_file}.csv", mime="text/csv", key="dl_csv_paid", use_container_width=True)
                if openpyxl is not None:
                    excel = io.BytesIO()
                    st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                    col2.download_button(T['download_excel'], excel.getvalue(), f"verisame_pro_{selected_file}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_paid", use_container_width=True)
                
                pdf_data = generate_pdf_report(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean)
                if pdf_data:
                    col3.download_button("Download Audit PDF Report 📊", pdf_data, f"verisame_audit_{selected_file}.pdf", mime="application/pdf", key="dl_pdf_paid", use_container_width=True)
