import json, os, io, time, re
import pandas as pd
from datetime import datetime, timedelta
import difflib 
import urllib.parse
import streamlit as st

try:
    from groq import Groq
except Exception:
    Groq = None
try:
    import qrcode
except Exception:
    qrcode = None
try:
    import openpyxl
except Exception:
    openpyxl = None
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except Exception:
    SimpleDocTemplate = None

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

UPI_ID = st.secrets.get("UPI_ID", st.secrets.get("UPI", "playwithreyansh0@okhdfcbank")) if hasattr(st, 'secrets') else "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
FREE_ROW_LIMIT = 200
ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "admin123") if hasattr(st, 'secrets') else "admin123"
FEEDBACK_EMAIL = "singhparidhi800@gmail.com"

def load_db():
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and data: return data
        except: pass
    if hasattr(st, 'secrets') and "saved_orders" in st.secrets:
        try:
            data = json.loads(st.secrets["saved_orders"])
            if isinstance(data, dict): return data
        except: pass
    return {}

def save_db(d):
    try:
        with open("backup_orders.json", "w") as f: json.dump(d, f, indent=2)
    except: pass

def enforce_processing_delay():
    is_pro = st.session_state.get("plan") == "pro" and st.session_state.get("admin_approved")
    delay = 3 if is_pro else 15
    progress_text = f"⏳ VeriSame AI Cleaning with 10 Tools ({delay}s)..."
    my_bar = st.progress(0, text=progress_text)
    step = delay / 100.0
    for percent_complete in range(100):
        time.sleep(step)
        my_bar.progress(percent_complete + 1, text=progress_text)
    my_bar.empty()

def words_to_num(s):
    if pd.isna(s): return s
    if isinstance(s, (int, float)): return s
    s_str = str(s).lower().strip().replace(',', '')
    if s_str.isdigit(): return int(s_str)
    try: return float(s_str)
    except: pass
    num_words = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,'hundred':100,'thousand':1000,'lakh':100000,'crore':10000000,'million':1000000,'billion':1000000000}
    total=0; current=0; has=False
    for word in re.findall(r'\w+', s_str):
        if word in num_words:
            has=True; val=num_words[word]
            if val>=100:
                current=max(1,current)*val
                if val>=1000: total+=current; current=0
            else: current+=val
        elif word.isdigit():
            has=True; current+=int(word)
    return (total+current) if has else s

def remove_fuzzy_duplicates(dataframe, column_name, threshold=0.85):
    if column_name not in dataframe.columns or dataframe[column_name].dtype != 'object':
        return dataframe
    df_copy = dataframe.copy()
    unique_values = df_copy[column_name].dropna().unique()
    if len(unique_values) > 300: unique_values = unique_values[:300]
    mapping = {}
    for i, val1 in enumerate(unique_values):
        if val1 in mapping: continue
        for val2 in unique_values[i+1:]:
            s1,s2 = str(val1).strip().lower(), str(val2).strip().lower()
            ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
            if ratio >= threshold: mapping[val2]=val1
    df_copy[column_name] = df_copy[column_name].replace(mapping)
    return df_copy.drop_duplicates().reset_index(drop=True)

def intelligent_date_parser(date_str):
    if pd.isna(date_str) or str(date_str).strip().lower() in ["","nan","none","null","n/a"]: return None
    clean_str = str(date_str).strip().replace('/', '-').replace('.', '-')
    try:
        parsed_dt = pd.to_datetime(clean_str, dayfirst=True, errors='coerce')
        if not pd.isna(parsed_dt): return parsed_dt.strftime('%Y-%m-%d')
    except: pass
    formats = ['%Y-%m-%d','%d-%m-%Y','%m-%d-%Y','%d %b %Y','%d %B %Y','%b %d, %Y','%B %d, %Y','%Y/%m/%d','%d/%m/%Y']
    for fmt in formats:
        try: return datetime.strptime(clean_str, fmt).strftime('%Y-%m-%d')
        except: continue
    match = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})', clean_str)
    if match:
        d,m,y = match.group(1), match.group(2), match.group(3)
        if len(y)==2: y="20"+y
        try: return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        except: pass
    return str(date_str)

