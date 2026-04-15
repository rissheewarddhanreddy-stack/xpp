from smart_expense import create_app
from smart_expense.services.predictor import get_model_insights, get_prediction_model


def test_dashboard_loads():
    get_prediction_model.cache_clear()
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"Smart Expense Prediction" in response.data


def test_budget_submission_creates_prediction():
    get_prediction_model.cache_clear()
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    client = app.test_client()
    response = client.post(
        "/",
        data={
            "monthly_income": "50000",
            "emi": "9000",
            "rent": "12000",
            "bills": "3500",
            "lifestyle": "working",
            "spending_habit": "balanced",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Latest smart budget snapshot" in response.data
    assert b"Risk Level" in response.data


def test_api_model_info_returns_feature_importances():
    get_prediction_model.cache_clear()
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    client = app.test_client()
    response = client.get("/api/model-info")

    assert response.status_code == 200
    data = response.get_json()
    assert data["model_name"] == "Random Forest Regressor"
    assert isinstance(data["feature_importances"], list)
    assert len(data["top_drivers"]) == 3


def test_predictor_model_insights_structure():
    get_prediction_model.cache_clear()
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        insights = get_model_insights()

    assert insights["model_name"] == "Random Forest Regressor"
    assert insights["training_source"] in {
        "historical user budget data",
        "synthetic benchmark dataset",
    }
    assert len(insights["feature_importances"]) == 9
