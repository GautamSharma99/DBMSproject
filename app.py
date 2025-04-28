from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
