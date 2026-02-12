import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    #Check if categories table is empty, if so insert default categories
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        default_categories = ['Books']
        c.executemany("INSERT INTO categories (name) VALUES (?)", [(cat,) for cat in default_categories])
        conn.commit()
        print("Inserted default categories into the database.")

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    # get all categories for dropdown
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()

    # Filter Logic
    category_filter = request.args.get('category_filter')
    if category_filter and category_filter != 'All':
        c.execute("SELECT * FROM expenses WHERE category = ?", (category_filter,))
    else:
        c.execute("SELECT * FROM expenses")
    expenses = c.fetchall()

    #calculate total and category totals
    total_cost = 0
    category_totals = {}
    
    for expense in expenses:
        total_cost += expense[2]
    
    # Calculate totals for each category
    for category in categories:
        c.execute("SELECT SUM(amount) FROM expenses WHERE category = ?", (category[1],))
        result = c.fetchone()
        category_totals[category[1]] = result[0] if result[0] is not None else 0.0

    conn.close()

    return render_template('index.html', expenses=expenses, total_cost=total_cost, categories=categories, selected_filter=category_filter, category_totals=category_totals)

@app.route('/add', methods=['POST'])
def add_expense():
    item = request.form['item']
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']

    conn= sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (item, amount, category, date) VALUES (?, ?, ?, ?)", (item, amount, category, date))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/add_category', methods=['POST'])
def add_category():
    category_name = request.form['category_name']
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        # This prevents crashing if you try to add a duplicate
        print("Category already exists.")
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete_category/<int:id>')
def delete_category(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0') 