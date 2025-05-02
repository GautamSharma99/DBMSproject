from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        name TEXT,
        email TEXT,
        phone TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registration_id INTEGER,
        latitude TEXT,
        longitude TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("SELECT * FROM events")
    events = c.fetchall()
    conn.close()
    return render_template('index.html', events=events)

@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        conn = sqlite3.connect('events.db')
        c = conn.cursor()
        c.execute("INSERT INTO events (title, description) VALUES (?, ?)", (title, description))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_event.html')

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register(event_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        conn = sqlite3.connect('events.db')
        c = conn.cursor()
        c.execute("INSERT INTO registrations (event_id, name, email, phone) VALUES (?, ?, ?, ?)",
                  (event_id, name, email, phone))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('register.html', event_id=event_id)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        name = request.form['name']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        conn = sqlite3.connect('events.db')
        c = conn.cursor()
        c.execute("SELECT id FROM registrations WHERE name=?", (name,))
        result = c.fetchone()
        if result:
            reg_id = result[0]
            c.execute("INSERT INTO attendance (registration_id, latitude, longitude) VALUES (?, ?, ?)",
                      (reg_id, latitude, longitude))
            conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('attendance.html')

@app.route('/registrations/<int:event_id>')
def view_registrations(event_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("SELECT name, email, phone FROM registrations WHERE event_id=?", (event_id,))
    registrations = c.fetchall()
    conn.close()
    return render_template('registration.html', registrations=registrations, event_id=event_id)

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        c.execute("UPDATE events SET title=?, description=?, date=? WHERE id=?", (title, description, date, event_id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        c.execute("SELECT * FROM events WHERE id=?", (event_id,))
        event = c.fetchone()
        conn.close()
        return render_template('edit_event.html', event=event)

@app.route('/delete_event/<int:event_id>')
def delete_event(event_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id=?", (event_id,))
    c.execute("DELETE FROM registrations WHERE event_id=?", (event_id,))  # Clean up related registrations
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit_registration/<int:event_id>/<int:reg_id>', methods=['GET', 'POST'])
def edit_registration(event_id, reg_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        c.execute("UPDATE registrations SET name=?, email=?, phone=? WHERE id=?", (name, email, phone, reg_id))
        conn.commit()
        conn.close()
        return redirect(f'/registrations/{event_id}')
    else:
        c.execute("SELECT * FROM registrations WHERE id=?", (reg_id,))
        reg = c.fetchone()
        conn.close()
        return render_template('edit_registration.html', reg=reg, event_id=event_id)

@app.route('/delete_registration/<int:event_id>/<int:reg_id>')
def delete_registration(event_id, reg_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("DELETE FROM registrations WHERE id=?", (reg_id,))
    conn.commit()
    conn.close()
    return redirect(f'/registrations/{event_id}')

@app.route('/view_attendance/<int:event_id>')
def view_attendance(event_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    # Join tables to get attendance records with participant names for the specific event
    c.execute("""
        SELECT r.name, r.email, a.latitude, a.longitude, a.timestamp 
        FROM attendance a
        JOIN registrations r ON a.registration_id = r.id
        WHERE r.event_id = ?
    """, (event_id,))
    attendance_records = c.fetchall()
    conn.close()
    return render_template('view_attendance.html', attendance_records=attendance_records, event_id=event_id)

if __name__ == '__main__':
    app.run(debug=True)

