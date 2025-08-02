from app import db
from datetime import datetime
from sqlalchemy import Text

class BotLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    level = db.Column(db.String(10), nullable=False)  # INFO, ERROR, WARNING
    message = db.Column(Text, nullable=False)
    group_name = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'level': self.level,
            'message': self.message,
            'group_name': self.group_name
        }

class BotConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(Text, nullable=False)
    
    @staticmethod
    def get_value(key, default=None):
        config = BotConfig.query.filter_by(key=key).first()
        return config.value if config else default
    
    @staticmethod
    def set_value(key, value):
        config = BotConfig.query.filter_by(key=key).first()
        if config:
            config.value = str(value)
        else:
            config = BotConfig(key=key, value=str(value))
            db.session.add(config)
        db.session.commit()

class BotStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=1)
    is_running = db.Column(db.Boolean, default=False, nullable=False)
    start_time = db.Column(db.DateTime)
    stop_time = db.Column(db.DateTime)
    scheduled_stop_time = db.Column(db.DateTime)
    messages_sent = db.Column(db.Integer, default=0)
    rounds_completed = db.Column(db.Integer, default=0)
    
    @staticmethod
    def get_status():
        status = BotStatus.query.first()
        if not status:
            status = BotStatus()
            db.session.add(status)
            db.session.commit()
        return status
