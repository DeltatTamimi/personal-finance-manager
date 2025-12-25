from flask import request, jsonify
from functools import wraps
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    create_account, get_account, get_all_accounts, update_account, delete_account,
    create_transaction, get_transaction, get_all_transactions,
    get_transactions_by_date_range, update_transaction, delete_transaction,
    create_income, get_income, get_all_income,
    get_income_by_date_range, update_income, delete_income,
    create_user, authenticate_user, validate_token, logout_user
)
from services import StatsService, ForecastService


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if token and token.startswith('Bearer '):
            token = token[7:]

        if not token or not validate_token(token):
            return jsonify({"error": "Unauthorized. Please login first."}), 401

        return f(*args, **kwargs)

    return decorated


def register_routes(app):
    # ==================== AUTH ROUTES (Public) ====================

    @app.route('/auth/register', methods=['POST'])
    def register():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        try:
            result = create_user(username, password)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/auth/login', methods=['POST'])
    def login():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        token = authenticate_user(username, password)

        if token:
            return jsonify({
                "message": "Login successful",
                "token": token,
                "username": username
            })
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    @app.route('/auth/logout', methods=['POST'])
    def logout():
        token = request.headers.get('Authorization')

        if token and token.startswith('Bearer '):
            token = token[7:]

        if token and logout_user(token):
            return jsonify({"message": "Logged out successfully"})

        return jsonify({"error": "Invalid token"}), 400

    # ==================== ACCOUNT ROUTES (Protected) ====================

    @app.route('/accounts', methods=['GET'])
    @require_auth
    def list_accounts():
        accounts = get_all_accounts()
        return jsonify({"accounts": accounts, "count": len(accounts)})

    @app.route('/accounts/<account_id>', methods=['GET'])
    @require_auth
    def get_single_account(account_id):
        account = get_account(account_id)
        if not account:
            return jsonify({"error": f"Account '{account_id}' not found"}), 404
        return jsonify(account)

    @app.route('/accounts', methods=['POST'])
    @require_auth
    def add_account():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ['id', 'name', 'currency']
        for field in required:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400

        try:
            account = create_account(
                id=data['id'],
                name=data['name'],
                currency=data['currency']
            )
            return jsonify(account), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/accounts/<account_id>', methods=['PUT'])
    @require_auth
    def edit_account(account_id):
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        try:
            account = update_account(
                account_id=account_id,
                name=data.get('name'),
                currency=data.get('currency')
            )
            return jsonify(account)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/accounts/<account_id>', methods=['DELETE'])
    @require_auth
    def remove_account(account_id):
        deleted = delete_account(account_id)
        if deleted:
            return jsonify({"message": f"Account '{account_id}' deleted"})
        return jsonify({"error": f"Account '{account_id}' not found"}), 404

    # ==================== TRANSACTION ROUTES (Protected) ====================

    @app.route('/transactions', methods=['GET'])
    @require_auth
    def list_transactions():
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        account_id = request.args.get('account_id')
        type_filter = request.args.get('type')
        category = request.args.get('category')

        try:
            if from_date or to_date or account_id or type_filter or category:
                transactions = get_transactions_by_date_range(
                    from_date=from_date,
                    to_date=to_date,
                    account_id=account_id,
                    type=type_filter,
                    category=category
                )
            else:
                transactions = get_all_transactions()

            return jsonify({"transactions": transactions, "count": len(transactions)})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/transactions/<transaction_id>', methods=['GET'])
    @require_auth
    def get_single_transaction(transaction_id):
        transaction = get_transaction(transaction_id)
        if not transaction:
            return jsonify({"error": f"Transaction '{transaction_id}' not found"}), 404
        return jsonify(transaction)

    @app.route('/transactions', methods=['POST'])
    @require_auth
    def add_transaction():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ['id', 'account_id', 'date', 'amount', 'type']
        for field in required:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400

        try:
            transaction = create_transaction(
                id=data['id'],
                account_id=data['account_id'],
                date=data['date'],
                amount=float(data['amount']),
                type=data['type'],
                category=data.get('category'),
                note=data.get('note')
            )
            return jsonify(transaction), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/transactions/<transaction_id>', methods=['PUT'])
    @require_auth
    def edit_transaction(transaction_id):
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        try:
            amount = float(data['amount']) if 'amount' in data else None
            transaction = update_transaction(
                transaction_id=transaction_id,
                date=data.get('date'),
                amount=amount,
                type=data.get('type'),
                category=data.get('category'),
                note=data.get('note')
            )
            return jsonify(transaction)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/transactions/<transaction_id>', methods=['DELETE'])
    @require_auth
    def remove_transaction(transaction_id):
        deleted = delete_transaction(transaction_id)
        if deleted:
            return jsonify({"message": f"Transaction '{transaction_id}' deleted"})
        return jsonify({"error": f"Transaction '{transaction_id}' not found"}), 404

    # ==================== INCOME ROUTES (Protected) ====================

    @app.route('/income', methods=['GET'])
    @require_auth
    def list_income():
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        account_id = request.args.get('account_id')
        source = request.args.get('source')

        try:
            if from_date or to_date or account_id or source:
                income_list = get_income_by_date_range(
                    from_date=from_date,
                    to_date=to_date,
                    account_id=account_id,
                    source=source
                )
            else:
                income_list = get_all_income()

            return jsonify({"income": income_list, "count": len(income_list)})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/income/<income_id>', methods=['GET'])
    @require_auth
    def get_single_income(income_id):
        income = get_income(income_id)
        if not income:
            return jsonify({"error": f"Income '{income_id}' not found"}), 404
        return jsonify(income)

    @app.route('/income', methods=['POST'])
    @require_auth
    def add_income():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ['id', 'account_id', 'date', 'amount']
        for field in required:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400

        try:
            income = create_income(
                id=data['id'],
                account_id=data['account_id'],
                date=data['date'],
                amount=float(data['amount']),
                source=data.get('source')
            )
            return jsonify(income), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/income/<income_id>', methods=['PUT'])
    @require_auth
    def edit_income(income_id):
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        try:
            amount = float(data['amount']) if 'amount' in data else None
            income = update_income(
                income_id=income_id,
                date=data.get('date'),
                amount=amount,
                source=data.get('source')
            )
            return jsonify(income)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/income/<income_id>', methods=['DELETE'])
    @require_auth
    def remove_income(income_id):
        deleted = delete_income(income_id)
        if deleted:
            return jsonify({"message": f"Income '{income_id}' deleted"})
        return jsonify({"error": f"Income '{income_id}' not found"}), 404

    # ==================== STATISTICS ROUTES (Protected) ====================

    @app.route('/stats/summary', methods=['GET'])
    @require_auth
    def get_stats_summary():
        from_date = request.args.get('from')
        to_date = request.args.get('to')

        summary = StatsService.get_summary(from_date, to_date)
        return jsonify(summary)

    @app.route('/stats/transactions', methods=['GET'])
    @require_auth
    def get_transaction_stats():
        from_date = request.args.get('from')
        to_date = request.args.get('to')

        stats = StatsService.get_transaction_stats(from_date, to_date)
        return jsonify(stats)

    @app.route('/stats/income', methods=['GET'])
    @require_auth
    def get_income_stats():
        from_date = request.args.get('from')
        to_date = request.args.get('to')

        stats = StatsService.get_income_stats(from_date, to_date)
        return jsonify(stats)

    # ==================== FORECAST ROUTES (Protected) ====================

    @app.route('/stats/income_forecast', methods=['GET'])
    @require_auth
    def get_income_forecast():
        months = request.args.get('months', default=3, type=int)

        if months < 1 or months > 12:
            return jsonify({"error": "months must be between 1 and 12"}), 400

        forecast = ForecastService.get_income_forecast(months_ahead=months)
        return jsonify(forecast)

    @app.route('/stats/expense_forecast', methods=['GET'])
    @require_auth
    def get_expense_forecast():
        months = request.args.get('months', default=3, type=int)

        if months < 1 or months > 12:
            return jsonify({"error": "months must be between 1 and 12"}), 400

        forecast = ForecastService.get_expense_trend(months_ahead=months)
        return jsonify(forecast)

    # ==================== UTILITY ROUTES (Public) ====================

    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            "name": "Personal Finance Manager API",
            "version": "1.0.0",
            "auth": {
                "POST /auth/register": "Create new user",
                "POST /auth/login": "Login and get token",
                "POST /auth/logout": "Logout and invalidate token"
            },
            "note": "All other endpoints require Authorization: Bearer <token> header"
        })