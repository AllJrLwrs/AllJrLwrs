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
import asyncio  # Import asyncio untuk menangani fungsi asinkron

# Fungsi untuk membuat token acak
def generate_random_token(length=30):
    characters = string.ascii_letters + string.digits  # Kombinasi huruf dan angka
    return ''.join(random.choice(characters) for _ in range(length))

# Fungsi untuk menghitung GitHub Signature
def generate_github_signature(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

# Fungsi untuk menyimpan token ke GitHub
def save_to_github(token):
    GITHUB_TOKEN = os.getenv("TOKEN_GITHUB")  # Ambil token GitHub dari secrets
    REPO_OWNER = "AllJrLwr"  # Ganti dengan username GitHub Anda
    REPO_NAME = "AllJrLwr"  # Ganti dengan nama repository Anda
    FILE_PATH = "tokens.json"  # Nama file di repository

    # URL untuk API GitHub
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

    # Ambil konten file saat ini
    try:
        response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        print(f"GET request to {url} status: {response.status_code}")
        response.raise_for_status()  # Ini akan memunculkan error jika status code != 200
        print("File fetched successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error mengambil file dari GitHub: {e}")
        return
    
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
    try:
        payload = {
            "message": "Add new token",
            "content": new_content_encoded,
            "sha": sha,
        }
        response = requests.put(url, json=payload, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        print(f"PUT request to {url} status: {response.status_code}")
        print(f"Response content: {response.text}")

        response.raise_for_status()  # Ini akan memunculkan error jika status code != 200
        if response.status_code == 200:
            print("Token berhasil disimpan ke GitHub!")
        else:
            print(f"Error menyimpan token ke GitHub: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error saat menyimpan token ke GitHub: {e}")

# Fungsi utama untuk menjalankan bot dan mengirimkan token ke grup
async def send_token():
    API_TOKEN = os.getenv("API_TOKEN")  # Ambil token API Telegram dari secrets
    GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # Ambil Chat ID grup dari secrets
    bot = Bot(token=API_TOKEN)
    
    # Generate token acak
    random_token = generate_random_token()
    mestext = f"""***❤‍🔥 Hurry Up and Cheers ❤‍🔥***

_Daily Token is Appearing Now_

> ||     {random_token}     ||

***info     : Use this Token to enter the Script***
***Expire : this token is only valid for 3 hours***
"""
    
    # Coba mengirim pesan ke grup Telegram
    try:
        message = await bot.send_message(chat_id=GROUP_CHAT_ID, text=mestext, parse_mode="MarkdownV2")
        print(f"Pesan berhasil dikirim ke Telegram dengan token: {random_token}")
        
        # Pin pesan yang baru dikirim
        await bot.pin_chat_message(chat_id=GROUP_CHAT_ID, message_id=message.message_id)
        print("Pesan berhasil dipin.")
        
        # Unpin pesan lama jika ada
        pinned_messages = await bot.get_chat_pinned_message(chat_id=GROUP_CHAT_ID)
        if pinned_messages:
            await bot.unpin_chat_message(chat_id=GROUP_CHAT_ID, message_id=pinned_messages.message_id)
            print("Pesan lama berhasil diunpin.")
    except Exception as e:
        print(f"Error mengirim pesan ke Telegram: {e}")
        return  # Jika gagal, hentikan eksekusi lebih lanjut
    
    # Simpan token ke GitHub
    try:
        save_to_github(random_token)
    except Exception as e:
        print(f"Error saat menyimpan token ke GitHub: {e}")

# Menjalankan event loop untuk menjalankan fungsi asinkron send_token
if __name__ == "__main__":
    asyncio.run(send_token())
