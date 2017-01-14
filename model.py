from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import csv
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
    title = db.Column(db.Text, nullable=False)
    filename = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    thumbnail1 = db.Column(db.Text, nullable=False)
    thumbnail2 = db.Column(db.Text, nullable=False)
    user_count = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, title, content, user_id, filename):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.thumbnail1, self.thumbnail2 = getThumbnails(content)
        self.user_count = 0
        self.filename = filename

    def __repr__(self):
        return self.content


def getThumbnails(content):
    content = content.split('\n')[1:]
    content.reverse()
    return content[1].split(',')[2].replace('"', ''), content[2].split(',')[2].replace('"', '')


def getUserCount(content):
    content = content.split('\n')[1:]
    content.reverse()
    content = content[1:]
    print('fffff',content[0],'fffff')

    for i in range(len(content)):
        if len(content[i].split(',')) > 2:
            content[i] = content[i].split(',')[1].replace('"', '')
    return len(set(content))
