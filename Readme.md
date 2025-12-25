
# Personal Finance Manager API

A Flask-based REST API for managing personal finances with SQLite database, statistical analysis, and income forecasting using linear regression.

## Features

- User Authentication (Register, Login, Logout)
- Account Management (Multiple currencies)
- Transaction Tracking (Expenses and Income)
- Income Management (Track income sources)
- Statistical Analysis (Mean, Median, Min, Max, Standard Deviation)
- Income Forecasting (Linear Regression)
- Web Interface (Charts and Visualizations)

## Project Structure

```
pfm_project/
├── api/
│   ├── __init__.py
│   └── routes.py
├── database/
│   ├── __init__.py
│   └── db.py
├── services/
│   ├── __init__.py
│   ├── stats_service.py
│   └── forecast_service.py
├── templates/
│   └── index.html
├── app.py
├── config.py
├── finance.db
├── requirements.txt
└── README.md
```

## Installation

### 1. Navigate to Project Directory

```bash
cd pfm_project
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

The application will automatically open at `http://127.0.0.1:5000/app`

## How to Use

### Using the Web Interface

#### Step 1: Register an Account
1. When the app opens, you'll see the login page
2. Click the "Register" tab
3. Enter a username and password (minimum 4 characters)
4. Click "Create Account"
5. You'll see a success message

#### Step 2: Login
1. Click the "Login" tab
2. Enter your username and password
3. Click "Login"
4. You'll be redirected to the dashboard

#### Step 3: View Dashboard
- See total accounts, income, expenses, and net balance
- View expense breakdown by category (pie chart)
- View income breakdown by source (pie chart)
- See recent transactions

#### Step 4: Create an Account
1. Click "Accounts" in the navigation
2. Fill in the form:
   - Account ID (e.g., ACC001)
   - Account Name (e.g., Main Checking)
   - Currency (USD, EUR, GBP, HUF)
3. Click "Create Account"
4. You'll see a success toast notification

#### Step 5: Add Transactions
1. Click "Transactions" in the navigation
2. Fill in the form:
   - Transaction ID (e.g., TXN001)
   - Select an account
   - Choose date
   - Enter amount
   - Select type (Expense or Income)
   - Enter category (e.g., Groceries, Rent, Entertainment)
   - Add optional note
3. Click "Add Transaction"

#### Step 6: Add Income
1. Click "Income" in the navigation
2. Fill in the form:
   - Income ID (e.g., INC001)
   - Select an account
   - Choose date
   - Enter amount
   - Enter source (e.g., Salary, Freelance, Bonus)
3. Click "Add Income"

#### Step 7: View Statistics
1. Click "Statistics" in the navigation
2. Optionally filter by date range
3. Click "Get Statistics"
4. View:
   - Mean, Median, Min, Max expenses
   - Standard Deviation
   - Category breakdown
   - Source breakdown

#### Step 8: Generate Forecast
1. Click "Forecast" in the navigation
2. Select months to predict (3, 6, or 12)
3. Click "Generate Forecast"
4. View:
   - Historical income chart
   - Predicted income (dashed line)
   - Model performance (R-squared)
   - Monthly income change

#### Step 9: Logout
1. Click the "Logout" button in the header
2. You'll be redirected to the login page

### Using the API (Postman)

#### Step 1: Register
1. Open Postman
2. Create new request:
   - Method: POST
   - URL: `http://127.0.0.1:5000/auth/register`
   - Body (raw JSON):
   ```json
   {
       "username": "demo",
       "password": "demo123"
   }
   ```
3. Click Send

#### Step 2: Login
1. Create new request:
   - Method: POST
   - URL: `http://127.0.0.1:5000/auth/login`
   - Body (raw JSON):
   ```json
   {
       "username": "demo",
       "password": "demo123"
   }
   ```
2. Click Send
3. Copy the `token` from the response

#### Step 3: Set Authorization Header
For all following requests, add header:
- Key: `Authorization`
- Value: `Bearer YOUR_TOKEN_HERE`

#### Step 4: Create Account
- Method: POST
- URL: `http://127.0.0.1:5000/accounts`
- Headers: `Authorization: Bearer <token>`
- Body:
```json
{
    "id": "ACC001",
    "name": "Main Checking",
    "currency": "USD"
}
```

#### Step 5: Create Transaction
- Method: POST
- URL: `http://127.0.0.1:5000/transactions`
- Headers: `Authorization: Bearer <token>`
- Body:
```json
{
    "id": "TXN001",
    "account_id": "ACC001",
    "date": "2024-12-15",
    "amount": 150.00,
    "type": "expense",
    "category": "Groceries",
    "note": "Weekly shopping"
}
```

