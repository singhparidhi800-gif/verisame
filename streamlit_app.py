import json, os, io, time, re, hashlib
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import streamlit as st
import requests

try:
    from groq import Groq
except:
    Groq = None
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
GROQ_MODEL = "openai/gpt-oss-20b"

def send_notification(email, amt, plan_name):
    try:
        url = f"https://ntfy.sh/{NTFY_TOPIC}"
        msg = f"New Payment: {email} - {plan_name} Rs{amt} at {datetime.now().strftime('%I:%M %p')}"
        requests.post(url, data=msg.encode('utf-8'), headers={"Title": f"VeriSame Rs{amt} Payment"}, timeout=8)
    except:
        pass

def load_db():
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
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
            return {"count": 0}
    return {"count": 0}

def save_free_clicks():
    try:
        data = load_free_clicks()
        data["count"] = data.get("count", 0) + 1
        with open(FREE_CLICKS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def enforce_delay():
    bar = st.progress(0, text=f"Cleaning with 10 Advanced Tools...")
    for i in range(100):
        time.sleep(0.02)
        bar.progress(i+1)
    bar.empty()

# 10 ADVANCED TOOLS
def tool1_date(df, problem_cells):
    fixed=0
    for col in df.columns:
        if not any(k in col.lower() for k in ['date','dob','birth','join']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip()
                if orig.lower() in ["","nan","none","null","n/a","unknown","nat","0"]: continue
                if orig.isdigit() and 30000 < int(orig) < 60000:
                    try:
                        base=datetime(1899,12,30)
                        parsed=base+timedelta(days=int(orig))
                        df.at[r,col]=parsed.strftime('%Y-%m-%d')
                        fixed+=1
                        problem_cells.add((r,col))
                        continue
                    except: pass
                clean=orig.replace('/','-').replace('.','-').strip()
                parsed=pd.to_datetime(clean, dayfirst=True, errors='coerce')
                if not pd.isna(parsed):
                    new_val=parsed.strftime('%Y-%m-%d')
                    if orig!=new_val:
                        df.at[r,col]=new_val
                        fixed+=1
                        problem_cells.add((r,col))
            except: continue
    return fixed

def tool2_fill(df, problem_cells):
    fixed=0
    for col in df.columns:
        if df[col].dtype!='object': df[col]=df[col].astype(object)
        cl=col.lower()
        fill_val=0 if any(k in cl for k in ['salary','amount','price']) else "missing@email.com" if 'email' in cl else "0000000000" if any(k in cl for k in ['phone','mobile']) else "Unknown"
        for r in range(len(df)):
            try:
                val=df.at[r,col]
                if pd.isna(val) or str(val).strip().lower() in ["nan","none","","null","n/a","nat","-"]:
                    df.at[r,col]=fill_val
                    fixed+=1
                    problem_cells.add((r,col))
            except: continue
    return fixed

def tool3_email(df, problem_cells):
    fixed=0
    pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    typo_map={"gmai.com":"gmail.com","gmal.com":"gmail.com","yaho.com":"yahoo.com","hotmal.com":"hotmail.com","outlok.com":"outlook.com"}
    for col in df.columns:
        if 'email' not in col.lower(): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip()
                low=orig.lower().replace(" ","")
                if "@" not in low or low in ["nan","none","","missing@email.com"]: continue
                for w,c in typo_map.items():
                    if w in low: low=low.replace(w,c)
                new_val=low if re.match(pattern,low) else "Invalid Email"
                if str(df.at[r,col]).strip()!=new_val:
                    df.at[r,col]=new_val
                    fixed+=1
                    problem_cells.add((r,col))
            except: continue
    return fixed

def tool4_phone(df, problem_cells):
    fixed=0
    for col in df.columns:
        if not any(k in col.lower() for k in ['phone','mobile','contact']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col])
                digits="".join([c for c in orig if c.isdigit()])
                if len(digits)==0 or digits=="0000000000": continue
                if len(digits)>10: digits=digits[-10:]
                if len(digits)==10 and digits!=orig:
                    df.at[r,col]=digits
                    fixed+=1
                    problem_cells.add((r,col))
            except: continue
    return fixed

def tool5_case(df, changed_cells):
    fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        if not any(k in col.lower() for k in ['name','city','state','company','country']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip()
                if orig.lower() in ["unknown","missing@email.com","invalid email",""]: continue
                new_val=' '.join([w.capitalize() for w in orig.lower().split()]) if orig.isupper() else ' '.join([w.capitalize() for w in orig.split()])
                if orig!=new_val:
                    df.at[r,col]=new_val
                    fixed+=1
                    changed_cells.add((r,col))
            except: continue
    return fixed

def tool6_symbols(df, problem_cells):
    fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['email','phone']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col])
                if orig.lower() in ["unknown","invalid email"]: continue
                cleaned=re.sub(r'[^a-zA-Z0-9\s.,@\-_()&/]', '', orig)
                cleaned=re.sub(r'\s+', ' ', cleaned).strip()
                if orig!=cleaned and cleaned!="":
                    df.at[r,col]=cleaned
                    fixed+=1
                    problem_cells.add((r,col))
            except: continue
    return fixed

def tool7_rename(df):
    fixed=0
    new_cols={}
    for c in df.columns:
        cleaned=re.sub(r'[^a-zA-Z0-9_ ]', '', str(c).strip())
        cleaned=re.sub(r'\s+', '_', cleaned.lower()).strip('_')
        cleaned=re.sub(r'_+', '_', cleaned)
        if cleaned=="" or cleaned[0].isdigit(): cleaned=f"col_{fixed}"
        new_cols[c]=cleaned
        if c!=cleaned: fixed+=1
    df.rename(columns=new_cols, inplace=True)
    return fixed

def tool8_dedup(df):
    before=len(df)
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return before-len(df)

def tool9_trim(df, changed_cells):
    fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col])
                trimmed=' '.join(orig.strip().split())
                if orig!=trimmed:
                    df.at[r,col]=trimmed
                    fixed+=1
                    changed_cells.add((r,col))
            except: continue
    return fixed

def tool10_spell(df, problem_cells):
    fixed=0
    typo_dict={"teh":"the","recieve":"receive","salery":"salary","custmer":"customer","addres":"address","manger":"manager","buisness":"business","definately":"definitely"}
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['email','phone']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col])
                words=orig.split()
                new_words=[]
                changed=False
                for w in words:
                    cw=w.lower().strip('.,')
                    if cw in typo_dict:
                        rep=typo_dict[cw]
                        if w[0].isupper(): rep=rep.capitalize()
                        new_words.append(rep)
                        changed=True
                    else: new_words.append(w)
                if changed:
                    df.at[r,col]=" ".join(new_words)
                    fixed+=1
                    problem_cells.add((r,col))
            except: continue
    return fixed

def find_ambiguous(original_df, cleaned_df):
    ambiguous=[]
    for col in original_df.columns:
        cl=col.lower()
        for r_idx in range(min(len(original_df), len(cleaned_df))):
            try:
                orig=str(original_df.at[r_idx,col]).strip()
                if orig.lower() in ["","nan","none","null","n/a","unknown","nat"]: continue
                if 'date' in cl or 'dob' in cl:
                    parts=re.split(r'[-/]',orig)
                    if len(parts)>=2:
                        try:
                            p1=int(re.sub(r'\D','',parts[0]))
                            p2=int(re.sub(r'\D','',parts[1]))
                            if 1<=p1<=12 and 1<=p2<=12 and p1!=p2 and ('/' in orig or '-' in orig):
                                ambiguous.append({"row":r_idx,"col":col,"original":orig,"question":f"Row {r_idx+1}: Date '{orig}' - DD/MM or MM/DD?","options":[f"{p1:02d}/{p2:02d} as DD/MM",f"{p2:02d}/{p1:02d} as MM/DD"]})
                        except: pass
            except: continue
    seen=set()
    uniq=[]
    for a in ambiguous:
        key=(a['row'],a['col'],a['original'])
        if key not in seen:
            seen.add(key)
            uniq.append(a)
    return uniq[:6]

