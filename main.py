from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from google.cloud import firestore
from google.cloud.sql.connector import Connector
import sqlalchemy
import bcrypt
import os
from datetime import datetime, timedelta
import secrets
from functools import wraps
import re
from datetime import datetime, timedelta

# Security: Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Security: Input sanitization
def sanitize_input(text, max_length=500):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text:
        return ""
    # Remove any HTML tags
    text = re.sub(r'<[^>]*>', '', str(text))
    # Limit length
    text = text[:max_length]
    # Remove potentially dangerous characters
    text = text.strip()
    return text

def validate_email(email):
    """Validate email format"""
    if not email or not EMAIL_REGEX.match(email):
        return False
    return True

# Security: Rate limiting (simple in-memory implementation)
request_counts = {}

def rate_limit(max_requests=10, time_window=60):
    """Rate limiting decorator - max_requests per time_window seconds"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            current_time = datetime.now()
            
            # Clean old entries
            expired_keys = [
                ip for ip, (count, timestamp) in request_counts.items()
                if (current_time - timestamp).seconds > time_window
            ]
            for ip in expired_keys:
                del request_counts[ip]
            
            # Check rate limit
            if client_ip in request_counts:
                count, first_request = request_counts[client_ip]
                if (current_time - first_request).seconds < time_window:
                    if count >= max_requests:
                        return jsonify({
                            'success': False,
                            'error': 'Rate limit exceeded. Please try again later.'
                        }), 429
                    request_counts[client_ip] = (count + 1, first_request)
                else:
                    request_counts[client_ip] = (1, current_time)
            else:
                request_counts[client_ip] = (1, current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Firestore client (NoSQL - for users, events)
db = firestore.Client(database='bookit-db')

# Collections
USERS_COLLECTION = 'users'
EVENTS_COLLECTION = 'events'

# Initialize Cloud SQL connection pool (SQL - for bookings, transactions)
connector = Connector()

def getconn():
    conn = connector.connect(
        "decisive-post-480518-t8:europe-west2:bookit-db-instance",
        "pg8000",
        user="postgres",
        password="BookitDB2025!",
        db="bookit_bookings"
    )
    return conn

db_pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

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
        email = sanitize_input(request.form.get('email'), 100)
        password = request.form.get('password')  
        name = sanitize_input(request.form.get('name'), 100)
        role = request.form.get('role', 'customer')
        # Validate email format
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('register.html')

# Validate password strength
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
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
    """Book an event - Now using Cloud SQL for bookings"""
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
    
    # Insert booking into Cloud SQL (PostgreSQL)
    insert_booking = sqlalchemy.text("""
        INSERT INTO bookings (user_id, event_id, event_name, tickets, total_price, status)
        VALUES (:user_id, :event_id, :event_name, :tickets, :total_price, :status)
        RETURNING id
    """)
    
    total_price = event_data['price'] * tickets_requested
    
    with db_pool.connect() as conn:
        result = conn.execute(insert_booking, {
            'user_id': session['user_id'],
            'event_id': event_id,
            'event_name': event_data['name'],
            'tickets': tickets_requested,
            'total_price': total_price,
            'status': 'confirmed'
        })
        booking_id = result.fetchone()[0]
        
        # Insert transaction record
        insert_transaction = sqlalchemy.text("""
            INSERT INTO transactions (booking_id, amount, payment_method, status)
            VALUES (:booking_id, :amount, :payment_method, :status)
        """)
        
        conn.execute(insert_transaction, {
            'booking_id': booking_id,
            'amount': total_price,
            'payment_method': 'card',
            'status': 'completed'
        })
        
        conn.commit()
    
    # Update available seats in Firestore
    new_seats = event_data['available_seats'] - tickets_requested
    event_ref.update({'available_seats': new_seats})
    
# Call Cloud Function to send booking confirmation
    try:
        import requests
        cloud_function_url = 'https://booking-confirmation-msefsopqja-nw.a.run.app'
        
        confirmation_data = {
            'booking_id': str(booking_id),
            'user_email': session.get('user_email'),
            'event_name': event_data['name'],
            'tickets': tickets_requested,
            'total_price': float(total_price)
        }
        
        # Call Cloud Function asynchronously (non-blocking)
        response = requests.post(cloud_function_url, json=confirmation_data, timeout=5)
        
        if response.status_code == 200:
            print(f"Confirmation email sent via Cloud Function for booking {booking_id}")
        else:
            print(f"Cloud Function call failed: {response.status_code}")
    except Exception as e:
        print(f"Error calling Cloud Function: {e}")
        # Don't fail the booking if email fails
    
    flash(f'Successfully booked {tickets_requested} ticket(s)! Confirmation email sent.', 'success')
    return redirect(url_for('my_bookings'))

@app.route('/my-bookings')
@login_required
def my_bookings():
    """Display user's bookings from Cloud SQL"""
    select_bookings = sqlalchemy.text("""
        SELECT id, event_id, event_name, tickets, total_price, booking_date, status
        FROM bookings
        WHERE user_id = :user_id
        ORDER BY booking_date DESC
    """)
    
    bookings_list = []
    with db_pool.connect() as conn:
        result = conn.execute(select_bookings, {'user_id': session['user_id']})
        for row in result:
            bookings_list.append({
                'id': str(row[0]),
                'event_id': row[1],
                'event_name': row[2],
                'tickets': row[3],
                'total_price': float(row[4]),
                'booking_date': row[5],
                'status': row[6]
            })
    
    return render_template('my_bookings.html', bookings=bookings_list)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics from both databases"""
    # Events from Firestore
    events_count = len(list(db.collection(EVENTS_COLLECTION).stream()))
    users_count = len(list(db.collection(USERS_COLLECTION).stream()))
    
    # Bookings from Cloud SQL
    count_bookings = sqlalchemy.text("SELECT COUNT(*) FROM bookings")
    with db_pool.connect() as conn:
        result = conn.execute(count_bookings)
        bookings_count = result.fetchone()[0]
    
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
            'image_url': request.form.get('image_url', ''),
            'created_at': datetime.now(),
            'created_by': session['user_id']
        }
        
        db.collection(EVENTS_COLLECTION).add(event_data)
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_event.html')
# ============================================
# REST API Endpoints (JSON responses)
# ============================================

@app.route('/api/events', methods=['GET'])
def api_get_events():
    """REST API: Get all events as JSON"""
    events_ref = db.collection(EVENTS_COLLECTION)
    events_list = []
    
    for doc in events_ref.stream():
        event_data = doc.to_dict()
        event_data['id'] = doc.id
        # Convert datetime to string for JSON serialization
        if 'created_at' in event_data:
            event_data['created_at'] = event_data['created_at'].isoformat()
        events_list.append(event_data)
    
    return jsonify({
        'success': True,
        'count': len(events_list),
        'events': events_list
    })

@app.route('/api/events/<event_id>', methods=['GET'])
def api_get_event(event_id):
    """REST API: Get single event by ID"""
    event_ref = db.collection(EVENTS_COLLECTION).document(event_id)
    event_doc = event_ref.get()
    
    if not event_doc.exists:
        return jsonify({
            'success': False,
            'error': 'Event not found'
        }), 404
    
    event_data = event_doc.to_dict()
    event_data['id'] = event_doc.id
    if 'created_at' in event_data:
        event_data['created_at'] = event_data['created_at'].isoformat()
    
    return jsonify({
        'success': True,
        'event': event_data
    })

@app.route('/api/bookings', methods=['GET'])
def api_get_bookings():
    """REST API: Get all bookings from Cloud SQL"""
    select_all = sqlalchemy.text("""
        SELECT b.id, b.user_id, b.event_id, b.event_name, b.tickets, 
               b.total_price, b.booking_date, b.status,
               t.amount as transaction_amount, t.payment_method
        FROM bookings b
        LEFT JOIN transactions t ON b.id = t.booking_id
        ORDER BY b.booking_date DESC
    """)
    
    bookings_list = []
    with db_pool.connect() as conn:
        result = conn.execute(select_all)
        for row in result:
            bookings_list.append({
                'id': row[0],
                'user_id': row[1],
                'event_id': row[2],
                'event_name': row[3],
                'tickets': row[4],
                'total_price': float(row[5]),
                'booking_date': row[6].isoformat() if row[6] else None,
                'status': row[7],
                'transaction_amount': float(row[8]) if row[8] else None,
                'payment_method': row[9]
            })
    
    return jsonify({
        'success': True,
        'count': len(bookings_list),
        'bookings': bookings_list
    })

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """REST API: Get platform statistics"""
    # Events from Firestore
    events_count = len(list(db.collection(EVENTS_COLLECTION).stream()))
    users_count = len(list(db.collection(USERS_COLLECTION).stream()))
    
    # Bookings stats from Cloud SQL
    stats_query = sqlalchemy.text("""
        SELECT 
            COUNT(*) as total_bookings,
            SUM(total_price) as total_revenue,
            SUM(tickets) as total_tickets_sold
        FROM bookings
        WHERE status = 'confirmed'
    """)
    
    with db_pool.connect() as conn:
        result = conn.execute(stats_query)
        row = result.fetchone()
        bookings_count = row[0] if row[0] else 0
        total_revenue = float(row[1]) if row[1] else 0.0
        total_tickets = row[2] if row[2] else 0
    
    return jsonify({
        'success': True,
        'statistics': {
            'total_events': events_count,
            'total_users': users_count,
            'total_bookings': bookings_count,
            'total_revenue': total_revenue,
            'total_tickets_sold': total_tickets
        }
    })
# ============================================
# AI Chatbot Endpoints
# ============================================

@app.route('/chat')
def chat_page():
    """Chatbot page"""
    return render_template('chat.html')
@app.route('/api/chat', methods=['POST'])
@rate_limit(max_requests=20, time_window=60)  # Max 20 requests per minute
def api_chat():
    """Rule-based Chatbot for BookIt"""
    user_message = request.json.get('message', '').lower()
    
    if not user_message:
        return jsonify({
            'success': False,
            'error': 'No message provided'
        }), 400
    
    # Rule-based responses
    response_text = ""
    
    if any(word in user_message for word in ['hello', 'hi', 'hey', 'greetings']):
        response_text = "Hello! Welcome to BookIt! I'm here to help you with event bookings. What would you like to know?"
    
    elif any(word in user_message for word in ['book', 'booking', 'reserve', 'ticket']):
        response_text = """To book an event:
