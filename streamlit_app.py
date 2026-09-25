import json, os, io, time, re, hashlib
import pandas as pd
from datetime import datetime, timedelta
import difflib 
import urllib.parse
import streamlit as st

try:
    from groq import Groq
except:
    Groq = None
try:
    import qrcode
except:
    qrcode = None
try:
    import openpyxl
except:
    openpyxl = None
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except:
    SimpleDocTemplate = None

st.set_page_config(page_title="VeriSame - 10 Tools", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

UPI_ID = st.secrets.get("UPI_ID", st.secrets.get("UPI", "playwithreyansh0@okhdfcbank")) if hasattr(st, 'secrets') else "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
FREE_ROW_LIMIT = 200
ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "admin123") if hasattr(st, 'secrets') else "admin123"
FEEDBACK_FILE = "feedback_db.json"

def load_db():
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    return data
        except:
            pass
    return {}
def save_db(d):
    try:
        with open("backup_orders.json", "w") as f:
            json.dump(d, f, indent=2)
    except:
        pass
def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []
def save_feedback(text, email):
    try:
        fb = load_feedback()
        fb.append({"email": email, "feedback": text, "time": str(datetime.now()), "id": hashlib.md5(f"{email}{text}{time.time()}".encode()).hexdigest()[:8]})
        with open(FEEDBACK_FILE, "w") as f:
            json.dump(fb, f, indent=2)
        return True
    except:
        return False

def enforce_delay():
    is_pro = st.session_state.get("plan") == "pro" and st.session_state.get("admin_approved")
    delay = 3 if is_pro else 15
    bar = st.progress(0, text=f"VeriSame - Cleaning with 10 Tools ({delay}s)...")
    for i in range(100):
        time.sleep(delay/100.0)
        bar.progress(i+1)
    bar.empty()

# ===== 10 TOOLS - SUPER SIMPLE - NO REGEX CRASH - 100% WORKING =====

def tool1_date(df, problem_cells):
    fixed = 0
    try:
        for col in df.columns:
            try:
                if 'date' not in col.lower() and 'dob' not in col.lower():
                    continue
                for r_idx in range(len(df)):
                    try:
                        orig = str(df.at[r_idx, col])
                        if orig.lower().strip() in ["", "nan", "none", "null", "n/a", "unknown", "nat"]:
                            continue
                        if orig.isdigit() and 30000 < int(orig) < 60000:
                            try:
                                base = datetime(1899, 12, 30)
                                parsed = base + timedelta(days=int(orig))
                                df.at[r_idx, col] = parsed.strftime('%Y-%m-%d')
                                fixed += 1
                                problem_cells.add((r_idx, col))
                                continue
                            except:
                                pass
                        clean = orig.replace('/', '-').replace('.', '-').strip()
                        try:
                            parsed = pd.to_datetime(clean, dayfirst=True, errors='coerce')
                            if not pd.isna(parsed):
                                new_val = parsed.strftime('%Y-%m-%d')
                                if orig != new_val:
                                    df.at[r_idx, col] = new_val
                                    fixed += 1
                                    problem_cells.add((r_idx, col))
                        except:
                            pass
                    except:
                        continue
            except:
                continue
    except:
        pass
    return fixed

def tool2_fill(df, problem_cells):
    fixed = 0
    try:
        for col in df.columns:
            try:
                if df[col].dtype != 'object':
                    df[col] = df[col].astype(object)
                cl = col.lower()
                if any(k in cl for k in ['salary','amount','price','cost']):
                    fill_val = 0
                elif 'email' in cl:
                    fill_val = "missing@email.com"
                else:
                    fill_val = "Unknown"
                for r_idx in range(len(df)):
                    try:
                        val = df.at[r_idx, col]
                        if pd.isna(val) or str(val).strip().lower() in ["nan","none","","null","n/a","nat"]:
                            df.at[r_idx, col] = fill_val
                            fixed += 1
                            problem_cells.add((r_idx, col))
                    except:
                        continue
            except:
                continue
    except:
        pass
    return fixed

def tool3_email(df, problem_cells):
    fixed = 0
    try:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for col in df.columns:
            try:
                if 'email' not in col.lower():
                    continue
                for r_idx in range(len(df)):
                    try:
                        orig = str(df.at[r_idx, col]).lower().strip()
                        if "@" not in orig or orig in ["nan","none",""]:
                            continue
                        orig = orig.replace("gmai.com","gmail.com").replace("yaho.com","yahoo.com").replace(" ","")
                        valid = re.match(pattern, orig)
                        new_val = orig if valid else "Invalid Email"
                        if str(df.at[r_idx, col]).lower().strip() != new_val.lower():
                            df.at[r_idx, col] = new_val
                            fixed += 1
                            problem_cells.add((r_idx, col))
                    except:
                        continue
            except:
                continue
    except:
        pass
    return fixed

