from app import app, db, Player, Match

with app.app_context():
    teams = db.session.query(Player.team).distinct().all()
    print("VALID_TEAMS:", [t[0] for t in teams])
    
    match = Match.query.get(1)
    if match:
        print(f"MATCH_TEAMS: '{match.home_team}' vs '{match.away_team}'")
