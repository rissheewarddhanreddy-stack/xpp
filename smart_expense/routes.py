from flask import Blueprint, jsonify, render_template, request
from .models import BudgetPlan
from . import db
from .services.advisor import build_financial_plan
from .services.predictor import get_model_insights, predict_expenses

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        try:
            monthly_income = float(request.form.get("monthly_income", 0))
            emi = float(request.form.get("emi", 0))
            rent = float(request.form.get("rent", 0))
            bills = float(request.form.get("bills", 0))
            lifestyle = request.form.get("lifestyle", "working")
            spending_habit = request.form.get("spending_habit", "balanced")

            prediction = predict_expenses(
                monthly_income,
                emi,
                rent,
                bills,
                lifestyle,
                spending_habit,
            )

            plan = build_financial_plan(
                monthly_income=monthly_income,
                fixed_costs={"emi": emi, "rent": rent, "bills": bills},
                predicted_costs={
                    "food": prediction["food"],
                    "transport": prediction["transport"],
                    "entertainment": prediction["entertainment"],
                    "miscellaneous": prediction["miscellaneous"],
                },
            )

            result = {
                "monthly_income": monthly_income,
                "emi": emi,
                "rent": rent,
                "bills": bills,
                "lifestyle": lifestyle,
                "spending_habit": spending_habit,
                "prediction": prediction,
                "plan": plan,
            }

            new_entry = BudgetPlan(
                monthly_income=monthly_income,
                emi=emi,
                rent=rent,
                bills=bills,
                lifestyle=lifestyle,
                spending_habit=spending_habit,
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

            db.session.add(new_entry)
            db.session.commit()

        except Exception:
            db.session.rollback()
            result = {"error": "Invalid input or internal error."}

    return render_template("index.html", result=result)

@main_bp.route("/api/model-info", methods=["GET"])
def model_info():
    return jsonify(get_model_insights())