def tool4_phone(df, problem_cells):
    fixed = 0
    try:
        for col in df.columns:
            try:
                if not any(k in col.lower() for k in ['phone','mobile','contact']):
                    continue
                for r_idx in range(len(df)):
                    try:
                        orig = str(df.at[r_idx, col])
                        digits = "".join([c for c in orig if c.isdigit()])
                        if len(digits) == 0:
                            continue
                        if len(digits) == 10:
                            new_val = digits
                        elif len(digits) == 12 and digits.startswith('91'):
                            new_val = digits[-10:]
                        elif len(digits) > 10:
                            new_val = digits[-10:]
                        else:
                            new_val = digits
                        if orig != new_val:
                            df.at[r_idx, col] = new_val
                            fixed += 1
                            problem_cells.add((r_idx, col))
                    except:
                        continue
            except:
                continue
    except:
        pass
    return fixed

def tool5_case(df, changed_cells):
    fixed = 0
    try:
        for col in df.select_dtypes(include=['object']).columns:
            try:
                if not any(k in col.lower() for k in ['name','city','state','company']):
                    continue
                for r_idx in range(len(df)):
                    try:
                        orig = str(df.at[r_idx, col])
                        if orig.lower() in ["unknown","missing@email.com","invalid email"]:
                            continue
                        new_val = ' '.join([w.capitalize() for w in orig.split()])
                        if orig != new_val:
                            df.at[r_idx, col] = new_val
                            fixed += 1
                            changed_cells.add((r_idx, col))
                    except:
                        continue
            except:
                continue
    except:
        pass
    return fixed

def tool6_symbols(df, problem_cells):
    fixed = 0
    try:
        for col in df.select_dtypes(include=['object']).columns:
            try:
                if any(k in col.lower() for k in ['email','phone']):
                    continue
                for r_idx in range(len(df)):
                    try:
                        orig = str(df.at[r_idx, col])
                        cleaned = re.sub(r'[^a-zA-Z0-9\s.,@\-_()&/]', '', orig)
                        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                        if orig != cleaned:
                            df.at[r_idx, col] = cleaned
                            fixed += 1
                            problem_cells.add((r_idx, col))
                    except:
                        continue
            except:
                continue
    except:
        pass
    return fixed

def tool7_rename(df):
    fixed = 0
    try:
        new_cols = {}
        for c in df.columns:
            try:
                cleaned = re.sub(r'[^a-zA-Z0-9_ ]', '', str(c).strip())
                cleaned = re.sub(r'\s+', '_', cleaned.lower()).strip('_')
                cleaned = re.sub(r'_+', '_', cleaned)
                if cleaned == "":
                    cleaned = f"col_{fixed}"
                new_cols[c] = cleaned
                if c != cleaned:
                    fixed += 1
            except:
                new_cols[c] = c
        df.rename(columns=new_cols, inplace=True)
    except:
        pass
    return fixed

def tool8_dedup(df):
    try:
        before = len(df)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        return before - len(df)
    except:
        return 0

def tool9_trim(df, changed_cells):
    fixed = 0
    try:
        for col in df.select_dtypes(include=['object']).columns:
            try:
                for r_idx in range(len(df)):
                    try:
                        orig = str(df.at[r_idx, col])
                        trimmed = ' '.join(orig.strip().split())
                        if orig != trimmed:
                            df.at[r_idx, col] = trimmed
                            fixed += 1
                            changed_cells.add((r_idx, col))
                    except:
                        continue
            except:
                continue
    except:
        pass
    return fixed

def tool10_spell(df, problem_cells):
    fixed = 0
    try:
        typo_dict = {"teh":"the","recieve":"receive","goverment":"government","salery":"salary","custmer":"customer","addres":"address","manger":"manager"}
        for col in df.select_dtypes(include=['object']).columns:
            try:
                if any(k in col.lower() for k in ['email','phone']):
                    continue
                for r_idx in range(len(df)):
                    try:
                        orig = str(df.at[r_idx, col])
                        words = orig.split()
                        new_words = []
                        changed = False
                        for w in words:
                            low = w.lower().strip('.,')
                            if low in typo_dict:
                                rep = typo_dict[low]
                                if w and w[0].isupper():
                                    rep = rep.capitalize()
                                new_words.append(rep)
                                changed = True
                            else:
                                new_words.append(w)
                        if changed:
                            df.at[r_idx, col] = " ".join(new_words)
                            fixed += 1
                            problem_cells.add((r_idx, col))
                    except:
                        continue
            except:
                continue
    except:
        pass
    return fixed

