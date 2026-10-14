"""Synthetic training data (English, Tanglish, Hindi-roman, Tamil/Hindi script). Replace with real data for real accuracy."""
import random
BANKS = ["SBI", "HDFC", "ICICI"]; COS = ["Amazon", "TCS", "Infosys", "Flipkart", "a leading MNC"]
WORDS = ["kyc", "verify", "secure", "help", "update", "careers", "hire", "support", "refund", "login"]
TLDS = ["xyz", "top", "online", "site", "club", "in", "com", "info", "click"]
OFFICIAL = ["https://www.amazon.in/orders/{n}", "https://www.sbi.co.in/web/personal-banking", "https://www.irctc.co.in/nget/train-search",
            "https://www.hdfcbank.com/personal", "https://www.google.com/maps", "https://www.flipkart.com/orders/{n}"]
PHISH = [
 "Congratulations! You are selected for a Work-From-Home job at {co}. Salary Rs {sal}/month. Pay Rs {fee} registration fee today to confirm: {u}",
 "Dear customer, your {bank} KYC has expired. Update within {h} hours or your account will be blocked: {u}",
 "You have won Rs {prize} in the {co} lucky draw! Claim your prize now, pay Rs {fee} processing fee: {u}",
 "Your {bank} account is suspended. Verify now and share your OTP and PIN: {u}",
 "Your parcel is held at customs. Pay Rs {fee} delivery charge immediately: {u}",
 "Your electricity will be disconnected tonight. Pay the pending bill now: {u}",
 "Sir, ungal {bank} KYC expire aagiduchu. {h} manikkulla update pannunga illana account block aagum: {u}",
 "Congratulations! Ungalukku {co} la work from home job kedaichirukku. Rs {fee} fee katti confirm pannunga: {u}",
 "Aapka {bank} KYC expire ho gaya hai. {h} ghante mein update karein warna account band ho jayega: {u}",
 "Badhai ho! Aapko {co} mein job mil gayi hai. Rs {fee} registration fee turant bhejein: {u}",
 "உங்கள் {bank} கணக்கு தடை செய்யப்படும். உடனே KYC புதுப்பிக்கவும்: {u}",
 "आपका {bank} खाता बंद हो जाएगा। तुरंत KYC अपडेट करें: {u}",
 "Selected candidates must pay Rs {fee} refundable deposit today to confirm the job. Send to UPI id hr{n}@upi",
 "URGENT: {bank} alert! Send your OTP immediately to avoid account suspension.",
]
LEGIT = [
 "Your OTP for {bank} login is {n}. Do not share it with anyone.",
 "Ungal OTP {n}. Yaarukkum share panna vendaam.",
 "Rs {amt} debited from a/c XX{n} on 12-Oct. If not you, call the number on your card.",
 "Your {co} order #{n} has been shipped. Track it here: {o}",
 "Hey, are we meeting at {t} today? Don't forget the notes.",
 "Reminder: your electricity bill of Rs {amt} is due on 20-Oct. Pay in the official app or at {o}",
 "Your interview with {co} is scheduled for Monday 10 AM. Details are in your registered email.",
 "Happy birthday! Party at my place tonight, come by {t}.",
 "Your {bank} statement for September is ready. Log in to the official app to view it.",
 "Urgent: please send the project report by 5 PM today, the review is tomorrow.",
 "Train ticket confirmed. PNR {n}. Details: {o}",
 "Kal class {t} ku irukku, notes eduthuttu vaanga.",
 "Aaj shaam {t} baje milte hain, mat bhoolna.",
 "Thanks for your payment of Rs {amt}. Your receipt is available on {o}",
]

def _url(rng, brand_spoof=True):
    b = rng.choice(["sbi", "hdfc", "amazon", "icici", "paytm", "global", "jobs", "secure"])
    host = f"{b}-{rng.choice(WORDS)}-{rng.choice(WORDS)}.{rng.choice(TLDS)}" if rng.random() < .8 else f"{b}{rng.choice(WORDS)}.{rng.choice(TLDS)}"
    pre = rng.choice(["https://", "http://", ""]) if rng.random() < .8 else "bit.ly/"
    return (pre + host if pre != "bit.ly/" else pre + str(rng.randint(10**5, 10**6))) + rng.choice(["/verify", "/apply", "/login", ""])

def make(n=3000, seed=7):
    rng = random.Random(seed); rows = []
    for i in range(n):
        d = dict(co=rng.choice(COS), bank=rng.choice(BANKS), sal=rng.choice([25000, 45000, 60000]), fee=rng.choice([500, 1500, 2500, 5000]),
                 h=rng.choice([2, 4, 24]), prize=rng.choice([50000, 500000]), n=rng.randint(1000, 999999), amt=rng.randint(100, 9000),
                 t=rng.choice(["5 PM", "6:30", "4 baje"]), o=rng.choice(OFFICIAL).format(n=rng.randint(100, 999)))
        if i % 2:
            d["u"] = _url(rng) if rng.random() < .9 else rng.choice(OFFICIAL).format(n=1)
            rows.append((rng.choice(PHISH).format(**d), 1, rng.random() < .7))
        else:
            rows.append((rng.choice(LEGIT).format(**d), 0, rng.random() < .02))
    return rows