def generate_pdf_report(orig_len, clean_len, empty_fixed, df):
    if SimpleDocTemplate is None: return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story=[]; styles=getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#6b21a8'), spaceAfter=15)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=11, textColor=colors.HexColor('#4b5563'), spaceAfter=25)
    story.append(Paragraph("VeriSame - AI Data Audit Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Account: {st.session_state.get('email','Guest')}", sub_style))
    story.append(Spacer(1,10))
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#1f2937'), spaceAfter=8)
    metric_data=[[Paragraph("<b>Metric Parameter</b>", text_style), Paragraph("<b>Value Counts</b>", text_style)],[Paragraph("Total Ingested Rows", text_style), Paragraph(str(orig_len), text_style)],[Paragraph("Clean Post-Processed Rows", text_style), Paragraph(str(clean_len), text_style)],[Paragraph("Duplicate Rows Extracted", text_style), Paragraph(str(orig_len-clean_len), text_style)],[Paragraph("Empty/Null Cells Fixed", text_style), Paragraph(str(empty_fixed), text_style)]]
    t1=Table(metric_data, colWidths=[250,200])
    t1.setStyle(TableStyle([('BACKGROUND',(0,0),(1,0),colors.HexColor('#9333ea')),('TEXTCOLOR',(0,0),(1,0),colors.white),('ALIGN',(0,0),(-1,-1),'LEFT'),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#c084fc'))]))
    story.append(t1); doc.build(story); buffer.seek(0); return buffer.getvalue()

def query_groq_ai(prompt_text, system_instruction="You are VeriSame AI assistant."):
    groq_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, 'secrets') else None
    if not groq_key or Groq is None: return None
    try:
        client = Groq(api_key=groq_key)
        completion = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":system_instruction},{"role":"user","content":prompt_text}], temperature=0.5, max_tokens=400)
        return completion.choices[0].message.content
    except Exception as e:
        st.session_state["groq_last_error"]=str(e); return None

def display_upi_qr(upi_uri, pay_amount):
    qr_generated=False
    if qrcode is not None:
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=2); qr.add_data(upi_uri); qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white"); buf=io.BytesIO(); img.save(buf, format="PNG")
            st.image(buf.getvalue(), width=220, caption=f"Scan to pay ₹{pay_amount}"); qr_generated=True
        except: qr_generated=False
    if not qr_generated:
        encoded_link = urllib.parse.quote(upi_uri)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={encoded_link}"
        st.image(qr_url, width=220, caption=f"Scan to pay ₹{pay_amount}")

def clear_widget_state(key_name, default_value=None):
    if default_value is None: default_value=[]
    st.session_state[key_name]=default_value

def render_feedback_front():
    st.markdown("---")
    st.markdown("### 💌 Feedback - Direct to Owner")
    st.caption(f"Your feedback will be sent to {FEEDBACK_EMAIL}")
    fb_front = st.text_area("Write your feedback here", placeholder="I love VeriSame... or any bug...", key="fb_front")
    if st.button("Send Feedback to Owner", key="fb_front_btn"):
        if fb_front.strip():
            subject = urllib.parse.quote(f"VeriSame Feedback from {st.session_state.get('email','Guest')}")
            body = urllib.parse.quote(fb_front)
            mailto = f"mailto:{FEEDBACK_EMAIL}?subject={subject}&body={body}"
            st.markdown(f"[📧 Click to send via Email App]({mailto})")
            st.success("Thank you! Click the link above to send.")
        else:
            st.warning("Please write feedback first")

def render_feedback_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💌 Feedback")
    st.sidebar.caption(f"To: {FEEDBACK_EMAIL}")
    fb_text = st.sidebar.text_area("Your feedback goes to owner", placeholder="Write feedback...", key="fb_text")
    if st.sidebar.button("Send Feedback", key="fb_send"):
        if fb_text.strip():
            subject = urllib.parse.quote(f"VeriSame Feedback from {st.session_state.get('email','Guest')}")
            body = urllib.parse.quote(fb_text)
            mailto = f"mailto:{FEEDBACK_EMAIL}?subject={subject}&body={body}"
            st.sidebar.markdown(f"[Click to send via Email]({mailto})")
            st.sidebar.success("Opening your email app...")
        else:
            st.sidebar.warning("Write something!")

T = {
    "title":"VeriSame","subtitle":"The Fastest Way to Clean Your Data","pro_banner":"UNLOCK 10 PREMIUM AI TOOLS",
    "free_title":"FREE FOREVER","pro1_title":"1 MONTH (30 DAYS)","pro6_title":"6 MONTHS (180 DAYS)",
    "free_feat":["200 Rows Limit","6 Tools Only (Date, Case, Dedup, Trim, Word2Num, Basic Clean)","Lifetime Free","15s Processing Delay","Email Support"],
    "pro_feat":["Unlimited Rows","10 Premium AI Tools - All Tools","CSV + Excel Export + PDF Report","3s Super Fast Speed","Priority Support","No Watermark"],
    "email_label":"Enter your email address","continue_btn":"Verify & Continue","upload_tab":"📤 Upload File","sample_tab":"🎯 Try Demo",
    "upload_text":"Drop CSV, Excel or JSON file here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview (Green 🟢 Modified | Red 🔴 Fixed Problems)",
    "tools_menu":"AI Studio - 1 Click Auto Clean","download_title":"Export Data","paid_msg":"Step 1: Select plan. Step 2: Pay via UPI/QR. Step 3: Click 'I Paid' for Admin approval.",
    "paid_btn":"I Paid ₹{amount} - Submit for Approval","wait_approval":"⏳ Request submitted! Waiting for Admin approval... Balloons after approval!",
    "download_success":"🎉 Download Ready!","tool1":"Smart Date Converter","tool2":"AI Fill Nulls","tool3":"Email Validator","tool4":"Phone Formatter","tool5":"Case Converter",
    "tool6":"Remove Symbols","tool7":"Bulk Rename","tool8":"Remove Duplicates / Fuzzy Match","tool9":"Trim Spaces","tool10":"Spell Check",
    "select_col":"Select Columns","select_case":"Choose Case Type","apply_btn":"Apply Actions","success":"Apply is completed! Your data has been successfully updated.",
    "admin_title":"👑 Admin Dashboard Panel 👑","admin_pending":"User Databases & Purchase Requests","admin_approve_btn":"Mark Paid - Unlock Customer Download + Balloons",
    "admin_user":"Customer Email","admin_plan":"Plan","admin_expiry":"Valid Till","delete_btn":"Delete User","download_csv":"Download as CSV","download_excel":"Download as Excel"
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 25%, #c084fc 50%, #a855f7 75%, #9333ea 100%); background-size: 400% 400%; animation: aurora 15s ease infinite; padding-top: 0.3rem;}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}
.block-container {background: rgba(255,255,255,0.96); backdrop-filter: blur(25px) saturate(180%); border-radius: 28px; padding: 2rem; max-width: 1200px; margin: 0 auto; box-shadow: 0 30px 60px rgba(139,92,246,0.25); border: 1.5px solid rgba(255,255,255,0.5);}
h1,h2,h3,p,span,label,div,li {color: #000!important; font-weight: 600!important;}
h1 {font-weight: 800!important; font-size: 3.2rem!important; margin-bottom: 0.2rem!important; background: linear-gradient(90deg, #6b21a8, #9333ea, #c084fc, #a855f7, #6b21a8); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 3s linear infinite;}
.subtitle {text-align: left; color: #4b5563!important; font-size: 1.1rem!important; font-weight: 500!important; margin-top: 6px!important; margin-bottom: 1rem!important;}
.tagline-badge {display: inline-block; padding: 6px 16px; background: linear-gradient(135deg, #9333ea, #6b21a8); color: #ffffff !important; font-weight: 700 !important; font-size: 0.95rem; border-radius: 20px; letter-spacing: 0.4px; box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3); vertical-align: middle; margin-left: 12px;}
.logo-float {animation: float 3s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.pricing-card {position: relative; border-radius: 22px; padding: 1.6rem; background: rgba(255,255,255,0.92)!important; transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(147,51,234,0.15); border: 2.5px solid #9333ea;}
.stButton>button {border-radius: 14px !important; font-weight: 700 !important; background: linear-gradient(90deg, #9333ea, #a855f7) !important; color: white !important; border: none !important; padding: 13px 26px !important; width: 100% !important; box-shadow: 0 5px 18px rgba(147,51,234,0.4) !important; }
.pro-banner {background: linear-gradient(135deg, #7e22ce, #a855f7, #d946ef); padding: 1.6rem; border-radius: 22px; color: white!important; text-align: center; margin: 1rem 0;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.95); padding: 9px 17px; border-radius: 28px; margin: 4px; border: 2px solid #9333ea; color: #000!important;}
.expiry-warning {background-color: #fee2e2 !important; border: 2px solid #ef4444 !important; border-radius: 16px; padding: 15px; margin-bottom: 20px; color: #991b1b !important; font-weight: 700 !important;}
.plan-status-box {padding: 12px 16px; border-radius: 14px; font-weight: 700 !important; margin-bottom: 12px;}
.plan-active {background-color: #dcfce7 !important; border: 2px solid #22c55e !important; color: #15803d !important;}
.plan-inactive {background-color: #fee2e2 !important; border: 2px solid #ef4444 !important; color: #b91c1c !important;}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame AI Studio. 💎 How can I help you clean or optimize your dataset today?"}]
if "changed_cells" not in st.session_state: st.session_state.changed_cells = set()
if "problem_cells" not in st.session_state: st.session_state.problem_cells = set()
if "uploaded_files" not in st.session_state: st.session_state.uploaded_files = {}
for key in ['plan','email','df_clean','df_original','show_balloon','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed','last_upload_sig','reset_announced','last_apply_msg','hub_report','clean_done']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['plan','email','df_clean','df_original','days','selected_plan','orig_len','empty_fixed','last_upload_sig','last_apply_msg','hub_report'] else False

def update_changed_cells():
    if st.session_state.df_original is None or st.session_state.df_clean is None:
        st.session_state.changed_cells=set(); return
    orig_df = st.session_state.df_original.reset_index(drop=True)
    clean_df = st.session_state.df_clean.reset_index(drop=True)
    changed=set()
    min_rows=min(len(orig_df), len(clean_df))
    common_cols=[c for c in orig_df.columns if c in clean_df.columns]
    for col in common_cols:
        orig_vals=orig_df[col].iloc[:min_rows].fillna("").astype(str).values
        clean_vals=clean_df[col].iloc[:min_rows].fillna("").astype(str).values
        for idx in range(min_rows):
            if orig_vals[idx]!=clean_vals[idx]: changed.add((idx,col))
    st.session_state.changed_cells=changed
    if "active_file_selector" in st.session_state and st.session_state.active_file_selector in st.session_state.uploaded_files:
        st.session_state.uploaded_files[st.session_state.active_file_selector]["changed_cells"]=changed

def apply_cell_styling(df_to_style):
    df_temp = df_to_style.copy().reset_index(drop=True)
    def highlight_cells(data):
        df_colors = pd.DataFrame('', index=data.index, columns=data.columns)
        for row,col in st.session_state.get("changed_cells", set()):
            if row in df_colors.index and col in df_colors.columns:
                df_colors.at[row,col]='background-color: #bbf7d0; color: #047857; font-weight: bold; border: 1.5px solid #10b981;'
        for row,col in st.session_state.get("problem_cells", set()):
            if row in df_colors.index and col in df_colors.columns:
                df_colors.at[row,col]='background-color: #fecaca; color: #991b1b; font-weight: bold; border: 1.5px solid #ef4444;'
        return df_colors
    return df_temp.style.apply(highlight_cells, axis=None)

def render_ai_chatbot(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 VeriSame Core AI Chat Bot")
    chat_html = "<div style='max-height: 280px; overflow-y: auto; padding: 12px; background: #ffffff !important; border: 2px solid #9333ea; border-radius: 14px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history:
        if chat["role"]=="assistant": chat_html+=f"<p style='color: #6b21a8 !important; margin: 5px 0; font-weight: 700;'><b>🤖 AI:</b> {chat['message']}</p>"
        else: chat_html+=f"<p style='color: #000000 !important; margin: 5px 0; font-weight: 600;'><b>👤 You:</b> {chat['message']}</p>"
    chat_html+="</div>"
    target.markdown(chat_html, unsafe_allow_html=True)
    s_id="side" if is_sidebar else "main"
    user_msg = target.text_input("Ask advanced questions...", placeholder="Ask about tools, recommend actions, pricing...", key=f"chat_in_{s_id}")
    submit = target.button("Send Message 🚀", key=f"btn_send_chat_{s_id}")
    if submit and user_msg and user_msg.strip():
        u=user_msg.lower().strip()
        st.session_state.chat_history.append({"role":"user","message":user_msg})
        reply=None
        system_prompt="You are the official AI assistant for VeriSame, a data cleaning platform built by Anugya. Keep answers helpful, clear, and focused on dataset cleaning, data preprocessing, and VeriSame's 10 tools."
        groq_reply=query_groq_ai(user_msg, system_instruction=system_prompt)
        if groq_reply: reply=groq_reply
        if not reply:
            tools_database={1:{"desc":"📅 **Tool 1 - Smart Date Converter:** Standardizes messy date strings into clean YYYY-MM-DD ISO format.","keywords":["smart date","date converter","date ai","tool 1"]},2:{"desc":"🛠️ **Tool 2 - AI Fill Nulls (Pro):** Detects missing values and populates blank cells using contextual defaults.","keywords":["ai fill","fill nulls","nulls","empty cells","tool 2"]},3:{"desc":"✉️ **Tool 3 - Email Validator (Pro):** Validates email RFC patterns and fixes common domain typos.","keywords":["email ai","email validator","email","tool 3"]},4:{"desc":"📞 **Tool 4 - Phone Formatter (Pro):** Standardizes phone numbers into clean 10-digit mobile numbers.","keywords":["phone ai","phone formatter","phone","mobile","tool 4"]},5:{"desc":"🔤 **Tool 5 - Case Converter:** Converts text columns into UPPERCASE, lowercase, Title Case, or Sentence case.","keywords":["case converter","case","uppercase","lowercase","tool 5"]},6:{"desc":"🔣 **Tool 6 - Remove Symbols (Pro):** Strips special characters while safeguarding currency keys.","keywords":["remove symbols","symbol cleaner","symbols","tool 6"]},7:{"desc":"✏️ **Tool 7 - Bulk Rename (Pro):** Renames individual columns or automatically cleans headers to snake_case.","keywords":["bulk rename","rename column","rename","tool 7"]},8:{"desc":"🧠 **Tool 8 - Fuzzy Deduplication:** Scans text columns using sequence algorithms to merge duplicate records.","keywords":["fuzzy deduplication","deduplication","duplicates","tool 8"]},9:{"desc":"✂️ **Tool 9 - Trim Spaces:** Cleans leading, trailing, and double whitespaces inside text cells.","keywords":["trim spaces","trim","whitespace","tool 9"]},10:{"desc":"🔠 **Tool 10 - Spell Check (Pro):** Scans text columns and corrects common typing blunders.","keywords":["spell check","spelling","typo","tool 10"]}}
            for t_info in tools_database.values():
                if any(kw in u for kw in t_info["keywords"]): reply=t_info["desc"]; break
            if not reply:
                if any(x in u for x in ["bye","exit"]): reply="👋 Goodbye! Enjoy cleaning your spreadsheets with VeriSame."
                elif any(x in u for x in ["thank you","thanks"]): reply="💖 You are very welcome! Let me know if you need more data cleaning help."
                elif u in ["hi","hello","hey"]: reply="👋 Hello! Ask me about any tool, pricing, or recommendations for your file!"
                else: reply="💡 Ask about any tool (e.g., 'Tool 1', 'Email Validator'), or ask about 'Pro Pricing'!"
        st.session_state.chat_history.append({"role":"assistant","message":reply}); st.rerun()

# ACCOUNT CHECK - SIDEBAR with BACK BUTTON
if st.session_state.email:
    db_state=load_db(); user=db_state.get(st.session_state.email,{})
    st.sidebar.success(f"📧 {st.session_state.email}")
    render_ai_chatbot(is_sidebar=True)
    # FEEDBACK AFTER CHATBOT IN SIDEBAR - AS YOU ASKED
    render_feedback_sidebar()
    
    if user.get("plan"):
        if user.get("plan")=="pro" and user.get("expiry"):
            try:
                exp_date=datetime.strptime(user["expiry"], "%Y-%m-%d").date(); today=datetime.now().date(); days_left=(exp_date-today).days
                if days_left>180:
                    exact_days=180 if user.get("amt")==PRO_6M else 30
                    exp_date=today+timedelta(days=exact_days); user["expiry"]=exp_date.strftime("%Y-%m-%d"); user["days"]=exact_days; db_state[st.session_state.email]=user; save_db(db_state)
                if exp_date<today:
                    user["plan"]="free"; user["status"]="EXPIRED"; user["amt"]=0; user["days"]=0; db_state[st.session_state.email]=user; save_db(db_state)
                    st.sidebar.warning("⚠️ Your PRO plan has expired! Access reverted to Free mode.")
            except: pass
        st.session_state.plan=user.get("plan"); st.session_state.amt=user.get("amt",0)
        if user.get("plan")=="pro" and user.get("status")=="PAID":
            try: exp_date=datetime.strptime(user["expiry"], "%Y-%m-%d").date()
            except: exp_date=datetime.now().date()+timedelta(days=30)
            st.session_state["user_plan_price"]=user.get("amt",299); st.session_state["expiry_date"]=exp_date
            PLANS={299:{"label":"PRO ₹299","total_days":30},1499:{"label":"PRO ₹1499","total_days":180}}
            current_plan_price=st.session_state.get("user_plan_price",299); plan_meta=PLANS.get(current_plan_price, PLANS[299])
            expiry_date=st.session_state.get("expiry_date", datetime.now().date()+timedelta(days=30))
            days_remaining=(expiry_date-datetime.now().date()).days; st.session_state.admin_approved=days_remaining>=0
            if days_remaining>=0:
                st.sidebar.markdown("<div class='plan-status-box plan-active'>🟢 Pro Active</div>", unsafe_allow_html=True)
                st.sidebar.markdown(f"**Plan: {plan_meta['label']} ({plan_meta['total_days']} Days Plan)**")
                st.sidebar.markdown(f"⏳ **Countdown:** {days_remaining} Days Remaining")
                st.sidebar.markdown(f"📅 **Valid Until:** {expiry_date.strftime('%Y-%m-%d')}")
                if days_remaining<=5:
                    st.sidebar.markdown(f"<p style='color: #dc2626 !important; font-weight: 700; background-color: #fee2e2; padding: 12px; border-radius: 12px; border: 2px solid #ef4444; margin-top: 10px;'>🚨 Warning: Your PRO plan is going to end in {days_remaining} days!</p>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>🔴 Pro Inactive (Expired)</div>", unsafe_allow_html=True)
        else:
            if user.get("status")=="PENDING":
                user_amt=user.get('amt',PRO_1M); chosen_plan="PRO ₹299 (30 Days)" if user_amt==PRO_1M else "PRO ₹1499 (180 Days)"
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>⏳ Pro Pending Approval</div>", unsafe_allow_html=True)
                st.sidebar.warning(f"Chosen Plan: {chosen_plan}\nWaiting for Admin Approval")
            elif user.get("status")=="EXPIRED":
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>🔴 Pro Inactive (Expired)</div>", unsafe_allow_html=True)
                st.sidebar.info("Plan: FREE FOREVER ✨ (200 Rows Limit)")
            else:
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>🔴 Free Plan</div>", unsafe_allow_html=True)
                st.sidebar.info("Plan: FREE FOREVER ✨ (200 Rows Limit | 15s Speed)")

if st.session_state.plan or st.session_state.email_entered:
    if st.sidebar.button("🚪 Logout Workspace / Exit", use_container_width=True):
        for key in ['plan','email','df_clean','df_original','payment_clicked','amt','sample_loaded','email_entered','days','selected_plan','admin_approved','df_loaded','orig_len','empty_fixed','last_upload_sig','reset_announced','last_apply_msg','hub_report','clean_done']:
            st.session_state[key]=None if key in ['plan','email','df_clean','df_original','days','selected_plan','orig_len','empty_fixed','last_upload_sig','last_apply_msg','hub_report'] else False
        st.session_state.changed_cells=set(); st.session_state.problem_cells=set(); st.session_state.uploaded_files={}; st.rerun()
    # BACK BUTTON IN SIDEBAR - AS YOU ASKED
    if st.sidebar.button("← Back to Plans", key="sidebar_back", use_container_width=True):
        st.session_state.selected_plan=None; st.session_state.plan=None; st.session_state.email_entered=False; st.rerun()

# HEADER
col1, col2 = st.columns([1.2, 3.8])
with col1: 
    st.markdown("""<div class="logo-float" style="width: 100%; min-height: 240px; display: flex; align-items: center; justify-content: center;"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width: 100%; height: auto; max-height: 240px; object-fit: contain;"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div style="margin-top: 15px;"><h1 style='margin-bottom: 0px; display: inline-block; vertical-align: middle;'>VeriSame</h1><span class="tagline-badge">Clean logic. Clear result</span><div class="subtitle">The Fastest Way to Clean Your Data</div></div>""", unsafe_allow_html=True)

st.markdown(f"<div class='pro-banner'><h2>💎 {T['pro_banner']}</h2><div>{''.join([f'<span class=\"tool-chip\">{tool}</span>' for tool in ['Smart Date','AI Fill','Email AI','Phone AI','Case','Clean','Rename','Dedup','Trim','Spell']])}</div></div>", unsafe_allow_html=True)

# ADMIN
if "admin" in st.query_params:
    if st.query_params.get("admin")==ADMIN_PASS:
        st.title(T['admin_title']); data=load_db(); st.subheader(T['admin_pending'])
        if data:
            for email,info in list(data.items()):
                if "@" not in email: continue
                amt=info.get('amt',0); status=info.get('status','PENDING')
                plan_text=f"PRO ₹299 (1 Month / 30 Days)" if amt==PRO_1M else f"PRO ₹1499 (6 Months / 180 Days)" if amt==PRO_6M else "FREE Plan"
                c1,c2,c3=st.columns([4,2,2])
                with c1:
                    status_color="🟢 PAID UNLOCKED" if status=="PAID" else "⏳ PENDING APPROVAL" if status=="PENDING" else "🔴 EXPIRED"
                    st.markdown(f"""<div class='pricing-card' style='background: rgba(243, 232, 255, 0.9) !important;'><b>{T['admin_user']}:</b> {email}<br><b>{T['admin_plan']}:</b> {plan_text}<br><b>Status:</b> {status_color}<br><b>{T['admin_expiry']}:</b> {info.get('expiry','N/A')}</div>""", unsafe_allow_html=True)
                with c2:
                    if status in ["PENDING","EXPIRED"] and info.get("plan")=="pro":
                        if st.button(T['admin_approve_btn'], key=f"verify_{email}", type="primary", use_container_width=True):
                            data[email]["status"]="PAID"; data[email]["plan"]="pro"; user_amt=data[email].get("amt",PRO_1M); exact_days=180 if user_amt==PRO_6M else 30
                            data[email]["amt"]=user_amt; data[email]["days"]=exact_days; data[email]["expiry"]=(datetime.now()+timedelta(days=exact_days)).strftime("%Y-%m-%d")
                            save_db(data); st.success(f"✓ {email} unlocked for {exact_days} days!"); st.balloons(); st.rerun()
                    else: st.button("✓ Active User", key=f"active_{email}", disabled=True, use_container_width=True)
                with c3:
                    if st.button(T['delete_btn'], key=f"delete_{email}", use_container_width=True):
                        del data[email]; save_db(data); st.error(f"✓ {email} deleted"); st.rerun()
        else: st.info("No records found in database.")
        st.stop()
    else:
        st.error("🔒 Unauthorized Access Detected. Admin Routing Halted."); st.stop()

# PRICING WORKFLOW - 2 BOXES
if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        col1,col2,col3 = st.columns(3, gap="medium")
        with col1:
            st.markdown(f"""<div class='pricing-card'><h2>{T['free_title']}</h2><h1>FREE</h1><p>Lifetime (200 Rows Limit)</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['free_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan="free"; st.rerun()
        with col2:
            st.markdown(f"""<div class='pricing-card' style='border: 3px solid #9333ea; box-shadow:0 15px 35px rgba(147,51,234,0.3)'><p>⭐ POPULAR</p><h2>{T['pro1_title']}</h2><h1>₹299</h1><p>1 Month / 30 Days - All Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro (1 Month / 30 Days)", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan="pro"; st.session_state.amt=PRO_1M; st.session_state.days=30; st.rerun()
        with col3:
            st.markdown(f"""<div class='pricing-card'><h2>{T['pro6_title']}</h2><h1>₹1499</h1><p>6 Months / 180 Days - All Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro+ (6 Months / 180 Days)", key="btn_pro6", type="primary", use_container_width=True):
                st.session_state.selected_plan="pro"; st.session_state.amt=PRO_6M; st.session_state.days=180; st.rerun()
        render_ai_chatbot(is_sidebar=False)
        # FEEDBACK AFTER CHATBOT IN FRONT PAGE - AS YOU ASKED
        render_feedback_front()
    else:
        st.markdown(f"<h2>Enter your email to continue with {st.session_state.selected_plan.upper()}</h2>", unsafe_allow_html=True)
        email_input = st.text_input(T['email_label'], placeholder="your@email.com").lower().strip()
        c_left,c_right=st.columns(2)
        with c_left:
            if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
                if "@" in email_input and "." in email_input:
                    st.session_state.email=email_input; st.session_state.email_entered=True; data=load_db()
                    if st.session_state.selected_plan=="free":
                        exact_days=36500; expiry=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d"); amt_val=0; status_val="PAID"
                    else:
                        exact_days=180 if st.session_state.amt==PRO_6M else 30; expiry=(datetime.now()+timedelta(days=exact_days)).strftime("%Y-%m-%d"); amt_val=st.session_state.amt; status_val="PENDING"
                    if email_input in data:
                        data[email_input]["plan"]=st.session_state.selected_plan
                        if st.session_state.selected_plan=="free":
                            data[email_input]["status"]="PAID"; data[email_input]["amt"]=0; data[email_input]["days"]=36500; data[email_input]["expiry"]=expiry
                        else:
                            if data[email_input].get("status")!="PAID":
                                data[email_input]["status"]="PENDING"; data[email_input]["amt"]=amt_val; data[email_input]["days"]=exact_days; data[email_input]["expiry"]=expiry
                        save_db(data); st.session_state.plan=data[email_input]["plan"]; st.session_state.amt=data[email_input].get("amt",st.session_state.amt); st.rerun()
                    else:
                        st.session_state.plan=st.session_state.selected_plan
                        data[email_input]={"plan":st.session_state.selected_plan,"status":status_val,"amt":amt_val,"days":exact_days,"expiry":expiry,"created":str(datetime.now())}
                        save_db(data)
                        if st.session_state.selected_plan=="free": st.balloons()
                        st.rerun()
                else: st.error("Valid email required")
        with c_right:
            # BACK BUTTON - AS YOU ASKED
            if st.button("← Back to Plans", key="back_to_plans", use_container_width=True):
                st.session_state.selected_plan=None; st.rerun()
        # ALSO RENDER FEEDBACK HERE AFTER EMAIL PAGE
        render_feedback_front()
        st.stop()
else:
    if st.session_state.email:
        db_state=load_db(); u_info=db_state.get(st.session_state.email,{})
        if u_info.get("plan")=="pro" and u_info.get("status")=="PAID" and u_info.get("expiry"):
            try:
                e_date=datetime.strptime(u_info["expiry"], "%Y-%m-%d").date(); rem_days=(e_date-datetime.now().date()).days
                if 0<=rem_days<=5:
                    st.markdown(f"""<div class="expiry-warning">🚨 <b>NOTIFICATION:</b> Your PRO plan is going to end in <b>{rem_days} days</b>! Please renew your plan to maintain uninterrupted access.</div>""", unsafe_allow_html=True)
            except: pass

    tab1, tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    with tab1:
        file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"], accept_multiple_files=True)
        if file:
            current_files=[f.name for f in file]; sheet_selections={}
            for f in file:
                if f.name.endswith((".xlsx",".xls")):
                    try:
                        excel_file=pd.ExcelFile(f); sheet_names=excel_file.sheet_names
                        selected_sheet=st.selectbox(f"📄 Select Sheet to Clean for {f.name}", sheet_names, key=f"sheet_sel_{f.name}"); sheet_selections[f.name]=selected_sheet
                    except: pass
            upload_sig=f"{current_files}-{list(sheet_selections.values())}"
            if st.session_state.get("last_upload_sig")!=upload_sig:
                try:
                    st.session_state.uploaded_files={}
                    for f in file:
                        if f.name.endswith((".xlsx",".xls")):
                            sheet=sheet_selections.get(f.name,0); sub_df=pd.read_excel(f, sheet_name=sheet)
                        elif f.name.endswith(".csv"): sub_df=pd.read_csv(f)
                        else: sub_df=pd.read_json(f)
                        if st.session_state.plan=="free" and len(sub_df)>FREE_ROW_LIMIT:
                            sub_df=sub_df.iloc[:FREE_ROW_LIMIT].copy()
                            st.warning(f"⚠️ Free Plan Active: Input file capped strictly to the first {FREE_ROW_LIMIT} rows.")
                        df_clean_init=sub_df.copy().drop_duplicates().reset_index(drop=True)
                        for col in df_clean_init.columns:
                            if df_clean_init[col].dtype=='object':
                                df_clean_init[col]=df_clean_init[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                            if any(k in col.lower() for k in ['salary','amount','price','paisa']): 
                                df_clean_init[col]=df_clean_init[col].apply(words_to_num)
                        st.session_state.uploaded_files[f.name]={"original":sub_df.copy().reset_index(drop=True),"clean":df_clean_init,"orig_len":len(sub_df),"empty_fixed":int(sub_df.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}
                    st.session_state.last_upload_sig=upload_sig
                except Exception as e: st.error(f"Error reading file: {str(e)}")
    with tab2:
        if st.button(T['sample_btn'], use_container_width=True):
            sample_df=pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT SINGH"],"Email":["RAHUL@GMAIL.COM","bad@gmai.com","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["one hundred","250","two thousand five hundred"]})
            df_clean=sample_df.copy().drop_duplicates().reset_index(drop=True)
            for col in df_clean.columns:
                if df_clean[col].dtype=='object': df_clean[col]=df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                if any(k in col.lower() for k in ['salary','amount','price','paisa']): df_clean[col]=df_clean[col].apply(words_to_num)
            st.session_state.uploaded_files={"sample_data.csv":{"original":sample_df.copy().reset_index(drop=True),"clean":df_clean,"orig_len":len(sample_df),"empty_fixed":int(sample_df.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}}
            st.session_state.last_upload_sig=None; st.toast("Sample data loaded successfully! 🎯"); st.rerun()

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        file_keys=list(st.session_state.uploaded_files.keys())
        st.markdown("### 📁 File Selection Workspace")
        col_back1, col_back2 = st.columns([1,3])
        with col_back1:
            if st.button("← Back", key="back_from_files"):
                st.session_state.uploaded_files={}; st.session_state.last_upload_sig=None; st.rerun()
        selected_file=st.selectbox("Choose which uploaded file you want to review and clean below:", file_keys, key="active_file_selector")
        if st.session_state.plan=="free":
            st.session_state.uploaded_files[selected_file]["clean"]=st.session_state.uploaded_files[selected_file]["clean"].iloc[:FREE_ROW_LIMIT]
            st.session_state.uploaded_files[selected_file]["original"]=st.session_state.uploaded_files[selected_file]["original"].iloc[:FREE_ROW_LIMIT]
        st.session_state.df_clean=st.session_state.uploaded_files[selected_file]["clean"]
        st.session_state.df_original=st.session_state.uploaded_files[selected_file]["original"]
        st.session_state.orig_len=len(st.session_state.df_original)
        st.session_state.empty_fixed=st.session_state.uploaded_files[selected_file]["empty_fixed"]
        st.session_state.problem_cells=st.session_state.uploaded_files[selected_file].get("problem_cells",set())
        update_changed_cells(); st.session_state.df_loaded=True
        df_clean=st.session_state.df_clean; orig_len=st.session_state.orig_len
        st.markdown(f"<h2>{T['summary_title']}</h2>", unsafe_allow_html=True)
        if st.button("🔄 Reset Active Dataset to Original Raw State", type="secondary", use_container_width=True):
            if st.session_state.df_original is not None:
                st.session_state.df_clean=st.session_state.df_original.copy(); st.session_state.changed_cells=set(); st.session_state.problem_cells=set()
                st.session_state["reset_announced"]=True; st.session_state["last_apply_msg"]=None; st.session_state["hub_report"]=None; st.session_state["clean_done"]=False
                st.session_state.uploaded_files[selected_file]["clean"]=st.session_state.df_clean
                st.session_state.uploaded_files[selected_file]["changed_cells"]=set(); st.session_state.uploaded_files[selected_file]["problem_cells"]=set(); st.rerun()
        c1,c2,c3,c4=st.columns(4)
        with c1: st.metric(T['rows'], orig_len)
        with c2: st.metric(T['clean'], len(df_clean))
        with c3: st.metric(T['dups'], max(0, orig_len-len(df_clean)))
        with c4: st.metric(T['empty'], st.session_state.empty_fixed)
        st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
        st.caption(T['preview'])
        styled_df=apply_cell_styling(df_clean.head(10))
        st.dataframe(styled_df, use_container_width=True, height=280)
        if st.session_state.get("reset_announced"):
            st.success("🔄 Success: Your original raw dataset states have been completely reset!"); st.session_state["reset_announced"]=False
        db_data=load_db(); user_info=db_data.get(st.session_state.email,{}); is_paid=user_info.get("status")=="PAID"
        
        # ONLY ONE BIG CLICK AND FIX - HIDING INDIVIDUAL TOOLS AS YOU ASKED
        st.markdown("<div style='background: #faf5ff; padding:20px; border-radius:18px; border:3px dashed #a855f7; margin-bottom:15px; text-align:center;'>", unsafe_allow_html=True)
        st.markdown("### 🧹 ONE CLICK = 10 TOOLS CLEAN EVERYTHING")
        st.write("No need to select columns or tools. Just click below - all 10 tools will auto clean your entire file. Free = 15 sec, Pro = 3 sec.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🧹 BIG CLEAN - Fix & Clean Everything (1 Click)", key="global_apply_btn", type="primary", use_container_width=True):
            enforce_processing_delay()
            df_curr=st.session_state.df_clean.copy()
            st.session_state.problem_cells=set(); hub_report=[]
            for col in df_curr.columns:
                if df_curr[col].dtype != 'object': df_curr[col]=df_curr[col].astype(object)
            orig_rows_count=len(df_curr)
            for col in df_curr.select_dtypes(include=['object']).columns:
                df_curr=remove_fuzzy_duplicates(df_curr, col)
            dups_merged=orig_rows_count-len(df_curr)
            hub_report.append(f"🧠 **Fuzzy Deduplication (Tool 8):** {'Merged '+str(dups_merged)+' duplicate rows 🔴' if dups_merged else 'OK (Already Clean) 🟢'}")
            date_changed=0
            for col in df_curr.columns:
                for r_idx in range(len(df_curr)):
                    val=df_curr.at[r_idx,col]; parsed=intelligent_date_parser(val)
                    if parsed and str(val)!=str(parsed) and parsed!="None":
                        df_curr.at[r_idx,col]=parsed; date_changed+=1; st.session_state.problem_cells.add((r_idx,col))
            hub_report.append(f"📅 **Smart Date Converter (Tool 1):** {'Fixed '+str(date_changed)+' messy date formats 🔴' if date_changed else 'OK (Already Clean) 🟢'}")
            null_fixed=0
            for col in df_curr.columns:
                sample=str(df_curr[col].dropna().iloc[0]).lower() if not df_curr[col].dropna().empty else ""
                if any(k in col.lower() for k in ['salary','amount','price','paisa']): fill_val=0
                elif '@' in sample or 'email' in col.lower(): fill_val="missing@email.com"
                else: fill_val="Unknown"
                df_curr[col]=df_curr[col].astype(object)
                for r_idx in range(len(df_curr)):
                    val=df_curr.at[r_idx,col]
                    if pd.isna(val) or str(val).strip().lower() in ["nan","none","","null","n/a",""]:
                        df_curr.at[r_idx,col]=fill_val; null_fixed+=1; st.session_state.problem_cells.add((r_idx,col))
            hub_report.append(f"🛠️ **AI Fill Nulls (Tool 2):** {'Fixed '+str(null_fixed)+' missing values 🔴' if null_fixed else 'OK (Already Clean) 🟢'}")
            email_fixed=0; pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            for col in df_curr.columns:
                if 'email' in col.lower() or df_curr[col].astype(str).str.contains('@').any():
                    for r_idx in range(len(df_curr)):
                        val=str(df_curr.at[r_idx,col]).lower().strip()
                        cleaned=val.replace("gmai.com","gmail.com").replace("yaho.com","yahoo.com").replace("outlok.com","outlook.com").replace("hotmial.com","hotmail.com")
                        valid_val=cleaned if re.match(pattern, cleaned) else "Invalid Email"
                        if str(df_curr.at[r_idx,col])!=valid_val:
                            df_curr.at[r_idx,col]=valid_val; email_fixed+=1; st.session_state.problem_cells.add((r_idx,col))
            hub_report.append(f"✉️ **Email Validator (Tool 3):** {'Fixed '+str(email_fixed)+' email errors/typos 🔴' if email_fixed else 'OK (Already Clean) 🟢'}")
            phone_fixed=0
            for col in df_curr.columns:
                if any(k in col.lower() for k in ['phone','mobile','contact']):
                    for r_idx in range(len(df_curr)):
                        val=str(df_curr.at[r_idx,col]); digits="".join(re.findall(r'\d+', val)); formatted=digits[-10:] if len(digits)>=10 else digits
                        if val!=formatted: df_curr.at[r_idx,col]=formatted; phone_fixed+=1; st.session_state.problem_cells.add((r_idx,col))
            hub_report.append(f"📞 **Phone Formatter (Tool 4):** {'Cleaned '+str(phone_fixed)+' phone numbers 🔴' if phone_fixed else 'OK (Already Clean) 🟢'}")
            case_fixed=0
            for col in df_curr.select_dtypes(include=['object']).columns:
                for r_idx in range(len(df_curr)):
                    val=str(df_curr.at[r_idx,col]); titled=val.title()
                    if val!=titled: df_curr.at[r_idx,col]=titled; case_fixed+=1; st.session_state.changed_cells.add((r_idx,col))
            hub_report.append(f"🔤 **Case Converter (Tool 5):** {'Standardized '+str(case_fixed)+' text cases 🟢' if case_fixed else 'OK (Already Clean) 🟢'}")
            symbols_fixed=0
            for col in df_curr.select_dtypes(include=['object']).columns:
                for r_idx in range(len(df_curr)):
                    val=str(df_curr.at[r_idx,col]); stripped=re.sub(r'[^a-zA-Z0-9\s.,₹$€£¥@\-+]', '', val)
                    if val!=stripped: df_curr.at[r_idx,col]=stripped; symbols_fixed+=1; st.session_state.problem_cells.add((r_idx,col))
            hub_report.append(f"🔣 **Remove Symbols (Tool 6):** {'Stripped symbols from '+str(symbols_fixed)+' cells 🔴' if symbols_fixed else 'OK (Already Clean) 🟢'}")
            new_cols={c: re.sub(r'[^a-zA-Z0-9_]', '', c.strip().lower().replace(' ', '_')) for c in df_curr.columns}
            headers_changed=sum(1 for k,v in new_cols.items() if k!=v); df_curr.rename(columns=new_cols, inplace=True)
            hub_report.append(f"✏️ **Header Clean (Tool 7):** {'Standardized '+str(headers_changed)+' headers 🟢' if headers_changed else 'OK (Already Clean) 🟢'}")
            spaces_fixed=0
            for col in df_curr.select_dtypes(include=['object']).columns:
                for r_idx in range(len(df_curr)):
                    val=str(df_curr.at[r_idx,col]); trimmed=re.sub(r'\s+', ' ', val.strip())
                    if val!=trimmed: df_curr.at[r_idx,col]=trimmed; spaces_fixed+=1; st.session_state.changed_cells.add((r_idx,col))
            hub_report.append(f"✂️ **Trim Spaces (Tool 9):** {'Trimmed excess whitespace in '+str(spaces_fixed)+' cells 🟢' if spaces_fixed else 'OK (Already Clean) 🟢'}")
            typo_dict={"teh":"the","recieve":"receive","goverment":"government","salery":"salary","amout":"amount","custmer":"customer","addres":"address","manger":"manager","dept":"department","org":"organization"}
            spell_fixed=0
            for col in df_curr.select_dtypes(include=['object']).columns:
                for r_idx in range(len(df_curr)):
                    val=str(df_curr.at[r_idx,col]); words=val.split(); fixed_words=[typo_dict.get(w.lower(), w) for w in words]; corrected=" ".join(fixed_words)
                    if val.lower()!=corrected.lower(): df_curr.at[r_idx,col]=corrected.title(); spell_fixed+=1; st.session_state.problem_cells.add((r_idx,col))
            hub_report.append(f"🔠 **Spell Check (Tool 10):** {'Corrected '+str(spell_fixed)+' typos 🔴' if spell_fixed else 'OK (Already Clean) 🟢'}")
            st.session_state.df_clean=df_curr; update_changed_cells(); st.session_state["hub_report"]=hub_report; st.session_state["clean_done"]=True
            st.session_state.uploaded_files[selected_file]["clean"]=st.session_state.df_clean
            st.session_state.uploaded_files[selected_file]["changed_cells"]=st.session_state.changed_cells
            st.session_state.uploaded_files[selected_file]["problem_cells"]=st.session_state.problem_cells
            st.success("✅ Data Cleaned! All 10 tools finished! Your data is cleaned.")
            st.balloons()
            st.rerun()
            
        if st.session_state.get("hub_report"):
            st.markdown("#### 📋 What happened - Tool by Tool Report (All 10 Tools):")
            for report_line in st.session_state["hub_report"]: st.write(report_line)
            st.success("🎉 Your data is cleaned! See below for download after payment.")
        st.markdown("</div>", unsafe_allow_html=True)

        # EXPORT & PAYMENT
        st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
        if st.session_state.plan=="free":
            if st.session_state.get("clean_done"):
                st.info("Free preview: Download limited. Pay ₹299 to unlock unlimited + Excel + PDF")
                csv=st.session_state.df_clean.to_csv(index=False).encode()
                col_dl1, col_dl2 = st.columns([1,1])
                with col_dl1:
                    if st.download_button(T['download_csv'], csv, f"verisame_free_{selected_file}.csv", mime="text/csv", key="dl_csv_free_btn", use_container_width=True):
                        st.balloons()
                with col_dl2:
                    if st.button("← Back", key="back_after_clean_free"):
                        st.session_state["clean_done"]=False; st.rerun()
            else:
                st.warning("Upload file and press BIG CLEAN button - 1 click = 10 tools")
        elif st.session_state.plan=="pro":
            if not is_paid:
                st.warning(T['paid_msg'])
                default_amt_index=0 if st.session_state.amt==PRO_1M else 1
                selected_pay_plan=st.radio("Choose Payment Duration Tier:", ["₹299 - 1 Month / 30 Days","₹1499 - 6 Months / 180 Days"], index=default_amt_index, horizontal=True, key="radio_pay_plan")
                pay_amt=PRO_1M if "299" in selected_pay_plan else PRO_6M; st.session_state.amt=pay_amt
                upi_pay_link=f"upi://pay?pa={UPI_ID}&pn=Reyansh&am={pay_amt}&cu=INR&tn=VeriSame{pay_amt}"
                st.link_button(f"💸 Pay ₹{pay_amt} directly via UPI App", upi_pay_link, use_container_width=True); display_upi_qr(upi_pay_link, pay_amt)
                c_pay1, c_pay2 = st.columns(2)
                with c_pay1:
                    if st.button(T['paid_btn'].format(amount=pay_amt), key="btn_paid", type="primary", use_container_width=True):
                        st.session_state.payment_clicked=True; data=load_db(); selected_days=180 if pay_amt==PRO_6M else 30
                        data[st.session_state.email]={"plan":"pro","amt":pay_amt,"days":selected_days,"expiry":(datetime.now()+timedelta(days=selected_days)).strftime("%Y-%m-%d"),"status":"PENDING"}
                        save_db(data); st.balloons(); st.info(T['wait_approval']); st.rerun()
                with c_pay2:
                    if st.button("← Back to Plans", key="back_from_pay"):
                        st.session_state.selected_plan=None; st.session_state.plan=None; st.rerun()
                if st.session_state.get("payment_clicked"): st.info(T['wait_approval'])
            else:
                st.success("🎉 Download Ready! Pro Active")
                st.balloons()
                col1,col2,col3=st.columns(3)
                csv=st.session_state.df_clean.to_csv(index=False).encode()
                col1.download_button(T['download_csv'], csv, f"verisame_pro_{selected_file}.csv", mime="text/csv", key="dl_csv_paid", use_container_width=True)
                if openpyxl is not None:
                    excel=io.BytesIO(); st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl'); excel.seek(0)
                    col2.download_button(T['download_excel'], excel.getvalue(), f"verisame_pro_{selected_file}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_paid", use_container_width=True)
                pdf_data=generate_pdf_report(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean)
                if pdf_data: col3.download_button("Download Audit PDF Report 📊", pdf_data, f"verisame_audit_{selected_file}.pdf", mime="application/pdf", key="dl_pdf_paid", use_container_width=True)
                # Balloons again logic
                if col1 or col2 or col3:
                    st.markdown("Balloon will show on download click 🎈")
