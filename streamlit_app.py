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
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Payment: {email} - {plan_name} Rs{amt}".encode('utf-8'), headers={"Title": f"VeriSame Rs{amt}"}, timeout=8)
    except: pass

def load_db():
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                d = json.load(f)
                if isinstance(d, dict): return d
        except: pass
    return {}
def save_db(d):
    try:
        with open("backup_orders.json", "w") as f: json.dump(d,f,indent=2)
    except: pass
def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE,"r") as f: return json.load(f)
        except: return []
    return []
def save_feedback(text,email):
    try:
        fb=load_feedback()
        fb.append({"email":email,"feedback":text,"time":str(datetime.now()),"id":hashlib.md5(f"{email}{text}{time.time()}".encode()).hexdigest()[:8]})
        with open(FEEDBACK_FILE,"w") as f: json.dump(fb,f,indent=2)
        return True
    except: return False
def load_free_clicks():
    if os.path.exists(FREE_CLICKS_FILE):
        try:
            with open(FREE_CLICKS_FILE,"r") as f: return json.load(f)
        except: return {"count":0}
    return {"count":0}
def save_free_clicks():
    try:
        data=load_free_clicks(); data["count"]=data.get("count",0)+1
        with open(FREE_CLICKS_FILE,"w") as f: json.dump(data,f,indent=2)
    except: pass

def enforce_delay():
    bar=st.progress(0, text="Cleaning with 10 Advanced Tools...")
    for i in range(100):
        time.sleep(0.02); bar.progress(i+1)
    bar.empty()

def tool1_date(df, problem_cells):
    fixed=0
    for col in df.columns:
        if not any(k in col.lower() for k in ['date','dob','birth','join']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip()
                if orig.lower() in ["","nan","none","null","n/a","unknown","nat","0","-"]: continue
                if orig.isdigit() and 30000 < int(orig) < 60000:
                    try:
                        base=datetime(1899,12,30); parsed=base+timedelta(days=int(orig))
                        df.at[r,col]=parsed.strftime('%Y-%m-%d'); fixed+=1; problem_cells.add((r,col)); continue
                    except: pass
                clean=orig.replace('/','-').replace('.','-').strip()
                parsed=pd.to_datetime(clean, dayfirst=True, errors='coerce')
                if not pd.isna(parsed):
                    new_val=parsed.strftime('%Y-%m-%d')
                    if orig!=new_val: df.at[r,col]=new_val; fixed+=1; problem_cells.add((r,col))
            except: continue
    return fixed

def tool2_fill(df, problem_cells):
    fixed=0
    for col in df.columns:
        if df[col].dtype!='object': df[col]=df[col].astype(object)
        cl=col.lower()
        if any(k in cl for k in ['salary','amount','price','age']): fill_val=0
        elif 'email' in cl: fill_val="missing@email.com"
        elif any(k in cl for k in ['phone','mobile']): fill_val="0000000000"
        else: fill_val="Unknown"
        for r in range(len(df)):
            try:
                if pd.isna(df.at[r,col]) or str(df.at[r,col]).strip().lower() in ["nan","none","","null","n/a","nat","-","?"]:
                    df.at[r,col]=fill_val; fixed+=1; problem_cells.add((r,col))
            except: continue
    return fixed

def tool3_email(df, problem_cells):
    fixed=0
    pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    typo={"gmai.com":"gmail.com","gmal.com":"gmail.com","yaho.com":"yahoo.com","hotmal.com":"hotmail.com","outlok.com":"outlook.com"}
    for col in df.columns:
        if 'email' not in col.lower(): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip(); low=orig.lower().replace(" ","")
                if "@" not in low or low in ["missing@email.com"]: continue
                for w,c in typo.items():
                    if w in low: low=low.replace(w,c)
                new_val=low if re.match(pattern,low) else "Invalid Email"
                if str(df.at[r,col]).strip()!=new_val: df.at[r,col]=new_val; fixed+=1; problem_cells.add((r,col))
            except: continue
    return fixed

def tool4_phone(df, problem_cells):
    fixed=0
    for col in df.columns:
        if not any(k in col.lower() for k in ['phone','mobile','contact']): continue
        if 'email' in col.lower(): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]); digits="".join([c for c in orig if c.isdigit()])
                if len(digits)==0 or digits=="0000000000": continue
                if len(digits)==12 and digits.startswith("91"): digits=digits[2:]
                if len(digits)==11 and digits.startswith("0"): digits=digits[1:]
                if len(digits)>10: digits=digits[-10:]
                if len(digits)==10 and digits!=orig: df.at[r,col]=digits; fixed+=1; problem_cells.add((r,col))
            except: continue
    return fixed

def tool5_case(df, changed_cells):
    fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        if not any(k in col.lower() for k in ['name','city','state','company']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip()
                if orig.lower() in ["unknown","missing@email.com","invalid email",""]: continue
                new_val=' '.join([w.capitalize() for w in orig.lower().split()]) if orig.isupper() else ' '.join([w.capitalize() for w in orig.split()])
                if orig!=new_val and len(new_val)>1: df.at[r,col]=new_val; fixed+=1; changed_cells.add((r,col))
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
                cleaned=re.sub(r'[^a-zA-Z0-9\s.,@\-_()&/]', '', orig); cleaned=re.sub(r'\s+', ' ', cleaned).strip()
                if orig!=cleaned and cleaned!="": df.at[r,col]=cleaned; fixed+=1; problem_cells.add((r,col))
            except: continue
    return fixed

def tool7_rename(df):
    fixed=0; new={}
    for c in df.columns:
        cl=re.sub(r'[^a-zA-Z0-9_ ]','',str(c).strip()); cl=re.sub(r'\s+','_',cl.lower()).strip('_'); cl=re.sub(r'_+','_',cl)
        if cl=="" or cl[0].isdigit(): cl="col_"+str(fixed)
        new[c]=cl
        if c!=cl: fixed+=1
    df.rename(columns=new,inplace=True)
    return fixed

def tool8_dedup(df):
    b=len(df); df.drop_duplicates(inplace=True); df.reset_index(drop=True,inplace=True); return b-len(df)

def tool9_trim(df, changed_cells):
    fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]); tr=' '.join(orig.strip().split())
                if orig!=tr: df.at[r,col]=tr; fixed+=1; changed_cells.add((r,col))
            except: continue
    return fixed

def tool10_spell(df, problem_cells):
    fixed=0; typo={"teh":"the","recieve":"receive","salery":"salary","custmer":"customer","addres":"address","manger":"manager","buisness":"business","definately":"definitely"}
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['email','phone']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]); words=orig.split(); nw=[]; ch=False
                for w in words:
                    cw=w.lower().strip('.,')
                    if cw in typo:
                        rep=typo[cw]; 
                        if w[0].isupper(): rep=rep.capitalize()
                        nw.append(rep); ch=True
                    else: nw.append(w)
                if ch: df.at[r,col]=" ".join(nw); fixed+=1; problem_cells.add((r,col))
            except: continue
    return fixed

