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
    position = db.Column(db.String(50))  # Ana pozisyon
    team = db.Column(db.String(100))
    jersey_number = db.Column(db.Integer, default=0)
    age = db.Column(db.Integer, default=0)
    photo_url = db.Column(db.String(200))
    
    # Genel istatistikler
    overall_rating = db.Column(db.Integer, default=0)
    
    # Mevki haritası (JSON formatında: {"ST": "green", "CF": "light-green", "LW": "yellow"})
    position_map = db.Column(db.Text, default='{}')
    
    # Ana yetenekler
    pace = db.Column(db.Integer, default=0)
    shooting = db.Column(db.Integer, default=0)
    passing = db.Column(db.Integer, default=0)
    dribbling = db.Column(db.Integer, default=0)
    defending = db.Column(db.Integer, default=0)
    physical = db.Column(db.Integer, default=0)
    
    # Detaylı yetenekler (JSON formatında)
    detailed_skills = db.Column(db.Text, default='{}')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    season_stats = db.relationship('SeasonStats', backref='player', lazy=True, cascade='all, delete-orphan')

class SeasonStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    season = db.Column(db.String(20), nullable=False)  # Örnek: "21/22"
    matches = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))  # Maç adı
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    match_date = db.Column(db.DateTime, nullable=False)
    match_time = db.Column(db.String(10))  # Saat
    stadium = db.Column(db.String(100))
    status = db.Column(db.String(20), default='finished')  # scheduled, live, finished
    image_url = db.Column(db.String(300))  # Maç görseli
    mvp_player_id = db.Column(db.Integer, db.ForeignKey('player.id'))  # Maçın oyuncusu
    timeline = db.Column(db.Text, default='[]')  # JSON: [{"minute": "15'", "type": "goal", "player": "...", "team": "home"}]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    mvp = db.relationship('Player', foreign_keys=[mvp_player_id])
    goals = db.relationship('Goal', backref='match', lazy=True, cascade='all, delete-orphan')

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    minute = db.Column(db.String(10))  # "15'" veya "45+2'"
    scorer_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    assist_id = db.Column(db.Integer, db.ForeignKey('player.id'))  # İsteğe bağlı
    team = db.Column(db.String(10))  # "home" veya "away"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    scorer = db.relationship('Player', foreign_keys=[scorer_id])
    assist = db.relationship('Player', foreign_keys=[assist_id])

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    # Eğer session yoksa, guest olarak işaretle
    if 'user_id' not in session:
        session['is_admin'] = False
        session['username'] = 'Misafir'
    
    matches = Match.query.order_by(Match.match_date.desc()).limit(10).all()
    players = Player.query.order_by(Player.overall_rating.desc()).limit(8).all()
    is_admin = session.get('is_admin', False)
    return render_template('dashboard.html', matches=matches, players=players, is_admin=is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'user')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
    
    return render_template('login.html', role=role)

@app.route('/admin/match/add', methods=['GET', 'POST'])
def admin_add_match():
    if not session.get('is_admin'):
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.form
        match_date_str = data.get('match_date')
        match_time = data.get('match_time', '00:00')
        match_datetime = datetime.strptime(f"{match_date_str} {match_time}", '%Y-%m-%d %H:%M')
        
        new_match = Match(
            name=data.get('name'),
            home_team=data.get('home_team'),
            away_team=data.get('away_team'),
            home_score=int(data.get('home_score', 0)),
            away_score=int(data.get('away_score', 0)),
            match_date=match_datetime,
            match_time=match_time,
            stadium=data.get('stadium'),
            image_url=data.get('image_url'),
            status='finished'
        )
        db.session.add(new_match)
        db.session.commit()
        
        # Gol verilerini işle
        goals_data = data.get('goals_data')
        if goals_data:
            try:
                goals_list = json.loads(goals_data)
                for goal_info in goals_list:
                    new_goal = Goal(
                        match_id=new_match.id,
                        minute=goal_info.get('minute'),
                        scorer_id=int(goal_info.get('scorer_id')),
                        assist_id=int(goal_info.get('assist_id')) if goal_info.get('assist_id') else None,
                        team=goal_info.get('team')
                    )
                    db.session.add(new_goal)
                db.session.commit()
            except Exception as e:
                print(f"Gol ekleme hatası: {e}")
        
        flash('Maç başarıyla eklendi!', 'success')
        return redirect(url_for('matches'))
    
    players = Player.query.order_by(Player.name).all()
    return render_template('admin_add_match_new.html', players=players)

