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

# PDF Report Generation Dependency
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except Exception:
    SimpleDocTemplate = None

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

UPI = "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
FREE_ROW_LIMIT = 200

# Secure admin password retrieval from Streamlit secrets
ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "admin123")

# 🔒 PERSISTENT DATABASE LOGIC
def load_db():
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    return data
        except Exception:
            pass
            
    if "saved_orders" in st.secrets:
        try:
            data = json.loads(st.secrets["saved_orders"])
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}

def save_db(d):
    try:
        with open("backup_orders.json", "w") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass

# 💰 ADVANCED WORD-TO-NUMBER CONVERSION ENGINE
def words_to_num(s):
    if pd.isna(s): return s
    if isinstance(s, (int, float)):
        return s
    
    s_str = str(s).lower().strip().replace(',', '')
    
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
        st.warning("Dataset cardinality is extremely high. Scanning top 1000 unique records to prevent engine freeze.")
        unique_values = unique_values[:1000]
        
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
    if SimpleDocTemplate is None:
        return None
    
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

T = {
    "title":"VeriSame","subtitle":"The Fastest Way to Clean Your Data","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"MONTHLY","pro6_title":"6 MONTHS",
    "free_feat":["200 Rows Limit","CSV Export","4 Free Tools Built-in","30s Processing","Email Support"],
    "pro_feat":["Unlimited Rows","CSV + Excel Export","10 Premium AI Tools","3s Speed","Priority Support","No Watermark","Lifetime Updates"],
    "email_label":"Enter your email address","continue_btn":"Verify & Continue","upload_tab":"📤 Upload File","sample_tab":"🎯 Try Demo",
    "upload_text":"Drop CSV, Excel or JSON file here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview (Green Highlights show where active tools worked 🟢)",
    "tools_menu":"AI Studio","back_btn":"← Back","download_title":"Export Data",
    "paid_msg":"Step 1: Pay ₹299 for 1 Month or ₹1499 for 6 Months via UPI. Step 2: Click I Paid button below.",
    "upi_text":"Scan QR to Pay ₹{amount}","paid_btn":"Customer I Paid ₹{amount}","wait_approval":"⏳ Waiting for Admin Approval...",
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
h1 {font-weight: 800!important; font-size: 3.2rem!important; margin-bottom: 0.2rem!important; background: linear-gradient(90deg, #6b21a8, #9333ea, #c084fc, #a855f7, #6b21a8); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 3s linear infinite;}
.subtitle {text-align: left; color: #000!important; font-size: 1.1rem!important; font-weight: 600!important; margin-bottom: 1rem!important;}
.logo-float {animation: float 3s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.pricing-card {
  position: relative; border-radius: 22px; padding: 1.6rem; background: rgba(255,255,255,0.92)!important;
  transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(147,51,234,0.15); border: 2.5px solid #9333ea;
}
.stButton>button {
    border-radius: 14px !important; 
    font-weight: 700 !important; 
    background: linear-gradient(90deg, #9333ea, #a855f7) !important; 
    color: white !important; 
    border: none !important; 
    padding: 13px 26px !important; 
    width: 100% !important; 
    box-shadow: 0 5px 18 rgba(147,51,234,0.4) !important; 
}
.pro-banner {background: linear-gradient(135deg, #7e22ce, #a855f7, #d946ef); padding: 1.6rem; border-radius: 22px; color: white!important; text-align: center; margin: 1rem 0;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.95); padding: 9px 17px; border-radius: 28px; margin: 4px; border: 2px solid #9333ea; color: #000!important;}
div[data-testid="stTabs"] button p {color: #000!important; font-weight: 700!important;}
div[data-testid="stTabs"] button {background: rgba(255,255,255,0.7)!important; border-radius: 12px; margin-right: 8px; border: 2px solid #9333ea;}
input[data-testid="stTextInputRootElement"], div[data-testid="stTextInput"] input {
    background-color: #ffffff !important; 
    color: #000000 !important; 
    border: 2px solid #9333ea !important; 
    border-radius: 11px !important;
}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame's Studio. 💎 How can I help you optimize your dataset today?"}]

if "changed_cells" not in st.session_state:
    st.session_state.changed_cells = set()

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# SETUP CORE REFRESH STATE CAPABILITIES
for key in ['plan','email','df_clean','df_original','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed','last_upload_sig','reset_announced','last_apply_msg']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['plan','email','df_clean','df_original','days','selected_plan','orig_len','empty_fixed','last_upload_sig','last_apply_msg'] else False

def track_modifications(old_df, new_df):
    try:
        for col in old_df.columns:
            if col in new_df.columns:
                mismatch_indices = old_df[old_df[col].astype(str) != new_df[col].astype(str)].index
                for idx in mismatch_indices:
                    st.session_state.changed_cells.add((idx, col))
    except Exception:
        pass

# 🟢 HIGHLIGHT LOGIC BOUNDED STRICTLY TO CURRENTLY ACTIVE SELECTED TOOL INTERFACES
def apply_cell_styling(df_to_style):
    active_cols = []
    for k in ["ms_date", "ms_fill", "ms_email", "ms_phone", "ms_case", "ms_spec", "sb_fuzzy", "ms_trim", "ms_spell"]:
        if k in st.session_state and st.session_state[k]:
            val = st.session_state[k]
            if isinstance(val, list): active_cols.extend(val)
            else: active_cols.append(val)
            
    def highlight_cells(x):
        df_colors = pd.DataFrame('', index=x.index, columns=x.columns)
        for row, col in st.session_state.changed_cells:
            if col in active_cols and row in df_colors.index and col in df_colors.columns:
                df_colors.at[row, col] = 'background-color: #bbf7d0; color: #047857; font-weight: bold; border: 1.5px solid #10b981;'
        return df_colors
    return df_to_style.style.apply(highlight_cells, axis=None)

# ADVANCED AI CHATBOT KNOWLEDGE BASE ENGINE
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
    user_msg = target.text_input("Ask advanced questions...", placeholder="Ask about tools, row limits, founder...", key=f"chat_in_{s_id}")
    submit = target.button("Send Message 🚀", key=f"btn_send_chat_{s_id}")

    if submit and user_msg and user_msg.strip():
        u = user_msg.lower().strip()
        st.session_state.chat_history.append({"role": "user", "message": user_msg})
        reply = None

        # Check live loaded dataset state context
        if st.session_state.get('df_loaded') and st.session_state.get('df_clean') is not None:
            live_df = st.session_state.df_clean
            if any(x in u for x in ["column", "columns", "what fields"]):
                reply = f"📊 **Live Dataset Columns:** Current active attributes are: `{', '.join(live_df.columns.tolist())}`."
            elif any(x in u for x in ["how many rows", "row count", "dataset size"]):
                reply = f"🔢 **Live Dataset Dimensions:** System currently handles `{len(live_df)}` rows across `{len(live_df.columns)}` columns."
            elif any(x in u for x in ["missing", "nulls", "empty boxes"]):
                reply = f"🛠️ **Cleanliness Status:** Captured `{st.session_state.get('empty_fixed', 0)}` missing values."

        if not reply:
            if any(x in u for x in ["bye", "tata", "exit"]): reply = "👋 **Goodbye! Enjoy cleaning your spreadsheets with VeriSame.**"
            elif any(x in u for x in ["thank you", "thanks"]): reply = "💖 **You are welcome! Let me know if you need more data cleaning help.**"
            elif any(x in u for x in ["haha", "hehe"]): reply = "😜 **Happy data processing!**"

        if not reply:
            knowledge_map = {
                # Founder & Identity
                "founder made creator created developer owner built architecture who designed anugya anugya singh": "👑 **Founder & Creator:** VeriSame was fully architected, designed, and coded by **Anugya Singh** to make preprocessing data effortless!",
                "your name naam identity profiling profile identify system bot": "💎 I am the **VeriSame Core Intelligence Bot**, built exclusively to guide you through VeriSame's 10 data cleaning tools.",
                
                # General App Capabilities & Pricing
                "what this app can do app work capability functionality features use utility details purpose": "💎 **VeriSame Capabilities:** VeriSame is an automated dataset cleaning platform. It standardizes dates, cleans emails & phones, handles missing values, removes fuzzy duplicates, and formats text in under 3 seconds.",
                "is this app free free version tier cost price free limit 200 rows": "✨ **Free Plan:** Free Forever with a limit of **200 rows**, CSV export, and 4 core tools (Date Converter, Case Converter, Fuzzy Deduplication, Trim Spaces).",
                "what is pro version premium cost subscription upgrades charges models tier level": "💎 **Pro Plan:** Unlocks **Unlimited Rows**, all 10 AI Tools, CSV + Excel exports, PDF Audit Reports, and 3s speed for ₹299 (1 Month) or ₹1499 (6 Months).",
                
                # File Formats & Reset
                "format formats csv excel xlsx json file types supported upload": "📤 **Supported Formats:** VeriSame supports `.csv`, `.xlsx`, `.xls`, and `.json` files, including multi-sheet Excel files!",
                "reset start over undo original raw clear cache": "🔄 **Resetting Data:** Click the **'Reset Active Dataset to Original Raw State'** button above the dataset summary to restore your original raw data at any time.",
                "pdf report audit report pdf download audit": "📊 **PDF Audit Report:** Available for Pro users upon export, generating a formal breakdown of ingested rows, removed duplicates, and fixed cells.",
                "bug error mistake crash glitch wrong stuck broken problem fix issue error code fault fail": "🛠️ **Troubleshooting:** Press **'Reset Active Dataset to Original Raw State'** to reset your cache. If problems persist, contact founder **Anugya Singh**.",
                "how to upload file spreadsheet csv excel insert": "📤 **File Ingestion:** Go to the 'Upload File' tab and drop your CSV, Excel, or JSON file.",
                "how to download file save file download csv excel export": "🎯 **Export Protocols:** Scroll down to 'Export Data' to download your clean file as CSV, Excel, or a PDF Audit Report.",

                # Overview of All Tools
                "how many tools total tools features list count kitne feature feature models number wise": """🛠️ **Total System Architecture:** VeriSame includes exactly **10 Engineering Tools**:
1. **Smart Date Converter** - Formats dates to standard YYYY-MM-DD.
2. **AI Fill Nulls** - Intelligently fills empty cells.
3. **Email Validator** - Validates email structures.
4. **Phone Formatter** - Formats 10-digit phone numbers.
5. **Case Converter** - UPPERCASE, lowercase, or Title Case.
6. **Remove Symbols** - Strips invalid characters while preserving currency keys.
7. **Bulk Rename** - Renames matrix spreadsheet column headers.
8. **Remove Duplicates / Fuzzy Match** - Merges close text matches.
9. **Trim Spaces** - Strips duplicate whitespaces.
10. **Spell Check** - Corrects common typos.""",

                # Individual Tool Deep Dives
                "tool 1 tool1 smart date date converter parse dates format date": "📅 **Tool 1 - Smart Date Converter:** Converts messy dates (e.g., DD/MM/YYYY, MM-DD-YYYY) into standardized `YYYY-MM-DD` ISO format.",
                "tool 2 tool2 ai fill nulls missing empty blank fill null values": "🛠️ **Tool 2 - AI Fill Nulls (Pro):** Automatically identifies missing data and fills blanks with intelligent context defaults (e.g., `0` for numeric, `missing@email.com` for email, `Unknown` for text).",
                "tool 3 tool3 email validator validate email clean email mail check": "✉️ **Tool 3 - Email Validator (Pro):** Checks emails against valid RFC patterns. Converts text to lowercase and replaces invalid formats with `Invalid Email`.",
                "tool 4 tool4 phone formatter mobile number contact phone clean": "📞 **Tool 4 - Phone Formatter (Pro):** Strips non-numeric characters, brackets, and spaces from contact numbers, extracting a clean 10-digit mobile number.",
                "tool 5 tool5 case converter uppercase lowercase titlecase text case": "🔤 **Tool 5 - Case Converter:** Converts textual columns into UPPERCASE, lowercase, or Title Case instantly.",
                "tool 6 tool6 remove symbols special characters clean symbols strip": "🔣 **Tool 6 - Remove Symbols (Pro):** Cleans noisy special characters while preserving standard punctuation and currency keys ($ , ₹).",
                "tool 7 tool7 bulk rename rename column header title rename columns": "✏️ **Tool 7 - Bulk Rename (Pro):** Allows you to select any existing column header and rename it cleanly.",
                "tool 8 tool8 remove duplicates fuzzy match similarity dedup deduplication": "🧠 **Tool 8 - Fuzzy Deduplication:** Uses string sequence matching algorithms to find near-identical textual records (e.g., 'John Doe' vs 'John Doe ') and merge duplicates.",
                "tool 9 tool9 trim spaces trailing leading whitespace space cleanup": "✂️ **Tool 9 - Trim Spaces:** Removes leading, trailing, and double spaces inside text fields.",
                "tool 10 tool10 spell check spelling typo correction fix typos": "🔠 **Tool 10 - Spell Check (Pro):** Scans selected text columns and automatically fixes common typing errors (e.g., 'salery' → 'Salary', 'teh' → 'The')."
            }
            
            best_score = 0.0
            best_reply = None
            user_words = [w for w in u.split() if len(w) > 2]
            
            for key_string, answer_text in knowledge_map.items():
                key_words = key_string.split()
                matched_words = sum(1 for w in user_words if w in key_words)
                word_ratio = matched_words / max(1, len(user_words)) if user_words else 0
                seq_ratio = difflib.SequenceMatcher(None, u, key_string).ratio()
                final_score = (word_ratio * 0.6) + (seq_ratio * 0.4)
                if final_score > best_score:
                    best_score = final_score
                    best_reply = answer_text
            
            if best_score >= 0.40 and best_reply: 
                reply = best_reply

        if not reply:
            reply = "I am configured by founder **Anugya Singh** to assist you with VeriSame's 10 data cleaning tools! You can ask me about any tool, file formats, or subscription options."

        st.session_state.chat_history.append({"role": "assistant", "message": reply})
        st.rerun()

if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button("🚪 Logout Workspace / Exit", use_container_width=True):
        for key in ['plan','email','df_clean','df_original','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed','last_upload_sig','reset_announced','last_apply_msg']:
            st.session_state[key] = None if key in ['plan','email','df_clean','df_original','days','selected_plan','orig_len','empty_fixed','last_upload_sig','last_apply_msg'] else False
        st.session_state.changed_cells = set()
        st.session_state.uploaded_files = {}
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
            st.sidebar.info("Plan: FREE FOREVER ✨ (200 Rows Limit)")
        else:
            exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d").date()
            days_left = (exp_date - datetime.now().date()).days
            st.session_state.admin_approved = user.get("status") == "PAID" and days_left > 0
            if days_left > 0: 
                st.sidebar.info(f"Plan: {user['plan'].upper()}\nValid Till: {user['expiry']}\n{days_left} days left")
                if days_left <= 3:
                    st.sidebar.markdown(f"<p style='color: #ef4444 !important; font-weight: 700; background-color: #fee2e2; padding: 10px; border-radius: 12px; border: 1.5px solid #fca5a5; margin-top: 10px;'>⚠️ Your plan will expire in {days_left} days!</p>", unsafe_allow_html=True)
            else:
                st.sidebar.info(f"Plan: {user['plan'].upper()}\nStatus: {user.get('status')}")

col1, col2 = st.columns([1.5, 3.5])
with col1: 
    st.markdown("""<div class="logo-float" style="width: 100%; min-height: 280px; display: flex; align-items: center; justify-content: center;"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width: 100%; height: auto; max-height: 280px; object-fit: contain;"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='margin-top: 25px; margin-bottom: 5px;'>VeriSame</h1>", unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{T["subtitle"]}</div>', unsafe_allow_html=True)

st.markdown(f"<div class='pro-banner'><h2>💎 {T['pro_banner']}</h2><div>{''.join([f"<span class='tool-chip'>{tool}</span>" for tool in ['Smart Date','AI Fill','Email AI','Phone AI','Case','Clean','Rename','Dedup','Trim','Spell']])}</div></div>", unsafe_allow_html=True)

# ADMIN ROUTING PANEL
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
                            days_to_add = data[email].get("days", 30)
                            data[email]["expiry"] = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
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
            st.markdown(f"""<div class='pricing-card'><h2>{T['free_title']}</h2><h1>FREE</h1><p>Lifetime (200 Rows Limit)</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['free_feat']])}</div></div>""", unsafe_allow_html=True)
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
                            data[email_input]["expiry"] = (datetime.now() + timedelta(days=36500)).strftime("%Y-%m-%d")
                        else:
                            if data[email_input].get("status") != "PAID":
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
                        selected_sheet = st.selectbox(f"📄 Select Sheet to Clean for {f.name}", sheet_names, key=f"sheet_sel_{f.name}")
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
                            
                        # ENFORCE 200 ROW LIMIT FOR FREE TIER
                        if st.session_state.plan == "free" and len(sub_df) > FREE_ROW_LIMIT:
                            sub_df = sub_df.head(FREE_ROW_LIMIT)
                            st.info(f"ℹ️ Free Plan active: Dataset capped to the first {FREE_ROW_LIMIT} rows.")

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
                "Email":["RAHUL@GMAIL.COM","bad@","priya@email.com"],
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
        selected_file = st.selectbox("Choose which uploaded file you want to review and clean below:", file_keys, key="active_file_selector")
        
        # Load picked active file variables dynamically
        st.session_state.df_clean = st.session_state.uploaded_files[selected_file]["clean"]
        st.session_state.df_original = st.session_state.uploaded_files[selected_file]["original"]
        st.session_state.orig_len = st.session_state.uploaded_files[selected_file]["orig_len"]
        st.session_state.empty_fixed = st.session_state.uploaded_files[selected_file]["empty_fixed"]
        st.session_state.changed_cells = st.session_state.uploaded_files[selected_file]["changed_cells"]
        st.session_state.df_loaded = True

        df_clean = st.session_state.df_clean
        orig_len = st.session_state.orig_len

        st.markdown(f"<h2>{T['summary_title']}</h2>", unsafe_allow_html=True)
        
        # 🔄 MASTER RESET INTERFACE
        if st.button("🔄 Reset Active Dataset to Original Raw State", type="secondary", use_container_width=True):
            if st.session_state.df_original is not None:
                st.session_state.df_clean = st.session_state.df_original.copy()
                st.session_state.changed_cells = set()
                for k in ["ms_date", "ms_fill", "ms_email", "ms_phone", "ms_case", "ms_spec", "sb_fuzzy", "ms_trim", "ms_spell"]:
                    if k in st.session_state: st.session_state[k] = []
                st.session_state["reset_announced"] = True
                st.session_state["last_apply_msg"] = None
                st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = set()
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

        # 🎯 EXPLICIT STATUS NOTIFICATION FEED
        if st.session_state.get("reset_announced"):
            st.success("🔄 Success: Your original raw dataset states have been completely reset and applied!")
            st.session_state["reset_announced"] = False

        if st.session_state.get("last_apply_msg"):
            msg_text = st.session_state["last_apply_msg"]
            if "No changes were required" in msg_text or "not needed" in msg_text:
                st.info(f"ℹ️ {msg_text}")
            else:
                st.success(msg_text)

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
        
        db_data = load_db()
        user_info = db_data.get(st.session_state.email, {})
        is_paid = user_info.get("status") == "PAID"

        # 🚀 RE-ENGINEERED MULTI-TOOL PROCESSING HUB (APPLY EVERYTHING AT ONCE)
        st.markdown("<div style='background: #faf5ff; padding:15px; border-radius:14px; border:2px dashed #a855f7; margin-bottom:15px;'>", unsafe_allow_html=True)
        st.markdown("### ⚡ Global Simultaneous Multi-Tool Hub")
        st.write("Configure column targets inside different option tabs below, then trigger this button to execute all tools together in a single operation phase.")
        
        if st.button("🚀 Execute All Configured AI Tools Simultaneously", key="global_apply_btn", type="primary", use_container_width=True):
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
                        sample = str(st.session_state.df_clean[col].dropna().iloc[0]).lower() if not st.session_state.df_clean[col].dropna().empty else ""
                        if any(k in col.lower() for k in ['salary','amount','price','paisa']): fill_val = 0
                        elif '@' in sample or 'email' in col.lower(): fill_val = "missing@email.com"
                        else: fill_val = "Unknown"
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].fillna(fill_val).replace(["nan", "None", "", " "], fill_val)
            # 3. Email
            if not is_free and st.session_state.get("ms_email"):
                tools_run.append(T['tool3'])
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                for col in st.session_state["ms_email"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower().str.strip().apply(lambda x: x if re.match(pattern, str(x)) else "Invalid Email")
            # 4. Phone
            if not is_free and st.session_state.get("ms_phone"):
                tools_run.append(T['tool4'])
                for col in st.session_state["ms_phone"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x)))
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: x[-10:] if len(x) >= 10 else x)
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
                fuzzy_target_col = st.session_state["sb_fuzzy"]
                if fuzzy_target_col in st.session_state.df_clean.columns:
                    st.session_state.df_clean = remove_fuzzy_duplicates(st.session_state.df_clean, fuzzy_target_col)
            # 9. Trim
            if st.session_state.get("ms_trim"):
                tools_run.append(T['tool9'])
                for col in st.session_state["ms_trim"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
            # 10. Spell Check
            if not is_free and st.session_state.get("ms_spell"):
                tools_run.append(T['tool10'])
                typo_dict = {"teh":"the","recieve":"receive","goverment":"government","salery":"salary","amout":"amount"}
                def fix_typos(text):
                    words = str(text).split()
                    return " ".join([typo_dict.get(w.lower(), w) for w in words])
                for col in st.session_state["ms_spell"]:
                    if col in st.session_state.df_clean.columns:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(fix_typos).astype(str).str.title()

            if not tools_run:
                st.session_state["last_apply_msg"] = "⚠️ No processing targets configured. Please select columns first inside the tabs below."
            else:
                track_modifications(old_snapshot, st.session_state.df_clean)
                if old_snapshot.equals(st.session_state.df_clean):
                    st.session_state["last_apply_msg"] = "This combination of tools is not needed because your column data is already perfectly clean."
                else:
                    st.session_state["last_apply_msg"] = f"🎉 Apply is completed! Successfully executed changes for: {', '.join(tools_run)}."
                
                # Save changes back into the correct multi-file state slot
                st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
        with tab1:
            st.write(f"**{T['tool1']}** ✅ Unlocked")
            date_cols = st.multiselect(T['select_col'], date_filtered_cols, key="ms_date")
            col_b1, col_b2 = st.columns(2)
            if col_b1.button(T['apply_btn'], key="btn_date", use_container_width=True):
                if date_cols:
                    old_snapshot = st.session_state.df_clean.copy()
                    for col in date_cols:
                        st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(intelligent_date_parser)
                    track_modifications(old_snapshot, st.session_state.df_clean)
                    if old_snapshot.equals(st.session_state.df_clean):
                        st.session_state["last_apply_msg"] = "This tool is not needed because your date variables are already completely optimized."
                    else:
                        st.session_state["last_apply_msg"] = T['success']
                    st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                    st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
                    st.rerun()
            if col_b2.button("✕ Reset / Clear Tool Selection", key="clear_date", use_container_width=True):
                if "ms_date" in st.session_state: del st.session_state["ms_date"]
                st.rerun()

            st.markdown("---")
            if is_free:
                st.write(f"**{T['tool2']}** 🔒 Locked (Upgrade to Pro)")
                st.multiselect(T['select_col'], all_cols, key="ms_fill_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_fill_disabled", disabled=True, use_container_width=True)
            else:
                st.write(f"**{T['tool2']}** ✅ Unlocked")
                fill_cols = st.multiselect(T['select_col'], all_cols, key="ms_fill")
                col_b3, col_b4 = st.columns(2)
                if col_b3.button(T['apply_btn'], key="btn_fill", use_container_width=True):
                    if fill_cols:
                        old_snapshot = st.session_state.df_clean.copy()
                        for col in fill_cols:
                            sample = str(st.session_state.df_clean[col].dropna().iloc[0]).lower() if not st.session_state.df_clean[col].dropna().empty else ""
                            if any(k in col.lower() for k in ['salary','amount','price','paisa']): fill_val = 0
                            elif '@' in sample or 'email' in col.lower(): fill_val = "missing@email.com"
                            else: fill_val = "Unknown"
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].fillna(fill_val).replace(["nan", "None", "", " "], fill_val)
                        track_modifications(old_snapshot, st.session_state.df_clean)
                        if old_snapshot.equals(st.session_state.df_clean):
                            st.session_state["last_apply_msg"] = "This tool is not needed because there are zero missing/null data blocks present."
                        else:
                            st.session_state["last_apply_msg"] = T['success']
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
                        st.rerun()
                if col_b4.button("✕ Reset / Clear Tool Selection", key="clear_fill", use_container_width=True):
                    if "ms_fill" in st.session_state: del st.session_state["ms_fill"]
                    st.rerun()

        with tab2:
            if is_free:
                st.write(f"**{T['tool3']}** 🔒 Locked (Upgrade to Pro)")
                st.multiselect(T['select_col'], email_filtered_cols, key="ms_email_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_fill_disabled_tab2", disabled=True, use_container_width=True)
            else:
                st.write(f"**{T['tool3']}** ✅ Unlocked")
                email_cols = st.multiselect(T['select_col'], email_filtered_cols, key="ms_email")
                col_b5, col_b6 = st.columns(2)
                if col_b5.button(T['apply_btn'], key="btn_email", use_container_width=True):
                    if email_cols:
                        old_snapshot = st.session_state.df_clean.copy()
                        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                        for col in email_cols: 
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower().str.strip().apply(lambda x: x if re.match(pattern, str(x)) else "Invalid Email")
                        track_modifications(old_snapshot, st.session_state.df_clean)
                        if old_snapshot.equals(st.session_state.df_clean):
                            st.session_state["last_apply_msg"] = "This tool is not needed because all rows are already legitimate email strings."
                        else:
                            st.session_state["last_apply_msg"] = T['success']
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
                        st.rerun()
                if col_b6.button("✕ Reset / Clear Tool Selection", key="clear_email", use_container_width=True):
                    if "ms_email" in st.session_state: del st.session_state["ms_email"]
                    st.rerun()

            st.markdown("---")
            if is_free:
                st.write(f"**{T['tool4']}** 🔒 Locked (Upgrade to Pro)")
                st.multiselect(T['select_col'], phone_filtered_cols, key="ms_phone_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_phone_disabled", disabled=True, use_container_width=True)
            else:
                st.write(f"**{T['tool4']}** ✅ Unlocked")
                phone_cols = st.multiselect(T['select_col'], phone_filtered_cols, key="ms_phone")
                col_b7, col_b8 = st.columns(2)
                if col_b7.button(T['apply_btn'], key="btn_phone", use_container_width=True):
                    if phone_cols:
                        old_snapshot = st.session_state.df_clean.copy()
                        for col in phone_cols: 
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x)))
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(lambda x: x[-10:] if len(x) >= 10 else x)
                        track_modifications(old_snapshot, st.session_state.df_clean)
                        if old_snapshot.equals(st.session_state.df_clean):
                            st.session_state["last_apply_msg"] = "This tool is not needed because all contact parameters are already fully cleaned."
                        else:
                            st.session_state["last_apply_msg"] = T['success']
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
                        st.rerun()
                if col_b8.button("✕ Reset / Clear Tool Selection", key="clear_phone", use_container_width=True):
                    if "ms_phone" in st.session_state: del st.session_state["ms_phone"]
                    st.rerun()

        with tab3:
            st.write(f"**{T['tool5']}** ✅ Unlocked")
            case_cols = st.multiselect(T['select_col'], text_cols, key="ms_case")
            case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
            col_b9, col_b10 = st.columns(2)
            if col_b9.button(T['apply_btn'], key="btn_case", use_container_width=True):
                if case_cols:
                    old_snapshot = st.session_state.df_clean.copy()
                    for col in case_cols: 
                        if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.upper()
                        elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower()
                        else: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.title()
                    track_modifications(old_snapshot, st.session_state.df_clean)
                    if old_snapshot.equals(st.session_state.df_clean):
                        st.session_state["last_apply_msg"] = "This tool is not needed because the dataset text case already conforms to your selection."
                    else:
                        st.session_state["last_apply_msg"] = T['success']
                    st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                    st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
                    st.rerun()
            if col_b10.button("✕ Reset / Clear Tool Selection", key="clear_case", use_container_width=True):
                if "ms_case" in st.session_state: del st.session_state["ms_case"]
                st.rerun()

            st.markdown("---")
            if is_free:
                st.write(f"**{T['tool6']}** 🔒 Locked (Upgrade to Pro)")
                st.multiselect(T['select_col'], text_cols, key="ms_spec_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_spec_disabled", disabled=True, use_container_width=True)
            else:
                st.write(f"**{T['tool6']}** ✅ Unlocked")
                spec_cols = st.multiselect(T['select_col'], text_cols, key="ms_spec")
                col_b11, col_b12 = st.columns(2)
                if col_b11.button(T['apply_btn'], key="btn_spec", use_container_width=True):
                    if spec_cols:
                        old_snapshot = st.session_state.df_clean.copy()
                        for col in spec_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9\s.,₹$@\-+]', '', x))
                        track_modifications(old_snapshot, st.session_state.df_clean)
                        if old_snapshot.equals(st.session_state.df_clean):
                            st.session_state["last_apply_msg"] = "This tool is not needed because there are no forbidden symbol arrays present."
                        else:
                            st.session_state["last_apply_msg"] = T['success']
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
                        st.rerun()
                if col_b12.button("✕ Reset / Clear Tool Selection", key="clear_spec", use_container_width=True):
                    if "ms_spec" in st.session_state: del st.session_state["ms_spec"]
                    st.rerun()

            st.markdown("---")
            if is_free:
                st.write(f"**{T['tool7']}** 🔒 Locked (Upgrade to Pro)")
                st.selectbox("Old column name", all_cols, key="sel_old_disabled", disabled=True)
                st.text_input("New column name", key="inp_new_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_rename_disabled", disabled=True, use_container_width=True)
            else:
                st.write(f"**{T['tool7']}** ✅ Unlocked")
                old = st.selectbox("Old column name", all_cols, key="sel_old")
                new = st.text_input("New column name", key="inp_new")
                col_b13, col_b14 = st.columns(2)
                if col_b13.button(T['apply_btn'], key="btn_rename", use_container_width=True):
                    if new and new.strip() != "" and old != new:
                        st.session_state.df_clean.rename(columns={old: new.strip()}, inplace=True)
                        st.session_state["last_apply_msg"] = "🎉 Column renaming successfully applied!"
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                        st.rerun()
                if col_b14.button("✕ Reset / Clear Tool Selection", key="clear_rename", use_container_width=True):
                    if "sel_old" in st.session_state: del st.session_state["sel_old"]
                    if "inp_new" in st.session_state: del st.session_state["inp_new"]
                    st.rerun()

            st.markdown("---")
            st.write(f"**{T['tool8']}** ✅ Unlocked")
            fuzzy_target_col = st.selectbox("Select Target Column for Fuzzy Deduplication", text_cols, key="sb_fuzzy")
            col_b15, col_b16 = st.columns(2)
            if col_b15.button(T['apply_btn'], key="btn_dedup", use_container_width=True):
                if fuzzy_target_col:
                    old_snapshot = st.session_state.df_clean.copy()
                    st.session_state.df_clean = remove_fuzzy_duplicates(st.session_state.df_clean, fuzzy_target_col)
                    if len(old_snapshot) == len(st.session_state.df_clean):
                        st.session_state["last_apply_msg"] = "This tool is not needed because there are no duplicate matching structures."
                    else:
                        st.session_state["last_apply_msg"] = T['success']
                    st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                    st.rerun()
            if col_b16.button("✕ Reset / Clear Tool Selection", key="clear_dedup", use_container_width=True):
                if "sb_fuzzy" in st.session_state: del st.session_state["sb_fuzzy"]
                st.rerun()

            st.markdown("---")
            st.write(f"**{T['tool9']}** ✅ Unlocked")
            trim_cols = st.multiselect(T['select_col'], text_cols, key="ms_trim")
            col_b17, col_b18 = st.columns(2)
            if col_b17.button(T['apply_btn'], key="btn_trim", use_container_width=True):
                if trim_cols:
                    old_snapshot = st.session_state.df_clean.copy()
                    for col in trim_cols: 
                        if st.session_state.df_clean[col].dtype == 'object':
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                    track_modifications(old_snapshot, st.session_state.df_clean)
                    if old_snapshot.equals(st.session_state.df_clean):
                        st.session_state["last_apply_msg"] = "This tool is not needed because there are no leading or trailing whitespace blocks."
                    else:
                        st.session_state["last_apply_msg"] = T['success']
                    st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                    st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
                    st.rerun()
            if col_b18.button("✕ Reset / Clear Tool Selection", key="clear_trim", use_container_width=True):
                if "ms_trim" in st.session_state: del st.session_state["ms_trim"]
                st.rerun()

            st.markdown("---")
            if is_free:
                st.write(f"**{T['tool10']}** 🔒 Locked (Upgrade to Pro)")
                st.multiselect(T['select_col'], text_cols, key="ms_spell_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_spell_disabled", disabled=True, use_container_width=True)
            else:
                st.write(f"**{T['tool10']}** ✅ Unlocked")
                spell_cols = st.multiselect(T['select_col'], text_cols, key="ms_spell")
                col_b19, col_b20 = st.columns(2)
                if col_b19.button(T['apply_btn'], key="btn_spell", use_container_width=True):
                    if spell_cols:
                        old_snapshot = st.session_state.df_clean.copy()
                        typo_dict = {"teh":"the","recieve":"receive","goverment":"government","salery":"salary","amout":"amount"}
                        def fix_typos(text):
                            words = str(text).split()
                            return " ".join([typo_dict.get(w.lower(), w) for w in words])
                        for col in spell_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].apply(fix_typos).astype(str).str.title()
                        track_modifications(old_snapshot, st.session_state.df_clean)
                        if old_snapshot.equals(st.session_state.df_clean):
                            st.session_state["last_apply_msg"] = "This tool is not needed because no common spelling typos were identified."
                        else:
                            st.session_state["last_apply_msg"] = T['success']
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["clean"] = st.session_state.df_clean
                        st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"] = st.session_state.changed_cells
                        st.rerun()
                if col_b20.button("✕ Reset / Clear Tool Selection", key="clear_spell", use_container_width=True):
                    if "ms_spell" in st.session_state: del st.session_state["ms_spell"]
                    st.rerun()

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
                if qrcode is not None:
                    upi_link = f"upi://pay?pa={UPI}&pn=VeriSame&am={st.session_state.amt}&cu=INR"
                    qr = qrcode.make(upi_link); buf = io.BytesIO(); qr.save(buf, format="PNG")
                    st.image(buf.getvalue(), width=220)
                else:
                    st.info(f"Send payment directly to UPI ID: {UPI}")
                    
                if st.button(T['paid_btn'].format(amount=st.session_state.amt), key="btn_paid", type="primary", use_container_width=True):
                    data = load_db()
                    selected_days = st.session_state.days if st.session_state.days else (180 if st.session_state.amt == 1499 else 30)
                    data[st.session_state.email] = {
                        "plan": "pro",
                        "amt": st.session_state.amt,
                        "days": selected_days,
                        "expiry": (datetime.now() + timedelta(days=selected_days)).strftime("%Y-%m-%d"),
                        "status": "PENDING"
                    }
                    save_db(data)
                    st.success("🚀 Request logged live in Admin Dashboard!")
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

    if not st.session_state.plan and not st.session_state.email_entered:
        pass
