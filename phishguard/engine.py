"""PhishGuard AI engine: feature extraction + explainable scoring."""
import os, re, datetime, joblib
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "model.joblib")

BRANDS = {"sbi": "sbi.co.in", "hdfc": "hdfcbank.com", "icici": "icicibank.com", "amazon": "amazon.in",
          "paytm": "paytm.com", "phonepe": "phonepe.com", "flipkart": "flipkart.com", "tcs": "tcs.com",
          "infosys": "infosys.com", "google": "google.com", "irctc": "irctc.co.in", "whatsapp": "whatsapp.com"}
OFFICIAL = set(BRANDS.values())
BAD_TLD = {"xyz", "top", "club", "info", "click", "work", "buzz", "online", "site", "icu", "live", "shop"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "rb.gy", "cutt.ly", "is.gd", "shorturl.at"}

KW = {
 "urgency": ["urgent", "immediately", "within 2 hours", "expire", "expired", "expires", "last chance", "today only",
             "right now", "act now", "hours", "avasaram", "udane", "manikkulla", "turant", "jaldi", "ghante",
             "तुरंत", "जल्दी", "உடனே", "அவசரம்"],
 "money_ask": ["registration fee", "processing fee", "pay rs", "pay ₹", "deposit", "advance", "refundable",
               "delivery charge", "fee", "upi id", "katti", "bhejein", "शुल्क", "பணம்", "கட்டணம்"],
 "credential_ask": ["otp", "pin", "password", "cvv", "kyc", "aadhaar", "aadhar", "pan card", "verify your",
                    "update your", "verify now", "login details"],
 "reward_bait": ["congratulations", "you have won", "lucky draw", "lottery", "prize", "selected", "work from home",
                 "work-from-home", "salary", "free gift", "cashback", "badhai", "kedaichirukku", "बधाई", "வாழ்த்துக்கள்"],
 "threat": ["blocked", "block", "suspended", "suspend", "disconnected", "legal action", "arrest", "band ho",
            "account band", "customs", "தடை", "बंद हो जाएगा"],
 "safe_warning": ["do not share", "don't share", "never share", "do not disclose", "share panna vendaam",
                  "yaarukkum share", "kisi ko na batayein", "na share karein"],
}
SHARE_RE = re.compile(r"(share|send|enter|provide|tell|bhejein|batayein).{0,25}(otp|pin|cvv|password)", re.I)
URL_RE = re.compile(r"(?:https?://|www\.)[^\s]+|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:in|com|xyz|top|club|info|click|work|"
                    r"buzz|online|site|icu|co|net|org|ly|live|shop)(?:/[^\s]*)?", re.I)

NAMES = ["urgency", "money_ask", "credential_ask", "share_request", "reward_bait", "threat", "has_url",
         "safe_warning", "url_long", "url_hyphens", "url_digits", "bad_tld", "shortener", "at_symbol",
         "brand_spoof", "official_domain", "no_https", "many_subdomains", "ip_host", "young_domain", "exclaim"]

REASONS = {
 "urgency": "Creates urgency or a deadline to rush you",
 "money_ask": "Asks you to pay money or a fee",
 "credential_ask": "Asks for sensitive details (KYC, OTP, PIN, Aadhaar)",
 "share_request": "Asks you to share or send a secret code",
 "reward_bait": "Offers an attractive job, prize or reward",
 "threat": "Threatens to block, suspend or cut something",
 "brand_spoof": "Link imitates a well-known brand but is not its official site",
 "bad_tld": "Link ends with a domain type common in scams",
 "shortener": "Link is shortened, hiding the real destination",
 "url_hyphens": "Link has many hyphens, typical of fake lookalike sites",
 "at_symbol": "Link contains '@', a trick to hide the real site",
 "ip_host": "Link uses a raw IP address instead of a site name",
 "many_subdomains": "Link has too many sub-domains",
 "no_https": "Link does not use secure HTTPS",
 "url_long": "Link is unusually long",
}
ADVICE = {
 "job": "Do not pay any fee. Real recruiters never charge to hire. Verify on the company's official careers page.",
 "kyc": "Do not click. Banks never ask for KYC through links. Call the number on your card or visit the branch.",
 "lottery": "You cannot win a contest you never entered. Ignore it and do not pay anything.",
 "otp": "Never share OTP, PIN or CVV with anyone, including 'bank staff'.",
 "parcel": "Do not pay. Check the courier's official app or website with your tracking number.",
 "bill": "Pay only through the official app or website, never through a message link.",
 "general": "Do not click links or pay money. Verify through an official channel first.",
}
CATS = {"job": ["job", "salary", "work from home", "work-from-home", "selected", "recruit", "hiring"],
        "kyc": ["kyc", "aadhaar", "pan card", "account"], "lottery": ["lottery", "won", "prize", "lucky"],
        "otp": ["otp", "pin", "cvv"], "parcel": ["parcel", "courier", "customs", "delivery"],
        "bill": ["electricity", "bill", "disconnected"]}


