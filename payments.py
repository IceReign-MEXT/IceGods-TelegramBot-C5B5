import os
import time
import requests
import sqlite3
from db import add_payment_record, get_pending_payment_requests, mark_payment_processed, add_subscription
from datetime import datetime

CMC_API_KEY = os.getenv("CMC_API_KEY")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
INFURA_API_KEY = os.getenv("INFURA_API_KEY")  # optional
ETH_MAIN_WALLET = os.getenv("ETH_MAIN_WALLET")
SOL_MAIN_WALLET = os.getenv("SOL_MAIN_WALLET")

# tolerance fraction: accept tx if amount >= required * (1 - TOLERANCE)
PAYMENT_TOLERANCE = 0.01  # 1% tolerance

CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

def get_prices_usd():
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": "ETH,SOL"}
    r = requests.get(CMC_URL, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()["data"]
    return {"ETH": float(data["ETH"]["quote"]["USD"]["price"]), "SOL": float(data["SOL"]["quote"]["USD"]["price"])}

# Etherscan txlist
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
    r.raise_for_status()
    res = r.json()
    if res.get("status") != "1":
        return []
    return res.get("result", [])

# Solscan recent transactions for address
def fetch_sol_txs(address):
    # Using Solscan public API
    url = f"https://public-api.solscan.io/account/transactions?address={address}&limit=50"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return []
    return r.json()

def amount_matches(required_amount, actual_amount):
    return actual_amount >= required_amount * (1.0 - PAYMENT_TOLERANCE)

def handle_eth_checks():
    # fetch pending payment requests from DB (requests placed when user requested /payment)
    pending = get_pending_payment_requests(chain="ETH")
    if not pending:
        return
    txs = fetch_eth_txs(ETH_MAIN_WALLET)
    # iterate pending and try match by telegram_id and required amount
    for req in pending:
        tg = req["telegram_id"]
        plan = req["plan"]
        required = float(req["expected_amount"])
        found = False
        for tx in txs:
            # tx structure: value in Wei, to address, hash, confirmations
            if tx.get("to", "").lower() != ETH_MAIN_WALLET.lower():
                continue
            try:
                value_wei = int(tx.get("value", "0"))
                value_eth = value_wei / 1e18
            except:
                continue
            if amount_matches(required, value_eth):
                # check confirmations
                confirmations = int(tx.get("confirmations", 0))
                if confirmations >= 1:
                    # record payment and activate subscription
                    add_payment_record(tg, tx.get("hash"), "ETH", value_eth, plan, "confirmed")
                    # Activate subscription: compute expiry
                    period_seconds = plan_to_seconds(plan)
                    start_ts = int(time.time())
                    add_subscription(tg, plan, start_ts, start_ts + period_seconds)
                    mark_payment_processed(req["id"])
                    found = True
                    break
        if found:
            print(f"Activated subscription for {tg} via ETH")

def handle_sol_checks():
    pending = get_pending_payment_requests(chain="SOL")
    if not pending:
        return
    txs = fetch_sol_txs(SOL_MAIN_WALLET)
    # Solscan tx structure is a list of dicts with token data; we inspect for SOL transfers to our address
    for req in pending:
        tg = req["telegram_id"]
        plan = req["plan"]
        required = float(req["expected_amount"])
        found = False
        for tx in txs:
            # check if tx involves SOL lamports and to our address
            # Solscan returns 'txHash' and 'changeAmount' or 'tokenTransfers' depending on endpoint
            try:
                # simplistic: look at parsed transaction postTokenBalances or tokenTransfers
                # fallback: check if 'to' equals our address in some field
                # Slightly heuristic because public API formats vary
                if tx.get("signature"):
                    # fetch tx details
                    detail_url = f"https://public-api.solscan.io/transaction/{tx['signature']}"
                    r = requests.get(detail_url, timeout=8)
                    if r.status_code != 200:
                        continue
                    detail = r.json()
                    # parse transfers
                    transfers = detail.get("tokenTransfers", []) or []
                    # also consider 'nativeTransfers' for SOL
                    native = detail.get("nativeTransfers", []) or []
                    for n in native:
                        if n.get("to") == SOL_MAIN_WALLET:
                            lamports = int(n.get("amount", 0))
                            sol_amount = lamports / 1e9
                            if amount_matches(required, sol_amount):
                                # enable subscription
                                add_payment_record(tg, tx['signature'], "SOL", sol_amount, plan, "confirmed")
                                start_ts = int(time.time())
                                add_subscription(tg, plan, start_ts, start_ts + plan_to_seconds(plan))
                                mark_payment_processed(req["id"])
                                found = True
                                break
                    if found:
                        break
            except Exception:
                continue
        if found:
            print(f"Activated subscription for {tg} via SOL")

def plan_to_seconds(plan):
    plan = plan.lower()
    if plan == "weekly":
        return 7 * 24 * 3600
    if plan == "monthly":
        return 30 * 24 * 3600
    if plan == "yearly":
        return 365 * 24 * 3600
    return 0

# This function will be called by background checker
def run_payment_checks():
    try:
        handle_eth_checks()
    except Exception as e:
        print("ETH check error:", e)
    try:
        handle_sol_checks()
    except Exception as e:
        print("SOL check error:", e)

# Utility used by handlers: record that user requested a payment for verification
def record_payment_check_request(telegram_id, plan, chain, expected_amount):
    # This function adds an entry into payments_pending table (in DB)
    from db import add_pending_payment_request
    add_pending_payment_request(telegram_id, plan, chain, float(expected_amount))