from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.Enum('admin', 'user'), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accounts = db.relationship('Account', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    account_type = db.Column(db.Enum('Savings', 'Current'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    transactions_sent = db.relationship('Transaction',
                                      foreign_keys='Transaction.from_account_id',
                                      backref='sender',
                                      lazy=True)
    transactions_received = db.relationship('Transaction',
                                          foreign_keys='Transaction.to_account_id',
                                          backref='receiver',
                                          lazy=True)
    cards = db.relationship('Card', backref='account', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'account_number': "X"*8+self.account_number[:4],
            'balance': self.balance,
            'account_type': self.account_type,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    risk_score = db.Column(db.Float, nullable=True)
    is_blocked = db.Column(db.Boolean, default=False)
    ml_analysis_timestamp = db.Column(db.DateTime, nullable=True)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships with explicit foreign keys
    from_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    def get_hour_of_day(self):
        return self.timestamp.hour

    def get_day_of_week(self):
        return self.timestamp.weekday()

    def analyze_risk(self, ml_service):
        # Get user history
        user_history = TransactionHistory.get_user_history(self.account.user_id)
        
        # Perform ML analysis
        analysis = ml_service.analyze_transaction(self, user_history)
        self.risk_score = analysis['risk_score']
        self.model_inference = analysis['inference']
        self.is_blocked = analysis['is_suspicious']  
        self.ml_analysis_timestamp = analysis['timestamp']
        
        return self.is_blocked

    def to_dict(self):
        return {
            'id': self.id,
            'from_account': self.from_account_id,
            'to_account': self.to_account_id,
            'amount': self.amount,
            'type': self.transaction_type,
            'is_flagged': self.is_flagged,
            'flag_reason': self.flag_reason,
            'timestamp': self.timestamp.isoformat(),
            'created_at': self.created_at.isoformat()
        }

class TransactionHistory:
    @staticmethod
    def get_user_history(user_id):
        recent_transactions = Transaction.query.join(Account).filter(
            Account.user_id == user_id
        ).order_by(Transaction.timestamp.desc()).limit(100).all()
        
        return {
            'transactions': recent_transactions,
            'get_average_transaction_amount': lambda: sum(t.amount for t in recent_transactions) / len(recent_transactions) if recent_transactions else 0,
            'get_transaction_frequency': lambda: len(recent_transactions)
        }

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), unique=True, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    card_type = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    #relationships
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
