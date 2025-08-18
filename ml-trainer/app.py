from fastapi import FastAPI, UploadFile, File
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os

app = FastAPI(title="FlowOpsAI Trainer")

@app.get("/")
def root():
    return {"message": "FlowOpsAI Trainer API running"}

@app.post("/train")
async def train_model(file: UploadFile = File(...)):
    # Save uploaded file
    file_location = f"/app/data/{file.filename}"
    os.makedirs("/app/data", exist_ok=True)
    with open(file_location, "wb+") as f:
        f.write(await file.read())

    # Load dataset
    df = pd.read_csv(file_location)
    if "target" not in df.columns:
        return {"error": "CSV must have a 'target' column"}

    X = df.drop("target", axis=1)
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    # Save trained model
    joblib.dump(model, "/app/data/model.joblib")

    return {"accuracy": acc, "model_path": "/app/data/model.joblib"}
