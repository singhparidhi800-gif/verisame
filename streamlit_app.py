import streamlit as st
import io
import pandas as pd
import re

# 🔒 App Setup (Anti-Dark Mode Enforced Glossy CSS - Your Exact Theme)
st.set_page_config(page_title="VeriSame", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# Secret admin query target configuration
ADMIN_QUERY_VALUE = "Sherni@123"

if 'session_active' not in st.session_state: st.session_state.session_active = False
if 'current_plan' not in st.session_state: st.session_state.current_plan = ""
if 'uploaded_data' not in st.session_state: st.session_state.uploaded_data = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "message": "Hello! Welcome to VeriSame's Smart AI Studio. 💎 Ask me anything about data cleaning features!"}]

# Custom Word-to-Number Logic for Tool 10
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

# Styling & CSS with Layout, 3D Effects, and Floating Animation Fixes
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}

.stApp {
    background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 25%, #d8b4fe 50%, #c084fc 75%, #a855f7 100%) !important; 
    background-size: 400% 400% !important; 
    animation: aurora 20s ease infinite !important; 
}
@keyframes aurora {0%{background-position: 0% 50%} 50%{background-position: 100% 50%} 100%{background-position: 0% 50%}}

/* 3D Glassmorphism Panel Depth Card */
.block-container {
    background: rgba(255, 255, 255, 0.96) !important; 
    backdrop-filter: blur(35px) saturate(210%) !important; 
    border-radius: 35px !important; 
    padding: 2.5rem !important; 
    max-width: 1260px; 
    margin: 1.5rem auto !important; 
    box-shadow: 0 30px 70px rgba(109, 40, 217, 0.2), inset 0 0 20px rgba(255, 255, 255, 0.6) !important; 
    border: 3px solid rgba(255, 255, 255, 0.8) !important;
    transform: perspective(1000px) translateZ(0px);
}

h1,h2,h3,p,span,label,div,li {color: #1e1b4b!important; font-weight: 600!important;}
h1 {
    font-weight: 900!important; 
    font-size: 3.6rem!important; 
    margin-bottom: 0.1rem!important; 
    background: linear-gradient(90deg, #4c1d95, #7c3aed, #c084fc, #6d28d9, #4c1d95) !important; 
    background-size: 200% auto !important; 
    -webkit-background-clip: text !important; 
    -webkit-text-fill-color: transparent !important; 
}
.subtitle {color: #4b5563!important; font-size: 1.2rem!important; font-weight: 500!important; margin-bottom: 1.2rem!important;}

/* Slow Motion Smooth Floating Animation for Logo */
@keyframes floatLogo {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-12px); }
    100% { transform: translateY(0px); }
}
.floating-logo-container {
    display: flex; align-items: center; justify-content: center; height:100%;
    animation: floatLogo 8s ease-in-out infinite;
}

/* Fixes the cropped anime image perfectly to see full banner context */
.anime-container {
    position: relative; width: 100%; border-radius: 25px; overflow: hidden; 
    box-shadow: 0 20px 45px rgba(76,29,149,0.25); border: 3px solid #7c3aed;
    background-color: #ffffff;
}
.anime-container img {width: 100%; height: auto; max-height: 280px; object-fit: contain; display: block; margin: 0 auto;}

/* Premium 3D Shadow Pricing Cards */
.pricing-card {
    border-radius: 24px; padding: 2rem; background: #ffffff!important;
    box-shadow: 0 15px 35px rgba(147,51,234,0.12), 0 5px 15px rgba(0,0,0,0.05); 
    border: 2.5px solid #e9d5ff !important; height: 100%;
    transition: transform 0.3s ease;
}
.pricing-card:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 20px 40px rgba(147,51,234,0.18);
}

