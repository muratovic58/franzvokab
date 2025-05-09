# FranzVokab - Französisch Vokabeltrainer

Ein interaktiver Französisch Vokabeltrainer für die 8. Klasse mit Karteikartensystem und SQL-Datenbankanbindung.

## Technologie-Stack

- **Backend**: Flask (Python)
- **Datenbank**: PostgreSQL (auf Railway)
- **Hosting**: Vercel (Serverless)
- **Authentifizierung**: Flask-Login
- **ORM**: SQLAlchemy
- **Migrationen**: Flask-Migrate

## Deployment auf Railway und Vercel

### Voraussetzungen

- Ein [GitHub](https://github.com/) Account
- Ein [Vercel](https://vercel.com/) Account (kostenlos erhältlich)
- Ein [Railway](https://railway.app/) Account (kostenlos erhältlich)
- [Git](https://git-scm.com/) auf deinem Computer installiert

### Schritt 1: PostgreSQL-Datenbank auf Railway einrichten

1. **Registriere dich bei Railway**
   - Gehe zu [Railway](https://railway.app/) und erstelle ein Konto (oder melde dich an)
   - Du kannst dich mit GitHub anmelden

2. **Erstelle ein neues PostgreSQL-Projekt**
   - Klicke auf "New Project"
   - Wähle "Provision PostgreSQL"
   - Warte, bis die Datenbank erstellt wurde

3. **Verbindungsdaten abrufen**
   - Klicke auf deine PostgreSQL-Datenbank
   - Gehe zum Tab "Connect"
   - Kopiere die Verbindungs-URL (Connection URL)
   - Diese URL hat das Format: `postgresql://postgres:password@containers-us-west-123.railway.app:7890/railway`

### Schritt 2: Code auf GitHub hochladen

1. **Erstelle ein GitHub Repository**
   - Gehe zu [GitHub](https://github.com/) und melde dich an
   - Klicke auf "New repository"
   - Gib einen Namen für dein Repository ein (z.B. "franzvokab")
   - Wähle "Public" oder "Private"
   - Klicke auf "Create repository"

2. **Lade deinen Code auf GitHub hoch**

   ```bash
   # Navigiere zum Projektverzeichnis
   cd pfad/zu/franzvokab

   # Initialisiere ein Git-Repository
   git init

   # Füge alle Dateien hinzu
   git add .

   # Erstelle einen Commit
   git commit -m "Initial commit"

   # Verbinde mit deinem GitHub-Repository (ersetze USERNAME und REPO_NAME)
   git remote add origin https://github.com/USERNAME/REPO_NAME.git

   # Lade den Code hoch
   git push -u origin main
   ```

### Schritt 3: Deploye auf Vercel

1. **Registriere dich bei Vercel**
   - Gehe zu [Vercel](https://vercel.com/) und erstelle ein Konto
   - Du kannst dich mit GitHub anmelden

2. **Importiere dein GitHub-Repository**
   - Klicke auf "New Project"
   - Wähle dein GitHub-Repository aus der Liste
   - Vercel erkennt automatisch, dass es sich um ein Python-Projekt handelt

3. **Konfiguriere das Projekt**
   - **Framework Preset**: Wähle "Other"
   - **Build Command**: Lasse dieses Feld leer
   - **Output Directory**: Lasse dieses Feld leer
   - **Install Command**: `pip install -r requirements.txt`

4. **Umgebungsvariablen einrichten**
   - Klicke auf "Environment Variables"
   - Füge die folgenden Variablen hinzu:
     - `FLASK_SECRET_KEY`: Ein sicherer zufälliger String (z.B. generiert mit `openssl rand -hex 32`)
     - `DATABASE_URL`: Die PostgreSQL-Verbindungs-URL von Railway
     - `FLASK_ENV`: `production`

5. **Deploye das Projekt**
   - Klicke auf "Deploy"
   - Warte, bis das Deployment abgeschlossen ist

### Schritt 4: Datenbank initialisieren

Nach dem Deployment müssen wir die Datenbank initialisieren:

1. **Installiere Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Melde dich bei Vercel an**
   ```bash
   vercel login
   ```

3. **Führe das Datenbanksetup aus**
   ```bash
   vercel env pull .env.local  # Lädt die Umgebungsvariablen herunter
   python setup_db.py          # Initialisiert die Datenbank
   ```

### Schritt 5: Überprüfe die Anwendung

- Öffne die von Vercel bereitgestellte URL (z.B. `https://franzvokab.vercel.app`)
- Registriere einen Benutzer und teste die Anwendung
- Überprüfe, ob die Daten korrekt in der Datenbank gespeichert werden

## SQL-Funktionen und Datenbankstruktur

Die Anwendung verwendet folgende Tabellen:

1. **users** - Benutzerinformationen
   - id (PK)
   - username
   - password (gehasht)
   - email
   - created_at

2. **vocabulary** - Vokabeln
   - id (PK)
   - french_word
   - german_word
   - chapter
   - created_at

3. **user_progress** - Lernfortschritt
   - id (PK)
   - user_id (FK)
   - vocabulary_id (FK)
   - correct_count
   - incorrect_count
   - mastered
   - last_reviewed
   - next_review
   - created_at

4. **learning_history** - Lernverlauf
   - id (PK)
   - user_id (FK)
   - date
   - words_reviewed
   - correct_count
   - created_at

5. **difficult_words** - Schwierige Wörter
   - id (PK)
   - user_id (FK)
   - vocabulary_id (FK)
   - error_count
   - total_count
   - created_at

## Lokale Entwicklung

Um die Anwendung lokal zu entwickeln:

1. **Erstelle eine lokale PostgreSQL-Datenbank** oder verwende SQLite für die Entwicklung

2. **Erstelle eine .env-Datei** basierend auf .env.example
   ```
   cp .env.example .env
   # Bearbeite die .env-Datei mit deinen Daten
   ```

3. **Installiere die Abhängigkeiten**
   ```
   pip install -r requirements.txt
   ```

4. **Initialisiere die Datenbank**
   ```
   python setup_db.py
   ```

5. **Starte die Anwendung**
   ```
   python app.py
   ```

6. **Öffne die Anwendung** im Browser unter `http://127.0.0.1:5000`

## Migrationen verwalten

Wenn du Änderungen am Datenbankschema vornimmst:

```bash
# Installiere Flask-Migrate und Flask-Script
pip install Flask-Migrate Flask-Script

# Initialisiere Migrationen (nur beim ersten Mal)
python -c "from app import app, db; from flask_migrate import Migrate, init; migrate = Migrate(app, db); init()"

# Erstelle eine neue Migration
python -c "from app import app, db; from flask_migrate import Migrate, migrate; migrate = Migrate(app, db); migrate()"

# Führe die Migration aus
python -c "from app import app, db; from flask_migrate import Migrate, upgrade; migrate = Migrate(app, db); upgrade()"
```
