import engine
CASES = [("Congratulations! You are selected for a Work-From-Home job at a leading MNC. Salary Rs 45,000/month. Pay Rs 2,500 registration fee today to confirm: global-careers-hire.in/apply", "DANGEROUS"),
 ("Dear customer, your SBI KYC has expired. Update within 2 hours or your account will be blocked: sbi-kyc-help.xyz/verify", "DANGEROUS"),
 ("Sir, ungal HDFC KYC expire aagiduchu. 2 manikkulla update pannunga illana account block aagum: hdfc-update.top/login", "DANGEROUS"),
 ("Your OTP for SBI login is 482910. Do not share it with anyone.", "SAFE"),
 ("Rs 450 debited from a/c XX1234 on 12-Oct. If not you, call the number on your card.", "SAFE"),
 ("Your Amazon order #4821 has been shipped. Track it here: https://www.amazon.in/orders/482", "SAFE"),
 ("Hey, are we meeting at 5 PM today? Don't forget the notes.", "SAFE")]
ok = 0
for t, want in CASES:
    r = engine.analyze(t); good = r["verdict"] == want; ok += good
    print("PASS" if good else "FAIL", r["verdict"], r["score"], "|", t[:50], "|", r["reasons"][:2])
print(f"{ok}/{len(CASES)} passed")
