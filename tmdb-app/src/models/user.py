import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from src import db


class User(db.Model):

    __tablename__ = 'user'
    id = db.Column(
        db.String(36),
        primary_key=True,
        default= lambda: str(uuid.uuid4())
    )
    name = db.Column(
        db.String(64),
        index=False,
        unique=True,
        nullable=False
    )
    email = db.Column(
        db.String(80),
        index=True,
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.String(200),
        index=False,
        unique=False,
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=False
    )
    admin = db.Column(
        db.Boolean,
        index=False,
        unique=False,
        nullable=False,
        default=False
    )
    movies = db.relationship(
        'Movie',
        back_populates='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)
    
    def to_dict(self, include_movies=True):
        user_data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'admin': self.admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_movies:
            user_data['movies'] = [movie.to_dict() for movie in self.movies]

        return user_data