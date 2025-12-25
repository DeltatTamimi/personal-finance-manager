import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_monthly_income_totals


class ForecastService:

    @staticmethod
    def get_income_forecast(months_ahead=3):
        monthly_data = get_monthly_income_totals()

        if len(monthly_data) < 2:
            return {
                "error": "Not enough data for prediction. Need at least 2 months of income data.",
                "history": monthly_data,
                "forecast": []
            }

        # Prepare data for linear regression
        # X = month index (0, 1, 2, ...)
        # y = income amount
        X = np.array(range(len(monthly_data))).reshape(-1, 1)
        y = np.array([m["total"] for m in monthly_data])

        # Train the model
        model = LinearRegression()
        model.fit(X, y)

        # Get the last month in the data
        last_month_str = monthly_data[-1]["month"]
        last_month_date = datetime.strptime(last_month_str + "-01", "%Y-%m-%d")

        # Generate predictions
        forecast = []
        for i in range(1, months_ahead + 1):
            future_index = len(monthly_data) - 1 + i
            predicted_value = model.predict([[future_index]])[0]

            future_date = last_month_date + relativedelta(months=i)
            future_month = future_date.strftime("%Y-%m")

            forecast.append({
                "month": future_month,
                "predicted_income": round(max(0, predicted_value), 2)  # No negative predictions
            })

        # Model info
        slope = round(model.coef_[0], 2)
        intercept = round(model.intercept_, 2)

        # Calculate R-squared score
        y_pred = model.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = round(1 - (ss_res / ss_tot), 4) if ss_tot != 0 else 0

        return {
            "history": monthly_data,
            "forecast": forecast,
            "model_info": {
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_squared,
                "interpretation": f"Income changes by ${slope} per month on average"
            }
        }

    @staticmethod
    def get_expense_trend(months_ahead=3):
        from database import get_all_transactions

        transactions = get_all_transactions()

        # Aggregate expenses by month
        monthly_expenses = {}
        for t in transactions:
            if t["type"] == "expense":
                month = t["date"][:7]  # Get YYYY-MM
                if month not in monthly_expenses:
                    monthly_expenses[month] = 0
                monthly_expenses[month] += t["amount"]

        if len(monthly_expenses) < 2:
            return {
                "error": "Not enough data for prediction. Need at least 2 months of expense data.",
                "history": [],
                "forecast": []
            }

        # Sort by month
        sorted_months = sorted(monthly_expenses.keys())
        monthly_data = [{"month": m, "total": monthly_expenses[m]} for m in sorted_months]

        # Prepare data for linear regression
        X = np.array(range(len(monthly_data))).reshape(-1, 1)
        y = np.array([m["total"] for m in monthly_data])

        # Train the model
        model = LinearRegression()
        model.fit(X, y)

        # Get the last month
        last_month_str = monthly_data[-1]["month"]
        last_month_date = datetime.strptime(last_month_str + "-01", "%Y-%m-%d")

        # Generate predictions
        forecast = []
        for i in range(1, months_ahead + 1):
            future_index = len(monthly_data) - 1 + i
            predicted_value = model.predict([[future_index]])[0]

            future_date = last_month_date + relativedelta(months=i)
            future_month = future_date.strftime("%Y-%m")

            forecast.append({
                "month": future_month,
                "predicted_expense": round(max(0, predicted_value), 2)
            })

        return {
            "history": monthly_data,
            "forecast": forecast
        }


