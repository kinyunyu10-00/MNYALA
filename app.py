from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_migrate import Migrate

from extensions import db
from config import Config
from routes.auth import auth
from routes.public import public
from routes.admin import admin

app = Flask(__name__)
app.config.from_object(Config)

if not app.config.get("SECRET_KEY") or not app.config.get("SQLALCHEMY_DATABASE_URI"):
    raise RuntimeError(
        "SECRET_KEY and DATABASE_URL must be set in your .env file. "
        "Copy .env.example to .env and fill in real values."
    )

db.init_app(app)
migrate = Migrate(app, db)


@app.context_processor
def inject_unread_messages():
    from flask import session

    if "user_id" not in session:
        return {}

    from models import Message

    return {
        "unread_messages": Message.query.filter_by(is_read=False).count()
    }


app.register_blueprint(public)
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(admin, url_prefix="/admin")

if __name__ == "__main__":
    app.run(debug=True)