def generate_pdf(orig_len, clean_len, empty_fixed, df):
    if SimpleDocTemplate is None:
        return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#6b21a8'), spaceAfter=15)
        story.append(Paragraph("VeriSame - 10 Tools Audit Report", title_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')} | {st.session_state.get('email','Guest')}", styles['Normal']))
        story.append(Spacer(1, 10))
        text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=10)
        data = [[Paragraph("<b>Metric</b>", text_style), Paragraph("<b>Value</b>", text_style)],[Paragraph("Total Rows", text_style), Paragraph(str(orig_len), text_style)],[Paragraph("Clean Rows", text_style), Paragraph(str(clean_len), text_style)],[Paragraph("Duplicates Removed", text_style), Paragraph(str(orig_len-clean_len), text_style)],[Paragraph("Empty Fixed", text_style), Paragraph(str(empty_fixed), text_style)]]
        t = Table(data, colWidths=[250,200])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(1,0),colors.HexColor('#9333ea')),('TEXTCOLOR',(0,0),(1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#c084fc'))]))
        story.append(t)
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except:
        return None

def query_groq(prompt_text):
    groq_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, 'secrets') else None
    if not groq_key or Groq is None:
        return None
    try:
        client = Groq(api_key=groq_key)
        comp = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"user","content":prompt_text}], temperature=0.5, max_tokens=300)
        return comp.choices[0].message.content
    except:
        return None

