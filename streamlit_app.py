import json, os, io, time, re, hashlib
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

st.set_page_config(page_title="VeriSame - Premium Data Cleaner", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

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
        fb.append({
            "email": email,
            "feedback": text,
            "time": str(datetime.now()),
            "id": hashlib.md5(f"{email}{text}{time.time()}".encode()).hexdigest()[:8]
        })
        with open(FEEDBACK_FILE, "w") as f:
            json.dump(fb, f, indent=2)
        return True
    except:
        return False

def enforce_processing_delay():
    is_pro = st.session_state.get("plan") == "pro" and st.session_state.get("admin_approved")
    delay = 3 if is_pro else 15
    progress_text = f"VeriSame AI - Running 11 Tools ({delay}s)..."
    my_bar = st.progress(0, text=progress_text)
    step = delay / 100.0
    for percent_complete in range(100):
        time.sleep(step)
        my_bar.progress(percent_complete + 1, text=progress_text)
    my_bar.empty()

def words_to_num_advanced(s):
    if pd.isna(s):
        return s
    if isinstance(s, (int, float)):
        return s
    s_str = str(s).lower().strip().replace(',', '')
    if s_str.isdigit():
        try:
            return int(s_str)
        except:
            return s
    try:
        return float(s_str)
    except:
        pass
    num_words = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
        'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000,
        'lakh': 100000, 'crore': 10000000
    }
    total = 0
    current = 0
    has = False
    for w in re.findall(r'\w+', s_str):
        if w in num_words:
            has = True
            v = num_words[w]
            if v >= 100:
                if current == 0:
                    current = 1
                current = current * v
                if v >= 1000:
                    total = total + current
                    current = 0
            else:
                current = current + v
        elif w.isdigit():
            has = True
            current = current + int(w)
    if has:
        return total + current
    return s

def tool_1_advanced_date_parser(df, problem_cells):
    fixed = 0
    for col in df.columns:
        sample_vals = df[col].astype(str).head(20).str.lower()
        date_like = False
        for sv in sample_vals:
            if re.search(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec', sv):
                date_like = True
                break
        if not date_like and 'date' not in col.lower() and 'dob' not in col.lower() and 'time' not in col.lower():
            continue
        for r_idx in range(len(df)):
            orig = str(df.at[r_idx, col])
            if orig.lower().strip() in ["", "nan", "none", "null", "n/a", "unknown"]:
                continue
            try:
                if orig.isdigit() and 30000 < int(orig) < 60000:
                    base = datetime(1899, 12, 30)
                    parsed_dt = base + timedelta(days=int(orig))
                    df.at[r_idx, col] = parsed_dt.strftime('%Y-%m-%d')
                    fixed = fixed + 1
                    problem_cells.add((r_idx, col))
                    continue
            except:
                pass
            clean = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?\s*(am|pm)?', '', orig, flags=re.IGNORECASE)
            clean = clean.replace('/', '-').replace('.', '-').strip()
            try:
                parsed_dt = pd.to_datetime(clean, dayfirst=True, errors='coerce')
                if not pd.isna(parsed_dt):
                    new_val = parsed_dt.strftime('%Y-%m-%d')
                    if orig != new_val:
                        df.at[r_idx, col] = new_val
                        fixed = fixed + 1
                        problem_cells.add((r_idx, col))
                    continue
            except:
                pass
    return fixed

def tool_2_advanced_fill_nulls(df, problem_cells):
    fixed = 0
    for col in df.columns:
        if df[col].dtype != 'object':
            df[col] = df[col].astype(object)
        col_lower = col.lower()
        if any(k in col_lower for k in ['salary', 'amount', 'price', 'paisa', 'cost', 'revenue']):
            fill_val = 0
        elif any(k in col_lower for k in ['age', 'count', 'qty', 'quantity']):
            fill_val = 0
        elif 'email' in col_lower:
            fill_val = "missing@email.com"
        elif any(k in col_lower for k in ['phone', 'mobile', 'contact']):
            fill_val = "Unknown"
        elif any(k in col_lower for k in ['name', 'city', 'state', 'country']):
            fill_val = "Unknown"
        elif 'date' in col_lower:
            fill_val = datetime.now().strftime('%Y-%m-%d')
        else:
            fill_val = "Unknown"
        for r_idx in range(len(df)):
            val = df.at[r_idx, col]
            if pd.isna(val) or str(val).strip().lower() in ["nan", "none", "", "null", "n/a", "nat", ""]:
                df.at[r_idx, col] = fill_val
                fixed = fixed + 1
                problem_cells.add((r_idx, col))
    return fixed

def tool_3_advanced_email_validator(df, problem_cells):
    fixed = 0
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    typo_map = {
        "gmai.com": "gmail.com",
        "gmal.com": "gmail.com",
        "yaho.com": "yahoo.com",
        "outlok.com": "outlook.com",
        "hotmial.com": "hotmail.com"
    }
    for col in df.columns:
        is_email_col = False
        if 'email' in col.lower():
            is_email_col = True
        else:
            try:
                at_count = df[col].astype(str).str.contains('@', na=False).sum()
                if at_count > len(df) * 0.3:
                    is_email_col = True
            except:
                pass
        if not is_email_col:
            continue
        for r_idx in range(len(df)):
            orig = str(df.at[r_idx, col]).lower().strip()
            if "@" not in orig or orig in ["nan", "none", ""]:
                continue
            for wrong, correct in typo_map.items():
                if wrong in orig:
                    orig = orig.replace(wrong, correct)
            orig = re.sub(r'\s+', '', orig)
            valid = re.match(pattern, orig)
            new_val = orig if valid else "Invalid Email"
            if str(df.at[r_idx, col]).lower().strip() != new_val.lower():
                df.at[r_idx, col] = new_val
                fixed = fixed + 1
                problem_cells.add((r_idx, col))
    return fixed

def tool_4_international_phone_formatter(df, problem_cells):
    """
    FIXED - LIKE BEFORE - INTERNATIONAL SUPPORT
    India: 9876543210 stays 9876543210 (10 digit)
           +91 9876543210 -> 9876543210
           91-9876543210 -> 9876543210
    USA: +1 123-456-7890 -> 11234567890 (keeps country code)
         123-456-7890 -> 1234567890
    Other: Keeps full number clean
    """
    fixed = 0
    for col in df.columns:
        if any(k in col.lower() for k in ['phone', 'mobile', 'contact', 'tel']):
            for r_idx in range(len(df)):
                orig = str(df.at[r_idx, col])
                digits = "".join(re.findall(r'\d+', orig))
                if len(digits) == 0:
                    continue
                # Clean logic - INTERNATIONAL FRIENDLY
                if len(digits) == 10:
                    new_val = digits
                elif len(digits) == 11 and digits.startswith('1'):
                    # USA number with country code 1
                    new_val = digits
                elif len(digits) == 12 and digits.startswith('91'):
                    # India with 91 country code - take last 10 for clean 10 digit
                    new_val = digits[-10:]
                elif len(digits) > 10:
                    # Other country or with country code - keep last 10 if India pattern else keep all
                    if digits.startswith('91') and len(digits) == 12:
                        new_val = digits[-10:]
                    else:
                        # For USA and others, keep full cleaned number (up to 15 digits is valid internationally)
                        new_val = digits
                else:
                    new_val = digits
                if orig != new_val:
                    df.at[r_idx, col] = new_val
                    fixed = fixed + 1
                    problem_cells.add((r_idx, col))
    return fixed

def tool_5_advanced_case_converter(df, changed_cells):
    fixed = 0
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['name', 'city', 'state', 'country', 'company', 'department']):
            for r_idx in range(len(df)):
                orig = str(df.at[r_idx, col])
                if orig.lower() in ["unknown", "missing@email.com", "invalid email"]:
                    continue
                new_val = ' '.join([w.capitalize() if len(w) > 1 else w.upper() for w in orig.split()])
                if orig != new_val:
                    df.at[r_idx, col] = new_val
                    fixed = fixed + 1
                    changed_cells.add((r_idx, col))
    return fixed

