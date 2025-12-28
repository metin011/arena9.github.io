from app import app, db, Player, Match

with app.app_context():
    teams = [t[0] for t in db.session.query(Player.team).distinct().limit(2).all()]
    print(f"TEAMS_FOUND: {teams}")
    
    if len(teams) >= 2:
        match = Match.query.get(1)
        if match:
            match.home_team = teams[0]
            match.away_team = teams[1]
            match.home_score = 3
            match.away_score = 2
            db.session.commit()
            print(f"MATCH_UPDATED: {match.home_team} vs {match.away_team}")
        else:
            print("MATCH_NOT_FOUND")
    else:
        print("NOT_ENOUGH_TEAMS")
