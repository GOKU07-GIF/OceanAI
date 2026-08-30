import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load dataset
data = pd.read_csv("app/ai/dataset/ocean_data.csv")

# Features
X = data[["temperature", "ph", "salinity", "oxygen"]]

# Target
y = data["quality"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Accuracy
accuracy = model.score(X_test, y_test)

print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save model
joblib.dump(
    model,
    "app/ai/models/ocean_model.pkl"
)

print("Model saved successfully.")