import os
from dotenv import load_dotenv
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import AddressNotFound
from db import deduct_balance, get_balance, add_withdrawal

load_dotenv()

TRON_PRIVATE_KEY = os.getenv('TRON_PRIVATE_KEY')
TRON_PAYOUT_ADDRESS = os.getenv('TRON_PAYOUT_ADDRESS')
OWNER_USDT_WALLET = os.getenv('OWNER_USDT_WALLET')
USDT_CONTRACT = os.getenv('USDT_CONTRACT')
MIN_WITHDRAWAL = float(os.getenv('MIN_WITHDRAWAL', 5.0))
FEE_PERCENT = float(os.getenv('FEE_PERCENT', 2.0))

client = Tron()
priv_key = PrivateKey(bytes.fromhex(TRON_PRIVATE_KEY))
contract = client.get_contract(USDT_CONTRACT)

def automate_payout(user_wallet: str, amount: float, user_id: int) -> dict:
    if amount < MIN_WITHDRAWAL:
        return {'success': False, 'error': f'Minimum withdrawal is ${MIN_WITHDRAWAL}'}

    balance = get_balance(user_id)
    if balance < amount:
        return {'success': False, 'error': 'Insufficient balance'}

    try:
        # Calculate fee
        fee = amount * (FEE_PERCENT / 100)
        payout_amount = amount - fee
        fee_amount = fee

        # Send payout
        amount_wei = int(payout_amount * 1_000_000)
        txn = (
            contract.functions.transfer(user_wallet, amount_wei)
            .with_owner(priv_key.public_key.to_base58check_address())
            .fee_limit(40_000_000)
            .build()
            .sign(priv_key)
            .broadcast()
        )
        result = txn.wait()
        txid = txn.get_txid()

        # Deduct from balance
        deduct_balance(user_id, amount)

        # Send fee to owner (if >0)
        if fee_amount > 0:
            fee_wei = int(fee_amount * 1_000_000)
            fee_txn = (
                contract.functions.transfer(OWNER_USDT_WALLET, fee_wei)
                .with_owner(priv_key.public_key.to_base58check_address())
                .fee_limit(40_000_000)
                .build()
                .sign(priv_key)
                .broadcast()
            )
            fee_txn.wait()

        # Log withdrawal
        add_withdrawal(user_id, amount, user_wallet, txid)

        return {
            'success': True,
            'txid': txid,
            'payout_amount': payout_amount,
            'fee': fee,
            'link': f'https://tronscan.org/#/transaction/{txid}'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
