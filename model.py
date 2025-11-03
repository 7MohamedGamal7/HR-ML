import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# تدريب النموذج
def train():
    data = pd.read_csv("data.csv")
    X = data[["experience", "education_level"]]
    y = data["promotion_eligible"]
    model = RandomForestClassifier()
    model.fit(X, y)
    pickle.dump(model, open("model.pkl", "wb"))

# التنبؤ
def predict(input):
    model = pickle.load(open("model.pkl", "rb"))
    df = pd.DataFrame([input])
    return model.predict(df)[0]
