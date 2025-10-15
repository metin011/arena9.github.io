from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///football_stats.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50))
    team = db.Column(db.String(100))
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    matches_played = db.Column(db.Integer, default=0)
    photo_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    match_date = db.Column(db.DateTime, nullable=False)
    stadium = db.Column(db.String(100))
    status = db.Column(db.String(20), default='scheduled')  # scheduled, live, finished
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    matches = Match.query.order_by(Match.match_date.desc()).limit(10).all()
    players = Player.query.order_by(Player.goals.desc()).limit(8).all()
    return render_template('index.html', matches=matches, players=players)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('index'))

@app.route('/matches')
def matches():
    all_matches = Match.query.order_by(Match.match_date.desc()).all()
    return render_template('matches.html', matches=all_matches)

@app.route('/players')
def players():
    all_players = Player.query.order_by(Player.goals.desc()).all()
    return render_template('players.html', players=all_players)

# Admin Routes
@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('index'))
    
    matches = Match.query.order_by(Match.match_date.desc()).all()
    players = Player.query.order_by(Player.name).all()
    users = User.query.all()
    
    return render_template('admin.html', matches=matches, players=players, users=users)

@app.route('/admin/match/add', methods=['POST'])
def add_match():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.form
    new_match = Match(
        home_team=data.get('home_team'),
        away_team=data.get('away_team'),
        home_score=int(data.get('home_score', 0)),
        away_score=int(data.get('away_score', 0)),
        match_date=datetime.strptime(data.get('match_date'), '%Y-%m-%dT%H:%M'),
        stadium=data.get('stadium'),
        status=data.get('status', 'scheduled')
    )
    db.session.add(new_match)
    db.session.commit()
    
    flash('Maç başarıyla eklendi!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/match/edit/<int:match_id>', methods=['POST'])
def edit_match(match_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    match = Match.query.get_or_404(match_id)
    data = request.form
    
    match.home_team = data.get('home_team')
    match.away_team = data.get('away_team')
    match.home_score = int(data.get('home_score', 0))
    match.away_score = int(data.get('away_score', 0))
    match.match_date = datetime.strptime(data.get('match_date'), '%Y-%m-%dT%H:%M')
    match.stadium = data.get('stadium')
    match.status = data.get('status')
    
    db.session.commit()
    flash('Maç güncellendi!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/match/delete/<int:match_id>', methods=['POST'])
def delete_match(match_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    
    flash('Maç silindi!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/player/add', methods=['POST'])
def add_player():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.form
    new_player = Player(
        name=data.get('name'),
        position=data.get('position'),
        team=data.get('team'),
        goals=int(data.get('goals', 0)),
        assists=int(data.get('assists', 0)),
        matches_played=int(data.get('matches_played', 0)),
        photo_url=data.get('photo_url')
    )
    db.session.add(new_player)
    db.session.commit()
    
    flash('Oyuncu başarıyla eklendi!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/player/edit/<int:player_id>', methods=['POST'])
def edit_player(player_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    player = Player.query.get_or_404(player_id)
    data = request.form
    
    player.name = data.get('name')
    player.position = data.get('position')
    player.team = data.get('team')
    player.goals = int(data.get('goals', 0))
    player.assists = int(data.get('assists', 0))
    player.matches_played = int(data.get('matches_played', 0))
    player.photo_url = data.get('photo_url')
    
    db.session.commit()
    flash('Oyuncu güncellendi!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/player/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    
    flash('Oyuncu silindi!', 'success')
    return redirect(url_for('admin_panel'))

# Initialize database and create admin user
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
