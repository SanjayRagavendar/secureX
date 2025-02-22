from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import db, User, Account, Transaction
from datetime import datetime
from decorators import admin_required, user_account_access
import random
import pandas as pd


api = Blueprint('api', __name__)

# Auth Routes
@api.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    user = User(
        username=data['username'],
        email=data['email'],
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token}), 200

# Account Routes
@api.route('/accounts', methods=['GET'])
@jwt_required()
def get_accounts():
    user_id = get_jwt_identity()
    accounts = Account.query.filter_by(user_id=user_id).all()
    return jsonify([account.to_dict() for account in accounts]), 200

@api.route('/accounts', methods=['POST'])
@jwt_required()
def create_account():
    user_id = get_jwt_identity()
    data = request.get_json()
    account = Account(
        account_number = str(random.randint(100000000000, 999999999999)),
        user_id=user_id,
        account_type=data['account_type'],
        balance=data.get('initial_balance', 0)
    )
    db.session.add(account)
    db.session.commit()
    return jsonify(account.to_dict()), 201

# Transaction Routes
@api.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    data = request.get_json()
    transaction = Transaction(
        from_account_id=data['from_account'],
        to_account_id=data['to_account'],
        amount=data['amount'],
        transaction_type=data['type']
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify(transaction.to_dict()), 201

@api.route('/transactions/<account_id>', methods=['GET'])
@jwt_required()
@user_account_access()
def get_transactions(account_id):
    transactions = Transaction.query.filter(
        (Transaction.from_account_id == account_id) |
        (Transaction.to_account_id == account_id)
    ).all()
    return jsonify([t.to_dict() for t in transactions]), 200

# Balance Routes
@api.route('/accounts/<account_id>/balance', methods=['GET'])
@jwt_required()
@user_account_access()
def get_balance(account_id):
    account = Account.query.get_or_404(account_id)
    return jsonify({"balance": account.balance}), 200

@api.route('/transfer', methods=['POST'])
@jwt_required()
def transfer_money():
    data = request.get_json()
    from_account = Account.query.get_or_404(data['from_account'])
    to_account = Account.query.get_or_404(data['to_account'])
    amount = data['amount']

    if from_account.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    # Predict fraud probability
    fraud_probability = preprocess_transaction(data)
    is_fraud = fraud_probability > 0.5

    # Store transaction in the database
    transaction = Transaction(
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        amount=amount,
        risk_score=fraud_probability,
        is_flagged=is_fraud,
        flag_reason="High Fraud Risk" if is_fraud else None
    )

    db.session.add(transaction)

    if is_fraud:
        return jsonify({
            "message": "Transaction flagged as suspicious",
            "fraud_probability": fraud_probability,
            "status": "Needs Review"
        }), 403

    from_account.balance -= amount
    to_account.balance += amount
    db.session.commit()

    return jsonify({
        "message": "Transfer successful",
        "fraud_probability": fraud_probability,
        "status": "Approved"
    }), 200

# Admin Routes
@api.route('/admin/transactions', methods=['GET'])
@admin_required()
def get_all_transactions():
    transactions = Transaction.query.all()
    return jsonify([t.to_dict() for t in transactions]), 200

@api.route('/admin/transactions/flagged', methods=['GET'])
@admin_required()
def get_flagged_transactions():
    flagged = Transaction.query.filter_by(is_flagged=True).all()
    return jsonify([t.to_dict() for t in flagged]), 200

@api.route('/admin/accounts', methods=['GET'])
@admin_required()
def get_all_accounts():
    accounts = Account.query.all()
    return jsonify([account.to_dict() for account in accounts]), 200

@api.route('/admin/users', methods=['GET'])
@admin_required()
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@api.route('/admin/transactions/<transaction_id>/flag', methods=['POST'])
@admin_required()
def flag_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    transaction.is_flagged = True
    transaction.flag_reason = request.json.get('reason', 'Suspicious activity')
    db.session.commit()
    return jsonify({"message": "Transaction flagged successfully"}), 200

@api.route('/admin/analytics/suspicious', methods=['GET'])
@admin_required()
def get_suspicious_activity():
    # Add logic to detect suspicious patterns
    large_transactions = Transaction.query.filter(Transaction.amount > 10000).all()
    frequent_transactions = Transaction.query\
        .filter(Transaction.created_at >= datetime.utcnow().date())\
        .group_by(Transaction.from_account_id)\
        .having(db.func.count() > 10)\
        .all()
    
    return jsonify({
        "large_transactions": [t.to_dict() for t in large_transactions],
        "frequent_transactions": [t.to_dict() for t in frequent_transactions]
    }), 200
