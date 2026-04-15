from smart_expense.models import BudgetPlan, db
from smart_expense.services.advisor import build_financial_plan
from smart_expense.services.predictor import predict_expenses


DEMO_SCENARIOS = [
    {
        "monthly_income": 48000,
        "emi": 7000,
        "rent": 11000,
        "bills": 3200,
        "lifestyle": "working",
        "spending_habit": "balanced",
    },
    {
        "monthly_income": 65000,
        "emi": 9000,
        "rent": 15000,
        "bills": 4300,
        "lifestyle": "family",
        "spending_habit": "balanced",
    },
    {
        "monthly_income": 32000,
        "emi": 0,
        "rent": 6500,
        "bills": 2200,
        "lifestyle": "student",
        "spending_habit": "frugal",
    },
]


def ensure_demo_data():
    if BudgetPlan.query.count() > 0:
        return

    for scenario in DEMO_SCENARIOS:
        prediction = predict_expenses(
            scenario["monthly_income"],
            scenario["emi"],
            scenario["rent"],
            scenario["bills"],
            scenario["lifestyle"],
            scenario["spending_habit"],
        )
        plan = build_financial_plan(
            monthly_income=scenario["monthly_income"],
            fixed_costs={
                "emi": scenario["emi"],
                "rent": scenario["rent"],
                "bills": scenario["bills"],
            },
            predicted_costs={
                "food": prediction["food"],
                "transport": prediction["transport"],
                "entertainment": prediction["entertainment"],
                "miscellaneous": prediction["miscellaneous"],
            },
        )

        record = BudgetPlan(
            monthly_income=scenario["monthly_income"],
            emi=scenario["emi"],
            rent=scenario["rent"],
            bills=scenario["bills"],
            lifestyle=scenario["lifestyle"],
            spending_habit=scenario["spending_habit"],
            predicted_food=prediction["food"],
            predicted_transport=prediction["transport"],
            predicted_entertainment=prediction["entertainment"],
            predicted_miscellaneous=prediction["miscellaneous"],
            total_expenses=plan["total_expenses"],
            remaining_amount=plan["remaining"],
            recommended_savings=plan["recommended_savings"],
            recommended_investment=plan["recommended_investment"],
            emergency_fund=plan["emergency_fund"],
            risk_level=plan["risk_level"],
            alerts="||".join(plan["alerts"]),
        )
        db.session.add(record)

    db.session.commit()
