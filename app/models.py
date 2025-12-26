from hashlib import md5
from app import app, db, login_manager
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), default="user")
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship("Post", backref="user", lazy=True)
    replies = db.relationship(
        "Reply",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return f"User({self.id}, username={self.username}, email={self.email})"
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    replies = db.relationship("Reply", backref="post", lazy=True, cascade="all, delete-orphan")

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False, index=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

