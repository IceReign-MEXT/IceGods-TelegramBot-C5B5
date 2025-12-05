import time
from db import get_users  # Add this func to db.py if needed

def check_referrals():
    while True:
        # Logic to credit pending referrals
        time.sleep(3600)  # Hourly

# threading.Thread(target=check_referrals, daemon=True).start()
