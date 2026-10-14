"""Train: `python train.py` (synthetic data) or `python train.py --csv data.csv` (columns: text,label with 1=scam)."""
import sys, json, joblib, random
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import engine, data_gen

def main(csv=None):
    if csv:
        import pandas as pd
        df = pd.read_csv(csv); rng = random.Random(1)
        rows = [(t, int(l), rng.random() < (.7 if l else .02)) for t, l in zip(df["text"], df["label"])]
        source = csv
    else:
        rows, source = data_gen.make(), "synthetic"
    X, y = [], []
    for text, label, young in rows:
        f, _ = engine.extract_features(text, domain_age=10 if young else None)
        if not f["has_url"]: f["young_domain"] = 0.0
        X.append([f[n] for n in engine.NAMES]); y.append(label)
    X, y = np.array(X), np.array(y)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.25, random_state=3, stratify=y)
    m = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000).fit(Xtr, ytr)
    p = m.predict(Xte); tn, fp, fn, tp = confusion_matrix(yte, p).ravel()
    metrics = {"data": source, "precision": round(precision_score(yte, p), 3), "recall": round(recall_score(yte, p), 3),
               "f1": round(f1_score(yte, p), 3), "false_positive_rate": round(float(fp / (fp + tn)), 3), "test_size": int(len(yte))}
    joblib.dump({"model": m}, engine.MODEL_PATH)
    json.dump(metrics, open(engine.MODEL_PATH.replace("model.joblib", "metrics.json"), "w"), indent=1)
    print(metrics)

if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--csv") + 1] if "--csv" in sys.argv else None)
