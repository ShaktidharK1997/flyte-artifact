# shared_ml_lib.py
from flytekit import task, workflow
import pandas as pd
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict

@task
def data_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """Common data cleaning task that all teams can use"""
    # Remove duplicates
    df = df.drop_duplicates()
    # Handle missing values
    df = df.fillna(df.mean(numeric_only=True))
    return df

@task
def feature_engineering(df: pd.DataFrame, feature_columns: list) -> pd.DataFrame:
    """Shared feature engineering logic"""
    # Create standard numerical features
    for col in feature_columns:
        if df[col].dtype in ['int64', 'float64']:
            # Add standard scaling
            df[f'{col}_normalized'] = (df[col] - df[col].mean()) / df[col].std()
            # Add binning
            df[f'{col}_binned'] = pd.qcut(df[col], q=4, labels=['q1', 'q2', 'q3', 'q4'])
    return df

@task
def train_test_splitter(
    df: pd.DataFrame,
    target_column: str,
    test_size: float = 0.2
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Shared train-test splitting logic"""
    X = df.drop(columns=[target_column])
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    return X_train, X_test, y_train, y_test

@task
def evaluate_model(y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
    """Shared model evaluation metrics"""
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    
    metrics = {
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': mean_squared_error(y_true, y_pred, squared=False),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred)
    }
    return metrics