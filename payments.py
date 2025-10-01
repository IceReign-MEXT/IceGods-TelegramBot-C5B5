from db import get_pending_payment_requests, mark_payment_processed, add_payment_record
import time

def run_payment_checks():
    print("🔎 Checking for payments...")
    pending = get_pending_payment_requests()
    for req in pending:
        # TODO: integrate real blockchain API check here
        # For now, we simulate confirmation
        print(f"Simulating payment for {req}")
        add_payment_record(
            telegram_id=req["telegram_id"],
            tx_hash="demo_tx_hash",
            chain=req["chain"],
            amount=req["expected_amount"],
            plan=req["plan"],
            status="confirmed"
        )
        mark_payment_processed(req["id"])
        time.sleep(1)