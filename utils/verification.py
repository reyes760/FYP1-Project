import random
import datetime
from flask_mail import Mail, Message

# Initialize Mail instance (to be bound to app in your main server file)
mail = Mail()

# In-memory cache for codes: { "email@example.com": {"code": "123456", "expiry": timestamp} }
verification_cache = {}

def generate_verification_code():
    """Generates a 6-digit numeric string."""
    return str(random.randint(100000, 999999))

def send_verification_email(email):
    """
    Generates a code, stores it with a 5-minute expiry, and sends the email.
    """
    code = generate_verification_code()
    
    # Store code with expiry (standard for secure sign-up systems)
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
    verification_cache[email] = {
        'code': code,
        'expiry': expiry
    }

    try:
        msg = Message(
            subject="DSS Portal Verification Code",
            recipients=[email],
            body=f"Your verification code is: {code}. It expires in 5 minutes."
        )
        mail.send(msg)
        print(f"📧 Code {code} sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Mail Error: {e}")
        return False

def verify_code(email, user_provided_code):
    # Checks if the code matches and is still valid.
    stored_data = verification_cache.get(email.strip().lower())
    
    if not stored_data:
        return False, "No code found for this email. Please request a new one."
    
    if datetime.datetime.now() > stored_data['expiry']:
        del verification_cache[email] # Cleanup expired code
        return False, "Verification code has expired."
    
    if stored_data['code'] != user_provided_code:
        return False, "Invalid verification code."
    
    # Success: Remove code from cache so it can't be reused
    del verification_cache[email]
    return True, "Code verified."