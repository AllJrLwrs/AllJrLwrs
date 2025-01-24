import os
import time
from telethon.sync import TelegramClient

# Mengambil API ID, API Hash, dan nomor telepon dari environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

# Username bot yang akan dihubungi
bot_username = "@Free_Trump_Instant_Pay_Bot"

# Pesan yang ingin dikirim
message = "🤏 Click☝"

# Fungsi utama
def main():
    # Membuat dan memulai klien Telethon
    with TelegramClient('session_name', api_id, api_hash) as client:
        print("Login berhasil!")
        while True:
            try:
                # Mengirim pesan ke bot
                client.send_message(bot_username, message)
                print(f"Pesan berhasil dikirim ke {bot_username}: {message}")

                # Timer 60 detik
                for remaining in range(60, 0, -1):
                    print(f"Menunggu {remaining} detik...", end="\r")
                    time.sleep(1)
                print(" " * 30, end="\r")  # Membersihkan baris

            except Exception as e:
                print(f"Terjadi kesalahan: {e}")
                break

if __name__ == "__main__":
    main()
