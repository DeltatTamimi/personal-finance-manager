import statistics
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_transactions_for_stats, get_income_for_stats


class StatsService:

    @staticmethod
    def calculate_basic_stats(values):
        if not values:
            return {
                "count": 0,
                "sum": 0,
                "mean": 0,
                "median": 0,
                "min": 0,
                "max": 0,
                "std_dev": 0
            }

        return {
            "count": len(values),
            "sum": round(sum(values), 2),
            "mean": round(statistics.mean(values), 2),
            "median": round(statistics.median(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0
        }

    @staticmethod
    def get_transaction_stats(from_date=None, to_date=None):
        transactions = get_transactions_for_stats(from_date, to_date)

        if not transactions:
            return {
                "period": {"from": from_date, "to": to_date},
                "total_transactions": 0,
                "expenses": StatsService.calculate_basic_stats([]),
                "income": StatsService.calculate_basic_stats([]),
                "by_category": {}
            }

        expense_amounts = [t["amount"] for t in transactions if t["type"] == "expense"]
        income_amounts = [t["amount"] for t in transactions if t["type"] == "income"]

        # Group by category
        by_category = {}
        for t in transactions:
            category = t["category"] or "Uncategorized"
            if category not in by_category:
                by_category[category] = {"count": 0, "total": 0, "amounts": []}
            by_category[category]["count"] += 1
            by_category[category]["total"] += t["amount"]
            by_category[category]["amounts"].append(t["amount"])

        # Calculate stats per category
        category_stats = {}
        for category, data in by_category.items():
            category_stats[category] = {
                "count": data["count"],
                "total": round(data["total"], 2),
                "mean": round(statistics.mean(data["amounts"]), 2),
                "percentage": round((data["total"] / sum(expense_amounts) * 100), 2) if expense_amounts else 0
            }

        return {
            "period": {"from": from_date, "to": to_date},
            "total_transactions": len(transactions),
            "expenses": StatsService.calculate_basic_stats(expense_amounts),
            "income": StatsService.calculate_basic_stats(income_amounts),
            "net": round(sum(income_amounts) - sum(expense_amounts), 2),
            "by_category": category_stats
        }

    @staticmethod
    def get_income_stats(from_date=None, to_date=None):
        income_records = get_income_for_stats(from_date, to_date)

        if not income_records:
            return {
                "period": {"from": from_date, "to": to_date},
                "total_records": 0,
                "stats": StatsService.calculate_basic_stats([]),
                "by_source": {}
            }

        amounts = [i["amount"] for i in income_records]

        # Group by source
        by_source = {}
        for i in income_records:
            source = i["source"] or "Unknown"
            if source not in by_source:
                by_source[source] = {"count": 0, "total": 0, "amounts": []}
            by_source[source]["count"] += 1
            by_source[source]["total"] += i["amount"]
            by_source[source]["amounts"].append(i["amount"])

        # Calculate stats per source
        source_stats = {}
        for source, data in by_source.items():
            source_stats[source] = {
                "count": data["count"],
                "total": round(data["total"], 2),
                "mean": round(statistics.mean(data["amounts"]), 2),
                "percentage": round((data["total"] / sum(amounts) * 100), 2)
            }

        return {
            "period": {"from": from_date, "to": to_date},
            "total_records": len(income_records),
            "stats": StatsService.calculate_basic_stats(amounts),
            "by_source": source_stats
        }

    @staticmethod
    def get_summary(from_date=None, to_date=None):
        transaction_stats = StatsService.get_transaction_stats(from_date, to_date)
        income_stats = StatsService.get_income_stats(from_date, to_date)

        return {
            "period": {"from": from_date, "to": to_date},
            "transactions": {
                "count": transaction_stats["total_transactions"],
                "total_expenses": transaction_stats["expenses"]["sum"],
                "total_income": transaction_stats["income"]["sum"],
                "expense_mean": transaction_stats["expenses"]["mean"],
                "expense_median": transaction_stats["expenses"]["median"],
                "expense_std_dev": transaction_stats["expenses"]["std_dev"],
                "expense_min": transaction_stats["expenses"]["min"],
                "expense_max": transaction_stats["expenses"]["max"]
            },
            "income": {
                "count": income_stats["total_records"],
                "total": income_stats["stats"]["sum"],
                "mean": income_stats["stats"]["mean"],
                "median": income_stats["stats"]["median"],
                "std_dev": income_stats["stats"]["std_dev"],
                "min": income_stats["stats"]["min"],
                "max": income_stats["stats"]["max"]
            },
            "category_breakdown": transaction_stats["by_category"],
            "source_breakdown": income_stats["by_source"]
        }


