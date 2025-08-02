#!/usr/bin/env python3
"""
Manual Telegram authentication script
Run this script to authenticate your Telegram account manually
"""

import asyncio
import os
from telethon import TelegramClient

async def authenticate():
    api_id = int(os.getenv('TELEGRAM_API_ID', '26646846'))
    api_hash = os.getenv('TELEGRAM_API_HASH', '9b49d058f3af38db717ce0768a57a4b2')
    phone = os.getenv('TELEGRAM_PHONE', '+62882002745128')
    
    client = TelegramClient('session_promo_bot', api_id, api_hash)
    
    print("🔐 Memulai autentikasi Telegram...")
    print(f"📱 Nomor telepon: {phone}")
    
    await client.start(phone=phone)
    
    if await client.is_user_authorized():
        print("✅ Autentikasi berhasil!")
        print("📂 Session file telah dibuat: session_promo_bot.session")
        print("🚀 Sekarang Anda dapat menjalankan bot dari dashboard web")
    else:
        print("❌ Autentikasi gagal")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(authenticate())