# PhishGuard AI

Explainable scam detector for messages and links (English, Tanglish, Hindi, Tamil/Hindi script).
Gives a risk score, the reasons, and what to do next.

## Run
```
pip install -r requirements.txt
python train.py          # trains and saves model.joblib + metrics.json
python tests.py          # quick sanity tests
streamlit run app.py     # opens the web UI
```

## How it works
1. `engine.py` pulls clues from the text (urgency, money ask, OTP/KYC ask, reward bait, threats) and the link
   (brand spoofing, hyphens, scam-style endings, shorteners, no HTTPS, optional domain age).
2. A Logistic Regression model turns the clues into a 0-100 risk score.
3. Each clue's contribution is shown (exact for a linear model, same idea as SHAP), and turned into plain-language reasons.
4. A rule picks scam type (job, KYC, lottery, OTP, parcel, bill) and gives matching advice.

## IMPORTANT: be honest in your presentation
- The included model is trained on **synthetic template data**, so its metrics are optimistic (near 100%).
  Do NOT quote them as real-world accuracy.
- To get real numbers: download real data (e.g. Kaggle SMS spam, PhishTank URLs, your own Tamil/Hindi scam samples),
  make a CSV with columns `text,label` (1 = scam), then run `python train.py --csv yourdata.csv`.
  Quote the new metrics from `metrics.json`.
- Domain age: install `python-whois` and tick the sidebar box, or use the demo override to type an age.

## Not included (future scope)
- Voice deepfake layer (idea: librosa spectrogram + CNN, ASVspoof dataset)
- LLM-written explanations (hook an LLM API into `analyze()` using the `reasons` list)
- WhatsApp bot / browser extension
