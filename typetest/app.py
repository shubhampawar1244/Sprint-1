from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
from constants import SAMPLE_TEXTS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    scores = db.relationship('Score', backref='user', lazy=True)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wpm = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    mistakes = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name}), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return jsonify({'id': user.id, 'name': user.name}), 200
    return jsonify({'error': 'Invalid email or password'}), 400

@app.route('/api/get-text')
def get_text():
    difficulty = request.args.get('difficulty', 'medium').lower()  # Default to medium
    if difficulty not in SAMPLE_TEXTS:
        difficulty = 'medium'  # Fallback to medium if invalid
    text = random.choice(SAMPLE_TEXTS[difficulty])
    return jsonify({'text': text})

@app.route('/api/save-score', methods=['POST'])
def save_score():
    data = request.get_json()
    user_id = data.get('userId')
    wpm = data.get('wpm')
    accuracy = data.get('accuracy')
    mistakes = data.get('mistakes')
    duration = data.get('duration')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 400

    score = Score(user_id=user_id, wpm=wpm, accuracy=accuracy, mistakes=mistakes, duration=duration)
    db.session.add(score)
    db.session.commit()
    return jsonify({'status': 'success'}), 201

@app.route('/api/scores/<int:user_id>')
def get_scores(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 400

    scores = Score.query.filter_by(user_id=user_id).order_by(Score.date.desc()).all()
    scores_data = [
        {
            'wpm': score.wpm,
            'accuracy': score.accuracy,
            'mistakes': score.mistakes,
            'duration': score.duration,
            'date': score.date.isoformat()
        }
        for score in scores
    ]
    return jsonify(scores_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)