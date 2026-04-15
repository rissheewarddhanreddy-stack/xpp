def build_financial_plan(monthly_income, fixed_costs, predicted_costs):
    total_expenses = round(sum(fixed_costs.values()) + sum(predicted_costs.values()), 2)
    remaining = round(monthly_income - total_expenses, 2)

    fixed_total = sum(fixed_costs.values())
    alerts = []
    risk_level = "Healthy"

    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than zero.")

    emi_ratio = fixed_costs["emi"] / monthly_income
    rent_ratio = fixed_costs["rent"] / monthly_income
    fixed_ratio = fixed_total / monthly_income

    if emi_ratio > 0.4:
        alerts.append("EMI is above 40% of income. Debt pressure is high.")
        risk_level = "High"
    elif emi_ratio > 0.25:
        alerts.append("EMI is noticeable. Track debt carefully this month.")
        if risk_level != "High":
            risk_level = "Moderate"

    if rent_ratio > 0.35:
        alerts.append("Rent is consuming more than 35% of income.")
        risk_level = "High"

    if fixed_ratio > 0.65:
        alerts.append("Fixed expenses are above 65% of income. Flexibility is limited.")
        risk_level = "High"

    if remaining < 0:
        risk_level = "Critical"
        alerts.append("Projected spending is higher than income. Reduce discretionary categories immediately.")
        return {
            "total_expenses": total_expenses,
            "remaining": remaining,
            "recommended_savings": 0.0,
            "recommended_investment": 0.0,
            "emergency_fund": 0.0,
            "alerts": alerts,
            "risk_level": risk_level,
        }

    if remaining < monthly_income * 0.15:
        alerts.append("Remaining amount is below 15% of income. Try reducing non-essential expenses.")
        if risk_level == "Healthy":
            risk_level = "Moderate"

    if fixed_costs["emi"] == 0:
        alerts.append("No EMI recorded. This improves loan-risk score and savings flexibility.")

    emergency_ratio = 0.2 if risk_level in {"High", "Critical"} else 0.15
    savings_ratio = 0.55 if risk_level == "Healthy" else 0.6

    emergency_fund = round(remaining * emergency_ratio, 2)
    recommended_savings = round(remaining * savings_ratio, 2)
    recommended_investment = round(
        max(remaining - emergency_fund - recommended_savings, 0), 2
    )

    savings_share = recommended_savings / monthly_income
    if savings_share < 0.2:
        alerts.append("Savings recommendation is under 20% of income. A leaner budget would improve long-term stability.")
        if risk_level == "Healthy":
            risk_level = "Moderate"

    return {
        "total_expenses": total_expenses,
        "remaining": remaining,
        "recommended_savings": recommended_savings,
        "recommended_investment": recommended_investment,
        "emergency_fund": emergency_fund,
        "alerts": alerts,
        "risk_level": risk_level,
    }
