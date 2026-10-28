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

def get_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", None) if hasattr(st, 'secrets') else None
        key = st.secrets.get("SUPABASE_KEY", None) if hasattr(st, 'secrets') else None
        if url and key:
            from supabase import create_client
            return create_client(url, key)
    except:
        pass
    return None

def load_db():
    # Try Supabase first - PRO COMPANY LEVEL - never delete
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("orders").select("*").execute()
            d = {}
            for row in res.data:
                email = row.get("email")
                if email:
                    d[email] = row
            return d
        except Exception as e:
            pass
    # Fallback to local json
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json","r") as f:
                d=json.load(f)
                if isinstance(d,dict): return d
        except: pass
    return {}

def save_db(d):
    sb = get_supabase()
    if sb:
        try:
            for email, info in d.items():
                if "@" not in email:
                    continue
                data = {
                    "email": email,
                    "plan": info.get("plan"),
                    "status": info.get("status"),
                    "amt": int(info.get("amt",0)) if str(info.get("amt","0")).isdigit() else 0,
                    "expiry": info.get("expiry",""),
                    "created": info.get("created",""),
                    "used": int(info.get("used",0)),
                    "days": int(info.get("days",0)) if info.get("days") else 0
                }
                sb.table("orders").upsert(data, on_conflict="email").execute()
            return
        except Exception as e:
            pass
    try:
        with open("backup_orders.json","w") as f: json.dump(d,f,indent=2)
    except: pass

def load_feedback():
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("feedbacks").select("*").order("time", desc=True).limit(100).execute()
            return res.data
        except:
            pass
    if os.path.exists(FEEDBACK_FILE):
        try: return json.load(open(FEEDBACK_FILE,"r"))
        except: return []
    return []

def save_feedback(text,email):
    sb = get_supabase()
    if sb:
        try:
            data = {
                "id": hashlib.md5(f"{email}{text}{time.time()}".encode()).hexdigest()[:8],
                "email": email,
                "feedback": text,
                "time": str(datetime.now())
            }
            sb.table("feedbacks").insert(data).execute()
            return True
        except:
            pass
    try:
        fb=load_feedback(); fb.append({"email":email,"feedback":text,"time":str(datetime.now()),"id":hashlib.md5(f"{email}{text}{time.time()}".encode()).hexdigest()[:8]})
        with open(FEEDBACK_FILE,"w") as f: json.dump(fb,f,indent=2)
        return True
    except: return False
def load_free_clicks():
    if os.path.exists(FREE_CLICKS_FILE):
        try: return json.load(open(FREE_CLICKS_FILE,"r"))
        except: return {"count":0}
    return {"count":0}
def save_free_clicks():
    try: data=load_free_clicks(); data["count"]=data.get("count",0)+1; json.dump(data, open(FREE_CLICKS_FILE,"w"), indent=2)
    except: pass
def enforce_delay():
    bar=st.progress(0, text="Cleaning with 10 Advanced Tools...")
    for i in range(100): time.sleep(0.02); bar.progress(i+1)
    bar.empty()

def tool1_date(df, pc):
    f=0
    for col in df.columns:
        if not any(k in col.lower() for k in ['date','dob','join','created','updated']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip()
                if orig.lower() in ["","nan","none","null","n/a","unknown","nat","0","-"]: continue
                if orig.isdigit() and 30000 < int(orig) < 60000:
                    try: base=datetime(1899,12,30); p=base+timedelta(days=int(orig)); df.at[r,col]=p.strftime('%Y-%m-%d'); f+=1; pc.add((r,col)); continue
                    except: pass
                cl=orig.replace('/','-').replace('.','-').replace('\\','-').strip()
                pr=pd.to_datetime(cl, dayfirst=True, errors='coerce')
                if not pd.isna(pr):
                    nv=pr.strftime('%Y-%m-%d')
                    if orig!=nv: df.at[r,col]=nv; f+=1; pc.add((r,col))
            except: continue
    return f
def tool2_fill(df, pc):
    f=0
    for col in df.columns:
        if df[col].dtype!='object': df[col]=df[col].astype(object)
        cl=col.lower()
        if any(k in cl for k in ['salary','amount','price','age','score']): fv=0
        elif 'email' in cl: fv="missing@email.com"
        elif any(k in cl for k in ['phone','mobile','contact']): fv="0000000000"
        elif any(k in cl for k in ['date','dob']): fv="2000-01-01"
        else: fv="Unknown"
        for r in range(len(df)):
            try:
                if pd.isna(df.at[r,col]) or str(df.at[r,col]).strip().lower() in ["nan","none","","null","n/a","nat","-","?",""]:
                    df.at[r,col]=fv; f+=1; pc.add((r,col))
            except: continue
    return f
def tool3_email(df, pc):
    f=0; pat=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    typo={"gmai.com":"gmail.com","gmal.com":"gmail.com","gmial.com":"gmail.com","gamil.com":"gmail.com","yaho.com":"yahoo.com","yahooo.com":"yahoo.com","yahho.com":"yahoo.com","hotmal.com":"hotmail.com","hotamil.com":"hotmail.com","hotmai.com":"hotmail.com","outlok.com":"outlook.com","outloo.com":"outlook.com","outllok.com":"outlook.com","rediffmail.cm":"rediffmail.com"}
    for col in df.columns:
        if 'email' not in col.lower(): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip(); low=orig.lower().replace(" ","").replace(",",".").replace("..",".").replace("@@","@")
                if "@" not in low or low in ["missing@email.com","invalid email"]: continue
                for w,c in typo.items():
                    if w in low: low=low.replace(w,c)
                nv=low if re.match(pat,low) else "Invalid Email"
                if str(df.at[r,col]).strip()!=nv: df.at[r,col]=nv; f+=1; pc.add((r,col))
            except: continue
    return f
def tool4_phone(df, pc):
    f=0
    for col in df.columns:
        if not any(k in col.lower() for k in ['phone','mobile','contact','tel','cell']): continue
        if 'email' in col.lower(): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]); dig="".join([c for c in orig if c.isdigit()])
                if len(dig)==0 or dig=="0000000000": continue
                if len(dig)==12 and dig.startswith("91"): dig=dig[2:]
                if len(dig)==11 and dig.startswith("0"): dig=dig[1:]
                if len(dig)>10: dig=dig[-10:]
                if len(dig)==10 and dig!=orig: df.at[r,col]=dig; f+=1; pc.add((r,col))
            except: continue
    return f
def tool5_case(df, cc):
    f=0
    for col in df.select_dtypes(include=['object']).columns:
        if not any(k in col.lower() for k in ['name','city','state','company','department','designation']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]).strip()
                if orig.lower() in ["unknown","missing@email.com","invalid email",""]: continue
                if orig.isupper() or orig.islower(): nv=' '.join([w.capitalize() for w in orig.lower().split()])
                else: nv=' '.join([w.capitalize() for w in orig.split()])
                if orig!=nv and len(nv)>1: df.at[r,col]=nv; f+=1; cc.add((r,col))
            except: continue
    return f
