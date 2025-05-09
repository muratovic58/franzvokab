import os
import csv
from app import app, db
from models import User, Vocabulary, UserProgress, LearningHistory, DifficultWord

def setup_database():
    """Initialize the database with tables and import vocabulary"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Only import vocabulary if the table is empty
        if Vocabulary.query.count() == 0:
            print("Importing vocabulary from CSV files...")
            vocab_dir = os.path.join(os.path.dirname(__file__), 'Karteikarten')
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
            print(f"Imported {Vocabulary.query.count()} vocabulary items")
        else:
            print(f"Vocabulary already exists: {Vocabulary.query.count()} items")

if __name__ == "__main__":
    setup_database()
    print("Database setup complete!")
