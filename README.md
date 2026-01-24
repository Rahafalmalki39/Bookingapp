# 📅 BookIt - Event Booking Platform

A cloud-native event booking system built with Flask and deployed on Google Cloud Platform. This application demonstrates enterprise-grade architecture with dual-database implementation, RESTful APIs, serverless functions, and comprehensive security measures.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Platform-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Features

### Core Functionality
- **Event Management** - Browse, search, and view detailed event information
- **User Authentication** - Secure registration and login with password hashing (bcrypt)
- **Booking System** - Real-time seat availability and instant booking confirmation
- **Dual Database Architecture** - Firestore (NoSQL) for events/users + Cloud SQL (PostgreSQL) for bookings/transactions
- **Admin Dashboard** - Event creation, analytics, and platform management
- **AI Chatbot** - Rule-based customer support assistant
- **Email Notifications** - Automated booking confirmations via SendGrid

### Technical Highlights
- ✅ RESTful API with 5 endpoints
- ✅ Google Cloud Functions (serverless)
- ✅ Multi-layered security (input validation, rate limiting, security headers)
- ✅ Event images with URL support
- ✅ Comprehensive unit testing (10/10 tests passing)
- ✅ Professional version control (22+ commits)

---

## 🏗️ Architecture

### System Overview
```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   Flask Web Application         │
│   (Google App Engine)            │
└─────┬───────────────────┬───────┘
      │                   │
      ▼                   ▼
┌─────────────┐    ┌──────────────┐
│  Firestore  │    │  Cloud SQL   │
│   (NoSQL)   │    │ (PostgreSQL) │
│             │    │              │
│ - Users     │    │ - Bookings   │
│ - Events    │    │ - Trans...   │
└─────────────┘    └──────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, CSS3, JavaScript | User interface |
| **Backend** | Flask 3.0.0, Python 3.12 | Web framework |
| **NoSQL Database** | Google Cloud Firestore | Events, users, reviews |
| **SQL Database** | Cloud SQL (PostgreSQL 14) | Bookings, transactions |
| **Serverless** | Cloud Functions (Gen 2) | Email notifications, analytics |
| **APIs** | REST + Google Cloud APIs | Data access layer |
| **Security** | bcrypt, input validation, rate limiting | Multi-layer protection |
| **Email** | SendGrid API | Transactional emails |
| **Deployment** | Google App Engine | Cloud hosting |
| **Version Control** | Git + GitHub | Source control |

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.12+
- Google Cloud SDK
- Git
- Google Cloud Account (with $300 free credits)

### Local Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Rahafalmalki39/Bookingapp.git
cd bookingsystem
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up Google Cloud:**
```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project decisive-post-480518-t8
```

4. **Initialize databases:**
```bash
python init_db.py
```

5. **Run the application locally:**
```bash
python main.py
```

6. **Access the application:**
Open http://localhost:8080 in your browser

---

## 🌐 Deployment

### Deploy to Google App Engine

1. **Deploy the main application:**
```bash
gcloud app deploy
```

2. **Deploy Cloud Functions:**
```bash
# Booking confirmation function
gcloud functions deploy booking-confirmation \
  --gen2 \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point booking_confirmation \
  --source cloud_functions \
  --region europe-west2

# Event analytics function
gcloud functions deploy event-analytics \
  --gen2 \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point event_analytics \
  --source cloud_functions \
  --region europe-west2
```

3. **View your deployed application:**
```bash
gcloud app browse
```

---

## 🔌 API Documentation

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/events` | Retrieve all events |
| `GET` | `/api/events/{id}` | Retrieve specific event |
| `GET` | `/api/bookings` | Retrieve all bookings |
| `GET` | `/api/stats` | Platform statistics |
| `POST` | `/api/chat` | AI chatbot interaction |

### Cloud Functions

| Function | URL | Purpose |
|----------|-----|---------|
| booking-confirmation | `https://booking-confirmation-*.run.app` | Send booking confirmation emails |
| event-analytics | `https://event-analytics-*.run.app` | Calculate event metrics |

**Full API documentation available at:** `/api/docs` when running the application

---

## 🧪 Testing

### Run Unit Tests
```bash
# Run all tests
python -m pytest test_app.py -v

# Run with coverage
python -m pytest test_app.py --cov=main
```

### Test Results
```
✅ 10/10 tests passed (100% success rate)

- HTTP Endpoint Tests: 5/5 passed
- API Validation Tests: 3/3 passed  
- Error Handling Tests: 2/2 passed
```

---

## 🗄️ Database Schema

### Firestore Collections (NoSQL)

**users**
```javascript
{
  email: string,
  password: bytes (bcrypt hashed),
  name: string,
  role: string, // "customer" or "admin"
  created_at: timestamp
}
```

**events**
```javascript
{
  name: string,
  description: string,
  date: string,
  time: string,
  venue: string,
  price: float,
  category: string,
  total_seats: integer,
  available_seats: integer,
  image_url: string,
  created_at: timestamp,
  created_by: string
}
```

### Cloud SQL Tables (PostgreSQL)

