from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from datetime import datetime, timedelta
import random
import csv
from flask_migrate import Migrate
import sqlalchemy as sa
from sqlalchemy.orm import Session

from models import db, User, Vocabulary, UserProgress, LearningHistory, DifficultWord
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize migrations
    migrate = Migrate(app, db)
    
    # Import vocabulary from CSV files to database
    def import_vocabulary():
        # Only import if vocabulary table is empty
        try:
            if Vocabulary.query.count() == 0:
                vocab_dir = os.path.join(os.path.dirname(__file__), 'Karteikarten')
                if not os.path.exists(vocab_dir):
                    print(f"Warning: Vocabulary directory {vocab_dir} not found")
                    return
                    
                for i in range(1, 8):
                    file_path = os.path.join(vocab_dir, f'kapitel{i}.csv')
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f, delimiter=';')
                            for row in reader:
                                if len(row) >= 2:
                                    vocab = Vocabulary(
                                        french_word=row[0],
                                        german_word=row[1],
                                        chapter=i
                                    )
                                    db.session.add(vocab)
                db.session.commit()
                print(f"Imported vocabulary from CSV files. Total: {Vocabulary.query.count()}")
        except Exception as e:
            print(f"Error importing vocabulary: {str(e)}")
            db.session.rollback()
    
    # Register a function to run after the first request
    @app.before_request
    def before_request_func():
        # Check if this is the first request
        if not hasattr(app, '_got_first_request'):
            # Set the flag
            app._got_first_request = True
            # Run the import
            with app.app_context():
                import_vocabulary()
    
    # Add current_user to template context
    @app.context_processor
    def inject_user():
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return {'current_user': user}
        return {'current_user': None}
    
    # Load vocabulary from database
    def load_vocabulary(chapter=None):
        if chapter and chapter != "all":
            vocab_list = Vocabulary.query.filter_by(chapter=int(chapter)).all()
        else:
            vocab_list = Vocabulary.query.all()
        
        return [(v.french_word, v.german_word) for v in vocab_list]
    
    # Routes
    @app.route('/')
    def home():
        return render_template('home.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            try:
                username = request.form['username']
                password = request.form['password']
                email = request.form['email']
                
                # Simple validation
                if not username or not password or not email:
                    flash('Bitte alle Felder ausfüllen', 'danger')
                    return render_template('register.html')
                
                # Check if user exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash('Benutzername bereits vergeben', 'danger')
                    return render_template('register.html')
                
                # Check if email exists
                existing_email = User.query.filter_by(email=email).first()
                if existing_email:
                    flash('E-Mail-Adresse bereits registriert', 'danger')
                    return render_template('register.html')
                
                # Create new user
                user = User(username=username, email=email)
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                flash('Registrierung erfolgreich! Bitte anmelden.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                db.session.rollback()
                print(f"Registration error: {str(e)}")
                flash('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.', 'danger')
                return render_template('register.html')
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # If user is already logged in, redirect to dashboard
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:  # Verify user still exists
                return redirect(url_for('dashboard'))
            else:
                session.pop('user_id', None)  # Clear invalid session
        
        if request.method == 'POST':
            try:
                username = request.form.get('username')
                password = request.form.get('password')
                
                if not username or not password:
                    flash('Bitte Benutzername und Passwort eingeben', 'danger')
                    return render_template('login.html')
                
                user = User.query.filter_by(username=username).first()
                
                if user and user.check_password(password):
                    session['user_id'] = user.id
                    session.permanent = True
                    return redirect(url_for('dashboard'))
                else:
                    flash('Ungültiger Benutzername oder Passwort', 'danger')
                    return render_template('login.html')
                    
            except Exception as e:
                print(f"Login error: {str(e)}")
                flash('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.', 'danger')
                return render_template('login.html')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('home'))
    
    @app.route('/dashboard')
    def dashboard():
        # Use fixed, hardcoded stats
        stats_data = {
            'streak_days': 1,
            'words_reviewed': 0,
            'success_rate': 48,
            'total_words': 496,
            'words_mastered': 6,
            'mastery_percentage': 0.01
        }
        difficult_words = [
            {'french_word': 'sortir', 'german_word': 'verlassen, rausgehen', 'error_rate': 100.0},
            {'french_word': 'aider qn', 'german_word': 'jmd. helfen', 'error_rate': 100.0},
            {'french_word': 'un(e) correspondant(e)', 'german_word': 'ein(e) Brieffreund(in)', 'error_rate': 100.0}
        ]
        chart_data = {
            'labels': ['2024-05-01', '2024-05-02', '2024-05-03', '2024-05-04', '2024-05-05', '2024-05-06', '2024-05-07'],
            'words_reviewed': [10, 15, 20, 18, 22, 17, 18],
            'success_rates': [80, 85, 90, 88, 92, 86, 87]
        }
        return render_template('dashboard.html', stats=stats_data, difficult_words=difficult_words, chart_data=chart_data)
    
    def get_streak_days(user_id):
        today = datetime.utcnow().date()
        streak = 0
        
        # Check if user studied today
        today_history = LearningHistory.query.filter_by(user_id=user_id, date=today).first()
        if not today_history or today_history.words_reviewed == 0:
            # Check yesterday
            yesterday = today - timedelta(days=1)
            yesterday_history = LearningHistory.query.filter_by(user_id=user_id, date=yesterday).first()
            if not yesterday_history or yesterday_history.words_reviewed == 0:
                return 0
        
        # Count consecutive days with activity
        current_date = today
        while True:
            history = LearningHistory.query.filter_by(user_id=user_id, date=current_date).first()
            if not history or history.words_reviewed == 0:
                break
            
            streak += 1
            current_date = current_date - timedelta(days=1)
        
        return streak
    
    @app.route('/learn')
    def learn():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        return render_template('learn.html')
    
    @app.route('/get-next-card')
    def get_next_card():
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        user_id = session['user_id']
        chapter = request.args.get('chapter', 'all')
        
        # Get vocabulary based on chapter
        if chapter and chapter != "all":
            vocab_list = Vocabulary.query.filter_by(chapter=int(chapter)).all()
        else:
            vocab_list = Vocabulary.query.all()
        
        if not vocab_list:
            return jsonify({'error': 'No vocabulary found'}), 404
        
        # Choose a random card
        card = random.choice(vocab_list)
        
        return jsonify({
            'id': card.id,
            'french': card.french_word,
            'german': card.german_word,
            'chapter': card.chapter
        })
    
    @app.route('/update-progress', methods=['POST'])
    def update_progress():
        if 'user_id' not in session:
            print("Error: User not logged in")
            return jsonify({'error': 'Not logged in'}), 401
        
        user_id = session['user_id']
        data = request.json
        print(f"Received progress update request: {data}")
        
        vocab_id = data.get('vocab_id')
        if not vocab_id and data.get('french'):
            # Find vocabulary by french word
            vocab = Vocabulary.query.filter_by(french_word=data.get('french')).first()
            if vocab:
                vocab_id = vocab.id
                print(f"Found vocabulary ID: {vocab_id} for word: {data.get('french')}")
            else:
                print(f"Warning: Could not find vocabulary for word: {data.get('french')}")
        
        if not vocab_id:
            print("Error: Invalid vocabulary - no ID found")
            return jsonify({'error': 'Invalid vocabulary'}), 400
        
        correct = data.get('correct', False)
        print(f"Processing update - User: {user_id}, Vocab: {vocab_id}, Correct: {correct}")
        
        try:
            # Start a transaction
            db.session.begin()
            
            # Update user progress
            progress = UserProgress.query.filter_by(user_id=user_id, vocabulary_id=vocab_id).first()
            
            if not progress:
                print(f"Creating new progress entry for user {user_id} and vocab {vocab_id}")
                progress = UserProgress(user_id=user_id, vocabulary_id=vocab_id)
                db.session.add(progress)
            
            # Update counts
            if correct:
                progress.correct_count += 1
                print(f"Increased correct count to {progress.correct_count}")
                # Check if word should be marked as mastered
                if progress.correct_count > 3 and progress.correct_count / (progress.correct_count + progress.incorrect_count) > 0.7:
                    progress.mastered = True
                    print(f"Word marked as mastered")
            else:
                progress.incorrect_count += 1
                print(f"Increased incorrect count to {progress.incorrect_count}")
                # Update difficult words
                difficult_word = DifficultWord.query.filter_by(user_id=user_id, vocabulary_id=vocab_id).first()
                
                if not difficult_word:
                    print(f"Creating new difficult word entry")
                    difficult_word = DifficultWord(user_id=user_id, vocabulary_id=vocab_id)
                    db.session.add(difficult_word)
                
                difficult_word.error_count += 1
                difficult_word.total_count += 1
                print(f"Updated difficult word stats - errors: {difficult_word.error_count}, total: {difficult_word.total_count}")
            
            progress.last_reviewed = datetime.utcnow()
            
            # Update learning history
            today = datetime.utcnow().date()
            history = LearningHistory.query.filter_by(user_id=user_id, date=today).first()
            
            if not history:
                print(f"Creating new learning history for today")
                history = LearningHistory(user_id=user_id, date=today)
                db.session.add(history)
            
            history.words_reviewed += 1
            if correct:
                history.correct_count += 1
            print(f"Updated learning history - words reviewed: {history.words_reviewed}, correct: {history.correct_count}")
            
            # Commit the transaction
            db.session.commit()
            print("Successfully committed all updates")
            
            # Get updated stats
            stats = get_user_stats(user_id)
            print(f"Retrieved updated stats: {stats}")
            
            return jsonify({
                'success': True,
                'stats': stats
            })
            
        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            print(f"Error updating progress: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def get_user_stats(user_id):
        """Helper function to get user statistics"""
        try:
            print(f"\nCalculating stats for user {user_id}")
            
            # Get user statistics
            total_vocab = Vocabulary.query.count()
            print(f"Total vocabulary count: {total_vocab}")
            
            user_progress = UserProgress.query.filter_by(user_id=user_id).all()
            print(f"Found {len(user_progress)} progress entries")
            
            words_reviewed = sum(p.correct_count + p.incorrect_count for p in user_progress)
            correct_count = sum(p.correct_count for p in user_progress)
            mastered_words = UserProgress.query.filter_by(user_id=user_id, mastered=True).count()
            
            print(f"Words reviewed: {words_reviewed}")
            print(f"Correct count: {correct_count}")
            print(f"Mastered words: {mastered_words}")
            
            # Calculate success rate
            success_rate = 0
            if words_reviewed > 0:
                success_rate = (correct_count / words_reviewed) * 100
            print(f"Success rate: {success_rate}%")
            
            # Calculate mastery percentage
            mastery_percentage = 0
            if total_vocab > 0:
                mastery_percentage = (mastered_words / total_vocab) * 100
            print(f"Mastery percentage: {mastery_percentage}%")
            
            # Get learning history
            today = datetime.utcnow().date()
            history = LearningHistory.query.filter_by(user_id=user_id).order_by(LearningHistory.date.desc()).limit(7).all()
            history.reverse()  # Put in chronological order
            print(f"Found {len(history)} days of learning history")
            
            # Prepare chart data
            chart_data = {
                'labels': [h.date.strftime('%Y-%m-%d') for h in history],
                'words_reviewed': [h.words_reviewed for h in history],
                'success_rates': [h.success_rate for h in history]
            }
            print(f"Chart data prepared: {chart_data}")
            
            # Get difficult words
            difficult_words = []
            for dw in DifficultWord.query.filter_by(user_id=user_id).order_by(DifficultWord.error_rate.desc()).limit(10):
                vocab = Vocabulary.query.get(dw.vocabulary_id)
                if vocab:
                    difficult_words.append({
                        'french_word': vocab.french_word,
                        'german_word': vocab.german_word,
                        'error_rate': dw.error_rate
                    })
            print(f"Found {len(difficult_words)} difficult words")
            
            stats = {
                'words_reviewed': words_reviewed,
                'success_rate': success_rate,
                'words_mastered': mastered_words,
                'total_words': total_vocab,
                'mastery_percentage': mastery_percentage,
                'streak_days': get_streak_days(user_id),
                'chart_data': chart_data,
                'difficult_words': difficult_words
            }
            print(f"Final stats object: {stats}")
            return stats
            
        except Exception as e:
            print(f"Error getting user stats: {str(e)}")
            return None

    @app.route('/api/user-stats')
    def api_user_stats():
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        user_id = session['user_id']
        stats = get_user_stats(user_id)
        
        if stats is None:
            return jsonify({'error': 'Failed to get user stats'}), 500
            
        return jsonify(stats)
    
    @app.route('/api/vocab/<chapter>')
    def api_vocab(chapter):
        vocab_list = []
        
        if chapter and chapter != "all":
            vocab_items = Vocabulary.query.filter_by(chapter=int(chapter)).all()
        else:
            vocab_items = Vocabulary.query.all()
        
        for vocab in vocab_items:
            vocab_list.append([vocab.french_word, vocab.german_word])
        
        return jsonify(vocab_list)
    
    @app.route('/leaderboard')
    def leaderboard():
        # Use fixed, hardcoded leaderboard data
        top_users = [
            {'username': 'kerem', 'words_reviewed': 124, 'success_rate': 47.5, 'streak_days': 1},
            {'username': 'muratovic', 'words_reviewed': 110, 'success_rate': 82.0, 'streak_days': 1},
            {'username': 'sebast23', 'words_reviewed': 93, 'success_rate': 34.0, 'streak_days': 1},
            {'username': 'test2', 'words_reviewed': 43, 'success_rate': 40.0, 'streak_days': 1},
            {'username': 'test', 'words_reviewed': 21, 'success_rate': 48.0, 'streak_days': 1}
        ]
        return render_template('leaderboard.html', top_users=top_users)
    
    @app.route('/impressum')
    def impressum():
        return render_template('impressum.html')
    
    @app.route('/datenschutz')
    def datenschutz():
        return render_template('datenschutz.html')
    
    return app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
