from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file as flask_send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
import os
import json
import csv
import io
import uuid
from sqlalchemy import or_, func, desc

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# File Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# PostgreSQL için DATABASE_URL düzəlişi (Render.com postgres:// -> postgresql:// dəyişdirir)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///football_stats.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Helper Functions for File Upload
def allowed_file(filename):
    """Fayl formatının icazəli olub-olmadığını yoxlayır"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder='players'):
    """Yüklənmiş faylı saxlayır və yolunu qaytarır"""
    if file and allowed_file(file.filename):
        # Unique filename yaradırıq
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Folder yoxlayırıq və yaradırıq
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Faylı saxlayırıq
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        
        # Thumbnail yaradırıq
        create_thumbnail(filepath, folder)
        
        # Relative path qaytarırıq
        return f"/static/uploads/{folder}/{filename}"
    return None

def create_thumbnail(filepath, folder, size=(150, 150)):
    """Şəkil üçün thumbnail yaradır"""
    try:
        with Image.open(filepath) as img:
            # RGB-yə çeviririk (RGBA problemi üçün)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Thumbnail yaradırıq
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Thumbnail qovluğuna saxlayırıq
            thumbnail_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', folder)
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            filename = os.path.basename(filepath)
            thumbnail_path = os.path.join(thumbnail_dir, filename)
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            return f"/static/uploads/thumbnails/{folder}/{filename}"
    except Exception as e:
        print(f"Thumbnail error: {e}")
        return None


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
    height = db.Column(db.Integer, default=0)
    weight = db.Column(db.Integer, default=0)
    preferred_foot = db.Column(db.String(10)) # Left, Right, Both
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
    
    # Advanced Metrics
    xg_total = db.Column(db.Float, default=0.0)
    pass_accuracy = db.Column(db.Float, default=0.0)
    
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
    xg = db.Column(db.Float, default=0.0)
    pass_accuracy = db.Column(db.Float, default=0.0)
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
    season = db.Column(db.String(20)) # Örnek: "24/25"
    
    # Advanced Metrics
    home_xg = db.Column(db.Float, default=0.0)
    away_xg = db.Column(db.Float, default=0.0)
    
    timeline = db.Column(db.Text, default='[]')  # JSON: [{"minute": "15'", "type": "goal", "player": "...", "team": "home"}]
    lineups = db.Column(db.Text, default='{"home": [], "away": []}')  # JSON: {"home": [id1, id2], "away": [id3, id4]}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def lineups_data(self):
        import json
        try:
            return json.loads(self.lineups)
        except:
            return {"home": [], "away": []}

    @property
    def timeline_data(self):
        import json
        try:
            return json.loads(self.timeline)
        except:
            return []

    # İlişkiler
    mvp = db.relationship('Player', foreign_keys=[mvp_player_id], post_update=True)
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

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE
    target_type = db.Column(db.String(50), nullable=False)  # Player, Match
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User relationship
    user = db.relationship('User', foreign_keys=[user_id])

class PlayerRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    player = db.relationship('Player', backref=db.backref('ratings', lazy=True))
    user = db.relationship('User', backref=db.backref('given_ratings', lazy=True))

class PlayerComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    player = db.relationship('Player', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('user_comments', lazy=True))

def log_action(user_id, action, target_type, target_id, details=None):
    """Helper function to record admin actions"""
    try:
        if isinstance(details, (dict, list)):
            details = json.dumps(details)
            
        log = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Audit Log Error: {e}")
        db.session.rollback()

# Routes
@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    # Yalnız ilk dəfə session yoxdursa guest olaraq təyin et
    if 'user_id' not in session and 'is_admin' not in session:
        session['is_admin'] = False
        session['username'] = 'Misafir'
    
    try:
        # KPI Stats
        total_players = Player.query.count()
        total_matches = Match.query.count()
        total_goals = Goal.query.count()
        
        # Recent Matches
        matches = Match.query.order_by(Match.match_date.desc()).limit(10).all()
        
        # Top Scorers (Real calculation from Goals)
        # Returns list of (Player, goal_count) tuples
        top_scorers_data = db.session.query(
            Player, func.count(Goal.id).label('total_goals')
        ).join(Goal, Goal.scorer_id == Player.id)\
         .group_by(Player.id)\
         .order_by(desc('total_goals'))\
         .limit(5).all()
         
        # Calculate Average Rating
        avg_rating = db.session.query(func.avg(Player.overall_rating)).scalar() or 0
        
        # Recent activity placeholders (or actual queries if available)
        recent_comments = PlayerComment.query.order_by(PlayerComment.timestamp.desc()).limit(5).all()
        user_rating = 0 # Default if not logged in
        form_data = [] # Placeholder
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        matches = []
        top_scorers_data = []
        total_players = 0
        total_matches = 0
        total_goals = 0
        avg_rating = 0
        recent_comments = []
        user_rating = 0
        form_data = []
    
    is_admin = session.get('is_admin', False)
    return render_template('dashboard.html', 
                         matches=matches, 
                         top_scorers=top_scorers_data,
                         total_players=total_players,
                         total_matches=total_matches,
                         total_goals=total_goals,
                         avg_rating=round(avg_rating, 1),
                         recent_comments=recent_comments,
                         user_rating=user_rating,
                         form_data=form_data,
                         is_admin=is_admin)

@app.route('/api/rate-player', methods=['POST'])
def rate_player():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Giriş etməlisiniz'}), 401
    
    data = request.json
    player_id = data.get('player_id')
    rating_val = data.get('rating')
    
    if not player_id or not rating_val:
        return jsonify({'success': False, 'message': 'Məlumat çatışmır'}), 400
    
    existing = PlayerRating.query.filter_by(player_id=player_id, user_id=session.get('user_id')).first()
    if existing:
        existing.rating = rating_val
    else:
        new_rating = PlayerRating(player_id=player_id, user_id=session.get('user_id'), rating=rating_val)
        db.session.add(new_rating)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/comment-player', methods=['POST'])
def comment_player():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Giriş etməlisiniz'}), 401
    
    data = request.json
    player_id = data.get('player_id')
    comment_text = data.get('comment')
    
    if not player_id or not comment_text:
        return jsonify({'success': False, 'message': 'Məlumat çatışmır'}), 400
    
    new_comment = PlayerComment(player_id=player_id, user_id=session.get('user_id'), comment=comment_text)
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'comment': {
            'username': session.get('username'),
            'text': comment_text,
            'timestamp': datetime.utcnow().strftime('%d.%m.%Y')
        }
    })

@app.route('/player-vs')
def player_vs():
    p1_id = request.args.get('p1', type=int)
    p2_id = request.args.get('p2', type=int)
    
    p1 = Player.query.get(p1_id) if p1_id else None
    p2 = Player.query.get(p2_id) if p2_id else None
    
    all_players = Player.query.all()
    
    return render_template('player_vs.html', p1=p1, p2=p2, all_players=all_players)

@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'user')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                flash('✅ Giriş uğurlu oldu!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('❌ İstifadəçi adı və ya şifrə yanlışdır!', 'error')
        except Exception as e:
            print(f"Login error: {e}")
            flash('⚠️ Giriş zamanı xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.', 'error')
    
    return render_template('login.html', role=role)

@app.route('/admin/match/add', methods=['GET', 'POST'])
def admin_add_match():
    if not session.get('is_admin'):
        flash('⛔ Bu işlem için yönetici izniniz yok!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.form
        match_date_str = data.get('match_date')
        match_time = data.get('match_time', '00:00')
        match_datetime = datetime.strptime(f"{match_date_str} {match_time}", '%Y-%m-%d %H:%M')
        
        image_url = data.get('image_url')
        
        # Şəkil yükləmə
        if 'match_image' in request.files:
            file = request.files['match_image']
            if file and file.filename != '':
                uploaded_path = save_uploaded_file(file, folder='matches')
                if uploaded_path:
                    image_url = uploaded_path

        mvp_id = data.get('mvp_player_id')
        if mvp_id:
            mvp_id = int(mvp_id)
        else:
            mvp_id = None

        home_score = int(data.get('home_score', 0))
        away_score = int(data.get('away_score', 0))

        new_match = Match(
            name=data.get('name'),
            home_team=data.get('home_team'),
            away_team=data.get('away_team'),
            home_score=home_score,
            away_score=away_score,
            match_date=match_datetime,
            match_time=match_time,
            stadium=data.get('stadium'),
            image_url=image_url,
            status='finished',
            mvp_player_id=mvp_id,
            season=data.get('season'),
            home_xg=float(data.get('home_xg', 0.0)),
            away_xg=float(data.get('away_xg', 0.0)),
            lineups=json.dumps({
                "home": json.loads(request.form.get('home_lineup') or '[]'),
                "away": json.loads(request.form.get('away_lineup') or '[]')
            })
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
        
        # Audit Log
        log_action(
            user_id=session.get('user_id'),
            action='CREATE',
            target_type='Match',
            target_id=new_match.id,
            details={'home_team': new_match.home_team, 'away_team': new_match.away_team}
        )
        
        flash('Maç başarıyla eklendi!', 'success')
        return redirect(url_for('matches'))
    
    unique_teams = [t[0] for t in db.session.query(Player.team).filter(Player.team != None).distinct().order_by(Player.team).all()]
    players = Player.query.order_by(Player.name).all()
    return render_template('admin_add_match_new.html', players=players, teams=unique_teams)

@app.route('/admin/player/add', methods=['GET', 'POST'])
def admin_add_player():
    if not session.get('is_admin'):
        flash('⛔ Bu işlem için yönetici izniniz yok!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.form
        
        # Detaylı yetenekleri formdan al - Daha ətraflı statistika
        detailed_skills = {
            'pace': {
                'acceleration': int(data.get('acceleration', 0) or 0),
                'sprint_speed': int(data.get('sprint_speed', 0) or 0)
            },
            'shooting': {
                'finishing': int(data.get('finishing', 0) or 0),
                'long_shots': int(data.get('long_shots', 0) or 0),
                'shot_power': int(data.get('shot_power', 0) or 0),
                'positioning': int(data.get('positioning', 0) or 0),
                'volleys': int(data.get('volleys', 0) or 0),
                'penalties': int(data.get('penalties', 0) or 0)
            },
            'passing': {
                'short_pass': int(data.get('short_pass', 0) or 0),
                'long_pass': int(data.get('long_pass', 0) or 0),
                'vision': int(data.get('vision', 0) or 0),
                'crossing': int(data.get('crossing', 0) or 0),
                'curve': int(data.get('curve', 0) or 0),
                'free_kick': int(data.get('free_kick', 0) or 0)
            },
            'dribbling': {
                'dribbling': int(data.get('dribbling', 0) or 0),
                'balance': int(data.get('balance', 0) or 0),
                'agility': int(data.get('agility', 0) or 0),
                'reactions': int(data.get('reactions', 0) or 0),
                'ball_control': int(data.get('ball_control', 0) or 0)
            },
            'defending': {
                'man_marking': int(data.get('man_marking', 0) or 0),
                'standing_tackle': int(data.get('standing_tackle', 0) or 0),
                'interceptions': int(data.get('interceptions', 0) or 0),
                'heading': int(data.get('heading', 0) or 0)
            },
            'physical': {
                'strength': int(data.get('strength', 0) or 0),
                'aggression': int(data.get('aggression', 0) or 0),
                'jumping': int(data.get('jumping', 0) or 0),
                'stamina': int(data.get('stamina', 0) or 0)
            }
        }
        
        # Ana yetenekleri detaylı yeteneklerin ortalamasından hesapla
        try:
            pace_avg = sum(detailed_skills['pace'].values()) // len(detailed_skills['pace']) if detailed_skills['pace'] else 75
            shooting_avg = sum(detailed_skills['shooting'].values()) // len(detailed_skills['shooting']) if detailed_skills['shooting'] else 75
            passing_avg = sum(detailed_skills['passing'].values()) // len(detailed_skills['passing']) if detailed_skills['passing'] else 75
            dribbling_avg = sum(detailed_skills['dribbling'].values()) // len(detailed_skills['dribbling']) if detailed_skills['dribbling'] else 75
            physical_avg = sum(detailed_skills['physical'].values()) // len(detailed_skills['physical']) if detailed_skills['physical'] else 75
            defending_avg = sum(detailed_skills['defending'].values()) // len(detailed_skills['defending']) if detailed_skills['defending'] else 75
        except Exception as e:
            print(f"Stats calculation error: {e}")
            pace_avg = shooting_avg = passing_avg = dribbling_avg = physical_avg = defending_avg = 75
        
        # Basit pozisyon haritası oluştur
        position_map = {'ST': 'green', 'CF': 'green'}
        
        # Şəkil yükləmə
        photo_url = data.get('photo_url') or 'https://via.placeholder.com/150'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                uploaded_path = save_uploaded_file(file, folder='players')
                if uploaded_path:
                    photo_url = uploaded_path

        new_player = Player(
            name=data.get('name'),
            position=data.get('position'),
            team=data.get('team'),
            jersey_number=int(data.get('jersey_number', 0) or 0),
            age=int(data.get('age', 0) or 0),
            height=int(data.get('height', 0) or 0),
            weight=int(data.get('weight', 0) or 0),
            preferred_foot=data.get('preferred_foot'),
            photo_url=photo_url,
            overall_rating=int(data.get('overall_rating', 75) or 75),
            pace=pace_avg,
            shooting=shooting_avg,
            passing=passing_avg,
            dribbling=dribbling_avg,
            defending=defending_avg,
            physical=physical_avg,
            xg_total=float(data.get('xg_total', 0.0) or 0.0),
            pass_accuracy=float(data.get('pass_accuracy', 0.0) or 0.0),
            position_map=json.dumps(position_map),
            detailed_skills=json.dumps(detailed_skills)
        )
        
        db.session.add(new_player)
        db.session.commit()
        
        # Audit Log
        log_action(
            user_id=session.get('user_id'),
            action='CREATE',
            target_type='Player',
            target_id=new_player.id,
            details={'name': new_player.name, 'team': new_player.team}
        )
        
        flash('✅ Oyuncu başarıyla eklendi!', 'success')
        return redirect(url_for('players'))
    
    return render_template('admin_add_player.html')

# Oyunçu redaktə route - edit_player funksiyasında birləşdirildi

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

@app.route('/welcome_page')
def welcome_page():
    matches = Match.query.order_by(Match.match_date.desc()).all()
    players = Player.query.all()
    return render_template('index.html', matches=matches, players=players)

@app.route('/matches')
def matches():
    try:
        all_matches = Match.query.order_by(Match.match_date.desc()).all()
    except Exception as e:
        print(f"Matches error: {e}")
        all_matches = []
    is_admin = session.get('is_admin', False)
    return render_template('matches_list.html', matches=all_matches, is_admin=is_admin)

@app.route('/match/<int:match_id>')
def match_detail(match_id):
    match = Match.query.get_or_404(match_id)
    is_admin = session.get('is_admin', False)
    
    # Lineups yuklə
    home_players = []
    away_players = []
    players_dict = {}
    
    try:
        lineups = json.loads(match.lineups) if match.lineups else {}
        home_ids = lineups.get('home', [])
        away_ids = lineups.get('away', [])
        
        if home_ids:
            home_players = Player.query.filter(Player.id.in_(home_ids)).all()
            for player in home_players:
                players_dict[player.id] = player
        if away_ids:
            away_players = Player.query.filter(Player.id.in_(away_ids)).all()
            for player in away_players:
                players_dict[player.id] = player
            
    except Exception as e:
        print(f"Lineup loading error: {e}")
        
    # Əgər lineup yoxdursa, köhnə üsulla (team adına görə) tapmağa çalış (fallback)
    if not home_players and match.home_team:
        home_players = Player.query.filter(Player.team == match.home_team).all()
    if not away_players and match.away_team:
        away_players = Player.query.filter(Player.team == match.away_team).all()
    
    # Get goals for this match
    goals = Goal.query.filter_by(match_id=match_id).order_by(Goal.minute).all()
    
    # Get MVP player if set
    mvp_player = None
    if match.mvp_player_id:
        mvp_player = Player.query.get(match.mvp_player_id)
        match.mvp_player = mvp_player
        
    return render_template('match_detail.html', match=match, is_admin=is_admin, 
                         home_players=home_players, away_players=away_players,
                         players_dict=players_dict, goals=goals)

@app.route('/players')
def players():
    try:
        all_players = Player.query.order_by(Player.overall_rating.desc()).all()
    except Exception as e:
        print(f"Players error: {e}")
        all_players = []
    is_admin = session.get('is_admin', False)
    return render_template('players_new.html', players=all_players, is_admin=is_admin)

@app.route('/teams')
def teams():
    try:
        all_teams = Team.query.all()
    except Exception as e:
        print(f"Teams error: {e}")
        all_teams = []
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
    
    # POTM Liderlik (Most Man of the Matches) - Using MVP field
    potm_query = db.session.query(
        Player,
        func.count(Match.id).label('potm_count')
    ).join(Match, Player.id == Match.mvp_player_id)\
     .group_by(Player.id)\
     .order_by(func.count(Match.id).desc())\
     .limit(10)\
     .all()
     
    top_potm = [{'player': row[0], 'count': row[1]} for row in potm_query]
    
    # Mövqe üzrə ortalama reytinq
    position_ratings = db.session.query(
        Player.position,
        func.avg(Player.overall_rating).label('avg_rating'),
        func.count(Player.id).label('player_count')
    ).filter(Player.position.isnot(None))\
     .group_by(Player.position)\
     .order_by(func.avg(Player.overall_rating).desc())\
     .all()
    
    position_stats = [{'position': row[0], 'avg_rating': round(row[1], 1), 'count': row[2]} for row in position_ratings]
    
    return render_template('leaderboard.html', 
                         top_scorers=top_scorers,
                         top_assists=top_assists,
                         top_potm=top_potm,
                         position_stats=position_stats)

@app.route('/player/<int:player_id>')
def player_profile(player_id):
    try:
        player = Player.query.get_or_404(player_id)
        
        # Reytinqləri və Şərhləri al - Hataları önlemek için filter_by kullanıyoruz
        avg_rating = 0
        try:
            avg_rating = db.session.query(func.avg(PlayerRating.rating)).filter(PlayerRating.player_id == player_id).scalar() or 0
        except: pass
        
        recent_comments = []
        try:
            recent_comments = PlayerComment.query.filter_by(player_id=player_id).order_by(PlayerComment.timestamp.desc()).limit(5).all()
        except: pass
        
        user_rating = 0
        if session.get('user_id'):
            try:
                existing_rating = PlayerRating.query.filter_by(player_id=player_id, user_id=session.get('user_id')).first()
                if existing_rating:
                    user_rating = existing_rating.rating
            except: pass

        # Son 5 mac performansı (Form)
        form_data = []
        try:
            # Goal tablosundan bu oyunçunun iştirak etdiyi son 5 macı tapırıq
            last_matches = db.session.query(Match).join(Goal, Match.id == Goal.match_id)\
                .filter((Goal.scorer_id == player_id) | (Goal.assist_id == player_id))\
                .order_by(Match.match_date.desc()).limit(5).all()
            
            # Form hesablanması (qol=2 xal, asist=1 xal, MVP=3 xal)
            for m in last_matches:
                score = 0
                goals_in_match = Goal.query.filter_by(match_id=m.id, scorer_id=player_id).count()
                assists_in_match = Goal.query.filter_by(match_id=m.id, assist_id=player_id).count()
                score += (goals_in_match * 2) + assists_in_match
                if m.mvp_player_id == player_id:
                    score += 3
                form_data.append({'date': m.match_date.strftime('%d.%m'), 'score': score})
            form_data.reverse() # Xronoloji ardıcıllıq
        except Exception as e:
            print(f"Form calculation error: {e}")
        
        # JSON verilerini parse et
        position_map = {}
        try:
            position_map = json.loads(player.position_map) if player.position_map else {}
        except: pass
        
        detailed_skills = {}
        try:
            detailed_skills = json.loads(player.detailed_skills) if player.detailed_skills else {}
        except: pass
        
        # Sezon istatistiklerini al
        season_stats = []
        try:
            season_stats = SeasonStats.query.filter_by(player_id=player_id).order_by(SeasonStats.season.desc()).all()
        except: pass
        
        is_admin = session.get('is_admin', False)
        
        return render_template('player_profile_new.html', 
                             player=player, 
                             position_map=position_map,
                             detailed_skills=detailed_skills,
                             season_stats=season_stats,
                             avg_rating=round(avg_rating, 1),
                             recent_comments=recent_comments,
                             user_rating=user_rating,
                             form_data=form_data,
                             is_admin=is_admin)
    except Exception as e:
        print(f"Profile loading error: {e}")
        flash('Oyunçu profili yüklənərkən xəta baş verdi.', 'error')
        return redirect(url_for('players'))

@app.route('/compare')
def compare_players():
    p1_id = request.args.get('p1')
    p2_id = request.args.get('p2')
    
    player1 = None
    player2 = None
    
    if p1_id:
        player1 = Player.query.get(p1_id)
    if p2_id:
        player2 = Player.query.get(p2_id)
        
    all_players = Player.query.order_by(Player.name).all()
    
    return render_template('player_compare.html', 
                         player1=player1, 
                         player2=player2, 
                         all_players=all_players)

@app.route('/dream-team')
def dream_team():
    all_players = Player.query.order_by(Player.name).all()
    return render_template('dream_team.html', all_players=all_players)

# API Endpoints for Charts
@app.route('/api/player/<int:player_id>/stats')
def api_player_stats(player_id):
    """Oyunçu statistika məlumatları (Chart.js üçün)"""
    player = Player.query.get_or_404(player_id)
    
    return jsonify({
        'name': player.name,
        'pace': player.pace,
        'shooting': player.shooting,
        'passing': player.passing,
        'dribbling': player.dribbling,
        'defending': player.defending,
        'physical': player.physical
    })

@app.route('/api/player/<int:player_id>/season-stats')
def api_season_stats(player_id):
    """Sezon statistikaları (Chart.js üçün)"""
    season_stats = SeasonStats.query.filter_by(player_id=player_id).order_by(SeasonStats.season).all()
    
    return jsonify({
        'seasons': [stat.season for stat in season_stats],
        'goals': [stat.goals for stat in season_stats],
        'assists': [stat.assists for stat in season_stats],
        'matches': [stat.matches for stat in season_stats]
    })

@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """Dashboard statistikaları"""
    from sqlalchemy import func
    
    total_players = Player.query.count()
    total_matches = Match.query.count()
    total_goals = Goal.query.count()
    
    # Mövqe üzrə ortalama reytinq
    position_stats = db.session.query(
        Player.position,
        func.avg(Player.overall_rating).label('avg_rating')
    ).group_by(Player.position).all()
    
    return jsonify({
        'total_players': total_players,
        'total_matches': total_matches,
        'total_goals': total_goals,
        'position_stats': {
            'positions': [stat[0] for stat in position_stats if stat[0]],
            'ratings': [round(float(stat[1]), 1) for stat in position_stats if stat[0]]
        }
    })


# Removed old add_player route - now using admin_add_player with dedicated page

@app.route('/admin/player/edit/<int:player_id>', methods=['GET', 'POST'])
def admin_edit_player(player_id):
    if not session.get('is_admin'):
        flash('⛔ Bu işlem için yönetici izniniz yok!', 'error')
        return redirect(url_for('dashboard'))
    
    player = Player.query.get_or_404(player_id)
    
    if request.method == 'POST':
        data = request.form
        
        # Detaylı yetenekleri güncelle
        detailed_skills = {
            'pace': {
                'acceleration': int(data.get('acceleration', 0) or 0),
                'sprint_speed': int(data.get('sprint_speed', 0) or 0)
            },
            'shooting': {
                'finishing': int(data.get('finishing', 0) or 0),
                'long_shots': int(data.get('long_shots', 0) or 0),
                'shot_power': int(data.get('shot_power', 0) or 0),
                'positioning': int(data.get('positioning', 0) or 0),
                'volleys': int(data.get('volleys', 0) or 0),
                'penalties': int(data.get('penalties', 0) or 0)
            },
            'passing': {
                'short_pass': int(data.get('short_pass', 0) or 0),
                'long_pass': int(data.get('long_pass', 0) or 0),
                'vision': int(data.get('vision', 0) or 0),
                'crossing': int(data.get('crossing', 0) or 0),
                'curve': int(data.get('curve', 0) or 0),
                'free_kick': int(data.get('free_kick', 0) or 0)
            },
            'dribbling': {
                'dribbling': int(data.get('dribbling', 0) or 0),
                'balance': int(data.get('balance', 0) or 0),
                'agility': int(data.get('agility', 0) or 0),
                'reactions': int(data.get('reactions', 0) or 0),
                'ball_control': int(data.get('ball_control', 0) or 0)
            },
            'defending': {
                'man_marking': int(data.get('man_marking', 0) or 0),
                'standing_tackle': int(data.get('standing_tackle', 0) or 0),
                'interceptions': int(data.get('interceptions', 0) or 0),
                'heading': int(data.get('heading', 0) or 0)
            },
            'physical': {
                'strength': int(data.get('strength', 0) or 0),
                'aggression': int(data.get('aggression', 0) or 0),
                'jumping': int(data.get('jumping', 0) or 0),
                'stamina': int(data.get('stamina', 0) or 0)
            }
        }
        
        # Ana yetenekleri detaylı yeteneklerin ortalamasından hesapla
        try:
            player.pace = sum(detailed_skills['pace'].values()) // len(detailed_skills['pace']) if detailed_skills['pace'] else 75
            player.shooting = sum(detailed_skills['shooting'].values()) // len(detailed_skills['shooting']) if detailed_skills['shooting'] else 75
            player.passing = sum(detailed_skills['passing'].values()) // len(detailed_skills['passing']) if detailed_skills['passing'] else 75
            player.dribbling = sum(detailed_skills['dribbling'].values()) // len(detailed_skills['dribbling']) if detailed_skills['dribbling'] else 75
            player.physical = sum(detailed_skills['physical'].values()) // len(detailed_skills['physical']) if detailed_skills['physical'] else 75
            player.defending = sum(detailed_skills['defending'].values()) // len(detailed_skills['defending']) if detailed_skills['defending'] else 75
        except Exception as e:
            print(f"Stats calculation error during edit: {e}")
        
        # Ana məlumatları yenilə
        player.name = data.get('name')
        player.position = data.get('position')
        player.team = data.get('team')
        player.jersey_number = int(data.get('jersey_number', 0) or 0)
        player.age = int(data.get('age', 0) or 0)
        player.height = int(data.get('height', 0) or 0)
        player.weight = int(data.get('weight', 0) or 0)
        player.preferred_foot = data.get('preferred_foot')
        
        # Şəkil yükləmə
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                uploaded_path = save_uploaded_file(file, folder='players')
                if uploaded_path:
                    player.photo_url = uploaded_path
        elif data.get('photo_url'):
            player.photo_url = data.get('photo_url')
        
        # Reytinqləri yenilə - OVR formdan gələ bilər və ya avtomatlaşdırıla bilər
        player.overall_rating = int(data.get('overall_rating', 75) or 75)
        player.xg_total = float(data.get('xg_total', 0.0) or 0.0)
        player.pass_accuracy = float(data.get('pass_accuracy', 0.0) or 0.0)
        
        # Detaylı bacarıqları yenilə
        player.detailed_skills = json.dumps(detailed_skills)
        
        db.session.commit()
        # Audit Log
        log_action(
            user_id=session.get('user_id'),
            action='UPDATE',
            target_type='Player',
            target_id=player.id,
            details={'name': player.name}
        )
        
        flash('✅ Oyuncu başarıyla güncellendi!', 'success')
        return redirect(url_for('player_profile', player_id=player.id))
    
    # GET isteği - redaktə formu göstər
    position_map = json.loads(player.position_map) if player.position_map else {}
    detailed_skills = json.loads(player.detailed_skills) if player.detailed_skills else {}
    
    return render_template('player_edit_full.html', 
                         player=player, 
                         position_map=position_map,
                         detailed_skills=detailed_skills)

@app.route('/admin/export/players')
def admin_export_players():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Header
    cw.writerow(['name', 'position', 'team', 'jersey_number', 'age', 'overall_rating', 
                 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physical'])
                 
    players = Player.query.all()
    for p in players:
        cw.writerow([p.name, p.position, p.team, p.jersey_number, p.age, p.overall_rating,
                     p.pace, p.shooting, p.passing, p.dribbling, p.defending, p.physical])
                     
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8-sig'))
    output.seek(0)
    
    return flask_send_file(output, mimetype="text/csv", as_attachment=True, download_name="players_export.csv")

@app.route('/admin/match/edit/<int:match_id>', methods=['GET', 'POST'])
def admin_edit_match(match_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    match = Match.query.get_or_404(match_id)
    all_players = Player.query.order_by(Player.name).all()
    unique_teams = [t[0] for t in db.session.query(Player.team).filter(Player.team != None).distinct().order_by(Player.team).all()]
    
    if request.method == 'POST':
        data = request.form
        
        # Update basic fields
        match.name = data.get('name')
        match.home_team = data.get('home_team')
        match.away_team = data.get('away_team')
        match.home_score = int(data.get('home_score', 0))
        match.away_score = int(data.get('away_score', 0))
        match.stadium = data.get('stadium')
        match.match_time = data.get('match_time')
        match.home_xg = float(data.get('home_xg', 0.0))
        match.away_xg = float(data.get('away_xg', 0.0))
        match.season = data.get('season')
        
        match_date_str = data.get('match_date')
        if match_date_str:
            match.match_date = datetime.strptime(match_date_str, '%Y-%m-%d')
            
        # Update MVP (POTM)
        mvp_id = data.get('mvp_player_id')
        if mvp_id:
            match.mvp_player_id = int(mvp_id)
        else:
            match.mvp_player_id = None
            
        # Lineupları güncəllə
        match.lineups = json.dumps({
            "home": json.loads(request.form.get('home_lineup', '[]')),
            "away": json.loads(request.form.get('away_lineup', '[]'))
        })
            
        # Update Image
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                photo_url = save_uploaded_file(file, folder='matches')
                if photo_url:
                    match.image_url = photo_url
                    
        # Update Goals
        # Simple strategy: Delete all existing goals and re-create them
        # This keeps it in sync with the frontend list
        try:
            # First, delete existing goals
            Goal.query.filter_by(match_id=match.id).delete()
            
            # Add new goals from JSON
            goals_json = data.get('goals_data')
            if goals_json:
                goals_list = json.loads(goals_json)
                for g in goals_list:
                    scorer_id = g.get('scorer_id')
                    if not scorer_id: continue
                    
                    assist_id = g.get('assist_id')
                    new_goal = Goal(
                        match_id=match.id,
                        scorer_id=int(scorer_id),
                        assist_id=int(assist_id) if assist_id else None,
                        minute=g.get('minute'),
                        team=g.get('team')
                    )
                    db.session.add(new_goal)
            
            db.session.commit()
            
            # Audit Log
            log_action(
                user_id=session.get('user_id'),
                action='UPDATE',
                target_type='Match',
                target_id=match.id,
                details={'home_team': match.home_team, 'away_team': match.away_team}
            )
            
            return redirect(url_for('match_detail', match_id=match.id))
            
        except Exception as e:
            db.session.rollback()
            return f"Xəta baş verdi: {e}"
            
    return render_template('admin_edit_match.html', match=match, players=all_players, teams=unique_teams)

@app.route('/admin/bulk-delete', methods=['POST'])
def admin_bulk_delete():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Fayl seçilməyib'})
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Fayl seçilməyib'})
        
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'success': False, 'message': 'Yalnız CSV faylları dəstəklənir'})

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        csv_input = csv.DictReader(stream)
        
        count_new = 0
        count_updated = 0
        
        for row in csv_input:
            name = row.get('name')
            if not name: continue
            
            # Mövcud oyunçunu axtar (case-insensitive)
            player = Player.query.filter(Player.name.ilike(name)).first()
            
            if not player:
                player = Player(name=name)
                db.session.add(player)
                count_new += 1
            else:
                count_updated += 1
                
            # Məlumatları yenilə
            player.position = row.get('position', player.position)
            player.team = row.get('team', player.team)
            player.jersey_number = int(row.get('jersey_number', player.jersey_number or 0))
            player.age = int(row.get('age', player.age or 0))
            player.overall_rating = int(row.get('overall_rating', player.overall_rating or 0))
            player.pace = int(row.get('pace', player.pace or 0))
            player.shooting = int(row.get('shooting', player.shooting or 0))
            player.passing = int(row.get('passing', player.passing or 0))
            player.dribbling = int(row.get('dribbling', player.dribbling or 0))
            player.defending = int(row.get('defending', player.defending or 0))
            player.physical = int(row.get('physical', player.physical or 0))
            
        db.session.commit()
        return jsonify({'success': True, 'message': f'Tamamlandı: {count_new} yeni, {count_updated} yeniləndi'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Xəta: {str(e)}'})

@app.route('/admin/player/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    if not session.get('is_admin'):
        flash('⛔ Bu işlem için yönetici izniniz yok!', 'error')
        return redirect(url_for('dashboard'))
    
    player = Player.query.get_or_404(player_id)
    player_name = player.name
    
    try:
        # Manually delete related records to avoid ForeignKey errors if cascade is missing
        # 1. Delete Stats
        MatchStats.query.filter_by(player_id=player_id).delete()
        # 2. Delete Goals & Assists
        Goal.query.filter_by(player_id=player_id).delete()
        Assist.query.filter_by(player_id=player_id).delete()
        # 3. Delete Logs references
        # AuditLog usually references target_id but not with FK constraint, so it's fine.
        
        # 4. Check for other potential relationships (Injury, Suspension if they exist)
        # Assuming only basic stats for now based on imported models.
        
        # Finally delete the player
        db.session.delete(player)
        db.session.commit()
        
        # Log action
        log_action(session.get('user_id'), 'DELETE', 'Player', player_id, {'name': player_name})
        
        flash(f'✅ {player_name} başarıyla silindi!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Delete Error: {e}")
        flash(f'❌ Oyunçu silinərkən xəta baş verdi. Zəhmət olmasa assosiasiya olunmuş məlumatları yoxlayın.', 'error')
        
    return redirect(url_for('players'))

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
    
    # Şəkil yükləmə
    if 'match_image' in request.files:
        file = request.files['match_image']
        if file and file.filename != '':
            uploaded_path = save_uploaded_file(file, folder='matches')
            if uploaded_path:
                match.image_url = uploaded_path
    
    db.session.commit()
    flash('Maç güncellendi!', 'success')
    return redirect(url_for('matches'))

@app.route('/admin/logs')
def admin_logs():
    if not session.get('is_admin'):
        flash('⛔ Bu səhifəyə giriş üçün admin icazəniz yoxdur!', 'error')
        return redirect(url_for('dashboard'))
    
    # Son 100 audit log qeydini gətir
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    return render_template('admin_logs.html', logs=logs)

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

# ===== SEO ROUTES =====

@app.route('/robots.txt')
def robots_txt():
    """Google bot üçün robots.txt"""
    robots_content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /login
Disallow: /register

Sitemap: https://arena9.onrender.com/sitemap.xml"""
    
    return robots_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/sitemap.xml')
