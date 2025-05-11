import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
import os

# Suppress specific warnings (optional but can be helpful)
warnings.filterwarnings("ignore", category=FutureWarning)

# 1. Load the cleaned and aggregated data
print("Current working directory:", os.getcwd())
df = pd.read_csv('WWE_CHAMPION_PREDICTOR/predictor/data/cleaned_wrestling_data.csv')

# Display column names for verification
print("Column Names in Data:", df.columns.tolist())

# 2. Validate that 'belt' column exists
if 'belt' not in df.columns:
    raise ValueError("The 'belt' column is missing from cleaned_wrestling_data.csv. Please verify the data structure.")

# 3. Create binary target: did this wrestler ever hold the WWE Championship?
df['target_champion'] = df['belt'].str.lower().eq('wwe championship').astype(int)

# 4. Select features for prediction
features = [
    'total_reigns',
    'total_days_as_champion',
    'average_reign_duration',
    'longest_single_reign',
    'shortest_single_reign',
    'days_since_last_reign',
    'title_diversity',
    'avg_gap_between_reigns',
    'career_span_days',
    'avg_reigns_per_title'
]

# 5. Validate that all features exist
missing_features = [col for col in features if col not in df.columns]
if missing_features:
    raise ValueError(f"Missing required feature columns: {missing_features}")

# 6. Prepare features and target
X = df[features].fillna(df[features].mean())  # Use mean imputation for missing numerical data
y = df['target_champion']

# 7. Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 8. Train logistic regression model
model = LogisticRegression(max_iter=1000, random_state=42, solver='liblinear', n_jobs=-1)
model.fit(X_train, y_train)

# 9. Evaluate model
y_pred = model.predict(X_test)
print("Model Evaluation:")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# 10. Save model to disk
joblib.dump(model, 'champion_predictor.pkl')
print("Model saved as 'champion_predictor.pkl'")
