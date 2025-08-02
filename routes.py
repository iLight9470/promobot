from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import BotLog, BotConfig, BotStatus
from bot_service import bot_service
import json

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the bot"""
    success, message = bot_service.start_bot()
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    success, message = bot_service.stop_bot()
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/bot/status')
def get_bot_status():
    """Get bot status"""
    status = bot_service.get_status()
    return jsonify(status)

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    level = request.args.get('level', '')
    
    query = BotLog.query
    if level:
        query = query.filter_by(level=level)
    
    logs = query.order_by(BotLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page,
        'has_next': logs.has_next,
        'has_prev': logs.has_prev
    })

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        config = {
            'delay_seconds': float(BotConfig.get_value('delay_seconds', '15')),
            'delay_between_rounds': float(BotConfig.get_value('delay_between_rounds', '1')),
            'operation_hours': float(BotConfig.get_value('operation_hours', '24'))
        }
        return jsonify(config)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Validate input
        try:
            delay_seconds = float(data.get('delay_seconds', 15))
            delay_between_rounds = float(data.get('delay_between_rounds', 1))
            operation_hours = float(data.get('operation_hours', 24))
            
            # Basic validation
            if delay_seconds < 5:
                return jsonify({'success': False, 'message': 'Delay antar grup minimal 5 detik'}), 400
            if delay_between_rounds < 0.1:
                return jsonify({'success': False, 'message': 'Delay antar putaran minimal 0.1 detik'}), 400
            if operation_hours < 0.1 or operation_hours > 48:
                return jsonify({'success': False, 'message': 'Durasi operasi harus antara 0.1 dan 48 jam'}), 400
            
            # Save configuration
            BotConfig.set_value('delay_seconds', delay_seconds)
            BotConfig.set_value('delay_between_rounds', delay_between_rounds)
            BotConfig.set_value('operation_hours', operation_hours)
            
            return jsonify({
                'success': True,
                'message': 'Konfigurasi berhasil disimpan'
            })
            
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'message': 'Format angka tidak valid'}), 400

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Clear all logs"""
    try:
        BotLog.query.delete()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Log berhasil dihapus'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Gagal menghapus log: {str(e)}'
        }), 500

@app.route('/api/bot/auth', methods=['POST'])
def authenticate_bot():
    """Authenticate bot with verification code"""
    data = request.get_json()
    code = data.get('code', '').strip()
    
    if not code:
        return jsonify({
            'success': False,
            'message': 'Kode verifikasi diperlukan'
        }), 400
    
    try:
        import asyncio
        import os
        from telethon import TelegramClient
        
        # Get credentials
        api_id = int(os.getenv('TELEGRAM_API_ID', '26646846'))
        api_hash = os.getenv('TELEGRAM_API_HASH', '9b49d058f3af38db717ce0768a57a4b2')
        phone = os.getenv('TELEGRAM_PHONE', '+62882002745128')
        
        async def authenticate_with_code():
            client = TelegramClient('session_promo_bot', api_id, api_hash)
            try:
                await client.connect()
                
                # Check if already authorized
                if await client.is_user_authorized():
                    await client.disconnect()
                    return True, "Sudah terautentikasi! Bot siap dijalankan."
                
                # First send code request to get phone_code_hash
                sent_code = await client.send_code_request(phone)
                
                # Now sign in with both code and phone_code_hash
                await client.sign_in(phone=phone, code=code, phone_code_hash=sent_code.phone_code_hash)
                
                if await client.is_user_authorized():
                    await client.disconnect()
                    return True, "Autentikasi berhasil! Bot siap dijalankan."
                else:
                    await client.disconnect()
                    return False, "Autentikasi gagal. Periksa kode verifikasi."
                    
            except Exception as e:
                if client.is_connected():
                    await client.disconnect()
                return False, f"Error autentikasi: {str(e)}"
        
        # Run authentication
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, message = loop.run_until_complete(authenticate_with_code())
        loop.close()
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Gagal autentikasi: {str(e)}'
        }), 500

@app.route('/api/bot/resend-code', methods=['POST'])
def resend_verification_code():
    """Resend verification code to phone number"""
    try:
        import asyncio
        import os
        from telethon import TelegramClient
        
        # Get credentials
        api_id = int(os.getenv('TELEGRAM_API_ID', '26646846'))
        api_hash = os.getenv('TELEGRAM_API_HASH', '9b49d058f3af38db717ce0768a57a4b2')
        phone = os.getenv('TELEGRAM_PHONE', '+62882002745128')
        
        async def send_new_code():
            client = TelegramClient('session_promo_bot', api_id, api_hash)
            try:
                await client.connect()
                
                # Check if already authorized
                if await client.is_user_authorized():
                    await client.disconnect()
                    return True, "Sudah terautentikasi! Tidak perlu kode verifikasi."
                
                # Send new verification code
                sent_code = await client.send_code_request(phone)
                await client.disconnect()
                
                return True, f"Kode verifikasi baru telah dikirim ke {phone}. Periksa SMS atau Telegram app."
                    
            except Exception as e:
                if client.is_connected():
                    await client.disconnect()
                return False, f"Gagal mengirim kode: {str(e)}"
        
        # Run code sending
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, message = loop.run_until_complete(send_new_code())
        loop.close()
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Gagal mengirim kode: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500
