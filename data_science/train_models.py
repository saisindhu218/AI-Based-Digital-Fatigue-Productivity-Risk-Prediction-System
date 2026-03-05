#!/usr/bin/env python3
"""
Train ML models using static dataset
RUN THIS ONCE to generate .pkl files
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
import joblib
import os
import sys

# ⭐ FIX: Force UTF-8 output to avoid Windows emoji crash
sys.stdout.reconfigure(encoding="utf-8", errors="ignore")


def train_fatigue_classifier():
    """Train fatigue classification model"""
    print("Training Fatigue Classification Model...")

    df = pd.read_csv('datasets/digital_usage_data.csv')
    print(f"Dataset shape: {df.shape}")

    X = df[['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio']]
    y = df['fatigue_level']

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    os.makedirs('../backend/ml_models', exist_ok=True)
    joblib.dump(model, '../backend/ml_models/fatigue_classifier.pkl')
    joblib.dump(le, '../backend/ml_models/fatigue_label_encoder.pkl')

    print("Fatigue classification models saved")

    return model, le, accuracy


def train_productivity_regressor():
    """Train productivity loss regression model"""
    print("\nTraining Productivity Loss Regression Model...")

    df = pd.read_csv('datasets/digital_usage_data.csv')

    X = df[['screen_time', 'avg_session', 'breaks',
            'night_ratio', 'productive_ratio', 'fatigue_score']]
    y = df['productivity_loss']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MAE: {mae:.4f}")
    print(f"R2 Score: {r2:.4f}")

    joblib.dump(model, '../backend/ml_models/productivity_loss_model.pkl')
    print("Productivity loss model saved")

    return model, mae, r2


def extract_feature_importance(classifier, regressor, le):
    """Extract and print feature importance"""
    print("\nFeature Importance Analysis:")

    class_features = ['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio']
    class_importance = classifier.feature_importances_

    print("Fatigue Classification Feature Importance:")
    for feature, importance in zip(class_features, class_importance):
        print(f"  {feature}: {importance:.4f}")

    reg_features = ['screen_time', 'avg_session', 'breaks',
                    'night_ratio', 'productive_ratio', 'fatigue_score']
    reg_importance = regressor.feature_importances_

    print("\nProductivity Loss Regression Feature Importance:")
    for feature, importance in zip(reg_features, reg_importance):
        print(f"  {feature}: {importance:.4f}")


def main():
    print("=" * 60)
    print("ML Model Training for Digital Fatigue Prediction")
    print("=" * 60)

    os.makedirs('../backend/ml_models', exist_ok=True)

    classifier, le, acc = train_fatigue_classifier()
    regressor, mae, r2 = train_productivity_regressor()

    extract_feature_importance(classifier, regressor, le)

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print(f"Fatigue Classifier Accuracy: {acc:.4f}")
    print(f"Productivity Regressor R2: {r2:.4f}")
    print("Models saved to: backend/ml_models/")
    print("=" * 60)

    with open('training_report.txt', 'w') as f:
        f.write("ML Model Training Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Fatigue Classifier Accuracy: {acc:.4f}\n")
        f.write(f"Productivity Regressor R2: {r2:.4f}\n")
        f.write(f"Productivity Regressor MAE: {mae:.4f}\n")

    print("Training report saved: training_report.txt")


if __name__ == "__main__":
    main()
