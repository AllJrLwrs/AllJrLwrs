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
    characters = string.ascii_letters + string.digits  # Kombinasi huruf dan angka
    return ''.join(random.choice(characters) for _ in range(length))

# Fungsi untuk menghitung GitHub Signature
def generate_github_signature(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

# Fungsi untuk menyimpan token ke GitHub
def save_to_github(token):
    GITHUB_TOKEN = os.getenv("TOKEN_GITHUB")  # Ambil token GitHub dari environment variable
    REPO_OWNER = "AllJrLwr"  # Username GitHub
    REPO_NAME = "AllJrLwr"  # Nama repository
    FILE_PATH = "tokens.json"  # Nama file di repository

    # URL untuk API GitHub
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

    # Ambil konten file saat ini
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if response.status_code == 200:
        data = response.json()
        sha = data["sha"]
        current_content = base64.b64decode(data["content"]).decode("utf-8")
    else:
        sha = None
        current_content = "[]"

    # Parse konten file
    current_tokens = json.loads(current_content)

    # Tambahkan token baru
    new_entry = {
        "id": uuid.uuid4().hex[:13],
        "token": token,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "telegram",
        "uuid": str(uuid.uuid4()),
        "githubSignature": generate_github_signature(token),
    }
    current_tokens.append(new_entry)

    # Encode konten baru
    new_content = json.dumps(current_tokens, indent=4)
    new_content_encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    # Update file di GitHub
    payload = {
        "message": "Add new token",
        "content": new_content_encoded,
        "sha": sha,
    }
    response = requests.put(url, json=payload, headers={"Authorization": f"token {GITHUB_TOKEN}"})

    if response.status_code == 200:
        print("Token berhasil disimpan ke GitHub!")
    else:
        print(f"Error menyimpan ke GitHub: {response.status_code}, {response.text}")

# Fungsi untuk mengirim token ke grup Telegram dan mengepin pesan
async def send_and_pin_token():
    try:
        # Ambil API Token dan Chat ID dari environment variable
        API_TOKEN = os.getenv("API_TOKEN")  # Token bot Telegram
        GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # Chat ID grup Telegram

        bot = Bot(token=API_TOKEN)

        # Generate token acak
        random_token = generate_random_token()
        mestext = f"""***❤‍🔥 Hurry Up and Cheers ❤‍🔥***

_Daily Token is Appearing Now_

> ||*** {random_token} ***||

***info     : Use this Token to enter the Script***
***Expire : this token is only valid for 5 hours***
"""
        # Kirim pesan ke grup Telegram
        sent_message = await bot.send_message(chat_id=GROUP_CHAT_ID, text=mestext, parse_mode="MarkdownV2")

        # Simpan token ke GitHub
        save_to_github(random_token)

        # Pin pesan di grup Telegram
        await bot.pin_chat_message(chat_id=GROUP_CHAT_ID, message_id=sent_message.message_id)

        print("Token berhasil dikirim dan dipin ke grup Telegram!")
    except Exception as e:
        print(f"Error: {e}")

# Main function
if __name__ == "__main__":
    print("Mengirim token ke grup Telegram dan menyimpannya ke GitHub...")
    import asyncio
    asyncio.run(send_and_pin_token())
