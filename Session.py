from telethon import TelegramClient
import asyncio
import os
import json

with open('api.json') as f:
    config = json.load(f)

API_ID = config['api_id']
API_HASH = config['api_hash']

ACCOUNT_FILE = 'Number.txt'
SESSION_DIR = 'Session'

os.makedirs(SESSION_DIR, exist_ok=True)

async def login_account(session_name, phone_number):
    client = TelegramClient(session_name, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone_number)
            code = input(f"[{session_name}] Enter the code for {phone_number}: ")
            try:
                await client.sign_in(phone_number, code)
            except Exception as e:
                if "2FA" in str(e) or "password" in str(e).lower():
                    password = input(f"[{session_name}] Enter 2FA password: ")
                    await client.sign_in(password=password)
        except Exception as e:
            print(f"❌ Error with {phone_number}: {e}")
    await client.disconnect()
    if await client.is_user_authorized() and os.path.exists(session_name + ".session"):
        print(f"✅ Saved session: {session_name}.session")
    else:
        print(f"❌ Login Failed for {phone_number}")

async def main():
    if not os.path.exists(ACCOUNT_FILE):
        print(f"{ACCOUNT_FILE} not found.")
        return

    with open(ACCOUNT_FILE, 'r') as f:
        numbers = [line.strip() for line in f if line.strip()]

    for idx, number in enumerate(numbers, start=1):
        Session_path = os.path.join(SESSION_DIR, f'account{idx}')
        print(f"\n=== Logging in {number} as {Session_path} ===")
        await login_account(Session_path, number)

if __name__ == "__main__":
    asyncio.run(main())
