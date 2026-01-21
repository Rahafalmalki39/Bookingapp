from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from google.cloud import firestore
import bcrypt
import os
from datetime import datetime, timedelta
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Firestore client
db = firestore.Client(database='bookit-db')

# Collections
USERS_COLLECTION = 'users'
EVENTS_COLLECTION = 'events'
BOOKINGS_COLLECTION = 'bookings'

# Helper Functions
def hash_password(password):
    """Hash a password for storing"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_ref = db.collection(USERS_COLLECTION).document(session['user_id'])
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'admin':
            return "Unauthorized", 403
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page - display all events"""
    events_ref = db.collection(EVENTS_COLLECTION)
    events = []
    for doc in events_ref.stream():
        event_data = doc.to_dict()
        event_data['id'] = doc.id
        events.append(event_data)
    
    user_data = None
    if 'user_id' in session:
        user_ref = db.collection(USERS_COLLECTION).document(session['user_id'])
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
    
    return render_template('index.html', events=events, user=user_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role', 'customer')  # default to customer
        
        # Check if user already exists
        users_ref = db.collection(USERS_COLLECTION)
        existing_user = users_ref.where('email', '==', email).limit(1).get()
        
        if len(list(existing_user)) > 0:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        hashed_pw = hash_password(password)
        user_data = {
            'email': email,
            'password': hashed_pw,
            'name': name,
            'role': role,
            'created_at': datetime.now()
        }
        
        new_user_ref = users_ref.document()
        new_user_ref.set(user_data)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user by email
        users_ref = db.collection(USERS_COLLECTION)
        users = users_ref.where('email', '==', email).limit(1).get()
        
        user_list = list(users)
        if len(user_list) == 0:
            flash('Invalid credentials', 'error')
            return render_template('login.html')
        
        user_doc = user_list[0]
        user_data = user_doc.to_dict()
        
        # Verify password
        if verify_password(password, user_data['password']):
            session['user_id'] = user_doc.id
            session['user_email'] = user_data['email']
            session['user_role'] = user_data['role']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/events')
def events():
    """Display all events"""
    events_ref = db.collection(EVENTS_COLLECTION)
    events_list = []
    for doc in events_ref.stream():
        event_data = doc.to_dict()
        event_data['id'] = doc.id
        events_list.append(event_data)
    
    return render_template('events.html', events=events_list)

@app.route('/event/<event_id>')
def event_detail(event_id):
    """Display single event details"""
    event_ref = db.collection(EVENTS_COLLECTION).document(event_id)
    event_doc = event_ref.get()
    
    if not event_doc.exists:
        return "Event not found", 404
    
    event_data = event_doc.to_dict()
    event_data['id'] = event_doc.id
    
    return render_template('event_detail.html', event=event_data)

@app.route('/book/<event_id>', methods=['POST'])
@login_required
def book_event(event_id):
    """Book an event"""
    event_ref = db.collection(EVENTS_COLLECTION).document(event_id)
    event_doc = event_ref.get()
    
    if not event_doc.exists:
        return "Event not found", 404
    
    event_data = event_doc.to_dict()
    tickets_requested = int(request.form.get('tickets', 1))
    
    # Check availability
    if event_data.get('available_seats', 0) < tickets_requested:
        flash('Not enough seats available', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Create booking
    booking_data = {
        'user_id': session['user_id'],
        'event_id': event_id,
        'event_name': event_data['name'],
        'tickets': tickets_requested,
        'total_price': event_data['price'] * tickets_requested,
        'booking_date': datetime.now(),
        'status': 'confirmed'
    }
    
    bookings_ref = db.collection(BOOKINGS_COLLECTION)
    bookings_ref.add(booking_data)
    
    # Update available seats
    new_seats = event_data['available_seats'] - tickets_requested
    event_ref.update({'available_seats': new_seats})
    
    flash(f'Successfully booked {tickets_requested} ticket(s)!', 'success')
    return redirect(url_for('my_bookings'))

@app.route('/my-bookings')
@login_required
def my_bookings():
    """Display user's bookings"""
    bookings_ref = db.collection(BOOKINGS_COLLECTION)
    bookings = bookings_ref.where('user_id', '==', session['user_id']).stream()
    
    bookings_list = []
    for doc in bookings:
        booking_data = doc.to_dict()
        booking_data['id'] = doc.id
        bookings_list.append(booking_data)
    
    return render_template('my_bookings.html', bookings=bookings_list)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    events_count = len(list(db.collection(EVENTS_COLLECTION).stream()))
    bookings_count = len(list(db.collection(BOOKINGS_COLLECTION).stream()))
    users_count = len(list(db.collection(USERS_COLLECTION).stream()))
    
    return render_template('admin_dashboard.html', 
                         events_count=events_count,
                         bookings_count=bookings_count,
                         users_count=users_count)

@app.route('/admin/create-event', methods=['GET', 'POST'])
@admin_required
def create_event():
    """Create new event"""
    if request.method == 'POST':
        event_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'date': request.form.get('date'),
            'time': request.form.get('time'),
            'venue': request.form.get('venue'),
            'price': float(request.form.get('price')),
            'total_seats': int(request.form.get('total_seats')),
            'available_seats': int(request.form.get('total_seats')),
            'category': request.form.get('category'),
            'created_at': datetime.now(),
            'created_by': session['user_id']
        }
        
        db.collection(EVENTS_COLLECTION).add(event_data)
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_event.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)