
import streamlit as st
import json, os, io
import pandas as pd
import re
from datetime import datetime, timedelta
import difflib

# Safe imports to completely avoid Streamlit Deployment Crashes
try:
    import openpyxl
except Exception:
    openpyxl = None

st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ROBUST WORD-TO-NUMBER CONVERSION
def words_to_num(s):
    if pd.isna(s): return s
    s_str = str(s).lower().strip()
    if s_str.isdigit():
        return int(s_str)
    try:
        if float(s_str): return float(s_str)
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
    return total + current if has_num_word and (total + current > 0) else s

T = {
    "title":"VeriSame","subtitle":"The Fastest Way to Clean Your Data",
    "upload_tab":"📤 Upload File","sample_tab":"🎯 Try Demo",
    "upload_text":"Drop CSV, Excel or JSON file here","sample_btn":"Load Sample Data","summary_title":"Data Summary",
    "rows":"Total Rows","clean":"Clean Rows","dups":"Duplicates Removed","empty":"Empty Cells Fixed","preview":"Live Preview (Green Highlights show where tools worked 🟢)",
    "tools_menu":"AI Studio","download_title":"Export Data",
    "download_success":"🎉 Download Ready!","tab1":"Date & Nulls","tab2":"Email & Phone","tab3":"Text Tools",
    "tool1":"Smart Date Converter","tool2":"AI Fill Nulls","tool3":"Email Validator","tool4":"Phone Formatter","tool5":"Case Converter",
    "tool6":"Remove Symbols","tool7":"Bulk Rename","tool8":"Remove Duplicates","tool9":"Trim Spaces","tool10":"Spell Check",
    "select_col":"Select Columns","select_case":"Choose Case Type","apply_btn":"Apply","success":"Apply is completed! Your data has been successfully updated.",
    "admin_title":"👑 Sherni Admin Panel 👑","admin_pending":"User Databases & Requests","admin_user":"Customer Email","admin_plan":"Plan","admin_expiry":"Valid Till","delete_btn":"Delete User",
    "download_csv":"Download as CSV","download_excel":"Download as Excel"
}

