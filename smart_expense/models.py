from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class BudgetPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monthly_income = db.Column(db.Float, nullable=False)
    emi = db.Column(db.Float, nullable=False, default=0.0)
    rent = db.Column(db.Float, nullable=False, default=0.0)
    bills = db.Column(db.Float, nullable=False, default=0.0)
    lifestyle = db.Column(db.String(30), nullable=False)
    spending_habit = db.Column(db.String(30), nullable=False)
    predicted_food = db.Column(db.Float, nullable=False)
    predicted_transport = db.Column(db.Float, nullable=False)
    predicted_entertainment = db.Column(db.Float, nullable=False)
    predicted_miscellaneous = db.Column(db.Float, nullable=False)
    total_expenses = db.Column(db.Float, nullable=False)
    remaining_amount = db.Column(db.Float, nullable=False)
    recommended_savings = db.Column(db.Float, nullable=False)
    recommended_investment = db.Column(db.Float, nullable=False)
    emergency_fund = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    alerts = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def expense_breakdown(self):
        return {
            "EMI": round(self.emi, 2),
            "Rent": round(self.rent, 2),
            "Bills": round(self.bills, 2),
            "Food": round(self.predicted_food, 2),
            "Transport": round(self.predicted_transport, 2),
            "Entertainment": round(self.predicted_entertainment, 2),
            "Miscellaneous": round(self.predicted_miscellaneous, 2),
        }

    def recommendation_breakdown(self):
        return {
            "Savings": round(self.recommended_savings, 2),
            "Investment": round(self.recommended_investment, 2),
            "Emergency Fund": round(self.emergency_fund, 2),
        }

    def alerts_list(self):
        return [item for item in self.alerts.split("||") if item]