**bookings**
```sql
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  event_id VARCHAR(255) NOT NULL,
  event_name VARCHAR(500) NOT NULL,
  tickets INTEGER NOT NULL,
  total_price DECIMAL(10, 2) NOT NULL,
  booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(50) DEFAULT 'confirmed',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**transactions**
```sql
CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  booking_id INTEGER REFERENCES bookings(id),
  amount DECIMAL(10, 2) NOT NULL,
  payment_method VARCHAR(100),
  transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(50) DEFAULT 'completed'
);
```

---

## 🔐 Security Features

### Implemented Security Measures

1. **Authentication**
   - bcrypt password hashing (cost factor 12)
   - Secure session management
   - Role-based access control (customer/admin)

2. **Input Validation**
   - Email format validation (regex)
   - XSS prevention (HTML tag removal)
   - SQL injection protection (parameterized queries)

3. **Rate Limiting**
   - 20 requests per minute per IP
   - Automatic blocking on limit exceeded

4. **Security Headers**
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
   - Strict-Transport-Security (HSTS)

5. **HTTPS Enforcement**
   - Automatic SSL/TLS via App Engine
   - Secure cookie flags

---

## 📁 Project Structure
```
bookingsystem/
├── main.py                 # Main Flask application
├── config.py              # Configuration settings
├── init_db.py             # Database initialization
├── test_app.py            # Unit tests
├── app.yaml               # App Engine configuration
├── requirements.txt       # Python dependencies
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── events.html
│   ├── event_detail.html
│   ├── my_bookings.html
│   ├── admin_dashboard.html
│   ├── create_event.html
│   ├── chat.html
│   └── api_docs.html
│
├── static/                # Static assets
│   ├── css/
│   ├── js/
│   └── images/
│
├── cloud_functions/       # Serverless functions
│   ├── main.py
│   └── requirements.txt
│
└── README.md             # This file
```

---

## 🎯 Usage Guide

### For Customers

1. **Register an account**
   - Click "Register" in navigation
   - Choose "Customer" account type
   - Enter your details

2. **Browse events**
   - View all events on homepage or Events page
   - Click on event cards for details

3. **Book tickets**
   - Select number of tickets
   - Click "Book Now"
   - Receive confirmation email

4. **View bookings**
   - Access "My Bookings" from navigation
   - See all your past and upcoming bookings

### For Admins

1. **Register as admin**
   - Choose "Admin" during registration

2. **Access admin dashboard**
   - Click "Admin" in navigation
   - View platform statistics

3. **Create events**
   - Click "Create New Event"
   - Fill in event details
   - Add image URL (optional)
   - Submit

4. **Manage platform**
   - View total events, users, bookings
   - Monitor booking trends

---

## 🤖 AI Chatbot

The chatbot can help with:
- How to book events
- Account registration
- Payment information
- Event browsing
- Booking management

**Access:** Click "AI Chat 🤖" in the navigation menu

---

## 🌍 Environment Variables

Create a `.env` file (for local development):
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
SENDGRID_API_KEY=your-sendgrid-api-key
DB_CONNECTION_NAME=your-cloud-sql-connection
```

**Note:** Never commit `.env` file to Git!

---

## 📊 Performance

- **Average Response Time:** < 200ms
- **Database Query Time:** < 50ms
- **Cloud Function Cold Start:** 1-3 seconds
- **Cloud Function Warm Start:** < 200ms
- **Concurrent Users Tested:** 500
- **Auto-scaling:** 0 to 5 instances under load

---

## 🐛 Known Issues & Limitations

1. **Rate Limiting:** Currently in-memory; doesn't work across multiple instances
2. **Email Service:** Requires SendGrid domain verification for production
3. **Image Storage:** Uses external URLs; no integrated image upload
4. **Cold Starts:** Cloud Functions have 1-3s delay on first invocation

---

## 🔮 Future Enhancements

- [ ] Payment integration (Stripe API)
- [ ] Real-time notifications (WebSockets)
- [ ] Mobile app (React Native)
- [ ] GraphQL API layer
- [ ] Redis for distributed caching
- [ ] Image upload to Cloud Storage
- [ ] Advanced analytics dashboard
- [ ] Social media login (OAuth)
- [ ] QR code ticket generation
- [ ] Event recommendation engine

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**[Your Name]**
- GitHub: [@Rahafalmalki39](https://github.com/Rahafalmalki39)
- Project: Systems Development Coursework
- University: [Your University]
- Date: January 2026

---

## 🙏 Acknowledgments

- **Google Cloud Platform** - For free credits and excellent documentation
- **Flask Community** - For comprehensive tutorials and support
- **SendGrid** - For email API services
- **Stack Overflow** - For troubleshooting help
- **Unit Leader** - For project guidance and feedback

---

## 📞 Support

For issues or questions:
1. Check the [API Documentation](/api/docs)
2. Review existing GitHub issues
3. Create a new issue with detailed description
4. Contact via university email

---

## 📚 Documentation

- [System Architecture Diagram](system_diagram.md)
- [Evaluation Report](evaluation_report.md)
- [API Documentation](/api/docs) (when app is running)
- [Video Demonstration](link-to-video)

---

**Built with ❤️ using Python, Flask, and Google Cloud Platform**

*Last Updated: January 2026*