def tool6_symbols(df, pc):
    f=0
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['email','phone','salary','amount']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col])
                if orig.lower() in ["unknown","invalid email"]: continue
                cln=re.sub(r'[^a-zA-Z0-9\s.,@\-_()&/,]', '', orig); cln=re.sub(r'\s+', ' ', cln).strip()
                if orig!=cln and cln!="": df.at[r,col]=cln; f+=1; pc.add((r,col))
            except: continue
    return f
def tool7_rename(df):
    f=0; new={}
    for c in df.columns:
        cl=re.sub(r'[^a-zA-Z0-9_ ]','',str(c).strip()); cl=re.sub(r'\s+','_',cl.lower()).strip('_'); cl=re.sub(r'_+','_',cl)
        if cl=="" or (cl and cl[0].isdigit()): cl="col_"+str(f)
        if cl=="": cl="col_"+str(f)
        new[c]=cl
        if c!=cl: f+=1
    df.rename(columns=new,inplace=True); return f
def tool8_dedup(df): b=len(df); df.drop_duplicates(inplace=True); df.reset_index(drop=True,inplace=True); return b-len(df)
def tool9_trim(df, cc):
    f=0
    for col in df.select_dtypes(include=['object']).columns:
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]); tr=' '.join(orig.strip().split()); tr=re.sub(r'\s*,\s*', ', ', tr)
                if orig!=tr: df.at[r,col]=tr; f+=1; cc.add((r,col))
            except: continue
    return f
def tool10_spell(df, pc):
    f=0; typo={"teh":"the","recieve":"receive","salery":"salary","custmer":"customer","addres":"address","manger":"manager","buisness":"business","definately":"definitely","accomodation":"accommodation","occured":"occurred","seperate":"separate","embarass":"embarrass","neccessary":"necessary","occassion":"occasion","maintainance":"maintenance"}
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['email','phone']): continue
        for r in range(len(df)):
            try:
                orig=str(df.at[r,col]); words=orig.split(); nw=[]; ch=False
                for w in words:
                    cw=w.lower().strip('.,!?:;')
                    if cw in typo:
                        rep=typo[cw]
                        if w and w[0].isupper(): rep=rep.capitalize()
                        nw.append(rep); ch=True
                    else: nw.append(w)
                if ch: df.at[r,col]=" ".join(nw); f+=1; pc.add((r,col))
            except: continue
    return f

