""" Uses machine learning to predict potential churn for non-churned customers in nps_data.csv based on NPS Score
and Customer Response, identifying at-risk customers for proactive intervention.
"""

# Purpose:

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.pipeline import make_pipeline
from scipy.sparse import hstack
import warnings
warnings.filterwarnings("ignore")  # Suppress warnings for cleaner output

# ====== Function to preprocess data and extract features
def preprocess_data(df):
    """
    Preprocess nps_data.csv and extract features for churn prediction.

    Args:
        df (pd.DataFrame): DataFrame with 'Customer Number', 'NPS Score', 'Customer Response', 'Churned'

    Returns:
        tuple: Feature matrix (X), target vector (y), feature names, and filtered DataFrame
    """
    required_columns = ['Customer Number', 'NPS Score', 'Customer Response', 'Churned']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain {required_columns}")

    # Select relevant columns
    df = df[required_columns].copy()

    # Convert Customer Response to TF-IDF features
    tfidf = TfidfVectorizer(max_features=100, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['Customer Response'])
    tfidf_features = tfidf.get_feature_names_out()

    # Combine NPS Score and TF-IDF features
    nps_feature = df[['NPS Score']].values
    X = hstack([tfidf_matrix, nps_feature])
    feature_names = list(tfidf_features) + ['NPS Score']

    # Target variable
    y = df['Churned']

    return X, y, feature_names, df

# ====== Function to train and evaluate model
def train_churn_model(X, y):
    """
    Train a Random Forest Classifier to predict churn.

    Args:
        X: Feature matrix
        y: Target vector (Churned)

    Returns:
        tuple: Trained model and feature importances
    """
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Train Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    print("Model Performance on Test Set:")
    print(classification_report(y_test, y_pred))
    print(f"ROC AUC Score: {roc_auc_score(y_test, y_proba):.2f}")

    # Feature importances
    importances = model.feature_importances_
    return model, importances

# ====== Function to predict churn for non-churned customers
def predict_at_risk_customers(model, X, df):
    """
    Predict churn probabilities for non-churned customers and identify high-risk ones.

    Args:
        model: Trained Random Forest Classifier
        X: Feature matrix
        df (pd.DataFrame): Preprocessed DataFrame with customer data

    Returns:
        pd.DataFrame: DataFrame with churn probabilities and high-risk customer summary
    """
    # Predict churn probabilities for all customers
    churn_proba = model.predict_proba(X)[:, 1]
    df['Churn Probability'] = churn_proba

    # Filter non-churned customers
    non_churned = df[df['Churned'] == 0].copy()

    # Identify high-risk customers (probability > 0.5)
    high_risk = non_churned[non_churned['Churn Probability'] > 0.5][
        ['Customer Number', 'NPS Score', 'Customer Response', 'Churn Probability']
    ]

    # Print summary of high-risk customers
    print("\nHigh-Risk Non-Churned Customers (Churn Probability > 50%):")
    if not high_risk.empty:
        print(high_risk.to_string(index=False))
    else:
        print("No non-churned customers with churn probability > 50%.")

    return df

# ====== Main execution
try:
    # Load the data
    df = pd.read_csv('nps_data.csv')

    # Preprocess data
    X, y, feature_names, processed_df = preprocess_data(df)

    # Train the model
    model, importances = train_churn_model(X, y)

    # Predict churn for non-churned customers
    result_df = predict_at_risk_customers(model, X, processed_df)

    # Save results with churn probabilities
    result_df.to_csv('nps_data_with_churn_predictions.csv', index=False)
    print("\nUpdated data with churn predictions saved to 'nps_data_with_churn_predictions.csv'")

    # Print top 5 features contributing to churn
    feature_importance = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
    print("\nTop 5 Features Contributing to Churn Prediction:")
    print(feature_importance.sort_values(by='Importance', ascending=False).head(5).to_string(index=False))

except FileNotFoundError:
    print("Error: 'nps_data.csv' not found.")
except Exception as e:
    print(f"Error during processing: {e}")