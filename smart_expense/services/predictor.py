from functools import lru_cache

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from ..models import BudgetPlan


LIFESTYLE_MAP = {
    "student": 0,
    "working": 1,
    "family": 2,
}

SPENDING_HABIT_MAP = {
    "frugal": 0,
    "balanced": 1,
    "premium": 2,
}


def _encode_feature(value, mapping, fallback):
    return mapping.get(value, mapping[fallback])


def _build_training_data(seed=42, sample_size=900):
    rng = np.random.default_rng(seed)

    incomes = rng.integers(18000, 150000, sample_size)
    lifestyle = rng.integers(0, 3, sample_size)
    spending_habit = rng.integers(0, 3, sample_size)

    emi_ratio = rng.uniform(0.03, 0.28, sample_size)
    rent_ratio = rng.uniform(0.08, 0.32, sample_size)
    bills_ratio = rng.uniform(0.04, 0.14, sample_size)

    emi = incomes * emi_ratio
    rent = incomes * rent_ratio
    bills = incomes * bills_ratio

    food = (
        incomes * (0.11 + lifestyle * 0.018 + spending_habit * 0.02)
        + rng.normal(0, 1500, sample_size)
    )
    transport = (
        incomes * (0.05 + lifestyle * 0.007 + spending_habit * 0.006)
        + rng.normal(0, 800, sample_size)
    )
    entertainment = (
        incomes * (0.04 + lifestyle * 0.009 + spending_habit * 0.03)
        + rng.normal(0, 1200, sample_size)
    )
    miscellaneous = (
        incomes * (0.03 + lifestyle * 0.01 + spending_habit * 0.012)
        + rng.normal(0, 900, sample_size)
    )

    targets = np.column_stack(
        [
            np.clip(food, 2000, None),
            np.clip(transport, 1000, None),
            np.clip(entertainment, 500, None),
            np.clip(miscellaneous, 700, None),
        ]
    )

    features = np.column_stack(
        [
            incomes,
            emi,
            rent,
            bills,
            lifestyle,
            spending_habit,
            emi / incomes,
            rent / incomes,
            bills / incomes,
        ]
    )

    return features, targets


FEATURE_NAMES = [
    "monthly_income",
    "emi",
    "rent",
    "bills",
    "lifestyle",
    "spending_habit",
    "emi_ratio",
    "rent_ratio",
    "bills_ratio",
]


def _build_training_data_from_history(records):
    features = []
    targets = []

    for record in records:
        encoded_lifestyle = _encode_feature(
            record.lifestyle, LIFESTYLE_MAP, "working"
        )
        encoded_habit = _encode_feature(
            record.spending_habit, SPENDING_HABIT_MAP, "balanced"
        )

        income = record.monthly_income
        features.append(
            [
                income,
                record.emi,
                record.rent,
                record.bills,
                encoded_lifestyle,
                encoded_habit,
                record.emi / max(income, 1),
                record.rent / max(income, 1),
                record.bills / max(income, 1),
            ]
        )
        targets.append(
            [
                record.predicted_food,
                record.predicted_transport,
                record.predicted_entertainment,
                record.predicted_miscellaneous,
            ]
        )

    return np.array(features), np.array(targets)


def _use_historical_training(min_records=8):
    return BudgetPlan.query.count() >= min_records


def _format_feature_importances(importances):
    return [
        {"feature": name, "importance": round(float(value), 4)}
        for name, value in zip(FEATURE_NAMES, importances)
    ]


def _try_build_training_data_from_db(min_records=8):
    records = BudgetPlan.query.all()
    if len(records) < min_records:
        return _build_training_data()

    return _build_training_data_from_history(records)


@lru_cache(maxsize=1)
def get_prediction_model():
    x_train, y_train = _try_build_training_data_from_db()
    model = RandomForestRegressor(
        n_estimators=220,
        max_depth=10,
        random_state=42,
        min_samples_leaf=2,
    )
    model.fit(x_train, y_train)
    return model


def get_model_insights():
    model = get_prediction_model()
    importances = _format_feature_importances(model.feature_importances_)
    sorted_importances = sorted(
        importances, key=lambda item: item["importance"], reverse=True
    )

    return {
        "model_name": "Random Forest Regressor",
        "training_source": "historical user budget data"
        if _use_historical_training()
        else "synthetic benchmark dataset",
        "feature_importances": sorted_importances,
        "top_drivers": [
            item["feature"] for item in sorted_importances[:3]
        ],
    }


def predict_expenses(monthly_income, emi, rent, bills, lifestyle, spending_habit):
    model = get_prediction_model()
    encoded_lifestyle = _encode_feature(lifestyle, LIFESTYLE_MAP, "working")
    encoded_habit = _encode_feature(spending_habit, SPENDING_HABIT_MAP, "balanced")
    features = np.array(
        [
            [
                monthly_income,
                emi,
                rent,
                bills,
                encoded_lifestyle,
                encoded_habit,
                emi / max(monthly_income, 1),
                rent / max(monthly_income, 1),
                bills / max(monthly_income, 1),
            ]
        ]
    )
    prediction = model.predict(features)[0]
    return {
        "food": round(float(prediction[0]), 2),
        "transport": round(float(prediction[1]), 2),
        "entertainment": round(float(prediction[2]), 2),
        "miscellaneous": round(float(prediction[3]), 2),
        "model_name": "Random Forest Regressor",
        "model_insights": get_model_insights(),
    }
