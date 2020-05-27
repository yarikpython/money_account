from new_mon_acc import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from time import time
import jwt


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    datejoin = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    categories = db.relationship('Category', backref='user', lazy='dynamic')
    history = db.relationship('History', backref='user', lazy='dynamic')
    latest_report = db.Column(db.String, default='default.png')

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithm='HS256')['reset_password']
        except:
            return
        return User.query.get(id)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sum = db.Column(db.Float, nullable=False, default=0.0)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    history = db.relationship('History', backref='category', lazy='dynamic')


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    spend = db.Column(db.Float, nullable=False, default=0.0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
