from app import app, db, Match, Player

with app.app_context():
    match = Match.query.first()
    if match:
        print(f"MATCH_FOUND: ID={match.id} {match.home_team} vs {match.away_team}")
        home_players = Player.query.filter_by(team=match.home_team).count()
        away_players = Player.query.filter_by(team=match.away_team).count()
        print(f"PLAYERS_FOUND: Home={home_players}, Away={away_players}")
        if match.mvp:
            print(f"MVP_FOUND: {match.mvp.name}")
        else:
            print("MVP_NOT_FOUND")
    else:
        print("NO_MATCHES")
