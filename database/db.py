import sqlite3
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def close_db_connection(conn):
    if conn:
        conn.close()


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS accounts
                   (
                       id
                       TEXT
                       PRIMARY
                       KEY,
                       name
                       TEXT
                       NOT
                       NULL,
                       currency
                       TEXT
                       NOT
                       NULL
                       DEFAULT
                       'USD',
                       created_at
                       TEXT
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS transactions
                   (
                       id
                       TEXT
                       PRIMARY
                       KEY,
                       account_id
                       TEXT
                       NOT
                       NULL,
                       date
                       TEXT
                       NOT
                       NULL,
                       amount
                       REAL
                       NOT
                       NULL,
                       type
                       TEXT
                       NOT
                       NULL
                       CHECK (
                       type
                       IN
                   (
                       'expense',
                       'income'
                   )),
                       category TEXT,
                       note TEXT,
                       created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY
                   (
                       account_id
                   ) REFERENCES accounts
                   (
                       id
                   ) ON DELETE CASCADE
                       )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS income
                   (
                       id
                       TEXT
                       PRIMARY
                       KEY,
                       account_id
                       TEXT
                       NOT
                       NULL,
                       date
                       TEXT
                       NOT
                       NULL,
                       amount
                       REAL
                       NOT
                       NULL,
                       source
                       TEXT,
                       created_at
                       TEXT
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       account_id
                   ) REFERENCES accounts
                   (
                       id
                   ) ON DELETE CASCADE
                       )
                   ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_income_date ON income(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_income_account ON income(account_id)')

    conn.commit()
    close_db_connection(conn)
    print("Database initialized successfully")


def drop_all_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS income")
    cursor.execute("DROP TABLE IF EXISTS accounts")
    conn.commit()
    close_db_connection(conn)
    print("All tables dropped")


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows):
    return [dict(row) for row in rows]


def validate_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ==================== ACCOUNT OPERATIONS ====================

def create_account(id, name, currency="USD"):
    if not id or not id.strip():
        raise ValueError("Account ID cannot be empty")
    if not name or not name.strip():
        raise ValueError("Account name cannot be empty")
    if not currency or len(currency) != 3:
        raise ValueError("Currency must be a 3-letter code")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO accounts (id, name, currency) VALUES (?, ?, ?)",
            (id.strip(), name.strip(), currency.upper())
        )
        conn.commit()
        return {"id": id.strip(), "name": name.strip(), "currency": currency.upper()}
    except sqlite3.IntegrityError:
        raise ValueError(f"Account with ID '{id}' already exists")
    finally:
        close_db_connection(conn)