@app.route('/admin/player/add', methods=['GET', 'POST'])
def admin_add_player():
    if not session.get('is_admin'):
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.form
        
        # Detaylı yetenekleri formdan al
        detailed_skills = {
            'pace': {
                'acceleration': int(data.get('acceleration', 0)),
                'sprint_speed': int(data.get('sprint_speed', 0))
            },
            'shooting': {
                'finishing': int(data.get('finishing', 0)),
                'long_shots': int(data.get('long_shots', 0)),
                'shot_power': int(data.get('shot_power', 0)),
                'positioning': int(data.get('positioning', 0)),
                'volleys': int(data.get('volleys', 0)),
                'penalties': int(data.get('penalties', 0))
            },
            'passing': {
                'short_pass': int(data.get('short_pass', 0)),
                'long_pass': int(data.get('long_pass', 0)),
                'vision': int(data.get('vision', 0)),
                'crossing': int(data.get('crossing', 0)),
                'curve': int(data.get('curve', 0)),
                'free_kick': int(data.get('free_kick', 0))
            },
            'dribbling': {
                'dribbling': int(data.get('dribbling_skill', 0)),
                'balance': int(data.get('balance', 0)),
                'agility': int(data.get('agility', 0)),
                'reactions': int(data.get('reactions', 0)),
                'ball_control': int(data.get('ball_control', 0))
            },
            'defending': {
                'man_marking': int(data.get('man_marking', 0)),
                'standing_tackle': int(data.get('standing_tackle', 0)),
                'interceptions': int(data.get('interceptions', 0)),
                'heading': int(data.get('heading', 0))
            },
            'physical': {
                'strength': int(data.get('strength', 0)),
                'aggression': int(data.get('aggression', 0)),
                'jumping': int(data.get('jumping', 0)),
                'stamina': int(data.get('stamina', 0))
            }
        }
        
        # Ana yetenekleri detaylı yeteneklerin ortalamasından hesapla
        pace_avg = sum(detailed_skills['pace'].values()) // len(detailed_skills['pace'])
        shooting_avg = sum(detailed_skills['shooting'].values()) // len(detailed_skills['shooting'])
        passing_avg = sum(detailed_skills['passing'].values()) // len(detailed_skills['passing'])
        dribbling_avg = sum(detailed_skills['dribbling'].values()) // len(detailed_skills['dribbling'])
        defending_avg = sum(detailed_skills['defending'].values()) // len(detailed_skills['defending'])
        physical_avg = sum(detailed_skills['physical'].values()) // len(detailed_skills['physical'])
        
        # Basit pozisyon haritası oluştur
        position_map = {'ST': 'green', 'CF': 'green'}
        
        new_player = Player(
            name=data.get('name'),
            position=data.get('position'),
            team=data.get('team'),
            jersey_number=int(data.get('jersey_number', 0)),
            age=int(data.get('age', 0)),
            overall_rating=int(data.get('overall_rating', 0)),
            pace=pace_avg,
            shooting=shooting_avg,
            passing=passing_avg,
            dribbling=dribbling_avg,
            defending=defending_avg,
            physical=physical_avg,
            photo_url=data.get('photo_url'),
            position_map=json.dumps(position_map),
            detailed_skills=json.dumps(detailed_skills)
        )
        db.session.add(new_player)
        db.session.commit()
        
        flash('Oyuncu başarıyla eklendi!', 'success')
        return redirect(url_for('players'))
    
    return render_template('admin_add_player.html')

@app.route('/admin/player/edit/<int:player_id>', methods=['GET', 'POST'])
def admin_edit_player(player_id):
    if not session.get('is_admin'):
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('dashboard'))
    
    player = Player.query.get_or_404(player_id)
    
    if request.method == 'POST':
        data = request.form
        player.name = data.get('name')
        player.age = int(data.get('age', 0))
        player.position = data.get('position')
        player.jersey_number = int(data.get('jersey_number', 0))
        player.team = data.get('team')
        player.overall_rating = int(data.get('overall_rating', 0))
        player.pace = int(data.get('pace', 0))
        player.shooting = int(data.get('shooting', 0))
        player.passing = int(data.get('passing', 0))
        player.dribbling = int(data.get('dribbling', 0))
        player.defending = int(data.get('defending', 0))
        player.physical = int(data.get('physical', 0))
        
        db.session.commit()
        flash('Oyuncu güncellendi!', 'success')
        return redirect(url_for('players'))
    
    return render_template('admin_edit_player.html', player=player)

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
    is_admin = session.get('is_admin', False)
    return render_template('matches_list.html', matches=all_matches, is_admin=is_admin)

