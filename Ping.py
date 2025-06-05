from telethon import TelegramClient
import asyncio
import logging
import os
import json
from tqdm.asyncio import tqdm  # Use tqdm.asyncio for async iteration

with open('api.json') as f:
    config = json.load(f)

API_ID = config['api_id']
API_HASH = config['api_hash']

SESSION_DIR = 'Session'
SESSIONS = [f.split('.')[0] for f in os.listdir(SESSION_DIR) if f.endswith('.session')]

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'telegram_ping.log')

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

async def ping_account(session_name):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            session_path = os.path.join(SESSION_DIR, session_name)
            client = TelegramClient(session_path, API_ID, API_HASH)
            await client.start()
            me = await client.get_me()
            logging.info(f"[{session_name}] Pinged as {me.username or me.phone} on attempt {attempt}")
            await client.send_message('me', '🔔 Auto-ping to avoid deletion.')
            await client.disconnect()
            return
        except Exception as e:
            logging.warning(f"[{session_name}] Attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)  # ✅ use asyncio-compatible sleep
            else:
                logging.error(f"[{session_name}] Failed after {MAX_RETRIES} attempts: {e}")

async def main():
    logging.info("=== Telegram Account Pinger Started ===")
    
    for session in tqdm(SESSIONS, desc="Pinging sessions", unit="session"):
        await ping_account(session)
    
    logging.info("=== Finished ===\n")

if __name__ == "__main__":
    asyncio.run(main())
