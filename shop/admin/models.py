from shop import db,login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Register.query.get(int(user_id))

class Register(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=False)
    username = db.Column(db.String(50),unique=True)
    email = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(200),unique=False)

    def __repr__(self):
        return '<Register %r>' % self.name