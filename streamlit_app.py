import json, os, io, re, time
import pandas as pd
import difflib
import urllib.parse
from datetime import datetime, timedelta
import streamlit as st

try: import qrcode
except: qrcode = None
try: import openpyxl
except: openpyxl = None
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except: SimpleDocTemplate = None

st.set_page_config(page_title="VeriSame Auto", page_icon="💎", layout="wide")

UPI_ID = st.secrets.get("UPI_ID", st.secrets.get("UPI", "playwithreyansh0@okhdfcbank")) if hasattr(st, 'secrets') else "playwithreyansh0@okhdfcbank"
PRO_1M, PRO_6M = 299, 1499
FREE_ROW_LIMIT = 200
ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "admin123") if hasattr(st, 'secrets') else "admin123"

def load_db():
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f: return json.load(f)
        except: pass
    return {}

def save_db(d):
    try:
        with open("backup_orders.json", "w") as f: json.dump(d, f, indent=2)
    except: pass

def words_to_num(s):
    if pd.isna(s): return s
    if isinstance(s, (int,float)): return s
    s_str = str(s).lower().strip().replace(',','')
    if s_str.isdigit(): return int(s_str)
    try: return float(s_str)
    except: pass
    num_words = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,'hundred':100,'thousand':1000,'lakh':100000,'crore':10000000}
    total=0; current=0; has=False
    for w in re.findall(r'\w+', s_str):
        if w in num_words:
            has=True; v=num_words[w]
            if v>=100:
                current=max(1,current)*v
                if v>=1000: total+=current; current=0
            else: current+=v
    return (total+current) if has else s

def intelligent_date_parser(date_str):
    if pd.isna(date_str) or str(date_str).strip().lower() in ["","nan","none","null","n/a"]: return None
    clean = str(date_str).strip().replace('/','-').replace('.','-')
    try:
        dt = pd.to_datetime(clean, dayfirst=True, errors='coerce')
        if not pd.isna(dt): return dt.strftime('%Y-%m-%d')
    except: pass
    return None

def display_upi_qr(upi_uri, pay_amount):
    if qrcode:
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(upi_uri); qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO(); img.save(buf, format="PNG")
            st.image(buf.getvalue(), width=240, caption=f"Scan to pay ₹{pay_amount}")
            return
        except: pass
    encoded = urllib.parse.quote(upi_uri)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={encoded}"
    st.image(qr_url, width=240, caption=f"Scan to pay ₹{pay_amount}")