.stButton>button {
    border-radius: 16px !important; font-weight: 700 !important; 
    background: linear-gradient(90deg, #7c3aed, #a855f7) !important; color: white !important; 
    border: none !important; padding: 14px 28px !important; width: 100% !important;
    box-shadow: 0 8px 20px rgba(124, 58, 237, 0.3) !important;
}

.pro-banner {
    background: linear-gradient(135deg, #5b21b6, #7c3aed, #d946ef) !important; 
    padding: 1.2rem; border-radius: 24px; text-align: center; margin: 1.5rem 0;
    box-shadow: 0 10px 25px rgba(91, 33, 182, 0.3);
}
.pro-banner h2 {color: white!important; margin:0;}

.tool-chip {
    display: inline-block; background: rgba(255,255,255,0.2) !important; padding: 8px 18px; 
    border-radius: 30px; margin: 6px; border: 1px solid white !important; color: white !important;
    font-size: 0.9rem;
}

.cherry {position: fixed; top: -10vh; color: #FFB7C5; font-size: 22px; animation: fall linear infinite; z-index: 9999; pointer-events: none;}
@keyframes fall {0%{transform: translateY(0vh) translateX(0vw) rotate(0deg); opacity: 1;} 100%{transform: translateY(110vh) translateX(10vw) rotate(360deg); opacity: 0;}}
</style>
<div class="cherry" style="left: 10%; animation-duration: 8s;">🌸</div>
<div class="cherry" style="left: 30%; animation-duration: 10s; animation-delay: 2s;">🌸</div>
<div class="cherry" style="left: 55%; animation-duration: 9s; animation-delay: 4s;">🌸</div>
<div class="cherry" style="left: 80%; animation-duration: 13s; animation-delay: 2.5s;">🌸</div>
""", unsafe_allow_html=True)

# 🎵 Modern Autoplay Music Bypass Injection Element
st.markdown("""
<iframe src="https://assets.mixkit.co/active_storage/sfx/123/123-200.wav" allow="autoplay" id="audio" style="display:none;"></iframe>
<audio autoplay loop>
    <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mp3">
</audio>
""", unsafe_allow_html=True)

# Top Header Layout (Enhanced columns alignment)
col1, col2, col3 = st.columns([1.6, 2.4, 1.6])
with col1:
    # Enlarged to 220px with smooth slow-motion hover/float action state
    st.markdown("""<div class="floating-logo-container"><img src="https://i.postimg.cc/gjWxsmHf/1779366919870.png" style="width: 220px; height: auto;"></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='margin-top: 30px;'>VeriSame</h1>", unsafe_allow_html=True)
    st.markdown('<div class="subtitle">The Fastest Way to Clean Your Data</div>', unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="anime-container"><img src="https://i.postimg.cc/8zdnX54g/IMG-20260609-WA0012.jpg"></div>""", unsafe_allow_html=True)

# 👑 URL LINK QUERY DETECTION SYSTEM FOR SHERNI ADMIN PANEL
if "admin" in st.query_params and st.query_params["admin"] == ADMIN_QUERY_VALUE:
    st.markdown("## 👑 Sherni Admin Panel Workstation 👑")
    st.info("Secure access granted via explicit URL parameter verification.")
    st.write("Welcome back, Admin! Database backups and logging telemetry streams are healthy.")
    if st.button("Exit Admin View"):
        st.query_params.clear()
        st.rerun()
    st.stop()

# Main Workspace (Before Login / Plan selection)
if not st.session_state.session_active:
    st.markdown("""
    <div class="pro-banner">
        <h2>💎 UNLOCK 10 PREMIUM AI TOOLS 💎</h2>
        <div style="text-align: center; margin-top: 10px;">
            <span class="tool-chip">Smart Date</span>
            <span class="tool-chip">AI Fill</span>
            <span class="tool-chip">Email AI</span>
            <span class="tool-chip">Phone AI</span>
            <span class="tool-chip">Case</span>
            <span class="tool-chip">Clean</span>
            <span class="tool-chip">Rename</span>
            <span class="tool-chip">Dedup</span>
            <span class="tool-chip">Trim</span>
            <span class="tool-chip">Spell</span>
        </div>
        <div style="color: white !important; font-size: 0.85rem; margin-top: 5px; opacity: 0.9;">
            🎵 Peaceful 20s Welcome Track Active • 🧠 Interactive Audio Effects Enabled On UI Action Buttons
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pricing Columns
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="color: #7c3aed !important;">FREE FOREVER</h3>
            <h1 style="font-size: 3rem; margin: 10px 0;">FREE</h1>
            <p style="font-size: 0.9rem; color: #4b5563 !important;">Lifetime</p>
            <p>✓ 1000 Rows Limit</p>
            <p>✓ CSV & Excel Export</p>
            <p>✓ 4 Free Tools Built-in</p>
            <p>✓ 30s Processing</p>
            <p>✓ Email Support</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Free", key="plan_free"):
            st.session_state.current_plan = "free"
            st.session_state.session_active = True
            st.rerun()

    with p_col2:
        st.markdown("""
        <div class="pricing-card" style="border: 2.5px solid #7c3aed !important; box-shadow: 0 15px 30px rgba(124, 58, 237, 0.15) !important;">
            <h3 style="color: #7c3aed !important;">⭐ POPULAR<br>MONTHLY</h3>
            <h1 style="font-size: 3rem; margin: 10px 0;">₹299</h1>
            <p style="font-size: 0.9rem; color: #4b5563 !important;">30 Days</p>
            <p>✓ Unlimited Rows</p>
            <p>✓ CSV + Excel Export</p>
            <p>✓ 10 Premium AI Tools</p>
            <p>✓ 3s Speed</p>
            <p>✓ Priority Support</p>
            <p>✓ No Watermark</p>
            <p>✓ Lifetime Updates</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Pro", key="plan_monthly"):
            st.session_state.current_plan = "pro"
            st.session_state.session_active = True
            st.rerun()

    with p_col3:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="color: #7c3aed !important;">6 MONTHS</h3>
            <h1 style="font-size: 3rem; margin: 10px 0;">₹1499</h1>
            <p style="font-size: 0.9rem; color: #4b5563 !important;">180 Days</p>
            <p>✓ Unlimited Rows</p>
            <p>✓ CSV + Excel Export</p>
            <p>✓ 10 Premium AI Tools</p>
            <p>✓ 3s Speed</p>
            <p>✓ Priority Support</p>
            <p>✓ No Watermark</p>
            <p>✓ Lifetime Updates</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Pro+", key="plan_6months"):
            st.session_state.current_plan = "pro"
            st.session_state.session_active = True
            st.rerun()

# Logged In Layout
else:
    st.success(f"Workspace Active: Plan **{st.session_state.current_plan.upper()}**")
    
    uploaded_file = st.file_uploader("Drop CSV or Excel file here", type=["csv", "xlsx"])
    
    if uploaded_file:
        if st.session_state.uploaded_data is None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                if st.session_state.current_plan == "free" and len(df) > 1000:
                    st.error(f"❌ Limit Exceeded: Free plan only supports up to 1000 rows. Current file has {len(df)} rows.")
                    st.stop()
                    
                st.session_state.uploaded_data = df
            except Exception as e:
                st.error(f"Error reading file: {e}")

    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        st.markdown("### 📊 Live Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        all_columns = df.columns.tolist()
        st.markdown("### 🛠️ Available Data Cleaning Features")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("#### 🆓 Core Tools (Unlocked)")
            
            # Tool 1: Smart Date Converter
            with st.expander("📆 Smart Date Converter"):
                sel_col = st.selectbox("Select Date Column", all_columns, key="t1")
                if st.button("Convert Date Format", key="btn_t1"):
                    st.session_state.uploaded_data[sel_col] = pd.to_datetime(st.session_state.uploaded_data[sel_col], errors='coerce').dt.strftime('%Y-%m-%d')
                    st.success("Successfully Normalized Dates!")
                    st.rerun()

            # Tool 5: Case Converter
            with st.expander("🔤 Case Converter"):
                sel_col = st.selectbox("Select Text Column", all_columns, key="t5")
                case_mode = st.selectbox("Format Type", ["UPPERCASE", "lowercase", "Title Case"], key="mode_t5")
                if st.button("Apply Case Change", key="btn_t5"):
                    if case_mode == "UPPERCASE": st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].astype(str).str.upper()
                    elif case_mode == "lowercase": st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].astype(str).str.lower()
                    else: st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].astype(str).str.title()
                    st.success("Case Updated Successfully!")
                    st.rerun()

            # Tool 8: Remove Duplicates
            with st.expander("👥 Remove Duplicates"):
                if st.button("Purge Duplicated Rows", key="btn_t8"):
                    st.session_state.uploaded_data = st.session_state.uploaded_data.drop_duplicates()
                    st.success("Duplicates Removed!")
                    st.rerun()

            # Tool 9: Trim Spaces
            with st.expander("✂️ Trim Spaces"):
                sel_col = st.selectbox("Select Target Column", all_columns, key="t9")
                if st.button("Clean Whitespaces", key="btn_t9"):
                    st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].astype(str).str.strip()
                    st.success("Whitespaces Trimmed!")
                    st.rerun()

        with col_t2:
            st.markdown("#### 💎 Premium Tools")
            
            if st.session_state.current_plan != "pro":
                st.warning("🔒 Upgrade to Pro to unlock Premium AI modules.")
            else:
                # Tool 2: AI Fill Nulls
                with st.expander("✨ AI Fill Nulls"):
                    sel_col = st.selectbox("Select Target Column", all_columns, key="t2")
                    fill_val = st.text_input("Fill Value", placeholder="e.g. Unknown")
                    if st.button("Fill Empty Cells", key="btn_t2"):
                        st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].fillna(fill_val)
                        st.success("Null Values Handled!")
                        st.rerun()

                # Tool 3: Email Validator
                with st.expander("📧 Email Validator"):
                    sel_col = st.selectbox("Select Email Column", all_columns, key="t3")
                    if st.button("Validate Emails", key="btn_t3"):
                        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                        st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].astype(str).apply(lambda x: x if re.match(pattern, x) else "Invalid Email")
                        st.success("Emails Evaluated!")
                        st.rerun()

                # Tool 4: Phone Formatter
                with st.expander("📱 Phone Formatter"):
                    sel_col = st.selectbox("Select Phone Column", all_columns, key="t4")
                    if st.button("Format Phone Numbers", key="btn_t4"):
                        st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].astype(str).apply(lambda x: "".join(re.findall(r'\d+', x))[-10:])
                        st.success("Phone Formats Cleaned!")
                        st.rerun()

                # Tool 6: Remove Symbols
                with st.expander("🚫 Remove Symbols"):
                    sel_col = st.selectbox("Select Column", all_columns, key="t6")
                    if st.button("Strip Special Characters", key="btn_t6"):
                        st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x))
                        st.success("Symbols Stripped!")
                        st.rerun()

                # Tool 7: Bulk Rename
                with st.expander("✏️ Rename Columns"):
                    old_n = st.selectbox("Pick Column", all_columns, key="t7")
                    new_n = st.text_input("New Name Title", key="t7_new")
                    if st.button("Rename Layout Now", key="btn_t7") and new_n:
                        st.session_state.uploaded_data.rename(columns={old_n: new_n}, inplace=True)
                        st.success("Column Renamed!")
                        st.rerun()

                # Tool 10: Words-to-Number
                with st.expander("🔢 Words To Numbers Engine"):
                    sel_col = st.selectbox("Pick Target Text Column", all_columns, key="t10")
                    if st.button("Apply Lexical Parsing", key="btn_t10"):
                        st.session_state.uploaded_data[sel_col] = st.session_state.uploaded_data[sel_col].apply(words_to_num)
                        st.success("Text Converted to Absolute Integers!")
                        st.rerun()

        st.markdown("### 📥 Download Cleaned Data")
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Clean File (CSV)", csv_data, "cleaned_data.csv", "text/csv", use_container_width=True)

        if st.button("← Reset Layout Session"):
            st.session_state.uploaded_data = None
            st.rerun()

# Chatbot Placement at the absolute bottom
st.markdown("---")
st.markdown("### 💬 VeriSame Live AI Chat Studio")

for chat in st.session_state.chat_history:
    if chat["role"] == "assistant":
        st.markdown(f"**🤖 AI:** {chat['message']}")
    else:
        st.markdown(f"**👤 You:** {chat['message']}")

u_input = st.text_input("Ask a question...", placeholder="e.g., How does Tool 4 work?", key="chat_msg_main")
if st.button("Send Message 🚀", key="send_btn_main") and u_input:
    st.session_state.chat_history.append({"role": "user", "message": u_input})
    u_lower = u_input.lower()
    ans = "I can guide you about any of our 10 tools! Just specify the tool you are interested in."
    if "tool 1" in u_lower or "date" in u_lower: ans = "Tool 1 normalizes dynamic variations of date formats cleanly into standard YYYY-MM-DD configurations."
    elif "free" in u_lower: ans = "The free tier gives access to exactly 4 unlocked core layout tools with a 1000 row restriction."
    elif "creator" in u_lower or "founder" in u_lower: ans = "👑 VeriSame's system platform architecture was completely envisioned and built by **Anugya Singh**."
    
    st.session_state.chat_history.append({"role": "assistant", "message": ans})
    st.rerun()
