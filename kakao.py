from flask import Flask, render_template, g, session, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from model import *
import sqlite3
import requests
import csv
import operator
import os
from werkzeug import secure_filename

UPLOAD_FOLDER = 'static/talk'
ALLOWED_EXTENSIONS = set(['txt', 'csv', 'jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'development-key'


@app.before_request
def before_request():
    print(">> before request")
    if 'user_id' in session:
        g.user = User.query.filter_by(id=session['user_id']).first()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    matrix = []
    filelink = "static/talk/aaaa.csv"
    f = open(filelink, 'r', encoding='UTF-8')
    csvReader = csv.reader(f)
    for row in csvReader:
        matrix.append(row)

    matrix = sorted(matrix, reverse=True)
    talk_recent = matrix[1:3]
    talk_recent = sorted(talk_recent, reverse=True)
    return render_template('index.html', talks=talk_recent)


@app.route('/chart')
def chart():
    return render_template('chart.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usr = User.query.filter_by(username=request.form['id']).first()
        if usr is None:
            error = True
        elif not check_password_hash(usr.password, request.form['pw']):
            error = True
        else:
            session['user_id'] = usr.id
            return redirect('/')
        return render_template('login.html', failed=True)
    return render_template('login.html', failed=False)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User(request.form['id'], generate_password_hash(request.form['pw']))
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect('/')
    return render_template('signup.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    matrix = []
    name_count = {}
    word_count = {}
    date_count = {}

    filelink = "static/talk/" + filename
    f = open(filelink, 'r', encoding='UTF-8')
    csvReader = csv.reader(f)
    for row in csvReader:
        matrix.append(row)
    count = len(matrix)
    for name in matrix:
        if name[1] in name_count:
            name_count[name[1]] += 1
        else:
            name_count[name[1]] = 1
    for words in matrix:
        for word in words[2].split():
            if word in word_count:
                word_count[word] += 1
        else:
            word_count[word] = 1
    for date in matrix:
        time = date[0].split()
        day = time[0]
        if day in date_count:
            date_count[day] += 1
        else:
            date_count[day] = 1

    matrix = sorted(matrix, reverse=True)
    sorted_name = sorted(name_count.items(), key=operator.itemgetter(1), reverse=True)
    sorted_word = sorted(word_count.items(), key=operator.itemgetter(1), reverse=True)
    sorted_date = sorted(date_count.items(), key=operator.itemgetter(1), reverse=True)
    print(matrix[1:3])
    print(sorted_name)
    print(sorted_word[0:20])
    print(sorted_date[0:20])
    f.close()
    return render_template('chart.html', name=sorted_name, word=sorted_word, date=sorted_date)


@app.route('/users/<string:username>')
def user_profile(username):
    return render_template('profile.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return '''s
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="/test" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run(port=8080, debug=True)
