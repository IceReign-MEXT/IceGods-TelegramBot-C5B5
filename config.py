import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
SOL_MAIN_WALLET = os.getenv("SOLANA_WALLET")
HELIUS_RPC = os.getenv("HELIUS_RPC")
DATABASE_URL = "postgresql://postgres.sezxolvjozcbqhwlhluz:ICEGODS30ICEDEIL30@://aws-1-eu-north-1.pooler.supabase.com"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "7_pWz-99_fake_key_for_build_only_").encode()
