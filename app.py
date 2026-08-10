from flask import Flask
from flask_migrate import Migrate
from extensions import db
from routes.auth import auth
from routes.public import public
from routes.admin import admin

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:56789@localhost:5432/mnyala_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your_secret_key"

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(public)
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(admin, url_prefix="/admin")

if __name__ == "__main__":
    app.run(debug=True)