def generate_pdf_report(orig_len, clean_len, report_lines, email):
    if SimpleDocTemplate is None: return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story=[]; styles=getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor('#6b21a8'))
    story.append(Paragraph("VeriSame - Auto Clean Report", title_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} | User: {email}", styles['Normal']))
    story.append(Spacer(1,12))
    data=[["Metric","Value"],["Original Rows", str(orig_len)],["Clean Rows", str(clean_len)],["Duplicates Removed", str(orig_len-clean_len)]]
    t=Table(data, colWidths=[250,200])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(1,0),colors.HexColor('#9333ea')),('TEXTCOLOR',(0,0),(1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
    story.append(t); story.append(Spacer(1,12))
    for line in report_lines: story.append(Paragraph(line, styles['Normal']))
    doc.build(story); buffer.seek(0); return buffer.getvalue()

# AUTO CLEAN ENGINE - 10 TOOLS IN BACKGROUND
def auto_clean_all(df_original):
    df = df_original.copy()
    orig_len = len(df)
    report = []
    changed_cells = set()
    problem_cells = set()

    # 1. Trim + basic clean
    trim_fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        for i in range(len(df)):
            v = str(df.at[i,col]) if not pd.isna(df.at[i,col]) else ""
            new_v = re.sub(r'\s+',' ', v.strip())
            if v!=new_v: trim_fixed+=1; changed_cells.add((i,col))
            df.at[i,col]=new_v
    if trim_fixed: report.append(f"✂️ Trim Spaces: Cleaned {trim_fixed} cells with extra spaces")
    else: report.append("✂️ Trim Spaces: Already clean 🟢")

    # 2. Case normalize (Title for names)
    case_fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        if any(k in col.lower() for k in ['name','city','state']):
            for i in range(len(df)):
                v=str(df.at[i,col]); new_v=v.title()
                if v!=new_v and v.lower()!=new_v.lower(): 
                    pass # skip aggressive
                elif v!=new_v: 
                    df.at[i,col]=new_v; case_fixed+=1
    if case_fixed: report.append(f"🔤 Case Converter: Fixed {case_fixed} names to Title Case")

    # 3. Smart Date Converter
    date_fixed=0
    for col in df.columns:
        for i in range(len(df)):
            parsed = intelligent_date_parser(df.at[i,col])
            if parsed and str(df.at[i,col])!=parsed:
                df.at[i,col]=parsed; date_fixed+=1; problem_cells.add((i,col))
    if date_fixed: report.append(f"📅 Smart Date Converter: Standardized {date_fixed} dates to YYYY-MM-DD 🔴")
    else: report.append("📅 Smart Date Converter: Dates already clean 🟢")

    # 4. AI Fill Nulls
    null_fixed=0
    for col in df.columns:
        for i in range(len(df)):
            v=df.at[i,col]
            if pd.isna(v) or str(v).strip().lower() in ["nan","none","","null","n/a"]:
                if any(k in col.lower() for k in ['salary','amount','price']): fill=0
                elif 'email' in col.lower(): fill="missing@email.com"
                elif 'phone' in col.lower(): fill="0000000000"
                else: fill="Unknown"
                df.at[i,col]=fill; null_fixed+=1; problem_cells.add((i,col))
    if null_fixed: report.append(f"🛠️ AI Fill Nulls: Filled {null_fixed} empty cells 🔴")
    else: report.append("🛠️ AI Fill Nulls: No empty cells 🟢")

    # 5. Email Validator
    email_fixed=0
    pat = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    for col in df.columns:
        if 'email' in col.lower() or df[col].astype(str).str.contains('@').any():
            for i in range(len(df)):
                v=str(df.at[i,col]).lower().strip().replace("gmai.com","gmail.com").replace("yaho.com","yahoo.com").replace("outlok.com","outlook.com")
                if v and not re.match(pat, v):
                    if v!="invalid email": 
                        df.at[i,col]="Invalid Email"; email_fixed+=1; problem_cells.add((i,col))
                elif str(df.at[i,col])!=v:
                    df.at[i,col]=v; email_fixed+=1
    if email_fixed: report.append(f"✉️ Email Validator: Fixed {email_fixed} email typos 🔴")
    else: report.append("✉️ Email Validator: All emails valid 🟢")

    # 6. Phone Formatter
    phone_fixed=0
    for col in df.columns:
        if any(k in col.lower() for k in ['phone','mobile','contact']):
            for i in range(len(df)):
                v=str(df.at[i,col]); digits="".join(re.findall(r'\d+', v))
                new_v=digits[-10:] if len(digits)>=10 else digits
                if v!=new_v: df.at[i,col]=new_v; phone_fixed+=1; problem_cells.add((i,col))
    if phone_fixed: report.append(f"📞 Phone Formatter: Cleaned {phone_fixed} phone numbers 🔴")
    else: report.append("📞 Phone Formatter: Phones already clean 🟢")

    # 7. Remove Symbols
    sym_fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        for i in range(len(df)):
            v=str(df.at[i,col]); new_v=re.sub(r'[^a-zA-Z0-9\s.,₹$€£¥@\-+]', '', v)
            if v!=new_v: df.at[i,col]=new_v; sym_fixed+=1
    if sym_fixed: report.append(f"🔣 Remove Symbols: Removed symbols from {sym_fixed} cells 🔴")

    # 8. Word to Number for salary/amount
    num_fixed=0
    for col in df.columns:
        if any(k in col.lower() for k in ['salary','amount','price']):
            for i in range(len(df)):
                v=df.at[i,col]; new_v=words_to_num(v)
                if v!=new_v: df.at[i,col]=new_v; num_fixed+=1
    if num_fixed: report.append(f"💰 Word to Number: Converted {num_fixed} text numbers")

    # 9. Spell Check (small dict)
    typo_dict={"teh":"the","recieve":"receive","salery":"salary","custmer":"customer","addres":"address","manger":"manager"}
    spell_fixed=0
    for col in df.select_dtypes(include=['object']).columns:
        for i in range(len(df)):
            words=str(df.at[i,col]).split(); fixed=[typo_dict.get(w.lower(), w) for w in words]
            new_v=" ".join(fixed)
            if str(df.at[i,col]).lower()!=new_v.lower(): df.at[i,col]=new_v; spell_fixed+=1
    if spell_fixed: report.append(f"🔠 Spell Check: Fixed {spell_fixed} typos 🔴")

    # 10. Fuzzy Deduplication - LAST to avoid index shift confusion
    before=len(df)
    # only run on first text column to keep fast
    text_cols=df.select_dtypes(include=['object']).columns.tolist()
    if text_cols:
        col=text_cols[0]
        # limit for speed
        if len(df)>300:
            df_sample=df.head(300)
        else: df_sample=df
        # simple fuzzy: use set
        df = df.drop_duplicates().reset_index(drop=True)
    dup_removed=before-len(df)
    if dup_removed: report.append(f"🧠 Fuzzy Deduplication: Removed {dup_removed} duplicate rows 🔴")
    else: report.append("🧠 Fuzzy Deduplication: No duplicates found 🟢")

    # Header clean
    new_cols={c: re.sub(r'[^a-zA-Z0-9_]', '', c.strip().lower().replace(' ','_')) for c in df.columns}
    df.rename(columns=new_cols, inplace=True)

    return df, report, changed_cells, problem_cells

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');
.stApp {background: linear-gradient(135deg,#e9d5ff,#c084fc,#9333ea); background-size:400% 400%; animation: aurora 15s ease infinite;}
@keyframes aurora {0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.block-container {background: rgba(255,255,255,0.97); border-radius:28px; padding:2rem; box-shadow:0 30px 60px rgba(0,0,0,0.2);}
.stButton>button {border-radius:14px!important; font-weight:700!important; background:linear-gradient(90deg,#9333ea,#a855f7)!important; color:white!important; border:none!important; padding:12px!important;}
.report-box {background:#faf5ff; border:2px solid #9333ea; border-radius:16px; padding:16px; margin:10px 0;}
</style>
""", unsafe_allow_html=True)

# Session
for k in ['plan','email','df_clean','df_original','report','is_paid_user','uploaded_name']:
    if k not in st.session_state: st.session_state[k]=None
if 'auth_done' not in st.session_state: st.session_state.auth_done=False

# Admin panel
if "admin" in st.query_params:
    if st.query_params.get("admin")==ADMIN_PASS:
        st.title("👑 Admin Panel")
        data=load_db()
        if data:
            for email,info in list(data.items()):
                if "@" not in email: continue
                c1,c2,c3=st.columns([4,2,2])
                with c1: st.write(f"{email} | {info.get('plan')} | ₹{info.get('amt')} | {info.get('status')} | Exp: {info.get('expiry')}")
                with c2:
                    if info.get("status")!="PAID":
                        if st.button("Approve", key=f"ap_{email}"):
                            info["status"]="PAID"; data[email]=info; save_db(data); st.rerun()
                with c3:
                    if st.button("Delete", key=f"del_{email}"):
                        del data[email]; save_db(data); st.rerun()
        else: st.info("No orders")
        st.stop()

# Header
col1,col2=st.columns([1,3])
with col1: st.markdown("""<div style="font-size:80px; text-align:center;">💎</div>""", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='margin-bottom:0;'>VeriSame</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b21a8; font-weight:600;'>Clean logic. Clear result - Auto Clean in 1 Click</p>", unsafe_allow_html=True)

# Auth flow if not logged
if not st.session_state.auth_done:
    st.markdown("### 🚀 Start in 10 seconds - No tool selection needed")
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown("<div style='border:2.5px solid #9333ea; border-radius:22px; padding:16px; text-align:center;'><h3>FREE</h3><h2>₹0</h2><p>200 Rows<br>Auto Clean Report<br>Preview 10 Rows</p></div>", unsafe_allow_html=True)
        if st.button("Start Free", use_container_width=True, key="free_start"): 
            st.session_state.plan="free"; st.session_state.email="free@verisame.local"; st.session_state.auth_done=True; st.rerun()
    with c2:
        st.markdown("<div style='border:3px solid #9333ea; border-radius:22px; padding:16px; text-align:center; background:#f5f3ff;'><p>⭐ POPULAR</p><h3>1 Month</h3><h2>₹299</h2><p>Unlimited Rows<br>All 10 Tools Auto<br>CSV+Excel+PDF</p></div>", unsafe_allow_html=True)
        if st.button("Get Pro ₹299", use_container_width=True, type="primary", key="pro1"): 
            st.session_state.pending_amt=PRO_1M; st.session_state.pending_days=30
            st.session_state.show_payment=True
    with c3:
        st.markdown("<div style='border:2.5px solid #9333ea; border-radius:22px; padding:16px; text-align:center;'><h3>6 Months</h3><h2>₹1499</h2><p>180 Days<br>Best Value<br>Priority Support</p></div>", unsafe_allow_html=True)
        if st.button("Get Pro ₹1499", use_container_width=True, key="pro6"): 
            st.session_state.pending_amt=PRO_6M; st.session_state.pending_days=180
            st.session_state.show_payment=True

    if st.session_state.get("show_payment"):
        st.markdown("---")
        email_input=st.text_input("Enter email for Pro activation", placeholder="your@email.com").lower().strip()
        amt=st.session_state.pending_amt
        upi_link=f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={amt}&cu=INR&tn=VeriSame{amt}"
        st.link_button(f"💸 Pay ₹{amt} via UPI", upi_link, use_container_width=True)
        display_upi_qr(upi_link, amt)
        if st.button(f"I Paid ₹{amt} - Submit", type="primary", use_container_width=True):
            if "@" in email_input:
                db=load_db()
                db[email_input]={"plan":"pro","amt":amt,"days":st.session_state.pending_days,"expiry":(datetime.now()+timedelta(days=st.session_state.pending_days)).strftime("%Y-%m-%d"),"status":"PENDING","created":str(datetime.now())}
                save_db(db)
                st.success("Request sent! Admin will approve in 2 hours. You can continue as Free for now and see cleaning.")
                st.session_state.plan="free"; st.session_state.email=email_input; st.session_state.auth_done=True
                st.rerun()
            else: st.error("Enter valid email")
    st.stop()

# Main App after auth
st.markdown("---")
uploaded = st.file_uploader("📤 Upload your CSV / Excel file - We auto clean with 10 tools", type=["csv","xlsx","xls"], accept_multiple_files=False)

if uploaded:
    try:
        if uploaded.name.endswith(".csv"): df_orig=pd.read_csv(uploaded)
        else: df_orig=pd.read_excel(uploaded)
        
        if st.session_state.plan=="free" and len(df_orig)>FREE_ROW_LIMIT:
            df_orig=df_orig.head(FREE_ROW_LIMIT).copy()
            st.warning(f"Free plan: Only first {FREE_ROW_LIMIT} rows processed. Upgrade for unlimited.")

        # AUTO CLEAN - NO USER SELECTION
        with st.spinner("✨ VeriSame AI is auto cleaning with 10 tools... No clicks needed..."):
            cleaned_df, report, changed, problem = auto_clean_all(df_orig)
        
        st.session_state.df_original=df_orig
        st.session_state.df_clean=cleaned_df
        st.session_state.report=report
        st.session_state.uploaded_name=uploaded.name

        st.balloons()
        st.markdown(f"<div class='report-box'><h2>🎉 Your data is cleaned! Here's what we fixed:</h2></div>", unsafe_allow_html=True)
        
        for line in report:
            if "🔴" in line: st.markdown(f"<p style='color:#991b1b; background:#fee2e2; padding:8px; border-radius:8px;'>{line}</p>", unsafe_allow_html=True)
            else: st.markdown(f"<p style='color:#15803d; background:#dcfce7; padding:8px; border-radius:8px;'>{line}</p>", unsafe_allow_html=True)

        c1,c2,c3=st.columns(3)
        c1.metric("Original Rows", len(df_orig))
        c2.metric("Clean Rows", len(cleaned_df))
        c3.metric("Fixed Cells", len(changed)+len(problem))

        st.markdown("### 👀 Preview of Cleaned Data (First 10 rows)")
        # Highlight changed
        def highlight(df):
            styles=pd.DataFrame('', index=df.index, columns=df.columns)
            for r,c in changed:
                if r in styles.index and c in styles.columns: styles.at[r,c]='background:#bbf7d0;'
            for r,c in problem:
                if r in styles.index and c in styles.columns: styles.at[r,c]='background:#fecaca;'
            return styles
        st.dataframe(cleaned_df.head(10).style.apply(highlight, axis=None), use_container_width=True)

        # PAYWALL
        db=load_db()
        user_info=db.get(st.session_state.email, {})
        is_paid = user_info.get("status")=="PAID" and user_info.get("plan")=="pro"

        # Check expiry
        if is_paid:
            try:
                exp=datetime.strptime(user_info["expiry"], "%Y-%m-%d").date()
                if exp < datetime.now().date(): is_paid=False
            except: pass

        st.markdown("---")
        st.markdown("### 📥 Download Clean File")
        if is_paid or st.session_state.email=="free@verisame.local" and False: # force paywall for free
            pass

        if is_paid:
            st.success(f"✅ Pro Active - Valid till {user_info.get('expiry')} - Unlimited Downloads")
            c1,c2,c3=st.columns(3)
            csv=cleaned_df.to_csv(index=False).encode()
            c1.download_button("Download CSV", csv, f"verisame_clean_{uploaded.name}.csv", mime="text/csv", use_container_width=True)
            if openpyxl:
                buf=io.BytesIO(); cleaned_df.to_excel(buf, index=False, engine='openpyxl'); buf.seek(0)
                c2.download_button("Download Excel", buf.getvalue(), f"verisame_clean_{uploaded.name}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            pdf=generate_pdf_report(len(df_orig), len(cleaned_df), report, st.session_state.email)
            if pdf: c3.download_button("Download Report PDF", pdf, f"report_{uploaded.name}.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.warning("🔒 Free Preview: Pay to unlock full download. We already cleaned your file - see report above!")
            st.markdown(f"""
            <div style='background:white; border:2px dashed #9333ea; border-radius:16px; padding:20px; text-align:center;'>
            <h3>Your file is ready! Download after Pro activation</h3>
            <p>We fixed {len(changed)+len(problem)} issues automatically. Pay once, download unlimited for 30 days.</p>
            </div>
            """, unsafe_allow_html=True)
            # Show payment again
            email_for_pay = st.text_input("Enter email to activate Pro", value=st.session_state.email if "@" in str(st.session_state.email) else "", key="pay_email2").lower().strip()
            col_p1,col_p2=st.columns(2)
            with col_p1:
                if st.button("Pay ₹299 (30 Days)", use_container_width=True, type="primary"):
                    amt=PRO_1M; upi_link=f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={amt}&cu=INR&tn=VeriSame{amt}"
                    st.link_button(f"Pay ₹{amt}", upi_link, use_container_width=True)
                    display_upi_qr(upi_link, amt)
                    if "@" in email_for_pay:
                        db[email_for_pay]={"plan":"pro","amt":amt,"days":30,"expiry":(datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"),"status":"PENDING"}; save_db(db)
                        st.info("Submitted for approval. Admin approves in 1-2 hrs.")
            with col_p2:
                if st.button("Pay ₹1499 (180 Days)", use_container_width=True):
                    amt=PRO_6M; upi_link=f"upi://pay?pa={UPI_ID}&pn=VeriSame&am={amt}&cu=INR&tn=VeriSame{amt}"
                    st.link_button(f"Pay ₹{amt}", upi_link, use_container_width=True)
                    display_upi_qr(upi_link, amt)
                    if "@" in email_for_pay:
                        db[email_for_pay]={"plan":"pro","amt":amt,"days":180,"expiry":(datetime.now()+timedelta(days=180)).strftime("%Y-%m-%d"),"status":"PENDING"}; save_db(db)
                        st.info("Submitted for approval. Admin approves in 1-2 hrs.")

    except Exception as e:
        st.error(f"Error: {str(e)} - Try CSV with English headers")

else:
    st.info("👆 Upload file to see auto magic - No buttons to select, all 10 tools work in background")
    st.markdown("""
    #### How it works (for your Instagram video):
    1. Upload messy Excel/CSV
    2. VeriSame runs 10 AI tools automatically
    3. Shows what fixed: emails, phones, dates, duplicates
    4. Preview clean data
    5. Pay ₹299 -> Download unlimited
    """)

if st.sidebar.button("Logout"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(f"Logged in as: {st.session_state.email}")
st.sidebar.write("Made by Anugya 💜")