def tool_6_advanced_remove_symbols(df, problem_cells):
    fixed = 0
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['email', 'phone']):
            continue
        for r_idx in range(len(df)):
            orig = str(df.at[r_idx, col])
            cleaned = re.sub(r'[^a-zA-Z0-9\s.,₹$€£¥@\-_()&/+]', '', orig)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if orig != cleaned:
                df.at[r_idx, col] = cleaned
                fixed = fixed + 1
                problem_cells.add((r_idx, col))
    return fixed

def tool_7_advanced_header_clean(df):
    fixed = 0
    new_cols = {}
    for c in df.columns:
        cleaned = re.sub(r'[^a-zA-Z0-9_ ]', '', str(c).strip())
        cleaned = re.sub(r'\s+', '_', cleaned.lower()).strip('_')
        cleaned = re.sub(r'_+', '_', cleaned)
        if cleaned == "":
            cleaned = f"col_{fixed}"
        new_cols[c] = cleaned
        if c != cleaned:
            fixed = fixed + 1
    df.rename(columns=new_cols, inplace=True)
    return fixed

def tool_8_advanced_fuzzy_dedup(df):
    before = len(df)
    df.drop_duplicates(inplace=True)
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    if text_cols and len(df) < 500:
        col = text_cols[0]
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) < 200:
            mapping = {}
            for i, v1 in enumerate(unique_vals):
                if v1 in mapping:
                    continue
                for v2 in unique_vals[i+1:]:
                    if v2 in mapping:
                        continue
                    r = difflib.SequenceMatcher(None, str(v1).lower().strip(), str(v2).lower().strip()).ratio()
                    if r >= 0.92:
                        mapping[v2] = v1
            if mapping:
                df[col] = df[col].replace(mapping)
                df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return before - len(df)

def tool_9_advanced_trim_spaces(df, changed_cells):
    fixed = 0
    for col in df.select_dtypes(include=['object']).columns:
        for r_idx in range(len(df)):
            orig = str(df.at[r_idx, col])
            trimmed = re.sub(r'\s+', ' ', orig.strip())
            if orig != trimmed:
                df.at[r_idx, col] = trimmed
                fixed = fixed + 1
                changed_cells.add((r_idx, col))
    return fixed

def tool_10_advanced_spell_check(df, problem_cells):
    fixed = 0
    typo_dict = {
        "teh": "the", "recieve": "receive", "goverment": "government",
        "salery": "salary", "amout": "amount", "custmer": "customer",
        "addres": "address", "manger": "manager", "dept": "department",
        "acnt": "account", "buisness": "business", "compny": "company"
    }
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['email', 'phone']):
            continue
        for r_idx in range(len(df)):
            orig = str(df.at[r_idx, col])
            words = orig.split()
            new_words = []
            changed = False
            for w in words:
                lower = w.lower().strip('.,')
                if lower in typo_dict:
                    replacement = typo_dict[lower]
                    if w and w[0].isupper():
                        replacement = replacement.capitalize()
                    new_words.append(replacement)
                    changed = True
                else:
                    new_words.append(w)
            if changed:
                df.at[r_idx, col] = " ".join(new_words)
                fixed = fixed + 1
                problem_cells.add((r_idx, col))
    return fixed

def tool_11_currency_cleaner(df, problem_cells):
    fixed = 0
    for col in df.columns:
        if any(k in col.lower() for k in ['salary', 'amount', 'price', 'cost', 'revenue', 'income']):
            for r_idx in range(len(df)):
                orig = df.at[r_idx, col]
                new_val = words_to_num_advanced(orig)
                if isinstance(new_val, str):
                    new_val_clean = re.sub(r'[₹$€£¥,]', '', new_val).strip()
                    try:
                        if new_val_clean.replace('.', '', 1).isdigit():
                            if '.' in new_val_clean:
                                new_val = float(new_val_clean)
                            else:
                                new_val = int(new_val_clean)
                        else:
                            new_val = new_val_clean
                    except:
                        new_val = new_val_clean
                if str(orig) != str(new_val):
                    df.at[r_idx, col] = new_val
                    fixed = fixed + 1
                    problem_cells.add((r_idx, col))
    return fixed

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
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Account: {st.session_state.get('email','Guest')}", sub_style))
    story.append(Spacer(1, 10))
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#1f2937'), spaceAfter=8)
    metric_data = [
        [Paragraph("<b>Metric Parameter</b>", text_style), Paragraph("<b>Value Counts</b>", text_style)],
        [Paragraph("Total Ingested Rows", text_style), Paragraph(str(orig_len), text_style)],
        [Paragraph("Clean Post-Processed Rows", text_style), Paragraph(str(clean_len), text_style)],
        [Paragraph("Duplicate Rows Extracted", text_style), Paragraph(str(orig_len-clean_len), text_style)],
        [Paragraph("Empty/Null Cells Fixed", text_style), Paragraph(str(empty_fixed), text_style)]
    ]
    t1 = Table(metric_data, colWidths=[250, 200])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#9333ea')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c084fc'))
    ]))
    story.append(t1)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def query_groq_ai(prompt_text, system_instruction="You are VeriSame AI assistant."):
    groq_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, 'secrets') else None
    if not groq_key or Groq is None:
        return None
    try:
        client = Groq(api_key=groq_key)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt_text}],
            temperature=0.5,
            max_tokens=400
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.session_state["groq_last_error"] = str(e)
        return None