def _hits(text, kws):
    t, n = text.lower(), 0
    for k in kws:
        if k.isascii():
            n += bool(re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t))
        else:
            n += k in t
    return n


def domain_age_days(host):
    """Optional online WHOIS lookup. Returns None if unavailable."""
    try:
        import whois
        c = whois.whois(host).creation_date
        c = c[0] if isinstance(c, list) else c
        return (datetime.datetime.now() - c).days if c else None
    except Exception:
        return None


def extract_features(text, domain_age=None, lookup=False):
    f = {n: 0.0 for n in NAMES}
    f["urgency"] = min(_hits(text, KW["urgency"]), 3)
    f["money_ask"] = min(_hits(text, KW["money_ask"]), 2)
    f["credential_ask"] = min(_hits(text, KW["credential_ask"]), 2)
    f["reward_bait"] = min(_hits(text, KW["reward_bait"]), 2)
    f["threat"] = min(_hits(text, KW["threat"]), 2)
    f["safe_warning"] = float(_hits(text, KW["safe_warning"]) > 0)
    f["share_request"] = float(bool(SHARE_RE.search(text)) and not f["safe_warning"])
    f["exclaim"] = min(text.count("!"), 3) / 3
    info = {"url": None, "host": None, "domain_age": None}
    m = URL_RE.search(text)
    if m:
        url = m.group(0).rstrip(".,;:)\"'")
        p = urlparse(url if "://" in url else "http://" + url)
        host = (p.hostname or "").lower().removeprefix("www.")
        info.update(url=url, host=host)
        f["has_url"] = 1.0
        f["url_long"] = min(len(url) / 75, 2) / 2
        f["url_hyphens"] = min(host.count("-"), 3) / 3
        f["url_digits"] = sum(c.isdigit() for c in host) / max(len(host), 1)
        f["bad_tld"] = float(host.rsplit(".", 1)[-1] in BAD_TLD)
        f["shortener"] = float(host in SHORTENERS)
        f["at_symbol"] = float("@" in url)
        f["ip_host"] = float(bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host)))
        f["no_https"] = float(not url.lower().startswith("https"))
        f["many_subdomains"] = float(host.count(".") > 2)
        official = any(host == o or host.endswith("." + o) for o in OFFICIAL)
        f["official_domain"] = float(official)
        flat = re.sub(r"[^a-z0-9]", "", host)
        f["brand_spoof"] = float(not official and any(b in flat for b in BRANDS))
        age = domain_age if domain_age else (domain_age_days(host) if lookup and host else None)
        info["domain_age"] = age
        f["young_domain"] = float(age is not None and age < 60)
    return f, info


def category(text):
    best = max(CATS, key=lambda c: _hits(text, CATS[c]))
    return best if _hits(text, CATS[best]) else "general"


def load_model():
    if not os.path.exists(MODEL_PATH):
        import train
        train.main()
    return joblib.load(MODEL_PATH)


def analyze(text, domain_age=None, lookup=False):
    bundle = load_model()
    model = bundle["model"]
    f, info = extract_features(text, domain_age, lookup)
    x = [[f[n] for n in NAMES]]
    score = float(model.predict_proba(x)[0][1]) * 100
    contrib = {n: float(model.coef_[0][i] * f[n]) for i, n in enumerate(NAMES)}
    top = sorted((c, n) for n, c in contrib.items() if c > 0.3)[::-1]
    reasons = []
    for _, n in top:
        if n == "young_domain":
            reasons.append(f"Website domain is very new (registered {info['domain_age']} days ago)")
        elif n in REASONS:
            reasons.append(REASONS[n])
    if f["money_ask"] and f["reward_bait"]:
        reasons.append("Real recruiters and contests never ask you to pay first")
    verdict = "DANGEROUS" if score >= 70 else "SUSPICIOUS" if score >= 35 else "SAFE"
    if verdict == "SAFE":
        reasons = []
    cat = category(text)
    advice = ADVICE[cat] + " Report scams at 1930 or cybercrime.gov.in." if verdict != "SAFE" else \
        "No scam signs found. Still, never share OTPs or pay through links."
    return {"score": round(score, 1), "verdict": verdict, "reasons": reasons, "advice": advice,
            "category": cat, "contrib": contrib, "info": info}