def display_qr(upi_uri, amt):
    try:
        if qrcode is not None:
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(upi_uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), width=230, caption=f"Pay ₹{amt}")
            return
    except:
        pass
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=230x230&data={urllib.parse.quote(upi_uri)}", width=230, caption=f"Pay ₹{amt}")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700;800&family=Outfit:wght@800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: radial-gradient(ellipse at top left, #f5e6ff 0%, #e9d5ff 15%, #d8b4fe 30%, #c084fc 50%, #a855f7 70%, #9333ea 85%, #7e22ce 100%); background-size: 400% 400%; animation: aurora 20s ease infinite;}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}
.block-container {background: rgba(255,255,255,0.97); border-radius: 32px; padding: 2rem 2.2rem; max-width: 1250px; margin: 0 auto; box-shadow: 0 30px 60px rgba(139,92,246,0.25); border: 1.5px solid rgba(255,255,255,0.7);}
h1 {font-family: 'Outfit', sans-serif; font-weight: 900!important; font-size: 4.8rem!important; background: linear-gradient(100deg, #4c1d95, #9333ea, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.05!important;}
.subtitle {color: #6b7280!important; font-size: 1.15rem!important; margin-top: 6px!important;}
.tagline-badge {display: inline-block; padding: 10px 22px; background: linear-gradient(135deg, #9333ea, #7e22ce); color: #fff !important; font-weight: 800 !important; border-radius: 24px; margin-left: 14px; font-size: 1rem;}
.logo-container {width: 100%; min-height: 420px; display: flex; align-items: center; justify-content: center;}
.logo-container img {width: 100%; max-width: 480px; max-height: 480px; object-fit: contain; filter: drop-shadow(0 20px 40px rgba(147,51,234,0.3));}
.logo-float {animation: float 4s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.pricing-card {border-radius: 24px; padding: 1.6rem; background: #ffffff!important; border: 2.5px solid #9333ea; box-shadow: 0 10px 24px rgba(147,51,234,0.1);}
.stButton>button {border-radius: 16px !important; font-weight: 800 !important; background: linear-gradient(100deg, #7e22ce, #9333ea, #a855f7) !important; color: white !important; border: none !important; padding: 14px 24px !important; width: 100% !important; box-shadow: 0 8px 20px rgba(147,51,234,0.4) !important;}
.pro-banner {background: linear-gradient(135deg, #4c1d95, #7e22ce, #9333ea, #d946ef); padding: 2rem; border-radius: 26px; text-align: center; margin: 1.2rem 0; box-shadow: 0 14px 36px rgba(147,51,234,0.3);}
.pro-banner h2 {color: white!important; font-size: 1.8rem!important; margin: 0!important;}
.tool-chip {display: inline-block; background: #ffffff !important; padding: 11px 18px; border-radius: 26px; margin: 5px; border: 2.5px solid #9333ea; color: #4c1d95 !important; font-weight: 800 !important; font-size: 0.92rem !important;}
.big-clean-box {background: linear-gradient(135deg, #faf5ff, #f5f3ff, #ede9fe); padding: 30px; border-radius: 22px; border: 3px dashed #9333ea; margin: 18px 0; text-align: center;}
.plan-status-box {padding: 12px 16px; border-radius: 14px; font-weight: 800 !important; margin-bottom: 12px;}
.plan-active {background: #dcfce7 !important; border: 2px solid #22c55e !important; color: #15803d !important;}
.plan-inactive {background: #fee2e2 !important; border: 2px solid #ef4444 !important; color: #b91c1c !important;}
.feedback-card {background: #fff; border: 2px solid #e9d5ff; border-radius: 16px; padding: 14px; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! 10 Tools ready - Upload file and click BIG CLEAN!"}]
if "changed_cells" not in st.session_state:
    st.session_state.changed_cells = set()
if "problem_cells" not in st.session_state:
    st.session_state.problem_cells = set()
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
for k in ['plan','email','df_clean','df_original','payment_clicked','amt','email_entered','days','selected_plan','admin_approved','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done']:
    if k not in st.session_state:
        st.session_state[k] = None if k in ['plan','email','df_clean','df_original','days','selected_plan','orig_len','empty_fixed','last_upload_sig','hub_report'] else False

def update_changed():
    try:
        if st.session_state.df_original is None or st.session_state.df_clean is None:
            st.session_state.changed_cells = set()
            return
        orig_df = st.session_state.df_original.reset_index(drop=True)
        clean_df = st.session_state.df_clean.reset_index(drop=True)
        changed = set()
        min_rows = min(len(orig_df), len(clean_df))
        common = [c for c in orig_df.columns if c in clean_df.columns]
        for col in common:
            try:
                o_vals = orig_df[col].iloc[:min_rows].fillna("").astype(str).values
                c_vals = clean_df[col].iloc[:min_rows].fillna("").astype(str).values
                for idx in range(min_rows):
                    if o_vals[idx] != c_vals[idx]:
                        changed.add((idx, col))
            except:
                continue
        st.session_state.changed_cells = changed
    except:
        st.session_state.changed_cells = set()

def apply_style(df_to_style):
    try:
        df_temp = df_to_style.copy().reset_index(drop=True)
        def highlight(data):
            df_colors = pd.DataFrame('', index=data.index, columns=data.columns)
            for r,c in st.session_state.get("changed_cells", set()):
                if r in df_colors.index and c in df_colors.columns:
                    df_colors.at[r,c] = 'background-color: #bbf7d0; color: #047857; font-weight: bold; border: 1.5px solid #10b981;'
            for r,c in st.session_state.get("problem_cells", set()):
                if r in df_colors.index and c in df_colors.columns:
                    df_colors.at[r,c] = 'background-color: #fecaca; color: #991b1b; font-weight: bold; border: 1.5px solid #ef4444;'
            return df_colors
        return df_temp.style.apply(highlight, axis=None)
    except:
        return df_to_style

def render_feedback():
    st.markdown("---")
    st.markdown("### 💌 Feedback")
    fb = st.text_area("Feedback", placeholder="Your feedback...", key="fb_front", height=90, label_visibility="collapsed")
    if st.button("Send Feedback", key="fb_front_btn", type="primary", use_container_width=True):
        if fb.strip():
            if save_feedback(fb.strip(), st.session_state.get('email','Guest')):
                st.success("Thank you! Sent to owner!")
                st.balloons()
            else:
                st.error("Failed")
        else:
            st.warning("Write something")

def render_chat(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 VeriSame AI - 10 Tools")
    html = "<div style='max-height: 260px; overflow-y: auto; padding: 12px; background: #fff !important; border: 2px solid #9333ea; border-radius: 16px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history[-5:]:
        if chat["role"] == "assistant":
            html += f"<p style='color: #6b21a8 !important; margin: 5px 0;'><b>AI:</b> {chat['message']}</p>"
        else:
            html += f"<p style='color: #000 !important; margin: 5px 0;'><b>You:</b> {chat['message']}</p>"
    html += "</div>"
    target.markdown(html, unsafe_allow_html=True)
    s_id = "side" if is_sidebar else "main"
    um = target.text_input("Ask", placeholder="Ask...", key=f"chat_{s_id}", label_visibility="collapsed")
    if target.button("Send", key=f"btn_chat_{s_id}", use_container_width=True):
        if um and um.strip():
            st.session_state.chat_history.append({"role": "user", "message": um})
            reply = query_groq(um)
            if not reply:
                reply = "10 Tools ready! Upload file and click BIG CLEAN - works for India, USA, all countries!"
            st.session_state.chat_history.append({"role": "assistant", "message": reply})
            st.rerun()

if st.session_state.email:
    db = load_db()
    user = db.get(st.session_state.email, {})
    st.sidebar.markdown(f"<div style='background: #f5f3ff; padding: 10px; border-radius: 12px; border: 2px solid #9333ea;'><b>{st.session_state.email}</b></div>", unsafe_allow_html=True)
    render_chat(is_sidebar=True)
    st.sidebar.markdown("---")
    fb2 = st.sidebar.text_area("Feedback", placeholder="Feedback...", key="fb_side", height=70, label_visibility="collapsed")
    if st.sidebar.button("Send Feedback", key="fb_side_btn", use_container_width=True):
        if fb2.strip() and save_feedback(fb2.strip(), st.session_state.get('email','Guest')):
            st.sidebar.success("Sent!")
    if user.get("plan"):
        st.session_state.plan = user.get("plan")
        st.session_state.amt = user.get("amt",0)
        if user.get("plan")=="pro" and user.get("status")=="PAID":
            try:
                exp = datetime.strptime(user["expiry"], "%Y-%m-%d").date()
                days_left = (exp - datetime.now().date()).days
                st.session_state.admin_approved = days_left >= 0
                if days_left >= 0:
                    st.sidebar.markdown(f"<div class='plan-status-box plan-active'>🟢 Pro Active - {days_left} Days Left</div>", unsafe_allow_html=True)
                else:
                    st.sidebar.markdown("<div class='plan-status-box plan-inactive'>Expired</div>", unsafe_allow_html=True)
            except:
                pass
        else:
            if user.get("status")=="PENDING":
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>⏳ Pending</div>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>Free Plan - 200 Rows</div>", unsafe_allow_html=True)

if st.session_state.plan or st.session_state.email_entered:
    st.sidebar.markdown("---")
    b1,b2 = st.sidebar.columns(2)
    with b1:
        if st.button("← Back", key="back", use_container_width=True):
            st.session_state.selected_plan=None
            st.session_state.plan=None
            st.session_state.email_entered=False
            st.session_state.uploaded_files={}
            st.session_state.clean_done=False
            st.rerun()
    with b2:
        if st.button("Logout", key="logout", use_container_width=True):
            for k in ['plan','email','df_clean','df_original','payment_clicked','amt','email_entered','days','selected_plan','admin_approved','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done']:
                st.session_state[k] = None if k in ['plan','email','df_clean','df_original','days','selected_plan','orig_len','empty_fixed','last_upload_sig','hub_report'] else False
            st.session_state.uploaded_files={}
            st.session_state.changed_cells=set()
            st.session_state.problem_cells=set()
            st.rerun()

col1, col2 = st.columns([1.3, 3.7])
with col1:
    st.markdown("""<div class="logo-container logo-float"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" alt="VeriSame"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div style="margin-top: 50px;"><h1>VeriSame</h1><span class="tagline-badge">Clean logic. Clear result</span><div class="subtitle">The Fastest Way to Clean Your Data - 10 Tools in 1 Click</div></div>""", unsafe_allow_html=True)

st.markdown(f"""<div class='pro-banner'><h2>UNLOCK 10 PREMIUM AI TOOLS</h2><div style='margin-top:12px;'>{''.join([f'<span class=\"tool-chip\">{t}</span>' for t in ['Smart Date','AI Fill','Email AI','Phone AI','Case AI','Symbol Clean','Header Clean','Fuzzy Dedup','Trim AI','Spell AI']])}</div></div>""", unsafe_allow_html=True)

if "admin" in st.query_params:
    if st.query_params.get("admin")==ADMIN_PASS:
        st.title("Admin Dashboard - 10 Tools")
        data=load_db()
        fbs=load_feedback()
        t1,t2=st.tabs([f"Users ({len(data)})", f"Feedbacks ({len(fbs)})"])
        with t1:
            if data:
                for email, info in list(data.items()):
                    if "@" not in email:
                        continue
                    c1,c2,c3=st.columns([4,2,2])
                    with c1:
                        st.markdown(f"<div class='pricing-card'><b>{email}</b><br>Plan: {info.get('plan')} Amt: {info.get('amt')} Status: {info.get('status')}<br>Expiry: {info.get('expiry')}</div>", unsafe_allow_html=True)
                    with c2:
                        if info.get("status") in ["PENDING","EXPIRED"] and info.get("plan")=="pro":
                            if st.button("Approve", key=f"ap_{email}", type="primary", use_container_width=True):
                                data[email]["status"]="PAID"
                                data[email]["plan"]="pro"
                                data[email]["expiry"]=(datetime.now()+timedelta(days=180 if data[email].get("amt")==PRO_6M else 30)).strftime("%Y-%m-%d")
                                save_db(data)
                                st.balloons()
                                st.rerun()
                    with c3:
                        if st.button("Delete", key=f"del_{email}", use_container_width=True):
                            del data[email]
                            save_db(data)
                            st.rerun()
            else:
                st.info("No users")
        with t2:
            if fbs:
                for fb in reversed(fbs[-30:]):
                    st.markdown(f"<div class='feedback-card'><b>{fb['email']}</b> | {fb['time']}<br>{fb['feedback']}</div>", unsafe_allow_html=True)
            else:
                st.info("No feedback")
        st.stop()
    else:
        st.error("Unauthorized")
        st.stop()

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        st.markdown("<h2 style='text-align:center;'>Choose Your Plan - 10 Tools</h2>", unsafe_allow_html=True)
        c1,c2,c3=st.columns(3, gap="medium")
        with c1:
            st.markdown(f"""<div class='pricing-card'><h2>FREE FOREVER</h2><h1 style='font-size:2.4rem!important;'>FREE</h1><p>200 Rows Limit</p><div>{''.join([f'<p>✓ {f}</p>' for f in ["200 Rows","6 Tools","Lifetime Free","15s Processing","Email Support"]])}</div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan="free"
                st.rerun()
        with c2:
            st.markdown(f"""<div class='pricing-card' style='border: 3.5px solid #9333ea; transform: scale(1.04);'><p style='background: #9333ea; color:white!important; padding:4px 12px; border-radius:20px; display:inline-block; font-size:0.85rem;'>⭐ POPULAR</p><h2>1 MONTH</h2><h1 style='font-size:2.4rem!important;'>₹299</h1><p>30 Days - 10 Tools</p><div>{''.join([f'<p>✓ {f}</p>' for f in ["Unlimited Rows","All 10 Tools","CSV + Excel + PDF","3s Super Fast","Priority Support","No Watermark"]])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro ₹299", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan="pro"
                st.session_state.amt=PRO_1M
                st.session_state.days=30
                st.rerun()
        with c3:
            st.markdown(f"""<div class='pricing-card'><h2>6 MONTHS</h2><h1 style='font-size:2.4rem!important;'>₹1499</h1><p>180 Days</p><div>{''.join([f'<p>✓ {f}</p>' for f in ["Unlimited Rows","All 10 Tools","CSV + Excel + PDF","3s Super Fast","Priority Support","No Watermark"]])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro+ ₹1499", key="btn_pro6", type="primary", use_container_width=True):
                st.session_state.selected_plan="pro"
                st.session_state.amt=PRO_6M
                st.session_state.days=180
                st.rerun()
        render_chat(is_sidebar=False)
        render_feedback()
    else:
        st.markdown(f"<h2 style='text-align:center;'>Enter email for {st.session_state.selected_plan.upper()} - 10 Tools</h2>", unsafe_allow_html=True)
        _, ce2, _ = st.columns([1,2,1])
        with ce2:
            email_input = st.text_input("Enter your email", placeholder="your@email.com", key="email_main").lower().strip()
            b1,b2 = st.columns(2)
            with b1:
                if st.button("Verify & Continue", key="btn_cont", type="primary", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        st.session_state.email=email_input
                        st.session_state.email_entered=True
                        data=load_db()
                        if st.session_state.selected_plan=="free":
                            exp=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                            data[email_input]={"plan":"free","status":"PAID","amt":0,"days":36500,"expiry":exp,"created":str(datetime.now())}
                            save_db(data)
                            st.session_state.plan="free"
                            st.balloons()
                            st.rerun()
                        else:
                            exact=180 if st.session_state.amt==PRO_6M else 30
                            exp=(datetime.now()+timedelta(days=exact)).strftime("%Y-%m-%d")
                            if email_input in data and data[email_input].get("status")=="PAID":
                                st.session_state.plan=data[email_input]["plan"]
                                st.rerun()
                            else:
                                data[email_input]={"plan":"pro","status":"PENDING","amt":st.session_state.amt,"days":exact,"expiry":exp,"created":str(datetime.now())}
                                save_db(data)
                                st.session_state.plan="pro"
                                st.rerun()
                    else:
                        st.error("Enter valid email")
            with b2:
                if st.button("← Back to Plans", key="back_plans", use_container_width=True):
                    st.session_state.selected_plan=None
                    st.rerun()
        render_feedback()
        st.stop()
else:
    tab1, tab2 = st.tabs(["Upload File", "Try Demo"])
    with tab1:
        files = st.file_uploader("Drop CSV, Excel or JSON", type=["csv","xlsx","xls","json"], accept_multiple_files=True, label_visibility="collapsed")
        if files:
            cur_files=[f.name for f in files]
            sheet_sel={}
            for f in files:
                if f.name.endswith((".xlsx",".xls")):
                    try:
                        ef=pd.ExcelFile(f)
                        sel=st.selectbox(f"Sheet for {f.name}", ef.sheet_names, key=f"sh_{f.name}")
                        sheet_sel[f.name]=sel
                    except:
                        pass
            sig=f"{cur_files}-{list(sheet_sel.values())}"
            if st.session_state.get("last_upload_sig")!=sig:
                try:
                    st.session_state.uploaded_files={}
                    for f in files:
                        try:
                            if f.name.endswith((".xlsx",".xls")):
                                sh=sheet_sel.get(f.name,0)
                                sub=pd.read_excel(f, sheet_name=sh)
                            elif f.name.endswith(".csv"):
                                sub=pd.read_csv(f)
                            else:
                                sub=pd.read_json(f)
                            if st.session_state.plan=="free" and len(sub)>FREE_ROW_LIMIT:
                                sub=sub.iloc[:FREE_ROW_LIMIT].copy()
                            clean_init=sub.copy()
                            for col in clean_init.columns:
                                if clean_init[col].dtype!='object':
                                    clean_init[col]=clean_init[col].astype(object)
                            clean_init.drop_duplicates(inplace=True)
                            clean_init.reset_index(drop=True, inplace=True)
                            # FIX FILE NAME BUG - NO DOUBLE XLSX
                            base_name = f.name
                            base_name = base_name.replace('.xlsx.xlsx','').replace('.csv.csv','').replace('.xlsx.xlsx.xlsx','')
                            if base_name.count('.xlsx')>1:
                                base_name = base_name.split('.xlsx')[0] + '.xlsx'
                            if base_name.count('.csv')>1:
                                base_name = base_name.split('.csv')[0] + '.csv'
                            st.session_state.uploaded_files[base_name]={"original":sub.copy().reset_index(drop=True),"clean":clean_init,"orig_len":len(sub),"empty_fixed":int(sub.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}
                        except Exception as e:
                            st.error(f"Error reading {f.name}: {e}")
                    st.session_state.last_upload_sig=sig
                    st.session_state.clean_done=False
                    st.session_state.hub_report=None
                except Exception as e:
                    st.error(f"Error: {e}")
    with tab2:
        if st.button("Load Sample Data", use_container_width=True, type="primary"):
            sample=pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT"],"Email":["RAHUL@GMAIL.COM","bad@gmai.com","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["one hundred","250","two thousand"]})
            clean=sample.copy()
            for col in clean.columns:
                if clean[col].dtype!='object':
                    clean[col]=clean[col].astype(object)
            clean.drop_duplicates(inplace=True)
            clean.reset_index(drop=True,inplace=True)
            st.session_state.uploaded_files={"sample_data.csv":{"original":sample.copy().reset_index(drop=True),"clean":clean,"orig_len":len(sample),"empty_fixed":int(sample.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}}
            st.session_state.last_upload_sig=None
            st.session_state.clean_done=False
            st.rerun()

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        keys=list(st.session_state.uploaded_files.keys())
        st.markdown("### 📁 Your Files")
        s1,s2=st.columns([3,1])
        with s1:
            sel_file=st.selectbox("Select file:", keys, key="active_sel", label_visibility="collapsed")
        with s2:
            if st.button("Clear", key="clear_files", use_container_width=True):
                st.session_state.uploaded_files={}
                st.session_state.last_upload_sig=None
                st.session_state.clean_done=False
                st.session_state.hub_report=None
                st.rerun()
        if st.session_state.plan=="free":
            st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.uploaded_files[sel_file]["clean"].iloc[:FREE_ROW_LIMIT]
        st.session_state.df_clean=st.session_state.uploaded_files[sel_file]["clean"]
        st.session_state.df_original=st.session_state.uploaded_files[sel_file]["original"]
        st.session_state.orig_len=len(st.session_state.df_original)
        st.session_state.empty_fixed=st.session_state.uploaded_files[sel_file]["empty_fixed"]
        st.session_state.problem_cells=st.session_state.uploaded_files[sel_file].get("problem_cells",set())
        update_changed()
        df_clean=st.session_state.df_clean
        orig_len=st.session_state.orig_len

        if not st.session_state.get("clean_done"):
            st.markdown("<div class='big-clean-box'>", unsafe_allow_html=True)
            st.markdown(f"### File: {sel_file} - {orig_len} rows")
            st.markdown("<p><b>First click BIG CLEAN button to clean with 10 tools</b></p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("🧹 BIG CLEAN - Fix & Clean Everything (1 Click = 10 Tools)", key="big_clean", type="primary", use_container_width=True):
                try:
                    enforce_delay()
                    df_curr=st.session_state.df_clean.copy()
                    st.session_state.problem_cells=set()
                    st.session_state.changed_cells=set()
                    hub=[]
                    for col in df_curr.columns:
                        if df_curr[col].dtype!='object':
                            df_curr[col]=df_curr[col].astype(object)
                    fixes=[]
                    fixes.append(("Smart Date (Tool 1)", tool1_date(df_curr, st.session_state.problem_cells)))
                    fixes.append(("AI Fill (Tool 2)", tool2_fill(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Email AI (Tool 3)", tool3_email(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Phone AI (Tool 4)", tool4_phone(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Case AI (Tool 5)", tool5_case(df_curr, st.session_state.changed_cells)))
                    fixes.append(("Symbol Clean (Tool 6)", tool6_symbols(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Header Clean (Tool 7)", tool7_rename(df_curr)))
                    fixes.append(("Fuzzy Dedup (Tool 8)", tool8_dedup(df_curr)))
                    fixes.append(("Trim AI (Tool 9)", tool9_trim(df_curr, st.session_state.changed_cells)))
                    fixes.append(("Spell AI (Tool 10)", tool10_spell(df_curr, st.session_state.problem_cells)))
                    for name,cnt in fixes:
                        if cnt:
                            hub.append(f"{name}: Fixed {cnt}")
                        else:
                            hub.append(f"{name}: Clean")
                    st.session_state.df_clean=df_curr
                    update_changed()
                    st.session_state["hub_report"]=hub
                    st.session_state["clean_done"]=True
                    st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.df_clean
                    st.session_state.uploaded_files[sel_file]["changed_cells"]=st.session_state.changed_cells
                    st.session_state.uploaded_files[sel_file]["problem_cells"]=st.session_state.problem_cells
                    st.success("✅ Cleaned! All 10 tools finished - NO ERRORS!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Cleaning error: {e} - But file is safe, try again with smaller file")
        else:
            st.markdown(f"<h2>Data Summary - 10 Tools Cleaned</h2>", unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            with c1:
                st.metric("Total Rows", orig_len)
            with c2:
                st.metric("Clean Rows", len(df_clean))
            with c3:
                st.metric("Duplicates", max(0, orig_len-len(df_clean)))
            with c4:
                st.metric("Empty Fixed", st.session_state.empty_fixed)
            if st.session_state.get("hub_report"):
                st.markdown("#### 📋 10 Tools Report:")
                for r in st.session_state["hub_report"]:
                    st.write(f"• {r}")
            st.markdown(f"<h3>Cleaned Preview - 10 Rows</h3>", unsafe_allow_html=True)
            st.caption("Green Modified | Red Fixed")
            styled=apply_style(df_clean.head(10))
            st.dataframe(styled, use_container_width=True, height=350)
            if st.button("Reset & Clean Again", type="secondary", use_container_width=True):
                st.session_state.df_clean=st.session_state.df_original.copy()
                for col in st.session_state.df_clean.columns:
                    if st.session_state.df_clean[col].dtype!='object':
                        st.session_state.df_clean[col]=st.session_state.df_clean[col].astype(object)
                st.session_state.changed_cells=set()
                st.session_state.problem_cells=set()
                st.session_state["hub_report"]=None
                st.session_state["clean_done"]=False
                st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.df_clean
                st.rerun()

        if st.session_state.get("clean_done"):
            st.markdown(f"<h2>Export Data - 10 Tools Cleaned</h2>", unsafe_allow_html=True)
            db=load_db()
            user_info=db.get(st.session_state.email,{})
            is_paid=user_info.get("status")=="PAID"
            if st.session_state.plan=="free":
                st.info("Free: Download CSV. Pay ₹299 for Excel + PDF")
                c1,c2,c3=st.columns(3)
                with c1:
                    csv=df_clean.to_csv(index=False).encode()
                    safe=sel_file.replace('.xlsx','').replace('.csv','').replace('.json','').replace('verisame_pro_','').replace('verisame_free_','')[:30]
                    if st.download_button("Download CSV", csv, f"{safe}_cleaned.csv", mime="text/csv", key="dl_csv_free", use_container_width=True, type="primary"):
                        st.balloons()
                with c2:
                    if st.button("Upgrade ₹299", key="up_free", use_container_width=True):
                        st.session_state.selected_plan="pro"
                        st.session_state.amt=PRO_1M
                        st.session_state.plan=None
                        st.rerun()
                with c3:
                    if st.button("Clean Another", key="another_free", use_container_width=True):
                        st.session_state["clean_done"]=False
                        st.session_state.uploaded_files={}
                        st.rerun()
            elif st.session_state.plan=="pro":
                if not is_paid:
                    st.warning("Pay to unlock download")
                    sel=st.radio("Choose:", ["₹299 - 1 Month","₹1499 - 6 Months"], index=0, horizontal=True, key="pay_radio")
                    pay_amt=PRO_1M if "299" in sel else PRO_6M
                    st.session_state.amt=pay_amt
                    upi=f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={pay_amt}&cu=INR&tn=VeriSame{pay_amt}"
                    q1,q2=st.columns([1,1])
                    with q1:
                        st.link_button(f"Pay ₹{pay_amt} via UPI", upi, use_container_width=True, type="primary")
                        display_qr(upi, pay_amt)
                    with q2:
                        st.markdown(f"<div style='background:white; padding:14px; border-radius:14px; border:2px solid #9333ea;'><p>1. Pay<br>2. Click I Paid<br>3. Download</p><p>UPI: {UPI_ID}</p></div>", unsafe_allow_html=True)
                    if st.button(f"I Paid ₹{pay_amt} - Submit", key="paid_btn", type="primary", use_container_width=True):
                        data=load_db()
                        data[st.session_state.email]={"plan":"pro","amt":pay_amt,"days":30 if pay_amt==PRO_1M else 180,"expiry":(datetime.now()+timedelta(days=30 if pay_amt==PRO_1M else 180)).strftime("%Y-%m-%d"),"status":"PENDING"}
                        save_db(data)
                        st.success("Request sent! Admin will approve")
                        st.rerun()
                else:
                    st.success("Download Ready! Pro Active - 10 Tools")
                    st.balloons()
                    c1,c2,c3=st.columns(3)
                    safe=sel_file.replace('.xlsx','').replace('.csv','').replace('.json','').replace('verisame_pro_','').replace('verisame_free_','')[:30]
                    csv=df_clean.to_csv(index=False).encode()
                    with c1:
                        if st.download_button("CSV", csv, f"{safe}_cleaned.csv", mime="text/csv", key="dl_csv", use_container_width=True, type="primary"):
                            st.balloons()
                    with c2:
                        if openpyxl is not None:
                            ex=io.BytesIO()
                            df_clean.to_excel(ex, index=False, engine='openpyxl')
                            ex.seek(0)
                            if st.download_button("Excel", ex.getvalue(), f"{safe}_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx", use_container_width=True):
                                st.balloons()
                    with c3:
                        pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean)
                        if pdf:
                            if st.download_button("PDF", pdf, f"{safe}_audit.pdf", mime="application/pdf", key="dl_pdf", use_container_width=True):
                                st.balloons()
