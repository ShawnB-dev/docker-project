import time
import os
import redis
from flask import Flask, render_template_string

app = Flask(__name__)

# Use environment variables for flexible configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Visitor Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #1a202c; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #2d3748; padding: 2.5rem; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); text-align: center; width: 350px; border-top: 4px solid #4299e1; }
        h1 { color: #edf2f7; margin-bottom: 0.5rem; font-weight: 300; }
        .counter { font-size: 4rem; font-weight: 800; color: #4299e1; margin: 1.5rem 0; }
        p { color: #a0aec0; font-size: 1.1rem; }
        .status { display: inline-block; padding: 5px 12px; background: rgba(66, 153, 225, 0.1); color: #4299e1; border-radius: 20px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="status">LIVE STATISTICS</div>
        <h1>Hello!</h1>
        <p>This page has been viewed</p>
        <div class="counter">{{ count if count is not none else '0' }}</div>
        <p>times</p>
        <div style="margin-top: 20px; border-top: 1px solid #4a5568; padding-top: 15px;">
            <a href="/admin" style="color: #718096; text-decoration: none; font-size: 0.8rem; transition: color 0.2s;" onmouseover="this.style.color='#4299e1'" onmouseout="this.style.color='#718096'">System Management</a>
        </div>
    </div>
</body>
</html>
"""

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template_string(HTML_TEMPLATE, count=count)

@app.route('/health')
def health():
    # Basic health check endpoint
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
