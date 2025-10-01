import os, time, requests
from db import add_payment_record, get_pending_payment_requests, mark_payment_processed, add_subscription
from datetime import datetime

CMC_API_KEY = os.getenv("CMC_API_KEY")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETH_MAIN_WALLET = os.getenv("ETH_MAIN_WALLET")
SOL_MAIN_WALLET = os.getenv("SOL_MAIN_WALLET")

PAYMENT_TOLERANCE = 0.01  # 1%

CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

def get_prices_usd():
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": "ETH,SOL"}
    r = requests.get(CMC_URL, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()["data"]
    return {"ETH": float(data["ETH"]["quote"]["USD"]["price"]), "SOL": float(data["SOL"]["quote"]["USD"]["price"])}

def fetch_eth_txs(address):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }
    r = requests.get(url, params=params, timeout=10)
    res = r.json()
    if res.get("status") != "1":
        return []
    return res.get("result", [])

def fetch_sol_txs(address):
    url = f"https://public-api.solscan.io/account/transactions?address={address}&limit=50"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return []
    return r.json()

def amount_matches(required, actual):
    return actual >= required * (1.0 - PAYMENT_TOLERANCE)

def plan_to_seconds(plan):
    plan = plan.lower()
    if plan == "weekly": return 7*24*3600
    if plan == "monthly": return 30*24*3600
    if plan == "yearly": return 365*24*3600
    return 0

def handle_eth_checks():
    pending = get_pending_payment_requests(chain="ETH")
    txs = fetch_eth_txs(ETH_MAIN_WALLET)
    for req in pending:
        tg, plan, required = req["telegram_id"], req["plan"], float(req["expected_amount"])
        for tx in txs:
            if tx.get("to", "").lower() != ETH_MAIN_WALLET.lower():
                continue
            try:
                value_eth = int(tx.get("value", "0")) / 1e18
            except: continue
            if amount_matches(required, value_eth) and int(tx.get("confirmations", 0)) >= 1:
                add_payment_record(tg, tx.get("hash"), "ETH", value_eth, plan, "confirmed")
                start = int(time.time())
                add_subscription(tg, plan, start, start + plan_to_seconds(plan))
                mark_payment_processed(req["id"])
                break

def handle_sol_checks():
    pending = get_pending_payment_requests(chain="SOL")
    txs = fetch_sol_txs(SOL_MAIN_WALLET)
    for req in pending:
        tg, plan, required = req["telegram_id"], req["plan"], float(req["expected_amount"])
        for tx in txs:
            try:
                if tx.get("signature"):
                    detail_url = f"https://public-api.solscan.io/transaction/{tx['signature']}"
                    r = requests.get(detail_url, timeout=8)
                    if r.status_code != 200: continue
                    detail = r.json()
                    native = detail.get("nativeTransfers", [])
                    for n in native:
                        if n.get("to") == SOL_MAIN_WALLET:
                            sol_amount = int(n.get("amount", 0)) / 1e9
                            if amount_matches(required, sol_amount):
                                add_payment_record(tg, tx['signature'], "SOL", sol_amount, plan, "confirmed")
                                start = int(time.time())
                                add_subscription(tg, plan, start, start + plan_to_seconds(plan))
                                mark_payment_processed(req["id"])
                                break
            except: continue

def run_payment_checks():
    try: handle_eth_checks()
    except Exception as e: print("ETH check error:", e)
    try: handle_sol_checks()
    except Exception as e: print("SOL check error:", e)