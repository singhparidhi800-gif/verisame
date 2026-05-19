    import streamlit as st
import pandas as pd
import re
from io import BytesIO
import time
from urllib.parse import parse_qs

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="VeriSame Pro - Data Cleaning Suite",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- LOAD SECRETS ---
PRO_USERS = st.secrets.get("PRO_USERS", "").split(",")
RAZORPAY_LINK = st.secrets.get("RAZORPAY_LINK", "")
WHATSAPP_NO = st.secrets.get("WHATSAPP_NO", "")

# --- PRO PLAN SETUP ---
FREE_ROW_LIMIT = 1000
FREE_DOWNLOAD_LIMIT = 100
FREE_WAIT_TIME = 30

def get_user_email():
    try:
        query_params = st.query_params
        return query_params.get("email", [None])[0]
    except:
        return None

def is_pro_user():
    email = get_user_email()
    return email and email.strip().lower() in [u.strip().lower() for u in PRO_USERS]

IS_PRO = is_pro_user()

# --- SIDEBAR ---
with st.sidebar:
    st.title("💼 VeriSame Pro")
    if IS_PRO:
        st.success("✅ Pro Plan Active")
        st.write("🚀 Unlimited Rows")
        st.write("⚡ Full Downloads")
        st.write("🔓 No Wait Time")
    else:
        st.warning("Current Plan: FREE")
        st.write(f"📊 Limit: {FREE_ROW_LIMIT} rows")
        st.write(f"📥 Download: {FREE_DOWNLOAD_LIMIT} rows")
        st.write(f"⏳ Wait: {FREE_WAIT_TIME}s per file")
        st.markdown("---")
        if RAZORPAY_LINK:
            st.link_button("🚀 Upgrade to Pro ₹2999", RAZORPAY_LINK, use_container_width=True)
        st.caption("After payment, WhatsApp us your email")

# --- MAIN APP ---
st.title("VeriSame Pro - Data Cleaning Suite")
if IS_PRO:
    st.success("Welcome Admin! Enterprise Data Cleaning & Duplicate Removal Tool")
else:
    st.info("Upload your CSV/Excel files. Duplicate removal + smart text cleaning.")

# --- CLEANING FUNCTIONS ---
def clean_text(text):
    if not isinstance(text, str): return text
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.title()

def process_dataframe(df):
    original_rows = len(df)
    df = df.drop_duplicates()
    after_dedup = len(df)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(clean_text)
    return df, original_rows, after_dedup

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Apni file upload karo", type=["csv", "xlsx", "xls"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    total_rows = len(df)

    st.write(f"📊 Total Rows: {total_rows}")

    if not IS_PRO and total_rows > FREE_ROW_LIMIT:
        st.error(f"❌ Free plan limit: {FREE_ROW_LIMIT} rows. Upgrade to Pro for unlimited.")
        st.stop()

    if not IS_PRO:
        with st.spinner(f"⏳ Free users: {FREE_WAIT_TIME} second wait..."):
            time.sleep(FREE_WAIT_TIME)

    with st.spinner("🔄 Cleaning data..."):
        cleaned_df, original, after_dedup = process_dataframe(df)

    st.success(f"✅ Done! {original} → {after_dedup} rows. Removed {original - after_dedup} duplicates.")
    st.dataframe(cleaned_df.head())

    if not IS_PRO and len(cleaned_df) > FREE_DOWNLOAD_LIMIT:
        st.warning(f"⚠️ Free download limit: {FREE_DOWNLOAD_LIMIT} rows. Upgrade for full file.")
        download_df = cleaned_df.head(FREE_DOWNLOAD_LIMIT)
    else:
        download_df = cleaned_df

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        download_df.to_excel(writer, index=False, sheet_name='Cleaned')

    st.download_button(
        label="📥 Download Cleaned File",
        data=output.getvalue(),
        file_name="VeriSame_Cleaned.xlsx",
        mime="application/vnd.ms-excel"
    )
