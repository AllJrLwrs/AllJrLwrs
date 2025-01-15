import asyncio
import random
import string
import requests
import base64
import json
import hashlib
import uuid
import os
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
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Mengambil GitHub token dari secrets
    REPO_OWNER = "AllJrLwr"  # Ganti dengan username GitHub Anda
    REPO_NAME = "AllJrLwr"  # Ganti dengan nama repository Anda
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

# Fungsi untuk mengirim token ke grup dan mengepin pesan token baru
async def send_and_pin_token(bot, group_chat_id, previous_message_id=None):
    try:
        # Generate token acak
        random_token = generate_random_token()
        mestext = f"""***❤‍🔥 Hurry Up and Cheers ❤‍🔥***

_Daily Token is Appearing Now_

> || ➡️    {random_token}    ⬅️ ||

***info     : Use this Token to enter the Script***
***Expire : this token is only valid for 3 hours***
"""
        # Kirim token ke grup
        sent_message = await bot.send_message(chat_id=group_chat_id, text=mestext, parse_mode="MarkdownV2")
        
        # Simpan token ke GitHub
        save_to_github(random_token)

        # Hapus pesan pin sebelumnya jika ada
        if previous_message_id:
            try:
                await bot.unpin_chat_message(chat_id=group_chat_id, message_id=previous_message_id)
            except Exception as e:
                print(f"Error saat unpin pesan sebelumnya: {e}")

        # Pin pesan baru
        await bot.pin_chat_message(chat_id=group_chat_id, message_id=sent_message.message_id)

        # Return ID pesan baru yang dipin
        return sent_message.message_id

    except Exception as e:
        print(f"Error: {e}")
        return None

# Fungsi utama untuk menjalankan bot dan mengirimkan token setiap 1 hari
async def send_token_periodically():
    API_TOKEN = os.getenv("API_TOKEN")  # Mengambil token API Telegram dari secrets
    GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # Mengambil ID grup Telegram dari secrets
    bot = Bot(token=API_TOKEN)
    previous_message_id = None  # ID pesan yang dipin sebelumnya
    while True:
        # Kirim dan pin token baru setiap 24 jam (86400 detik)
        previous_message_id = await send_and_pin_token(bot, GROUP_CHAT_ID, previous_message_id)

# Main function
if __name__ == "__main__":
    print("Bot sedang berjalan, mengirim token, mengepin pesan, dan menyimpan ke GitHub...")
    asyncio.run(send_token_periodically())
