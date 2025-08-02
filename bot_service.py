import asyncio
import threading
import queue
import datetime
import random
import os
from telethon import TelegramClient
from telethon.errors import ChatAdminRequiredError, FloodWaitError
from telethon.tl.functions.channels import JoinChannelRequest
from app import db
from models import BotLog, BotConfig, BotStatus

class TelegramBotService:
    def __init__(self):
        self.api_id = int(os.getenv('TELEGRAM_API_ID', '26646846'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '9b49d058f3af38db717ce0768a57a4b2')
        self.phone = os.getenv('TELEGRAM_PHONE', '+62882002745128')
        
        self.client = None
        self.is_running = False
        self.should_stop = False
        self.thread = None
        self.loop = None
        
        # Default configuration
        self.delay_seconds = 15
        self.delay_between_rounds = 1
        self.operation_hours = 24
        
        self.group_usernames = [
            'lpm_jualan_nokoscnit',
            'lpmaccttt',
            'LpmNokosIDL',
            'lapakjbbebas',
            'rnkajoee24',
            'groupjuaranyafollowers',
            'jualbeliakunmedsos02',
            'diskusixodiac',
            'giftt_roblox',
        ]
        
        self.promo_message = """🟣 [ GILA MURAH ‼️ JASA BOOSTING IG & TIKTOK ]

✅ 100% Aman bukan tipu2 
✅ Masuk cepat (<30 menit)
✅ Bisa request jumlah & link
✅ Bonus setiap order!
—

📸 INSTAGRAM

🎥 VIEWS IG:
• 5.000 views = Rp 1.000
• 10.000 views = Rp 1.800
• 30.000 views = Rp 4.500
• 100.000 views = Rp 10.000

👍 LIKES IG:
• 100 likes = Rp 1.200
• 250 likes = Rp 2.800
• 500 likes = Rp 5.000
• 1.000 likes = Rp 9.000

💾 SAVES IG:
• 100 saves = Rp 1.500
• 250 saves = Rp 3.200
• 500 saves = Rp 6.000

💬 KOMENTAR IG:
• 50 komen = Rp 3.000
• 100 komen = Rp 5.500
• Bisa custom isi komen juga!

📸 INSTAGRAM FOLLOWERS
• 100 followers = Rp 3.000
• 250 followers = Rp 6.000
• 500 followers = Rp 10.000
• 1.000 followers = Rp 18.000

🎁 BUNDLING IG:
• 5k views + 100 followers = Rp 3.700
• 10k views + 250 followers = Rp 7.500
• 30k views + 500 followers = Rp 13.000
• 100k views + 1.000 followers = Rp 22.000

—

🎵 TIKTOK

🎥 VIEWS TT:
• 5.000 views = Rp 1.000
• 10.000 views = Rp 1.800
• 30.000 views = Rp 4.500
• 100.000 views = Rp 10.000

👍 LIKES TT:
• 100 likes = Rp 1.000
• 250 likes = Rp 2.500
• 500 likes = Rp 4.500
• 1.000 likes = Rp 8.500

💾 SAVES TT:
• 100 saves = Rp 1.300
• 250 saves = Rp 3.000
• 500 saves = Rp 5.500

💬 KOMENTAR TT:
• 50 komen = Rp 2.800
• 100 komen = Rp 5.000
• Bisa custom isi komen juga!

🎵 TIKTOK FOLLOWERS
• 100 followers = Rp 4.000
• 250 followers = Rp 9.000
• 500 followers = Rp 16.000
• 1.000 followers = Rp 28.000

🎁 BUNDLING TT:
• 5k views + 100 followers = Rp 5.000
• 10k views + 250 followers = Rp 10.500
• 30k views + 500 followers = Rp 18.000
• 100k views + 1.000 followers = Rp 30.000

—

📩 ORDER LANGSUNG!
🔥 WhatsApp: wa.me/6281313420263 
atau chat langsung telegram @chaosxpedia"""

    def log_message(self, level, message, group_name=None):
        """Log message to database"""
        try:
            from app import app
            with app.app_context():
                log_entry = BotLog(level=level, message=message, group_name=group_name)
                db.session.add(log_entry)
                db.session.commit()
        except Exception as e:
            print(f"Failed to log message: {e}")

    def load_config(self):
        """Load configuration from database"""
        self.delay_seconds = float(BotConfig.get_value('delay_seconds', '15'))
        self.delay_between_rounds = float(BotConfig.get_value('delay_between_rounds', '1'))
        self.operation_hours = float(BotConfig.get_value('operation_hours', '24'))

    async def ensure_join(self, group):
        """Ensure bot is joined to the group"""
        try:
            await self.client(JoinChannelRequest(group))
            self.log_message('INFO', f'✅ Bergabung ke {group}', group)
        except Exception as e:
            if "already" in str(e).lower():
                self.log_message('INFO', f'ℹ️ Sudah tergabung di {group}', group)
            else:
                self.log_message('WARNING', f'⚠️ Gagal join {group}: {e}', group)

    async def send_safe(self, group, message):
        """Safely send message to group with error handling"""
        try:
            entity = await self.client.get_entity(group)
        except Exception as e:
            self.log_message('ERROR', f'❌ Gagal resolve {group}: {e}', group)
            return False

        try:
            await self.client.send_message(entity, message)
            self.log_message('INFO', f'✅ Terkirim ke {group}', group)
            return True
        except Exception as e:
            lower = str(e).lower()
            if 'join the discussion group' in lower or 'discussion' in lower:
                self.log_message('WARNING', f'⚠️ Perlu join dulu {group}, mencoba join...', group)
                await self.ensure_join(group)
                try:
                    await self.client.send_message(entity, message)
                    self.log_message('INFO', f'✅ (after join) Terkirim ke {group}', group)
                    return True
                except Exception as e2:
                    self.log_message('ERROR', f'❌ Tetap gagal setelah join {group}: {e2}', group)
                    return False
            elif isinstance(e, FloodWaitError):
                self.log_message('WARNING', f'🛑 FloodWait {e.seconds} detik, tunggu dulu...', group)
                await asyncio.sleep(e.seconds + 1)
                return await self.send_safe(group, message)
            elif isinstance(e, ChatAdminRequiredError):
                self.log_message('WARNING', f'⚠️ Butuh izin/admin di {group}', group)
                return False
            else:
                self.log_message('ERROR', f'❌ Error kirim ke {group}: {e}', group)
                return False

    async def run_bot_cycle(self):
        """Main bot cycle"""
        start_time = datetime.datetime.now()
        stop_time = start_time + datetime.timedelta(hours=self.operation_hours)
        
        # Update status
        from app import app
        with app.app_context():
            status = BotStatus.get_status()
            status.start_time = start_time
            status.scheduled_stop_time = stop_time
            status.is_running = True
            status.messages_sent = 0
            status.rounds_completed = 0
            db.session.commit()
        
        self.log_message('INFO', f'🚀 Bot dimulai untuk {self.operation_hours} jam')
        self.log_message('INFO', f'📅 Akan berhenti pada: {stop_time.strftime("%Y-%m-%d %H:%M:%S")}')
        
        try:
            self.log_message('INFO', '🔐 Mencoba login ke Telegram...')
            
            # Connect first
            if not self.client.is_connected():
                await self.client.connect()
                self.log_message('INFO', '🔗 Terhubung ke server Telegram')
            
            # Check if already authorized
            if not await self.client.is_user_authorized():
                self.log_message('WARNING', '⚠️ Belum terautentikasi, memerlukan verifikasi...')
                await self.client.send_code_request(self.phone)
                self.log_message('ERROR', '❌ Memerlukan kode verifikasi dari Telegram. Gunakan form Autentikasi di dashboard untuk memasukkan kode.')
                return
            else:
                self.log_message('INFO', '✅ Sudah terautentikasi, melanjutkan...')
            
            self.log_message('INFO', '✅ Berhasil login ke Telegram!')
            
            while datetime.datetime.now() < stop_time and not self.should_stop:
                self.log_message('INFO', '🚀 Mulai satu putaran broadcast')
                messages_in_round = 0
                
                for group in self.group_usernames:
                    if self.should_stop or datetime.datetime.now() >= stop_time:
                        break
                        
                    success = await self.send_safe(group, self.promo_message)
                    if success:
                        messages_in_round += 1
                        
                    # Delay with jitter
                    jitter = random.uniform(-2, 2)
                    inter_delay = max(5, self.delay_seconds + jitter)
                    self.log_message('INFO', f'⏳ Tunggu {inter_delay:.1f} detik sebelum lanjut ke grup berikutnya...')
                    await asyncio.sleep(inter_delay)
                
                # Update statistics
                from app import app
                with app.app_context():
                    status = BotStatus.get_status()
                    status.messages_sent += messages_in_round
                    status.rounds_completed += 1
                    db.session.commit()
                
                if datetime.datetime.now() < stop_time and not self.should_stop:
                    self.log_message('INFO', f'✅ Putaran selesai, jeda pendek {self.delay_between_rounds} detik sebelum ulang...')
                    await asyncio.sleep(self.delay_between_rounds)
                    
        except Exception as e:
            self.log_message('ERROR', f'❌ Error dalam bot cycle: {e}')
        finally:
            # Update final status
            from app import app
            with app.app_context():
                status = BotStatus.get_status()
                status.is_running = False
                status.stop_time = datetime.datetime.now()
                db.session.commit()
            
            self.log_message('INFO', '🛑 Bot berhenti')
            self.is_running = False

    def run_in_thread(self):
        """Run the bot in a separate thread"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.client = TelegramClient('session_promo_bot', self.api_id, self.api_hash)
            
            # Run the bot cycle
            self.loop.run_until_complete(self.run_bot_cycle())
                
        except Exception as e:
            self.log_message('ERROR', f'❌ Critical error in bot thread: {e}')
        finally:
            self.is_running = False
            if self.client and self.client.is_connected():
                try:
                    self.loop.run_until_complete(self.client.disconnect())
                except:
                    pass
            if self.loop:
                self.loop.close()

    def start_bot(self):
        """Start the bot service"""
        if self.is_running:
            return False, "Bot sudah berjalan"
            
        self.load_config()
        self.should_stop = False
        self.is_running = True
        
        # Start bot in separate thread
        self.thread = threading.Thread(target=self.run_in_thread, daemon=True)
        self.thread.start()
        
        return True, "Bot berhasil dimulai"

    def stop_bot(self):
        """Stop the bot service"""
        if not self.is_running:
            return False, "Bot tidak sedang berjalan"
            
        self.should_stop = True
        self.log_message('INFO', '🛑 Perintah stop diterima, menghentikan bot...')
        
        # Update status
        from app import app
        with app.app_context():
            status = BotStatus.get_status()
            status.is_running = False
            status.stop_time = datetime.datetime.now()
            db.session.commit()
        
        return True, "Bot sedang dihentikan"

    def get_status(self):
        """Get current bot status"""
        status = BotStatus.get_status()
        return {
            'is_running': self.is_running,
            'start_time': status.start_time.strftime('%Y-%m-%d %H:%M:%S') if status.start_time else None,
            'stop_time': status.stop_time.strftime('%Y-%m-%d %H:%M:%S') if status.stop_time else None,
            'scheduled_stop_time': status.scheduled_stop_time.strftime('%Y-%m-%d %H:%M:%S') if status.scheduled_stop_time else None,
            'messages_sent': status.messages_sent,
            'rounds_completed': status.rounds_completed,
            'time_remaining': self._calculate_time_remaining(status)
        }

    def _calculate_time_remaining(self, status):
        """Calculate remaining time"""
        if not status.scheduled_stop_time or not self.is_running:
            return None
            
        remaining = status.scheduled_stop_time - datetime.datetime.now()
        if remaining.total_seconds() <= 0:
            return "00:00:00"
            
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Global bot service instance
bot_service = TelegramBotService()
