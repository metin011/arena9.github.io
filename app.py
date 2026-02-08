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
from datetime import timedelta
app.permanent_session_lifetime = timedelta(days=31)

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
    motm = db.Column(db.Integer, default=0)
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
    type = db.Column(db.String(100), default='Dostluq')

    
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
@app.route('/players')
@app.route('/maclar')
@app.route('/machs')
@app.route('/istatistikler')
@app.route('/muqayise')
@app.route('/dream-team')
def index():
    # Serve the new SPA frontend
    return render_template('spa.html')


@app.route('/api/auth-status')
def api_auth_status():
    return jsonify({
        'is_logged_in': 'user_id' in session,
        'is_admin': session.get('is_admin', False),
        'username': session.get('username')
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session.permanent = True
        return jsonify({'success': True, 'is_admin': user.is_admin})
    
    return jsonify({'success': False, 'message': 'İstifadəçi adı və ya şifrə yanlışdır'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Yalnız adminlər fayl yükləyə bilər'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Fayl seçilməyib'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Fayl adı boşdur'}), 400
        
    try:
        path = save_uploaded_file(file, folder='uploads')
        if path:
            return jsonify({'success': True, 'url': path})
        return jsonify({'success': False, 'message': 'Faylı saxlamaq mümkün olmadı'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server xətası: {str(e)}'}), 500


@app.route('/api/players', methods=['GET', 'POST'])
def api_players():
    if request.method == 'POST':
        if not session.get('is_admin'):
            return jsonify({'success': False, 'message': 'Yalnız adminlər oyunçu əlavə edə bilər'}), 403
        
        data = request.json
        try:
            def safe_int(val, default=0):
                try: return int(val) if val not in [None, ''] else default
                except: return default

            stats = data.get('stats', {})
            new_player = Player(
                name=data.get('name', 'İsimsiz'),
                jersey_number=safe_int(data.get('num'), 0),
                age=safe_int(data.get('age'), 0),
                overall_rating=safe_int(data.get('overall'), 75), 
                pace=safe_int(stats.get('Hız'), 0),
                shooting=safe_int(stats.get('Şut'), 0),
                passing=safe_int(stats.get('Pas'), 0),
                dribbling=safe_int(stats.get('Dribling'), 0),
                defending=safe_int(stats.get('Defans'), 0),
                physical=safe_int(stats.get('Fizik'), 0),
                height=safe_int(data.get('height'), 0),
                weight=safe_int(data.get('weight'), 0),
                position=data.get('position', 'CM'),
                preferred_foot=data.get('preferred_foot', 'Right'),
                photo_url=data.get('photo_url')
            )

            
            db.session.add(new_player)
            db.session.commit()
            
            log_action(session.get('user_id'), 'CREATE', 'Player', new_player.id, {'name': new_player.name})
            
            return jsonify({'success': True, 'id': new_player.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Xəta: {str(e)}'}), 500


    # GET
    players = Player.query.all()
    result = []
    for p in players:
        # Reconstruct stats object for frontend compatibility
        stats = {
            'Hız': p.pace, 'Şut': p.shooting, 'Pas': p.passing,
            'Dribling': p.dribbling, 'Defans': p.defending, 'Fizik': p.physical
        }
        
        # Reconstruct season stats
        past_data = {}
        try:
            seasons = SeasonStats.query.filter_by(player_id=p.id).all()
            for s in seasons:
                past_data[s.season] = {'g': s.goals, 'a': s.assists, 'm': s.matches, 'om': s.motm or 0}
        except Exception as e:
            # Handle schema mismatch or missing columns gracefully
            print(f"SeasonStats error for player {p.id}: {e}")
            past_data = {}
            
        # Reconstruct type stats
        type_data = {}
        for t in ["Sinif Ligi", "Dostluq matçları", "Məktəbdənkənar", "Məktəb çempionatı"]:
            type_data[t] = {'g': 0, 'a': 0, 'm': 0, 'om': 0}
            
        result.append({
            'id': p.id,
            'name': p.name,
            'num': p.jersey_number,
            'age': p.age,
            'photo_url': p.photo_url,
            'stats': stats,
            'pastData': past_data,
            'typeStats': type_data,
            'height': p.height,
            'weight': p.weight,
            'position': p.position,
            'preferred_foot': p.preferred_foot,
        })



    return jsonify(result)

@app.route('/api/players/<int:id>', methods=['PUT', 'DELETE'])
def api_player_detail(id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    player = Player.query.get(id)
    if not player:
        return jsonify({'success': False, 'message': 'Player not found'}), 404
        
    if request.method == 'DELETE':
        try:
            # Delete related records first to avoid FK constraint errors
            # Delete season stats
            SeasonStats.query.filter_by(player_id=id).delete()
            
            # Delete goals where player is scorer or assister
            Goal.query.filter_by(scorer_id=id).delete()
            Goal.query.filter_by(assist_id=id).delete()
            
            # Reset MVP references in matches
            Match.query.filter_by(mvp_player_id=id).update({Match.mvp_player_id: None})

            
            # Delete player ratings and comments if they exist
            try:
                PlayerRating.query.filter_by(player_id=id).delete()
                PlayerComment.query.filter_by(player_id=id).delete()
            except:
                pass  # These tables might not exist yet
            
            # Finally delete the player
            player_id_for_log = player.id
            player_name_for_log = player.name
            db.session.delete(player)
            db.session.commit()
            
            log_action(session.get('user_id'), 'DELETE', 'Player', player_id_for_log, {'name': player_name_for_log})
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

        
    if request.method == 'PUT':
        if not session.get('is_admin'):
            return jsonify({'success': False, 'message': 'Yalnız adminlər dəyişiklik edə bilər'}), 403
            
        data = request.json
        try:
            def safe_int(val, default=0):
                try: return int(val) if val not in [None, ''] else default
                except: return default

            player.name = data.get('name', player.name)
            player.age = safe_int(data.get('age'), player.age)
            player.jersey_number = safe_int(data.get('num'), player.jersey_number)
            player.photo_url = data.get('photo_url', player.photo_url)
            
            if 'stats' in data:
                stats = data['stats']
                player.pace = safe_int(stats.get('Hız'), player.pace)
                player.shooting = safe_int(stats.get('Şut'), player.shooting)
                player.passing = safe_int(stats.get('Pas'), player.passing)
                player.dribbling = safe_int(stats.get('Dribling'), player.dribbling)
                player.defending = safe_int(stats.get('Defans'), player.defending)
                player.physical = safe_int(stats.get('Fizik'), player.physical)
            
            player.height = safe_int(data.get('height'), player.height)
            player.weight = safe_int(data.get('weight'), player.weight)
            player.position = data.get('position', player.position)
            player.preferred_foot = data.get('preferred_foot', player.preferred_foot)

            # Update Season Statistics from pastData
            if 'pastData' in data:
                for season, stats in data['pastData'].items():
                    s_stat = SeasonStats.query.filter_by(player_id=id, season=season).first()
                    if not s_stat:
                        s_stat = SeasonStats(player_id=id, season=season)
                        db.session.add(s_stat)
                    
                    s_stat.goals = safe_int(stats.get('g'), s_stat.goals)
                    s_stat.assists = safe_int(stats.get('a'), s_stat.assists)
                    s_stat.matches = safe_int(stats.get('m'), s_stat.matches)
                    s_stat.motm = safe_int(stats.get('om'), s_stat.motm)

            db.session.commit()
            
            log_action(session.get('user_id'), 'UPDATE', 'Player', player.id, {'name': player.name})
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Xəta: {str(e)}'}), 500



@app.route('/api/matches', methods=['GET', 'POST'])
def api_matches():
    if request.method == 'POST':
        if not session.get('is_admin'):
             return jsonify({'success': False, 'message': 'Yalnız adminlər matç əlavə edə bilər'}), 403
        
        data = request.json
        try:
            def safe_int(val, default=0):
                try: return int(val) if val not in [None, ''] else default
                except: return default

            # Simplified match creation from JSON
            m = Match(
                home_team=data.get('home', 'Home'),
                away_team=data.get('away', 'Away'),
                home_score=safe_int(data.get('s1'), 0),
                away_score=safe_int(data.get('s2'), 0),
                match_date=datetime.strptime(data.get('date'), '%Y-%m-%dT%H:%M') if data.get('date') else datetime.utcnow(),
                season=data.get('season', '24/25'),
                status='finished',
                type=data.get('type', 'Dostluq')
            )
            
            # MVP
            if data.get('motm'):
                p = Player.query.filter_by(name=data.get('motm')).first()
                if p: m.mvp_player_id = p.id
                
            db.session.add(m)
            db.session.flush() # Get match ID before events
            
            # Events
            for ev in data.get('events', []):
                scorer_name = ev.get('player')
                assist_name = ev.get('assist')
                
                scorer = Player.query.filter_by(name=scorer_name).first()
                assist = Player.query.filter_by(name=assist_name).first() if assist_name else None
                
                if scorer:
                    g = Goal(
                        match_id=m.id,
                        scorer_id=scorer.id,
                        assist_id=assist.id if assist else None,
                        team=ev.get('team')
                    )
                    db.session.add(g)
            
            db.session.commit()
            
            log_action(session.get('user_id'), 'CREATE', 'Match', m.id, {'home': m.home_team, 'away': m.away_team})
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Matç xətası: {str(e)}'}), 500


    # GET
    matches = Match.query.order_by(Match.match_date.desc()).all()
    result = []
    for m in matches:
        mvp_name = m.mvp.name if m.mvp else None
        
        # Events
        events = []
        for g in m.goals:
             events.append({
                 'player': g.scorer.name if g.scorer else 'Unknown',
                 'assist': g.assist.name if g.assist else None,
                 'team': g.team
             })
             
        result.append({
            'id': m.id,
            'home': m.home_team,
            'away': m.away_team,
            's1': m.home_score,
            's2': m.away_score,
            'date': m.match_date.isoformat(),
            'season': m.season,
            'type': m.type or 'Dostluq',

            'motm': mvp_name,
            'events': events
        })
    return jsonify(result)

@app.route('/api/matches/<int:id>', methods=['PUT', 'DELETE'])
def api_match_detail(id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    match = Match.query.get(id)
    if not match:
        return jsonify({'success': False, 'message': 'Match not found'}), 404
        
    if request.method == 'DELETE':
        match_id_for_log = match.id
        match_info_for_log = {'home': match.home_team, 'away': match.away_team}
        db.session.delete(match)
        db.session.commit()
        
        log_action(session.get('user_id'), 'DELETE', 'Match', match_id_for_log, match_info_for_log)
        
        return jsonify({'success': True})
        
    if request.method == 'PUT':
        data = request.json
        match.home_team = data.get('home', match.home_team)
        match.away_team = data.get('away', match.away_team)
        match.home_score = data.get('s1', match.home_score)
        match.away_score = data.get('s2', match.away_score)
        match.season = data.get('season', match.season)
        
        if data.get('date'):
             try:
                 match.match_date = datetime.strptime(data.get('date'), '%Y-%m-%dT%H:%M')
             except: pass
             
        # MVP update
        if data.get('motm'):
            p = Player.query.filter_by(name=data.get('motm')).first()
            if p: match.mvp_player_id = p.id
            
        # Re-create goals (events) - simpler to clear and re-add
        Goal.query.filter_by(match_id=match.id).delete()
        for ev in data.get('events', []):
            scorer = Player.query.filter_by(name=ev.get('player')).first()
            assist = Player.query.filter_by(name=ev.get('assist')).first() if ev.get('assist') else None
            
            if scorer:
                g = Goal(
                    match_id=match.id,
                    scorer_id=scorer.id,
                    assist_id=assist.id if assist else None,
                    team=ev.get('team')
                )
                db.session.add(g)
        
        db.session.commit()
        
        log_action(session.get('user_id'), 'UPDATE', 'Match', match.id, {'home': match.home_team, 'away': match.away_team})
        
        return jsonify({'success': True})



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


@app.route('/admin/bulk-import', methods=['POST'])
def admin_bulk_import():
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
                    # MatchStats table does not exist in current schema, skipping.
                    # Assist table does not exist (handled in Goal), skipping.
                    
                    # Delete Goals where player is scorer
                    Goal.query.filter_by(scorer_id=pid).delete()
                    # Delete Goals where player is assister
                    Goal.query.filter_by(assist_id=pid).delete()
                    
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
with app.app_context():
    try:
        db.create_all()
        # Production-da köhnə database varsa, yeni sütunları əlavə etmək üçün manual check
        from sqlalchemy import text
        try:
            # SeasonStats üçün xg və pass_accuracy yoxla
            db.session.execute(text('ALTER TABLE season_stats ADD COLUMN IF NOT EXISTS xg FLOAT DEFAULT 0.0'))
            db.session.execute(text('ALTER TABLE season_stats ADD COLUMN IF NOT EXISTS pass_accuracy FLOAT DEFAULT 0.0'))
            db.session.execute(text('ALTER TABLE season_stats ADD COLUMN IF NOT EXISTS motm INTEGER DEFAULT 0'))
            # Match üçün type yoxla
            db.session.execute(text('ALTER TABLE match ADD COLUMN IF NOT EXISTS type VARCHAR(100) DEFAULT \'Dostluq\''))
            db.session.commit()

            print("✓ Database columns verified/added")
        except Exception as inner_e:
            print(f"Skipping ADD COLUMN (might be SQLite or already exists): {inner_e}")
            db.session.rollback()
            
        print("✓ Database tables created/verified")
    except Exception as e:
        print(f"Database initialization error: {e}")



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
