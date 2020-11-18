from datetime import datetime
from app import db

# create db
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    username = db.Column(db.String(64))


    def __repr__(self):
        return '<User: {}>'.format(self.id)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(64), db.ForeignKey('users.account')) # foreignkey: user
    senter = db.Column(db.String(64), db.ForeignKey('users.account')) # foreignkey: user
    message = db.Column(db.Text(64)) # no limit
    pub_date = db.Column(db.String, nullable=False,
                         default=datetime.now())
    # Setup the relationship to the User table
    owner_relationship = db.relationship('User', foreign_keys='Message.owner')
    senter_relationship = db.relationship('User', foreign_keys='Message.senter')


    def __repr__(self):
        return '<Message: {}>'.format(self.id)