from google.cloud.sql.connector import Connector
import pg8000
import sqlalchemy

def init_connection_pool():
    """Initialize connection pool for Cloud SQL"""
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

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool

def create_tables(pool):
    """Create necessary tables in Cloud SQL"""
    create_bookings_table = """
    CREATE TABLE IF NOT EXISTS bookings (
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
    """
    
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        booking_id INTEGER REFERENCES bookings(id),
        amount DECIMAL(10, 2) NOT NULL,
        payment_method VARCHAR(100),
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'completed'
    );
    """
    
    with pool.connect() as conn:
        conn.execute(sqlalchemy.text(create_bookings_table))
        conn.execute(sqlalchemy.text(create_transactions_table))
        conn.commit()
    
    print("✅ Tables created successfully!")

if __name__ == '__main__':
    pool = init_connection_pool()
    create_tables(pool)
    print("Database initialization complete!")