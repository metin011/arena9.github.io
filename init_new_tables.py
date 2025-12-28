from app import app, db, PlayerRating, PlayerComment

with app.app_context():
    db.create_all()
    print("Rating and Comment tables created successfully!")