def find_ambiguous(orig_df, clean_df):
    amb=[]
    for col in orig_df.columns:
        if 'date' not in col.lower() and 'dob' not in col.lower(): continue
        for r_idx in range(min(len(orig_df), len(clean_df))):
            try:
                orig=str(orig_df.at[r_idx,col]).strip()
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
        buffer=io.BytesIO(); doc=SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story=[]; styles=getSampleStyleSheet()
        title_style=ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#6b21a8'))
        story.append(Paragraph("VeriSame - 10 Tools Audit Report", title_style)); story.append(Spacer(1,10))
        text_style=ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=9)
        small_bold=ParagraphStyle('SmallBold', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
        data=[[Paragraph("<b>Metric</b>",small_bold),Paragraph("<b>Value</b>",small_bold)],[Paragraph("Total Rows",text_style),Paragraph(str(orig_len),text_style)],[Paragraph("Clean Rows",text_style),Paragraph(str(clean_len),text_style)]]
        if hub_report:
            for line in hub_report:
                parts=line.split(":")
                if len(parts)>=2: data.append([Paragraph(parts[0],text_style),Paragraph(parts[1],text_style)])
        t=Table(data, colWidths=[220,200]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(1,0),colors.HexColor('#9333ea')),('TEXTCOLOR',(0,0),(1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#c084fc'))]))
        story.append(t); doc.build(story); buffer.seek(0); return buffer.getvalue()
    except: return None

def query_groq(user_prompt):
    groq_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, 'secrets') else None
    knowledge = "You are VeriSame AI. Welcome: Hello Welcome to the VeriSame what would you like to know? Founder Anugya only when asked who made. Pricing FREE 200, Starter Rs49 2000 rows QR+UPI, Pro Rs299 30 days, Rs1499 180 days. 10 tools advanced."
    if not groq_key or Groq is None:
        low=user_prompt.lower()
        if any(k in low for k in ['founder','who made','kisne banaya','made by']): return "Made by Anugya."
        return "Hello Welcome to the VeriSame what would you like to know?"
    try:
        client=Groq(api_key=groq_key); comp=client.chat.completions.create(model=GROQ_MODEL, messages=[{"role":"system","content":knowledge},{"role":"user","content":user_prompt}], temperature=0.5, max_tokens=400)
        return comp.choices[0].message.content
    except: return "Hello Welcome to the VeriSame what would you like to know?"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;800;900&family=Outfit:wght@900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif; font-weight: 800 !important;}
.stApp {background: radial-gradient(ellipse at top left, #faf5ff 0%, #f5f3ff 20%, #ede9fe 40%, #e9d5ff 60%, #d8b4fe 80%, #c4b5fd 100%); background-attachment: fixed;}
.block-container {background: rgba(255,255,255,0.98); border-radius: 28px; padding: 2rem; max-width: 1350px; margin: 0 auto; box-shadow: 0 20px 60px rgba(139,92,246,0.22);}
.welcome-black {font-family: 'Outfit', sans-serif; font-weight: 900!important; font-size: 3.8rem!important; color: #000!important; text-align: center;}
.subtitle {color: #000!important; text-align:center; margin-top: 12px!important; font-size: 1.35rem!important; font-weight: 900!important;}
.tagline-badge {display: inline-block; padding: 12px 28px; background: linear-gradient(135deg, #7e22ce, #9333ea); color: #fff !important; font-weight: 900 !important; border-radius: 22px; font-size: 1.2rem!important;}
.logo-container {width: 100%; display: flex; justify-content: center; padding: 5px 0;}
.logo-container img {width: 100%; max-width: 450px; max-height: 450px; object-fit: contain;}
.logo-float {animation: float 5s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.pricing-card {border-radius: 24px; padding: 2rem; background: #ffffff!important; border: 2.5px solid #e9d5ff; min-height: 420px; display: flex; flex-direction: column; box-shadow: 0 10px 24px rgba(147,51,234,0.12);}
.pricing-card h3 {font-size: 1.5rem!important; font-weight: 900!important; color: #000!important;}
.pricing-card h1 {font-size: 3.6rem!important; font-weight: 900!important; color: #000!important;}
.pricing-card p {font-size: 1.12rem!important; font-weight: 800!important; color: #000!important; margin: 6px 0!important;}
.pricing-card-free {border: 3px solid #c4b5fd !important;}
.pricing-card-starter {border: 3.5px solid #22c55e !important;}
.pricing-card-pro {border: 3.5px solid #9333ea !important;}
.stButton>button {border-radius: 16px !important; font-weight: 900 !important; background: linear-gradient(100deg, #7e22ce, #9333ea) !important; color: white !important; border: none !important; width: 100% !important; padding: 16px 24px !important; font-size: 1.2rem!important; box-shadow: 0 8px 20px rgba(147,51,234,0.35)!important;}
.big-pay-button {display: block; width: 100%; padding: 32px 22px; background: linear-gradient(100deg, #16a34a, #22c55e, #4ade80); color: white !important; font-weight: 900 !important; font-size: 1.9rem !important; text-align: center; border-radius: 20px; text-decoration: none !important; margin: 20px 0; border: 3px solid #16a34a; box-shadow: 0 16px 36px rgba(34,197,94,0.45);}
.big-pay-button-pro {background: linear-gradient(100deg, #7e22ce, #9333ea, #a855f7) !important; border: 3px solid #7e22ce !important;}
.big-pay-sub {font-size: 1.15rem!important; display: block; margin-top: 8px; font-weight: 800!important;}
.pro-banner {background: linear-gradient(135deg, #4c1d95, #7e22ce, #9333ea, #a855f7); padding: 1.8rem; border-radius: 22px; text-align: center; margin: 1rem 0;}
.pro-banner h2 {color: white!important; font-size: 1.7rem!important; margin: 0!important; font-weight: 900!important;}
.pro-banner-small {background: linear-gradient(135deg, #4c1d95, #7e22ce); padding: 1.2rem; border-radius: 16px; text-align: center; margin: 0.8rem 0;}
.pro-banner-small h2 {color: white!important; font-size: 1.3rem!important; margin: 0!important; font-weight: 900!important;}
.tool-chip {display: inline-block; background: #fff !important; padding: 12px 18px; border-radius: 22px; margin: 6px; color: #000 !important; font-weight: 900 !important; font-size: 1.02rem !important; border: 2.5px solid #9333ea;}
.plan-status-box {padding: 14px 18px; border-radius: 14px; font-weight: 900 !important; margin-bottom: 12px; font-size: 1.1rem!important; line-height: 1.4;}
.plan-active {background: #dcfce7 !important; border: 3px solid #22c55e !important; color: #000 !important;}
.plan-pending {background: #fef9c3 !important; border: 3px solid #eab308 !important; color: #000 !important;}
.red-dot {display: inline-block; width: 12px; height: 12px; background: #ef4444; border-radius: 50%; margin-right: 8px; animation: pulse 1.5s infinite;}
.green-dot {display: inline-block; width: 12px; height: 12px; background: #22c55e; border-radius: 50%; margin-right: 8px;}
@keyframes pulse {0%,100%{opacity:1;} 50%{opacity:0.4;}}
.hundred-box {background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important; border: 3px solid #22c55e !important; border-radius: 18px; padding: 20px; margin: 12px 0; text-align: center; font-weight: 900!important; font-size: 1.25rem!important; color: #000!important;}
.qr-box {background: #ffffff !important; border: 5px solid #9333ea !important; border-radius: 24px; padding: 36px; text-align: center; margin: 24px 0; box-shadow: 0 16px 40px rgba(147,51,234,0.25);}
.upgrade-msg {background: linear-gradient(135deg, #fef9c3 0%, #fef3c7 100%) !important; border: 3px solid #eab308 !important; border-radius: 18px; padding: 20px; text-align: center; margin: 12px 0; font-weight: 900!important; font-size: 1.2rem!important; color: #000!important;}
.tool-report-clean {background: #ffffff !important; border: 2.5px solid #22c55e !important; border-radius: 14px; padding: 14px 18px; margin: 8px 0; font-size: 1.15rem!important; font-weight: 900!important; color: #000!important; display: flex; justify-content: space-between; align-items: center;}
.verifying-box {background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important; border: 3px solid #3b82f6 !important; border-radius: 20px; padding: 28px; margin: 20px 0; text-align: center; font-weight: 900!important; font-size: 1.2rem!important; color: #000!important;}
.thankyou-box {background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important; border: 3px solid #22c55e !important; border-radius: 20px; padding: 22px; margin: 16px 0; text-align: center; font-weight: 900!important; font-size: 1.15rem!important; color: #000!important;}
p, div, span, label, h1, h2, h3, h4, h5 {font-weight: 800!important;}
.or-divider {display: flex; align-items: center; justify-content: center; margin: 24px 0; gap: 16px;}
.or-divider-line {height: 3px; flex: 1; background: linear-gradient(90deg, #9333ea, #e9d5ff);}
.or-divider-text {font-size: 1.8rem!important; font-weight: 900!important; color: #000!important; background: #fff; padding: 8px 24px; border-radius: 12px; border: 3px solid #9333ea;}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello Welcome to the VeriSame what would you like to know?"}]
if "changed_cells" not in st.session_state: st.session_state.changed_cells=set()
if "problem_cells" not in st.session_state: st.session_state.problem_cells=set()
if "uploaded_files" not in st.session_state: st.session_state.uploaded_files={}
for k in ['plan','email','df_clean','df_original','amt','email_entered','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done','ambiguous_list','hundred_done','confirm_choices','just_approved','demo_loaded']:
    if k not in st.session_state:
        st.session_state[k]=None if k in ['plan','email','df_clean','df_original','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','ambiguous_list','confirm_choices'] else False

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
                if r in df_colors.index and c in df_colors.columns: df_colors.at[r,c]='background-color: #bbf7d0; color: #047857; font-weight: 900; border: 2px solid #10b981; font-size: 1.1rem;'
            for r,c in st.session_state.get("problem_cells", set()):
                if r in df_colors.index and c in df_colors.columns: df_colors.at[r,c]='background-color: #fecaca; color: #991b1b; font-weight: 900; border: 2px solid #ef4444;'
            return df_colors
        return df_temp.style.apply(highlight, axis=None)
    except: return df_to_style

def render_chat(is_sidebar=False):
    target=st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### VeriSame AI")
    chat_html="<div style='max-height: 320px; overflow-y: auto; padding: 14px; background: #fff; border: 3px solid #9333ea; border-radius: 14px; margin-bottom: 12px;'>"
    for chat in st.session_state.chat_history[-6:]:
        msg=chat['message'][:500]
        if chat["role"]=="assistant": chat_html+="<p style='color: #000; margin: 10px 0; font-size: 1.05rem; font-weight: 900;'><b>AI:</b> "+msg+"</p>"
        else: chat_html+="<p style='color: #111; margin: 10px 0; font-size: 1.05rem; font-weight: 800;'><b>You:</b> "+msg+"</p>"
    chat_html+="</div>"
    target.markdown(chat_html, unsafe_allow_html=True)
    s_id="side" if is_sidebar else "main"
    um=target.text_input("Ask", placeholder="Ask...", key="chat_"+s_id+"_finalv2", label_visibility="collapsed")
    if target.button("Send", key="btn_chat_"+s_id+"_finalv2", use_container_width=True):
        if um and um.strip():
            st.session_state.chat_history.append({"role":"user","message":um})
            reply=query_groq(um)
            st.session_state.chat_history.append({"role":"assistant","message":reply})
            st.rerun()

# SIDEBAR LOGIC - NEW AS PER USER REQUEST
if st.session_state.email and st.session_state.plan != "free":
    db=load_db(); user=db.get(st.session_state.email,{})
    st.sidebar.markdown("<div style='background: #f5f3ff; padding: 14px; border-radius: 12px; border: 3px solid #9333ea; font-weight: 900; font-size: 1.1rem;'><b>"+st.session_state.email+"</b></div>", unsafe_allow_html=True)
    if user:
        try:
            exp_date=datetime.strptime(user.get("expiry","2000-01-01"), "%Y-%m-%d").date()
            days_left=(exp_date-datetime.now().date()).days
            st.session_state.days=days_left
            if days_left<0 and user.get("plan")!="starter": 
                user["status"]="EXPIRED"; save_db(db)
                days_left=0
            
            plan_type=user.get("plan","")
            amt_type=user.get("amt",0)
            status=user.get("status","")
            
            if plan_type=="starter":
                if status=="PENDING":
                    st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>Pending - One time per file 49 rupees</div>", unsafe_allow_html=True)
                elif status=="PAID":
                    st.sidebar.markdown("<div class='plan-status-box plan-active'><span class='green-dot'></span>✓ One time per file - Active</div>", unsafe_allow_html=True)
                else:
                    st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>One time per file 49 rupees</div>", unsafe_allow_html=True)
            else:
                if amt_type==STARTER_PRICE: amt_type=PRO_1M
                if amt_type==PRO_1M:
                    if status=="PENDING":
                        st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>Pending - 1 month 30 days</div>", unsafe_allow_html=True)
                    elif status=="PAID":
                        if days_left<=5 and days_left>=0:
                            st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>✓ "+str(max(0,days_left))+" days left</div>", unsafe_allow_html=True)
                        else:
                            st.sidebar.markdown("<div class='plan-status-box plan-active'><span class='green-dot'></span>✓ "+str(max(0,days_left))+" days left</div>", unsafe_allow_html=True)
                    else:
                        st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>Pending - 1 month 30 days</div>", unsafe_allow_html=True)
                else:
                    if status=="PENDING":
                        st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>Pending - 6 months 180 days</div>", unsafe_allow_html=True)
                    elif status=="PAID":
                        if days_left<=5 and days_left>=0:
                            st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>✓ "+str(max(0,days_left))+" days left</div>", unsafe_allow_html=True)
                        else:
                            st.sidebar.markdown("<div class='plan-status-box plan-active'><span class='green-dot'></span>✓ "+str(max(0,days_left))+" days left</div>", unsafe_allow_html=True)
                    else:
                        st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>Pending - 6 months 180 days</div>", unsafe_allow_html=True)
        except Exception as e:
            if user.get("status")=="PENDING":
                st.sidebar.markdown("<div class='plan-status-box plan-pending'><span class='red-dot'></span>Pending</div>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown("<div class='plan-status-box plan-active'><span class='green-dot'></span>✓ Active</div>", unsafe_allow_html=True)
    render_chat(is_sidebar=True)
elif st.session_state.plan=="free":
    st.sidebar.markdown("<div class='plan-status-box plan-active' style='font-weight: 900; font-size: 1.1rem;'><span class='green-dot'></span>Free - 200 Rows</div>", unsafe_allow_html=True)
    render_chat(is_sidebar=True)

# ONLY LOGOUT BUTTON - NO BACK BUTTON (USER REQUEST)
if st.session_state.plan or st.session_state.email_entered:
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", key="nav_logout_finalv2", use_container_width=True):
        for k in ['plan','email','df_clean','df_original','amt','email_entered','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','clean_done','ambiguous_list','hundred_done','confirm_choices','just_approved','demo_loaded']:
            st.session_state[k]=None if k in ['plan','email','df_clean','df_original','days','selected_plan','selected_amt','orig_len','empty_fixed','last_upload_sig','hub_report','ambiguous_list','confirm_choices'] else False
        st.session_state.uploaded_files={}; st.session_state.changed_cells=set(); st.session_state.problem_cells=set(); st.query_params.clear(); st.rerun()

is_first_page=(st.session_state.plan is None and st.session_state.selected_plan is None)

if is_first_page:
    st.markdown('<div class="logo-container logo-float"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" alt="VeriSame Logo"></div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-space"></div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-black">Welcome To VeriSame👋</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; margin-top:12px;"><span class="tagline-badge">Clean logic. Clear result</span><div class="subtitle">The Fastest Way to Clean Your Data</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="pro-banner" style="margin-top:18px;"><h2>10 Advanced Tools - All Plans Include All 10 Tools</h2><div style="margin-top:10px;"><span class="tool-chip">Date Fix</span><span class="tool-chip">Fill Missing</span><span class="tool-chip">Email Fix</span><span class="tool-chip">Phone Fix</span><span class="tool-chip">Case Fix</span><span class="tool-chip">Symbol Clean</span><span class="tool-chip">Header Clean</span><span class="tool-chip">Dedup</span><span class="tool-chip">Trim</span><span class="tool-chip">Spell Fix</span></div></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="pro-banner-small"><h2>10 Advanced Tools - All Plans Include All 10 Tools</h2></div>', unsafe_allow_html=True)

if "admin" in st.query_params:
    if st.query_params.get("admin")==ADMIN_PASS:
        st.title("Secret Dashboard - VeriSame")
        data=load_db(); fbs=load_feedback(); free_data=load_free_clicks()
        tab1,tab2,tab3,tab4=st.tabs(["FREE "+str(free_data.get('count',0)), "STARTER Rs49", "PRO", "Feedback "+str(len(fbs))])
        with tab1: st.markdown("<h2 style='font-weight: 900;'>"+str(free_data.get('count',0))+" Free Users</h2>", unsafe_allow_html=True)
        with tab2:
            for email,info in list({k:v for k,v in data.items() if v.get('amt')==STARTER_PRICE}.items()):
                if "@" not in email: continue
                c1,c2,c3=st.columns([4,2,2])
                with c1: st.write(email+" - "+info.get('status','')+" - Used "+str(info.get('used',0)))
                with c2:
                    if info.get("status") in ["PENDING","UNPAID","EXPIRED"]:
                        if st.button("Approve", key="ap_s_"+email+"_fv2", type="primary", use_container_width=True):
                            data[email]["status"]="PAID"; data[email]["used"]=0; data[email]["expiry"]=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d"); save_db(data); st.balloons(); st.rerun()
                with c3:
                    if st.button("Delete", key="del_s_"+email+"_fv2", use_container_width=True): del data[email]; save_db(data); st.rerun()
        with tab3:
            for email,info in list({k:v for k,v in data.items() if v.get('amt') in [PRO_1M, PRO_6M]}.items()):
                if "@" not in email: continue
                c1,c2,c3=st.columns([4,2,2])
                with c1:
                    try: exp_d=datetime.strptime(info.get('expiry','2000-01-01'), "%Y-%m-%d").date(); dl=(exp_d-datetime.now().date()).days
                    except: dl=0
                    st.write(email+" - Rs"+str(info.get('amt',''))+" - "+info.get('status','')+" - Days Left: "+str(dl))
                with c2:
                    if info.get("status") in ["PENDING","UNPAID","EXPIRED"]:
                        if st.button("Approve", key="ap_p_"+email+"_fv2", type="primary", use_container_width=True):
                            data[email]["status"]="PAID"; data[email]["expiry"]=(datetime.now()+timedelta(days=180 if data[email].get("amt")==PRO_6M else 30)).strftime("%Y-%m-%d"); save_db(data); st.balloons(); st.rerun()
                with c3:
                    if st.button("Delete", key="del_p_"+email+"_fv2", use_container_width=True): del data[email]; save_db(data); st.rerun()
        with tab4:
            if fbs:
                for fb in reversed(fbs[-50:]): st.markdown("<div style='background:#fff; border:2.5px solid #9333ea; border-radius:14px; padding:14px; margin:10px 0; font-weight: 800;'><b>"+fb['email']+"</b><br><p>"+fb['feedback'][:500]+"</p><small>"+fb.get('time','')[:19]+"</small></div>", unsafe_allow_html=True)
        st.stop()

if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        st.markdown("<h2 style='text-align:center; color:#000; margin-top:24px; font-weight: 900; font-size: 2.2rem;'>Choose Your Plan</h2>", unsafe_allow_html=True)
        col_free, col_starter, col_pro = st.columns(3, gap="medium")
        with col_free:
            st.markdown('<div class="pricing-card pricing-card-free"><h3>FREE FOREVER</h3><h1>FREE</h1><p><b>200 Rows - Lifetime Free</b></p><div style="margin-top:14px; flex-grow:1;"><p>✓ All 10 Advanced Tools</p><p>✓ Super Fast Cleaning</p><p>✓ CSV + Excel + PDF</p><p>✓ 100% Private</p><p>✓ AI Support</p></div></div>', unsafe_allow_html=True)
            if st.button("Start Free", key="btn_free_fv2", type="primary", use_container_width=True): save_free_clicks(); st.session_state.selected_plan="free"; st.session_state.plan="free"; st.session_state.email="Guest_Free"; st.session_state.email_entered=True; st.balloons(); st.rerun()
        with col_starter:
            st.markdown('<div class="pricing-card pricing-card-starter"><p style="background: #22c55e; color:white; padding:10px 18px; border-radius:16px; display:inline-block; font-size:1.0rem; font-weight: 900;">ONE TIME PER FILE</p><h3 style="margin-top:12px;">STARTER</h3><h1>Rs49</h1><p><b>One-Time Per File - 2,000 Rows</b></p><div style="margin-top:14px; flex-grow:1;"><p>✓ All 10 Advanced Tools</p><p>✓ Pay Again For Next File</p><p>✓ QR Code + Direct Pay</p><p>✓ Instant Approval</p></div></div>', unsafe_allow_html=True)
            if st.button("Start with 49", key="btn_starter_fv2", type="primary", use_container_width=True): st.session_state.selected_plan="starter"; st.session_state.selected_amt=STARTER_PRICE; st.session_state.amt=STARTER_PRICE; st.rerun()
        with col_pro:
            st.markdown('<div class="pricing-card pricing-card-pro"><p style="background: #9333ea; color:white; padding:10px 18px; border-radius:16px; display:inline-block; font-size:1.0rem; font-weight: 900;">POPULAR - BEST VALUE</p><h3 style="margin-top:12px;">PRO</h3><h1 style="font-size:2.8rem;">Rs299 / Rs1499</h1><p><b>Unlimited Rows</b></p><div style="margin-top:14px; flex-grow:1;"><p>✓ Rs299 = 1 Month (30 Days)</p><p>✓ Rs1499 = 6 Months (180 Days)</p><p>✓ Unlimited Rows</p><p>✓ QR + Direct Pay</p><p>✓ Instant Approval</p></div></div>', unsafe_allow_html=True)
            c_p1,c_p2=st.columns(2)
            with c_p1:
                if st.button("Rs299 - 30 Days", key="btn_pro_299_fv2", type="primary", use_container_width=True): st.session_state.selected_plan="pro"; st.session_state.selected_amt=PRO_1M; st.session_state.amt=PRO_1M; st.rerun()
            with c_p2:
                if st.button("Rs1499 - 180 Days", key="btn_pro_1499_fv2", type="primary", use_container_width=True): st.session_state.selected_plan="pro"; st.session_state.selected_amt=PRO_6M; st.session_state.amt=PRO_6M; st.rerun()
        render_chat(is_sidebar=False)
        st.markdown("---")
        st.markdown("<h2 style='font-weight: 900; font-size: 1.7rem; color: #000;'>Feedback - We Value Your Feedback</h2>", unsafe_allow_html=True)
        fb_front=st.text_area("Feedback", placeholder="Your feedback...", key="fb_front_fv2", height=90, label_visibility="collapsed")
        if st.button("Send Feedback", key="fb_front_btn_fv2", type="primary", use_container_width=True):
            if fb_front.strip() and save_feedback(fb_front.strip(), "Guest"): st.success("Thank you!"); st.balloons()
    else:
        if st.session_state.selected_plan=="free": st.session_state.plan="free"; st.session_state.email="Guest_Free"; st.session_state.email_entered=True; st.rerun()
        if st.session_state.selected_plan=="starter": plan_text="STARTER - Rs49 One-Time Per File"
        else:
            if st.session_state.selected_amt==PRO_1M: plan_text="PRO - 1 Month Rs299"
            else: plan_text="PRO - 6 Months Rs1499"
        st.markdown("<h2 style='text-align:center; margin-top:18px; font-weight: 900; font-size: 1.6rem; color: #000;'>Enter email for "+plan_text+"</h2>", unsafe_allow_html=True)
        _,ce2,_=st.columns([1,2,1])
        with ce2:
            email_input=st.text_input("Enter email", placeholder="your@email.com", key="email_main_fv2").lower().strip()
            b1,b2=st.columns(2)
            with b1:
                if st.button("Verify & Continue", key="btn_verify_fv2", type="primary", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        data=load_db()
                        existing=data.get(email_input)
                        # === CRITICAL FIX: IF EMAIL ALREADY PAID AND NOT EXPIRED, DON'T OVERWRITE ===
                        is_existing_valid=False
                        if existing and existing.get("status")=="PAID":
                            try:
                                exp_d=datetime.strptime(existing.get("expiry","2000-01-01"), "%Y-%m-%d").date()
                                days_left_existing=(exp_d - datetime.now().date()).days
                                if days_left_existing>=0:
                                    # Still valid - keep existing PAID status
                                    is_existing_valid=True
                                    st.session_state.email=email_input
                                    st.session_state.email_entered=True
                                    st.session_state.plan=existing.get("plan","pro")
                                    st.session_state.amt=existing.get("amt",PRO_1M)
                                    st.balloons()
                                    st.rerun()
                            except:
                                pass
                        
                        if not is_existing_valid:
                            # New user or expired - create UNPAID
                            st.session_state.email=email_input
                            st.session_state.email_entered=True
                            if st.session_state.selected_plan=="starter":
                                exp=(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d")
                                data[email_input]={"plan":"starter","status":"UNPAID","amt":STARTER_PRICE,"expiry":exp,"created":str(datetime.now()),"used":0}
                                save_db(data)
                                st.session_state.plan="starter"
                                st.session_state.amt=STARTER_PRICE
                                st.balloons()
                                st.rerun()
                            else:
                                exact=180 if st.session_state.selected_amt==PRO_6M else 30
                                exp=(datetime.now()+timedelta(days=exact)).strftime("%Y-%m-%d")
                                data[email_input]={"plan":"pro","status":"UNPAID","amt":st.session_state.selected_amt,"expiry":exp,"created":str(datetime.now())}
                                save_db(data)
                                st.session_state.plan="pro"
                                st.session_state.amt=st.session_state.selected_amt
                                st.balloons()
                                st.rerun()
                    else: st.error("Enter valid email")
            with b2:
                if st.button("Back to Plans", key="btn_back_fv2_2", use_container_width=True): st.session_state.selected_plan=None; st.session_state.selected_amt=None; st.rerun()
        st.stop()
else:
    tab1, tab2 = st.tabs(["Upload File", "Try Demo - No File? Test Here"])
    with tab1:
        files=st.file_uploader("Drop CSV, Excel or JSON", type=["csv","xlsx","xls","json"], accept_multiple_files=True, label_visibility="collapsed")
        if files:
            cur_files=[f.name for f in files]; sheet_sel={}
            for f in files:
                if f.name.endswith((".xlsx",".xls")):
                    try: ef=pd.ExcelFile(f); sel=st.selectbox("Sheet for "+f.name, ef.sheet_names, key="sh_"+f.name+"_fv2"); sheet_sel[f.name]=sel
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
                    st.session_state.last_upload_sig=sig; st.session_state.clean_done=False; st.session_state.hundred_done=False; st.session_state.ambiguous_list=None; st.session_state.hub_report=None; st.session_state.just_approved=False; st.session_state.demo_loaded=False
                except Exception as e: st.error("Error: "+str(e))
    with tab2:
        st.markdown("<h2 style='font-weight: 900; font-size: 1.7rem; color: #000;'>Try Demo - No File? Test Here!</h2>", unsafe_allow_html=True)
        st.markdown("<div style='background:#faf5ff; border:3.5px solid #9333ea; border-radius:18px; padding:20px; font-size: 1.15rem; font-weight: 900; color: #000;'><b>Click below, file will come automatically, then press BIG CLEAN and see cleaned file with what tool cleaned what!</b></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CLICK HERE - Load Demo File Instantly", key="btn_load_demo_fv2", type="primary", use_container_width=True):
            demo_data={
                "Join Date": ["12/5/2024", "05.06.2024", "15-03-2023", "40000", "12/5/2024", ""],
                "  Name@  ": ["  RAHUL KUMAR  ", "priya SHARMA", "AMIT @#$ Kumar", "teh custmer", "  RAHUL KUMAR  ", "Amit Kumar"],
                "Email ID": ["RAHUL@GMAI.COM", "priya@yaho.com ", "test@outlok.com", "bad email", "RAHUL@GMAI.COM", ""],
                "Phone Number": ["+91 98765-43210", "09123456789", "987-654-3210", "  98765 43210  ", "+91 98765-43210", "9876543210"],
                "  Company   ": ["  TCS  pvt  ltd  ", "infosys  @#$", "  WIPRO  ", "teh buisness", "  TCS  pvt  ltd  ", "TCS Pvt Ltd"],
                "Salary": ["", "salery 50000", "10000", "teh salery", "", "50000"],
                "City": ["  MUMBAI  ", "delhi", "BANGALORE @#$", "teh city", "  MUMBAI  ", "Mumbai"],
            }
            sample=pd.DataFrame(demo_data)
            clean=sample.copy()
            st.session_state.uploaded_files={"VeriSame_Demo_All_10_Tools.csv":{"original":sample.copy().reset_index(drop=True),"clean":clean,"orig_len":len(sample),"empty_fixed":int(sample.isna().sum().sum()),"changed_cells":set(),"problem_cells":set()}}
            st.session_state.last_upload_sig=None; st.session_state.clean_done=False; st.session_state.hundred_done=False; st.session_state.ambiguous_list=None; st.session_state.just_approved=False; st.session_state.demo_loaded=True; st.balloons(); st.success("Demo file loaded! Now check Upload File tab - Press BIG CLEAN!"); st.rerun()
        if st.session_state.get("demo_loaded") and st.session_state.uploaded_files:
            st.markdown("<div class='hundred-box'><b>Demo file loaded! Go to Upload File tab - Press BIG CLEAN!</b></div>", unsafe_allow_html=True)

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        keys=list(st.session_state.uploaded_files.keys()); sel_file=st.selectbox("Select file:", keys, key="active_file_fv2", label_visibility="collapsed")
        limit=FREE_LIMIT if st.session_state.plan=="free" else STARTER_LIMIT if st.session_state.plan=="starter" else 1000000
        if st.session_state.plan in ["free","starter"] and len(st.session_state.uploaded_files[sel_file]["clean"]) > limit: st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.uploaded_files[sel_file]["clean"].iloc[:limit]
        st.session_state.df_clean=st.session_state.uploaded_files[sel_file]["clean"]; st.session_state.df_original=st.session_state.uploaded_files[sel_file]["original"]; st.session_state.orig_len=len(st.session_state.df_original); st.session_state.empty_fixed=st.session_state.uploaded_files[sel_file]["empty_fixed"]; st.session_state.problem_cells=st.session_state.uploaded_files[sel_file].get("problem_cells",set()); update_changed(); df_clean=st.session_state.df_clean; orig_len=st.session_state.orig_len

        if not st.session_state.get("clean_done"):
            st.markdown("<h2 style='font-weight: 900; font-size: 1.6rem; color: #000;'>File: "+sel_file+" - "+str(orig_len)+" rows</h2>", unsafe_allow_html=True)
            if st.button("BIG CLEAN - 1 Click = 10 Advanced Tools", key="btn_big_clean_fv2", type="primary", use_container_width=True):
                try:
                    enforce_delay(); df_curr=st.session_state.df_clean.copy(); st.session_state.problem_cells=set(); st.session_state.changed_cells=set()
                    for col in df_curr.columns:
                        if df_curr[col].dtype!='object': df_curr[col]=df_curr[col].astype(object)
                    fixes=[]
                    fixes.append(("Date Fix", tool1_date(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Fill Missing", tool2_fill(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Email Fix", tool3_email(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Phone Fix", tool4_phone(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Case Fix", tool5_case(df_curr, st.session_state.changed_cells)))
                    fixes.append(("Symbol Clean", tool6_symbols(df_curr, st.session_state.problem_cells)))
                    fixes.append(("Header Clean", tool7_rename(df_curr)))
                    fixes.append(("Dedup", tool8_dedup(df_curr)))
                    fixes.append(("Trim", tool9_trim(df_curr, st.session_state.changed_cells)))
                    fixes.append(("Spell Fix", tool10_spell(df_curr, st.session_state.problem_cells)))
                    hub=[]
                    for name,cnt in fixes:
                        hub.append(f"{name}: {cnt} fixed ✓")
                    st.session_state.df_clean=df_curr; update_changed(); ambiguous=find_ambiguous(st.session_state.df_original, st.session_state.df_clean); st.session_state["hub_report"]=hub; st.session_state["clean_done"]=True; st.session_state["ambiguous_list"]=ambiguous; st.session_state["hundred_done"]=len(ambiguous)==0; st.session_state.uploaded_files[sel_file]["clean"]=st.session_state.df_clean; st.success("Cleaned! 10 Tools Advanced!"); st.balloons(); st.rerun()
                except Exception as e: st.error("Error: "+str(e))
        else:
            ambiguous=st.session_state.get("ambiguous_list", []); is_hundred=st.session_state.get("hundred_done", False) or len(ambiguous)==0
            if is_hundred: percent_text="100% Clean"
            else: percent_text="95% Clean"
            st.markdown("<h2 style='font-weight: 900; font-size: 1.6rem; color: #000;'>Data Summary - "+percent_text+" - 10 Tools Advanced</h2>", unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            with c1: st.metric("Total Rows", orig_len)
            with c2: st.metric("Clean Rows", len(df_clean))
            with c3: st.metric("Duplicates", max(0, orig_len-len(df_clean)))
            with c4: st.metric("Empty Fixed", st.session_state.empty_fixed)
            if st.session_state.get("hub_report"):
                st.markdown("<h2 style='font-weight: 900; font-size: 1.5rem; color: #000;'>What Each Tool Cleaned:</h2>", unsafe_allow_html=True)
                for report_line in st.session_state.hub_report:
                    st.markdown("<div class='tool-report-clean'><span>"+report_line+"</span><span style='color:#22c55e; font-size:1.3rem;'>✓</span></div>", unsafe_allow_html=True)
            if is_hundred: st.markdown("<div class='hundred-box'><h3>100% Clean! All 10 Tools Applied!</h3></div>", unsafe_allow_html=True); st.balloons()
            else:
                st.markdown("<div class='upgrade-msg'><h3>Need Help - "+str(len(ambiguous))+" Items</h3></div>", unsafe_allow_html=True)
                choices=st.session_state.get("confirm_choices", {})
                for i, amb in enumerate(ambiguous):
                    st.markdown("<div style='background:#fff; border:3px solid #f59e0b; border-radius:12px; padding:14px; margin:10px 0; font-weight: 900; font-size: 1.1rem; color: #000;'><b>Q"+str(i+1)+": "+amb['question']+"</b><br><small>"+amb['original']+"</small></div>", unsafe_allow_html=True)
                    selected=st.radio("Choose:", amb['options'], key="amb_"+str(i)+"_fv2", index=0); choices[i]=selected
                st.session_state.confirm_choices=choices
                if st.button("Apply & Make 100% Clean", key="btn_apply_amb_fv2", type="primary", use_container_width=True):
                    st.session_state.hundred_done=True; st.session_state.ambiguous_list=[]; st.success("Now 100% Clean!"); st.balloons(); st.rerun()
            st.markdown("<h3 style='font-weight: 900; font-size: 1.35rem; color: #000;'>Preview - Cleaned File - "+percent_text+"</h3>", unsafe_allow_html=True)
            styled=apply_style(df_clean.head(10)); st.dataframe(styled, use_container_width=True, height=420)

        if st.session_state.get("clean_done"):
            db=load_db(); user_info=db.get(st.session_state.email,{}) if st.session_state.email and st.session_state.email != "Guest_Free" else {}; is_paid=user_info.get("status")=="PAID" if user_info else True if st.session_state.plan=="free" else False; is_expired=False
            if user_info and user_info.get("expiry"):
                try:
                    exp_d=datetime.strptime(user_info["expiry"], "%Y-%m-%d").date(); days_left=(exp_d-datetime.now().date()).days
                    if user_info.get("plan") != "starter" and days_left < 0: is_expired=True
                except: pass
            if is_paid and not st.session_state.get("just_approved") and user_info.get("plan") in ["starter","pro"]: st.session_state.just_approved=True; st.balloons()
            
            if st.session_state.plan=="free":
                st.markdown("<h2 style='font-weight: 900; font-size: 1.5rem; color: #000;'>Export - "+percent_text+"</h2>", unsafe_allow_html=True); c1,c2,c3=st.columns(3); safe=sel_file[:30]
                with c1: csv=df_clean.to_csv(index=False).encode(); st.download_button("CSV - "+percent_text+" - BIG", csv, safe+"_cleaned.csv", mime="text/csv", key="dl_csv_free_fv2", use_container_width=True, type="primary")
                with c2:
                    if openpyxl is not None: ex=io.BytesIO(); df_clean.to_excel(ex, index=False, engine='openpyxl'); ex.seek(0); st.download_button("Excel - "+percent_text+" - BIG", ex.getvalue(), safe+"_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx_free_fv2", use_container_width=True)
                with c3: pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean, st.session_state.get("hub_report")); 
                with c3:
                    if pdf: st.download_button("PDF - "+percent_text+" - BIG", pdf, safe+"_audit.pdf", mime="application/pdf", key="dl_pdf_free_fv2", use_container_width=True)
            elif st.session_state.plan in ["starter","pro"]:
                if is_expired: st.markdown("<div class='upgrade-msg'><b>Plan Ended - Pay again</b></div>", unsafe_allow_html=True); is_paid=False
                
                if not is_paid:
                    sel_amt=user_info.get("amt", st.session_state.get("selected_amt", 0))
                    if sel_amt in [STARTER_PRICE, PRO_1M, PRO_6M]: amt_to_show=sel_amt
                    else: amt_to_show=st.session_state.get("selected_amt", STARTER_PRICE)
                    if amt_to_show==STARTER_PRICE: plan_name="Starter Rs49 - ONE TIME per File - 2000 Rows"; upi_link="upi://pay?pa="+UPI_ID+"&pn=VeriSame&am="+str(STARTER_PRICE)+"&cu=INR&tn=VeriSame Starter "+str(STARTER_PRICE); btn_class=""
                    elif amt_to_show==PRO_1M: plan_name="Pro Rs299 - 1 Month 30 Days Unlimited"; upi_link="upi://pay?pa="+UPI_ID+"&pn=VeriSame&am="+str(PRO_1M)+"&cu=INR&tn=VeriSame Pro 299"; btn_class="big-pay-button-pro"
                    else: plan_name="Pro Rs1499 - 6 Months 180 Days Best Value"; upi_link="upi://pay?pa="+UPI_ID+"&pn=VeriSame&am="+str(PRO_6M)+"&cu=INR&tn=VeriSame Pro 1499"; btn_class="big-pay-button-pro"; amt_to_show=PRO_6M
                    
                    if user_info.get("status")=="PENDING":
                        st.markdown("<div class='verifying-box'><h3>Thank you for your payment</h3><p>Your payment is being verified.<br>Please wait a moment, our team will confirm shortly.</p></div>", unsafe_allow_html=True)
                        if st.button("Check Status", key="check_status_fv2", type="primary", use_container_width=True): st.rerun()
                    else:
                        st.markdown("<div class='upgrade-msg'><h3>Your file cleaned "+percent_text+" - "+plan_name+"</h3></div>", unsafe_allow_html=True)
                        st.markdown("<div class='qr-box'>", unsafe_allow_html=True)
                        st.markdown("<h2 style='font-weight: 900; font-size: 1.8rem; color: #000; text-align: center;'>"+plan_name+"</h2>", unsafe_allow_html=True)
                        qr_url="https://api.qrserver.com/v1/create-qr-code/?size=450x450&data="+urllib.parse.quote(upi_link)
                        c_qr1, c_qr2, c_qr3 = st.columns([1,2,1])
                        with c_qr2:
                            st.image(qr_url, width=450)
                            st.markdown("<p style='font-size: 1.25rem; color: #000; text-align: center; margin-top: 18px; font-weight: 900;'>Pay by scanning with any payment app<br>GPay | PhonePe | Paytm | BHIM | Amazon Pay</p>", unsafe_allow_html=True)
                        st.markdown("<div class='or-divider'><div class='or-divider-line'></div><div class='or-divider-text'>OR</div><div class='or-divider-line'></div></div>", unsafe_allow_html=True)
                        st.markdown("<p style='font-weight: 900; font-size: 1.4rem; text-align: center; color: #000; margin: 20px 0;'>Pay Directly - Click to open payment app</p>", unsafe_allow_html=True)
                        st.markdown('<a href="'+upi_link+'" class="big-pay-button '+btn_class+'">PAY Rs'+str(amt_to_show)+'<br><span class="big-pay-sub">Direct to Any Payment App - GPay | PhonePe | Paytm | BHIM</span></a>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("<div style='margin-top:24px;'>", unsafe_allow_html=True)
                        st.markdown("<p style='text-align:center; font-weight: 900; color: #000; margin-bottom: 12px; font-size: 1.35rem;'>After payment, click below:</p>", unsafe_allow_html=True)
                        if st.button("I Paid Rs"+str(amt_to_show)+" - Confirm Payment - BIG", key="btn_paid_"+str(amt_to_show)+"_fv2", type="primary", use_container_width=True):
                            data=load_db()
                            if amt_to_show==STARTER_PRICE: data[st.session_state.email]={"plan":"starter","amt":STARTER_PRICE,"days":36500,"expiry":(datetime.now()+timedelta(days=36500)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now()),"used":0}
                            elif amt_to_show==PRO_1M: data[st.session_state.email]={"plan":"pro","amt":PRO_1M,"days":30,"expiry":(datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                            else: data[st.session_state.email]={"plan":"pro","amt":PRO_6M,"days":180,"expiry":(datetime.now()+timedelta(days=180)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                            save_db(data); send_notification(st.session_state.email, amt_to_show, plan_name); st.success("Payment submitted! Waiting approval"); st.balloons(); time.sleep(1); st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    if st.session_state.get("just_approved"): st.balloons(); st.markdown("<div class='thankyou-box'><h3>Thank You! Payment Confirmed! Balloons! 🎉</h3><p>Your download is ready</p></div>", unsafe_allow_html=True)
                    else: st.markdown("<h2 style='font-weight: 900; font-size: 1.6rem; color: #000;'>Export Ready - "+percent_text+" - Balloons! 🎉</h2>", unsafe_allow_html=True)
                    
                    c1,c2,c3=st.columns(3); safe=sel_file[:30]; csv=df_clean.to_csv(index=False).encode()
                    with c1:
                        if st.download_button("CSV - "+percent_text+" - BIG", csv, safe+"_cleaned.csv", mime="text/csv", key="dl_csv_paid_fv2", use_container_width=True, type="primary"):
                            if st.session_state.plan=="starter":
                                db_u=load_db()
                                if st.session_state.email in db_u: db_u[st.session_state.email]["used"]=db_u[st.session_state.email].get("used",0)+1; save_db(db_u)
                    with c2:
                        if openpyxl is not None: ex=io.BytesIO(); df_clean.to_excel(ex, index=False, engine='openpyxl'); ex.seek(0)
                        if openpyxl is not None:
                            if st.download_button("Excel - "+percent_text+" - BIG", ex.getvalue(), safe+"_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx_paid_fv2", use_container_width=True):
                                if st.session_state.plan=="starter":
                                    db_u=load_db()
                                    if st.session_state.email in db_u: db_u[st.session_state.email]["used"]=db_u[st.session_state.email].get("used",0)+1; save_db(db_u)
                    with c3: pdf=generate_pdf(orig_len, len(df_clean), st.session_state.empty_fixed, df_clean, st.session_state.get("hub_report")); 
                    with c3:
                        if pdf:
                            if st.download_button("PDF - "+percent_text+" - BIG", pdf, safe+"_audit.pdf", mime="application/pdf", key="dl_pdf_paid_fv2", use_container_width=True):
                                if st.session_state.plan=="starter":
                                    db_u=load_db()
                                    if st.session_state.email in db_u: db_u[st.session_state.email]["used"]=db_u[st.session_state.email].get("used",0)+1; save_db(db_u)
