from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import sqlite3

categories = [
    'Food', 'Transport', 'Entertainment', 'Utilities', 'Healthcare', 'Education', 'Other']

def init_db():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT
        )''')

    # Create budget table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            amount REAL
        )''')

    connection.commit()
    connection.close()


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# API Routes for React frontend
@app.route('/api/summary', methods=['GET'])
def api_summary():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Get all expenses
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()

    # Calculate total expenses
    total_expenses = sum(expense[1] for expense in expenses)

    # Get budget
    cursor.execute('SELECT amount FROM budget WHERE id = 1')
    budget_row = cursor.fetchone()
    budget = budget_row[0] if budget_row else 0

    connection.close()

    return jsonify({
        'expenses': expenses,
        'total_expenses': total_expenses,
        'budget': budget
    })


@app.route('/api/set_budget', methods=['POST'])
def api_set_budget():
    data = request.get_json()
    budget = data['budget']

    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Check if budget entry exists
    cursor.execute('SELECT id FROM budget WHERE id = 1')
    budget_entry = cursor.fetchone()

    if budget_entry is None:
        cursor.execute('INSERT INTO budget (id, amount) VALUES (1, ?)', (budget,))
    else:
        cursor.execute('UPDATE budget SET amount = ? WHERE id = 1', (budget,))

    connection.commit()
    connection.close()

    return jsonify({'success': True})

@app.route('/api/reset_budget', methods=['POST'])
def api_reset_budget():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Reset budget
    cursor.execute('DELETE FROM budget')

    connection.commit()
    connection.close()

    return jsonify({'success': True})


@app.route('/api/add_expense', methods=['POST'])
def api_add_expense():
    data = request.get_json()
    amount = data['amount']
    category = data['category']

    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO expenses (amount, category) VALUES (?, ?)', (amount, category))
    connection.commit()
    connection.close()

    return jsonify({'success': True})


@app.route('/api/reset', methods=['POST'])
def api_reset():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    # Delete all expenses but keep budget
    cursor.execute('DELETE FROM expenses')

    connection.commit()
    connection.close()

    return jsonify({'success': True})


# Original HTML routes (keep these if you want to use templates too)
@app.route('/')
def index():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()
    total_expenses = sum(expense[1] for expense in expenses)
    cursor.execute('SELECT amount FROM budget WHERE id = 1')
    budget_row = cursor.fetchone()
    budget = budget_row[0] if budget_row else 0
    connection.close()
    return render_template('index.html', expenses=expenses, total_expenses=total_expenses, budget=budget)


@app.route('/set_budget', methods=['POST'])
def set_budget():
    budget = request.form['budget']
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM budget WHERE id = 1')
    budget_entry = cursor.fetchone()

    if budget_entry is None:
        cursor.execute('INSERT INTO budget (id, amount) VALUES (1, ?)', (budget,))
    else:
        cursor.execute('UPDATE budget SET amount = ? WHERE id = 1', (budget,))

    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_expense():
    amount = request.form['amount']
    category = request.form['category']
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO expenses (amount, category) VALUES (?, ?)', (amount, category))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/reset_all', methods=['POST'])
def reset_all():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM expenses')
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)