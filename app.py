import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, g

# Initialize Flask application
app = Flask(__name__)

# Database configuration
DATABASE = 'finance_tracker.db'

def get_db():
    """
    Establishes a database connection or returns the existing one.
    Uses Flask's `g` object to store the connection for the current request.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Set row_factory to sqlite3.Row to get dictionary-like rows
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """
    Closes the database connection at the end of the request.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """
    Initializes the database by creating the 'expenses' table if it doesn't exist.
    This function should be called once when the application starts or is deployed.
    It now includes a 'category' column.
    """
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                category TEXT
            )
        ''')
        db.commit()
        print("Database initialized successfully.")

def add_expense_to_db(item, price, date, category):
    """
    Adds a new expense record to the database, including date and category.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO expenses (item, price, date, category) VALUES (?, ?, ?, ?)",
        (item, price, date, category)
    )
    db.commit()

def get_total_spending(period_type):
    """
    Calculates the total spending for a given period (day, month, or year).
    :param period_type: 'day', 'month', or 'year'
    :return: Total spending for the current period, or 0.00 if no expenses found.
    """
    db = get_db()
    cursor = db.cursor()
    current_date = datetime.now()
    total = 0.00

    if period_type == 'day':
        # Get total for today
        date_str = current_date.strftime('%Y-%m-%d')
        cursor.execute("SELECT SUM(price) FROM expenses WHERE date = ?", (date_str,))
    elif period_type == 'month':
        # Get total for the current month
        month_str = current_date.strftime('%Y-%m')
        cursor.execute("SELECT SUM(price) FROM expenses WHERE strftime('%Y-%m', date) = ?", (month_str,))
    elif period_type == 'year':
        # Get total for the current year
        year_str = current_date.strftime('%Y')
        cursor.execute("SELECT SUM(price) FROM expenses WHERE strftime('%Y', date) = ?", (year_str,))
    else:
        return 0.00 # Invalid period type

    result = cursor.fetchone()[0]
    if result is not None:
        total = float(result)
    return total

def get_recent_expenses(limit=10):
    """
    Fetches the most recent expenses from the database.
    :param limit: The maximum number of expenses to retrieve.
    :return: A list of expense dictionaries.
    """
    db = get_db()
    cursor = db.cursor()
    # Order by id DESC to get the most recent entries
    cursor.execute("SELECT id, item, price, date, category FROM expenses ORDER BY id DESC LIMIT ?", (limit,))
    expenses = cursor.fetchall()
    return expenses

@app.route('/', methods=['GET'])
def index():
    """
    Renders the main page, displaying the expense input form, spending totals,
    and a list of recent expenses.
    """
    # Get current spending totals
    daily_total = get_total_spending('day')
    monthly_total = get_total_spending('month')
    yearly_total = get_total_spending('year')

    # Get recent expenses
    recent_expenses = get_recent_expenses(limit=10) # Display last 10 expenses

    # Define categories for the dropdown
    categories = [
        "Food", "Transport", "Entertainment", "Shopping", "Utilities",
        "Rent", "Health", "Education", "Groceries", "Other"
    ]

    return render_template(
        'index.html',
        daily_total=daily_total,
        monthly_total=monthly_total,
        yearly_total=yearly_total,
        recent_expenses=recent_expenses,
        categories=categories,
        current_date=datetime.now().strftime('%Y-%m-%d') # Pass current date for default on date picker
    )

@app.route('/add_expense', methods=['POST'])
def add_expense():
    """
    Handles the submission of a new expense.
    Validates input and adds the expense to the database.
    Now includes date and category.
    """
    item = request.form.get('item')
    price_str = request.form.get('price')
    expense_date = request.form.get('expense_date') # New: get date from form
    category = request.form.get('category') # New: get category from form

    # Basic validation
    if not item or not price_str or not expense_date or not category:
        print("Error: All fields (item, price, date, category) are required.")
        return redirect(url_for('index'))

    try:
        price = float(price_str)
        if price <= 0:
            print("Error: Price must be a positive number.")
            return redirect(url_for('index'))
    except ValueError:
        print("Error: Price must be a valid number.")
        return redirect(url_for('index'))

    # Validate date format (optional, as HTML type="date" helps, but good for robustness)
    try:
        datetime.strptime(expense_date, '%Y-%m-%d')
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        return redirect(url_for('index'))

    add_expense_to_db(item, price, expense_date, category)

    return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize the database when the application starts
    init_db()
    # Run the Flask app in debug mode (for development)
    app.run(debug=True)
