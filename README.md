# PhishGuard-AI
PhishGuard AI is an explainable, multi-lingual cybersecurity tool that detects phishing URLs and malicious scams across English, Hindi, and Tamil text using a hybrid machine learning pipeline.
# 🛡️ PhishGuard AI

**An explainable scam detector for messages and links, built for Indian users.**

PhishGuard AI reads a suspicious message (SMS, WhatsApp, email), checks the text and the link inside it, and returns a **risk score**, the **reasons behind the verdict**, and **what to do next**. It understands English, Tanglish, Hindi (romanised and Devanagari) and Tamil script.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Streamlit](https://img.shields.io/badge/UI-Streamlit-red) ![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-orange) ![Status](https://img.shields.io/badge/Status-Prototype-yellow)

---

## Table of Contents

1. [Problem](#problem)
2. [Objectives](#objectives)
3. [Features](#features)
4. [Demo](#demo)
5. [How It Works](#how-it-works)
6. [Tech Stack](#tech-stack)
7. [Project Structure](#project-structure)
8. [Installation](#installation)
9. [Usage](#usage)
10. [Training on Your Own Data](#training-on-your-own-data)
11. [Evaluation and Limitations](#evaluation-and-limitations)
12. [Roadmap](#roadmap)
13. [Responsible Use](#responsible-use)
14. [Team](#team)

---

## Problem

Attackers now use AI to write flawless phishing messages in any language, so the old signs of a scam (spelling mistakes, clumsy grammar) no longer work. Fake job offers, "KYC expired" alerts, lottery wins and parcel-fee messages reach students, parents and small businesses every day. Most existing filters only label a message "spam" without a reason, so people ignore the warning.

## Objectives

1. Detect scam messages written in English, Tanglish, Hindi and Tamil.
2. Analyse the link inside a message for signs of a fake website.
3. Explain every verdict with a risk score and plain-language reasons.
4. Tell the user what to do next (do not click, do not pay, report to 1930).

## Features

- **Multilingual message analysis** for English, Tanglish, Hindi (Roman and Devanagari) and Tamil script
- **Link analysis**: brand spoofing, hyphen-heavy domains, scam-style domain endings, URL shorteners, missing HTTPS, raw IP hosts, `@` tricks
- **Optional domain-age check** (online WHOIS lookup, or a manual override for demos)
- **Explainable output**: risk percentage, ranked reasons, and a bar chart showing how each clue moved the score
- **Scam-type advice**: tailored guidance for job, KYC, lottery, OTP, parcel and bill scams, with the cyber-crime helpline (1930)
- **Safe-message handling**: genuine OTP notices, bank debit alerts and order updates are not flagged
- **Retrainable**: plug in your own labelled data with a single command

## Demo

| Message | Verdict |
|---|---|
| "Congratulations! You are selected for a Work-From-Home job... Pay Rs 2,500 registration fee... `global-careers-hire.in/apply`" | 🔴 DANGEROUS |
| "Dear customer, your SBI KYC has expired. Update within 2 hours or your account will be blocked: `sbi-kyc-help.xyz/verify`" | 🔴 DANGEROUS |
| "Sir, ungal HDFC KYC expire aagiduchu... `hdfc-update.top/login`" | 🔴 DANGEROUS |
| "Your OTP for SBI login is 482910. Do not share it with anyone." | 🟢 SAFE |
| "Your Amazon order #4821 has been shipped. Track it here: `https://www.amazon.in/orders/482`" | 🟢 SAFE |

Example output for the first message:

```
🔴 DANGEROUS
Why:
 - Asks you to pay money or a fee
 - Offers an attractive job, prize or reward
 - Real recruiters and contests never ask you to pay first
Advice: Do not pay any fee. Real recruiters never charge to hire.
        Report scams at 1930 or cybercrime.gov.in.
```

## How It Works

```
 Message / link
       │
       ▼
┌───────────────────────────┐
│  Feature extraction       │  urgency, money ask, OTP/KYC ask, reward bait,
│  (engine.py)              │  threats + link clues (spoofing, TLD, HTTPS ...)
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│  Logistic Regression      │  clues → risk score (0 to 100)
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│  Explanation layer        │  per-clue contribution → plain-language reasons
└─────────────┬─────────────┘
              ▼
   Verdict + score + reasons + advice
```

**Verdict thresholds:** below 35 is SAFE, 35 to 70 is SUSPICIOUS, 70 and above is DANGEROUS.

**Why a linear model?** Each clue's contribution is simply its weight multiplied by its value, so the explanation is exact and transparent (the same idea as SHAP for linear models). Security teams can see and trust why a message was flagged.

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.9+ |
| ML | scikit-learn (Logistic Regression), NumPy, pandas |
| UI | Streamlit |
| Model storage | joblib |
| Optional | python-whois (domain age) |

## Project Structure

```
phishguard/
├── app.py            # Streamlit web interface
├── engine.py         # Feature extraction, scoring, reasons, advice
├── train.py          # Model training and evaluation
├── data_gen.py       # Synthetic training data generator
├── tests.py          # Sanity tests on sample messages
├── requirements.txt  # Python dependencies
├── model.joblib      # Trained model (created by train.py)
├── metrics.json      # Evaluation results (created by train.py)
└── README.md
```

## Installation

```bash
git clone <https://nishajas291-crypto.github.io/PhishGuard-AI/>
cd phishguard
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Optional, for live domain-age lookup:

```bash
pip install python-whois
```

## Usage

```bash
python train.py          # train the model and write metrics.json
python tests.py          # run sanity tests (expects 7/7 passed)
streamlit run app.py     # launch the web app
```

In the web app:

1. Pick an example from the dropdown or paste your own message.
2. Click **Check message**.
3. Read the verdict, the reasons and the advice. Open **How the score was calculated** for the contribution chart.
4. In the sidebar, set **Domain age in days** to demonstrate the new-domain signal, or tick the online lookup box for real domains.

## Training on Your Own Data

Create a CSV with two columns:

| text | label |
|---|---|
| "You have won a lottery, pay Rs 500 fee..." | 1 |
| "Hey, meeting at 5 today?" | 0 |

`label` is `1` for scam and `0` for genuine. Then run:

```bash
python train.py --csv yourdata.csv
```

Suggested sources: public SMS-spam datasets, PhishTank (phishing URLs), and scam and genuine messages collected in Tamil and Hindi. The new metrics are saved to `metrics.json` and shown in the app sidebar.

## Evaluation and Limitations

> **Important:** the bundled model is trained on **synthetic, template-generated data** so the project runs out of the box. Its metrics (near 100%) are **not** real-world accuracy. Retrain on real data and quote the numbers from `metrics.json`.

Metrics reported by `train.py`: precision, recall, F1 and false-positive rate.

Known limitations:

- Keyword and feature rules can be evaded by attackers who rephrase messages. Treat the output as a recommendation, not a final decision.
- Tamil and Hindi coverage depends on the keyword lists and the training data. More real samples will improve it.
- Domain age needs an online WHOIS lookup and is skipped when unavailable.
- Text and links only. Voice and video are not analysed in this version.

## Roadmap

- [ ] Train on large real-world datasets and report verified metrics
- [ ] Upgrade the text model to a multilingual transformer (for example DistilBERT)
- [ ] Voice deepfake detection (spectrogram + CNN)
- [ ] LLM-written explanations on top of the reason list
- [ ] WhatsApp bot and browser extension
- [ ] More Indian languages

## Responsible Use

PhishGuard AI is a defensive tool. Use it only on messages you are authorised to analyse. It does not generate phishing content and must not be used to build or test attacks on real systems. Results are advisory: when in doubt, verify through an official channel and report scams at **1930** or **cybercrime.gov.in**.

## Team

**Team:** ZYNEX

**Members:** Jasminenisha H, Barjana M, Asin Aswanthitha S

**College:** S.Veerasamy Chettiar College of Engineering and Technology

---

*Built as a hackathon prototype exploring AI-powered defence against AI-powered scams.*
