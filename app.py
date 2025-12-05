from flask import Flask
from bot import main  # Not directly, but for worker

app = Flask(__name__)

@app.route('/')
def home():
    return "Earnings Bot is running! 🚀"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