def display_upi_qr(upi_uri, pay_amount):
    qr_generated = False
    if qrcode is not None:
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(upi_uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), width=250, caption=f"Scan to pay {pay_amount}")
            qr_generated = True
        except:
            qr_generated = False
    if not qr_generated:
        encoded_link = urllib.parse.quote(upi_uri)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_link}"
        st.image(qr_url, width=250, caption=f"Scan to pay {pay_amount}")

T = {
    "title": "VeriSame",
    "subtitle": "The Fastest Way to Clean Your Data",
    "pro_banner": "11 ADVANCED AI TOOLS - INTERNATIONAL PHONE SUPPORT",
    "free_title": "FREE FOREVER",
    "pro1_title": "1 MONTH (30 DAYS)",
    "pro6_title": "6 MONTHS (180 DAYS)",
    "free_feat": ["200 Rows Limit", "6 Tools", "Lifetime Free", "15s Delay", "Email Support"],
    "pro_feat": ["Unlimited Rows", "11 Tools - International", "CSV + Excel + PDF", "3s Fast", "Priority Support", "No Watermark"],
    "email_label": "Enter your email address",
    "continue_btn": "Verify & Continue",
    "upload_tab": "Upload File",
    "sample_tab": "Try Demo",
    "upload_text": "Drop CSV, Excel or JSON file here",
    "sample_btn": "Load Sample Data",
    "summary_title": "Data Summary",
    "rows": "Total Rows",
    "clean": "Clean Rows",
    "dups": "Duplicates Removed",
    "empty": "Empty Cells Fixed",
    "preview": "Cleaned Preview - 10 Rows",
    "tools_menu": "One-Click AI Studio",
    "download_title": "Export Data",
    "paid_msg": "Select plan -> Pay via UPI/QR -> Click I Paid -> Admin approves -> Balloons + Download",
    "paid_btn": "I Paid {amount} - Submit for Approval",
    "wait_approval": "Request submitted! Waiting for Admin approval...",
    "download_success": "Download Ready!",
    "admin_title": "Admin Dashboard",
    "admin_pending": "Users & Feedback",
    "admin_approve_btn": "Mark Paid",
    "admin_user": "Customer Email",
    "admin_plan": "Plan",
    "admin_expiry": "Valid Till",
    "delete_btn": "Delete User",
    "download_csv": "Download as CSV",
    "download_excel": "Download as Excel"
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Outfit:wght@700;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: radial-gradient(ellipse at top left, #f5e6ff 0%, #e9d5ff 15%, #d8b4fe 30%, #c084fc 50%, #a855f7 70%, #9333ea 85%, #7e22ce 100%); background-size: 400% 400%; animation: aurora 20s ease infinite; padding-top: 0.2rem;}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}
.block-container {background: rgba(255,255,255,0.94); backdrop-filter: blur(30px) saturate(180%); border-radius: 32px; padding: 2.2rem 2.5rem; max-width: 1250px; margin: 0 auto; box-shadow: 0 40px 80px rgba(139,92,246,0.30); border: 1.5px solid rgba(255,255,255,0.7);}
h1 {font-family: 'Outfit', sans-serif; font-weight: 900!important; font-size: 4.2rem!important; background: linear-gradient(100deg, #4c1d95 0%, #6b21a8 20%, #9333ea 40%, #a855f7 60%, #c084fc 80%, #6b21a8 100%); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 4s linear infinite;}
h2,h3,p,span,label,div,li {color: #111827!important; font-weight: 600!important;}
.subtitle {color: #6b7280!important; font-size: 1.15rem!important; font-weight: 500!important; margin-top: 4px!important; margin-bottom: 1.2rem!important;}
.tagline-badge {display: inline-block; padding: 8px 20px; background: linear-gradient(135deg, #9333ea 0%, #7e22ce 100%); color: #ffffff !important; font-weight: 800 !important; font-size: 1rem; border-radius: 24px; box-shadow: 0 8px 20px rgba(147, 51, 234, 0.4); margin-left: 14px;}
.logo-container {width: 100%; min-height: 350px; display: flex; align-items: center; justify-content: center;}
.logo-container img {width: 100%; max-width: 380px; height: auto; max-height: 380px; object-fit: contain; filter: drop-shadow(0 20px 40px rgba(147,51,234,0.3));}
.logo-float {animation: float 4s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-12px);}}
.pricing-card {border-radius: 26px; padding: 1.8rem; background: linear-gradient(145deg, rgba(255,255,255,0.98) 0%, rgba(250,245,255,0.95) 100%)!important; box-shadow: 0 12px 28px rgba(147,51,234,0.12); border: 2.5px solid #9333ea;}
.stButton>button {border-radius: 16px !important; font-weight: 800 !important; background: linear-gradient(100deg, #7e22ce 0%, #9333ea 30%, #a855f7 70%, #9333ea 100%) !important; color: white !important; border: none !important; padding: 14px 28px !important; width: 100% !important; box-shadow: 0 8px 24px rgba(147,51,234,0.45) !important;}
.pro-banner {background: linear-gradient(135deg, #4c1d95 0%, #6b21a8 15%, #7e22ce 35%, #9333ea 55%, #a855f7 75%, #d946ef 100%); padding: 1.8rem; border-radius: 24px; color: white!important; text-align: center; margin: 1.2rem 0;}
.pro-banner h2, .pro-banner div, .pro-banner span {color: white!important;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.95); padding: 10px 18px; border-radius: 28px; margin: 5px; border: 2px solid #9333ea; color: #000!important; font-weight: 700!important;}
.expiry-warning {background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important; border: 2.5px solid #ef4444 !important; border-radius: 18px; padding: 16px; margin-bottom: 20px; color: #991b1b !important; font-weight: 800 !important;}
.plan-status-box {padding: 14px 18px; border-radius: 16px; font-weight: 800 !important; margin-bottom: 14px;}
.plan-active {background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important; border: 2.5px solid #22c55e !important; color: #15803d !important;}
.plan-inactive {background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important; border: 2.5px solid #ef4444 !important; color: #b91c1c !important;}
.big-clean-box {background: linear-gradient(135deg, #faf5ff 0%, #f5f3ff 50%, #ede9fe 100%); padding: 28px; border-radius: 24px; border: 3px dashed #9333ea; margin: 20px 0; text-align: center; box-shadow: 0 12px 32px rgba(147,51,234,0.15);}
.feedback-card {background: rgba(255,255,255,0.9); border: 2px solid #e9d5ff; border-radius: 18px; padding: 18px; margin: 12px 0;}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! I'm VeriSame AI - International phone support! Upload file and click BIG CLEAN!"}]
if "changed_cells" not in st.session_state:
    st.session_state.changed_cells = set()
if "problem_cells" not in st.session_state:
    st.session_state.problem_cells = set()
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
for key in ['plan', 'email', 'df_clean', 'df_original', 'show_balloon', 'payment_clicked', 'amt', 'sample_loaded', 'email_entered', 'days', 'selected_plan', 'admin_approved', 'df_loaded', 'orig_len', 'empty_fixed', 'last_upload_sig', 'reset_announced', 'last_apply_msg', 'hub_report', 'clean_done']:
    if key not in st.session_state:
        if key in ['plan', 'email', 'df_clean', 'df_original', 'days', 'selected_plan', 'orig_len', 'empty_fixed', 'last_upload_sig', 'last_apply_msg', 'hub_report']:
            st.session_state[key] = None
        else:
            st.session_state[key] = False

def update_changed_cells():
    if st.session_state.df_original is None or st.session_state.df_clean is None:
        st.session_state.changed_cells = set()
        return
    orig_df = st.session_state.df_original.reset_index(drop=True)
    clean_df = st.session_state.df_clean.reset_index(drop=True)
    changed = set()
    min_rows = min(len(orig_df), len(clean_df))
    common_cols = [c for c in orig_df.columns if c in clean_df.columns]
    for col in common_cols:
        orig_vals = orig_df[col].iloc[:min_rows].fillna("").astype(str).values
        clean_vals = clean_df[col].iloc[:min_rows].fillna("").astype(str).values
        for idx in range(min_rows):
            if orig_vals[idx] != clean_vals[idx]:
                changed.add((idx, col))
    st.session_state.changed_cells = changed

def apply_cell_styling(df_to_style):
    df_temp = df_to_style.copy().reset_index(drop=True)
    def highlight_cells(data):
        df_colors = pd.DataFrame('', index=data.index, columns=data.columns)
        for row, col in st.session_state.get("changed_cells", set()):
            if row in df_colors.index and col in df_colors.columns:
                df_colors.at[row, col] = 'background-color: #bbf7d0; color: #047857; font-weight: bold; border: 1.5px solid #10b981;'
        for row, col in st.session_state.get("problem_cells", set()):
            if row in df_colors.index and col in df_colors.columns:
                df_colors.at[row, col] = 'background-color: #fecaca; color: #991b1b; font-weight: bold; border: 1.5px solid #ef4444;'
        return df_colors
    return df_temp.style.apply(highlight_cells, axis=None)

def render_feedback_front():
    st.markdown("---")
    st.markdown("### Feedback - Help Us Improve")
    fb_front = st.text_area("Write feedback", placeholder="Love VeriSame? Found bug?", key="fb_front", height=100, label_visibility="collapsed")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Send Feedback", key="fb_front_btn", type="primary", use_container_width=True):
            if fb_front.strip():
                if save_feedback(fb_front.strip(), st.session_state.get('email', 'Guest')):
                    st.success("Feedback sent! Thank you!")
                    st.balloons()
                else:
                    st.error("Failed")
            else:
                st.warning("Write something first")
    with col2:
        st.caption("No email shown, direct to database")

def render_feedback_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Feedback")
    fb_text = st.sidebar.text_area("Feedback", placeholder="Your feedback...", key="fb_text", height=80, label_visibility="collapsed")
    if st.sidebar.button("Send Feedback", key="fb_send", use_container_width=True):
        if fb_text.strip():
            if save_feedback(fb_text.strip(), st.session_state.get('email', 'Guest')):
                st.sidebar.success("Sent to owner!")
                st.sidebar.balloons()
            else:
                st.sidebar.error("Failed")
        else:
            st.sidebar.warning("Write something!")

def render_ai_chatbot(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### VeriSame AI Assistant")
    chat_html = "<div style='max-height: 300px; overflow-y: auto; padding: 14px; background: #ffffff !important; border: 2.5px solid #9333ea; border-radius: 18px; margin-bottom: 12px;'>"
    for chat in st.session_state.chat_history[-6:]:
        if chat["role"] == "assistant":
            chat_html = chat_html + f"<p style='color: #6b21a8 !important; margin: 8px 0;'><b>AI:</b> {chat['message']}</p>"
        else:
            chat_html = chat_html + f"<p style='color: #000000 !important; margin: 8px 0;'><b>You:</b> {chat['message']}</p>"
    chat_html = chat_html + "</div>"
    target.markdown(chat_html, unsafe_allow_html=True)
    s_id = "side" if is_sidebar else "main"
    user_msg = target.text_input("Ask", placeholder="How to clean? Pricing?", key=f"chat_in_{s_id}", label_visibility="collapsed")
    if target.button("Send Message", key=f"btn_send_chat_{s_id}", use_container_width=True):
        if user_msg and user_msg.strip():
            st.session_state.chat_history.append({"role": "user", "message": user_msg})
            system_prompt = "You are VeriSame AI, built by Anugya. International phone support."
            groq_reply = query_groq_ai(user_msg, system_instruction=system_prompt)
            reply = groq_reply if groq_reply else "I have 11 tools with international phone support! Upload file and click BIG CLEAN!"
            st.session_state.chat_history.append({"role": "assistant", "message": reply})
            st.rerun()

if st.session_state.email:
    db_state = load_db()
    user = db_state.get(st.session_state.email, {})
    st.sidebar.markdown(f"<div style='background: #f5f3ff; padding: 12px; border-radius: 14px; border: 2px solid #9333ea;'><b>{st.session_state.email}</b></div>", unsafe_allow_html=True)
    render_ai_chatbot(is_sidebar=True)
    render_feedback_sidebar()
    if user.get("plan"):
        if user.get("plan") == "pro" and user.get("expiry"):
            try:
                exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d").date()
                today = datetime.now().date()
                days_left = (exp_date - today).days
                if days_left > 180:
                    exact_days = 180 if user.get("amt") == PRO_6M else 30
                    exp_date = today + timedelta(days=exact_days)
                    user["expiry"] = exp_date.strftime("%Y-%m-%d")
                    user["days"] = exact_days
                    db_state[st.session_state.email] = user
                    save_db(db_state)
                if exp_date < today:
                    user["plan"] = "free"
                    user["status"] = "EXPIRED"
                    user["amt"] = 0
                    user["days"] = 0
                    db_state[st.session_state.email] = user
                    save_db(db_state)
                    st.sidebar.warning("PRO expired! Free now.")
            except:
                pass
        st.session_state.plan = user.get("plan")
        st.session_state.amt = user.get("amt", 0)
        if user.get("plan") == "pro" and user.get("status") == "PAID":
            try:
                exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d").date()
            except:
                exp_date = datetime.now().date() + timedelta(days=30)
            st.session_state["user_plan_price"] = user.get("amt", 299)
            st.session_state["expiry_date"] = exp_date
            PLANS = {299: {"label": "PRO 299", "total_days": 30}, 1499: {"label": "PRO 1499", "total_days": 180}}
            current_plan_price = st.session_state.get("user_plan_price", 299)
            plan_meta = PLANS.get(current_plan_price, PLANS[299])
            expiry_date = st.session_state.get("expiry_date", datetime.now().date() + timedelta(days=30))
            days_remaining = (expiry_date - datetime.now().date()).days
            st.session_state.admin_approved = days_remaining >= 0
            if days_remaining >= 0:
                st.sidebar.markdown("<div class='plan-status-box plan-active'>Pro Active</div>", unsafe_allow_html=True)
                st.sidebar.markdown(f"**{plan_meta['label']} ({plan_meta['total_days']} Days)**")
                st.sidebar.markdown(f"{days_remaining} Days Left")
                st.sidebar.markdown(f"Valid Till: {expiry_date.strftime('%Y-%m-%d')}")
                if days_remaining <= 5:
                    st.sidebar.markdown(f"<div class='expiry-warning'>Ends in {days_remaining} days! Renew!</div>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>Expired</div>", unsafe_allow_html=True)
        else:
            if user.get("status") == "PENDING":
                user_amt = user.get('amt', PRO_1M)
                chosen_plan = "PRO 299 (30 Days)" if user_amt == PRO_1M else "PRO 1499 (180 Days)"
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>Pending Approval</div>", unsafe_allow_html=True)
                st.sidebar.warning(f"{chosen_plan}\nWaiting for Admin")
            elif user.get("status") == "EXPIRED":
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>Expired - Free Now</div>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown("<div class='plan-status-box plan-inactive'>Free Plan</div>", unsafe_allow_html=True)
                st.sidebar.info("FREE - 200 Rows | 15s")

if st.session_state.plan or st.session_state.email_entered:
    st.sidebar.markdown("---")
    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        if st.button("Back", key="sidebar_back", use_container_width=True):
            st.session_state.selected_plan = None
            st.session_state.plan = None
            st.session_state.email_entered = False
            st.session_state.uploaded_files = {}
            st.session_state.clean_done = False
            st.rerun()
    with col_s2:
        if st.button("Logout", key="sidebar_logout", use_container_width=True):
            for key in ['plan', 'email', 'df_clean', 'df_original', 'payment_clicked', 'amt', 'sample_loaded', 'email_entered', 'days', 'selected_plan', 'admin_approved', 'df_loaded', 'orig_len', 'empty_fixed', 'last_upload_sig', 'reset_announced', 'last_apply_msg', 'hub_report', 'clean_done']:
                if key in ['plan', 'email', 'df_clean', 'df_original', 'days', 'selected_plan', 'orig_len', 'empty_fixed', 'last_upload_sig', 'last_apply_msg', 'hub_report']:
                    st.session_state[key] = None
                else:
                    st.session_state[key] = False
            st.session_state.changed_cells = set()
            st.session_state.problem_cells = set()
            st.session_state.uploaded_files = {}
            st.rerun()

col1, col2 = st.columns([1.5, 3.5])
with col1:
    st.markdown("""<div class="logo-container logo-float"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" alt="VeriSame Logo"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div style="margin-top: 35px;"><h1 style='margin-bottom: 0px; display: inline-block; vertical-align: middle;'>VeriSame</h1><span class="tagline-badge">Clean logic. Clear result</span><div class="subtitle">The Fastest Way to Clean Your Data - International Support</div></div>""", unsafe_allow_html=True)

st.markdown(f"<div class='pro-banner'><h2 style='margin:0; font-size:1.6rem;'>{T['pro_banner']}</h2><div style='margin-top:10px;'>{''.join([f'<span class=\"tool-chip\">{tool}</span>' for tool in ['Smart Date','AI Fill','Email AI','Phone International','Case AI','Symbol Clean','Header Clean','Fuzzy Dedup','Trim AI','Spell AI','Currency AI']])}</div><p style='margin-top:12px; font-size:0.95rem; opacity:0.9;'>Smart phone cleaning: India 10-digit, USA keeps country code - International ready</p></div>", unsafe_allow_html=True)

if "admin" in st.query_params:
    if st.query_params.get("admin") == ADMIN_PASS:
        st.title(T['admin_title'])
        data = load_db()
        feedbacks = load_feedback()
        tab_a1, tab_a2 = st.tabs([f"Users ({len(data)})", f"Feedbacks ({len(feedbacks)})"])
        with tab_a1:
            st.subheader(T['admin_pending'])
            if data:
                for email, info in list(data.items()):
                    if "@" not in email:
                        continue
                    amt = info.get('amt', 0)
                    status = info.get('status', 'PENDING')
                    plan_text = f"PRO 299" if amt == PRO_1M else f"PRO 1499" if amt == PRO_6M else "FREE"
                    c1, c2, c3 = st.columns([4, 2, 2])
                    with c1:
                        status_color = "PAID" if status == "PAID" else "PENDING" if status == "PENDING" else "EXPIRED"
                        st.markdown(f"""<div class='pricing-card'><b>Email:</b> {email}<br><b>Plan:</b> {plan_text}<br><b>Status:</b> {status_color}<br><b>Valid Till:</b> {info.get('expiry','N/A')}</div>""", unsafe_allow_html=True)
                    with c2:
                        if status in ["PENDING", "EXPIRED"] and info.get("plan") == "pro":
                            if st.button("Approve", key=f"verify_{email}", type="primary", use_container_width=True):
                                data[email]["status"] = "PAID"
                                data[email]["plan"] = "pro"
                                user_amt = data[email].get("amt", PRO_1M)
                                exact_days = 180 if user_amt == PRO_6M else 30
                                data[email]["amt"] = user_amt
                                data[email]["days"] = exact_days
                                data[email]["expiry"] = (datetime.now() + timedelta(days=exact_days)).strftime("%Y-%m-%d")
                                save_db(data)
                                st.success(f"{email} unlocked!")
                                st.balloons()
                                st.rerun()
                        else:
                            st.button("Active", key=f"active_{email}", disabled=True, use_container_width=True)
                    with c3:
                        if st.button("Delete", key=f"delete_{email}", use_container_width=True):
                            del data[email]
                            save_db(data)
                            st.rerun()
            else:
                st.info("No users yet")
        with tab_a2:
            st.subheader("User Feedbacks")
            if feedbacks:
                for fb in reversed(feedbacks[-20:]):
                    st.markdown(f"<div class='feedback-card'><b>From:</b> {fb['email']} | <b>Time:</b> {fb['time']}<br><b>Feedback:</b> {fb['feedback']}</div>", unsafe_allow_html=True)
            else:
                st.info("No feedbacks yet")
        st.stop()
    else:
        st.error("Unauthorized")
        st.stop()

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        st.markdown("<h2 style='text-align:center; margin-bottom:20px;'>Choose Plan - International Phone Support</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            st.markdown(f"""<div class='pricing-card'><h2>FREE FOREVER</h2><h1>FREE</h1><p>Lifetime - 200 Rows</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['free_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free", type="primary", use_container_width=True):
                st.session_state.selected_plan = "free"
                st.rerun()
        with col2:
            st.markdown(f"""<div class='pricing-card' style='border: 3.5px solid #9333ea;'><p>⭐ POPULAR</p><h2>1 MONTH</h2><h1>₹299</h1><p>30 Days - International</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro ₹299", key="btn_pro1", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"
                st.session_state.amt = PRO_1M
                st.session_state.days = 30
                st.rerun()
        with col3:
            st.markdown(f"""<div class='pricing-card'><h2>6 MONTHS</h2><h1>₹1499</h1><p>180 Days - International</p><div>{''.join([f'<p>✓ {f}</p>' for f in T['pro_feat']])}</div></div>""", unsafe_allow_html=True)
            if st.button("Get Pro+ ₹1499", key="btn_pro6", type="primary", use_container_width=True):
                st.session_state.selected_plan = "pro"
                st.session_state.amt = PRO_6M
                st.session_state.days = 180
                st.rerun()
        render_ai_chatbot(is_sidebar=False)
        render_feedback_front()
    else:
        st.markdown(f"<h2>Enter email for {st.session_state.selected_plan.upper()}</h2>", unsafe_allow_html=True)
        col_e1, col_e2, col_e3 = st.columns([1, 2, 1])
        with col_e2:
            email_input = st.text_input(T['email_label'], placeholder="your@email.com", key="email_input_main").lower().strip()
            c_left, c_right = st.columns(2)
            with c_left:
                if st.button(T['continue_btn'], key="btn_continue", type="primary", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        st.session_state.email = email_input
                        st.session_state.email_entered = True
                        data = load_db()
                        if st.session_state.selected_plan == "free":
                            exact_days = 36500
                            expiry = (datetime.now() + timedelta(days=36500)).strftime("%Y-%m-%d")
                            amt_val = 0
                            status_val = "PAID"
                        else:
                            exact_days = 180 if st.session_state.amt == PRO_6M else 30
                            expiry = (datetime.now() + timedelta(days=exact_days)).strftime("%Y-%m-%d")
                            amt_val = st.session_state.amt
                            status_val = "PENDING"
                        if email_input in data:
                            data[email_input]["plan"] = st.session_state.selected_plan
                            if st.session_state.selected_plan == "free":
                                data[email_input]["status"] = "PAID"
                                data[email_input]["amt"] = 0
                                data[email_input]["days"] = 36500
                                data[email_input]["expiry"] = expiry
                            else:
                                if data[email_input].get("status") != "PAID":
                                    data[email_input]["status"] = "PENDING"
                                    data[email_input]["amt"] = amt_val
                                    data[email_input]["days"] = exact_days
                                    data[email_input]["expiry"] = expiry
                            save_db(data)
                            st.session_state.plan = data[email_input]["plan"]
                            st.session_state.amt = data[email_input].get("amt", st.session_state.amt)
                            st.rerun()
                        else:
                            st.session_state.plan = st.session_state.selected_plan
                            data[email_input] = {"plan": st.session_state.selected_plan, "status": status_val, "amt": amt_val, "days": exact_days, "expiry": expiry, "created": str(datetime.now())}
                            save_db(data)
                            if st.session_state.selected_plan == "free":
                                st.balloons()
                            st.rerun()
                    else:
                        st.error("Enter valid email")
            with c_right:
                if st.button("Back to Plans", key="back_to_plans", use_container_width=True):
                    st.session_state.selected_plan = None
                    st.rerun()
        render_feedback_front()
        st.stop()
else:
    if st.session_state.email:
        db_state = load_db()
        u_info = db_state.get(st.session_state.email, {})
        if u_info.get("plan") == "pro" and u_info.get("status") == "PAID" and u_info.get("expiry"):
            try:
                e_date = datetime.strptime(u_info["expiry"], "%Y-%m-%d").date()
                rem_days = (e_date - datetime.now().date()).days
                if 0 <= rem_days <= 5:
                    st.markdown(f"""<div class="expiry-warning">Ends in {rem_days} days! Renew soon!</div>""", unsafe_allow_html=True)
            except:
                pass

    tab1, tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
    with tab1:
        file = st.file_uploader(T['upload_text'], type=["csv", "xlsx", "xls", "json"], accept_multiple_files=True, label_visibility="collapsed")
        if file:
            current_files = [f.name for f in file]
            sheet_selections = {}
            for f in file:
                if f.name.endswith((".xlsx", ".xls")):
                    try:
                        excel_file = pd.ExcelFile(f)
                        sheet_names = excel_file.sheet_names
                        selected_sheet = st.selectbox(f"Sheet for {f.name}", sheet_names, key=f"sheet_sel_{f.name}")
                        sheet_selections[f.name] = selected_sheet
                    except:
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
                        if st.session_state.plan == "free" and len(sub_df) > FREE_ROW_LIMIT:
                            sub_df = sub_df.iloc[:FREE_ROW_LIMIT].copy()
                            st.warning(f"Free: Only first {FREE_ROW_LIMIT} rows")
                        df_clean_init = sub_df.copy()
                        for col in df_clean_init.columns:
                            if df_clean_init[col].dtype != 'object':
                                df_clean_init[col] = df_clean_init[col].astype(object)
                        df_clean_init.drop_duplicates(inplace=True)
                        df_clean_init.reset_index(drop=True, inplace=True)
                        st.session_state.uploaded_files[f.name] = {"original": sub_df.copy().reset_index(drop=True), "clean": df_clean_init, "orig_len": len(sub_df), "empty_fixed": int(sub_df.isna().sum().sum()), "changed_cells": set(), "problem_cells": set()}
                    st.session_state.last_upload_sig = upload_sig
                    st.session_state.clean_done = False
                    st.session_state.hub_report = None
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    with tab2:
        if st.button(T['sample_btn'], use_container_width=True, type="primary"):
            sample_df = pd.DataFrame({"Date": ["12/5/2024", "", "15-03-2023", "44927"], "Name": [" RAHUL KUMAR ", "priya sharma", "AMIT SINGH", " anugya "], "Email": ["RAHUL@GMAIL.COM", "bad@gmai.com", "priya@email.com", "test@yaho.com"], "Phone": ["98765-43210", "+1 123-456-7890", "000123", "+91 9876543210"], "Salary": ["one hundred", "250", "two thousand five hundred", "50,000"]})
            df_clean = sample_df.copy()
            for col in df_clean.columns:
                if df_clean[col].dtype != 'object':
                    df_clean[col] = df_clean[col].astype(object)
            df_clean.drop_duplicates(inplace=True)
            df_clean.reset_index(drop=True, inplace=True)
            st.session_state.uploaded_files = {"sample_data.csv": {"original": sample_df.copy().reset_index(drop=True), "clean": df_clean, "orig_len": len(sample_df), "empty_fixed": int(sample_df.isna().sum().sum()), "changed_cells": set(), "problem_cells": set()}}
            st.session_state.last_upload_sig = None
            st.session_state.clean_done = False
            st.toast("Sample loaded! Click BIG CLEAN")
            st.rerun()

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        file_keys = list(st.session_state.uploaded_files.keys())
        st.markdown("### Your Files")
        col_sel1, col_sel2 = st.columns([3, 1])
        with col_sel1:
            selected_file = st.selectbox("Select file:", file_keys, key="active_file_selector", label_visibility="collapsed")
        with col_sel2:
            if st.button("Back / Clear", key="back_from_files", use_container_width=True):
                st.session_state.uploaded_files = {}
                st.session_state.last_upload_sig = None
                st.session_state.clean_done = False
                st.session_state.hub_report = None
                st.rerun()
        if st.session_state.plan == "free":
            st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.uploaded_files[selected_file]["clean"].iloc[:FREE_ROW_LIMIT]
            st.session_state.uploaded_files[selected_file]["original"] = st.session_state.uploaded_files[selected_file]["original"].iloc[:FREE_ROW_LIMIT]
        st.session_state.df_clean = st.session_state.uploaded_files[selected_file]["clean"]
        st.session_state.df_original = st.session_state.uploaded_files[selected_file]["original"]
        st.session_state.orig_len = len(st.session_state.df_original)
        st.session_state.empty_fixed = st.session_state.uploaded_files[selected_file]["empty_fixed"]
        st.session_state.problem_cells = st.session_state.uploaded_files[selected_file].get("problem_cells", set())
        update_changed_cells()
        st.session_state.df_loaded = True
        df_clean = st.session_state.df_clean
        orig_len = st.session_state.orig_len

        if not st.session_state.get("clean_done"):
            st.markdown("<div class='big-clean-box'>", unsafe_allow_html=True)
            st.markdown(f"### File Uploaded: {selected_file}")
            st.markdown(f"<p><b>{orig_len} rows</b> - Ready to clean with 11 Tools - International Phone Support</p>", unsafe_allow_html=True)
            st.markdown("<p>Click BIG CLEAN below. After cleaning, you will see 10 rows preview.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
            with col_c2:
                if st.button("BIG CLEAN - Fix Everything (International)", key="global_apply_btn", type="primary", use_container_width=True):
                    enforce_processing_delay()
                    df_curr = st.session_state.df_clean.copy()
                    st.session_state.problem_cells = set()
                    st.session_state.changed_cells = set()
                    hub_report = []
                    for col in df_curr.columns:
                        if df_curr[col].dtype != 'object':
                            df_curr[col] = df_curr[col].astype(object)
                    fixes = []
                    fixes.append(("Fuzzy Dedup", tool_8_advanced_fuzzy_dedup(df_curr)))
                    fixes.append(("Smart Date", tool_1_advanced_date_parser(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Fill Nulls", tool_2_advanced_fill_nulls(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Email Validator", tool_3_advanced_email_validator(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Phone International", tool_4_international_phone_formatter(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Case Converter", tool_5_advanced_case_converter(df_curr, st.session_state.changed_cells)))
                    fixes.append(("Remove Symbols", tool_6_advanced_remove_symbols(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Header Clean", tool_7_advanced_header_clean(df_curr)))
                    fixes.append(("Trim Spaces", tool_9_advanced_trim_spaces(df_curr, st.session_state.changed_cells)))
                    fixes.append(("Spell Check", tool_10_advanced_spell_check(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Currency Cleaner", tool_11_currency_cleaner(df_curr, st.session_state.problem_cells)))
                    for name, count in fixes:
                        if "Dedup" in name or "Header" in name:
                            if count:
                                hub_report.append(f"{name}: Removed {count}")
                            else:
                                hub_report.append(f"{name}: Already Clean")
                        else:
                            if count:
                                hub_report.append(f"{name}: Fixed {count} cells")
                            else:
                                hub_report.append(f"{name}: Already Clean")
                    st.session_state.df_clean = df_curr
                    update_changed_cells()
                    st.session_state["hub_report"] = hub_report
                    st.session_state["clean_done"] = True
                    st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.df_clean
                    st.session_state.uploaded_files[selected_file]["changed_cells"] = st.session_state.changed_cells
                    st.session_state.uploaded_files[selected_file]["problem_cells"] = st.session_state.problem_cells
                    st.success("Data Cleaned! International phone support done!")
                    st.balloons()
                    st.rerun()
        else:
            st.markdown(f"<h2>{T['summary_title']} - After Cleaning</h2>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric(T['rows'], orig_len)
            with c2:
                st.metric(T['clean'], len(df_clean))
            with c3:
                st.metric(T['dups'], max(0, orig_len-len(df_clean)))
            with c4:
                st.metric(T['empty'], st.session_state.empty_fixed)
            if st.session_state.get("hub_report"):
                st.markdown("#### What 11 Tools Fixed:")
                for report_line in st.session_state["hub_report"]:
                    st.write(report_line)
            st.markdown(f"<h3>Cleaned Preview - 10 Rows - International</h3>", unsafe_allow_html=True)
            styled_df = apply_cell_styling(df_clean.head(10))
            st.dataframe(styled_df, use_container_width=True, height=350)
            if st.button("Reset & Clean Again", type="secondary", use_container_width=True):
                if st.session_state.df_original is not None:
                    st.session_state.df_clean = st.session_state.df_original.copy()
                    for col in st.session_state.df_clean.columns:
                        if st.session_state.df_clean[col].dtype != 'object':
                            st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(object)
                    st.session_state.changed_cells = set()
                    st.session_state.problem_cells = set()
                    st.session_state["hub_report"] = None
                    st.session_state["clean_done"] = False
                    st.session_state.uploaded_files[selected_file]["clean"] = st.session_state.df_clean
                    st.session_state.uploaded_files[selected_file]["changed_cells"] = set()
                    st.session_state.uploaded_files[selected_file]["problem_cells"] = set()
                    st.rerun()

        if st.session_state.get("clean_done"):
            st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
            db_data = load_db()
            user_info = db_data.get(st.session_state.email, {})
            is_paid = user_info.get("status") == "PAID"
            if st.session_state.plan == "free":
                st.info("Free Preview: Cleaned! Download CSV. Pay Rs299 for Excel + PDF")
                col_dl1, col_dl2, col_dl3 = st.columns(3)
                with col_dl1:
                    csv = st.session_state.df_clean.to_csv(index=False).encode()
                    if st.download_button(T['download_csv'], csv, f"verisame_free_{selected_file}.csv", mime="text/csv", key="dl_csv_free_btn", use_container_width=True, type="primary"):
                        st.balloons()
                with col_dl2:
                    if st.button("Upgrade to Pro 299", key="upgrade_from_free", use_container_width=True):
                        st.session_state.selected_plan = "pro"
                        st.session_state.amt = PRO_1M
                        st.session_state.plan = None
                        st.rerun()
                with col_dl3:
                    if st.button("Clean Another File", key="back_after_clean_free", use_container_width=True):
                        st.session_state["clean_done"] = False
                        st.session_state.uploaded_files = {}
                        st.rerun()
            elif st.session_state.plan == "pro":
                if not is_paid:
                    st.warning("Pay to unlock download - File cleaned ready!")
                    default_amt_index = 0 if st.session_state.amt == PRO_1M else 1
                    selected_pay_plan = st.radio("Choose Plan:", ["Rs299 - 1 Month / 30 Days", "Rs1499 - 6 Months / 180 Days"], index=default_amt_index, horizontal=True, key="radio_pay_plan")
                    pay_amt = PRO_1M if "299" in selected_pay_plan else PRO_6M
                    st.session_state.amt = pay_amt
                    upi_pay_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={pay_amt}&cu=INR&tn=VeriSame{pay_amt}"
                    col_qr1, col_qr2 = st.columns([1, 1])
                    with col_qr1:
                        st.link_button(f"Pay Rs{pay_amt} via UPI", upi_pay_link, use_container_width=True, type="primary")
                        display_upi_qr(upi_pay_link, pay_amt)
                    with col_qr2:
                        st.markdown(f"<div style='background:white; padding:16px; border-radius:16px; border:2px solid #9333ea;'><h4>After Payment:</h4><p>1. Click I Paid<br>2. Admin approves<br>3. Balloons + Download</p><p>UPI: {UPI_ID}</p></div>", unsafe_allow_html=True)
                    c_pay1, c_pay2 = st.columns(2)
                    with c_pay1:
                        if st.button(T['paid_btn'].format(amount=pay_amt), key="btn_paid", type="primary", use_container_width=True):
                            st.session_state.payment_clicked = True
                            data = load_db()
                            selected_days = 180 if pay_amt == PRO_6M else 30
                            data[st.session_state.email] = {"plan": "pro", "amt": pay_amt, "days": selected_days, "expiry": (datetime.now() + timedelta(days=selected_days)).strftime("%Y-%m-%d"), "status": "PENDING"}
                            save_db(data)
                            st.balloons()
                            st.success("Request sent!")
                            st.rerun()
                    with c_pay2:
                        if st.button("Back to Plans", key="back_from_pay", use_container_width=True):
                            st.session_state.selected_plan = None
                            st.session_state.plan = None
                            st.rerun()
                    if st.session_state.get("payment_clicked"):
                        st.info(T['wait_approval'])
                else:
                    st.success("Download Ready! Pro Active!")
                    st.balloons()
                    col1, col2, col3 = st.columns(3)
                    csv = st.session_state.df_clean.to_csv(index=False).encode()
                    with col1:
                        if st.download_button(f"{T['download_csv']}", csv, f"verisame_pro_{selected_file}.csv", mime="text/csv", key="dl_csv_paid", use_container_width=True, type="primary"):
                            st.balloons()
                    with col2:
                        if openpyxl is not None:
                            excel = io.BytesIO()
                            st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                            excel.seek(0)
                            if st.download_button(f"{T['download_excel']}", excel.getvalue(), f"verisame_pro_{selected_file}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_paid", use_container_width=True):
                                st.balloons()
                    with col3:
                        pdf_data = generate_pdf_report(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean)
                        if pdf_data:
                            if st.download_button("Audit PDF", pdf_data, f"verisame_audit_{selected_file}.pdf", mime="application/pdf", key="dl_pdf_paid", use_container_width=True):
                                st.balloons()