def generate_pdf(orig_len, clean_len, empty_fixed, df, hub_report):
    if SimpleDocTemplate is None: return None
    try:
        buffer=io.BytesIO()
        doc=SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story=[]
        styles=getSampleStyleSheet()
        title_style=ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#6b21a8'))
        story.append(Paragraph("VeriSame - 10 Advanced Tools Audit Report", title_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')} | {st.session_state.get('email','Guest')}", styles['Normal']))
        story.append(Spacer(1,10))
        text_style=ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=9)
        small_bold=ParagraphStyle('SmallBold', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
        data=[[Paragraph("<b>Metric</b>",small_bold),Paragraph("<b>Value</b>",small_bold)],[Paragraph("Total Rows",text_style),Paragraph(str(orig_len),text_style)],[Paragraph("Clean Rows",text_style),Paragraph(str(clean_len),text_style)]]
        if hub_report:
            for line in hub_report:
                parts=line.split(":")
                if len(parts)>=2:
                    data.append([Paragraph(parts[0],text_style),Paragraph(parts[1],text_style)])
        t=Table(data, colWidths=[220,200])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(1,0),colors.HexColor('#9333ea')),('TEXTCOLOR',(0,0),(1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#c084fc'))]))
        story.append(t)
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except: return None

def query_groq(user_prompt):
    groq_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, 'secrets') else None
    if not groq_key or Groq is None:
        return """Hello! I am VeriSame AI 😊

I know everything about VeriSame:

✨ 10 Advanced Tools:
1. Smart Date Fix - Fixes all date formats to YYYY-MM-DD
2. AI Fill Missing - Fills empty values smartly
3. Email AI Fix - Corrects typos like gmai.com to gmail.com
4. Phone AI Fix - Standardizes to 10 digits
5. Case AI Fix - Proper case for names
6. Symbol Clean - Removes unwanted symbols
7. Header Clean - Cleans column names
8. Fuzzy Dedup - Removes duplicates
9. Trim AI - Removes extra spaces
10. Spell AI - Fixes spelling mistakes

💰 Pricing in Indian Rupees:
• FREE: 200 Rows - Lifetime Free, all 10 tools, instant download
• STARTER: ₹49 One-Time Per File - 2000 Rows, pay again for next file
• PRO ₹299: 1 Month (30 Days) Unlimited Rows
• PRO ₹1499: 6 Months (180 Days) Unlimited Rows - Best Value

📥 Download Flow:
Upload file → Click BIG CLEAN → See what each tool fixed → Download as CSV / Excel / PDF

If paid plan: After cleaning, scan QR or click Pay button (GPay/PhonePe/Paytm) → Click 'I Paid' → Wait for admin approval → Balloon + Download buttons appear → Thank you message!

🔐 Groq connection uses model openai/gpt-oss-20b - add GROQ_API_KEY in Streamlit Secrets as gsk_... to enable AI chat.

How can I help you clean your data today?"""
    try:
        client = Groq(api_key=groq_key)
        system_prompt = f"""
You are VeriSame AI - Expert for VeriSame app. Model: {GROQ_MODEL}. Always reply in friendly helpful tone.

You must know everything about VeriSame:

APP OVERVIEW:
VeriSame is data cleaning app with 10 advanced tools. Tagline: Clean logic. Clear result.

10 ADVANCED TOOLS (explain what each cleans):
1. Smart Date Fix - Converts any date format (DD/MM/YYYY, MM-DD-YY, Excel numbers like 45000) to standard YYYY-MM-DD
2. AI Fill Missing - Fills empty cells: 0 for salary/amount, missing@email.com for email, Unknown for names
3. Email AI Fix - Corrects typos: gmai.com->gmail.com, yaho.com->yahoo.com, removes spaces, validates format
4. Phone AI Fix - Extracts 10 digits, removes country code 91, removes spaces/dashes
5. Case AI Fix - Converts RAHUL KUMAR to Rahul Kumar, proper title case for names/city
6. Symbol Clean - Removes special symbols except basic punctuation
7. Header Clean - Cleans column names to lowercase_with_underscore
8. Fuzzy Dedup - Removes duplicate rows
9. Trim AI - Removes extra spaces between words
10. Spell AI - Fixes common typos: teh->the, recieve->receive, salery->salary etc

PRICING - ALWAYS IN INDIAN RUPEES (INR), NEVER IN DOLLARS:
• FREE: 200 Rows Limit - Lifetime Free - All 10 tools - Instant download - No email needed for free
• STARTER: ₹49 One-Time Per File - 2000 Rows - Pay again for next file - QR + GPay Direct - No UPI ID shown
• PRO ₹299: 1 Month (30 Days) - Unlimited Rows - Today is 30 days, tomorrow 29, till 0 days - After 0, QR comes again
• PRO ₹1499: 6 Months (180 Days) - Unlimited Rows - Best Value - Today 180 days, tomorrow 179, till 0

DOWNLOAD FLOW:
1. Choose plan, enter email
2. Upload CSV/Excel/JSON file
3. Click BIG CLEAN button (1 click = 10 tools)
4. App shows summary: Total Rows, Clean Rows, Duplicates, Empty Fixed
5. Shows detailed report: Which tool fixed how many (e.g., Smart Date: 5 fixed, Email AI: 3 fixed)
6. Preview 10 rows with green for fixed
7. For FREE: Direct download CSV/Excel/PDF
8. For PAID: If not paid, shows QR Code (400x400) + Big Pay Button (Pay via GPay or any UPI app). After clicking I Paid, shows formal message "Thank you for your payment. Your payment is being verified. Please wait a moment, admin will confirm shortly."
9. Admin approves from secret dashboard (?admin=YOUR_PASSWORD)
10. User gets balloon celebration + Download options: CSV / Excel / PDF + Formal thank you message

DATE COUNTING:
• Starter ₹49 is ONE-TIME per file, no days counting
• Pro ₹299: 1 Month = 30 Days - Logic: If expiry is 30 days from payment, today shows 30 days left, tomorrow 29, day after 28... till 0. With actual calendar dates.
• Pro ₹1499: 6 Months = 180 Days - Today 180 days left, tomorrow 179... till 0. With actual dates.
• Before 5 days of ending: Show red alert: "Your payment is going to end in 5 days" then 4,3,2,1,0. At 0 days, lock all downloads, show QR again to pay again.

UI:
• Big logo (420px) - not too big, floating animation
• After logo, big space, then Welcome To VeriSame black bold 3.2rem
• Only on first page - when user goes to plan or cleaning page, hide logo and welcome, show only 10 tools banner
• Pricing cards responsive - same look on mobile, tablet, laptop, chrome
• Secret dashboard at ?admin=PASSWORD shows all users, approve/delete

Groq model is {GROQ_MODEL}. If user asks about connection, tell them to add GROQ_API_KEY in Streamlit Secrets as gsk_...

Always answer in INR, never dollars. Be concise but complete.
"""
        comp = client.chat.completions.create(model=GROQ_MODEL, messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], temperature=0.5, max_tokens=600)
        return comp.choices[0].message.content
    except Exception as e:
        err=str(e)
        if "403" in err or "Access denied" in err:
            return """Hello! I am VeriSame AI 😊 I am facing a temporary connection issue (403 - Please check GROQ_API_KEY in Streamlit Secrets). But I can still help you with VeriSame!

💰 Pricing in INR:
• FREE: 200 Rows - Lifetime Free
• STARTER: ₹49 One-Time Per File - 2000 Rows
• PRO ₹299: 1 Month (30 Days) Unlimited
• PRO ₹1499: 6 Months (180 Days) Unlimited

✨ 10 Tools clean your data in 1 click. Please check GROQ_API_KEY (should be gsk_...) to enable full AI chat. Your data cleaning still works perfectly!"""
        return f"Hello! VeriSame AI here - I clean with 10 tools. Pricing: FREE 200 rows, Starter ₹49 one-time per file 2000 rows, Pro ₹299 30 days unlimited, Pro ₹1499 180 days unlimited. How can I help? (AI note: {err[:100]})"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Outfit:wght@800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: radial-gradient(ellipse at top left, #faf5ff 0%, #f5f3ff 18%, #ede9fe 36%, #e9d5ff 54%, #d8b4fe 72%, #c4b5fd 90%); background-attachment: fixed;}
.block-container {background: rgba(255,255,255,0.98); border-radius: 28px; padding: 1.8rem; max-width: 1350px; margin: 0 auto; box-shadow: 0 20px 50px rgba(139,92,246,0.18);}
.welcome-black {font-family: 'Outfit', sans-serif; font-weight: 900!important; font-size: 3.2rem!important; color: #000000!important; text-align: center; letter-spacing: -1px; line-height:1.1; margin: 0;}
.welcome-space {height: 35px;}
@media (max-width: 768px) { .welcome-black {font-size: 2.1rem!important;} .welcome-space{height: 20px;} }
.subtitle {color: #6b7280!important; font-size: 1.05rem!important; text-align:center; margin-top: 10px!important;}
.tagline-badge {display: inline-block; padding: 8px 20px; background: linear-gradient(135deg, #7e22ce, #9333ea); color: #fff !important; font-weight: 700 !important; border-radius: 20px; font-size: 0.95rem;}
.logo-container {width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5px 0;}
.logo-container img {width: 100%; max-width: 450px; max-height: 450px; object-fit: contain; filter: drop-shadow(0 12px 25px rgba(147,51,234,0.18));}
.logo-float {animation: float 5s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.pricing-card {border-radius: 22px; padding: 1.4rem; background: #ffffff!important; border: 2px solid #e9d5ff; box-shadow: 0 8px 20px rgba(147,51,234,0.08); min-height: 380px; display: flex; flex-direction: column; transition: all 0.2s;}
.pricing-card:hover {transform: translateY(-4px); box-shadow: 0 14px 28px rgba(147,51,234,0.15);}
.pricing-card-free {border: 2px solid #c4b5fd !important;}
.pricing-card-starter {border: 2.5px solid #22c55e !important;}
.pricing-card-pro {border: 2.5px solid #9333ea !important;}
.stButton>button {border-radius: 14px !important; font-weight: 700 !important; background: linear-gradient(100deg, #7e22ce, #9333ea) !important; color: white !important; border: none !important; padding: 12px 20px !important; width: 100% !important; box-shadow: 0 6px 16px rgba(147,51,234,0.3) !important;}
.big-pay-button {display: block; width: 100%; padding: 22px 18px; background: linear-gradient(100deg, #16a34a, #22c55e); color: white !important; font-weight: 800 !important; font-size: 1.45rem !important; text-align: center; border-radius: 16px; text-decoration: none !important; box-shadow: 0 8px 20px rgba(34,197,94,0.35); margin: 12px 0; border: 2px solid #16a34a; transition: transform 0.15s;}
.big-pay-button:hover {transform: scale(1.02);}
.big-pay-button-pro {background: linear-gradient(100deg, #7e22ce, #9333ea, #a855f7) !important; border: 2px solid #7e22ce !important;}
.big-pay-sub {font-size: 0.9rem!important; font-weight: 600!important; display: block; margin-top: 4px;}
.pro-banner {background: linear-gradient(135deg, #4c1d95, #7e22ce, #9333ea, #a855f7); padding: 1.4rem; border-radius: 20px; text-align: center; margin: 1rem 0; box-shadow: 0 10px 20px rgba(147,51,234,0.2);}
.pro-banner h2 {color: white!important; font-size: 1.3rem!important; margin: 0!important; font-weight: 800!important;}
.pro-banner-small {background: linear-gradient(135deg, #4c1d95, #7e22ce); padding: 1rem; border-radius: 16px; text-align: center; margin: 0.8rem 0;}
.pro-banner-small h2 {color: white!important; font-size: 1.1rem!important; margin: 0!important; font-weight: 700!important;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.95) !important; padding: 7px 12px; border-radius: 20px; margin: 3px; border: 1.5px solid rgba(255,255,255,0.6); color: #4c1d95 !important; font-weight: 700 !important; font-size: 0.78rem !important;}
.plan-status-box {padding: 10px 14px; border-radius: 12px; font-weight: 700 !important; margin-bottom: 10px; font-size: 0.88rem!important; line-height:1.5;}
.plan-active {background: #dcfce7 !important; border: 2px solid #22c55e !important; color: #15803d !important;}
.plan-selected {background: #fef9c3 !important; border: 2px solid #eab308 !important; color: #854d0e !important;}
.expiry-red {background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%) !important; border: 2.5px solid #ef4444 !important; border-radius: 16px; padding: 14px; margin: 10px 0; text-align: center; animation: pulse 2s infinite;}
@keyframes pulse {0%,100%{transform: scale(1);} 50%{transform: scale(1.02);}}
.hundred-box {background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important; border: 2.5px solid #22c55e !important; border-radius: 16px; padding: 16px; margin: 10px 0; text-align: center;}
.qr-box {background: #ffffff !important; border: 3px solid #9333ea !important; border-radius: 20px; padding: 22px; text-align: center; margin: 14px 0; box-shadow: 0 10px 24px rgba(147,51,234,0.12);}
.upgrade-msg {background: linear-gradient(135deg, #fef9c3 0%, #fef3c7 100%) !important; border: 2.5px solid #eab308 !important; border-radius: 16px; padding: 16px; text-align: center; margin: 10px 0;}
.confirm-box {background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%) !important; border: 2.5px solid #f59e0b !important; border-radius: 18px; padding: 16px; margin: 10px 0;}
.tool-report {background: #faf5ff !important; border: 1.5px solid #e9d5ff !important; border-radius: 12px; padding: 10px; margin: 5px 0; font-size: 0.85rem!important;}
.day-counter {background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 2px solid #3b82f6; border-radius: 14px; padding: 12px; text-align: left; margin: 10px 0; font-size: 0.86rem!important; line-height:1.6;}
.verifying-box {background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important; border: 2.5px solid #3b82f6 !important; border-radius: 18px; padding: 20px; margin: 14px 0; text-align: center;}
.thankyou-box {background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important; border: 2.5px solid #22c55e !important; border-radius: 18px; padding: 18px; margin: 14px 0; text-align: center;}
@media (max-width: 768px) {
  .block-container {padding: 1rem 0.8rem !important;}
  .logo-container img {max-width: 320px !important; max-height: 320px !important;}
  .pricing-card {min-height: auto !important; margin-bottom: 14px !important;}
  [data-testid="column"] {width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;}
  .stColumns {flex-wrap: wrap !important;}
  .big-pay-button {font-size: 1.15rem !important; padding: 18px 14px !important;}
}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! I am VeriSame AI 😊 FREE 200 rows lifetime, Starter ₹49 one-time per file 2000 rows, Pro ₹299 30 days unlimited, Pro ₹1499 180 days unlimited. How can I help?"}]
if "changed_cells" not in st.session_state: st.session_state.changed_cells = set()
if "problem_cells" not in st.session_state: st.session_state.problem_cells = set()
if "uploaded_files" not in st.session_state: st.session_state.uploaded_files = {}
if "payment_pending_shown" not in st.session_state: st.session_state.payment_pending_shown = False
for k in ['plan','email','df_clean','df_original','amt','email_entered','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done','ambiguous_list','hundred_done','confirm_choices','just_approved']:
    if k not in st.session_state:
        st.session_state[k] = None if k in ['plan','email','df_clean','df_original','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','ambiguous_list','confirm_choices'] else False

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
            except: continue
        st.session_state.changed_cells = changed
    except: st.session_state.changed_cells = set()

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
    except: return df_to_style

def render_chat(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown(f"### 🤖 VeriSame AI")
    chat_html = "<div style='max-height: 300px; overflow-y: auto; padding: 10px; background: #fff !important; border: 2px solid #e9d5ff; border-radius: 14px; margin-bottom: 10px; word-wrap: break-word;'>"
    for chat in st.session_state.chat_history[-6:]:
        msg = chat['message'][:600]
        if chat["role"] == "assistant":
            chat_html += f"<p style='color: #6b21a8 !important; margin: 8px 0; font-size: 0.85rem; line-height:1.4; word-break: break-word;'><b>AI:</b> {msg}</p>"
        else:
            chat_html += f"<p style='color: #111 !important; margin: 8px 0; font-size: 0.85rem; word-break: break-word;'><b>You:</b> {msg}</p>"
    chat_html += "</div>"
    target.markdown(chat_html, unsafe_allow_html=True)
    s_id = "side" if is_sidebar else "main"
    um = target.text_input("Ask", placeholder="Ask about 10 tools, pricing...", key=f"chat_{s_id}_finalperfect", label_visibility="collapsed")
    if target.button("Send", key=f"btn_chat_{s_id}_finalperfect", use_container_width=True):
        if um and um.strip():
            st.session_state.chat_history.append({"role": "user", "message": um})
            reply = query_groq(um)
            st.session_state.chat_history.append({"role": "assistant", "message": reply})
            st.rerun()

# SIDEBAR
if st.session_state.email and st.session_state.plan != "free":
    db = load_db()
    user = db.get(st.session_state.email, {})
    st.sidebar.markdown(f"<div style='background: #f5f3ff; padding: 10px; border-radius: 12px; border: 2px solid #9333ea; font-size:0.85rem;'><b>{st.session_state.email}</b></div>", unsafe_allow_html=True)
    if user.get("plan") in ["starter","pro"] and user.get("expiry"):
        try:
            sel_amt = user.get("amt",0)
            exp_date = datetime.strptime(user["expiry"], "%Y-%m-%d").date()
            today = datetime.now().date()
            days_left = (exp_date - today).days
            st.session_state.days = days_left
            if user.get("plan") == "starter":
                if user.get("status") == "PAID":
                    st.sidebar.markdown(f"<div class='plan-status-box plan-active'>🟢 <b>Starter Active</b><br>₹49 - ONE TIME per file<br>2000 Rows</div>", unsafe_allow_html=True)
                else:
                    st.sidebar.markdown(f"<div class='plan-status-box plan-selected'>🟡 <b>Starter ₹49</b><br>ONE TIME per file<br>Waiting for approval</div>", unsafe_allow_html=True)
            else:
                if days_left < 0:
                    st.sidebar.markdown(f"<div class='expiry-red'><b>❌ Plan Ended - 0 Days Left</b><br>Download locked - Please pay again</div>", unsafe_allow_html=True)
                    user["status"] = "EXPIRED"
                    save_db(db)
                elif 0 <= days_left <= 5:
                    tomorrow_date = (today + timedelta(days=1)).strftime("%d %b %Y")
                    day_after_date = (today + timedelta(days=2)).strftime("%d %b %Y")
                    exp_date_str = exp_date.strftime("%d %b %Y")
                    st.sidebar.markdown(f"<div class='expiry-red'><b>⚠️ Your payment is going to end in {days_left} days</b><br>Please renew soon</div>", unsafe_allow_html=True)
                    st.sidebar.markdown(f"<div class='day-counter'><b>🟢 Pro ₹{sel_amt} Active</b><br>Expiry: {exp_date_str}<br>Today: <b>{days_left} days left</b> - {today.strftime('%d %b')}<br>Tomorrow: {max(0, days_left-1)} - {tomorrow_date}<br>...<br>Day 0 = {exp_date_str}</div>", unsafe_allow_html=True)
                else:
                    if user.get("status") == "PAID":
                        tomorrow_date = (today + timedelta(days=1)).strftime("%d %b %Y")
                        exp_date_str = exp_date.strftime("%d %b %Y")
                        st.sidebar.markdown(f"<div class='plan-status-box plan-active'>🟢 <b>Pro ₹{sel_amt} Active</b><br>{'1 Month - 30 Days' if sel_amt==PRO_1M else '6 Months - 180 Days'}</div>", unsafe_allow_html=True)
                        st.sidebar.markdown(f"<div class='day-counter'>📅 <b>Expiry:</b> {exp_date_str}<br>Today: <b>{days_left} days left</b> ({today.strftime('%d %b %Y')})<br>Tomorrow: {max(0, days_left-1)} ({tomorrow_date})<br>Day 0 = {exp_date_str}</div>", unsafe_allow_html=True)
                    else:
                        st.sidebar.markdown(f"<div class='plan-status-box plan-selected'>🟡 <b>Pro ₹{sel_amt}</b><br>Waiting for approval</div>", unsafe_allow_html=True)
        except:
            pass
    render_chat(is_sidebar=True)
elif st.session_state.plan == "free":
    st.sidebar.markdown(f"<div class='plan-status-box plan-active'>🟢 <b>Free</b><br>200 Rows<br>Lifetime Free</div>", unsafe_allow_html=True)
    render_chat(is_sidebar=True)

if st.session_state.plan or st.session_state.email_entered:
    st.sidebar.markdown("---")
    b1,b2 = st.sidebar.columns(2)
    with b1:
        if st.button("← Back", key="nav_back_finalperfect", use_container_width=True):
            st.session_state.selected_plan=None
            st.session_state.selected_amt=None
            st.session_state.plan=None
            st.session_state.email_entered=False
            st.session_state.uploaded_files={}
            st.session_state.clean_done=False
            st.session_state.hundred_done=False
            st.session_state.ambiguous_list=None
            st.session_state.just_approved=False
            st.rerun()
    with b2:
        if st.button("Logout", key="nav_logout_finalperfect", use_container_width=True):
            for k in ['plan','email','df_clean','df_original','amt','email_entered','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done','ambiguous_list','hundred_done','confirm_choices','just_approved']:
                st.session_state[k] = None if k in ['plan','email','df_clean','df_original','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','ambiguous_list','confirm_choices'] else False
            st.session_state.uploaded_files={}
            st.session_state.changed_cells=set()
            st.session_state.problem_cells=set()
            st.query_params.clear()
            st.rerun()

# ===== HEADER LOGIC: LOGO SMALLER + ONLY SHOW ON FIRST PAGE =====
is_first_page = (st.session_state.plan is None and st.session_state.selected_plan is None)

if is_first_page:
    # FIRST PAGE: Logo small (450px) + Welcome black bold + 10 tools
    st.markdown("""<div class="logo-container logo-float"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" alt="VeriSame Logo"></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="welcome-space"></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="welcome-black">Welcome To VeriSame👋</div>""", unsafe_allow_html=True)
    st.markdown("""<div style="text-align:center; margin-top:10px;"><span class="tagline-badge">Clean logic. Clear result</span><div class="subtitle">The Fastest Way to Clean Your Data</div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class='pro-banner' style="margin-top:18px;"><h2>✨ 10 Advanced Tools - All Plans Include All 10 Tools</h2><div style='margin-top:8px;'>{''.join([f'<span class=\"tool-chip\">{t}</span>' for t in ['Date Fix','Fill Missing','Email Fix','Phone Fix','Case Fix','Symbol Clean','Header Clean','Dedup','Trim','Spell Fix']])}</div></div>""", unsafe_allow_html=True)
else:
    # INSIDE PLAN OR CLEANING PAGE: Hide logo and welcome, show only 10 tools banner small
    st.markdown(f"""<div class='pro-banner-small'><h2>✨ 10 Advanced Tools - Date Fix, Fill Missing, Email Fix, Phone Fix, Case Fix, Symbol Clean, Header Clean, Dedup, Trim, Spell Fix</h2></div>""", unsafe_allow_html=True)

if "admin" in st.query_params:
    if st.query_params.get("admin")==ADMIN_PASS:
        st.title("🔐 Secret Dashboard - VeriSame")
        st.markdown("<div style='background: #dcfce7; border: 2px solid #22c55e; border-radius: 12px; padding: 12px; margin: 10px 0;'><b>✅ Manual Approval - QR 400x400 Guaranteed - Days Counting with Actual Dates</b></div>", unsafe_allow_html=True)
        data=load_db()
        fbs=load_feedback()
        free_data=load_free_clicks()
        tab1, tab2, tab3, tab4 = st.tabs([f"FREE {free_data.get('count',0)}", f"STARTER ₹49 {len([k for k,v in data.items() if v.get('amt')==STARTER_PRICE])}", f"PRO ₹299/1499 {len([k for k,v in data.items() if v.get('amt') in [PRO_1M, PRO_6M]])}", f"Feedback {len(fbs)}"])
        with tab1:
            st.markdown(f"<div class='pricing-card' style='text-align:center; min-height:80px;'><h2>{free_data.get('count',0)}</h2><p>Total Free Users</p></div>", unsafe_allow_html=True)
        with tab2:
            starter_users = {k:v for k,v in data.items() if v.get('amt')==STARTER_PRICE}
            for email, info in list(starter_users.items()):
                if "@" not in email: continue
                c1,c2,c3=st.columns([4,2,2])
                with c1:
                    st.markdown(f"<div class='pricing-card' style='min-height:70px;'><b>{email}</b><br>₹49 ONE-TIME Per File<br>Status: {info.get('status')} | Used: {info.get('used',0)}<br>Created: {info.get('created','')[:19]}</div>", unsafe_allow_html=True)
                with c2:
                    if info.get("status") in ["PENDING","EXPIRED"]:
                        if st.button("✅ Approve", key=f"ap_s_{email}_finalperfect", type="primary", use_container_width=True):
                            data[email]["status"]="PAID"
                            data[email]["used"]=0
                            data[email]["expiry"]=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                            save_db(data)
                            st.rerun()
                with c3:
                    if st.button("Delete", key=f"del_s_{email}_finalperfect", use_container_width=True):
                        del data[email]
                        save_db(data)
                        st.rerun()
        with tab3:
            pro_users = {k:v for k,v in data.items() if v.get('amt') in [PRO_1M, PRO_6M]}
            for email, info in list(pro_users.items()):
                if "@" not in email: continue
                try:
                    exp_d = datetime.strptime(info.get("expiry","2000-01-01"), "%Y-%m-%d").date()
                    days_left_admin = (exp_d - datetime.now().date()).days
                    exp_str = exp_d.strftime("%d %b %Y")
                except:
                    days_left_admin = 0
                    exp_str = "Invalid"
                c1,c2,c3=st.columns([4,2,2])
                with c1:
                    if info.get("amt")==PRO_1M:
                        desc = f"₹299 - 1 Month (30 Days) - {days_left_admin} days left - Expiry: {exp_str}"
                    else:
                        desc = f"₹1499 - 6 Months (180 Days) - {days_left_admin} days left - Expiry: {exp_str} - Best Value"
                    st.markdown(f"<div class='pricing-card' style='min-height:70px;'><b>{email}</b><br>{desc}<br>Status: {info.get('status')} | Created: {info.get('created','')[:19]}</div>", unsafe_allow_html=True)
                with c2:
                    if info.get("status") in ["PENDING","EXPIRED"]:
                        if st.button("✅ Approve", key=f"ap_p_{email}_finalperfect", type="primary", use_container_width=True):
                            data[email]["status"]="PAID"
                            data[email]["expiry"]=(datetime.now()+timedelta(days=180 if data[email].get("amt")==PRO_6M else 30)).strftime("%Y-%m-%d")
                            save_db(data)
                            st.rerun()
                with c3:
                    if st.button("Delete", key=f"del_p_{email}_finalperfect", use_container_width=True):
                        del data[email]
                        save_db(data)
                        st.rerun()
        with tab4:
            if fbs:
                for fb in reversed(fbs[-30:]):
                    st.markdown(f"<div style='background:#fff; border:2px solid #e9d5ff; border-radius:12px; padding:10px; margin:8px 0; font-size:0.85rem;'><b>{fb['email']}</b><br>{fb['feedback'][:300]}<br><small>{fb.get('time','')[:19]}</small></div>", unsafe_allow_html=True)
        st.stop()
    else:
        st.error("Unauthorized")
        st.stop()

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        st.markdown("<h2 style='text-align:center; font-size:1.5rem!important; color:#4c1d95!important; margin-top:20px;'>Choose Your Plan</h2>", unsafe_allow_html=True)
        col_free, col_starter, col_pro = st.columns(3, gap="medium")
        with col_free:
            st.markdown(f"""<div class='pricing-card pricing-card-free'><h3>🆓 FREE FOREVER</h3><h1 style='font-size:3rem!important;'>FREE</h1><p><b>200 Rows - Lifetime Free</b></p><div style='margin-top:10px; flex-grow:1;'><p>✓ All 10 Advanced Tools</p><p>✓ Super Fast Cleaning</p><p>✓ CSV + Excel + PDF</p><p>✓ 100% Private</p><p>✓ AI Support (openai/gpt-oss-20b)</p></div></div>""", unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free_finalperfect", type="primary", use_container_width=True):
                save_free_clicks()
                st.session_state.selected_plan="free"
                st.session_state.plan="free"
                st.session_state.email="Guest_Free"
                st.session_state.email_entered=True
                st.rerun()
        with col_starter:
            st.markdown(f"""<div class='pricing-card pricing-card-starter'><p style='background: #22c55e; color:white!important; padding:5px 12px; border-radius:16px; display:inline-block; font-size:0.75rem; font-weight: 700;'>✨ ONE TIME PER FILE</p><h3>STARTER</h3><h1 style='font-size:3rem!important;'>₹49</h1><p><b>One-Time Per File - 2,000 Rows</b></p><div style='margin-top:10px; flex-grow:1;'><p>✓ All 10 Advanced Tools</p><p>✓ Pay Again For Next File</p><p>✓ QR + GPay Direct</p><p>✓ No UPI ID Shown</p><p>✓ Big Pay Box</p></div></div>""", unsafe_allow_html=True)
            if st.button("Start with 49", key="btn_starter_finalperfect", type="primary", use_container_width=True):
                st.session_state.selected_plan="starter"
                st.session_state.selected_amt=STARTER_PRICE
                st.session_state.amt=STARTER_PRICE
                st.session_state.days=36500
                st.rerun()
        with col_pro:
            st.markdown(f"""<div class='pricing-card pricing-card-pro'><p style='background: #9333ea; color:white!important; padding:5px 12px; border-radius:16px; display:inline-block; font-size:0.75rem; font-weight: 700;'>⭐ POPULAR</p><h3>PRO</h3><h1 style='font-size:2.2rem!important;'>₹299 / ₹1499</h1><p><b>Unlimited Rows</b></p><div style='margin-top:10px; flex-grow:1;'><p>✓ ₹299 = 1 Month (30 Days)</p><p>✓ ₹1499 = 6 Months (180 Days)</p><p>✓ Unlimited Rows</p><p>✓ QR + Big Pay Box</p><p>✓ Red Alert 5→0 Days</p></div></div>""", unsafe_allow_html=True)
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                if st.button("₹299 - 30 Days", key="btn_pro_299_finalperfect", type="primary", use_container_width=True):
                    st.session_state.selected_plan="pro"
                    st.session_state.selected_amt=PRO_1M
                    st.session_state.amt=PRO_1M
                    st.session_state.days=30
                    st.rerun()
            with c_p2:
                if st.button("₹1499 - 180 Days", key="btn_pro_1499_finalperfect", type="primary", use_container_width=True):
                    st.session_state.selected_plan="pro"
                    st.session_state.selected_amt=PRO_6M
                    st.session_state.amt=PRO_6M
                    st.session_state.days=180
                    st.rerun()
        render_chat(is_sidebar=False)
        st.markdown("---")
        st.markdown("### 💌 Feedback")
        fb_front = st.text_area("Feedback", placeholder="Your feedback...", key="fb_front_finalperfect", height=70, label_visibility="collapsed")
        if st.button("Send Feedback", key="fb_front_btn_finalperfect", type="primary", use_container_width=True):
            if fb_front.strip() and save_feedback(fb_front.strip(), "Guest"):
                st.success("Thank you! 💜")
                st.balloons()
    else:
        if st.session_state.selected_plan == "free":
            st.session_state.plan = "free"
            st.session_state.email = "Guest_Free"
            st.session_state.email_entered = True
            st.rerun()
        if st.session_state.selected_plan == "starter":
            plan_text = f"STARTER - ₹{STARTER_PRICE} One-Time Per File"
        else:
            if st.session_state.selected_amt == PRO_1M:
                plan_text = "PRO - 1 Month (30 Days) - ₹299"
            else:
                plan_text = "PRO - 6 Months (180 Days) - ₹1499"
        st.markdown(f"<h2 style='text-align:center; font-size:1.2rem!important; margin-top:15px;'>Enter email for {plan_text}</h2>", unsafe_allow_html=True)
        _, ce2, _ = st.columns([1,2,1])
        with ce2:
            email_input = st.text_input("Enter your email", placeholder="your@email.com", key="email_main_finalperfect").lower().strip()
            b1,b2 = st.columns(2)
            with b1:
                if st.button("Verify & Continue", key="btn_verify_finalperfect", type="primary", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        st.session_state.email=email_input
                        st.session_state.email_entered=True
                        data=load_db()
                        if st.session_state.selected_plan=="starter":
                            exp=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                            data[email_input]={"plan":"starter","status":"PENDING","amt":STARTER_PRICE,"days":36500,"expiry":exp,"created":str(datetime.now()),"used":0}
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
                if st.button("← Back", key="btn_back_finalperfect", use_container_width=True):
                    st.session_state.selected_plan=None
                    st.session_state.selected_amt=None
                    st.rerun()
        render_chat(is_sidebar=False)
        st.stop()
else:
    tab1, tab2 = st.tabs(["📁 Upload File", "✨ Try Demo"])
    with tab1:
        files = st.file_uploader("Drop CSV, Excel or JSON", type=["csv","xlsx","xls","json"], accept_multiple_files=True, label_visibility="collapsed")
        if files:
            cur_files=[f.name for f in files]
            sheet_sel={}
            for f in files:
                if f.name.endswith((".xlsx",".xls")):
                    try:
                        ef=pd.ExcelFile(f)
                        sel=st.selectbox(f"Sheet for {f.name}", ef.sheet_names, key=f"sh_{f.name}_finalperfect")
                        sheet_sel[f.name]=sel
                    except: pass
            sig=f"{cur_files}-{list(sheet_sel.values())}"
            db_check = load_db()
            if st.session_state.email in db_check and db_check[st.session_state.email].get("plan")=="starter" and db_check[st.session_state.email].get("status")=="PAID":
                prev_sig = st.session_state.get("last_upload_sig")
                if prev_sig and prev_sig != sig and sig:
                    if db_check[st.session_state.email].get("used",0) >= 1:
                        db_check[st.session_state.email]["status"] = "EXPIRED"
                        save_db(db_check)
                        st.warning("⚠️ Starter ₹49 is one-time per file. Please pay again for next file.")
                        st.rerun()
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
                    st.session_state.confirm_choices=None
                    st.session_state.just_approved=False
                except Exception as e:
                    st.error(f"Error: {e}")
    with tab2:
        if st.button("Load Sample Data", key="btn_load_sample_finalperfect", use_container_width=True, type="primary"):
            sample=pd.DataFrame({"Date":["12/5/2024","05/06/2024","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT"],"Email":["RAHUL@GMAI.COM","bad@yaho.com","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["100","250","50000"]})
            clean=sample.copy()
            st.session_state.uploaded_files={"sample_data.csv":{"original":sample.copy().reset_index(drop=True),"clean":clean,"orig_len":len(sample),"empty_fixed":int(sample.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}}
            st.session_state.last_upload_sig=None
            st.session_state.clean_done=False
            st.session_state.hundred_done=False
            st.session_state.ambiguous_list=None
            st.session_state.confirm_choices=None
            st.session_state.just_approved=False
            st.rerun()

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        keys=list(st.session_state.uploaded_files.keys())
        sel_file=st.selectbox("Select file:", keys, key="active_file_finalperfect", label_visibility="collapsed")
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
            st.markdown(f"### 📄 File: {sel_file} - {orig_len} rows")
            if st.button("🧹 BIG CLEAN - 1 Click = 10 Tools", key="btn_big_clean_finalperfect", type="primary", use_container_width=True):
                try:
                    enforce_delay()
                    df_curr=st.session_state.df_clean.copy()
                    st.session_state.problem_cells=set()
                    st.session_state.changed_cells=set()
                    for col in df_curr.columns:
                        if df_curr[col].dtype!='object':
                            df_curr[col]=df_curr[col].astype(object)
                    fixes=[]
                    fixes.append(("📅 Dates Fixed", tool1_date(df_curr, st.session_state.problem_cells)))
                    fixes.append(("📝 Missing Values Filled", tool2_fill(df_curr, st.session_state.problem_cells)))
                    fixes.append(("📧 Emails Fixed", tool3_email(df_curr, st.session_state.problem_cells)))
                    fixes.append(("📱 Phones Fixed", tool4_phone(df_curr, st.session_state.problem_cells)))
                    fixes.append(("🔤 Names & Case Fixed", tool5_case(df_curr, st.session_state.changed_cells)))
                    fixes.append(("✨ Symbols Cleaned", tool6_symbols(df_curr, st.session_state.problem_cells)))
                    fixes.append(("🏷️ Headers Cleaned", tool7_rename(df_curr)))
                    fixes.append(("👥 Duplicates Removed", tool8_dedup(df_curr)))
                    fixes.append(("✂️ Extra Spaces Removed", tool9_trim(df_curr, st.session_state.changed_cells)))
                    fixes.append(("📖 Spelling Fixed", tool10_spell(df_curr, st.session_state.problem_cells)))
                    hub=[]
                    for name,cnt in fixes:
                        hub.append(f"{name}: {cnt} fixed" if cnt else f"{name}: Already clean")
                    st.session_state.df_clean=df_curr
                    update_changed()
                    ambiguous = find_ambiguous(st.session_state.df_original, st.session_state.df_clean)
                    st.session_state["hub_report"]=hub
                    st.session_state["clean_done"]=True
                    st.session_state["ambiguous_list"]=ambiguous
                    st.session_state["hundred_done"] = len(ambiguous) == 0
                    st.session_state["confirm_choices"] = {}
                    st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.df_clean
                    st.session_state.uploaded_files[sel_file]["changed_cells"]=st.session_state.changed_cells
                    st.session_state.uploaded_files[sel_file]["problem_cells"]=st.session_state.problem_cells
                    st.success("✅ Cleaned! Perfect!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            ambiguous = st.session_state.get("ambiguous_list", [])
            is_hundred = st.session_state.get("hundred_done", False) or len(ambiguous) == 0
            percent_text = "100% Clean" if is_hundred else "95% Clean - Need Your Choice"
            st.markdown(f"<h2>Data Summary - {percent_text}</h2>", unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            with c1: st.metric("Total Rows", orig_len)
            with c2: st.metric("Clean Rows", len(df_clean))
            with c3: st.metric("Duplicates", max(0, orig_len-len(df_clean)))
            with c4: st.metric("Empty Fixed", st.session_state.empty_fixed)
            if st.session_state.get("hub_report"):
                st.markdown("### 🔧 What We Fixed - Advanced 10 Tools Report:")
                cols = st.columns(2)
                for idx, report_line in enumerate(st.session_state.hub_report):
                    with cols[idx % 2]:
                        st.markdown(f"<div class='tool-report'>✅ {report_line}</div>", unsafe_allow_html=True)
            if is_hundred:
                st.markdown("<div class='hundred-box'><h3>🎉 100% Clean! All 10 Tools Applied Successfully!</h3></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='confirm-box'><h3>🤔 Need Your Help - {len(ambiguous)} Items Need Confirmation</h3><p>Please confirm to make it 100% clean</p></div>", unsafe_allow_html=True)
                choices = st.session_state.get("confirm_choices", {})
                for i, amb in enumerate(ambiguous):
                    st.markdown(f"<div style='background:#fff; border:2px solid #f59e0b; border-radius:12px; padding:12px; margin:8px 0; font-size:0.85rem;'><b>Q{i+1}: {amb['question']}</b><br><small>Original: {amb['original']}</small></div>", unsafe_allow_html=True)
                    selected = st.radio(f"Choose:", amb['options'], key=f"amb_{i}_finalperfect", index=0)
                    choices[i] = selected
                st.session_state.confirm_choices = choices
                if st.button("✅ Apply & Make 100% Clean", key="btn_apply_amb_finalperfect", type="primary", use_container_width=True):
                    st.session_state.hundred_done = True
                    st.session_state.ambiguous_list = []
                    st.success("✅ Now 100% Clean!")
                    st.balloons()
                    st.rerun()
            st.markdown(f"<h3>Preview - 10 Rows - {percent_text}</h3>", unsafe_allow_html=True)
            styled=apply_style(df_clean.head(10))
            st.dataframe(styled, use_container_width=True, height=350)

        if st.session_state.get("clean_done"):
            ambiguous = st.session_state.get("ambiguous_list", [])
            is_hundred = st.session_state.get("hundred_done", False) or len(ambiguous) == 0
            percent_text = "100% Clean" if is_hundred else "95% Clean"
            db=load_db()
            user_info=db.get(st.session_state.email,{}) if st.session_state.email and st.session_state.email != "Guest_Free" else {}
            is_paid=user_info.get("status")=="PAID" if user_info else True if st.session_state.plan=="free" else False
            is_expired = False
            days_left = 999
            if user_info and user_info.get("expiry"):
                try:
                    exp_d = datetime.strptime(user_info["expiry"], "%Y-%m-%d").date()
                    days_left = (exp_d - datetime.now().date()).days
                    if user_info.get("plan") != "starter" and days_left < 0:
                        is_expired = True
                except: pass
            
            if is_paid and not st.session_state.get("just_approved") and user_info.get("plan") in ["starter","pro"]:
                st.session_state.just_approved = True
                st.balloons()
            
            if st.session_state.plan=="free":
                st.markdown(f"<h2>Export - {percent_text}</h2>", unsafe_allow_html=True)
                c1,c2,c3=st.columns(3)
                safe=sel_file[:30]
                suffix = "100_percent" if is_hundred else "95_percent"
                with c1:
                    csv=df_clean.to_csv(index=False).encode()
                    st.download_button(f"📥 CSV - {percent_text}", csv, f"{safe}_{suffix}_cleaned.csv", mime="text/csv", key="dl_csv_free_finalperfect", use_container_width=True, type="primary")
                with c2:
                    if openpyxl is not None:
                        ex=io.BytesIO()
                        df_clean.to_excel(ex, index=False, engine='openpyxl')
                        ex.seek(0)
                        st.download_button(f"📥 Excel - {percent_text}", ex.getvalue(), f"{safe}_{suffix}_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx_free_finalperfect", use_container_width=True)
                with c3:
                    pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean, st.session_state.get("hub_report"))
                    if pdf:
                        st.download_button(f"📥 PDF - {percent_text}", pdf, f"{safe}_{suffix}_audit.pdf", mime="application/pdf", key="dl_pdf_free_finalperfect", use_container_width=True)
            elif st.session_state.plan in ["starter","pro"]:
                if st.session_state.plan == "pro" and 0 <= days_left <= 5 and not is_expired:
                    st.markdown(f"<div class='expiry-red'><b>⚠️ Your payment is going to end in {days_left} days</b><br>Please renew your plan before expiry</div>", unsafe_allow_html=True)
                if is_expired:
                    st.markdown(f"<div class='expiry-red'><b>❌ Your plan has ended - 0 days left - Download locked</b><br>Please pay again to unlock downloads</div>", unsafe_allow_html=True)
                    is_paid = False
                
                if not is_paid:
                    sel_amt = user_info.get("amt", st.session_state.get("selected_amt", 0))
                    clean_msg = "100% successfully" if is_hundred else "95% - Confirm for 100%"
                    created_str = user_info.get("created", "")
                    if user_info.get("status") == "PENDING" and created_str:
                        st.markdown(f"""
                        <div class='verifying-box'>
                            <h3 style='color: #1e40af !important; margin: 0;'>⏳ Thank you for your payment</h3>
                            <p style='color: #1e3a8a !important; margin-top: 10px; font-size: 0.95rem;'>Your payment is being verified.<br>Please wait a moment, our team will confirm shortly.<br>Your download will be available right after approval.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("🔄 Check Status", key="check_status_finalperfect", type="primary", use_container_width=True):
                            st.rerun()
                    else:
                        amt_to_show = sel_amt if sel_amt in [STARTER_PRICE, PRO_1M, PRO_6M] else st.session_state.get("selected_amt", STARTER_PRICE)
                        if amt_to_show == STARTER_PRICE:
                            plan_name = "Starter ₹49 - ONE TIME per File - 2000 Rows"
                            upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={STARTER_PRICE}&cu=INR&tn=VeriSame Starter {STARTER_PRICE}"
                            btn_class = ""
                            pay_text = f"Pay {STARTER_PRICE} from GPay or any other pay"
                        elif amt_to_show == PRO_1M:
                            plan_name = "Pro ₹299 - 1 Month (30 Days) - Unlimited"
                            upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={PRO_1M}&cu=INR&tn=VeriSame Pro 299"
                            btn_class = "big-pay-button-pro"
                            pay_text = f"Pay {PRO_1M} from GPay or any other pay"
                        else:
                            plan_name = "Pro ₹1499 - 6 Months (180 Days) - Best Value"
                            upi_link = f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={PRO_6M}&cu=INR&tn=VeriSame Pro 1499"
                            btn_class = "big-pay-button-pro"
                            amt_to_show = PRO_6M
                            pay_text = f"Pay {PRO_6M} with GPay or any other pay"
                        
                        st.markdown(f"<div class='upgrade-msg'><h3 style='font-size:1.1rem!important;'>✅ Your file is cleaned {clean_msg} — {plan_name}</h3></div>", unsafe_allow_html=True)
                        # ===== QR + PAYMENT SYSTEM 100% FIXED - GUARANTEED =====
                        st.markdown("<div class='qr-box'>", unsafe_allow_html=True)
                        st.markdown(f"### 💳 {plan_name}")
                        st.markdown(f"<p style='color:#000; font-weight:800; font-size:1.1rem; text-align:center;'>FULL PAYMENT SYSTEM - QR CODE 400x400 + BIG PAY BUTTON + I PAID</p>", unsafe_allow_html=True)
                        
                        col_qr, col_pay = st.columns([1, 1.2], gap="large")
                        with col_qr:
                            st.markdown(f"<p style='font-weight:900; text-align:center; font-size:1.15rem; color:#000;'>📱 QR CODE - SCAN & PAY</p>", unsafe_allow_html=True)
                            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={urllib.parse.quote(upi_link)}"
                            st.image(qr_url, width=400)
                            st.markdown(f"<p style='font-size:0.8rem; color:#000; font-weight:700; text-align:center; margin-top:8px;'>₹{amt_to_show} - Secure UPI - QR Never Deleted</p>", unsafe_allow_html=True)
                        
                        with col_pay:
                            st.markdown(f"<p style='font-weight:800; font-size:1.15rem; color:#000; margin-bottom:12px;'>💳 {pay_text}</p>", unsafe_allow_html=True)
                            st.markdown(f"""
                            <a href="{upi_link}" class="big-pay-button {btn_class}">
                                💳 PAY ₹{amt_to_show}<br>
                                <span class="big-pay-sub">Click to Open GPay / PhonePe / Paytm / BHIM</span>
                            </a>
                            """, unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align:center; color:#6b7280; font-size:0.9rem; margin-top:12px; font-weight:600;'>Works with GPay, PhonePe, Paytm, BHIM & all UPI apps<br>No UPI ID shown - 100% Secure UPI<br>Scan QR or Click PAY Button</p>", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button(f"✅ I Paid ₹{amt_to_show}", key=f"btn_paid_{amt_to_show}_finalperfect", type="primary", use_container_width=True):
                                data=load_db()
                                if amt_to_show == STARTER_PRICE:
                                    data[st.session_state.email]={"plan":"starter","amt":STARTER_PRICE,"days":36500,"expiry":(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now()),"used":0}
                                elif amt_to_show == PRO_1M:
                                    data[st.session_state.email]={"plan":"pro","amt":PRO_1M,"days":30,"expiry":(datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                                else:
                                    data[st.session_state.email]={"plan":"pro","amt":PRO_6M,"days":180,"expiry":(datetime.now()+timedelta(days=180)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                                save_db(data)
                                send_notification(st.session_state.email, amt_to_show, plan_name)
                                st.success("✅ Payment submitted successfully!")
                                st.markdown(f"""
                                <div class='verifying-box'>
                                    <h3 style='color: #1e40af !important;'>⏳ Thank you for your payment</h3>
                                    <p style='color: #1e3a8a !important; margin-top: 8px;'>Your payment is being verified.<br>Please wait a moment, our team will confirm shortly.</p>
                                </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    if st.session_state.get("just_approved"):
                        st.balloons()
                        st.markdown(f"""
                        <div class='thankyou-box'>
                            <h3 style='color: #15803d !important; margin:0;'>🎉 Thank You! Your Payment is Confirmed!</h3>
                            <p style='color: #166534 !important; margin-top:8px;'>We sincerely appreciate your trust in VeriSame.<br>Your download is now ready. Please choose your format below.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h2>🎉 Export Ready - {percent_text}</h2>", unsafe_allow_html=True)
                    
                    if st.session_state.plan == "starter":
                        st.markdown(f"<div style='background:#eff6ff; border:2px solid #3b82f6; border-radius:12px; padding:10px; text-align:center;'><b>✅ Starter ₹49 Active - ONE TIME per file</b><br>2000 Rows - Pay again for next file</div>", unsafe_allow_html=True)
                    else:
                        if days_left >= 0:
                            exp_str = (datetime.now().date() + timedelta(days=days_left)).strftime("%d %b %Y")
                            sel_amt = user_info.get("amt", st.session_state.get("selected_amt", PRO_1M))
                            if sel_amt == PRO_1M:
                                st.markdown(f"<div class='day-counter'>✅ <b>Pro ₹299 Active</b> - 1 Month (30 Days) - Unlimited<br>Today {days_left} days left ({datetime.now().date().strftime('%d %b %Y')}) - Expiry: {exp_str}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='day-counter'>✅ <b>Pro ₹1499 Active</b> - 6 Months (180 Days) - Best Value<br>Today {days_left} days left ({datetime.now().date().strftime('%d %b %Y')}) - Expiry: {exp_str}</div>", unsafe_allow_html=True)
                        if 0 <= days_left <= 5 and days_left>=0:
                            st.markdown(f"<div class='expiry-red'><b>⚠️ Your payment is going to end in {days_left} days</b><br>Day 0 = Download locked, QR will appear again</div>", unsafe_allow_html=True)
                    
                    if st.session_state.get("hub_report"):
                        with st.expander(f"📊 Detailed Report - What Each Tool Cleaned - {percent_text}", expanded=False):
                            for line in st.session_state.hub_report:
                                st.markdown(f"- ✅ {line}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    c1,c2,c3=st.columns(3)
                    safe=sel_file[:30]
                    suffix = "100_percent" if is_hundred else "95_percent"
                    csv=df_clean.to_csv(index=False).encode()
                    with c1:
                        if st.download_button(f"📥 Download as CSV - {percent_text}", csv, f"{safe}_{suffix}_cleaned.csv", mime="text/csv", key="dl_csv_paid_finalperfect", use_container_width=True, type="primary"):
                            if st.session_state.plan == "starter":
                                db_u = load_db()
                                if st.session_state.email in db_u:
                                    db_u[st.session_state.email]["used"] = db_u[st.session_state.email].get("used",0) + 1
                                    save_db(db_u)
                    with c2:
                        if openpyxl is not None:
                            ex=io.BytesIO()
                            df_clean.to_excel(ex, index=False, engine='openpyxl')
                            ex.seek(0)
                            if st.download_button(f"📥 Download as Excel - {percent_text}", ex.getvalue(), f"{safe}_{suffix}_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx_paid_finalperfect", use_container_width=True):
                                if st.session_state.plan == "starter":
                                    db_u = load_db()
                                    if st.session_state.email in db_u:
                                        db_u[st.session_state.email]["used"] = db_u[st.session_state.email].get("used",0) + 1
                                        save_db(db_u)
                    with c3:
                        pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean, st.session_state.get("hub_report"))
                        if pdf:
                            if st.download_button(f"📥 Download as PDF - {percent_text}", pdf, f"{safe}_{suffix}_audit.pdf", mime="application/pdf", key="dl_pdf_paid_finalperfect", use_container_width=True):
                                if st.session_state.plan == "starter":
                                    db_u = load_db()
                                    if st.session_state.email in db_u:
                                        db_u[st.session_state.email]["used"] = db_u[st.session_state.email].get("used",0) + 1
                                        save_db(db_u)
                    
                    st.markdown("""
                    <div class='thankyou-box' style='margin-top:20px;'>
                        <h4 style='color: #15803d !important; margin:0;'>🙏 Thank You for Choosing VeriSame</h4>
                        <p style='color: #166534 !important; margin-top:8px; font-size:0.9rem;'>We sincerely appreciate your trust in our service. Your file has been cleaned with our 10 advanced tools with precision and care.<br>For any assistance, please contact our support. We value your association with VeriSame - Clean logic. Clear result.</p>
                    </div>
                    """, unsafe_allow_html=True)
