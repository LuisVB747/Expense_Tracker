from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
import sqlite3
import uuid
import os


def init_db():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Create expenses table with session_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            amount REAL,
            category TEXT
        )''')

    # Create budget table with session_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            amount REAL
        )''')

    connection.commit()
    connection.close()


app = Flask(__name__)

# Production-ready CORS setup
if os.environ.get('FLASK_ENV') == 'production':
    # In production, only allow your frontend domain
    CORS(app, resources={r"/api/*": {"origins": "https://ldexpensetracker.netlify.app"}}, supports_credentials=True)

else:
    # In development, allow localhost
    CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

# Secret key for sessions (uses environment variable in production)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')


def get_session_id():
    """Get or create a session ID for the current user"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


# API Routes for React frontend
@app.route('/api/summary', methods=['GET'])
def api_summary():
    session_id = get_session_id()
    
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Get all expenses for this session
    cursor.execute('SELECT * FROM expenses WHERE session_id = ?', (session_id,))
    expenses = cursor.fetchall()

    # Calculate total expenses
    total_expenses = sum(expense[2] for expense in expenses)  # expense[2] is amount

    # Get budget for this session
    cursor.execute('SELECT amount FROM budget WHERE session_id = ? ORDER BY id DESC LIMIT 1', (session_id,))
    budget_row = cursor.fetchone()
    budget = budget_row[0] if budget_row else 0

    connection.close()

    return jsonify({
        'expenses': [[e[0], e[2], e[3]] for e in expenses],  # [id, amount, category]
        'total_expenses': total_expenses,
        'budget': budget
    })


@app.route('/api/categories', methods=['GET'])
def api_categories():
    # Define your categories list
    categories = [
        "Food",
        "Transportation", 
        "Entertainment",
        "Utilities",
        "Shopping",
        "Healthcare",
        "Other"
    ]
    
    return jsonify({'categories': categories})


@app.route('/api/set_budget', methods=['POST'])
def api_set_budget():
    session_id = get_session_id()
    data = request.get_json()
    budget = data['budget']

    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Check if budget entry exists for this session
    cursor.execute('SELECT id FROM budget WHERE session_id = ?', (session_id,))
    budget_entry = cursor.fetchone()

    if budget_entry is None:
        cursor.execute('INSERT INTO budget (session_id, amount) VALUES (?, ?)', (session_id, budget))
    else:
        cursor.execute('UPDATE budget SET amount = ? WHERE session_id = ?', (budget, session_id))

    connection.commit()
    connection.close()

    return jsonify({'success': True})


@app.route('/api/reset_budget', methods=['POST'])
def api_reset_budget():
    session_id = get_session_id()
    
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Reset budget for this session only
    cursor.execute('DELETE FROM budget WHERE session_id = ?', (session_id,))

    connection.commit()
    connection.close()

    return jsonify({'success': True})


@app.route('/api/add_expense', methods=['POST'])
def api_add_expense():
    session_id = get_session_id()
    
    try:
        data = request.get_json()
        print("📦 Received data for new expense:", data)

        if data is None:
            raise ValueError("No JSON payload received")

        amount = float(data.get('amount'))
        category = data.get('category')
        if not category:
            raise ValueError("Missing category")

        print(f"Debug insert values: session_id={session_id}, amount={amount}, category={category}")

        connection = sqlite3.connect('expenses.db')
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO expenses (session_id, amount, category) VALUES (?, ?, ?)', 
            (session_id, amount, category)
        )
        connection.commit()
        connection.close()

        return jsonify({'success': True})

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("❌ Error in /api/add_expense:", e)
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/reset', methods=['POST'])
def api_reset():
    session_id = get_session_id()
    
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Delete all expenses for this session only
    cursor.execute('DELETE FROM expenses WHERE session_id = ?', (session_id,))

    connection.commit()
    connection.close()

    return jsonify({'success': True})


# Health check endpoint for deployment platforms
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})


# Original HTML routes (updated for sessions)
@app.route('/')
def index():
    session_id = get_session_id()
    
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM expenses WHERE session_id = ?', (session_id,))
    expenses = cursor.fetchall()
    total_expenses = sum(expense[2] for expense in expenses)
    cursor.execute('SELECT amount FROM budget WHERE session_id = ? ORDER BY id DESC LIMIT 1', (session_id,))
    budget_row = cursor.fetchone()
    budget = budget_row[0] if budget_row else 0
    connection.close()
    return render_template('index.html', expenses=expenses, total_expenses=total_expenses, budget=budget)


if __name__ == "__main__":
    init_db()
    # Use environment variable for port (required for deployment platforms)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)