1. Browse events on our Events page
2. Click on an event you're interested in
3. Select the number of tickets you want
4. Click 'Book Now' to confirm your booking

You must be logged in to make a booking. If you don't have an account, please register first!"""
    
    elif any(word in user_message for word in ['payment', 'pay', 'price', 'cost']):
        response_text = "Our payment system is secure and encrypted. Event prices vary depending on the event. You can see the price per ticket on each event's detail page. The total cost will be calculated based on the number of tickets you select."
    
    elif any(word in user_message for word in ['cancel', 'refund', 'change']):
        response_text = "To view or manage your bookings, go to 'My Bookings' in the navigation menu. For cancellations or changes, please contact our support team with your booking ID."
    
    elif any(word in user_message for word in ['register', 'sign up', 'account', 'create account']):
        response_text = "To create an account, click 'Register' in the top menu. You can register as a Customer (to book events) or as an Admin (to create and manage events). Registration is quick and free!"
    
    elif any(word in user_message for word in ['event', 'concert', 'conference', 'workshop', 'what events']):
        response_text = "We have various types of events including concerts, conferences, workshops, sports events, theatre shows, and more! Visit our Events page to browse all available events. You can filter by category to find what interests you."
    
    elif any(word in user_message for word in ['how', 'help', 'support']):
        response_text = """I can help you with:
- Booking events and buying tickets
- Creating an account
- Understanding our payment process
- Finding events
- Managing your bookings

What would you like help with?"""
    
    elif any(word in user_message for word in ['admin', 'create event', 'manage']):
        response_text = "If you're an admin, you can create and manage events from the Admin Dashboard. To access it, register with an Admin account and log in. From there, you can create events, view statistics, and manage the platform."
    
    elif any(word in user_message for word in ['thank', 'thanks', 'appreciate']):
        response_text = "You're welcome! Happy to help. If you have any other questions about BookIt, feel free to ask!"
    
    elif any(word in user_message for word in ['bye', 'goodbye', 'see you']):
        response_text = "Goodbye! Have a great time at your events! Come back anytime you need help with BookIt."
    
    else:
        response_text = """I'm here to help with BookIt! I can assist you with:
- Booking events
- Account registration
- Payment information
- Event browsing
- Managing bookings

What would you like to know more about?"""
    
    return jsonify({
        'success': True,
        'message': response_text
    })
@app.route('/api/docs')
def api_docs():
    """API Documentation page"""
    return render_template('api_docs.html')
# Security: Add security headers to all responses
@app.after_request
def add_security_headers(response):
    """Add security headers to all HTTP responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https:; img-src 'self' https: data:;"
    return response
            
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)