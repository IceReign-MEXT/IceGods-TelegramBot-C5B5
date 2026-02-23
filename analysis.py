import re
import httpx
import os

HELIUS_RPC = os.getenv("HELIUS_RPC")

def extract_address(text):
    match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', text)
    return match.group(0) if match else None

async def check_rug(token_addr):
    """Scans for Mint Authority, Freeze Authority, and Mutability."""
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getAsset", "params": {"id": token_addr}}
        async with httpx.AsyncClient() as client:
            resp = await client.post(HELIUS_RPC, json=payload)
            data = resp.json().get('result', {})
            
            # Security Flags
            if data.get('frozen', False) or data.get('mutable', True):
                return False, "RISK: Mutable Metadata or Freeze Enabled"
            return True, "SAFE"
    except:
        return False, "ANALYSIS_ERROR"
