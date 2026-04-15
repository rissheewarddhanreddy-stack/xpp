import csv
import io

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from .models import BudgetPlan, db
from .services.advisor import build_financial_plan
from .services.predictor import (
    get_model_insights,
    get_prediction_model,
    predict_expenses,
)


main_bp = Blueprint("main", __name__)


def _to_float(value):
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def _serialize_plan(record):
    if not record:
        return None

    return {
        "id": record.id,
        "monthly_income": round(record.monthly_income, 2),
        "total_expenses": round(record.total_expenses, 2),
        "remaining_amount": round(record.remaining_amount, 2),
        "risk_level": record.risk_level,
        "expense_breakdown": record.expense_breakdown(),
        "recommendation_breakdown": record.recommendation_breakdown(),
        "alerts": record.alerts_list(),
        "lifestyle": record.lifestyle.title(),
        "spending_habit": record.spending_habit.title(),
    }


def _build_prediction_and_plan(monthly_income, emi, rent, bills, lifestyle, spending_habit):
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than zero.")

    prediction = predict_expenses(
        monthly_income=monthly_income,
        emi=emi,
        rent=rent,
        bills=bills,
        lifestyle=lifestyle,
        spending_habit=spending_habit,
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
    return prediction, plan


@main_bp.route("/", methods=["GET", "POST"])
def dashboard():
    validation_error = None
    if request.method == "POST":
        monthly_income = _to_float(request.form.get("monthly_income"))
        emi = _to_float(request.form.get("emi"))
        rent = _to_float(request.form.get("rent"))
        bills = _to_float(request.form.get("bills"))
        lifestyle = request.form.get("lifestyle", "working")
        spending_habit = request.form.get("spending_habit", "balanced")

        try:
            prediction, plan = _build_prediction_and_plan(
                monthly_income, emi, rent, bills, lifestyle, spending_habit
            )
        except ValueError as exc:
            validation_error = str(exc)
        else:
            record = BudgetPlan(
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
            db.session.add(record)
            db.session.commit()
            get_prediction_model.cache_clear()
            return redirect(url_for("main.dashboard", plan_id=record.id))

    plan_id = request.args.get("plan_id", type=int)
    active_plan = (
        db.session.get(BudgetPlan, plan_id)
        if plan_id
        else BudgetPlan.query.order_by(BudgetPlan.created_at.desc()).first()
    )
    recent_records = BudgetPlan.query.order_by(BudgetPlan.created_at.asc()).limit(8).all()

    dashboard_data = {
        "active_plan": _serialize_plan(active_plan),
        "history": [
            {
                "label": record.created_at.strftime("%b %d"),
                "income": round(record.monthly_income, 2),
                "expenses": round(record.total_expenses, 2),
                "remaining": round(record.remaining_amount, 2),
            }
            for record in recent_records
        ],
        "model_insights": get_model_insights(),
    }

    return render_template(
        "index.html",
        plan=active_plan,
        dashboard_data=dashboard_data,
        model_name="Random Forest Regressor",
        validation_error=validation_error,
    )


@main_bp.route("/api/predict", methods=["POST"])
def api_predict():
    payload = request.get_json(force=True)
    monthly_income = _to_float(payload.get("monthly_income"))
    emi = _to_float(payload.get("emi"))
    rent = _to_float(payload.get("rent"))
    bills = _to_float(payload.get("bills"))
    lifestyle = payload.get("lifestyle", "working")
    spending_habit = payload.get("spending_habit", "balanced")

    try:
        prediction, plan = _build_prediction_and_plan(
            monthly_income, emi, rent, bills, lifestyle, spending_habit
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"prediction": prediction, "plan": plan})


@main_bp.route("/api/model-info", methods=["GET"])
def api_model_info():
    return jsonify(get_model_insights())


@main_bp.route("/report.csv")
def export_report():
    rows = BudgetPlan.query.order_by(BudgetPlan.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Income",
            "EMI",
            "Rent",
            "Bills",
            "Food",
            "Transport",
            "Entertainment",
            "Miscellaneous",
            "Total Expenses",
            "Remaining",
            "Savings",
            "Investment",
            "Emergency Fund",
            "Risk Level",
            "Created At",
        ]
    )
    for record in rows:
        writer.writerow(
            [
                record.monthly_income,
                record.emi,
                record.rent,
                record.bills,
                record.predicted_food,
                record.predicted_transport,
                record.predicted_entertainment,
                record.predicted_miscellaneous,
                record.total_expenses,
                record.remaining_amount,
                record.recommended_savings,
                record.recommended_investment,
                record.emergency_fund,
                record.risk_level,
                record.created_at.isoformat(),
            ]
        )

    memory_file = io.BytesIO(output.getvalue().encode("utf-8"))
    return send_file(
        memory_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name="smart_expense_report.csv",
    )
