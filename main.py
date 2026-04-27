from flask import Flask
from flask_cors import CORS
from config import DEBUG, PORT, HOST, SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT

# Import database initializers
from database.user_db import init_user_db
from database.vehicle_db import init_vehicle_db
from database.schedule_db import init_schedule_db

# Import route blueprints
from routes.auth import auth_bp
from routes.users import users_bp
from routes.vehicles import vehicles_bp
from routes.schedules import schedules_bp
from routes.home import home_bp

from utils.verification import mail

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Register config for verification code
app.config['MAIL_SERVER'] = SMTP_SERVER
app.config['MAIL_PORT'] = SMTP_PORT
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = SENDER_EMAIL
app.config['MAIL_PASSWORD'] = SENDER_PASSWORD # Must be a 16-character App Password
app.config['MAIL_DEFAULT_SENDER'] = SENDER_EMAIL

# Register blueprints (route groups)
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(vehicles_bp)
app.register_blueprint(schedules_bp)
app.register_blueprint(home_bp)

def print_routes():
    """Print available API routes"""
    print("\n🚀 Server ready: http://localhost:5000")
    print("   ─────────────────────────────────────")
    print("   📋 AUTH ROUTES")
    print("   POST   /api/signup")
    print("   POST   /api/login")
    print("   ─────────────────────────────────────")
    print("   👥 USER ROUTES")
    print("   GET    /api/health")
    print("   GET    /api/users")
    print("   GET    /api/users/count")
    print("   ─────────────────────────────────────")
    print("   🚗 VEHICLE ROUTES")
    print("   GET    /api/vehicles")
    print("   POST   /api/vehicles")
    print("   PUT    /api/vehicles/<id>")
    print("   DELETE /api/vehicles/<id>")
    print("   ─────────────────────────────────────")
    print("   📅 SCHEDULE ROUTES")
    print("   GET    /api/schedules")
    print("   POST   /api/schedules")
    print("   PUT    /api/schedules/<id>")
    print("   DELETE /api/schedules/<id>")
    print("   ─────────────────────────────────────")
    print("   📊 DASHBOARD ROUTES")
    print("   GET    /api/home-stats")
    print("   GET    /api/recent-bookings")
    print("   ─────────────────────────────────────\n")

if __name__ == '__main__':
    # Initialize databases
    print("\n🗄️  Initializing databases...")
    init_user_db()
    init_vehicle_db()
    init_schedule_db()
    mail.init_app(app)
    
    # Print available routes
    print_routes()
    
    # Start server
    app.run(debug=DEBUG, host=HOST, port=PORT)