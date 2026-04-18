import time
import os
import redis
from flask import Flask

app = Flask(__name__)

# Use environment variables for flexible configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

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
    return f'Hello! This page has been viewed {count} times.\n'

@app.route('/health')
def health():
    # Basic health check endpoint
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