def sitemap_xml():
    """Google üçün sitemap.xml - saytın bütün səhifələri"""
    
    # Base URL
    base_url = "https://arena9.onrender.com"
    
    # Sitemap başlığı
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Əsas səhifələr
    pages = [
        {'loc': '/', 'priority': '1.00', 'changefreq': 'daily'},
        {'loc': '/dashboard', 'priority': '1.00', 'changefreq': 'daily'},
        {'loc': '/players', 'priority': '0.90', 'changefreq': 'daily'},
        {'loc': '/matches', 'priority': '0.90', 'changefreq': 'daily'},
        {'loc': '/leaderboard', 'priority': '0.90', 'changefreq': 'weekly'},
    ]
    
    for page in pages:
        sitemap.append('  <url>')
        sitemap.append(f'    <loc>{base_url}{page["loc"]}</loc>')
        sitemap.append(f'    <priority>{page["priority"]}</priority>')
        sitemap.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        sitemap.append('  </url>')
    
    # Dinamik oyunçu səhifələri (son 50 oyunçu)
    try:
        players = Player.query.order_by(Player.created_at.desc()).limit(50).all()
        for player in players:
            sitemap.append('  <url>')
            sitemap.append(f'    <loc>{base_url}/player/{player.id}</loc>')
            sitemap.append('    <priority>0.70</priority>')
            sitemap.append('    <changefreq>weekly</changefreq>')
            sitemap.append('  </url>')
    except Exception as e:
        print(f"Sitemap player error: {e}")
    
    # Dinamik maç səhifələri (son 50 maç)
    try:
        matches = Match.query.order_by(Match.match_date.desc()).limit(50).all()
        for match in matches:
            sitemap.append('  <url>')
            sitemap.append(f'    <loc>{base_url}/match/{match.id}</loc>')
            sitemap.append('    <priority>0.70</priority>')
            sitemap.append('    <changefreq>weekly</changefreq>')
            sitemap.append('  </url>')
    except Exception as e:
        print(f"Sitemap match error: {e}")
    
    sitemap.append('</urlset>')
    
    return '\n'.join(sitemap), 200, {'Content-Type': 'application/xml; charset=utf-8'}

