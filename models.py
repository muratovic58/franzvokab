from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    history = db.relationship('LearningHistory', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_authenticated(self):
        return True
        
    def is_active(self):
        return True
        
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return str(self.id)

class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'
    
    id = db.Column(db.Integer, primary_key=True)
    french_word = db.Column(db.String(100), nullable=False)
    german_word = db.Column(db.String(100), nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    progress = db.relationship('UserProgress', backref='vocabulary', lazy=True)

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vocabulary_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id'), nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)
    mastered = db.Column(db.Boolean, default=False)
    last_reviewed = db.Column(db.DateTime)
    next_review = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def error_rate(self):
        total = self.correct_count + self.incorrect_count
        if total == 0:
            return 0
        return (self.incorrect_count / total) * 100

class LearningHistory(db.Model):
    __tablename__ = 'learning_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    words_reviewed = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def success_rate(self):
        if self.words_reviewed == 0:
            return 0
        return (self.correct_count / self.words_reviewed) * 100

class DifficultWord(db.Model):
    __tablename__ = 'difficult_words'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vocabulary_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id'), nullable=False)
    error_count = db.Column(db.Integer, default=0)
    total_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('difficult_words', lazy=True))
    vocabulary = db.relationship('Vocabulary')
    
    @property
    def error_rate(self):
        if self.total_count == 0:
            return 0
        return (self.error_count / self.total_count) * 100
