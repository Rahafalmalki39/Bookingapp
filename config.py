import os

# Cloud SQL Configuration
DB_USER = 'postgres'
DB_PASSWORD = 'BookitDB2025!'
DB_NAME = 'bookit_bookings'
DB_CONNECTION_NAME = 'decisive-post-480518-t8:europe-west2:bookit-db-instance'

# Firestore Configuration
FIRESTORE_DATABASE = 'bookit-db'

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Google Gemini AI Configuration
GEMINI_API_KEY = 'AIzaSyBiYB5Qh6p2-DWCXf4LMwUALvF3zf7iwcs'