# # config.py
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     # Database
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#     # Security
#     SECRET_KEY = os.environ.get('SECRET_KEY')
#     SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'default-salt-change-me')
    
#     # =============================================
#     # EMAIL CONFIGURATION
#     # =============================================
#     MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
#     MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
#     MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
#     MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    
#     # Sender email - BETSONLEARNING
#     MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'betsonlearning2025@gmail.com')
#     MAIL_PASSWORD = os.environ.get('tlik afzr roia qtrk')  # App Password
#     MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)




# config.py
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'default-salt-change-me')
    
    # =============================================
    # EMAIL CONFIGURATION
    # =============================================
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    
    # Sender email - BETSONLEARNING
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    
    # Debug - Print email config (only in development)
    if os.environ.get('FLASK_ENV') != 'production':
        print(f"📧 [Config] MAIL_USERNAME: {MAIL_USERNAME}")
        print(f"🔑 [Config] MAIL_PASSWORD: {'*' * len(MAIL_PASSWORD) if MAIL_PASSWORD else 'NOT SET'}")