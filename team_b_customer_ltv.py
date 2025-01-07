# team_b_customer_ltv.py
from flytekit import task, workflow
from shared_ml_lib import data_cleaning, feature_engineering, train_test_splitter, evaluate_model
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

@task
def load_customer_data() -> pd.DataFrame:
    """Team B's specific data loading logic"""
    # Simulated customer LTV data
    data = pd.DataFrame({
        'age': [25, 35, 45, 30, 50],
        'spending': [1000, 2000, 3000, 1500, 2500],
        'ltv': [5000, 12000, 20000, 8000, 15000]
    })
    return data

@task
def train_rf_model(
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> RandomForestRegressor:
    """Team B's specific model training"""
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

@workflow
def customer_ltv_prediction():
    """Team B's workflow for customer LTV prediction"""
    # Load data
    raw_data = load_customer_data()
    
    # Use shared tasks
    cleaned_data = data_cleaning(df=raw_data)
    featured_data = feature_engineering(
        df=cleaned_data,
        feature_columns=['age', 'spending']
    )
    
    # Split data using shared splitter
    X_train, X_test, y_train, y_test = train_test_splitter(
        df=featured_data,
        target_column='ltv'
    )
    
    # Train team's specific model
    model = train_rf_model(X_train=X_train, y_train=y_train)
    
    # Use shared evaluation
    predictions = model.predict(X_test)
    metrics = evaluate_model(y_true=y_test, y_pred=pd.Series(predictions))
    
    return metrics