@app.route('/match/<int:match_id>')
def match_detail(match_id):
    match = Match.query.get_or_404(match_id)
    is_admin = session.get('is_admin', False)
    return render_template('match_detail.html', match=match, is_admin=is_admin)

@app.route('/players')
def players():
    all_players = Player.query.order_by(Player.overall_rating.desc()).all()
    is_admin = session.get('is_admin', False)
    return render_template('players_new.html', players=all_players, is_admin=is_admin)

@app.route('/teams')
def teams():
    all_teams = Team.query.all()
    return render_template('teams.html', teams=all_teams)

@app.route('/leaderboard')
def leaderboard():
    # Gol krallığı - Goal tablosundan gol sayılarını hesapla
    from sqlalchemy import func
    
    scorers_query = db.session.query(
        Player,
        func.count(Goal.id).label('goals')
    ).join(Goal, Player.id == Goal.scorer_id)\
     .group_by(Player.id)\
     .order_by(func.count(Goal.id).desc())\
     .limit(20)\
     .all()
    
    # Row objelerini dict'e çevir
    top_scorers = [{'player': row[0], 'goals': row[1]} for row in scorers_query]
    
    # Asist krallığı - Goal tablosundan asist sayılarını hesapla
    assists_query = db.session.query(
        Player,
        func.count(Goal.id).label('assists')
    ).join(Goal, Player.id == Goal.assist_id)\
     .filter(Goal.assist_id.isnot(None))\
     .group_by(Player.id)\
     .order_by(func.count(Goal.id).desc())\
     .limit(20)\
     .all()
    
    # Row objelerini dict'e çevir
    top_assists = [{'player': row[0], 'assists': row[1]} for row in assists_query]
    
    return render_template('leaderboard.html', 
                         top_scorers=top_scorers,
                         top_assists=top_assists)

@app.route('/player/<int:player_id>')
def player_profile(player_id):
    player = Player.query.get_or_404(player_id)
    
    # JSON verilerini parse et
    position_map = json.loads(player.position_map) if player.position_map else {}
    detailed_skills = json.loads(player.detailed_skills) if player.detailed_skills else {}
    
    # Sezon istatistiklerini al
    season_stats = SeasonStats.query.filter_by(player_id=player_id).order_by(SeasonStats.season.desc()).all()
    
    is_admin = session.get('is_admin', False)
    
    return render_template('player_profile_new.html', 
                         player=player, 
                         position_map=position_map,
                         detailed_skills=detailed_skills,
                         season_stats=season_stats,
                         is_admin=is_admin)

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

# Removed old add_player route - now using admin_add_player with dedicated page

@app.route('/admin/player/edit/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    if not session.get('is_admin'):
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('index'))
    
    player = Player.query.get_or_404(player_id)
    
    if request.method == 'POST':
        data = request.form
        
        # Detaylı yetenekleri güncelle
        detailed_skills = {
            'pace': {
                'acceleration': int(data.get('acceleration', 0)),
                'sprint_speed': int(data.get('sprint_speed', 0))
            },
            'shooting': {
                'finishing': int(data.get('finishing', 0)),
                'long_shots': int(data.get('long_shots', 0)),
                'shot_power': int(data.get('shot_power', 0)),
                'positioning': int(data.get('positioning', 0)),
                'volleys': int(data.get('volleys', 0)),
                'penalties': int(data.get('penalties', 0))
            },
            'passing': {
                'short_pass': int(data.get('short_pass', 0)),
                'long_pass': int(data.get('long_pass', 0)),
                'vision': int(data.get('vision', 0)),
                'crossing': int(data.get('crossing', 0)),
                'curve': int(data.get('curve', 0)),
                'free_kick': int(data.get('free_kick', 0))
            },
            'dribbling': {
                'dribbling': int(data.get('dribbling_skill', 0)),
                'balance': int(data.get('balance', 0)),
                'agility': int(data.get('agility', 0)),
                'reactions': int(data.get('reactions', 0)),
                'ball_control': int(data.get('ball_control', 0))
            },
            'defending': {
                'man_marking': int(data.get('man_marking', 0)),
                'standing_tackle': int(data.get('standing_tackle', 0)),
                'interceptions': int(data.get('interceptions', 0)),
                'heading': int(data.get('heading', 0))
            },
            'physical': {
                'strength': int(data.get('strength', 0)),
                'aggression': int(data.get('aggression', 0)),
                'jumping': int(data.get('jumping', 0)),
                'stamina': int(data.get('stamina', 0))
            }
        }
        
        player.name = data.get('name')
        player.position = data.get('position')
        player.team = data.get('team')
        player.jersey_number = int(data.get('jersey_number', 0))
        player.age = int(data.get('age', 0))
        player.overall_rating = int(data.get('overall_rating', 0))
        player.pace = int(data.get('pace', 0))
        player.shooting = int(data.get('shooting', 0))
        player.passing = int(data.get('passing', 0))
        player.dribbling = int(data.get('dribbling', 0))
        player.defending = int(data.get('defending', 0))
        player.physical = int(data.get('physical', 0))
        player.photo_url = data.get('photo_url')
        player.position_map = data.get('position_map', '{}')
        player.detailed_skills = json.dumps(detailed_skills)
        
        db.session.commit()
        flash('Oyuncu güncellendi!', 'success')
        return redirect(url_for('admin_panel'))
    
    # GET isteği için düzenleme formu
    position_map = json.loads(player.position_map) if player.position_map else {}
    detailed_skills = json.loads(player.detailed_skills) if player.detailed_skills else {}
    
    return render_template('edit_player.html', 
                         player=player, 
                         position_map=position_map,
                         detailed_skills=detailed_skills)

