from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///kanalytics.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.TEXT, nullable=False)
    password = db.Column(db.TEXT, nullable=False)
    chats = db.relationship('Chat', backref=db.backref('user', lazy='joined'), lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.username


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    thumbnail1 = db.Column(db.Text, nullable=False)
    thumbnail2 = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)

    def __int__(self, content, user_id):
        self.content = content
        self.user_id = user_id
        self.thumbnail1 = getThumbnails(content)[0]
        self.thumbnail2 = getxThumbnails(content)[1]

    def __repr__(self):
        return self.content


def getThumbnails(contain):
    matrix = []
    csvReader = csv.reader(contain)
    for row in csvReader:
        matrix.append(row)
    matrix = sorted(matrix, reverse=True)
    talk_recent = matrix[1:3]
    return talk_recent
