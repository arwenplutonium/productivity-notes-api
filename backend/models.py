from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, UniqueConstraint

from backend.extensions import bcrypt, db


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('username', name='uq_user_username'),
        CheckConstraint('LENGTH(username) >= 3', name='ck_username_min_length'),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    notes = db.relationship('Note', back_populates='user', cascade='all, delete-orphan')

    @property
    def password(self):
        # Write-only attribute: the hash is never readable through the model.
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, plain_text_password):
        if not plain_text_password or len(plain_text_password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, plain_text_password):
        return bcrypt.check_password_hash(self.password_hash, plain_text_password)

    def validate_username(self):
        if not self.username or not self.username.strip():
            raise ValueError("Username must not be empty.")
        if len(self.username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(self.username) > 80:
            raise ValueError("Username must be 80 characters or fewer.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_username()

    def to_dict(self):
        # password_hash is deliberately left out of the payload.
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Note(db.Model):
    __tablename__ = 'notes'
    __table_args__ = (
        CheckConstraint('LENGTH(title) > 0', name='ck_note_title_not_empty'),
        CheckConstraint('LENGTH(content) > 0', name='ck_note_content_not_empty'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='notes')

    def validate_title(self):
        if not self.title or not self.title.strip():
            raise ValueError("Note title must not be empty.")
        if len(self.title) > 120:
            raise ValueError("Note title must be 120 characters or fewer.")

    def validate_content(self):
        if not self.content or not self.content.strip():
            raise ValueError("Note content must not be empty.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_title()
        self.validate_content()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
        }
