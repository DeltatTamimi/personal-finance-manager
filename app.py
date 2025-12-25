from flask import Flask, render_template
from database import init_db, seed_sample_data, get_all_accounts, init_users_table
from api import register_routes
import webbrowser
from threading import Timer

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

register_routes(app)


@app.route('/app')
def frontend():
    return render_template('index.html')


def setup_database():
    init_db()
    init_users_table()

    accounts = get_all_accounts()
    if not accounts:
        print("No data found. Seeding sample data...")
        seed_sample_data()
    else:
        print(f"Database has {len(accounts)} accounts")


def open_browser():
    webbrowser.open('http://127.0.0.1:5000/app')


if __name__ == '__main__':
    print("=" * 50)
    print("Personal Finance Manager API")
    print("=" * 50)

    setup_database()

    print("\nStarting server...")
    print("API running at: http://127.0.0.1:5000")
    print("Frontend at: http://127.0.0.1:5000/app")
    print("Press CTRL+C to stop\n")

    Timer(1.5, open_browser).start()

    app.run(debug=True, port=5000, use_reloader=False)