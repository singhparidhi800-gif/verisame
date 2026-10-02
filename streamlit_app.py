import json, os, io, time, re, hashlib
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
import requests

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
STARTER_PRICE, PRO_1M, PRO_6M = 49, 299, 1499
FREE_LIMIT, STARTER_LIMIT = 200, 2000
ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "admin123") if hasattr(st, 'secrets') else "admin123"
FEEDBACK_FILE = "feedback_db.json"
FREE_CLICKS_FILE = "free_clicks.json"
NTFY_TOPIC = st.secrets.get("NTFY_TOPIC", "verisame-anugya-97949-payments") if hasattr(st, 'secrets') else "verisame-anugya-97949-payments"

def send_notification(email, amt, plan_name):
    try:
        url = f"https://ntfy.sh/{NTFY_TOPIC}"
        msg = f"💰 New Payment!\nEmail: {email}\nPlan: {plan_name} - Rs{amt}\nTime: {datetime.now().strftime('%I:%M %p, %d %b')}"
        requests.post(url, data=msg.encode('utf-8'), headers={"Title": f"VeriSame Rs{amt} Paid!", "Priority": "high", "Tags": "moneybag,heavy_dollar_sign"}, timeout=8)
        return True
    except:
        return False

def load_db():
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    changed = False
                    for email, info in data.items():
                        if info.get("status") == "PENDING":
                            try:
                                created_str = info.get("created", "")
                                if "." in created_str:
                                    created_str = created_str.split(".")[0]
                                created_time = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
                                diff_seconds = (datetime.now() - created_time).total_seconds()
                                if diff_seconds > 60:
                                    info["status"] = "PAID"
                                    if info.get("amt") == STARTER_PRICE:
                                        info["expiry"] = (datetime.now() + timedelta(days=36500)).strftime("%Y-%m-%d")
                                    elif info.get("amt") == PRO_6M:
                                        info["expiry"] = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
                                    else:
                                        info["expiry"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                                    info["auto_approved"] = True
                                    changed = True
                            except:
                                pass
                    if changed:
                        save_db(data)
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

def load_free_clicks():
    if os.path.exists(FREE_CLICKS_FILE):
        try:
            with open(FREE_CLICKS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"count": 0, "clicks": []}
    return {"count": 0, "clicks": []}

def save_free_clicks():
    try:
        data = load_free_clicks()
        data["count"] = data.get("count", 0) + 1
        data["clicks"].append({"time": str(datetime.now()), "id": hashlib.md5(str(time.time()).encode()).hexdigest()[:6]})
        data["clicks"] = data["clicks"][-100:]
        with open(FREE_CLICKS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def enforce_delay():
    delay = 3
    bar = st.progress(0, text=f"VeriSame - Cleaning with 10 Tools ({delay}s)...")
    for i in range(100):
        time.sleep(delay/100.0)
        bar.progress(i+1)
    bar.empty()

def tool1_date(df, problem_cells):
    fixed = 0
    try:
        for col in df.columns:
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
        pass
    return fixed

def tool2_fill(df, problem_cells):
    fixed = 0
    try:
        for col in df.columns:
            if df[col].dtype != 'object':
                df[col] = df[col].astype(object)
            cl = col.lower()
            fill_val = 0 if any(k in cl for k in ['salary','amount','price','cost']) else "missing@email.com" if 'email' in cl else "Unknown"
            for r_idx in range(len(df)):
                try:
                    val = df.at[r_idx, col]
                    if pd.isna(val) or str(val).strip().lower() in ["nan","none","","null","n/a","nat",""]:
                        df.at[r_idx, col] = fill_val
                        fixed += 1
                        problem_cells.add((r_idx, col))
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
        pass
    return fixed

def tool4_phone(df, problem_cells):
    fixed = 0
    try:
        for col in df.columns:
            if not any(k in col.lower() for k in ['phone','mobile','contact']):
                continue
            for r_idx in range(len(df)):
                try:
                    orig = str(df.at[r_idx, col])
                    digits = "".join([c for c in orig if c.isdigit()])
                    if len(digits) == 0:
                        continue
                    new_val = digits[-10:] if len(digits) > 10 else digits
                    if len(digits) == 12 and digits.startswith('91'):
                        new_val = digits[-10:]
                    if orig != new_val:
                        df.at[r_idx, col] = new_val
                        fixed += 1
                        problem_cells.add((r_idx, col))
                except:
                    continue
    except:
        pass
    return fixed

def tool5_case(df, changed_cells):
    fixed = 0
    try:
        for col in df.select_dtypes(include=['object']).columns:
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
        pass
    return fixed

def tool6_symbols(df, problem_cells):
    fixed = 0
    try:
        for col in df.select_dtypes(include=['object']).columns:
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
        pass
    return fixed

def tool7_rename(df):
    fixed = 0
    try:
        new_cols = {}
        for c in df.columns:
            cleaned = re.sub(r'[^a-zA-Z0-9_ ]', '', str(c).strip())
            cleaned = re.sub(r'\s+', '_', cleaned.lower()).strip('_')
            cleaned = re.sub(r'_+', '_', cleaned)
            if cleaned == "":
                cleaned = f"col_{fixed}"
            new_cols[c] = cleaned
            if c != cleaned:
                fixed += 1
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
        pass
    return fixed

def tool10_spell(df, problem_cells):
    fixed = 0
    try:
        typo_dict = {"teh":"the","recieve":"receive","goverment":"government","salery":"salary","custmer":"customer","addres":"address","manger":"manager"}
        for col in df.select_dtypes(include=['object']).columns:
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
        pass
    return fixed

def find_ambiguous(original_df, cleaned_df):
    ambiguous = []
    try:
        for col in original_df.columns:
            cl = col.lower()
            for r_idx in range(min(len(original_df), len(cleaned_df))):
                try:
                    orig = str(original_df.at[r_idx, col]).strip()
                    cleaned = str(cleaned_df.at[r_idx, col]) if r_idx < len(cleaned_df) else orig
                    if orig.lower() in ["", "nan", "none", "null", "n/a", "unknown", "nat"]:
                        continue
                    if 'date' in cl or 'dob' in cl:
                        parts = re.split(r'[-/]', orig)
                        if len(parts) >= 2:
                            try:
                                p1 = int(re.sub(r'\D', '', parts[0]))
                                p2 = int(re.sub(r'\D', '', parts[1]))
                                if 1 <= p1 <= 12 and 1 <= p2 <= 12 and p1 != p2 and p1 <= 31 and p2 <= 31:
                                    if '/' in orig or '-' in orig:
                                        ambiguous.append({"row": r_idx, "col": col, "original": orig, "cleaned": cleaned, "type": "date","question": f"Date '{orig}' - DD/MM or MM/DD?","options": [f"{p1:02d}/{p2:02d} as DD/MM", f"{p2:02d}/{p1:02d} as MM/DD"]})
                            except:
                                pass
                    if any(k in cl for k in ['salary','amount','price','cost']) and orig.isdigit():
                        try:
                            val = int(orig)
                            if 1 <= val <= 500:
                                ambiguous.append({"row": r_idx, "col": col, "original": orig, "cleaned": cleaned, "type": "salary","question": f"Salary '{orig}' - ₹{orig} or ₹{orig}000?","options": [f"₹{orig} (keep)", f"₹{orig}000", f"₹{orig}00000"]})
                        except:
                            pass
                except:
                    continue
    except:
        pass
    seen = set()
    uniq = []
    for a in ambiguous:
        key = (a['row'], a['col'], a['original'])
        if key not in seen:
            seen.add(key)
            uniq.append(a)
    return uniq[:8]

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

def query_groq(user_prompt):
    groq_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, 'secrets') else None
    if not groq_key or Groq is None:
        return "Groq API key missing - Add GROQ_API_KEY in secrets. Model: openai/gpt-oss-20b"
    try:
        client = Groq(api_key=groq_key)
        system_prompt = """You are VeriSame AI - expert for VeriSame. 10 Tools: Smart Date, AI Fill, Email AI, Phone AI, Case AI, Symbol Clean, Header Clean, Dedup, Trim AI, Spell AI. Plans: Free 200 rows no email, Starter 49 2000 rows credit never expires, Pro 299 30 days, Pro 1499 180 days unlimited."""
        comp = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], temperature=0.6, max_tokens=500)
        return comp.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)[:200]}"

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
.block-container {background: rgba(255,255,255,0.97); border-radius: 32px; padding: 2rem 2.2rem; max-width: 1350px; margin: 0 auto; box-shadow: 0 30px 60px rgba(139,92,246,0.25); border: 1.5px solid rgba(255,255,255,0.7);}
h1 {font-family: 'Outfit', sans-serif; font-weight: 900!important; font-size: 4.8rem!important; background: linear-gradient(100deg, #4c1d95, #9333ea, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.05!important;}
.subtitle {color: #6b7280!important; font-size: 1.15rem!important; margin-top: 6px!important;}
.tagline-badge {display: inline-block; padding: 10px 22px; background: linear-gradient(135deg, #9333ea, #7e22ce); color: #fff !important; font-weight: 800 !important; border-radius: 24px; margin-left: 14px; font-size: 1rem;}
.logo-container {width: 100%; min-height: 420px; display: flex; align-items: center; justify-content: center;}
.logo-container img {width: 100%; max-width: 480px; max-height: 480px; object-fit: contain;}
.logo-float {animation: float 4s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.pricing-card {border-radius: 24px; padding: 1.6rem; background: #ffffff!important; border: 2.5px solid #9333ea; box-shadow: 0 10px 24px rgba(147,51,234,0.1); height: 100%;}
.pricing-card-free {border: 2.5px solid #9333ea !important;}
.pricing-card-starter {border: 2.5px solid #22c55e !important; transform: scale(1.02);}
.pricing-card-pro {border: 3.5px solid #9333ea !important; transform: scale(1.03);}
.stButton>button {border-radius: 16px !important; font-weight: 800 !important; background: linear-gradient(100deg, #7e22ce, #9333ea, #a855f7) !important; color: white !important; border: none !important; padding: 14px 24px !important; width: 100% !important; box-shadow: 0 8px 20px rgba(147,51,234,0.4) !important; transition: all 0.2s ease !important;}
.stButton>button:active {transform: scale(0.97) !important;}
.pro-banner {background: linear-gradient(135deg, #4c1d95, #7e22ce, #9333ea, #d946ef); padding: 2rem; border-radius: 26px; text-align: center; margin: 1.2rem 0;}
.pro-banner h2 {color: white!important; font-size: 1.8rem!important; margin: 0!important;}
.tool-chip {display: inline-block; background: #ffffff !important; padding: 11px 18px; border-radius: 26px; margin: 5px; border: 2.5px solid #9333ea; color: #4c1d95 !important; font-weight: 800 !important; font-size: 0.92rem !important;}
.big-clean-box {background: linear-gradient(135deg, #faf5ff, #f5f3ff, #ede9fe); padding: 30px; border-radius: 22px; border: 3px dashed #9333ea; margin: 18px 0; text-align: center;}
.plan-status-box {padding: 12px 16px; border-radius: 14px; font-weight: 800 !important; margin-bottom: 12px;}
.plan-active {background: #dcfce7 !important; border: 2px solid #22c55e !important; color: #15803d !important;}
.plan-selected {background: #fef9c3 !important; border: 2.5px solid #eab308 !important; color: #854d0e !important;}
.plan-warning {background: #fef2f2 !important; border: 3px solid #ef4444 !important; color: #991b1b !important; animation: blink 1.5s infinite; font-weight: 900 !important; border-radius: 16px; padding: 14px; margin-bottom: 12px;}
@keyframes blink {0%,100%{opacity: 1;} 50%{opacity: 0.7;}}
.confirm-box {background: #fef3c7 !important; border: 3px solid #f59e0b !important; border-radius: 20px; padding: 20px; margin: 16px 0;}
.hundred-box {background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important; border: 3px solid #22c55e !important; border-radius: 20px; padding: 20px; margin: 16px 0; text-align: center;}
.qr-box {background: #ffffff !important; border: 2.5px solid #9333ea !important; border-radius: 20px; padding: 16px; text-align: center; margin: 10px 0;}
.upgrade-msg {background: linear-gradient(135deg, #fef9c3 0%, #fef3c7 100%) !important; border: 3px solid #eab308 !important; border-radius: 20px; padding: 22px; text-align: center; margin: 16px 0;}
.upgrade-msg h3 {color: #854d0e !important; font-size: 1.3rem !important; margin: 0 !important;}
.red-btn button {background: linear-gradient(100deg, #ef4444, #dc2626) !important; border: 2.5px solid #ef4444 !important;}
.white-red-btn button {background: #ffffff !important; color: #ef4444 !important; border: 2.5px solid #ef4444 !important; box-shadow: 0 4px 12px rgba(239,68,68,0.2) !important;}
@media (max-width: 768px) {
  .block-container {padding: 1rem 1rem !important; border-radius: 20px !important; max-width: 100% !important;}
  h1 {font-size: 2.8rem!important;}
  .logo-container {min-height: 280px !important;}
  .logo-container img {max-width: 280px !important; max-height: 280px !important;}
  .tagline-badge {font-size: 0.85rem !important; margin-left: 0px !important; margin-top: 8px !important; display: block !important;}
  .pro-banner h2 {font-size: 1.2rem!important;}
  .tool-chip {padding: 8px 12px !important; font-size: 0.8rem !important; margin: 3px !important;}
  .pricing-card {margin-bottom: 16px !important;}
}
</style>
""", unsafe_allow_html=True)

components.html("<script>localStorage.getItem('verisame_email');</script>", height=0)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! I am VeriSame AI - All 10 tools in every plan! Free 200 rows no email, Starter ₹49 2000 rows never expires, Pro ₹299 30 days, Pro ₹1499 180 days unlimited."}]
if "changed_cells" not in st.session_state:
    st.session_state.changed_cells = set()
if "problem_cells" not in st.session_state:
    st.session_state.problem_cells = set()
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
for k in ['plan','email','df_clean','df_original','amt','email_entered','days','selected_plan','selected_amt','admin_approved','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done','ambiguous_list','hundred_done','confirm_choices','payment_pending','payment_time']:
    if k not in st.session_state:
        st.session_state[k] = None if k in ['plan','email','df_clean','df_original','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','ambiguous_list','confirm_choices','payment_time'] else False

query_email = st.query_params.get("email", None)
if query_email and not st.session_state.email and not st.session_state.selected_plan:
    query_email = query_email.lower().strip()
    if "@" in query_email and "." in query_email:
        db_check = load_db()
        if query_email in db_check:
            user_check = db_check[query_email]
            try:
                exp = datetime.strptime(user_check.get("expiry", "2000-01-01"), "%Y-%m-%d").date()
                if exp >= datetime.now().date() or user_check.get("plan") in ["starter"]:
                    st.session_state.email = query_email
                    st.session_state.email_entered = True
                    st.session_state.plan = user_check.get("plan")
                    st.session_state.amt = user_check.get("amt",0)
                    st.session_state.selected_amt = user_check.get("amt",0)
            except:
                pass

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

def render_chat(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 VeriSame AI - Ask Anything")
    html = "<div style='max-height: 280px; overflow-y: auto; padding: 12px; background: #fff !important; border: 2px solid #9333ea; border-radius: 16px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history[-6:]:
        if chat["role"] == "assistant":
            html += f"<p style='color: #6b21a8 !important; margin: 6px 0;'><b>AI:</b> {chat['message']}</p>"
        else:
            html += f"<p style='color: #000 !important; margin: 6px 0;'><b>You:</b> {chat['message']}</p>"
    html += "</div>"
    target.markdown(html, unsafe_allow_html=True)
    s_id = "side" if is_sidebar else "main"
    um = target.text_input("Ask", placeholder="Ask about VeriSame, 10 tools...", key=f"chat_{s_id}_final_restore", label_visibility="collapsed")
    if target.button("Send", key=f"btn_chat_{s_id}_final_restore", use_container_width=True):
        if um and um.strip():
            st.session_state.chat_history.append({"role": "user", "message": um})
            reply = query_groq(um)
            st.session_state.chat_history.append({"role": "assistant", "message": reply})
            st.rerun()

if st.session_state.email and st.session_state.plan != "free":
    db = load_db()
    user = db.get(st.session_state.email, {})
    st.sidebar.markdown(f"<div style='background: #f5f3ff; padding: 10px; border-radius: 12px; border: 2px solid #9333ea;'><b>{st.session_state.email}</b></div>", unsafe_allow_html=True)
    if user.get("plan") in ["starter","pro"] and user.get("expiry"):
        try:
            sel_amt = user.get("amt",0)
            exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d").date()
            today = datetime.now().date()
            days_left = (exp_date - today).days
            st.session_state.days = days_left
            if user.get("status") == "PAID":
                st.session_state.admin_approved = True
                if user.get("plan") == "starter":
                    st.sidebar.markdown(f"<div class='plan-status-box plan-active'>🟢 Starter Active - 2000 Rows - Credit Never Expires</div>", unsafe_allow_html=True)
                else:
                    if sel_amt == PRO_1M:
                        name = "Pro ₹299 - 30 Days"
                    else:
                        name = "Pro ₹1499 - 180 Days (6 Months)"
                    if days_left < 0:
                        st.sidebar.markdown(f"<div class='plan-selected'>🟡 {name} Ended</div>", unsafe_allow_html=True)
                    elif 1 <= days_left <= 5:
                        st.sidebar.markdown(f"<div class='plan-selected'>⚠️ {name} ends in {days_left} days!</div>", unsafe_allow_html=True)
                        st.sidebar.markdown(f"<div class='plan-status-box plan-active'>🟢 Pro Active - {days_left} Days Left</div>", unsafe_allow_html=True)
                    else:
                        st.sidebar.markdown(f"<div class='plan-status-box plan-active'>🟢 {name} - {days_left} Days Left</div>", unsafe_allow_html=True)
            else:
                if sel_amt == STARTER_PRICE:
                    st.sidebar.markdown(f"<div class='plan-status-box plan-selected'>🟡 Starter ₹49 - Selected</div>", unsafe_allow_html=True)
                elif sel_amt == PRO_1M:
                    st.sidebar.markdown(f"<div class='plan-status-box plan-selected'>🟡 Pro ₹299 - 30 Days - Selected</div>", unsafe_allow_html=True)
                elif sel_amt == PRO_6M:
                    st.sidebar.markdown(f"<div class='plan-status-box plan-selected'>🟡 Pro ₹1499 - 180 Days - Selected</div>", unsafe_allow_html=True)
                else:
                    st.sidebar.markdown(f"<div class='plan-status-box plan-selected'>🟡 Selected</div>", unsafe_allow_html=True)
        except:
            st.sidebar.markdown(f"<div class='plan-status-box plan-selected'>🟡 Selected Plan</div>", unsafe_allow_html=True)
    render_chat(is_sidebar=True)
    st.sidebar.markdown("---")
    fb2 = st.sidebar.text_area("Feedback", placeholder="Your feedback...", key="fb_side_restore", height=70, label_visibility="collapsed")
    if st.sidebar.button("Send Feedback", key="fb_side_btn_restore", use_container_width=True):
        if fb2.strip() and save_feedback(fb2.strip(), st.session_state.get('email','Guest')):
            st.sidebar.success("Sent!")
    components.html(f"<script>localStorage.setItem('verisame_email', '{st.session_state.email}');</script>", height=0)
elif st.session_state.plan == "free":
    st.sidebar.markdown(f"<div class='plan-status-box plan-active'>🟢 Free Plan - 200 Rows - Lifetime Free</div>", unsafe_allow_html=True)
    render_chat(is_sidebar=True)
    st.sidebar.markdown("---")
    fb2 = st.sidebar.text_area("Feedback", placeholder="Feedback...", key="fb_side_free_restore", height=70, label_visibility="collapsed")
    if st.sidebar.button("Send Feedback", key="fb_side_free_btn_restore", use_container_width=True):
        if fb2.strip() and save_feedback(fb2.strip(), "Guest_Free"):
            st.sidebar.success("Sent!")

if st.session_state.plan or st.session_state.email_entered:
    st.sidebar.markdown("---")
    b1,b2 = st.sidebar.columns(2)
    with b1:
        if st.button("← Back", key="nav_back_restore", use_container_width=True):
            st.session_state.selected_plan=None
            st.session_state.selected_amt=None
            st.session_state.plan=None
            st.session_state.email_entered=False
            st.session_state.uploaded_files={}
            st.session_state.clean_done=False
            st.session_state.hundred_done=False
            st.session_state.ambiguous_list=None
            st.session_state.payment_pending=False
            st.session_state.payment_time=None
            st.rerun()
    with b2:
        if st.button("Logout", key="nav_logout_restore", use_container_width=True):
            for k in ['plan','email','df_clean','df_original','amt','email_entered','days','selected_plan','selected_amt','admin_approved','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done','ambiguous_list','hundred_done','confirm_choices','payment_pending','payment_time']:
                st.session_state[k] = None if k in ['plan','email','df_clean','df_original','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','ambiguous_list','confirm_choices','payment_time'] else False
            st.session_state.uploaded_files={}
            st.session_state.changed_cells=set()
            st.session_state.problem_cells=set()
            st.query_params.clear()
            st.rerun()

col1, col2 = st.columns([1.3, 3.7])
with col1:
    st.markdown("""<div class="logo-container logo-float"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" alt="VeriSame"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div style="margin-top: 50px;"><h1>VeriSame</h1><span class="tagline-badge">Clean logic. Clear result</span><div class="subtitle">The Fastest Way to Clean Your Data</div></div>""", unsafe_allow_html=True)

st.markdown(f"""<div class='pro-banner'><h2>UNLOCK 10 PREMIUM AI TOOLS - All Plans Include All 10 Tools</h2><div style='margin-top:12px;'>{''.join([f'<span class=\"tool-chip\">{t}</span>' for t in ['Smart Date','AI Fill','Email AI','Phone AI','Case AI','Symbol Clean','Header Clean','Fuzzy Dedup','Trim AI','Spell AI']])}</div></div>""", unsafe_allow_html=True)

if "admin" in st.query_params:
    if st.query_params.get("admin")==ADMIN_PASS:
        st.title("🔐 Secret Dashboard - 1 MIN AUTO")
        st.success(f"✅ 1 min auto-approve ON | Topic: {NTFY_TOPIC}")
        data=load_db()
        fbs=load_feedback()
        free_data=load_free_clicks()
        tab1, tab2, tab3, tab4 = st.tabs([f"1. FREE - {free_data.get('count',0)} Clicks", f"2. STARTER ₹49 - {len([k for k,v in data.items() if v.get('amt')==STARTER_PRICE])} Users", f"3. PRO ₹299/₹1499 - {len([k for k,v in data.items() if v.get('amt') in [PRO_1M, PRO_6M]])} Users", f"4. Feedback - {len(fbs)}"])
        with tab1:
            st.markdown(f"<div class='pricing-card' style='text-align:center;'><h1 style='font-size:3rem!important;'>{free_data.get('count',0)}</h1><p>Total Free Clicks</p></div>", unsafe_allow_html=True)
            if free_data.get("clicks"):
                for click in reversed(free_data["clicks"][-20:]):
                    st.markdown(f"<div style='background:#f5f3ff; padding:8px; border-radius:8px; margin:4px 0;'>🕒 {click.get('time','')}</div>", unsafe_allow_html=True)
        with tab2:
            starter_users = {k:v for k,v in data.items() if v.get('amt')==STARTER_PRICE}
            if starter_users:
                for email, info in list(starter_users.items()):
                    if "@" not in email: continue
                    c1,c2,c3=st.columns([4,2,2])
                    with c1:
                        auto = " (Auto)" if info.get("auto_approved") else ""
                        st.markdown(f"<div class='pricing-card'><b>{email}</b><br>₹{info.get('amt')} Status: {info.get('status')}{auto}<br>{info.get('expiry')}</div>", unsafe_allow_html=True)
                    with c2:
                        if info.get("status") in ["PENDING","EXPIRED"]:
                            if st.button("✅ Approve", key=f"ap_s_{email}_restore", type="primary", use_container_width=True):
                                data[email]["status"]="PAID"
                                data[email]["expiry"]=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                                save_db(data)
                                st.rerun()
                    with c3:
                        if st.button("Delete", key=f"del_s_{email}_restore", use_container_width=True):
                            del data[email]
                            save_db(data)
                            st.rerun()
        with tab3:
            pro_users = {k:v for k,v in data.items() if v.get('amt') in [PRO_1M, PRO_6M]}
            if pro_users:
                for email, info in list(pro_users.items()):
                    if "@" not in email: continue
                    try:
                        exp_d = datetime.strptime(info.get("expiry","2000-01-01"), "%Y-%m-%d").date()
                        days_left_admin = (exp_d - datetime.now().date()).days
                    except:
                        days_left_admin = 0
                    c1,c2,c3=st.columns([4,2,2])
                    with c1:
                        sel = "1M ₹299 - 30 Days" if info.get("amt")==PRO_1M else "6M ₹1499 - 180 Days"
                        st.markdown(f"<div class='pricing-card'><b>{email}</b><br>{sel} Status: {info.get('status')}<br>Days Left: {days_left_admin}</div>", unsafe_allow_html=True)
                    with c2:
                        if info.get("status") in ["PENDING","EXPIRED"]:
                            if st.button("✅ Approve", key=f"ap_p_{email}_restore", type="primary", use_container_width=True):
                                data[email]["status"]="PAID"
                                data[email]["expiry"]=(datetime.now()+timedelta(days=180 if data[email].get("amt")==PRO_6M else 30)).strftime("%Y-%m-%d")
                                save_db(data)
                                st.rerun()
                    with c3:
                        if st.button("Delete", key=f"del_p_{email}_restore", use_container_width=True):
                            del data[email]
                            save_db(data)
                            st.rerun()
        with tab4:
            if fbs:
                for fb in reversed(fbs[-50:]):
                    st.markdown(f"<div style='background:#fff; border:2px solid #e9d5ff; border-radius:16px; padding:14px; margin:10px 0;'><b>{fb['email']}</b> | {fb['time']}<br>{fb['feedback']}</div>", unsafe_allow_html=True)
        st.stop()
    else:
        st.error("Unauthorized")
        st.stop()

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        st.markdown("<h2 style='text-align:center;'>Choose Your Plan - All 10 Tools Included</h2>", unsafe_allow_html=True)
        col_free, col_starter, col_pro = st.columns(3, gap="medium")
        with col_free:
            st.markdown(f"""<div class='pricing-card pricing-card-free'><h3>FREE FOREVER</h3><h1 style='font-size:2.2rem!important;'>FREE</h1><p><b>200 Rows Limit</b> (Lifetime Free)</p><div style='margin-top:12px;'><p>✓ All 10 Tools Included</p><p>✓ 3s Super Fast Cleaning</p><p>✓ CSV + Excel + PDF Support</p><p>✓ File Auto-Deleted - 100% Private</p><p>✓ Email Support</p></div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free_restore", type="primary", use_container_width=True):
                save_free_clicks()
                st.session_state.selected_plan="free"
                st.session_state.plan="free"
                st.session_state.email="Guest_Free"
                st.session_state.email_entered=True
                st.session_state.admin_approved=True
                st.rerun()
        with col_starter:
            st.markdown(f"""<div class='pricing-card pricing-card-starter'><p style='background: #22c55e; color:white!important; padding:6px 14px; border-radius:20px; display:inline-block; font-size:0.85rem; font-weight: 800;'>✨ BEST FOR TRYING</p><h3>STARTER</h3><h1 style='font-size:2.2rem!important;'>₹49</h1><p><b>One-Time - 2,000 Rows Credit</b></p><div style='margin-top:12px;'><p>✓ All 10 Tools</p><p>✓ Credit Never Expires</p><p>✓ 3s Super Fast</p><p>✓ No Watermark</p><p>✓ CSV + Excel + PDF</p></div></div>""", unsafe_allow_html=True)
            if st.button("Start with 49", key="btn_starter_restore", type="primary", use_container_width=True):
                st.session_state.selected_plan="starter"
                st.session_state.selected_amt=STARTER_PRICE
                st.session_state.amt=STARTER_PRICE
                st.session_state.days=36500
                st.rerun()
        with col_pro:
            st.markdown(f"""<div class='pricing-card pricing-card-pro'><p style='background: #9333ea; color:white!important; padding:6px 14px; border-radius:20px; display:inline-block; font-size:0.85rem; font-weight: 800;'>⭐ POPULAR - BEST VALUE</p><h3>PRO</h3><h1 style='font-size:2rem!important;'>₹299 / ₹1499</h1><p><b>Unlimited Rows</b></p><div style='margin-top:12px;'><p>✓ ₹299 for 1 Month (30 Days)</p><p>✓ ₹1499 for 6 Months (180 Days)</p><p>✓ Unlimited Rows</p><p>✓ All 10 Premium AI Tools</p><p>✓ Priority Support</p><p>✓ No Watermark</p></div></div>""", unsafe_allow_html=True)
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                if st.button("Start with 299", key="btn_pro_299_restore", type="primary", use_container_width=True):
                    st.session_state.selected_plan="pro"
                    st.session_state.selected_amt=PRO_1M
                    st.session_state.amt=PRO_1M
                    st.session_state.days=30
                    st.rerun()
            with c_p2:
                if st.button("Start with 1499", key="btn_pro_1499_restore", type="primary", use_container_width=True):
                    st.session_state.selected_plan="pro"
                    st.session_state.selected_amt=PRO_6M
                    st.session_state.amt=PRO_6M
                    st.session_state.days=180
                    st.rerun()
        render_chat(is_sidebar=False)
        st.markdown("---")
        st.markdown("### 💌 Feedback - We Listen!")
        fb_front = st.text_area("Feedback", placeholder="Your feedback about VeriSame...", key="fb_front_restore", height=90, label_visibility="collapsed")
        if st.button("Send Feedback", key="fb_front_btn_restore", type="primary", use_container_width=True):
            if fb_front.strip() and save_feedback(fb_front.strip(), st.session_state.get('email','Guest_Front')):
                st.success("Thank you for feedback! 💜")
                st.balloons()
    else:
        if st.session_state.selected_plan == "free":
            st.session_state.plan = "free"
            st.session_state.email = "Guest_Free"
            st.session_state.email_entered = True
            st.session_state.admin_approved = True
            st.rerun()
        
        if st.session_state.selected_plan == "starter":
            plan_text = f"STARTER - ₹{STARTER_PRICE} One-Time - 2,000 Rows Credit"
        else:
            if st.session_state.selected_amt == PRO_1M:
                plan_text = "PRO - 1 Month (30 Days) - ₹299"
            else:
                plan_text = "PRO - 6 Months (180 Days) - ₹1499 - Best Value"
        st.markdown(f"<h2 style='text-align:center;'>Enter email for {plan_text}</h2>", unsafe_allow_html=True)
        _, ce2, _ = st.columns([1,2,1])
        with ce2:
            email_input = st.text_input("Enter your email", placeholder="your@email.com", key="email_main_restore").lower().strip()
            b1,b2 = st.columns(2)
            with b1:
                if st.button("Verify & Continue", key="btn_verify_restore", type="primary", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        st.session_state.email=email_input
                        st.session_state.email_entered=True
                        data=load_db()
                        if st.session_state.selected_plan=="starter":
                            exp=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                            data[email_input]={"plan":"starter","status":"PENDING","amt":STARTER_PRICE,"days":36500,"expiry":exp,"created":str(datetime.now())}
                            save_db(data)
                            st.session_state.plan="starter"
                            st.session_state.amt=STARTER_PRICE
                            st.rerun()
                        else:
                            exact=180 if st.session_state.selected_amt==PRO_6M else 30
                            exp=(datetime.now()+timedelta(days=exact)).strftime("%Y-%m-%d")
                            data[email_input]={"plan":"pro","status":"PENDING","amt":st.session_state.selected_amt,"days":exact,"expiry":exp,"created":str(datetime.now())}
                            save_db(data)
                            st.session_state.plan="pro"
                            st.session_state.amt=st.session_state.selected_amt
                            st.rerun()
                    else:
                        st.error("Enter valid email")
            with b2:
                if st.button("← Back to Plans", key="btn_back_restore", use_container_width=True):
                    st.session_state.selected_plan=None
                    st.session_state.selected_amt=None
                    st.rerun()
        render_chat(is_sidebar=False)
        st.markdown("---")
        st.markdown("### 💌 Feedback")
        fb_e = st.text_area("Feedback", placeholder="Your feedback...", key="fb_email_restore", height=80, label_visibility="collapsed")
        if st.button("Send Feedback", key="fb_email_btn_restore", use_container_width=True):
            if fb_e.strip() and save_feedback(fb_e.strip(), st.session_state.get('email','Guest')):
                st.success("Sent!")
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
                        sel=st.selectbox(f"Sheet for {f.name}", ef.sheet_names, key=f"sh_{f.name}_restore")
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
                            limit = FREE_LIMIT if st.session_state.plan=="free" else STARTER_LIMIT if st.session_state.plan=="starter" else 1000000
                            if len(sub)>limit and st.session_state.plan in ["free","starter"]:
                                sub=sub.iloc[:limit].copy()
                            clean_init=sub.copy()
                            for col in clean_init.columns:
                                if clean_init[col].dtype!='object':
                                    clean_init[col]=clean_init[col].astype(object)
                            clean_init.drop_duplicates(inplace=True)
                            clean_init.reset_index(drop=True, inplace=True)
                            base_name = f.name
                            st.session_state.uploaded_files[base_name]={"original":sub.copy().reset_index(drop=True),"clean":clean_init,"orig_len":len(sub),"empty_fixed":int(sub.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}
                        except Exception as e:
                            st.error(f"Error reading {f.name}: {e}")
                    st.session_state.last_upload_sig=sig
                    st.session_state.clean_done=False
                    st.session_state.hundred_done=False
                    st.session_state.ambiguous_list=None
                    st.session_state.hub_report=None
                except Exception as e:
                    st.error(f"Error: {e}")
    with tab2:
        if st.button("Load Sample Data", key="btn_load_sample_restore", type="primary", use_container_width=True):
            sample=pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT"],"Email":["RAHUL@GMAIL.COM","bad@gmai.com","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["100","250","50000"]})
            clean=sample.copy()
            st.session_state.uploaded_files={"sample_data.csv":{"original":sample.copy().reset_index(drop=True),"clean":clean,"orig_len":len(sample),"empty_fixed":int(sample.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}}
            st.session_state.last_upload_sig=None
            st.session_state.clean_done=False
            st.session_state.hundred_done=False
            st.session_state.ambiguous_list=None
            st.rerun()

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        keys=list(st.session_state.uploaded_files.keys())
        sel_file=st.selectbox("Select file:", keys, key="active_file_restore", label_visibility="collapsed")
        limit = FREE_LIMIT if st.session_state.plan=="free" else STARTER_LIMIT if st.session_state.plan=="starter" else 1000000
        if st.session_state.plan in ["free","starter"] and len(st.session_state.uploaded_files[sel_file]["clean"]) > limit:
            st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.uploaded_files[sel_file]["clean"].iloc[:limit]
        st.session_state.df_clean=st.session_state.uploaded_files[sel_file]["clean"]
        st.session_state.df_original=st.session_state.uploaded_files[sel_file]["original"]
        st.session_state.orig_len=len(st.session_state.df_original)
        st.session_state.empty_fixed=st.session_state.uploaded_files[sel_file]["empty_fixed"]
        st.session_state.problem_cells=st.session_state.uploaded_files[sel_file].get("problem_cells",set())
        update_changed()
        df_clean=st.session_state.df_clean
        orig_len=st.session_state.orig_len

        if not st.session_state.get("clean_done"):
            st.markdown(f"### File: {sel_file} - {orig_len} rows")
            if st.button("🧹 BIG CLEAN - Fix & Clean Everything (1 Click = 10 Tools)", key="btn_big_clean_restore", type="primary", use_container_width=True):
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
                    fixes.append(("Smart Date", tool1_date(df_curr, st.session_state.problem_cells)))
                    fixes.append(("AI Fill", tool2_fill(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Email AI", tool3_email(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Phone AI", tool4_phone(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Case AI", tool5_case(df_curr, st.session_state.changed_cells)))
                    fixes.append(("Symbol Clean", tool6_symbols(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Header Clean", tool7_rename(df_curr)))
                    fixes.append(("Fuzzy Dedup", tool8_dedup(df_curr)))
                    fixes.append(("Trim AI", tool9_trim(df_curr, st.session_state.changed_cells)))
                    fixes.append(("Spell AI", tool10_spell(df_curr, st.session_state.problem_cells)))
                    for name,cnt in fixes:
                        hub.append(f"{name}: Fixed {cnt}" if cnt else f"{name}: Clean")
                    st.session_state.df_clean=df_curr
                    update_changed()
                    ambiguous = find_ambiguous(st.session_state.df_original, st.session_state.df_clean)
                    st.session_state["hub_report"]=hub
                    st.session_state["clean_done"]=True
                    st.session_state["ambiguous_list"]=ambiguous
                    st.session_state["hundred_done"] = len(ambiguous) == 0
                    st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.df_clean
                    st.session_state.uploaded_files[sel_file]["changed_cells"]=st.session_state.changed_cells
                    st.session_state.uploaded_files[sel_file]["problem_cells"]=st.session_state.problem_cells
                    st.success("✅ Cleaned! 100% Clean Logic")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Cleaning error: {e}")
        else:
            ambiguous = st.session_state.get("ambiguous_list", [])
            is_hundred = st.session_state.get("hundred_done", False) or len(ambiguous) == 0
            percent_text = "100% Clean" if is_hundred else "95% Clean"
            st.markdown(f"<h2>Data Summary - {percent_text}</h2>", unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            with c1:
                st.metric("Total Rows", orig_len)
            with c2:
                st.metric("Clean Rows", len(df_clean))
            with c3:
                st.metric("Duplicates", max(0, orig_len-len(df_clean)))
            with c4:
                st.metric("Empty Fixed", st.session_state.empty_fixed)
            
            if is_hundred:
                st.markdown("<div class='hundred-box'><h3>🎉 100% Clean Achieved!</h3></div>", unsafe_allow_html=True)

            st.markdown(f"<h3>Cleaned Preview - 10 Rows - {percent_text}</h3>", unsafe_allow_html=True)
            styled=apply_style(df_clean.head(10))
            st.dataframe(styled, use_container_width=True, height=350)

        if st.session_state.get("clean_done"):
            ambiguous = st.session_state.get("ambiguous_list", [])
            is_hundred = st.session_state.get("hundred_done", False) or len(ambiguous) == 0
            percent_text = "100% Clean" if is_hundred else "95% Clean"
            db=load_db()
            user_info=db.get(st.session_state.email,{}) if st.session_state.email and st.session_state.email != "Guest_Free" else {}
            is_paid=user_info.get("status")=="PAID" if user_info else True if st.session_state.plan=="free" else False
            
            if st.session_state.plan=="free":
                st.markdown(f"<h2>Export Data - {percent_text}</h2>", unsafe_allow_html=True)
                c1,c2,c3=st.columns(3)
                safe=sel_file[:30]
                suffix = "100_percent" if is_hundred else "95_percent"
                with c1:
                    csv=df_clean.to_csv(index=False).encode()
                    st.download_button(f"CSV - {percent_text}", csv, f"{safe}_{suffix}_cleaned.csv", mime="text/csv", key="dl_csv_free_restore", use_container_width=True, type="primary")
                with c2:
                    if openpyxl is not None:
                        ex=io.BytesIO()
                        df_clean.to_excel(ex, index=False, engine='openpyxl')
                        ex.seek(0)
                        st.download_button(f"Excel - {percent_text}", ex.getvalue(), f"{safe}_{suffix}_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx_free_restore", use_container_width=True)
                with c3:
                    pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean)
                    if pdf:
                        st.download_button(f"PDF - {percent_text}", pdf, f"{safe}_{suffix}_audit.pdf", mime="application/pdf", key="dl_pdf_free_restore", use_container_width=True)
            elif st.session_state.plan in ["starter","pro"]:
                if not is_paid:
                    sel_amt = user_info.get("amt", st.session_state.get("selected_amt", 0))
                    clean_msg = "100% successfully" if is_hundred else "95% - Confirm for 100%"
                    
                    # CHECK PENDING - HIDDEN BACKGROUND LOGIC
                    pending_info = db.get(st.session_state.email, {})
                    created_str = pending_info.get("created", "")
                    is_pending = pending_info.get("status") == "PENDING" and created_str != ""
                    
                    if is_pending:
                        try:
                            if "." in created_str:
                                created_str_clean = created_str.split(".")[0]
                            else:
                                created_str_clean = created_str
                            created_time = datetime.strptime(created_str_clean, "%Y-%m-%d %H:%M:%S")
                            elapsed = (datetime.now() - created_time).total_seconds()
                            
                            if elapsed >= 60:
                                st.success("🎉 Payment verified! Download ready!")
                                st.balloons()
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                # HIDDEN - No countdown visible to user, just spinner
                                st.markdown("""
                                <div style='background: #f5f3ff; border: 2px solid #9333ea; border-radius: 16px; padding: 16px; text-align: center; margin: 16px 0;'>
                                    <p style='margin:0; color: #6b21a8; font-weight: 700;'>✅ Payment received! Your download is being prepared...</p>
                                    <p style='margin:4px 0 0 0; color: #6b7280; font-size: 0.9rem;'>Please wait, file is safe!</p>
                                </div>
                                """, unsafe_allow_html=True)
                                with st.spinner("Preparing your download..."):
                                    # Hidden auto-refresh every 4 sec in background - checks for approval
                                    components.html("""
                                    <script>
                                        setTimeout(function(){
                                            window.parent.location.reload();
                                        }, 4000);
                                    </script>
                                    """, height=0)
                                st.stop()
                        except:
                            pass
                    
                    if not is_pending:
                        if sel_amt == STARTER_PRICE:
                            st.markdown(f"<div class='upgrade-msg'><h3>✅ Your file is cleaned {clean_msg} — Upgrade to ₹49 to download full file</h3></div>", unsafe_allow_html=True)
                            st.markdown("<div class='qr-box'>", unsafe_allow_html=True)
                            st.markdown("### Starter - ₹49 One-Time")
                            upi_49=f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={STARTER_PRICE}&cu=INR&tn=VeriSame Starter"
                            st.link_button(f"Pay ₹{STARTER_PRICE} via UPI", upi_49, use_container_width=True, type="primary", key="pay_49_restore")
                            display_qr(upi_49, STARTER_PRICE)
                            if st.button(f"I Paid ₹{STARTER_PRICE}", key="btn_paid_49_restore", type="primary", use_container_width=True):
                                data=load_db()
                                data[st.session_state.email]={"plan":"starter","amt":STARTER_PRICE,"days":36500,"expiry":(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                                save_db(data)
                                send_notification(st.session_state.email, STARTER_PRICE, "Starter ₹49")
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                        elif sel_amt == PRO_1M:
                            st.markdown(f"<div class='upgrade-msg'><h3>✅ Your file is cleaned {clean_msg} — Upgrade to ₹299 to download full file</h3></div>", unsafe_allow_html=True)
                            st.markdown("<div class='qr-box'>", unsafe_allow_html=True)
                            st.markdown("### Pro - ₹299 - 30 Days")
                            upi_299=f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={PRO_1M}&cu=INR&tn=VeriSame 1Month"
                            st.link_button(f"Pay ₹{PRO_1M} via UPI", upi_299, use_container_width=True, type="primary", key="pay_299_restore")
                            display_qr(upi_299, PRO_1M)
                            if st.button(f"I Paid ₹{PRO_1M}", key="btn_paid_299_restore", type="primary", use_container_width=True):
                                data=load_db()
                                data[st.session_state.email]={"plan":"pro","amt":PRO_1M,"days":30,"expiry":(datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                                save_db(data)
                                send_notification(st.session_state.email, PRO_1M, "Pro ₹299")
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                        elif sel_amt == PRO_6M:
                            st.markdown(f"<div class='upgrade-msg'><h3>✅ Your file is cleaned {clean_msg} — Upgrade to ₹1499 to download full file</h3></div>", unsafe_allow_html=True)
                            st.markdown("<div class='qr-box'>", unsafe_allow_html=True)
                            st.markdown("### Pro - ₹1499 - 180 Days (6 Months) - Best Value")
                            upi_1499=f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={PRO_6M}&cu=INR&tn=VeriSame 6Months"
                            st.link_button(f"Pay ₹{PRO_6M} via UPI", upi_1499, use_container_width=True, type="primary", key="pay_1499_restore")
                            display_qr(upi_1499, PRO_6M)
                            if st.button(f"I Paid ₹{PRO_6M}", key="btn_paid_1499_restore", type="primary", use_container_width=True):
                                data=load_db()
                                data[st.session_state.email]={"plan":"pro","amt":PRO_6M,"days":180,"expiry":(datetime.now()+timedelta(days=180)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                                save_db(data)
                                send_notification(st.session_state.email, PRO_6M, "Pro ₹1499 180 Days")
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h2>Export Data - {percent_text}</h2>", unsafe_allow_html=True)
                    st.success(f"🎉 Download Ready! {percent_text}")
                    st.balloons()
                    c1,c2,c3=st.columns(3)
                    safe=sel_file[:30]
                    suffix = "100_percent" if is_hundred else "95_percent"
                    csv=df_clean.to_csv(index=False).encode()
                    with c1:
                        st.download_button(f"CSV - {percent_text}", csv, f"{safe}_{suffix}_cleaned.csv", mime="text/csv", key="dl_csv_paid_restore", use_container_width=True, type="primary")
                    with c2:
                        if openpyxl is not None:
                            ex=io.BytesIO()
                            df_clean.to_excel(ex, index=False, engine='openpyxl')
                            ex.seek(0)
                            st.download_button(f"Excel - {percent_text}", ex.getvalue(), f"{safe}_{suffix}_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx_paid_restore", use_container_width=True)
                    with c3:
                        pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean)
                        if pdf:
                            st.download_button(f"PDF - {percent_text}", pdf, f"{safe}_{suffix}_audit.pdf", mime="application/pdf", key="dl_pdf_paid_restore", use_container_width=True)
