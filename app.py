from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from flask import Flask, render_template
from flask_migrate import Migrate

from extensions import db, mail
from config import Config
from routes.auth import auth
from routes.public import public
from routes.admin import admin

app = Flask(__name__)
app.config.from_object(Config)

# =============================================
# CHECK CRITICAL CONFIGURATIONS
# =============================================
if not app.config.get("SECRET_KEY") or not app.config.get("SQLALCHEMY_DATABASE_URI"):
    raise RuntimeError(
        "SECRET_KEY and DATABASE_URL must be set in your .env file. "
        "Copy .env.example to .env and fill in real values."
    )

# =============================================
# CHECK EMAIL CONFIGURATION (Warning only)
# =============================================
if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
    print("⚠️  WARNING: Email configuration is not set!")
    print("   MAIL_USERNAME and MAIL_PASSWORD must be set in .env")
    print("   Password reset functionality will not work!")
else:
    print("✅ Email configuration found:")
    print(f"   MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"   MAIL_PASSWORD: {'*' * len(app.config.get('MAIL_PASSWORD', ''))}")
    print(f"   MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"   MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"   MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")

# =============================================
# INITIALIZE EXTENSIONS
# =============================================
db.init_app(app)
mail.init_app(app) 
migrate = Migrate(app, db)


# =============================================
# CONTEXT PROCESSOR - Unread Messages
# =============================================
@app.context_processor
def inject_unread_messages():
    from flask import session

    if "user_id" not in session:
        return {}

    from models import Message

    try:
        unread_count = Message.query.filter_by(is_read=False).count()
        return {"unread_messages": unread_count}
    except Exception:
        return {"unread_messages": 0}


# =============================================
# ERROR HANDLERS
# =============================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html"), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403


# =============================================
# REGISTER BLUEPRINTS
# =============================================
app.register_blueprint(public)
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(admin, url_prefix="/admin")


# =============================================
# TEST EMAIL FUNCTION (Optional - Development)
# =============================================
@app.cli.command("test-email")
def test_email():
    """Test email configuration by sending a test email."""
    from flask_mail import Message
    import os
    
    print("=" * 60)
    print("TESTING EMAIL CONFIGURATION")
    print("=" * 60)
    
    # Check if email is configured
    if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
        print("❌ Email not configured! Set MAIL_USERNAME and MAIL_PASSWORD in .env")
        return
    
    print(f"📧 From: {app.config.get('MAIL_USERNAME')}")
    print(f"📧 To: {app.config.get('MAIL_USERNAME')} (sending to self)")
    print(f"🔧 Server: {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')}")
    print("-" * 60)
    
    try:
        msg = Message(
            subject="Test Email from MNYALA System",
            recipients=[app.config.get('MAIL_USERNAME')],
            body=f"""
            This is a test email from MNYALA Business Management System.
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Server: {app.config.get('MAIL_SERVER')}
            Port: {app.config.get('MAIL_PORT')}
            TLS: {app.config.get('MAIL_USE_TLS')}
            
            If you received this email, your email configuration is working correctly!
            """
        )
        mail.send(msg)
        print("✅ Test email sent successfully!")
        print("   Check your inbox for the test email.")
    except Exception as e:
        print(f"❌ Failed to send test email: {str(e)}")
        print("\n🔍 Troubleshooting tips:")
        print("   1. Check if MAIL_PASSWORD is the App Password (not your regular password)")
        print("   2. Verify 2-Step Verification is enabled on your Google account")
        print("   3. Check if App Password was generated for 'Mail' app")
        print("   4. Try generating a new App Password at: https://myaccount.google.com/apppasswords")


# =============================================
# DEVELOPMENT SERVER
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MNYALA BUSINESS MANAGEMENT SYSTEM")
    print("=" * 60)
    print(f"🔗 Server URL: http://127.0.0.1:5000")
    print(f"📧 Email: {'✅ Configured' if app.config.get('MAIL_USERNAME') else '❌ Not Configured'}")
    print("=" * 60)
    
    app.run(debug=True)