# team_a_housing_price.py
from flytekit import task, workflow
from shared_ml_lib import data_cleaning, feature_engineering, train_test_splitter, evaluate_model
import pandas as pd
from sklearn.linear_model import LinearRegression

@task
def load_housing_data() -> pd.DataFrame:
    """Team A's specific data loading logic"""
    # Simulated housing data
    data = pd.DataFrame({
        'size': [1500, 2000, 1800, 2200, 1600],
        'bedrooms': [3, 4, 3, 4, 3],
        'price': [300000, 400000, 350000, 420000, 310000]
    })
    return data

@task
def train_linear_model(
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> LinearRegression:
    """Team A's specific model training"""
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

@workflow
def housing_price_prediction():
    """Team A's workflow for house price prediction"""
    # Load data
    raw_data = load_housing_data()
    
    # Use shared tasks
    cleaned_data = data_cleaning(df=raw_data)
    featured_data = feature_engineering(
        df=cleaned_data,
        feature_columns=['size', 'bedrooms']
    )
    
    # Split data using shared splitter
    X_train, X_test, y_train, y_test = train_test_splitter(
        df=featured_data,
        target_column='price'
    )
    
    # Train team's specific model
    model = train_linear_model(X_train=X_train, y_train=y_train)
    
    # Use shared evaluation
    predictions = model.predict(X_test)
    metrics = evaluate_model(y_true=y_test, y_pred=pd.Series(predictions))
    
    return metrics