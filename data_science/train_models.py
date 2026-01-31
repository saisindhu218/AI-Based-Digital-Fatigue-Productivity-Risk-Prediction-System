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

def train_fatigue_classifier():
    """Train fatigue classification model"""
    print("Training Fatigue Classification Model...")
    
    # Load dataset
    df = pd.read_csv('datasets/digital_usage_data.csv')
    print(f"Dataset shape: {df.shape}")
    
    # Features based on friend's notebook
    X = df[['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio']]
    y = df['fatigue_level']
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Save models
    os.makedirs('../backend/ml_models', exist_ok=True)
    joblib.dump(model, '../backend/ml_models/fatigue_classifier.pkl')
    joblib.dump(le, '../backend/ml_models/fatigue_label_encoder.pkl')
    print("✅ Fatigue classification models saved")
    
    return model, le, accuracy

def train_productivity_regressor():
    """Train productivity loss regression model"""
    print("\nTraining Productivity Loss Regression Model...")
    
    # Load dataset
    df = pd.read_csv('datasets/digital_usage_data.csv')
    
    # Features based on friend's notebook
    X = df[['screen_time', 'avg_session', 'breaks', 
            'night_ratio', 'productive_ratio', 'fatigue_score']]
    y = df['productivity_loss']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"MAE: {mae:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    # Save model
    joblib.dump(model, '../backend/ml_models/productivity_loss_model.pkl')
    print("✅ Productivity loss model saved")
    
    return model, mae, r2

def extract_feature_importance(classifier, regressor, le):
    """Extract and print feature importance"""
    print("\nFeature Importance Analysis:")
    
    # Classification features
    class_features = ['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio']
    class_importance = classifier.feature_importances_
    
    print("Fatigue Classification Feature Importance:")
    for feature, importance in zip(class_features, class_importance):
        print(f"  {feature}: {importance:.4f}")
    
    # Regression features
    reg_features = ['screen_time', 'avg_session', 'breaks', 
                    'night_ratio', 'productive_ratio', 'fatigue_score']
    reg_importance = regressor.feature_importances_
    
    print("\nProductivity Loss Regression Feature Importance:")
    for feature, importance in zip(reg_features, reg_importance):
        print(f"  {feature}: {importance:.4f}")

def main():
    """Main training function"""
    print("=" * 60)
    print("ML Model Training for Digital Fatigue Prediction")
    print("=" * 60)
    
    # Create output directory
    os.makedirs('../backend/ml_models', exist_ok=True)
    
    # Train models
    classifier, le, acc = train_fatigue_classifier()
    regressor, mae, r2 = train_productivity_regressor()
    
    # Feature importance
    extract_feature_importance(classifier, regressor, le)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print(f"✓ Fatigue Classifier Accuracy: {acc:.4f}")
    print(f"✓ Productivity Regressor R²: {r2:.4f}")
    print(f"✓ Models saved to: backend/ml_models/")
    print("=" * 60)
    
    # Save training report
    with open('training_report.txt', 'w') as f:
        f.write("ML Model Training Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Fatigue Classifier Accuracy: {acc:.4f}\n")
        f.write(f"Productivity Regressor R²: {r2:.4f}\n")
        f.write(f"Productivity Regressor MAE: {mae:.4f}\n")
    
    print("✅ Training report saved: training_report.txt")

if __name__ == "__main__":
    main()