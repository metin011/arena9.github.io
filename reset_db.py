import os
import sys
import time

# Veritabanını sil - instance klasöründen
db_paths = ['football_stats.db', 'instance/football_stats.db']
deleted = False

for db_path in db_paths:
    for i in range(3):
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"✅ {db_path} silindi!")
                deleted = True
                time.sleep(0.5)
                break
        except PermissionError:
            print(f"⚠️ {db_path} kullanımda, tekrar deneniyor... ({i+1}/3)")
            time.sleep(1)
    else:
        if os.path.exists(db_path):
            print(f"❌ HATA: {db_path} silinemedi! Uygulamayı kapat (Ctrl+C) ve tekrar dene.")
            sys.exit(1)

if not deleted:
    print(f"ℹ️ Veritabanı dosyası bulunamadı, yenisi oluşturulacak.")

# Yeni veritabanını oluştur
from app_updated import app, db, User, Player, Match, SeasonStats
from werkzeug.security import generate_password_hash
from datetime import datetime
import json

with app.app_context():
    db.create_all()
    print("✅ Veritabanı tabloları oluşturuldu!")
    
    # Admin kullanıcı ekle (sadece yoksa)
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        print("✅ Admin kullanıcı eklendi!")
    
    # Örnek oyuncular ekle
    players_data = [
        {
            'name': 'Ahmet Yılmaz',
            'position': 'Forvet',
            'team': 'Arena9 FC',
            'jersey_number': 10,
            'age': 25,
            'overall_rating': 85,
            'pace': 88,
            'shooting': 86,
            'passing': 82,
            'dribbling': 84,
            'defending': 45,
            'physical': 78
        },
        {
            'name': 'Mehmet Kaya',
            'position': 'Orta Saha',
            'team': 'Arena9 FC',
            'jersey_number': 8,
            'age': 27,
            'overall_rating': 82,
            'pace': 75,
            'shooting': 78,
            'passing': 88,
            'dribbling': 80,
            'defending': 70,
            'physical': 76
        },
        {
            'name': 'Mustafa Demir',
            'position': 'Defans',
            'team': 'Arena9 FC',
            'jersey_number': 4,
            'age': 29,
            'overall_rating': 80,
            'pace': 70,
            'shooting': 55,
            'passing': 75,
            'dribbling': 65,
            'defending': 88,
            'physical': 85
        }
    ]
    
    for player_data in players_data:
        player = Player(
            name=player_data['name'],
            position=player_data['position'],
            team=player_data['team'],
            jersey_number=player_data['jersey_number'],
            age=player_data['age'],
            overall_rating=player_data['overall_rating'],
            pace=player_data['pace'],
            shooting=player_data['shooting'],
            passing=player_data['passing'],
            dribbling=player_data['dribbling'],
            defending=player_data['defending'],
            physical=player_data['physical'],
            position_map=json.dumps({'ST': 'green', 'CF': 'green'}),
            detailed_skills=json.dumps({
                'pace': {'acceleration': 90, 'sprint_speed': 86},
                'shooting': {'finishing': 88, 'long_shots': 84, 'shot_power': 85, 'positioning': 87, 'volleys': 82, 'penalties': 80},
                'passing': {'short_pass': 83, 'long_pass': 80, 'vision': 84, 'crossing': 78, 'curve': 81, 'free_kick': 75},
                'dribbling': {'dribbling': 85, 'balance': 83, 'agility': 86, 'reactions': 84, 'ball_control': 87},
                'defending': {'man_marking': 40, 'standing_tackle': 42, 'interceptions': 48, 'heading': 50},
                'physical': {'strength': 75, 'aggression': 72, 'jumping': 80, 'stamina': 82}
            })
        )
        db.session.add(player)
    
    # Örnek maç ekle
    match1 = Match(
        name='Şampiyonluk Finali',
        home_team='Arena9 FC',
        away_team='Rakip Takım',
        home_score=3,
        away_score=2,
        match_date=datetime(2024, 10, 15, 20, 0),
        match_time='20:00',
        stadium='Arena9 Stadyumu',
        status='finished',
        image_url='https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800'
    )
    db.session.add(match1)
    
    db.session.commit()
    print("✅ Örnek veriler eklendi!")
    print("\n🎉 Hazır! Şimdi uygulamayı başlat: python app_updated.py")
    print("👤 Admin giriş: admin / admin123")
