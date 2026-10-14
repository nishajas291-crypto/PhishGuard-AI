import json, os
import pandas as pd
import streamlit as st
import engine

st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️", layout="centered")
EXAMPLES = {
 "Job offer scam": "Congratulations! You are selected for a Work-From-Home job at a leading MNC. Salary Rs 45,000/month. Pay Rs 2,500 registration fee today to confirm: global-careers-hire.in/apply",
 "Bank KYC scam": "Dear customer, your SBI KYC has expired. Update within 2 hours or your account will be blocked: sbi-kyc-help.xyz/verify",
 "Tanglish KYC scam": "Sir, ungal HDFC KYC expire aagiduchu. 2 manikkulla update pannunga illana account block aagum: hdfc-update.top/login",
 "Genuine OTP message": "Your OTP for SBI login is 482910. Do not share it with anyone.",
 "Genuine order update": "Your Amazon order #4821 has been shipped. Track it here: https://www.amazon.in/orders/482",
 "Friend message": "Hey, are we meeting at 5 PM today? Don't forget the notes.",
}
st.title("🛡️ PhishGuard AI")
st.caption("Paste a message or link. Get a risk score, the reasons, and what to do next.")
with st.sidebar:
    st.header("Options")
    age = st.number_input("Domain age in days (demo override, 0 = unknown)", 0, 5000, 0)
    lookup = st.checkbox("Look up domain age online (needs python-whois)")
    mp = engine.MODEL_PATH.replace("model.joblib", "metrics.json")
    if os.path.exists(mp):
        st.subheader("Model metrics")
        st.json(json.load(open(mp)))
        st.caption("Measured on the training source shown above. Retrain on real data before quoting these.")
choice = st.selectbox("Try an example", ["(type your own)"] + list(EXAMPLES))
text = st.text_area("Message", EXAMPLES.get(choice, ""), height=120)
if st.button("Check message", type="primary") and text.strip():
    r = engine.analyze(text, domain_age=age or None, lookup=lookup)
    color = {"DANGEROUS": "🔴", "SUSPICIOUS": "🟡", "SAFE": "🟢"}[r["verdict"]]
    st.subheader(f"{color} {r['verdict']}  {r['score']}%")
    st.progress(min(int(r["score"]), 100) / 100)
    if r["reasons"]:
        st.markdown("**Why:**")
        for x in r["reasons"]:
            st.markdown(f"- {x}")
    (st.error if r["verdict"] == "DANGEROUS" else st.warning if r["verdict"] == "SUSPICIOUS" else st.success)(r["advice"])
    with st.expander("How the score was calculated"):
        c = pd.Series({k: v for k, v in r["contrib"].items() if abs(v) > 0.01}).sort_values()
        st.bar_chart(c)
        st.caption("Positive bars push the score toward scam, negative bars toward safe. Exact for a linear model.")
        if r["info"]["host"]:
            st.write("Link found:", r["info"]["host"])
