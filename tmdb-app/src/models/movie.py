from src import db

class Movie (db.Model):
    __tablename__ = 'movie'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    title = db.Column(
        db.String(255),
        unique=False,
        nullable=False
    )
    release_date = db.Column(
        db.Date,
        unique=False,
        nullable=True
    )
    rating = db.Column(
        db.Float,
        unique=False,
        nullable=True
    )
    imgUrl = db.Column(
        db.String(255),
        nullable=True
    )
    roster = db.Column(
        db.String(255),
        nullable=True
    )
    synopsis = db.Column(
        db.Text,
        nullable=True
    )
    genre = db.Column(
        db.String(255),
        nullable=True
    )
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=True
    )

    rating_user = db.Column(
        db.Float,
        unique=False,
        nullable=True
        )
    
    user = db.relationship('User', back_populates='movies')

    def __repr__(self):
        return '<Movie {}>'.format(self.title)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'synopsis': self.synopsis,
            'genre': self.genre,
            'rating': self.rating,
            'imgUrl': self.imgUrl,
            'roster': self.roster,
            'user_id': self.user_id,
            'rating_user': self.rating_user
        }