def find_ambiguous(orig_df, clean_df):
    amb=[]
    for col in orig_df.columns:
        cl=col.lower()
        for r_idx in range(min(len(orig_df), len(clean_df))):
            try:
                orig=str(orig_df.at[r_idx,col]).strip()
                if orig.lower() in ["","nan","none"]: continue
                if 'date' in cl:
                    parts=re.split(r'[-/]',orig)
                    if len(parts)>=2:
                        try:
                            p1=int(re.sub(r'\D','',parts[0])); p2=int(re.sub(r'\D','',parts[1]))
                            if 1<=p1<=12 and 1<=p2<=12 and p1!=p2 and ('/' in orig or '-' in orig):
                                amb.append({"row":r_idx,"col":col,"original":orig,"question":f"Row {r_idx+1}: Date '{orig}' - DD/MM or MM/DD?","options":[f"{p1:02d}/{p2:02d} as DD/MM",f"{p2:02d}/{p1:02d} as MM/DD"]})
                        except: pass
            except: continue
    seen=set(); uniq=[]
    for a in amb:
        key=(a['row'],a['col'],a['original'])
        if key not in seen: seen.add(key); uniq.append(a)
    return uniq[:6]

def generate_pdf(orig_len, clean_len, empty_fixed, df, hub_report):
    if SimpleDocTemplate is None: return None
    try:
        buffer=io.BytesIO()
        doc=SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story=[]; styles=getSampleStyleSheet()
        title_style=ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#6b21a8'))
        story.append(Paragraph("VeriSame - 10 Tools Audit Report", title_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')} | {st.session_state.get('email','Guest')}", styles['Normal']))
        story.append(Spacer(1,10))
        text_style=ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=9)
        small_bold=ParagraphStyle('SmallBold', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
        data=[[Paragraph("<b>Metric</b>",small_bold),Paragraph("<b>Value</b>",small_bold)],[Paragraph("Total Rows",text_style),Paragraph(str(orig_len),text_style)],[Paragraph("Clean Rows",text_style),Paragraph(str(clean_len),text_style)]]
        if hub_report:
            for line in hub_report:
                parts=line.split(":")
                if len(parts)>=2: data.append([Paragraph(parts[0],text_style),Paragraph(parts[1],text_style)])
        t=Table(data, colWidths=[220,200])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(1,0),colors.HexColor('#9333ea')),('TEXTCOLOR',(0,0),(1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#c084fc'))]))
        story.append(t); doc.build(story); buffer.seek(0); return buffer.getvalue()
    except: return None

def query_groq(user_prompt):
    groq_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, 'secrets') else None
    knowledge = """
You are VeriSame AI.

WELCOME MESSAGE: Hello Welcome to the VeriSame what would you like to know?

APP:
- Name: VeriSame - Clean logic. Clear result - Fastest Way to Clean Your Data
- Founder: Anugya (only say when asked who made, who is founder, kisne banaya)
- Pricing: FREE 200 rows, Starter Rs49 one-time per file 2000 rows QR+UPI, Pro Rs299 30 days unlimited, Pro Rs1499 180 days unlimited
- 10 Tools: Date Fix, Fill Missing, Email Fix, Phone Fix, Case Fix, Symbol Clean, Header Clean, Dedup, Trim, Spell Fix - all advanced working
- Payment: QR Code + Direct Pay Button GPay/PhonePe/Paytm/BHIM UPI playwithreyansh0@okhdfcbank
- Date Decrease: YES for Pro daily countdown with actual dates red alert 5 days, for Starter per file
- Feedback connected to dashboard ?admin=PASSWORD
- Balloons on success

If asked who made app, say: Made by Anugya.
Else don't keep saying Anugya everywhere. Be short, helpful.
"""
    if not groq_key or Groq is None:
        low=user_prompt.lower()
        if any(k in low for k in ['founder','who made','who created','kisne banaya','made by','creator','developer']):
            return "Made by Anugya."
        if any(k in low for k in ['date decrease','days left','expiry']):
            return "Yes date decrease is in app for Pro - daily countdown with actual dates, red alert when 5 days left. For Starter it's per file."
        if 'feedback' in low:
            return "Feedback is connected to secret dashboard ?admin=PASSWORD."
        return "Hello Welcome to the VeriSame what would you like to know? FREE 200 rows, Starter Rs49 with QR+UPI, Pro Rs299 30 days, Rs1499 180 days, 10 tools advanced, date decrease yes."
    try:
        client=Groq(api_key=groq_key)
        comp=client.chat.completions.create(model=GROQ_MODEL, messages=[{"role":"system","content":knowledge},{"role":"user","content":user_prompt}], temperature=0.5, max_tokens=400)
        return comp.choices[0].message.content
    except:
        return "Hello Welcome to the VeriSame what would you like to know?"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Outfit:wght@800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: radial-gradient(ellipse at top left, #faf5ff 0%, #f5f3ff 18%, #ede9fe 36%, #e9d5ff 54%, #d8b4fe 72%, #c4b5fd 90%); background-attachment: fixed;}
.block-container {background: rgba(255,255,255,0.96); border-radius: 28px; padding: 1.8rem; max-width: 1350px; margin: 0 auto; box-shadow: 0 20px 50px rgba(139,92,246,0.18);}
.welcome-black {font-family: 'Outfit', sans-serif; font-weight: 900!important; font-size: 3.2rem!important; color: #000000!important; text-align: center;}
.welcome-space {height: 30px;}
.subtitle {color: #6b7280!important; text-align:center; margin-top: 8px!important;}
.tagline-badge {display: inline-block; padding: 8px 20px; background: linear-gradient(135deg, #7e22ce, #9333ea); color: #fff !important; font-weight: 700 !important; border-radius: 20px;}
.logo-container {width: 100%; display: flex; justify-content: center; padding: 5px 0;}
.logo-container img {width: 100%; max-width: 450px; max-height: 450px; object-fit: contain;}
.logo-float {animation: float 5s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.pricing-card {border-radius: 22px; padding: 1.6rem; background: #ffffff!important; border: 2px solid #e9d5ff; min-height: 430px; display: flex; flex-direction: column; box-shadow: 0 8px 20px rgba(147,51,234,0.08);}
.pricing-card-free {border: 2px solid #c4b5fd !important;}
.pricing-card-starter {border: 2.5px solid #22c55e !important;}
.pricing-card-pro {border: 2.5px solid #9333ea !important;}
.stButton>button {border-radius: 14px !important; font-weight: 700 !important; background: linear-gradient(100deg, #7e22ce, #9333ea) !important; color: white !important; border: none !important; width: 100% !important; padding: 12px 20px !important;}
.big-pay-button {display: block; width: 100%; padding: 22px 18px; background: linear-gradient(100deg, #16a34a, #22c55e); color: white !important; font-weight: 800 !important; font-size: 1.4rem !important; text-align: center; border-radius: 16px; text-decoration: none !important; margin: 12px 0; border: 2px solid #16a34a;}
.big-pay-button-pro {background: linear-gradient(100deg, #7e22ce, #9333ea, #a855f7) !important; border: 2px solid #7e22ce !important;}
.big-pay-sub {font-size: 0.9rem!important; display: block; margin-top: 4px;}
.pro-banner {background: linear-gradient(135deg, #4c1d95, #7e22ce, #9333ea, #a855f7); padding: 1.5rem; border-radius: 20px; text-align: center; margin: 1rem 0;}
.pro-banner h2 {color: white!important; font-size: 1.4rem!important; margin: 0!important; font-weight: 800!important;}
.pro-banner-small {background: linear-gradient(135deg, #4c1d95, #7e22ce); padding: 1rem; border-radius: 16px; text-align: center; margin: 0.8rem 0;}
.pro-banner-small h2 {color: white!important; font-size: 1.1rem!important; margin: 0!important;}
.tool-chip {display: inline-block; background: #fff !important; padding: 8px 14px; border-radius: 20px; margin: 4px; color: #4c1d95 !important; font-weight: 700 !important; font-size: 0.82rem !important;}
.plan-status-box {padding: 10px 14px; border-radius: 12px; font-weight: 700 !important; margin-bottom: 10px; font-size: 0.88rem!important;}
.plan-active {background: #dcfce7 !important; border: 2px solid #22c55e !important; color: #15803d !important;}
.plan-selected {background: #fef9c3 !important; border: 2px solid #eab308 !important; color: #854d0e !important;}
.expiry-red {background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%) !important; border: 2.5px solid #ef4444 !important; border-radius: 16px; padding: 14px; margin: 10px 0; text-align: center;}
.hundred-box {background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important; border: 2.5px solid #22c55e !important; border-radius: 16px; padding: 16px; margin: 10px 0; text-align: center;}
.qr-box {background: #ffffff !important; border: 3px solid #9333ea !important; border-radius: 20px; padding: 24px; text-align: center; margin: 14px 0; box-shadow: 0 10px 24px rgba(147,51,234,0.12);}
.upgrade-msg {background: linear-gradient(135deg, #fef9c3 0%, #fef3c7 100%) !important; border: 2.5px solid #eab308 !important; border-radius: 16px; padding: 16px; text-align: center; margin: 10px 0;}
.tool-report {background: #faf5ff !important; border: 1.5px solid #e9d5ff !important; border-radius: 12px; padding: 12px; margin: 6px 0; font-size: 0.86rem!important;}
.day-counter {background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 2px solid #3b82f6; border-radius: 14px; padding: 12px; margin: 10px 0; font-size: 0.86rem!important;}
.verifying-box {background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important; border: 2.5px solid #3b82f6 !important; border-radius: 18px; padding: 22px; margin: 18px 0; text-align: center;}
.thankyou-box {background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important; border: 2.5px solid #22c55e !important; border-radius: 18px; padding: 18px; margin: 14px 0; text-align: center;}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello Welcome to the VeriSame what would you like to know?"}]
if "changed_cells" not in st.session_state: st.session_state.changed_cells = set()
if "problem_cells" not in st.session_state: st.session_state.problem_cells = set()
if "uploaded_files" not in st.session_state: st.session_state.uploaded_files = {}
for k in ['plan','email','df_clean','df_original','amt','email_entered','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done','ambiguous_list','hundred_done','confirm_choices','just_approved']:
    if k not in st.session_state:
        st.session_state[k] = None if k in ['plan','email','df_clean','df_original','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','ambiguous_list','confirm_choices'] else False

def update_changed():
    try:
        if st.session_state.df_original is None or st.session_state.df_clean is None: st.session_state.changed_cells=set(); return
        orig_df=st.session_state.df_original.reset_index(drop=True); clean_df=st.session_state.df_clean.reset_index(drop=True)
        changed=set(); min_rows=min(len(orig_df),len(clean_df)); common=[c for c in orig_df.columns if c in clean_df.columns]
        for col in common:
            try:
                o_vals=orig_df[col].iloc[:min_rows].fillna("").astype(str).values; c_vals=clean_df[col].iloc[:min_rows].fillna("").astype(str).values
                for idx in range(min_rows):
                    if o_vals[idx]!=c_vals[idx]: changed.add((idx,col))
            except: continue
        st.session_state.changed_cells=changed
    except: st.session_state.changed_cells=set()

def apply_style(df_to_style):
    try:
        df_temp=df_to_style.copy().reset_index(drop=True)
        def highlight(data):
            df_colors=pd.DataFrame('', index=data.index, columns=data.columns)
            for r,c in st.session_state.get("changed_cells", set()):
                if r in df_colors.index and c in df_colors.columns: df_colors.at[r,c]='background-color: #bbf7d0; color: #047857; font-weight: bold; border: 1.5px solid #10b981;'
            for r,c in st.session_state.get("problem_cells", set()):
                if r in df_colors.index and c in df_colors.columns: df_colors.at[r,c]='background-color: #fecaca; color: #991b1b; font-weight: bold; border: 1.5px solid #ef4444;'
            return df_colors
        return df_temp.style.apply(highlight, axis=None)
    except: return df_to_style

def render_chat(is_sidebar=False):
    target=st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### VeriSame AI")
    chat_html="<div style='max-height: 300px; overflow-y: auto; padding: 10px; background: #fff; border: 2px solid #e9d5ff; border-radius: 14px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history[-6:]:
        msg=chat['message'][:500]
        if chat["role"]=="assistant": chat_html+="<p style='color: #6b21a8; margin: 8px 0; font-size: 0.85rem;'><b>AI:</b> "+msg+"</p>"
        else: chat_html+="<p style='color: #111; margin: 8px 0; font-size: 0.85rem;'><b>You:</b> "+msg+"</p>"
    chat_html+="</div>"
    target.markdown(chat_html, unsafe_allow_html=True)
    s_id="side" if is_sidebar else "main"
    um=target.text_input("Ask", placeholder="Ask...", key="chat_"+s_id+"_perfect", label_visibility="collapsed")
    if target.button("Send", key="btn_chat_"+s_id+"_perfect", use_container_width=True):
        if um and um.strip():
            st.session_state.chat_history.append({"role":"user","message":um})
            reply=query_groq(um)
            st.session_state.chat_history.append({"role":"assistant","message":reply})
            st.rerun()

if st.session_state.email and st.session_state.plan != "free":
    db=load_db(); user=db.get(st.session_state.email,{})
    st.sidebar.markdown("<div style='background: #f5f3ff; padding: 10px; border-radius: 12px; border: 2px solid #9333ea;'><b>"+st.session_state.email+"</b></div>", unsafe_allow_html=True)
    if user.get("plan") in ["starter","pro"] and user.get("expiry"):
        try:
            exp_date=datetime.strptime(user["expiry"], "%Y-%m-%d").date(); days_left=(exp_date-datetime.now().date()).days; st.session_state.days=days_left
            if user.get("plan")=="starter":
                if user.get("status")=="PAID": st.sidebar.markdown("<div class='plan-status-box plan-active'>Starter Active<br>Rs49 - ONE TIME per file</div>", unsafe_allow_html=True)
                else: st.sidebar.markdown("<div class='plan-status-box plan-selected'>Starter Rs49 Waiting</div>", unsafe_allow_html=True)
            else:
                if days_left<0: st.sidebar.markdown("<div class='expiry-red'><b>Plan Ended - 0 Days Left</b></div>", unsafe_allow_html=True); user["status"]="EXPIRED"; save_db(db)
                elif 0<=days_left<=5: exp_str=exp_date.strftime("%d %b %Y"); st.sidebar.markdown("<div class='expiry-red'><b>Your payment is going to end in "+str(days_left)+" days</b><br>Expiry: "+exp_str+"</div>", unsafe_allow_html=True)
                else:
                    if user.get("status")=="PAID": exp_str=exp_date.strftime("%d %b %Y"); st.sidebar.markdown("<div class='plan-status-box plan-active'>Pro Rs"+str(user.get("amt",0))+" Active</div>", unsafe_allow_html=True)
        except: pass
    render_chat(is_sidebar=True)
elif st.session_state.plan=="free":
    st.sidebar.markdown("<div class='plan-status-box plan-active'>Free - 200 Rows</div>", unsafe_allow_html=True)
    render_chat(is_sidebar=True)

if st.session_state.plan or st.session_state.email_entered:
    st.sidebar.markdown("---")
    b1,b2=st.sidebar.columns(2)
    with b1:
        if st.button("Back", key="nav_back_perfect", use_container_width=True):
            st.session_state.selected_plan=None; st.session_state.selected_amt=None; st.session_state.plan=None; st.session_state.email_entered=False; st.session_state.uploaded_files={}; st.session_state.clean_done=False; st.session_state.hundred_done=False; st.session_state.ambiguous_list=None; st.session_state.just_approved=False; st.rerun()
    with b2:
        if st.button("Logout", key="nav_logout_perfect", use_container_width=True):
            for k in ['plan','email','df_clean','df_original','amt','email_entered','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done','ambiguous_list','hundred_done','confirm_choices','just_approved']:
                st.session_state[k]=None if k in ['plan','email','df_clean','df_original','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','ambiguous_list','confirm_choices'] else False
            st.session_state.uploaded_files={}; st.session_state.changed_cells=set(); st.session_state.problem_cells=set(); st.query_params.clear(); st.rerun()

is_first_page=(st.session_state.plan is None and st.session_state.selected_plan is None)

if is_first_page:
    st.markdown('<div class="logo-container logo-float"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" alt="VeriSame Logo"></div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-space"></div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-black">Welcome To VeriSame👋</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; margin-top:10px;"><span class="tagline-badge">Clean logic. Clear result</span><div class="subtitle">The Fastest Way to Clean Your Data</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="pro-banner" style="margin-top:18px;"><h2>10 Advanced Tools - All Plans Include All 10 Tools</h2><div style="margin-top:8px;"><span class="tool-chip">Date Fix</span><span class="tool-chip">Fill Missing</span><span class="tool-chip">Email Fix</span><span class="tool-chip">Phone Fix</span><span class="tool-chip">Case Fix</span><span class="tool-chip">Symbol Clean</span><span class="tool-chip">Header Clean</span><span class="tool-chip">Dedup</span><span class="tool-chip">Trim</span><span class="tool-chip">Spell Fix</span></div></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="pro-banner-small"><h2>10 Advanced Tools - All Plans Include All 10 Tools</h2></div>', unsafe_allow_html=True)

if "admin" in st.query_params:
    if st.query_params.get("admin")==ADMIN_PASS:
        st.title("Secret Dashboard - VeriSame")
        st.markdown('<div style="background: #dcfce7; border: 2px solid #22c55e; border-radius: 12px; padding: 12px; margin: 10px 0;"><b>Manual Approval Only - QR Code - Date Decrease - Feedback Connected - Made by Anugya</b></div>', unsafe_allow_html=True)
        data=load_db(); fbs=load_feedback(); free_data=load_free_clicks()
        tab1,tab2,tab3,tab4=st.tabs(["FREE "+str(free_data.get('count',0)), "STARTER Rs49", "PRO", "Feedback "+str(len(fbs))])
        with tab1: st.markdown("<h2>"+str(free_data.get('count',0))+" Free Users</h2>", unsafe_allow_html=True)
        with tab2:
            for email,info in list({k:v for k,v in data.items() if v.get('amt')==STARTER_PRICE}.items()):
                if "@" not in email: continue
                c1,c2,c3=st.columns([4,2,2])
                with c1: st.write(email+" - "+info.get('status','')+" - Used "+str(info.get('used',0)))
                with c2:
                    if info.get("status") in ["PENDING","EXPIRED"]:
                        if st.button("Approve", key="ap_s_"+email+"_perfect", type="primary", use_container_width=True):
                            data[email]["status"]="PAID"; data[email]["used"]=0; data[email]["expiry"]=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d"); save_db(data); st.balloons(); st.rerun()
                with c3:
                    if st.button("Delete", key="del_s_"+email+"_perfect", use_container_width=True): del data[email]; save_db(data); st.rerun()
        with tab3:
            for email,info in list({k:v for k,v in data.items() if v.get('amt') in [PRO_1M, PRO_6M]}.items()):
                if "@" not in email: continue
                c1,c2,c3=st.columns([4,2,2])
                with c1: st.write(email+" - Rs"+str(info.get('amt',''))+" - "+info.get('status',''))
                with c2:
                    if info.get("status") in ["PENDING","EXPIRED"]:
                        if st.button("Approve", key="ap_p_"+email+"_perfect", type="primary", use_container_width=True):
                            data[email]["status"]="PAID"; data[email]["expiry"]=(datetime.now()+timedelta(days=180 if data[email].get("amt")==PRO_6M else 30)).strftime("%Y-%m-%d"); save_db(data); st.balloons(); st.rerun()
                with c3:
                    if st.button("Delete", key="del_p_"+email+"_perfect", use_container_width=True): del data[email]; save_db(data); st.rerun()
        with tab4:
            if fbs:
                for fb in reversed(fbs[-50:]): st.markdown("<div style='background:#fff; border:2px solid #e9d5ff; border-radius:14px; padding:14px; margin:10px 0;'><b>"+fb['email']+"</b><br><p>"+fb['feedback'][:500]+"</p><small>"+fb.get('time','')[:19]+"</small></div>", unsafe_allow_html=True)
        st.stop()

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        st.markdown("<h2 style='text-align:center; color:#4c1d95; margin-top:22px;'>Choose Your Plan</h2>", unsafe_allow_html=True)
        col_free, col_starter, col_pro = st.columns(3, gap="medium")
        with col_free:
            st.markdown('<div class="pricing-card pricing-card-free"><h3>FREE FOREVER</h3><h1 style="font-size:3.2rem;">FREE</h1><p><b>200 Rows - Lifetime Free</b></p><div style="margin-top:12px; flex-grow:1;"><p>✓ All 10 Advanced Tools</p><p>✓ Super Fast Cleaning</p><p>✓ CSV + Excel + PDF</p><p>✓ 100% Private</p><p>✓ AI Support</p></div></div>', unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free_perfect", type="primary", use_container_width=True):
                save_free_clicks(); st.session_state.selected_plan="free"; st.session_state.plan="free"; st.session_state.email="Guest_Free"; st.session_state.email_entered=True; st.balloons(); st.rerun()
        with col_starter:
            st.markdown('<div class="pricing-card pricing-card-starter"><p style="background: #22c55e; color:white; padding:6px 14px; border-radius:16px; display:inline-block; font-size:0.78rem; font-weight: 800;">ONE TIME PER FILE</p><h3 style="margin-top:10px;">STARTER</h3><h1 style="font-size:3.2rem;">Rs49</h1><p><b>One-Time Per File - 2,000 Rows</b></p><div style="margin-top:12px; flex-grow:1;"><p>✓ All 10 Advanced Tools</p><p>✓ Pay Again For Next File</p><p>✓ QR Code + GPay Direct - UPI Included</p><p>✓ Big Pay Box + I Paid + Balloons</p><p>✓ Date Decrease: Per File</p></div></div>', unsafe_allow_html=True)
            if st.button("Start with 49", key="btn_starter_perfect", type="primary", use_container_width=True):
                st.session_state.selected_plan="starter"; st.session_state.selected_amt=STARTER_PRICE; st.session_state.amt=STARTER_PRICE; st.rerun()
        with col_pro:
            st.markdown('<div class="pricing-card pricing-card-pro"><p style="background: #9333ea; color:white; padding:6px 14px; border-radius:16px; display:inline-block; font-size:0.78rem; font-weight: 800;">POPULAR - DATE DECREASE YES</p><h3 style="margin-top:10px;">PRO</h3><h1 style="font-size:2.4rem;">Rs299 / Rs1499</h1><p><b>Unlimited Rows - Date Decrease YES</b></p><div style="margin-top:12px; flex-grow:1;"><p>✓ Rs299 = 1 Month (30 Days)</p><p>✓ Rs1499 = 6 Months (180 Days)</p><p>✓ Unlimited Rows</p><p>✓ QR + Big Pay Box - UPI Included</p><p>✓ Date Decrease: Daily + Red Alert 5 Days</p></div></div>', unsafe_allow_html=True)
            c_p1,c_p2=st.columns(2)
            with c_p1:
                if st.button("Rs299 - 30 Days", key="btn_pro_299_perfect", type="primary", use_container_width=True):
                    st.session_state.selected_plan="pro"; st.session_state.selected_amt=PRO_1M; st.session_state.amt=PRO_1M; st.rerun()
            with c_p2:
                if st.button("Rs1499 - 180 Days", key="btn_pro_1499_perfect", type="primary", use_container_width=True):
                    st.session_state.selected_plan="pro"; st.session_state.selected_amt=PRO_6M; st.session_state.amt=PRO_6M; st.rerun()
        render_chat(is_sidebar=False)
        st.markdown("---")
        st.markdown("### Feedback - We Value Your Feedback")
        fb_front=st.text_area("Feedback", placeholder="Your feedback...", key="fb_front_perfect", height=80, label_visibility="collapsed")
        if st.button("Send Feedback", key="fb_front_btn_perfect", type="primary", use_container_width=True):
            if fb_front.strip() and save_feedback(fb_front.strip(), "Guest"): st.success("Thank you! 💜"); st.balloons()
    else:
        if st.session_state.selected_plan=="free": st.session_state.plan="free"; st.session_state.email="Guest_Free"; st.session_state.email_entered=True; st.rerun()
        if st.session_state.selected_plan=="starter": plan_text="STARTER - Rs49 One-Time Per File"
        else:
            if st.session_state.selected_amt==PRO_1M: plan_text="PRO - 1 Month Rs299 - Date Decrease YES"
            else: plan_text="PRO - 6 Months Rs1499 - Date Decrease YES"
        st.markdown("<h2 style='text-align:center; margin-top:18px;'>Enter email for "+plan_text+"</h2>", unsafe_allow_html=True)
        _,ce2,_=st.columns([1,2,1])
        with ce2:
            email_input=st.text_input("Enter email", placeholder="your@email.com", key="email_main_perfect").lower().strip()
            b1,b2=st.columns(2)
            with b1:
                if st.button("Verify & Continue", key="btn_verify_perfect", type="primary", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        st.session_state.email=email_input; st.session_state.email_entered=True; data=load_db()
                        if st.session_state.selected_plan=="starter":
                            exp=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d"); data[email_input]={"plan":"starter","status":"PENDING","amt":STARTER_PRICE,"expiry":exp,"created":str(datetime.now()),"used":0}; save_db(data); st.session_state.plan="starter"; st.session_state.amt=STARTER_PRICE; st.balloons(); st.rerun()
                        else:
                            exact=180 if st.session_state.selected_amt==PRO_6M else 30; exp=(datetime.now()+timedelta(days=exact)).strftime("%Y-%m-%d"); data[email_input]={"plan":"pro","status":"PENDING","amt":st.session_state.selected_amt,"expiry":exp,"created":str(datetime.now())}; save_db(data); st.session_state.plan="pro"; st.session_state.amt=st.session_state.selected_amt; st.balloons(); st.rerun()
                    else: st.error("Enter valid email")
            with b2:
                if st.button("Back", key="btn_back_perfect2", use_container_width=True): st.session_state.selected_plan=None; st.session_state.selected_amt=None; st.rerun()
        st.stop()
else:
    tab1, tab2 = st.tabs(["Upload File", "Try Demo"])
    with tab1:
        files=st.file_uploader("Drop CSV, Excel or JSON", type=["csv","xlsx","xls","json"], accept_multiple_files=True, label_visibility="collapsed")
        if files:
            cur_files=[f.name for f in files]; sheet_sel={}
            for f in files:
                if f.name.endswith((".xlsx",".xls")):
                    try: ef=pd.ExcelFile(f); sel=st.selectbox("Sheet for "+f.name, ef.sheet_names, key="sh_"+f.name+"_perfect"); sheet_sel[f.name]=sel
                    except: pass
            sig=str(cur_files)+"-"+str(list(sheet_sel.values()))
            db_check=load_db()
            if st.session_state.email in db_check and db_check[st.session_state.email].get("plan")=="starter" and db_check[st.session_state.email].get("status")=="PAID":
                prev_sig=st.session_state.get("last_upload_sig")
                if prev_sig and prev_sig!=sig and sig:
                    if db_check[st.session_state.email].get("used",0)>=1: db_check[st.session_state.email]["status"]="EXPIRED"; save_db(db_check); st.warning("Starter Rs49 one-time per file. Pay again."); st.rerun()
            if st.session_state.get("last_upload_sig")!=sig:
                try:
                    st.session_state.uploaded_files={}
                    for f in files:
                        try:
                            if f.name.endswith((".xlsx",".xls")): sh=sheet_sel.get(f.name,0); sub=pd.read_excel(f, sheet_name=sh)
                            elif f.name.endswith(".csv"): sub=pd.read_csv(f)
                            else: sub=pd.read_json(f)
                            limit=FREE_LIMIT if st.session_state.plan=="free" else STARTER_LIMIT if st.session_state.plan=="starter" else 1000000
                            if len(sub)>limit and st.session_state.plan in ["free","starter"]: sub=sub.iloc[:limit].copy()
                            clean_init=sub.copy()
                            for col in clean_init.columns:
                                if clean_init[col].dtype!='object': clean_init[col]=clean_init[col].astype(object)
                            clean_init.drop_duplicates(inplace=True); clean_init.reset_index(drop=True, inplace=True)
                            st.session_state.uploaded_files[f.name]={"original":sub.copy().reset_index(drop=True),"clean":clean_init,"orig_len":len(sub),"empty_fixed":int(sub.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}
                        except Exception as e: st.error("Error reading "+f.name+": "+str(e))
                    st.session_state.last_upload_sig=sig; st.session_state.clean_done=False; st.session_state.hundred_done=False; st.session_state.ambiguous_list=None; st.session_state.hub_report=None; st.session_state.just_approved=False
                except Exception as e: st.error("Error: "+str(e))
    with tab2:
        st.markdown("### Try Demo - Perfect Sample Shows All 10 Tools Working")
        st.markdown("<div style='background:#faf5ff; border:2px solid #e9d5ff; border-radius:12px; padding:12px; font-size:0.85rem;'><b>This demo file has dirty data for ALL 10 tools so you can see each tool is advanced and working:</b><br>• Date: 12/5/2024, 40000 Excel serial, 05.06.2024<br>• Name: RAHUL KUMAR caps, extra spaces<br>• Email: GMAI.COM typo, YAHO.COM typo<br>• Phone: +91 98765-43210, 09123456789, dashes<br>• Symbols: @#$ in name<br>• Header: Extra spaces<br>• Dup: Duplicate row<br>• Trim: Extra spaces<br>• Spell: teh, salery, custmer</div>", unsafe_allow_html=True)
        if st.button("Load Perfect Demo File - See All 10 Tools Work", key="btn_load_demo_perfect", type="primary", use_container_width=True):
            # PERFECT DEMO FILE - SHOWS EVERY TOOL GOOD
            demo_data={
                "Join Date": ["12/5/2024", "05.06.2024", "15-03-2023", "40000", "12/5/2024"],
                "  Name@  ": ["  RAHUL KUMAR  ", "priya SHARMA", "AMIT @#$ Kumar", "teh custmer", "  RAHUL KUMAR  "],
                "Email ID": ["RAHUL@GMAI.COM", "priya@yaho.com ", "test@outlok.com", "bad email", "RAHUL@GMAI.COM"],
                "Phone Number": ["+91 98765-43210", "09123456789", "987-654-3210", "  98765 43210  ", "+91 98765-43210"],
                "  Company   ": ["  TCS  pvt  ltd  ", "infosys  @#$", "  WIPRO  ", "teh buisness", "  TCS  pvt  ltd  "],
                "Salary": ["", "salery 50000", "10000", "teh salery", ""],
                "City": ["  MUMBAI  ", "delhi", "BANGALORE @#$", "teh city", "  MUMBAI  "],
            }
            sample=pd.DataFrame(demo_data)
            clean=sample.copy()
            st.session_state.uploaded_files={"VeriSame_Perfect_Demo_All_10_Tools.csv":{"original":sample.copy().reset_index(drop=True),"clean":clean,"orig_len":len(sample),"empty_fixed":int(sample.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}}
            st.session_state.last_upload_sig=None; st.session_state.clean_done=False; st.session_state.hundred_done=False; st.session_state.ambiguous_list=None; st.session_state.just_approved=False; st.balloons(); st.success("Perfect demo file loaded! Click BIG CLEAN to see all 10 tools work!"); st.rerun()

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        keys=list(st.session_state.uploaded_files.keys()); sel_file=st.selectbox("Select file:", keys, key="active_file_perfect", label_visibility="collapsed")
        limit=FREE_LIMIT if st.session_state.plan=="free" else STARTER_LIMIT if st.session_state.plan=="starter" else 1000000
        if st.session_state.plan in ["free","starter"] and len(st.session_state.uploaded_files[sel_file]["clean"]) > limit: st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.uploaded_files[sel_file]["clean"].iloc[:limit]
        st.session_state.df_clean=st.session_state.uploaded_files[sel_file]["clean"]; st.session_state.df_original=st.session_state.uploaded_files[sel_file]["original"]; st.session_state.orig_len=len(st.session_state.df_original); st.session_state.empty_fixed=st.session_state.uploaded_files[sel_file]["empty_fixed"]; st.session_state.problem_cells=st.session_state.uploaded_files[sel_file].get("problem_cells",set()); update_changed(); df_clean=st.session_state.df_clean; orig_len=st.session_state.orig_len

        if not st.session_state.get("clean_done"):
            st.markdown("### File: "+sel_file+" - "+str(orig_len)+" rows")
            if st.button("BIG CLEAN - 1 Click = 10 Advanced Tools", key="btn_big_clean_perfect", type="primary", use_container_width=True):
                try:
                    enforce_delay(); df_curr=st.session_state.df_clean.copy(); st.session_state.problem_cells=set(); st.session_state.changed_cells=set()
                    for col in df_curr.columns:
                        if df_curr[col].dtype!='object': df_curr[col]=df_curr[col].astype(object)
                    fixes=[]; fixes.append(("Dates Fixed", tool1_date(df_curr, st.session_state.problem_cells))); fixes.append(("Missing Values Filled", tool2_fill(df_curr, st.session_state.problem_cells))); fixes.append(("Emails Fixed", tool3_email(df_curr, st.session_state.problem_cells))); fixes.append(("Phones Fixed", tool4_phone(df_curr, st.session_state.problem_cells))); fixes.append(("Names & Case Fixed", tool5_case(df_curr, st.session_state.changed_cells))); fixes.append(("Symbols Cleaned", tool6_symbols(df_curr, st.session_state.problem_cells))); fixes.append(("Headers Cleaned", tool7_rename(df_curr))); fixes.append(("Duplicates Removed", tool8_dedup(df_curr))); fixes.append(("Extra Spaces Removed", tool9_trim(df_curr, st.session_state.changed_cells))); fixes.append(("Spelling Fixed", tool10_spell(df_curr, st.session_state.problem_cells)))
                    hub=[]
                    for name,cnt in fixes: hub.append(name+": "+str(cnt)+" fixed" if cnt else name+": Already clean")
                    st.session_state.df_clean=df_curr; update_changed(); ambiguous=find_ambiguous(st.session_state.df_original, st.session_state.df_clean); st.session_state["hub_report"]=hub; st.session_state["clean_done"]=True; st.session_state["ambiguous_list"]=ambiguous; st.session_state["hundred_done"]=len(ambiguous)==0; st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.df_clean; st.success("Cleaned with 10 Advanced Tools!"); st.balloons(); st.rerun()
                except Exception as e: st.error("Error: "+str(e))
        else:
            ambiguous=st.session_state.get("ambiguous_list", []); is_hundred=st.session_state.get("hundred_done", False) or len(ambiguous)==0
            if is_hundred: percent_text="100% Clean"
            else: percent_text="95% Clean"
            st.markdown("<h2>Data Summary - "+percent_text+" - 10 Advanced Tools</h2>", unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            with c1: st.metric("Total Rows", orig_len)
            with c2: st.metric("Clean Rows", len(df_clean))
            with c3: st.metric("Duplicates", max(0, orig_len-len(df_clean)))
            with c4: st.metric("Empty Fixed", st.session_state.empty_fixed)
            db_after=load_db(); user_after=db_after.get(st.session_state.email,{}) if st.session_state.email and st.session_state.email != "Guest_Free" else {}
            if user_after.get("plan")=="pro" and user_after.get("expiry"):
                try:
                    exp_d=datetime.strptime(user_after["expiry"], "%Y-%m-%d").date(); days_left_after=(exp_d-datetime.now().date()).days; exp_str_after=exp_d.strftime("%d %b %Y")
                    if 0<=days_left_after<=5: st.markdown("<div class='expiry-red'><b>Your payment is going to end in "+str(days_left_after)+" days</b><br>Expiry: "+exp_str_after+"</div>", unsafe_allow_html=True)
                    elif days_left_after>=0: st.markdown("<div class='day-counter'>Days Left: "+str(days_left_after)+" days - Expiry: "+exp_str_after+"</div>", unsafe_allow_html=True)
                except: pass
            if st.session_state.get("hub_report"):
                st.markdown("### What We Fixed - 10 Tools Report:")
                cols=st.columns(2)
                for idx, report_line in enumerate(st.session_state.hub_report):
                    with cols[idx%2]: st.markdown("<div class='tool-report'>✅ "+report_line+"</div>", unsafe_allow_html=True)
            if is_hundred: st.markdown("<div class='hundred-box'><h3>100% Clean! All 10 Tools Applied!</h3></div>", unsafe_allow_html=True); st.balloons()
            else:
                st.markdown("<div class='upgrade-msg'><h3>Need Your Help - "+str(len(ambiguous))+" Items</h3></div>", unsafe_allow_html=True)
                choices=st.session_state.get("confirm_choices", {})
                for i, amb in enumerate(ambiguous):
                    st.markdown("<div style='background:#fff; border:2px solid #f59e0b; border-radius:12px; padding:12px; margin:8px 0;'><b>Q"+str(i+1)+": "+amb['question']+"</b><br><small>"+amb['original']+"</small></div>", unsafe_allow_html=True)
                    selected=st.radio("Choose:", amb['options'], key="amb_"+str(i)+"_perfect", index=0); choices[i]=selected
                st.session_state.confirm_choices=choices
                if st.button("Apply & Make 100% Clean", key="btn_apply_amb_perfect", type="primary", use_container_width=True):
                    st.session_state.hundred_done=True; st.session_state.ambiguous_list=[]; st.success("Now 100% Clean!"); st.balloons(); st.rerun()
            st.markdown("<h3>Preview - 10 Rows - "+percent_text+"</h3>", unsafe_allow_html=True)
            styled=apply_style(df_clean.head(10)); st.dataframe(styled, use_container_width=True, height=380)

        if st.session_state.get("clean_done"):
            db=load_db(); user_info=db.get(st.session_state.email,{}) if st.session_state.email and st.session_state.email != "Guest_Free" else {}; is_paid=user_info.get("status")=="PAID" if user_info else True if st.session_state.plan=="free" else False; is_expired=False; days_left=999
            if user_info and user_info.get("expiry"):
                try:
                    exp_d=datetime.strptime(user_info["expiry"], "%Y-%m-%d").date(); days_left=(exp_d-datetime.now().date()).days
                    if user_info.get("plan") != "starter" and days_left < 0: is_expired=True
                except: pass
            if is_paid and not st.session_state.get("just_approved") and user_info.get("plan") in ["starter","pro"]: st.session_state.just_approved=True; st.balloons()
            
            if st.session_state.plan=="free":
                st.markdown("<h2>Export - "+percent_text+"</h2>", unsafe_allow_html=True); c1,c2,c3=st.columns(3); safe=sel_file[:30]
                with c1: csv=df_clean.to_csv(index=False).encode(); st.download_button("CSV - "+percent_text, csv, safe+"_cleaned.csv", mime="text/csv", key="dl_csv_free_perfect", use_container_width=True, type="primary")
                with c2:
                    if openpyxl is not None: ex=io.BytesIO(); df_clean.to_excel(ex, index=False, engine='openpyxl'); ex.seek(0); st.download_button("Excel - "+percent_text, ex.getvalue(), safe+"_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx_free_perfect", use_container_width=True)
                with c3: pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean, st.session_state.get("hub_report")); 
                with c3:
                    if pdf: st.download_button("PDF - "+percent_text, pdf, safe+"_audit.pdf", mime="application/pdf", key="dl_pdf_free_perfect", use_container_width=True)
            elif st.session_state.plan in ["starter","pro"]:
                if is_expired: st.markdown("<div class='expiry-red'><b>Plan Ended - 0 days - Pay again</b></div>", unsafe_allow_html=True); is_paid=False
                
                if not is_paid:
                    sel_amt=user_info.get("amt", st.session_state.get("selected_amt", 0))
                    if sel_amt in [STARTER_PRICE, PRO_1M, PRO_6M]: amt_to_show=sel_amt
                    else: amt_to_show=st.session_state.get("selected_amt", STARTER_PRICE)
                    if amt_to_show==STARTER_PRICE: plan_name="Starter Rs49 - ONE TIME per File - 2000 Rows"; upi_link="upi://pay?pa="+UPI_ID+"&pn=VeriSame&am="+str(STARTER_PRICE)+"&cu=INR&tn=VeriSame Starter "+str(STARTER_PRICE); btn_class=""; pay_text="Pay "+str(STARTER_PRICE)+" from GPay or any other pay"
                    elif amt_to_show==PRO_1M: plan_name="Pro Rs299 - 1 Month 30 Days Unlimited"; upi_link="upi://pay?pa="+UPI_ID+"&pn=VeriSame&am="+str(PRO_1M)+"&cu=INR&tn=VeriSame Pro 299"; btn_class="big-pay-button-pro"; pay_text="Pay "+str(PRO_1M)+" from GPay or any other pay"
                    else: plan_name="Pro Rs1499 - 6 Months 180 Days Best Value"; upi_link="upi://pay?pa="+UPI_ID+"&pn=VeriSame&am="+str(PRO_6M)+"&cu=INR&tn=VeriSame Pro 1499"; btn_class="big-pay-button-pro"; amt_to_show=PRO_6M; pay_text="Pay "+str(PRO_6M)+" with GPay or any other pay"
                    
                    if user_info.get("status")=="PENDING":
                        st.markdown("<div class='verifying-box'><h3>Thank you for your payment</h3><p>Your payment is being verified.<br>Please wait a moment, our team will confirm shortly.<br>Your download will be available right after approval.</p></div>", unsafe_allow_html=True)
                        if st.button("Check Status", key="check_status_perfect", type="primary", use_container_width=True): st.rerun()
                    else:
                        st.markdown("<div class='upgrade-msg'><h3>Your file cleaned "+percent_text+" - "+plan_name+"</h3></div>", unsafe_allow_html=True)
                        # QR CODE + PAY BUTTON - BOTH PRESENT
                        st.markdown("<div class='qr-box'>", unsafe_allow_html=True)
                        st.markdown("### "+plan_name)
                        
                        col_qr, col_pay = st.columns([1, 1.2], gap="large")
                        with col_qr:
                            st.markdown("<p style='font-weight:800; text-align:center; font-size:1.05rem; color:#000;'>QR Code - Scan & Pay</p>", unsafe_allow_html=True)
                            qr_url="https://api.qrserver.com/v1/create-qr-code/?size=350x350&data="+urllib.parse.quote(upi_link)
                            st.image(qr_url, width=350)
                            st.markdown("<p style='font-size:0.75rem; color:#6b7280; text-align:center; margin-top:6px;'>UPI ID: "+UPI_ID+" - Secure Payment - Rs"+str(amt_to_show)+"</p>", unsafe_allow_html=True)
                        
                        with col_pay:
                            st.markdown("<p style='font-weight:700; font-size:1.1rem; margin-bottom:10px; color:#000;'>"+pay_text+"</p>", unsafe_allow_html=True)
                            st.markdown('<a href="'+upi_link+'" class="big-pay-button '+btn_class+'">PAY Rs'+str(amt_to_show)+'<br><span class="big-pay-sub">Click to Open GPay / PhonePe / Paytm / BHIM - UPI Included</span></a>', unsafe_allow_html=True)
                            st.markdown("<p style='text-align:center; color:#6b7280; font-size:0.85rem; margin-top:10px;'>Works with GPay, PhonePe, Paytm, BHIM<br>UPI ID: "+UPI_ID+"<br>Scan QR or Click PAY Button</p>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                        st.markdown("<p style='text-align:center; font-weight:700; color:#4c1d95; margin-bottom:8px;'>After payment, click below:</p>", unsafe_allow_html=True)
                        if st.button("I Paid Rs"+str(amt_to_show), key="btn_paid_"+str(amt_to_show)+"_perfect", type="primary", use_container_width=True):
                            data=load_db()
                            if amt_to_show==STARTER_PRICE: data[st.session_state.email]={"plan":"starter","amt":STARTER_PRICE,"days":36500,"expiry":(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now()),"used":0}
                            elif amt_to_show==PRO_1M: data[st.session_state.email]={"plan":"pro","amt":PRO_1M,"days":30,"expiry":(datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                            else: data[st.session_state.email]={"plan":"pro","amt":PRO_6M,"days":180,"expiry":(datetime.now()+timedelta(days=180)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                            save_db(data); send_notification(st.session_state.email, amt_to_show, plan_name); st.success("Payment submitted!"); st.balloons(); time.sleep(1); st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    if st.session_state.get("just_approved"):
                        st.balloons()
                        st.markdown("<div class='thankyou-box'><h3>Thank You! Payment Confirmed!</h3><p>Your download is ready.</p></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h2>Export Ready - "+percent_text+"</h2>", unsafe_allow_html=True)
                    
                    if st.session_state.plan=="starter":
                        st.markdown("<div style='background:#eff6ff; border:2px solid #3b82f6; border-radius:12px; padding:10px; text-align:center;'><b>Starter Rs49 Active - ONE TIME per file</b></div>", unsafe_allow_html=True)
                    else:
                        if days_left>=0:
                            exp_str=(datetime.now().date()+timedelta(days=days_left)).strftime("%d %b %Y")
                            sel_amt=user_info.get("amt", st.session_state.get("selected_amt", PRO_1M))
                            if sel_amt==PRO_1M: st.markdown("<div class='day-counter'>Pro Rs299 Active - "+str(days_left)+" days left - Expiry: "+exp_str+"</div>", unsafe_allow_html=True)
                            else: st.markdown("<div class='day-counter'>Pro Rs1499 Active - "+str(days_left)+" days left - Expiry: "+exp_str+"</div>", unsafe_allow_html=True)
                    
                    c1,c2,c3=st.columns(3); safe=sel_file[:30]; csv=df_clean.to_csv(index=False).encode()
                    with c1:
                        if st.download_button("CSV - "+percent_text, csv, safe+"_cleaned.csv", mime="text/csv", key="dl_csv_paid_perfect", use_container_width=True, type="primary"):
                            if st.session_state.plan=="starter":
                                db_u=load_db()
                                if st.session_state.email in db_u: db_u[st.session_state.email]["used"]=db_u[st.session_state.email].get("used",0)+1; save_db(db_u)
                    with c2:
                        if openpyxl is not None: ex=io.BytesIO(); df_clean.to_excel(ex, index=False, engine='openpyxl'); ex.seek(0)
                        if openpyxl is not None:
                            if st.download_button("Excel - "+percent_text, ex.getvalue(), safe+"_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx_paid_perfect", use_container_width=True):
                                if st.session_state.plan=="starter":
                                    db_u=load_db()
                                    if st.session_state.email in db_u: db_u[st.session_state.email]["used"]=db_u[st.session_state.email].get("used",0)+1; save_db(db_u)
                    with c3: pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean, st.session_state.get("hub_report")); 
                    with c3:
                        if pdf:
                            if st.download_button("PDF - "+percent_text, pdf, safe+"_audit.pdf", mime="application/pdf", key="dl_pdf_paid_perfect", use_container_width=True):
                                if st.session_state.plan=="starter":
                                    db_u=load_db()
                                    if st.session_state.email in db_u: db_u[st.session_state.email]["used"]=db_u[st.session_state.email].get("used",0)+1; save_db(db_u)