@app.route('/admin/bulk-delete', methods=['POST'])
def admin_bulk_delete():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 403
    
    try:
        data = request.json
        item_type = data.get('type')
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({'success': False, 'message': 'Seçili öğe yok'}), 400
            
        count = 0
        if item_type == 'player':
            for pid in ids:
                player = Player.query.get(pid)
                if player:
                    # Manually cleanup related records
                    MatchStats.query.filter_by(player_id=pid).delete()
                    Goal.query.filter_by(player_id=pid).delete()
                    Assist.query.filter_by(player_id=pid).delete()
                    
                    db.session.delete(player)
                    count += 1
        elif item_type == 'match':
            # Implement match bulk delete if needed
            pass
            
        db.session.commit()
        return jsonify({'success': True, 'message': f'{count} öğe başarıyla silindi'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/recalculate-stats')
def admin_recalculate_stats():
    if not session.get('is_admin'):
        flash('⛔ Bu işlem için yönetici izniniz yok!', 'error')
        return redirect(url_for('login'))
        
    try:
        players = Player.query.all()
        # Mövcud mövsümləri tapırıq
        seasons = [s[0] for s in db.session.query(Match.season).filter(Match.season != None).distinct().all()]
        
        for player in players:
            for season in seasons:
                # Bu mövsümdə oyunçunun iştirak etdiyi matçlar
                season_matches = Match.query.filter_by(season=season).all()
                matches_count = 0
                for m in season_matches:
                    try:
                        lineups = json.loads(m.lineups) if m.lineups else {}
                        if player.id in lineups.get('home', []) or player.id in lineups.get('away', []):
                            matches_count += 1
                    except:
                        continue
                
                # Qol sayı
                goals_count = Goal.query.join(Match).filter(
                    Match.season == season,
                    Goal.scorer_id == player.id
                ).count()
                
                # Asist sayı
                assists_count = Goal.query.join(Match).filter(
                    Match.season == season,
                    Goal.assist_id == player.id
                ).count()
                
                # Mövsüm statistikalarını tap və ya yarat
                s_stat = SeasonStats.query.filter_by(player_id=player.id, season=season).first()
                if not s_stat:
                    s_stat = SeasonStats(player_id=player.id, season=season)
                    db.session.add(s_stat)
                
                s_stat.matches = matches_count
                s_stat.goals = goals_count
                s_stat.assists = assists_count
        
        db.session.commit()
        flash('Bütün mövsüm statistikaları uğurla hesablandı!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Xəta baş verdi: {str(e)}', 'error')
        
    return redirect(url_for('admin_dashboard'))

# Database initialize et (həm lokal, həm production üçün)
try:
    init_db()
except Exception as e:
    print(f"Database initialization error: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
