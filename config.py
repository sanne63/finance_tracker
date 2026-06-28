import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'finance-tracker-very-secret-key-12345')
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finance.db')