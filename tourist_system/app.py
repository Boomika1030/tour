from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_tourist_key'
DATABASE = 'tourist.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        
        # Create places table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                image_url TEXT
            )
        ''')
        
        # Create bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                place_id INTEGER,
                booking_date TEXT,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(place_id) REFERENCES places(id)
            )
        ''')
        
        # Insert admin if not exists
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)', ('admin', 'admin123', 1))
            
        # Insert some demo places if empty
        cursor.execute('SELECT COUNT(*) FROM places')
        if cursor.fetchone()[0] == 0:
            places = [
                ('Paris, France', 'Experience the city of love, Eiffel Tower, and fine dining.', 1200.00, '/static/images/paris.jpg'),
                ('Kyoto, Japan', 'Discover historical temples, gardens, and traditional wooden houses.', 1500.00, '/static/images/kyoto.jpg'),
                ('Rome, Italy', 'Explore ancient ruins, art, and vibrant street life.', 1100.00, '/static/images/rome.jpg')
            ]
            cursor.executemany('INSERT INTO places (name, description, price, image_url) VALUES (?, ?, ?, ?)', places)

        db.commit()

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to require admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM places')
    places = cursor.fetchall()
    return render_template('index.html', places=places)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/book/<int:place_id>', methods=['GET', 'POST'])
@login_required
def book(place_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM places WHERE id = ?', (place_id,))
    place = cursor.fetchone()
    
    if not place:
        flash('Place not found.', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        date = request.form['date']
        
        cursor.execute('INSERT INTO bookings (user_id, place_id, booking_date, status) VALUES (?, ?, ?, ?)',
                      (session['user_id'], place_id, date, 'Pending Payment'))
        db.commit()
        booking_id = cursor.lastrowid
        return redirect(url_for('payment', booking_id=booking_id))
        
    return render_template('booking.html', place=place)

@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def payment(booking_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT b.id, b.booking_date, p.name, p.price 
        FROM bookings b 
        JOIN places p ON b.place_id = p.id 
        WHERE b.id = ? AND b.user_id = ?
    ''', (booking_id, session['user_id']))
    booking = cursor.fetchone()
    
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('history'))
        
    if request.method == 'POST':
        # Simulate payment success
        cursor.execute("UPDATE bookings SET status = 'Confirmed' WHERE id = ?", (booking_id,))
        db.commit()
        flash('Payment successful! Booking confirmed.', 'success')
        return redirect(url_for('history'))
        
    return render_template('payment.html', booking=booking)

@app.route('/history')
@login_required
def history():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT b.id, p.name, p.price, b.booking_date, b.status 
        FROM bookings b 
        JOIN places p ON b.place_id = p.id 
        WHERE b.user_id = ?
        ORDER BY b.id DESC
    ''', (session['user_id'],))
    bookings = cursor.fetchall()
    return render_template('history.html', bookings=bookings)

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_place':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            image_url = request.form['image_url']
            cursor.execute('INSERT INTO places (name, description, price, image_url) VALUES (?, ?, ?, ?)',
                          (name, description, price, image_url))
            db.commit()
            flash('Place added successfully.', 'success')
            
        elif action == 'delete_place':
            place_id = request.form['place_id']
            cursor.execute('DELETE FROM places WHERE id = ?', (place_id,))
            db.commit()
            flash('Place deleted.', 'success')
            
        elif action == 'update_booking':
            booking_id = request.form['booking_id']
            status = request.form['status']
            cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', (status, booking_id))
            db.commit()
            flash('Booking updated.', 'success')
            
        return redirect(url_for('admin'))
        
    cursor.execute('SELECT * FROM places')
    places = cursor.fetchall()
    
    cursor.execute('''
        SELECT b.id, u.username, p.name, b.booking_date, b.status 
        FROM bookings b 
        JOIN users u ON b.user_id = u.id 
        JOIN places p ON b.place_id = p.id
        ORDER BY b.id DESC
    ''')
    bookings = cursor.fetchall()
    
    return render_template('admin.html', places=places, bookings=bookings)

if __name__ == '__main__':
    # Initializing DB before starting the server
    with app.app_context():
        init_db()
    # To run on VS Code (locally) typically we just use app.run()
    app.run(debug=True, port=5000)