@app.route('/admin/player/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    
    flash('Oyuncu silindi!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/season-stats/add', methods=['POST'])
def add_season_stats():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.form
    new_stats = SeasonStats(
        player_id=int(data.get('player_id')),
        season=data.get('season'),
        matches=int(data.get('matches', 0)),
        goals=int(data.get('goals', 0)),
        assists=int(data.get('assists', 0))
    )
    db.session.add(new_stats)
    db.session.commit()
    
    flash('Sezon istatistiği eklendi!', 'success')
    return redirect(url_for('edit_player', player_id=data.get('player_id')))

# Match Admin Routes (ikinci route silindi, yuxarıda admin_add_match var)

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
        
        # Create sample player if no players exist
        if Player.query.count() == 0:
            sample_skills = {
                'pace': {'acceleration': 92, 'sprint_speed': 94},
                'shooting': {'finishing': 95, 'long_shots': 85, 'shot_power': 88, 'positioning': 93, 'volleys': 87, 'penalties': 80},
                'passing': {'short_pass': 86, 'long_pass': 78, 'vision': 89, 'crossing': 82, 'curve': 84, 'free_kick': 79},
                'dribbling': {'dribbling': 96, 'balance': 91, 'agility': 94, 'reactions': 90, 'ball_control': 95},
                'defending': {'man_marking': 45, 'standing_tackle': 40, 'interceptions': 52, 'heading': 70},
                'physical': {'strength': 78, 'aggression': 65, 'jumping': 85, 'stamina': 88}
            }
            
            sample_positions = {'ST': 'green', 'CF': 'light-green', 'LW': 'yellow', 'RW': 'yellow'}
            
            sample_player = Player(
                name='Ethan Carter',
                position='Forward',
                team='FC Barcelona',
                jersey_number=10,
                age=24,
                overall_rating=88,
                pace=93,
                shooting=88,
                passing=83,
                dribbling=93,
                defending=52,
                physical=79,
                photo_url='https://via.placeholder.com/150',
                position_map=json.dumps(sample_positions),
                detailed_skills=json.dumps(sample_skills)
            )
            db.session.add(sample_player)
            db.session.commit()
            
            # Add sample season stats
            seasons = [
                {'season': '21/22', 'matches': 2, 'goals': 1, 'assists': 0},
                {'season': '22/23', 'matches': 0, 'goals': 0, 'assists': 0},
                {'season': '23/24', 'matches': 5, 'goals': 0, 'assists': 0},
                {'season': '24/25', 'matches': 33, 'goals': 7, 'assists': 5},
                {'season': '25/26', 'matches': 1, 'goals': 0, 'assists': 0}
            ]
            
            for season_data in seasons:
                stats = SeasonStats(
                    player_id=sample_player.id,
                    season=season_data['season'],
                    matches=season_data['matches'],
                    goals=season_data['goals'],
                    assists=season_data['assists']
                )
                db.session.add(stats)
            
            db.session.commit()
            print("Sample player and season stats created!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
