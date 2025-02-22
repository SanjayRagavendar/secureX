from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('user', 'admin'), default='user')
    experience_points = db.Column(db.Integer, default=0)
    titles = db.Column(db.JSON, default=list)
    tier = db.Column(db.Enum('bronze', 'silver', 'gold', 'platinum', 'diamond'), default='bronze')
    streaks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    submitted_cases = db.relationship('UserScamCase', backref='user', lazy=True)
    gamification_data = db.relationship('Gamification', backref='user', lazy=True)

class ScamCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.Enum('low', 'medium', 'high', 'critical'), nullable=False)
    patterns = db.relationship('ScamPattern', backref='category', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScamPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pattern_name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    common_indicators = db.Column(db.JSON, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('scam_category.id'), nullable=False)
    difficulty_level = db.Column(db.Enum('beginner', 'intermediate', 'advanced'), nullable=False)
    quizzes = db.relationship('Quiz', backref='pattern', lazy=True)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  # in seconds
    completed = db.Column(db.Boolean, default=False)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('multiple_choice', 'true_false', 'scenario_analysis'), nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.JSON, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quiz(db.Model):
    content = db.Column(db.Text, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    scam_pattern_id = db.Column(db.Integer, db.ForeignKey('scam_pattern.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    difficulty_level = db.Column(db.Enum('beginner', 'intermediate', 'advanced'), nullable=False)
    time_limit = db.Column(db.Integer, nullable=True)  # in seconds
    passing_score = db.Column(db.Float, nullable=False, default=70.0)
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True)
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'scam_pattern_id': self.scam_pattern_id,
            'questions': json.dumps(self.questions) if isinstance(self.questions, list) else self.questions,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def deserialize(data):
        questions = data.get('questions', [])
        if isinstance(questions, str):
            try:
                questions = json.loads(questions)
            except json.JSONDecodeError:
                questions = []
        
        return Quiz(
            scam_pattern_id=data.get('scam_pattern_id'),
            questions=questions
        )

class UserScamCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scam_details = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.JSON, default=list)
    ai_verification_status = db.Column(db.Enum('pending', 'verified', 'not_a_scam'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScamDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario_description = db.Column(db.Text, nullable=False)
    ai_analysis_result = db.Column(db.Text, nullable=False)
    is_new_pattern = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Gamification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_mode = db.Column(db.Enum('scam_survival', 'bounty_hunters', 'real_scam_detective', 
                                 'fraud_boss_battles', 'high_stakes_risk'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    badges = db.Column(db.JSON, default=list)
    leaderboard_position = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScamBounty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scam_type = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.Enum('easy', 'medium', 'hard'), nullable=False)
    bounty_points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FraudBossBattle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ai_scam_scenario = db.Column(db.Text, nullable=False)
    possible_responses = db.Column(db.JSON, nullable=False)
    correct_response = db.Column(db.Text, nullable=False)
    ai_tricks_used = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
