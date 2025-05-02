from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Create DB if it doesn't exist
def init_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        conn.execute('''CREATE TABLE registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            event_name TEXT NOT NULL
        )''')
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    event_name = request.form['event_name']

    conn = sqlite3.connect('database.db')
    conn.execute("INSERT INTO registrations (name, email, phone, event_name) VALUES (?, ?, ?, ?)",
                 (name, email, phone, event_name))
    conn.commit()
    conn.close()
    return "Registration Successful!"

@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations")
    rows = cursor.fetchall()
    conn.close()
    return render_template('admin.html', registrations=rows)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect('database.db')
    conn.execute("DELETE FROM registrations WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/edit/<int:id>', methods=['GET'])
def edit(id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations WHERE id = ?", (id,))
    registration = cursor.fetchone()
    conn.close()
    return render_template('edit.html', registration=registration)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    event_name = request.form['event_name']
    
    conn = sqlite3.connect('database.db')
    conn.execute("UPDATE registrations SET name = ?, email = ?, phone = ?, event_name = ? WHERE id = ?",
                 (name, email, phone, event_name, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