def get_account(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
    row = cursor.fetchone()
    close_db_connection(conn)
    return row_to_dict(row)


def get_all_accounts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts ORDER BY name")
    rows = cursor.fetchall()
    close_db_connection(conn)
    return rows_to_list(rows)


def update_account(account_id, name=None, currency=None):
    existing = get_account(account_id)
    if not existing:
        raise ValueError(f"Account with ID '{account_id}' not found")

    updates = []
    params = []

    if name is not None:
        if not name.strip():
            raise ValueError("Account name cannot be empty")
        updates.append("name = ?")
        params.append(name.strip())

    if currency is not None:
        if len(currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
        updates.append("currency = ?")
        params.append(currency.upper())

    if not updates:
        return existing

    params.append(account_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"UPDATE accounts SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    close_db_connection(conn)
    return get_account(account_id)


def delete_account(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    close_db_connection(conn)
    return deleted


# ==================== TRANSACTION OPERATIONS ====================

def create_transaction(id, account_id, date, amount, type, category=None, note=None):
    if not id or not id.strip():
        raise ValueError("Transaction ID cannot be empty")
    if not account_id:
        raise ValueError("Account ID is required")
    if not get_account(account_id):
        raise ValueError(f"Account '{account_id}' does not exist")
    if not validate_date_format(date):
        raise ValueError("Date must be in YYYY-MM-DD format")
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if type not in ('expense', 'income'):
        raise ValueError("Type must be 'expense' or 'income'")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO transactions (id, account_id, date, amount, type, category, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (id.strip(), account_id, date, amount, type, category, note)
        )
        conn.commit()
        return {
            "id": id.strip(), "account_id": account_id, "date": date,
            "amount": amount, "type": type, "category": category, "note": note
        }
    except sqlite3.IntegrityError:
        raise ValueError(f"Transaction with ID '{id}' already exists")
    finally:
        close_db_connection(conn)


def get_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    row = cursor.fetchone()
    close_db_connection(conn)
    return row_to_dict(row)


def get_all_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = cursor.fetchall()
    close_db_connection(conn)
    return rows_to_list(rows)


def get_transactions_by_date_range(from_date=None, to_date=None, account_id=None,
                                   type=None, category=None):
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if from_date:
        if not validate_date_format(from_date):
            raise ValueError("from_date must be in YYYY-MM-DD format")
        query += " AND date >= ?"
        params.append(from_date)

    if to_date:
        if not validate_date_format(to_date):
            raise ValueError("to_date must be in YYYY-MM-DD format")
        query += " AND date <= ?"
        params.append(to_date)

    if account_id:
        query += " AND account_id = ?"
        params.append(account_id)

    if type:
        query += " AND type = ?"
        params.append(type)

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY date DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    close_db_connection(conn)
    return rows_to_list(rows)


def update_transaction(transaction_id, date=None, amount=None, type=None,
                       category=None, note=None):
    existing = get_transaction(transaction_id)
    if not existing:
        raise ValueError(f"Transaction with ID '{transaction_id}' not found")

    updates = []
    params = []

    if date is not None:
        if not validate_date_format(date):
            raise ValueError("Date must be in YYYY-MM-DD format")
        updates.append("date = ?")
        params.append(date)

    if amount is not None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        updates.append("amount = ?")
        params.append(amount)

    if type is not None:
        if type not in ('expense', 'income'):
            raise ValueError("Type must be 'expense' or 'income'")
        updates.append("type = ?")
        params.append(type)

    if category is not None:
        updates.append("category = ?")
        params.append(category)

    if note is not None:
        updates.append("note = ?")
        params.append(note)

    if not updates:
        return existing

    params.append(transaction_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    close_db_connection(conn)
    return get_transaction(transaction_id)


def delete_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    close_db_connection(conn)
    return deleted


# ==================== INCOME OPERATIONS ====================

def create_income(id, account_id, date, amount, source=None):
    if not id or not id.strip():
        raise ValueError("Income ID cannot be empty")
    if not account_id:
        raise ValueError("Account ID is required")
    if not get_account(account_id):
        raise ValueError(f"Account '{account_id}' does not exist")
    if not validate_date_format(date):
        raise ValueError("Date must be in YYYY-MM-DD format")
    if amount <= 0:
        raise ValueError("Amount must be positive")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO income (id, account_id, date, amount, source) VALUES (?, ?, ?, ?, ?)",
            (id.strip(), account_id, date, amount, source)
        )
        conn.commit()
        return {
            "id": id.strip(), "account_id": account_id,
            "date": date, "amount": amount, "source": source
        }
    except sqlite3.IntegrityError:
        raise ValueError(f"Income with ID '{id}' already exists")
    finally:
        close_db_connection(conn)


def get_income(income_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM income WHERE id = ?", (income_id,))
    row = cursor.fetchone()
    close_db_connection(conn)
    return row_to_dict(row)


def get_all_income():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM income ORDER BY date DESC")
    rows = cursor.fetchall()
    close_db_connection(conn)
    return rows_to_list(rows)


def get_income_by_date_range(from_date=None, to_date=None, account_id=None, source=None):
    query = "SELECT * FROM income WHERE 1=1"
    params = []

    if from_date:
        if not validate_date_format(from_date):
            raise ValueError("from_date must be in YYYY-MM-DD format")
        query += " AND date >= ?"
        params.append(from_date)

    if to_date:
        if not validate_date_format(to_date):
            raise ValueError("to_date must be in YYYY-MM-DD format")
        query += " AND date <= ?"
        params.append(to_date)

    if account_id:
        query += " AND account_id = ?"
        params.append(account_id)

    if source:
        query += " AND source = ?"
        params.append(source)

    query += " ORDER BY date DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    close_db_connection(conn)
    return rows_to_list(rows)


def update_income(income_id, date=None, amount=None, source=None):
    existing = get_income(income_id)
    if not existing:
        raise ValueError(f"Income with ID '{income_id}' not found")

    updates = []
    params = []

    if date is not None:
        if not validate_date_format(date):
            raise ValueError("Date must be in YYYY-MM-DD format")
        updates.append("date = ?")
        params.append(date)

    if amount is not None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        updates.append("amount = ?")
        params.append(amount)

    if source is not None:
        updates.append("source = ?")
        params.append(source)

    if not updates:
        return existing

    params.append(income_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"UPDATE income SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    close_db_connection(conn)
    return get_income(income_id)


def delete_income(income_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id = ?", (income_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    close_db_connection(conn)
    return deleted


# ==================== AGGREGATION QUERIES ====================

def get_monthly_income_totals():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
                   FROM income
                   GROUP BY strftime('%Y-%m', date)
                   ORDER BY month ASC
                   """)
    rows = cursor.fetchall()
    close_db_connection(conn)
    return [{"month": row["month"], "total": row["total"]} for row in rows]


def get_transactions_for_stats(from_date=None, to_date=None):
    return get_transactions_by_date_range(from_date=from_date, to_date=to_date)


def get_income_for_stats(from_date=None, to_date=None):
    return get_income_by_date_range(from_date=from_date, to_date=to_date)


# ==================== SAMPLE DATA ====================

def seed_sample_data():
    accounts = [
        ("ACC001", "Main Checking", "USD"),
        ("ACC002", "Savings", "USD"),
        ("ACC003", "Euro Account", "EUR"),
    ]

    for acc in accounts:
        try:
            create_account(*acc)
        except ValueError:
            pass

    transactions = [
        ("TXN001", "ACC001", "2024-07-15", 150.00, "expense", "Groceries", "Weekly shopping"),
        ("TXN002", "ACC001", "2024-07-20", 50.00, "expense", "Transport", "Gas"),
        ("TXN003", "ACC001", "2024-08-10", 200.00, "expense", "Utilities", "Electric bill"),
        ("TXN004", "ACC001", "2024-08-15", 80.00, "expense", "Entertainment", "Movies"),
        ("TXN005", "ACC001", "2024-09-05", 120.00, "expense", "Groceries", "Weekly shopping"),
        ("TXN006", "ACC001", "2024-09-20", 300.00, "expense", "Shopping", "Clothes"),
        ("TXN007", "ACC001", "2024-10-10", 175.00, "expense", "Groceries", "Weekly shopping"),
        ("TXN008", "ACC001", "2024-10-25", 90.00, "expense", "Dining", "Restaurant"),
        ("TXN009", "ACC001", "2024-11-05", 250.00, "expense", "Utilities", "Internet + Phone"),
        ("TXN010", "ACC001", "2024-11-15", 100.00, "expense", "Entertainment", "Concert tickets"),
        ("TXN011", "ACC001", "2024-12-01", 180.00, "expense", "Groceries", "Weekly shopping"),
        ("TXN012", "ACC001", "2024-12-10", 500.00, "expense", "Shopping", "Christmas gifts"),
    ]

    for txn in transactions:
        try:
            create_transaction(*txn)
        except ValueError:
            pass

    income_records = [
        ("INC001", "ACC001", "2024-07-01", 3000.00, "Salary"),
        ("INC002", "ACC001", "2024-07-15", 500.00, "Freelance"),
        ("INC003", "ACC001", "2024-08-01", 3000.00, "Salary"),
        ("INC004", "ACC001", "2024-08-20", 300.00, "Freelance"),
        ("INC005", "ACC001", "2024-09-01", 3200.00, "Salary"),
        ("INC006", "ACC001", "2024-10-01", 3200.00, "Salary"),
        ("INC007", "ACC001", "2024-10-10", 800.00, "Freelance"),
        ("INC008", "ACC001", "2024-11-01", 3400.00, "Salary"),
        ("INC009", "ACC001", "2024-11-25", 200.00, "Bonus"),
        ("INC010", "ACC001", "2024-12-01", 3400.00, "Salary"),
        ("INC011", "ACC001", "2024-12-15", 1000.00, "Year-end Bonus"),
    ]

    for inc in income_records:
        try:
            create_income(*inc)
        except ValueError:
            pass

    print("Sample data seeded successfully")


# ==================== USER OPERATIONS ====================

def init_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       password
                       TEXT
                       NOT
                       NULL,
                       token
                       TEXT,
                       created_at
                       TEXT
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    conn.commit()
    close_db_connection(conn)


def create_user(username, password):
    import hashlib

    if not username or not password:
        raise ValueError("Username and password are required")

    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters")

    hashed = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username.strip(), hashed)
        )
        conn.commit()
        return {"username": username, "message": "User created successfully"}
    except sqlite3.IntegrityError:
        raise ValueError(f"Username '{username}' already exists")
    finally:
        close_db_connection(conn)


def authenticate_user(username, password):
    import hashlib
    import secrets

    hashed = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password = ?",
        (username, hashed)
    )
    user = cursor.fetchone()

    if not user:
        close_db_connection(conn)
        return None

    token = secrets.token_hex(32)

    cursor.execute(
        "UPDATE users SET token = ? WHERE username = ?",
        (token, username)
    )
    conn.commit()
    close_db_connection(conn)

    return token


def validate_token(token):
    if not token:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE token = ?", (token,))
    user = cursor.fetchone()
    close_db_connection(conn)

    return user is not None


def logout_user(token):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET token = NULL WHERE token = ?", (token,))
    conn.commit()
    affected = cursor.rowcount
    close_db_connection(conn)

    return affected > 0
