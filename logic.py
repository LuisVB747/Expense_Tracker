from flask import Flask, render_template, request, redirect, url_for, CORS
import sqlite3


def init_db():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        category TEXT,
        budget REAL
    )''')
    connection.commit()
    connection.close()

app = Flask(__name__)

@app.route('/')
def index():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()
    total_expenses = sum(expense[1] for expense in expenses)
    cursor.execute('SELECT budget FROM expenses LIMIT 1')
    budget = cursor.fetchone()
    budget = budget[0] if budget else 0
    connection.close()
    return render_template('index.html', expenses=expenses, total_expenses=total_expenses, budget=budget)

@app.route('/set_budget', methods=['POST'])
def set_budget():
    budget = request.form['budget']
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM expenses WHERE id = 1')
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO expenses (amount, category, budget) VALUES (0, "Budget", ?)', (budget,))
    else:
        cursor.execute('UPDATE expenses SET budget = ? WHERE id = 1', (budget,))

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
    # cursor.execute('UPDATE expenses SET budget = 0 where id = 1')
    # cursor.execute('DELETE from expenses WHERE (amount, category) VALUES (?, ?)', (request.form['amount'], request.form['category']))
    connection.commit()
    connection.close()

    # connection = sqlite3.connect('expenses.db')
    # cursor = connection.cursor()
    # cursor.execute('VACUUM')
    # connection.close()

    return redirect(url_for('index'))



def view_expenses():
    if len(expenses) == 0:
        print("There are no expenses")
    else:
        for i, expense in enumerate(expenses):
            print(f"{i}. Amount: {expense['amount']}, Category: {expense['category']}")

def total_expenses():
    return sum(expense['amount'] for expense in expenses)

def check_budget():
    total = total_expenses()
    percentage = (total/budget) * 100
    over_budget = total_expenses() - budget
    if total > budget:
        print(f"Warning, you have spent {total} which is {over_budget} more that your total budget of {budget}")
    elif total >= budget * 0.8:
        print(f"Warning, you have spent {total} which is {percentage:.2f}% of your total budget of {budget}")

def main():
    while True:
        print("\n--- Expense Tracker ---")
        print("1. Set Budget")
        print("2. Add Expense")
        print("3. View Expenses")
        print("4. Show Total Expenses")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            set_budget()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            view_expenses()
        elif choice == "4":
            print(f'Total expenses: {total_expenses()}')
        elif choice == "5":
            print("Thank you!")
            break
        else:
            print("Invalid choice. PLease try again.")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)