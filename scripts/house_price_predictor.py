import typing
from pathlib import Path
from typing import Tuple

import flytekit
import joblib
import numpy as np
import pandas as pd
from flytekit import Resources, task, workflow
from flytekit.types.file import JoblibSerializedFile
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

# Constants
NUM_HOUSES_PER_LOCATION = 1000
COLUMNS = [
    "PRICE",
    "YEAR_BUILT",
    "SQUARE_FEET",
    "NUM_BEDROOMS",
    "NUM_BATHROOMS",
    "LOT_ACRES",
    "GARAGE_SPACES",
]
MAX_YEAR = 2021
SPLIT_RATIOS = [0.6, 0.3, 0.1]

def gen_price(house) -> int:
    _base_price = int(house["SQUARE_FEET"] * 150)
    _price = int(
        _base_price
        + (10000 * house["NUM_BEDROOMS"])
        + (15000 * house["NUM_BATHROOMS"])
        + (15000 * house["LOT_ACRES"])
        + (15000 * house["GARAGE_SPACES"])
        - (5000 * (MAX_YEAR - house["YEAR_BUILT"]))
    )
    return _price

def gen_houses(num_houses) -> pd.DataFrame:
    _house_list = []
    for _ in range(num_houses):
        _house = {
            "SQUARE_FEET": int(np.random.normal(3000, 750)),
            "NUM_BEDROOMS": np.random.randint(2, 7),
            "NUM_BATHROOMS": np.random.randint(2, 7) / 2,
            "LOT_ACRES": round(np.random.normal(1.0, 0.25), 2),
            "GARAGE_SPACES": np.random.randint(0, 4),
            "YEAR_BUILT": min(MAX_YEAR, int(np.random.normal(1995, 10))),
        }
        _price = gen_price(_house)
        _house_list.append(
            [
                _price,
                _house["YEAR_BUILT"],
                _house["SQUARE_FEET"],
                _house["NUM_BEDROOMS"],
                _house["NUM_BATHROOMS"],
                _house["LOT_ACRES"],
                _house["GARAGE_SPACES"],
            ]
        )
    _df = pd.DataFrame(
        _house_list,
        columns=COLUMNS,
    )
    return _df

def split_data(
    df: pd.DataFrame, seed: int, split: typing.List[float]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seed = seed
    val_size = split[1]
    test_size = split[2]

    num_samples = df.shape[0]
    x1 = df.values[:num_samples, 1:]
    y1 = df.values[:num_samples, :1]

    x_train, x_test, y_train, y_test = train_test_split(x1, y1, test_size=test_size, random_state=seed)
    x_train, x_val, y_train, y_val = train_test_split(
        x_train,
        y_train,
        test_size=(val_size / (1 - test_size)),
        random_state=seed,
    )

    _train = np.concatenate([y_train, x_train], axis=1)
    _val = np.concatenate([y_val, x_val], axis=1)
    _test = np.concatenate([y_test, x_test], axis=1)

    return (
        pd.DataFrame(_train, columns=COLUMNS),
        pd.DataFrame(_val, columns=COLUMNS),
        pd.DataFrame(_test, columns=COLUMNS),
    )

# Define NamedTuple for dataset
dataset = typing.NamedTuple(
    "GenerateSplitDataOutputs",
    train_data=pd.DataFrame,
    val_data=pd.DataFrame,
    test_data=pd.DataFrame,
)

@task(cache=True, cache_version="0.1", limits=Resources(mem="600Mi"))
def generate_and_split_data(number_of_houses: int, seed: int) -> dataset:
    _houses = gen_houses(number_of_houses)
    return split_data(_houses, seed, split=SPLIT_RATIOS)

@task(cache_version="1.0", cache=True, limits=Resources(mem="600Mi"))
def fit(loc: str, train: pd.DataFrame, val: pd.DataFrame) -> JoblibSerializedFile:
    x = train[train.columns[1:]]
    y = train[train.columns[0]]
    eval_x = val[val.columns[1:]]
    eval_y = val[val.columns[0]]

    m = XGBRegressor()
    m.fit(x, y, eval_set=[(eval_x, eval_y)])

    working_dir = flytekit.current_context().working_directory
    fname = str(Path(working_dir) / f"model-{loc}.joblib.dat")
    joblib.dump(m, fname)

    return JoblibSerializedFile(path=fname)

@task(cache_version="1.0", cache=True, limits=Resources(mem="600Mi"))
def predict(
    test: pd.DataFrame,
    model_ser: JoblibSerializedFile,
) -> typing.List[float]:
    model = joblib.load(model_ser)
    x_df = test[test.columns[1:]]
    y_pred = model.predict(x_df).tolist()
    return y_pred

@workflow
def house_price_predictor_trainer(seed: int = 7, number_of_houses: int = NUM_HOUSES_PER_LOCATION) -> typing.List[float]:
    split_data_vals = generate_and_split_data(number_of_houses=number_of_houses, seed=seed)
    model = fit(loc="NewYork_NY", train=split_data_vals.train_data, val=split_data_vals.val_data)
    predictions = predict(model_ser=model, test=split_data_vals.test_data)
    return predictions

if __name__ == "__main__":
    print(house_price_predictor_trainer())
