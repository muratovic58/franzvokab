from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, session, jsonify
import os
import csv
import json
from datetime import datetime, timedelta
import random

# Create a simple login form template
LOGIN_TEMPLATE = '''
{% extends "layout.html" %}

{% block title %}Anmelden - VocaFranz{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card shadow">
                <div class="card-body">
                    <h2 class="card-title text-center mb-4">Anmelden</h2>
                    
                    {% with messages = get_flashed_messages() %}
                        {% if messages %}
                            {% for message in messages %}
                                <div class="alert alert-danger">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST" action="{{ url_for('login') }}">
                        <div class="mb-3">
                            <label for="username" class="form-label">Benutzername</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Passwort</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Anmelden</button>
                        </div>
                    </form>
                    
                    <div class="text-center mt-3">
                        <p>Noch kein Konto? <a href="{{ url_for('register') }}">Jetzt registrieren</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# Create a simple register form template
REGISTER_TEMPLATE = '''
{% extends "layout.html" %}

{% block title %}Registrieren - VocaFranz{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card shadow">
                <div class="card-body">
                    <h2 class="card-title text-center mb-4">Registrieren</h2>
                    
                    {% with messages = get_flashed_messages() %}
                        {% if messages %}
                            {% for message in messages %}
                                <div class="alert alert-danger">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST" action="{{ url_for('register') }}">
                        <div class="mb-3">
                            <label for="username" class="form-label">Benutzername</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="email" class="form-label">E-Mail</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Passwort</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password2" class="form-label">Passwort bestätigen</label>
                            <input type="password" class="form-control" id="password2" name="password2" required>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Registrieren</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# User class to handle authentication
class User:
    def __init__(self, username=None):
        self.username = username
        self.is_authenticated = username is not None
        self.id = username  # Use username as ID for simplicity
        
    def is_active(self):
        return self.is_authenticated
        
    def is_anonymous(self):
        return not self.is_authenticated

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Simple user management with JSON file persistence
import json
import os

# File paths for data storage
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
USER_CARDS_FILE = os.path.join(DATA_DIR, 'user_cards.json')
USER_STATS_FILE = os.path.join(DATA_DIR, 'user_stats.json')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Load data from JSON files or initialize empty dictionaries
def load_data():
    global users, user_cards, user_stats
    
    # Load users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    else:
        users = {}
    
    # Load user cards
    if os.path.exists(USER_CARDS_FILE):
        with open(USER_CARDS_FILE, 'r') as f:
            user_cards = json.load(f)
    else:
        user_cards = {}
    
    # Load user stats
    if os.path.exists(USER_STATS_FILE):
        with open(USER_STATS_FILE, 'r') as f:
            user_stats = json.load(f)
    else:
        user_stats = {}

# Save data to JSON files
def save_data():
    # Save users
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    # Save user cards
    with open(USER_CARDS_FILE, 'w') as f:
        json.dump(user_cards, f, indent=2)
    
    # Save user stats
    with open(USER_STATS_FILE, 'w') as f:
        json.dump(user_stats, f, indent=2)

# Initialize data
load_data()

# Register function to save data when application exits
import atexit
atexit.register(save_data)

# Add current_user to template context
@app.context_processor
def inject_user():
    if 'username' in session:
        user = User(session['username'])
    else:
        user = User()
    return {'current_user': user}

def load_vocabulary(chapter=None):
    vocab_dir = os.path.join(os.path.dirname(__file__), 'Karteikarten')
    all_vocab = []
    
    if chapter and chapter != "all":
        file_path = os.path.join(vocab_dir, f'kapitel{chapter}.csv')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                vocab_list = list(reader)
                return vocab_list
    else:
        for i in range(1, 8):
            file_path = os.path.join(vocab_dir, f'kapitel{i}.csv')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    all_vocab.extend(list(reader))
        return all_vocab

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Simple validation
        if not username or not password or not email:
            flash('Bitte alle Felder ausfüllen', 'danger')
            return render_template('register.html')
        
        if username in users:
            flash('Benutzername bereits vergeben', 'danger')
            return render_template('register.html')
        
        # Store user (in a real app, you'd hash the password)
        users[username] = {
            'username': username,
            'password': password,
            'email': email
        }
        
        # Initialize user cards and stats
        user_cards[username] = []
        user_stats[username] = {
            'streak_days': 1,
            'words_reviewed': 0,
            'correct_count': 0,
            'total_words': len(load_vocabulary()),
            'mastered_words': 0,
            'history': [],
            'difficult_words': []
        }
        
        # Save data after registration
        save_data()
        
        flash('Registrierung erfolgreich! Bitte anmelden.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            
            # Make sure user has stats initialized
            if username not in user_stats:
                user_stats[username] = {
                    'streak_days': 1,
                    'words_reviewed': 0,
                    'correct_count': 0,
                    'total_words': len(load_vocabulary()),
                    'mastered_words': 0,
                    'history': [],
                    'difficult_words': []
                }
                save_data()
                
            return redirect(url_for('dashboard'))
        else:
            flash('Ungültiger Benutzername oder Passwort', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Initialize user stats if not exists
    if username not in user_stats:
        user_stats[username] = {
            'streak_days': 1,
            'words_reviewed': 0,
            'correct_count': 0,
            'total_words': len(user_cards.get(username, [])),
            'mastered_words': 0,
            'history': [{'date': datetime.now().date().strftime('%Y-%m-%d'), 'reviewed': 0, 'correct': 0}]
        }
    
    # Generate chart data for the past week
    today = datetime.now().date()
    past_week = [today - timedelta(days=x) for x in range(6, -1, -1)]
    past_week_str = [d.strftime('%Y-%m-%d') for d in past_week]
    
    # Prepare chart data from history
    words_reviewed = [0] * 7
    success_rates = [0] * 7
    
    for entry in user_stats[username]['history']:
        if entry['date'] in past_week_str:
            idx = past_week_str.index(entry['date'])
            words_reviewed[idx] = entry['reviewed']
            success_rates[idx] = round((entry['correct'] / entry['reviewed'] * 100) if entry['reviewed'] > 0 else 0)
    
    chart_data = {
        'labels': [d.strftime('%d.%m') for d in past_week],
        'words_reviewed': words_reviewed,
        'success_rates': success_rates
    }
    
    # Get some difficult words for display
    difficult_words = []
    if username in user_cards and user_cards[username]:
        sample_size = min(5, len(user_cards[username]))
        sample_cards = random.sample(user_cards[username], sample_size)
        difficult_words = [{
            'french_word': card[0],
            'german_word': card[1],
            'incorrect_count': random.randint(1, 5),  # Simulated data
            'error_rate': random.randint(20, 80)  # Simulated error rate as percentage
        } for card in sample_cards]
    
    # Calculate actual success rate and mastery percentage
    success_rate = round((user_stats[username]['correct_count'] / user_stats[username]['words_reviewed'] * 100) 
                      if user_stats[username]['words_reviewed'] > 0 else 0)
    mastery_percentage = round((user_stats[username]['mastered_words'] / user_stats[username]['total_words'] * 100) 
                           if user_stats[username]['total_words'] > 0 else 0)
    
    stats_data = {
        'streak_days': user_stats[username]['streak_days'],
        'words_reviewed': user_stats[username]['words_reviewed'],
        'success_rate': success_rate,
        'mastery_percentage': mastery_percentage,
        'words_mastered': user_stats[username]['mastered_words'],
        'total_words': user_stats[username]['total_words'],
        'due_words': user_stats[username]['total_words'] - user_stats[username]['mastered_words']
    }
    
    return render_template('dashboard.html', 
                           stats=stats_data, 
                           difficult_words=difficult_words, 
                           chart_data=chart_data)

@app.route('/learn')
def learn():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('learn.html')

@app.route('/get-next-card')
def get_next_card():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session['username']
    chapter = request.args.get('chapter', 'all')
    
    vocab_list = load_vocabulary(chapter)
    if not vocab_list:
        return jsonify({'error': 'No vocabulary found'}), 404
    
    # Choose a random card
    card = random.choice(vocab_list)
    
    return jsonify({
        'id': str(vocab_list.index(card)),
        'french': card[0],
        'german': card[1],
        'chapter': chapter
    })

@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

@app.route('/datenschutz')
def datenschutz():
    return render_template('datenschutz.html')

@app.route('/get-vocabulary/<chapter>')
def get_vocabulary(chapter):
    vocab_list = load_vocabulary(chapter)
    return jsonify({'vocabulary': vocab_list})

@app.route('/api/vocab/<chapter>')
def api_vocab(chapter):
    vocab_list = load_vocabulary(chapter)
    return jsonify(vocab_list)

@app.route('/update-progress', methods=['POST'])
def update_progress():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session['username']
    data = request.json
    
    # Update user stats
    if username not in user_stats:
        user_stats[username] = {
            'streak_days': 1,
            'words_reviewed': 0,
            'correct_count': 0,
            'total_words': len(user_cards.get(username, [])),
            'mastered_words': 0,
            'history': [],
            'difficult_words': []
        }
    
    user_stats[username]['words_reviewed'] += 1
    if data.get('correct', False):
        user_stats[username]['correct_count'] += 1
    
    # Update history for today
    today_str = datetime.now().date().strftime('%Y-%m-%d')
    history_entry = None
    
    # Find today's entry or create it
    for entry in user_stats[username]['history']:
        if entry['date'] == today_str:
            history_entry = entry
            break
    
    if not history_entry:
        history_entry = {'date': today_str, 'reviewed': 0, 'correct': 0}
        user_stats[username]['history'].append(history_entry)
    
    # Update today's stats
    history_entry['reviewed'] += 1
    if data.get('correct', False):
        history_entry['correct'] += 1
    
    # Update mastery progress based on actual performance
    if data.get('correct', False):
        # Increase chance of mastering a word when answered correctly
        if random.random() > 0.7:  # 30% chance to master a word when correct
            user_stats[username]['mastered_words'] += 1
    else:
        # Track difficult words
        french_word = data.get('french', '')
        german_word = data.get('german', '')
        
        # Check if word is already in difficult words list
        word_found = False
        for word in user_stats[username].get('difficult_words', []):
            if word['french_word'] == french_word:
                word['error_count'] += 1
                word['total_count'] += 1
                word['error_rate'] = (word['error_count'] / word['total_count']) * 100
                word_found = True
                break
        
        # Add new difficult word if not found
        if not word_found and french_word and german_word:
            user_stats[username].setdefault('difficult_words', []).append({
                'french_word': french_word,
                'german_word': german_word,
                'error_count': 1,
                'total_count': 1,
                'error_rate': 100.0
            })
        
        # Small chance to lose mastery when answered incorrectly
        if random.random() > 0.9 and user_stats[username]['mastered_words'] > 0:  # 10% chance to lose mastery
            user_stats[username]['mastered_words'] -= 1
    
    # Sort difficult words by error rate (highest first)
    if 'difficult_words' in user_stats[username]:
        user_stats[username]['difficult_words'].sort(key=lambda x: x['error_rate'], reverse=True)
        # Keep only top 10 difficult words
        user_stats[username]['difficult_words'] = user_stats[username]['difficult_words'][:10]
    
    # Save data after updating progress
    save_data()
    
    return jsonify({'success': True})

@app.route('/api/user-stats')
def get_user_stats():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session['username']
    
    if username not in user_stats:
        return jsonify({'error': 'No stats available'}), 404
    
    stats = user_stats[username]
    
    # Calculate success rate
    success_rate = 0
    if stats['words_reviewed'] > 0:
        success_rate = (stats['correct_count'] / stats['words_reviewed']) * 100
    
    # Calculate mastery percentage
    mastery_percentage = 0
    if stats['total_words'] > 0:
        mastery_percentage = (stats['mastered_words'] / stats['total_words']) * 100
    
    # Prepare chart data
    chart_data = {
        'labels': [],
        'words_reviewed': [],
        'success_rates': []
    }
    
    # Get the last 7 days of history (or fewer if not available)
    history = sorted(stats['history'], key=lambda x: x['date'], reverse=True)[:7]
    history.reverse()  # Put in chronological order
    
    for entry in history:
        chart_data['labels'].append(entry['date'])
        chart_data['words_reviewed'].append(entry['reviewed'])
        
        # Calculate success rate for this day
        day_success_rate = 0
        if entry['reviewed'] > 0:
            day_success_rate = (entry['correct'] / entry['reviewed']) * 100
        chart_data['success_rates'].append(day_success_rate)
    
    # Get difficult words
    difficult_words = stats.get('difficult_words', [])
    
    return jsonify({
        'words_reviewed': stats['words_reviewed'],
        'success_rate': success_rate,
        'words_mastered': stats['mastered_words'],
        'total_words': stats['total_words'],
        'mastery_percentage': mastery_percentage,
        'streak_days': stats['streak_days'],
        'chart_data': chart_data,
        'difficult_words': difficult_words
    })

@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('settings.html')

@app.route('/leaderboard')
def leaderboard():
    # Get all users with their stats
    leaderboard_data = []
    
    # Debug: Print all user stats
    print("User stats:", user_stats)
    
    # Include all users with stats, even if they're not in the users dictionary
    # This ensures users who have practiced are shown on the leaderboard
    for username, stats in user_stats.items():
        leaderboard_data.append({
            'username': username,
            'words_reviewed': stats.get('words_reviewed', 0),
            'success_rate': stats.get('correct_count', 0) / stats.get('words_reviewed', 1) * 100 if stats.get('words_reviewed', 0) > 0 else 0,
            'streak_days': stats.get('streak_days', 0)
        })
    
    # Sort by words reviewed (descending)
    leaderboard_data.sort(key=lambda x: x['words_reviewed'], reverse=True)
    
    # Get top 5 users
    top_users = leaderboard_data[:5]
    
    # Debug: Print leaderboard data
    print("Leaderboard data:", leaderboard_data)
    print("Top users:", top_users)
    
    return render_template('leaderboard.html', top_users=top_users)

if __name__ == '__main__':
    app.run(debug=True)
