import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase connect - wahi purana wala
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ===== SECURITY LOCK =====
ADMIN_PASSWORD = "sherni@123"  # Ye password tu badal dena apna wala daal ke

pwd = st.text_input("Admin Password Daalo", type="password")
if pwd != ADMIN_PASSWORD:
    st.error("Galat password sherni! Tu hi hai na? 😎")
    st.stop()

st.success("Welcome Boss! 🔥 Payment Control Room")
st.title("💰 Payment Control Panel")

# ===== SAARE USER DIKHAO =====
docs = db.collection("users").stream()

data = []
for doc in docs:
    d = doc.to_dict()
    data.append({
        "Email": doc.id,
        "Plan": d.get("plan", "N/A"),
        "Amount": f"₹{d.get('amount', 0)}",
        "Status": d.get("status", "pending"),
        "Date": d.get("timestamp", "N/A")
    })

if not data:
    st.info("Abhi koi user nahi hai. Marketing kar jaldi! 📢")
else:
    for user in data:
        col1, col2, col3, col4, col5 = st.columns([3,1,1,1,2])
        
        col1.write(f"**{user['Email']}**")
        col2.write(user['Plan'])
        col3.write(user['Amount'])
        
        if user['Status'] == "pending":
            col4.error("Pending")
            if col5.button("✅ Paid Karo", key=user['Email']):
                db.collection("users").document(user['Email']).update({"status": "paid"})
                st.rerun()  # Page refresh ho jayega
        else:
            col4.success("Paid ✅")
            col5.write("Unlocked")

st.divider()
st.caption("Tip: Password 'sherni@123' ko badal dena. Kisi ko mat batana 🔒")
