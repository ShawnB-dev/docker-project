import logging
import re
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Configure logging to capture attacker details
logging.basicConfig(level=logging.INFO, format='%(asctime)s - ALERT - %(message)s')

# File logging for CLI export
LOG_DIR = "/home/appuser/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "honeypot.log")
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Portal | Secure Login</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #1a202c; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #2d3748; padding: 40px; border-radius: 8px; width: 100%; max-width: 400px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); border-top: 4px solid #4299e1; }
        h2 { color: #edf2f7; text-align: center; margin-bottom: 24px; font-weight: 300; letter-spacing: 1px; }
        label { display: block; color: #a0aec0; margin-bottom: 8px; font-size: 0.875rem; }
        input { width: 100%; padding: 12px; margin-bottom: 20px; background: #4a5568; border: 1px solid #718096; border-radius: 4px; color: white; box-sizing: border-box; }
        input:focus { outline: none; border-color: #4299e1; box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5); }
        button { width: 100%; padding: 12px; background: #4299e1; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #3182ce; }
        .footer { margin-top: 20px; text-align: center; font-size: 0.75rem; color: #718096; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>ADMIN ACCESS</h2>
        {% if error %}
        <div style="background: #fed7d7; color: #c53030; padding: 10px; border-radius: 4px; margin-bottom: 20px; font-size: 0.875rem; text-align: center; border: 1px solid #fc8181;">
            Invalid username or password. Please try again.
        </div>
        {% endif %}
        <form method="POST">
            <label>Username</label>
            <input type="text" name="username" placeholder="Enter administrative ID" required>
            <label>Password</label>
            <input type="password" name="password" placeholder="••••••••" required>
            <button type="submit">SIGN IN</button>
        </form>
        <div class="footer">
            <a href="/admin/forgot-password" style="color: #4299e1; text-decoration: none; font-size: 0.8rem;">Forgot Password?</a><br><br>
            Protected by Enterprise Grade Encryption
        </div>
    </div>
</body>
</html>
"""

FORGOT_PASSWORD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Password Recovery | Admin Portal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #1a202c; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #2d3748; padding: 40px; border-radius: 8px; width: 100%; max-width: 400px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); border-top: 4px solid #4299e1; }
        h2 { color: #edf2f7; text-align: center; margin-bottom: 15px; font-weight: 300; letter-spacing: 1px; }
        p { color: #a0aec0; font-size: 0.875rem; text-align: center; margin-bottom: 24px; line-height: 1.5; }
        label { display: block; color: #a0aec0; margin-bottom: 8px; font-size: 0.875rem; }
        input { width: 100%; padding: 12px; margin-bottom: 20px; background: #4a5568; border: 1px solid #718096; border-radius: 4px; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #4299e1; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .footer { margin-top: 20px; text-align: center; font-size: 0.75rem; color: #718096; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>RECOVERY</h2>
        {% if error %}
        <div style="background: #fed7d7; color: #c53030; padding: 10px; border-radius: 4px; margin-bottom: 20px; font-size: 0.875rem; text-align: center; border: 1px solid #fc8181;">
            Please enter a valid administrative email address.
        </div>
        {% endif %}
        {% if success %}
        <p style="color: #68d391;">If this account exists in our database, a recovery link has been sent to the associated email address.</p>
        <div class="footer"><a href="/admin" style="color: #4299e1; text-decoration: none;">Back to Login</a></div>
        {% else %}
        <p>Enter your administrative email address to reset your access credentials.</p>
        <form method="POST">
            <label>Email Address</label>
            <input type="email" name="email" placeholder="admin@internal.corp" required>
            <button type="submit">SEND RECOVERY LINK</button>
        </form>
        <div class="footer"><a href="/admin" style="color: #4299e1; text-decoration: none;">Return to Login</a></div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    # RFC 5322 compliant regex for email validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        
        # Server-side validation check
        if not re.match(email_regex, email):
            app.logger.info(f"[MALFORMED INPUT] IP: {client_ip} | Input: {email} | UA: {user_agent}")
            return render_template_string(FORGOT_PASSWORD_TEMPLATE, success=False, error=True), 400

        # Log the email for threat intelligence
        app.logger.info(f"[EMAIL HARVEST] IP: {client_ip} | Email: {email} | UA: {user_agent}")
        return render_template_string(FORGOT_PASSWORD_TEMPLATE, success=True), 200
        
    return render_template_string(FORGOT_PASSWORD_TEMPLATE, success=False), 200

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def trap(path):
    # Identify the attacker's details (X-Real-IP is passed by our Nginx proxy)
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    if request.method == 'POST':
        # Capture attempted credentials for threat intelligence
        user = request.form.get('username', 'N/A')
        pwd = request.form.get('password', 'N/A')
        
        # Log as a high-priority brute-force alert
        app.logger.info(f"[BRUTE FORCE] IP: {client_ip} | Path: /{path} | Attempt: {user}:{pwd} | UA: {user_agent}")
        
        # Return 401 to keep the attacker/bot engaged in "guessing"
        return render_template_string(ADMIN_LOGIN_TEMPLATE, error=True), 401

    # Log as a scanning/probing attempt
    app.logger.info(f"[SCAN] IP: {client_ip} | Path: /{path} | UA: {user_agent}")
    # Return the fake login page to bait the attacker
    return render_template_string(ADMIN_LOGIN_TEMPLATE), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)