# CSS STYLING WITH CHERRY BLOSSOMS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 25%, #c084fc 50%, #a855f7 75%, #9333ea 100%); background-size: 400% 400%; animation: aurora 15s ease infinite; padding-top: 0.3rem;}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}
.block-container {background: rgba(255,255,255,0.96); backdrop-filter: blur(25px) saturate(180%); border-radius: 28px; padding: 2rem; max-width: 1200px; margin: 0 auto; box-shadow: 0 30px 60px rgba(139,92,246,0.25); border: 1.5px solid rgba(255,255,255,0.5);}
@media (max-width: 768px) {
.block-container {padding: 1rem!important; border-radius: 20px!important;}
h1 {font-size: 2.2rem!important;}
}
h1,h2,h3,p,span,label,div,li {color: #000!important; font-weight: 600!important;}
h1 {font-weight: 800!important; font-size: 3.2rem!important; margin-bottom: 0.2rem!important; background: linear-gradient(90deg, #6b21a8, #9333ea, #c084fc, #a855f7, #6b21a8); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 3s linear infinite;}
@keyframes shine {0%{background-position: 0% center;} 100%{background-position: 200% center;}}
.subtitle {text-align: left; color: #000!important; font-size: 1.1rem!important; font-weight: 600!important; margin-bottom: 1rem!important;}
.logo-float {animation: float 3s ease-in-out infinite;}
@keyframes float {0%,100%{transform: translateY(0px);} 50%{transform: translateY(-10px);}}
.anime-container {position: relative; width: 100%; min-height: 280px; border-radius: 25px; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.3); border: 3px solid #9333ea;}
.anime-container img {width: 100%; height: 280px; object-fit: cover; object-position: center top; display: block;}
.pricing-card {
  position: relative; border-radius: 22px; padding: 1.6rem; background: rgba(255,255,255,0.92)!important;
  backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(147,51,234,0.15), 0 2px 6px rgba(147,51,234,0.1);
  height: 100%; transform: translateZ(0); border: 2.5px solid #9333ea; clip-path: polygon(0% 3%, 3% 0%, 97% 0%, 100% 3%, 100% 97%, 97% 100%, 3% 100%, 0% 97%);
}

.stButton>button {
    border-radius: 14px!important;
    font-weight: 700!important;
    background: linear-gradient(90deg, #9333ea, #a855f7)!important;
    color: white!important;
    border: none!important;
    padding: 13px 26px!important;
    width: 100%!important;
    box-shadow: 0 5px 18px rgba(147,51,234,0.4)!important;
    transition: all 0.3s!important;
    cursor: pointer!important;
    font-size: 1rem!important;
    margin-top: 1rem!important;
}
.stButton>button:hover {transform: translateY(-3px) scale(1.02)!important; box-shadow: 0 10px 28px rgba(147,51,234,0.5)!important;}

.pro-banner {background: linear-gradient(135deg, #7e22ce, #a855f7, #d946ef); padding: 1.6rem; border-radius: 22px; color: white!important; text-align: center; margin: 1rem 0; border: 2px solid #9333ea; box-shadow: 0 8px 20px rgba(147,51,234,0.3);}
.pro-banner h2 {color: white!important;}
.tool-chip {display: inline-block; background: rgba(255,255,255,0.95); padding: 9px 17px; border-radius: 28px; margin: 4px; font-weight: 700; border: 2px solid #9333ea; color: #000!important; font-size: 0.92rem;}
div[data-testid="stTabs"] button p {color: #000!important; font-weight: 700!important; font-size: 1rem!important;}
div[data-testid="stTabs"] button[aria-selected="true"] p {color: #6b21a8!important; font-weight: 800!important; border-bottom: 3px solid #9333ea;}
div[data-testid="stTabs"] button {background: rgba(255,255,255,0.7)!important; backdrop-filter: blur(5px); border-radius: 12px; margin-right: 8px; border: 2px solid #9333ea;}
.stAlert,.stInfo,.stSuccess,.stError {color: #000!important; font-weight: 600!important; background: rgba(255,255,255,0.8)!important; backdrop-filter: blur(5px); border-radius: 12px; border: 2px solid #9333ea;}
.stDataFrame {background: rgba(255,255,255,0.9)!important;}
.stFileUploader {background: rgba(255,255,255,0.8)!important; border: 2px dashed #9333ea;}

.cherry {position: fixed; top: -10vh; color: #FFB7C5; font-size: 20px; animation: fall linear infinite; z-index: 9999; pointer-events: none;}
@keyframes fall {0%{transform: translateY(0vh) translateX(0vw) rotate(0deg); opacity: 1;} 100%{transform: translateY(110vh) translateX(10vw) rotate(360deg); opacity: 0;}}
</style>
<div class="cherry" style="left: 10%; animation-duration: 8s;">🌸</div>
<div class="cherry" style="left: 20%; animation-duration: 12s; animation-delay: 1s;">🌸</div>
<div class="cherry" style="left: 30%; animation-duration: 10s; animation-delay: 2s;">🌸</div>
<div class="cherry" style="left: 45%; animation-duration: 14s; animation-delay: 0.5s;">🌸</div>
<div class="cherry" style="left: 55%; animation-duration: 9s; animation-delay: 4s;">🌸</div>
<div class="cherry" style="left: 70%; animation-duration: 11s; animation-delay: 1s;">🌸</div>
<div class="cherry" style="left: 80%; animation-duration: 13s; animation-delay: 2.5s;">🌸</div>
<div class="cherry" style="left: 90%; animation-duration: 7s; animation-delay: 3s;">🌸</div>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame's Smart AI Studio. 💎"}]

if "changed_cells" not in st.session_state:
    st.session_state.changed_cells = set()

for key in ['df_clean','show_balloon','sample_loaded','df_loaded','orig_len','empty_fixed']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['df_clean','orig_len','empty_fixed'] else False

# HELPER TO AUTOMATICALLY HIGHLIGHT CHANGED CELLS IN GREEN
def track_modifications(old_df, new_df):
    try:
        for col in old_df.columns:
            if col in new_df.columns:
                mismatch_indices = old_df[old_df[col].astype(str)!= new_df[col].astype(str)].index
                for idx in mismatch_indices:
                    st.session_state.changed_cells.add((idx, col))
    except Exception:
        pass

def apply_cell_styling(df_to_style):
    def highlight_cells(x):
        df_colors = pd.DataFrame('', index=x.index, columns=x.columns)
        for row, col in st.session_state.changed_cells:
            if row in df_colors.index and col in df_colors.columns:
                df_colors.at[row, col] = 'background-color: #bbf7d0; color: #047857; font-weight: bold;'
        return df_colors
    return df_to_style.style.apply(highlight_cells, axis=None)

# 🔒 SIDEBAR DISPLAY FOR FREE FOREVER + BACK BUTTON + CHATBOT
st.sidebar.markdown(
    """
    <div style="border: 2px solid #a855f7; padding: 10px; border-radius: 10px; background-color: #f3e8ff; text-align: center; margin-bottom: 15px;">
        <p style="margin: 0; font-weight: bold; color: #6b21a8;">Plan: FREE FOREVER ✨</p>
    </div>
    """,
    unsafe_allow_html=True
)

# BACK BUTTON ADDED
if st.sidebar.button("⬅️ Back to Home", use_container_width=True):
    st.session_state.df_loaded = False
    st.rerun()

# CHATBOT ADDED
st.sidebar.markdown("### 💬 AI Assistant")
user_msg = st.sidebar.text_input("Ask me anything...", key="chat_input")
if st.sidebar.button("Send", key="send_chat"):
    if user_msg:
        st.session_state.chat_history.append({"role": "user", "message": user_msg})
        st.session_state.chat_history.append({"role": "assistant", "message": f"You asked: {user_msg}. I'm here to help with data cleaning! 💎"})
        st.rerun()

for chat in st.session_state.chat_history[-3:]:
    if chat["role"] == "user":
        st.sidebar.markdown(f"**You:** {chat['message']}")
    else:
        st.sidebar.markdown(f"**Bot:** {chat['message']}")

# 👑 SHERNI ADMIN PANEL VIA ROUTING QUERY PARAMS - PAYMENT SYSTEM REMOVED
if "admin" in st.query_params:
    st.title(T['admin_title'])
    st.subheader(T['admin_pending'])
    st.info("System is currently locked to FREE FOREVER. No payment actions or approvals required.")
    st.stop()

# MAIN LOGO SECTION
col1, col2, col3 = st.columns([1.1, 2.2, 1.7])
with col1: st.markdown("""<div class="logo-float" style="width: 100%; min-height: 280px; display: flex; align-items: center; justify-content: center;"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width: 100%; height: auto; max-height: 280px; object-fit: contain;"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='margin-top: 5px; margin-bottom: 5px;'>VeriSame</h1>", unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{T["subtitle"]}</div>', unsafe_allow_html=True)
with col3: st.markdown("""<div class="anime-container"><img src="https://i.postimg.cc/8zdnX54g/IMG-20260609-WA0012.jpg"></div>""", unsafe_allow_html=True)
st.markdown(f"<div class='pro-banner'><h2>💎 {T['title']} - FREE EDITION</h2><div>{''.join([f"<span class='tool-chip'>{tool}</span>" for tool in ['Smart Date','Case Converter','Remove Duplicates','Trim Spaces']])}</div></div>", unsafe_allow_html=True)

# LOAD TABS
tab1, tab2 = st.tabs([T['upload_tab'], T['sample_tab']])
df = None
with tab1:
    file = st.file_uploader(T['upload_text'], type=["csv","xlsx","xls","json"], accept_multiple_files=True)
    if file:
        try:
            df_list = []
            for f in file:
                if f.name.endswith((".xlsx", ".xls")):
                    excel_file = pd.ExcelFile(f)
                    sheet_names = excel_file.sheet_names
                    selected_sheet = st.selectbox(f"📄 Select Sheet to Clean for {f.name}", sheet_names, key=f"sheet_sel_{f.name}")
                    sub_df = pd.read_excel(f, sheet_name=selected_sheet)
                elif f.name.endswith(".csv"):
                    sub_df = pd.read_csv(f)
                else:
                    sub_df = pd.read_json(f)
                df_list.append(sub_df)
            df = pd.concat(df_list, ignore_index=True) if df_list else None
        except Exception as e: st.error(f"Error reading file: {str(e)}")
with tab2:
    if st.button(T['sample_btn'], use_container_width=True):
        df = pd.DataFrame({"Date":["12/5/2024","","15-03-2023"],"Name":[" RAHUL KUMAR ","priya sharma","AMIT SINGH"],"Email":["RAHUL@GMAIL.COM","bad@","priya@email.com"],"Phone":["98765-43210","9123 456 789","000123"],"Salary":["one hundred","250","two thousand five hundred"]})

if df is not None:
    if 'df_loaded' not in st.session_state or not st.session_state.df_loaded:
        st.session_state.df_clean = df.copy()
        orig_len = len(df)
        df_clean = st.session_state.df_clean.drop_duplicates()
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
            if any(k in col.lower() for k in ['salary','amount','price','paisa']):
                df_clean[col] = df_clean[col].apply(words_to_num)
        st.session_state.df_clean = df_clean
        st.session_state.df_loaded = True
        st.session_state.orig_len = orig_len
        st.session_state.empty_fixed = int(df.isna().sum().sum())
        st.session_state.changed_cells = set()

    try:
        if st.session_state.get('df_clean') is not None:
            df_clean = st.session_state.df_clean
            orig_len = st.session_state.orig_len

            st.markdown(f"<h2>{T['summary_title']}</h2>", unsafe_allow_html=True)
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric(T['rows'], orig_len)
            with c2: st.metric(T['clean'], len(df_clean))
            with c3: st.metric(T['dups'], orig_len-len(df_clean))
            with c4: st.metric(T['empty'], st.session_state.empty_fixed)

            st.markdown(f"<h2>{T['tools_menu']}</h2>", unsafe_allow_html=True)
            st.caption(T['preview'])

            styled_df = apply_cell_styling(df_clean.head(10))
            st.dataframe(styled_df, use_container_width=True, height=300)

            all_cols = df_clean.columns.tolist()

            # 4 UNLOCKED FREE TOOLS ONLY CYCLE - 6 LOCKED
            tab1,tab2,tab3 = st.tabs([T['tab1'], T['tab2'], T['tab3']])
            with tab1:
                # Tool 1: Smart Date Converter (FREE UNLOCKED)
                st.write(f"**{T['tool1']}** ✅ Unlocked")
                date_cols = st.multiselect(T['select_col'], all_cols, key="ms_date")
                if st.button(T['apply_btn'], key="btn_date", use_container_width=True):
                    old_snapshot = st.session_state.df_clean.copy()
                    for col in date_cols:
                        try:
                            if any(k in col.lower() for k in ['salary', 'amount', 'price', 'phone', 'id', 'score', 'age']):
                                st.error(f"⚠️ Column '{col}' contains numbers/money, not dates!")
                                continue
                            converted = pd.to_datetime(st.session_state.df_clean[col], errors='coerce', format='mixed', dayfirst=True)
                            st.session_state.df_clean[col] = converted.dt.strftime('%Y-%m-%d').fillna("None")
                        except Exception: pass
                    track_modifications(old_snapshot, st.session_state.df_clean)
                    st.success(T['success']); st.rerun()

                # Tool 2: AI Fill Nulls (LOCKED)
                st.write(f"**{T['tool2']}** 🔒 Locked")
                st.multiselect(T['select_col'], all_cols, key="ms_fill_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_fill_disabled", disabled=True, use_container_width=True)

            with tab2:
                # Tool 3: Email Validator (LOCKED)
                st.write(f"**{T['tool3']}** 🔒 Locked")
                st.multiselect(T['select_col'], all_cols, key="ms_email_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_email_disabled", disabled=True, use_container_width=True)

                # Tool 4: Phone Formatter (LOCKED)
                st.write(f"**{T['tool4']}** 🔒 Locked")
                st.multiselect(T['select_col'], all_cols, key="ms_phone_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_phone_disabled", disabled=True, use_container_width=True)

            with tab3:
                # Tool 5: Case Converter (FREE UNLOCKED)
                st.write(f"**{T['tool5']}** ✅ Unlocked")
                case_cols = st.multiselect(T['select_col'], all_cols, key="ms_case")
                case_opt = st.selectbox(T['select_case'], ["Uppercase", "Lowercase", "Title Case"], key="sel_case")
                if st.button(T['apply_btn'], key="btn_case", use_container_width=True):
                    old_snapshot = st.session_state.df_clean.copy()
                    for col in case_cols:
                        if case_opt == "Uppercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.upper()
                        elif case_opt == "Lowercase": st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.lower()
                        else: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.title()
                    track_modifications(old_snapshot, st.session_state.df_clean)
                    st.success(T['success']); st.rerun()

                # Tool 6: Remove Symbols (LOCKED)
                st.write(f"**{T['tool6']}** 🔒 Locked")
                st.multiselect(T['select_col'], all_cols, key="ms_spec_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_spec_disabled", disabled=True, use_container_width=True)

                # Tool 7: Bulk Rename (LOCKED)
                st.write(f"**{T['tool7']}** 🔒 Locked")
                st.selectbox("Old column name", all_cols, key="sel_old_disabled", disabled=True)
                st.text_input("New column name", key="inp_new_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_rename_disabled", disabled=True, use_container_width=True)

                # Tool 8: Remove Duplicates (FREE UNLOCKED)
                st.write(f"**{T['tool8']}** ✅ Unlocked")
                if st.button(T['apply_btn'], key="btn_dedup", use_container_width=True):
                    st.session_state.df_clean = st.session_state.df_clean.drop_duplicates()
                    st.success(T['success']); st.rerun()

                # Tool 9: Trim Spaces (FREE UNLOCKED)
                st.write(f"**{T['tool9']}** ✅ Unlocked")
                trim_cols = st.multiselect(T['select_col'], all_cols, key="ms_trim")
                if st.button(T['apply_btn'], key="btn_trim", use_container_width=True):
                    old_snapshot = st.session_state.df_clean.copy()
                    for col in trim_cols: st.session_state.df_clean[col] = st.session_state.df_clean[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                    track_modifications(old_snapshot, st.session_state.df_clean)
                    st.success(T['success']); st.rerun()

                # Tool 10: Spell Check (LOCKED)
                st.write(f"**{T['tool10']}** 🔒 Locked")
                st.multiselect(T['select_col'], all_cols, key="ms_spell_disabled", disabled=True)
                st.button(T['apply_btn'], key="btn_spell_disabled", disabled=True, use_container_width=True)

            # CLEAN EXPORT CAPABILITIES (DIRECTLY FREE DOWNLOAD, NO QR CODES)
            st.markdown(f"<h2>{T['download_title']}</h2>", unsafe_allow_html=True)
            if st.session_state.show_balloon: st.balloons(); st.session_state.show_balloon = False

            col1, col2 = st.columns(2)
            csv = st.session_state.df_clean.to_csv(index=False).encode()
            if col1.download_button(T['download_csv'], csv, "verisame_clean.csv", mime="text/csv", key="dl_csv_free", use_container_width=True):
                st.session_state.show_balloon = True; st.rerun()
            try:
                if openpyxl is not None:
                    excel = io.BytesIO()
                    st.session_state.df_clean.to_excel(excel, index=False, engine='openpyxl')
                    if col2.download_button(T['download_excel'], excel.getvalue(), "verisame_clean.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel_free", use_container_width=True):
                        st.session_state.show_balloon = True; st.rerun()
            except Exception: pass
    except Exception: pass
