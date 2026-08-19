import os   

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:56789@localhost:5432/mnyala_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "mysecretkey"
