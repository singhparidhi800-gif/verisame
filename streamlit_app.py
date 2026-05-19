import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

# SECRET SETTINGS - YE STREAMLIT CLOUD SE AAYENGI
FREE_ROW_LIMIT = 1000
PRO_USERS = st.secrets.get("PRO_USERS", "").split(",")
RAZORPAY_LINK = st.secrets.get("RAZORPAY_LINK", "https://wa.me/919794906852")
WHATSAPP_NO = st.secrets.get("WHATSAPP_NO", "919794906852")

# RATE LIMITING SETUP
if 'last_run' not in st.session_state:
    st.session_state.last_run = datetime.now() - timedelta(seconds=10)

# SESSION STATE SETUP
if 'user_type' not in st.session_state:
    st.session_state.user_type = 'pro' if st.query_params.get("email") in PRO_USERS else 'free'
if 'rows_used_this_month' not in st.session_state:
    st.session_state.rows_used_this_month = 0
if 'first_use_date' not in st.session_state:
    st.session_state.first_use_date = datetime.now()

# MONTHLY LIMIT RESET
if datetime.now() > st.session_state.first_use_date + timedelta(days=30):
    st.session_state.rows_used_this_month = 0
    st.session_state.first_use_date = datetime.now()

# SIDEBAR UI
st.sidebar.title("Verisame 🔍")
st.sidebar.markdown(f"**Plan:** `{st.session_state.user_type.upper()}`")

if st.session_state.user_type == 'free':
    st.sidebar.progress(st.session_state.rows_used_this_month / FREE_ROW_LIMIT)
    st.sidebar.caption(f"Used: {st.session_state.rows_used_this_month}/{FREE_ROW_LIMIT} rows")
    if st.sidebar.button("🚀 Upgrade to Pro ₹2999"):
        st.sidebar.markdown(f"[Pay Karo]({RAZORPAY_LINK})")
else:
    st.sidebar.success("✅ Pro Active")
    st.sidebar.caption("Unlimited rows + Excel download")

# MAIN APP
st.title("Verisame - Data Cleaner")
st.caption("🔒 Your data is never stored. Processed in memory & deleted instantly.")
st.write("Upload CSV ya Excel. Hum duplicate hatayenge + text saaf karenge.")

uploaded_file = st.file_uploader("Apni file upload karo", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    # FILE SIZE LIMIT
    if uploaded_file.size > 200 * 1024 * 1024:
        st.error("❌ File 200MB se badi hai. Pro users contact kare: " + WHATSAPP_NO)
        st.stop()

    # RATE LIMIT CHECK
    time_diff = (datetime.now() - st.session_state.last_run).total_seconds()
    if time_diff < 10:
        st.warning(f"⏳ Thoda ruk jao. {int(10-time_diff)} sec baad try karo.")
        st.stop()
    st.session_state.last_run = datetime.now()

    # SAFE FILE READ
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error("File read nahi ho paayi. Sirf CSV/Excel chahiye.")
        st.stop()

    total_rows = len(df)
    st.write(f"📊 File me **{total_rows} rows** hain")

    # FREE USER LIMIT CHECK
    if st.session_state.user_type == 'free':
        rows_left = FREE_ROW_LIMIT - st.session_state.rows_used_this_month
        if total_rows > rows_left:
            st.error(f"❌ Limit Khatam! Sirf {rows_left} rows bache hain is mahine.")
            st.link_button("Pro Kharido ₹2999", RAZORPAY_LINK)
            st.stop()

    # TIME DELAY
    if st.session_state.user_type == 'free':
        with st.spinner('Free user: Processing... 30 sec wait ⏳'):
            time.sleep(30)
    else:
        with st.spinner('Pro Speed: Processing... 2 Sec ⚡'):
            time.sleep(2)

    # CLEANING LOGIC
    df_cleaned = df.copy()
    del df
    initial_count = len(df_cleaned)
    df_cleaned = df_cleaned.drop_duplicates()
    duplicates_removed = initial_count - len(df_cleaned)

    text_cols = df_cleaned.select_dtypes(include=['object']).columns
    for col in text_cols:
        df_cleaned[col] = df_cleaned[col].astype(str).str.strip().str.title()
        df_cleaned[col] = df_cleaned[col].replace('Nan', '')

    st.success(f"✅ Done! {duplicates_removed} duplicates hataye.")
    st.write(f"**Cleaned Rows:** {len(df_cleaned)}")

    if st.session_state.user_type == 'free':
        st.session_state.rows_used_this_month += total_rows

    # DOWNLOAD
    st.subheader("Preview Cleaned Data")
    if st.session_state.user_type == 'pro':
        st.dataframe(df_cleaned.head(100))
        csv_data = df_cleaned.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full CSV", csv_data, "verisame_cleaned.csv", "text/csv")
        del df_cleaned, csv_data
    else:
        st.dataframe(df_cleaned.head(3))
        st.info("💡 Pro users ko full Excel download milta hai.")
        del df_cleaned

st.sidebar.markdown("---")
st.sidebar.caption(f"🔒 Zero Data Storage | Support: {WHATSAPP_NO}")
