from datetime import datetime
from . import db

class BudgetPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monthly_income = db.Column(db.Float, nullable=False)
    emi = db.Column(db.Float, nullable=False, default=0.0)
    rent = db.Column(db.Float, nullable=False, default=0.0)
    bills = db.Column(db.Float, nullable=False, default=0.0)
    lifestyle = db.Column(db.String(32), nullable=False, default='working')
    spending_habit = db.Column(db.String(32), nullable=False, default='balanced')
    predicted_food = db.Column(db.Float, nullable=False, default=0.0)
    predicted_transport = db.Column(db.Float, nullable=False, default=0.0)
    predicted_entertainment = db.Column(db.Float, nullable=False, default=0.0)
    predicted_miscellaneous = db.Column(db.Float, nullable=False, default=0.0)
    total_expenses = db.Column(db.Float, nullable=False, default=0.0)
    remaining_amount = db.Column(db.Float, nullable=False, default=0.0)
    recommended_savings = db.Column(db.Float, nullable=False, default=0.0)
    recommended_investment = db.Column(db.Float, nullable=False, default=0.0)
    emergency_fund = db.Column(db.Float, nullable=False, default=0.0)
    risk_level = db.Column(db.String(32), nullable=False, default='Healthy')
    alerts = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
