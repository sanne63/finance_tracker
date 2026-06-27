import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'finance-tracker-very-secret-key-123456')
    
    # MySQL Database connection configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'finance_tracker')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # Optional fallback behavior (if MySQL connection fails, can fall back to SQLite for testing)
    # We will prioritize MySQL as requested by the user.
