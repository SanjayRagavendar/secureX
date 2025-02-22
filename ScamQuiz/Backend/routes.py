from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import (
    db, User, Quiz, QuizAttempt, ScamCategory, ScamPattern,
    UserScamCase, ScamDetection, Gamification, ScamBounty, FraudBossBattle
)
from datetime import datetime
from functools import wraps
from flask_jwt_extended import jwt_required, create_access_token
import os
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

api = Blueprint('api', __name__)

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            verify_jwt_in_request()
            current_user = User.query.get(get_jwt_identity())
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Auth Routes
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        token = create_access_token(identity=user.id, additional_claims={'first_name': user.name, 'role': user.role})
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# Quiz Routes
@api.route('/quizzes', methods=['GET'])
@token_required
def get_quizzes(current_user):
    quizzes = Quiz.query.all()
    return jsonify([quiz.serialize() for quiz in quizzes])

@api.route('/quizzes/<int:quiz_id>', methods=['GET'])
@token_required
def get_quiz(current_user, quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify(quiz.serialize())

@api.route('/quiz-attempts', methods=['POST'])
@token_required
def submit_quiz_attempt(current_user):
    data = request.get_json()
    new_attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=data['quiz_id'],
        score=data['score'],
        answers=data['answers'],
        time_taken=data['time_taken'],
        completed=True
    )
    db.session.add(new_attempt)
    db.session.commit()
    return jsonify({'message': 'Quiz attempt submitted successfully'}), 201

# Scam Case Routes
@api.route('/scam-cases', methods=['POST'])
@token_required
def submit_scam_case(current_user):
    data = request.get_json()
    new_case = UserScamCase(
        user_id=current_user.id,
        scam_details=data['scam_details'],
        evidence=data['evidence']
    )
    db.session.add(new_case)
    db.session.commit()
    return jsonify({'message': 'Scam case submitted successfully'}), 201

# Gamification Routes
@api.route('/gamification/progress', methods=['GET'])
@token_required
def get_gamification_progress(current_user):
    progress = Gamification.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'game_mode': p.game_mode,
        'progress': p.progress,
        'score': p.score,
        'badges': p.badges
    } for p in progress])

@api.route('/bounties', methods=['GET'])
@token_required
def get_bounties(current_user):
    bounties = ScamBounty.query.all()
    return jsonify([{
        'id': b.id,
        'scam_type': b.scam_type,
        'difficulty_level': b.difficulty_level,
        'bounty_points': b.bounty_points
    } for b in bounties])

# Boss Battle Routes
@api.route('/boss-battles', methods=['GET'])
@token_required
def get_boss_battles(current_user):
    battles = FraudBossBattle.query.all()
    return jsonify([{
        'id': b.id,
        'ai_scam_scenario': b.ai_scam_scenario,
        'possible_responses': b.possible_responses
    } for b in battles])

# User Profile Routes
@api.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'name': current_user.name,
        'email': current_user.email,
        'experience_points': current_user.experience_points,
        'titles': current_user.titles,
        'streaks': current_user.streaks,
        'tier': current_user.tier
    })

@api.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    if 'name' in data:
        current_user.name = data['name']
    if 'email' in data:
        current_user.email = data['email']
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

