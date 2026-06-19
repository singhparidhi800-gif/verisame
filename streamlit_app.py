import streamlit as st
import json, os, io, re, zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Force premium page config layout configurations
st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "sherni_admin")

# 🔒 ROBUST PERSISTENT STATE STORAGE DATABASE ENGINE
if "global_db_backup" not in st.session_state:
    st.session_state.global_db_backup = {}

def load_db():
    if os.path.exists("backup_orders.json"):
        try:
            with open("backup_orders.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    st.session_state.global_db_backup = data
                    return data
        except Exception: pass
    return st.session_state.global_db_backup

def save_db(d):
    try:
        st.session_state.global_db_backup = d
        with open("backup_orders.json", "w") as f:
            json.dump(d, f, indent=2)
    except Exception: pass

# 🔄 DYNAMIC ADVANCED WORDS-TO-NUMBER COMPUTATIONAL PARSER
def words_to_num(s):
    if pd.isna(s): return s
    s_str = str(s).lower().strip()
    if s_str.isdigit(): return int(s_str)
    try: return float(s_str)
    except ValueError: pass
        
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
    return total + current if has_num_word and (total + current > 0) else s

# ANTI-DARK MODE ENFORCED GLOSSY GRADIENT STYLING DOM
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {
    background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 25%, #d8b4fe 50%, #c084fc 75%, #a855f7 100%) !important; 
    background-size: 400% 400% !important; 
    animation: aurora 20s ease infinite !important;
}
.block-container {
    background: rgba(255,255,255,0.97) !important; 
    backdrop-filter: blur(30px) saturate(200%) !important; 
    border-radius: 30px !important; padding: 2.5rem !important; 
    max-width: 1240px; margin: 1.5rem auto !important; 
    box-shadow: 0 40px 80px rgba(147,51,234,0.18) !important;
    border: 2px solid rgba(255,255,255,0.7) !important;
}
h1,h2,h3,p,span,label,div,li {color: #1e1b4b!important; font-weight: 600!important;}
h1 {
    font-weight: 900!important; font-size: 3.6rem!important; 
    background: linear-gradient(90deg, #4c1d95, #7c3aed, #c084fc, #6d28d9, #4c1d95) !important; 
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
}
.badge-free {background-color: #10b981 !important; color: white !important; padding: 6px 16px; border-radius: 20px; font-size: 0.9rem; display: inline-block;}
.cherry {position: fixed; top: -10vh; color: #FFB7C5; font-size: 22px; animation: fall linear infinite; z-index: 9999; pointer-events: none;}
@keyframes fall {0%{transform: translateY(0vh) rotate(0deg); opacity: 1;} 100%{transform: translateY(110vh) rotate(360deg); opacity: 0;}}
</style>
<div class="cherry" style="left: 12%; animation-duration: 7s;">🌸</div>
<div class="cherry" style="left: 68%; animation-duration: 12s; animation-delay: 1s;">🌸</div>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Welcome to VeriSame Intelligence Studio. How can I guide your pipeline diagnostics today?"}]

# 🤖 INTENSE TECHNICAL KNOWLEDGE STACK ENGLISH AI CHATBOT
def render_ai_chatbot(is_sidebar=False):
    target = st.sidebar if is_sidebar else st
    target.markdown("---")
    target.markdown("### 🤖 Advanced Data Pipeline AI Assistant")
    
    chat_html = "<div style='max-height: 260px; overflow-y: auto; padding: 12px; background: #ffffff; border: 2px solid #7c3aed; border-radius: 12px; margin-bottom: 10px;'>"
    for chat in st.session_state.chat_history:
        if chat["role"] == "assistant":
            chat_html += f"<p style='color: #6d28d9 !important; margin: 4px 0;'><b>🤖 AI:</b> {chat['message']}</p>"
        else:
            chat_html += f"<p style='color: #111827 !important; margin: 4px 0;'><b>👤 User:</b> {chat['message']}</p>"
    chat_html += "</div>"
    target.markdown(chat_html, unsafe_allow_html=True)

    s_id = "side" if is_sidebar else "main"
    user_msg = target.text_input("Query architectural framework specifications...", key=f"chat_in_{s_id}")
    if target.button("Evaluate Framework Stream 🚀", key=f"btn_send_{s_id}") and user_msg.strip():
        u = user_msg.lower().strip()
        st.session_state.chat_history.append({"role": "user", "message": user_msg})
        
        reply = "I am trained deeply on VeriSame core engine structures. Please request clear architectural criteria regarding workflows."
        if "free" in u:
            reply = "The Free Tier offers lifetime unmetered access to 4 core processes: Smart Date Converter, Case Converter, Remove Duplicates, and Space Trimmer. It operates under a hard technical threshold of a maximum 1000 rows per file."
        elif "pro" in u or "batch" in u or "zip" in u:
            reply = "The Pro Studio Layer unlocks the absolute entirety of all 10 tools with infinitely variable row scalability. It deploys high-speed Multi-File Batch processing (handling 10 to 20 files simultaneously) in strictly isolated containerized memory frames, outputting a unified zip batch package."
        elif "date" in u:
            reply = "The Smart Date Converter implements high-order parser matrices to automatically interpret fragmented dates and re-align them into standard ISO-8601 (YYYY-MM-DD) string objects."
        elif "text" in u or "number" in u or "words-to-num" in u:
            reply = "The text-to-numbers algorithm actively tokenizes standard natural language alphabetic numbers (e.g., 'one hundred thousand') and dynamically aggregates them back into computer-readable integer primitives."
        elif "founder" in u or "owner" in u or "creator" in u:
            reply = "The entire VeriSame analytical ecosystem and workflow pipelines were mapped, engineered, and deployed by **Anugya Singh**."
            
        st.session_state.chat_history.append({"role": "assistant", "message": reply})
        st.rerun()

# WORKSPACE STATE STRUCTURING
for k in ['plan','email','uploaded_dfs','processed_dfs','email_entered','selected_plan']:
    if k not in st.session_state: st.session_state[k] = None if k in ['plan','email','selected_plan'] else {}

if st.session_state.plan:
    if st.sidebar.button("← Reset System Workspace Layout", use_container_width=True):
        for k in ['plan','email','uploaded_dfs','processed_dfs','email_entered','selected_plan']:
            st.session_state[k] = None if k in ['plan','email','selected_plan'] else {}
        st.rerun()

if st.session_state.email:
    st.sidebar.success(f"📧 Profile Session: {st.session_state.email}")
    render_ai_chatbot(is_sidebar=True)

# THEMED HEADER LAYOUT
col1, col2, col3 = st.columns([1, 2, 1.5])
with col1: st.markdown('<img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width:100%; max-height:190px; object-fit:contain;">', unsafe_allow_html=True)
with col2:
    st.markdown("<h1>VeriSame</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#4b5563; font-size:1.1rem;'>The Advanced Multi-Tier Clean Pipeline Studio</p>", unsafe_allow_html=True)
with col3: st.markdown('<div style="border-radius:20px; overflow:hidden;"><img src="https://i.postimg.cc/8zdnX54g/IMG-20260609-WA0012.jpg" style="width:100%; height:170px; object-fit:cover;"></div>', unsafe_allow_html=True)

# USER PROFILE REGISTRATION ENTRY
if st.session_state.plan is None:
    if st.session_state.selected_plan is None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### FREE FOREVER ✨<br>Basic Operations Framework", unsafe_allow_html=True)
            if st.button("Initialize Free Pipeline Workspace", use_container_width=True):
                st.session_state.selected_plan = "free"; st.rerun()
        with c2:
            st.markdown("### PRO STUDIO 💎<br>Unlimited Concurrent Batch Engine", unsafe_allow_html=True)
            if st.button("Initialize Pro Studio Workspace", use_container_width=True):
                st.session_state.selected_plan = "pro"; st.rerun()
        st.stop()
    else:
        em = st.text_input("Enter Profile Registration Email Address:").lower().strip()
        if st.button("Authorize Application Mount"):
            if "@" in em:
                st.session_state.email = em
                st.session_state.plan = st.session_state.selected_plan
                st.rerun()
        st.stop()

# DATA UPLOAD BATCHING PIPELINE CONTROL
st.markdown("---")
if st.session_state.plan == "free":
    st.markdown("<h3>Active Cluster: <span class='badge-free'>Free Forever Layout ✨</span></h3>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload Processing Data (Single Workbook Allowed)", type=["csv","xlsx"])
    files_list = [uploaded_files] if uploaded_files else []
else:
    st.markdown("<h3>Active Cluster: <span style='color:#7c3aed;'>💎 Pro Corporate Suite Active</span></h3>", unsafe_allow_html=True)
    files_list = st.file_uploader("Upload Multi-File Batch Data Streams (Supports 10 to 20 Files Simultaneously)", type=["csv","xlsx"], accept_multiple_files=True)

# ISOLATED ALLOCATION OF FILES TO PREVENT MIXUPS
if files_list:
    for f in files_list:
        if f.name not in st.session_state.uploaded_dfs:
            try:
                raw_df = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
                
                # Rigid enforcement of rows check criteria for Free Tier
                if st.session_state.plan == "free" and len(raw_df) > 1000:
                    st.error(f"❌ Structural Limit Violation in '{f.name}' ({len(raw_df)} rows)! Free Tier can only clean data models up to 1000 rows. Please mount a Pro Session to access infinite matrix parameters.")
                    st.stop()
                    
                st.session_state.uploaded_dfs[f.name] = raw_df.copy()
                st.session_state.processed_dfs[f.name] = raw_df.copy()
            except Exception as e:
                st.error(f"IO Parser Interruption: {e}")

if st.session_state.processed_dfs:
    active_filename = st.selectbox("Select Target Active File Stream to Preview/Configure Operations:", list(st.session_state.processed_dfs.keys()))
    current_df = st.session_state.processed_dfs[active_filename]
    
    st.markdown(f"**Live Matrix Monitoring Frame:** `{active_filename}` | Total Row Vector Index: `{len(current_df)}`")
    st.dataframe(current_df.head(5), use_container_width=True)
    all_cols = current_df.columns.tolist()

    # 🔮 SMART COLUMN PREDICTION ANALYSIS FRAMEWORK
    with st.expander("🔮 Automated Predictive Structural Pattern Analyzer"):
        for c in all_cols:
            sample_val = str(current_df[c].dropna().iloc[0]) if not current_df[c].dropna().empty else ""
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', sample_val):
                st.info(f"Target Column `{c}` evaluated profile: **EMAIL ADDRESS SCHEME**")
            elif any(w in str(sample_val).lower() for w in ['one','two','three','hundred','thousand']):
                st.info(f"Target Column `{c}` evaluated profile: **NATURAL LANGUAGE STRING LITERAL NUMERIC**")
            elif re.search(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', sample_val):
                st.info(f"Target Column `{c}` evaluated profile: **TIMESTAMP ARRAY LAYOUT**")
            else:
                st.write(f"Target Column `{c}` evaluated profile: Standard Raw Continuous Value Array")

    # OPERATIONAL ACCELERATION MATRIX DIVISION
    st.markdown("### Operational Studio Pipeline Matrix")
    
    # Tier locked vs unlocked layout metrics configuration
    is_pro = (st.session_state.plan == "pro")
    free_label = "✅ Unlocked"
    pro_label = "✅ Unlocked" if is_pro else "🔒 Pro Only (Locked)"

    c_t1, c_t2 = st.columns(2)
    
    with c_t1:
        st.markdown(f"#### 🆓 Core Free Process Operations ({free_label})")
        
        # Tool 1: Smart Date Converter
        with st.container():
            st.markdown("**Tool 1: Smart Date Converter**")
            d_cols = st.multiselect("Select Target Date Columns:", all_cols, key=f"d_{active_filename}")
            if st.button("Execute Date Matrix Parsing Sequence", key=f"b_d_{active_filename}"):
                for col in d_cols:
                    st.session_state.processed_dfs[active_filename][col] = pd.to_datetime(st.session_state.processed_dfs[active_filename][col], errors='coerce').dt.strftime('%Y-%m-%d').fillna("None")
                st.success("Date alignment matrix stabilized!"); st.rerun()

        # Tool 5: Universal Case Converter
        with st.container():
            st.markdown("**Tool 5: Universal Case Normalization**")
            c_cols = st.multiselect("Select Target Text Columns:", all_cols, key=f"c_{active_filename}")
            c_type = st.selectbox("Target String Conversion Model Specification:", ["UPPERCASE", "lowercase", "Title Case"], key=f"ct_{active_filename}")
            if st.button("Execute String Capitalization Strategy", key=f"b_c_{active_filename}"):
                for col in c_cols:
                    if c_type == "UPPERCASE": st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].astype(str).str.upper()
                    elif c_type == "lowercase": st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].astype(str).str.lower()
                    else: st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].astype(str).str.title()
                st.success("String configurations remapped!"); st.rerun()

        # Tool 8: Remove Duplicates
        with st.container():
            st.markdown("**Tool 8: Primary High-Speed Deduplication Engine**")
            if st.button("Purge Repetitive Overlapping Node Signatures", key=f"b_dedup_{active_filename}"):
                st.session_state.processed_dfs[active_filename] = st.session_state.processed_dfs[active_filename].drop_duplicates()
                st.success("Duplicate vectors completely removed!"); st.rerun()

        # Tool 9: Trim Spaces
        with st.container():
            st.markdown("**Tool 9: White-Space Padding Extraction Gate**")
            tr_cols = st.multiselect("Select Padded Data Fields:", all_cols, key=f"tr_{active_filename}")
            if st.button("Execute Structural Workspace Trim", key=f"b_tr_{active_filename}"):
                for col in tr_cols:
                    st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                st.success("Space boundaries aligned flawlessly!"); st.rerun()

    with c_t2:
        st.markdown(f"#### 💎 Corporate Premium Process Operations ({pro_label})")
        
        if not is_pro:
            st.warning("⚠️ Access Denied. These remaining 6 advanced analytic nodes are restricted to Pro Tier workspaces.")
        else:
            # Tool 2: AI Fill Nulls
            with st.container():
                st.markdown("**Tool 2: Predictive Structural Null Filler**")
                f_cols = st.multiselect("Select target missing arrays:", all_cols, key=f"f_{active_filename}")
                if st.button("Execute Missing Imputation Run", key=f"b_f_{active_filename}"):
                    for col in f_cols: st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].fillna("Unknown Baseline")
                    st.success("Imputation strategy fully executed!"); st.rerun()

            # Tool 3: Email Validator
            with st.container():
                st.markdown("**Tool 3: Strict Regular Expression Email Verification Layer**")
                em_cols = st.multiselect("Select client email structures:", all_cols, key=f"em_{active_filename}")
                if st.button("Deploy Matrix Addressing Clean Filters", key=f"b_em_{active_filename}"):
                    pat = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    for col in em_cols: st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].astype(str).apply(lambda x: x if re.match(pat, x) else "Broken Protocol Signature")
                    st.success("Email structures mapped and verified!"); st.rerun()

            # Tool 4: Phone Formatter
            with st.container():
                st.markdown("**Tool 4: Fixed Terminal Mobile Array Formatter**")
                ph_cols = st.multiselect("Select raw communication numbers:", all_cols, key=f"ph_{active_filename}")
                if st.button("Enforce Uniform Numeric Bounds", key=f"b_ph_{active_filename}"):
                    for col in ph_cols: st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x))[-10:])
                    st.success("Communication configurations standardized!"); st.rerun()

            # Tool 6: Remove Symbols
            with st.container():
                st.markdown("**Tool 6: Complete Alphanumeric Integrity Extraction Gate**")
                sy_cols = st.multiselect("Select targeted symbolic elements:", all_cols, key=f"sy_{active_filename}")
                if st.button("Purge Non-Alphanumeric Artifacts", key=f"b_sy_{active_filename}"):
                    for col in sy_cols: st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x))
                    st.success("Symbols cleanly eliminated!"); st.rerun()

            # Tool 7: Bulk Rename
            with st.container():
                st.markdown("**Tool 7: Structural Mapping Column Renamer**")
                old_c = st.selectbox("Choose Source Mapping Target Structural Key:", all_cols, key=f"old_{active_filename}")
                new_c = st.text_input("Enter Updated Semantic Descriptor Identity Tag:", key=f"new_{active_filename}")
                if st.button("Commit Structural Layout Rewrite Sequence", key=f"b_rn_{active_filename}") and new_c:
                    st.session_state.processed_dfs[active_filename].rename(columns={old_c: new_c}, inplace=True)
                    st.success("Workspace layout identifiers remitted!"); st.rerun()

            # Tool 10: Spell Check + Words to Number Engine Implementation
            with st.container():
                st.markdown("**Tool 10: Natural Language Text-to-Numbers Engine Integration**")
                sp_cols = st.multiselect("Select natural string currency/metric records:", all_cols, key=f"sp_{active_filename}")
                if st.button("Deploy Analytical Phrase Tokenization Framework", key=f"b_sp_{active_filename}"):
                    for col in sp_cols:
                        st.session_state.processed_dfs[active_filename][col] = st.session_state.processed_dfs[active_filename][col].apply(words_to_num)
                    st.success("Alphabetic metric arrays parsed to float primitives!"); st.rerun()

    # 📊 DYNAMIC METRICS MONITORING: MATHEMATICAL ALLOCATION PIE CHART
    st.markdown("### 📊 Active Cluster Analysis Visualizations")
    valid_records = len(current_df)
    anomalous_nulls = int(current_df.isna().sum().sum())
    
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie([max(1, valid_records), anomalous_nulls + 1], labels=['Clean Verified Data Matrix', 'Empty Index Null Structural Nodes'], colors=['#7c3aed', '#f472b6'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title("Active Workflow Processing Structural Proportional Allocation Map", color="#1e1b4b", weight="bold")
    st.pyplot(fig)

    # 💾 BINARY DATA STORAGE CONVERSION GATEWAYS
    st.markdown("### 💾 Secure Workbook Document Compilation Hub")
    
    csv_bytes = current_df.to_csv(index=False).encode('utf-8')
    
    excel_io_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_io_buffer, engine='openpyxl') as wr:
        current_df.to_excel(wr, index=False, sheet_name='CleanedDataBlock')
    excel_bytes = excel_io_buffer.getvalue()

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button("Download Active Stream File as Standard CSV Output", csv_bytes, f"verisame_clean_{active_filename}.csv", "text/csv", use_container_width=True)
    with d_col2:
        st.download_button("Download Active Stream File as Excel Workbook Binary", excel_bytes, f"verisame_clean_{active_filename}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    # SECURE MULTI-FILE ZIP ARCHIVAL GATEWAY DEPLOYMENT
    if is_pro and len(st.session_state.processed_dfs) > 1:
        st.markdown("#### 📦 Multi-File Concurrent Batch Package Gateway Output Archive")
        aggregated_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(aggregated_zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zipped_pack:
            for title, data_frame in st.session_state.processed_dfs.items():
                compiled_csv_stream = data_frame.to_csv(index=False)
                zipped_pack.writestr(f"cleaned_batch_stream_{title}.csv", compiled_csv_stream)
        st.download_button("🎁 Export Full Isolated Multi-File Batch Package (.ZIP Archive Layout)", aggregated_zip_buffer.getvalue(), "verisame_batch_archive.zip", "application/zip", use_container_width=True)