#### Step 6: Create Income
- Method: POST
- URL: `http://127.0.0.1:5000/income`
- Headers: `Authorization: Bearer <token>`
- Body:
```json
{
    "id": "INC001",
    "account_id": "ACC001",
    "date": "2024-12-01",
    "amount": 3000.00,
    "source": "Salary"
}
```

#### Step 7: Get Statistics
- Method: GET
- URL: `http://127.0.0.1:5000/stats/summary`
- Headers: `Authorization: Bearer <token>`

#### Step 8: Get Forecast
- Method: GET
- URL: `http://127.0.0.1:5000/stats/income_forecast?months=3`
- Headers: `Authorization: Bearer <token>`

### Using the API (cURL)

#### Register
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

#### Login
```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

#### Create Account
```bash
curl -X POST http://127.0.0.1:5000/accounts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"id": "ACC001", "name": "Main Account", "currency": "USD"}'
```

#### Create Transaction
```bash
curl -X POST http://127.0.0.1:5000/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"id": "TXN001", "account_id": "ACC001", "date": "2024-12-15", "amount": 50, "type": "expense", "category": "Food"}'
```

#### Create Income
```bash
curl -X POST http://127.0.0.1:5000/income \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"id": "INC001", "account_id": "ACC001", "date": "2024-12-01", "amount": 3000, "source": "Salary"}'
```

#### Get All Accounts
```bash
curl http://127.0.0.1:5000/accounts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Transactions with Filter
```bash
curl "http://127.0.0.1:5000/transactions?from=2024-01-01&to=2024-12-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Statistics
```bash
curl http://127.0.0.1:5000/stats/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Income Forecast
```bash
curl "http://127.0.0.1:5000/stats/income_forecast?months=3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Delete Transaction
```bash
curl -X DELETE http://127.0.0.1:5000/transactions/TXN001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Logout
```bash
curl -X POST http://127.0.0.1:5000/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get token |
| POST | `/auth/logout` | Logout |

### Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/accounts` | List all accounts |
| GET | `/accounts/<id>` | Get account by ID |
| POST | `/accounts` | Create account |
| PUT | `/accounts/<id>` | Update account |
| DELETE | `/accounts/<id>` | Delete account |

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transactions` | List transactions |
| GET | `/transactions?from=YYYY-MM-DD&to=YYYY-MM-DD` | Filter by date |
| GET | `/transactions/<id>` | Get transaction by ID |
| POST | `/transactions` | Create transaction |
| PUT | `/transactions/<id>` | Update transaction |
| DELETE | `/transactions/<id>` | Delete transaction |

### Income

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/income` | List income records |
| GET | `/income?from=YYYY-MM-DD&to=YYYY-MM-DD` | Filter by date |
| GET | `/income/<id>` | Get income by ID |
| POST | `/income` | Create income |
| PUT | `/income/<id>` | Update income |
| DELETE | `/income/<id>` | Delete income |

### Statistics & Forecasting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats/summary` | Get statistical summary |
| GET | `/stats/summary?from=YYYY-MM-DD&to=YYYY-MM-DD` | Filter by date |
| GET | `/stats/income_forecast?months=3` | Predict future income |
| GET | `/stats/expense_forecast?months=3` | Predict future expenses |

## Database Schema

### accounts
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| name | TEXT | Account name |
| currency | TEXT | Currency code |
| created_at | TEXT | Timestamp |

### transactions
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| account_id | TEXT | Foreign key |
| date | TEXT | YYYY-MM-DD |
| amount | REAL | Amount |
| type | TEXT | expense/income |
| category | TEXT | Category |
| note | TEXT | Note |
| created_at | TEXT | Timestamp |

### income
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| account_id | TEXT | Foreign key |
| date | TEXT | YYYY-MM-DD |
| amount | REAL | Amount |
| source | TEXT | Source |
| created_at | TEXT | Timestamp |

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Unique |
| password | TEXT | Hashed |
| token | TEXT | Auth token |
| created_at | TEXT | Timestamp |

## Statistical Analysis

The `/stats/summary` endpoint returns:

- **count**: Number of transactions
- **sum**: Total amount
- **mean**: Average amount
- **median**: Middle value
- **min**: Minimum amount
- **max**: Maximum amount
- **std_dev**: Standard deviation
- **category_breakdown**: Expenses grouped by category
- **source_breakdown**: Income grouped by source

## Linear Regression Forecasting

The income forecasting uses scikit-learn's LinearRegression:

1. Aggregates monthly income totals
2. Fits a linear model to historical data
3. Predicts future months

Response includes:
- **history**: Past monthly income
- **forecast**: Predicted future income
- **model_info**: Slope, intercept, R-squared

## Technologies

- Python 3.x
- Flask
- SQLite
- scikit-learn
- NumPy
- Chart.js

## Author

Mohannad Altamimi
