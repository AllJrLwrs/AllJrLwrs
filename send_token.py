import os
import random
import string
import requests
import base64
import json
import hashlib
import uuid
from datetime import datetime, timezone
from telegram import Bot

# Fungsi untuk membuat token acak
def generate_random_token(length=30):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Fungsi untuk menghitung GitHub Signature
def generate_github_signature(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

# Fungsi untuk menyimpan token ke GitHub
def save_to_github(token):
    GITHUB_TOKEN = os.getenv("TOKEN_GITHUB")
    REPO_OWNER = "AllJrLwr"
    REPO_NAME = "AllJrLwr"
    FILE_PATH = "tokens.json"

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        sha = data["sha"]
        current_content = base64.b64decode(data["content"]).decode("utf-8")
    else:
        sha = None
        current_content = "[]"

    current_tokens = json.loads(current_content)

    new_entry = {
        "id": uuid.uuid4().hex[:13],
        "token": token,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "telegram",
        "uuid": str(uuid.uuid4()),
        "githubSignature": generate_github_signature(token),
    }
    current_tokens.append(new_entry)

    new_content = json.dumps(current_tokens, indent=4)
    new_content_encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": "Add new token",
        "content": new_content_encoded,
        "sha": sha,
    }
    put_response = requests.put(url, json=payload, headers=headers)

    if put_response.status_code in [200, 201]:
        print("✅ Token berhasil disimpan ke GitHub!")
    else:
        print(f"❌ Gagal menyimpan ke GitHub: {put_response.status_code}, {put_response.text}")

# Fungsi utama untuk kirim dan pin token
async def send_and_pin_token():
    try:
        API_TOKEN = os.getenv("API_TOKEN")
        GROUP_CHAT_IDS = os.getenv("GROUP_CHAT_ID", "").split(",")
        bot = Bot(token=API_TOKEN)

        random_token = generate_random_token()
        mestext = f"""***❤‍🔥 Hurry Up and Cheers ❤‍🔥***

_Free Tokens every 6 hours is Appearing Now_

> ||*** {random_token} ***||

***info     : Use this Token to enter the Script***
***Expire : this token is only valid for 2 hours***
"""

        for chat_id in GROUP_CHAT_IDS:
            chat_id = chat_id.strip()
            try:
                sent_message = await bot.send_message(
                    chat_id=chat_id,
                    text=mestext,
                    parse_mode="MarkdownV2"
                )
                await bot.pin_chat_message(chat_id=chat_id, message_id=sent_message.message_id)
                print(f"✅ Terkirim & dipin ke {chat_id}")
            except Exception as err:
                print(f"❌ Gagal kirim/pin ke chat_id {chat_id}: {err}")

        save_to_github(random_token)

    except Exception as e:
        print(f"❌ Error utama: {e}")

# Main runner
if __name__ == "__main__":
    print("🚀 Mengirim token ke grup Telegram dan menyimpannya ke GitHub...")
    import asyncio
    asyncio.run(send_and_pin_token())
