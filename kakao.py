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
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/talk'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'jpg'}

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
    if 'user_id' not in session:
        print('nnnn')
        return render_template('login.html')

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
    return redirect('/login')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User(request.form['id'], generate_password_hash(request.form['pw']))
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect('/')
    return render_template('signup.html')


@app.route('/chart', methods=['GET', 'POST'])
def charts():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = 'static/talk/' + filename
            with open(file_url, "r") as myfile:
                # print('ssssss',myfile.read().split('\n')[0:3],'eeee')

                talk_con = myfile.read()

            print(type(talk_con))
            chat = Chat(request.form['title'], talk_con, session['user_id'], file_url)
            db.session.add(chat)
            db.session.commit()
    matrix = []
    name_count = {}
    word_count = {}
    date_count = {}

    f = open(file_url, 'r')
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

    # print(matrix[1:3])
    # print(sorted_name)
    # print(sorted_word[0:20])
    # print(sorted_date[0:20])
    f.close()

    user_counts = len(sorted_name) - 1

    cha = Chat.query.filter_by(title=request.form['title']).first()
    cha.user_count = user_counts
    db.session.commit()
    return render_template('chart.html', name=sorted_name, word=sorted_word[40:50], date=sorted_date,
                           title=request.form['title'], user_count=user_counts)


@app.route('/chart/<string:chat_id>', methods=['GET', 'POST'])
def test(chat_id):
    if request.method == 'GET':
        cha = Chat.query.filter_by(title=chat_id).first()
        if cha is not None:
            error = True
        else:
            return redirect('/')
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = 'static/talk/' + filename
            with open(file_url, "r") as myfile:
                talk_con = '''Date,User,Message
2016-08-07 00:12:07,"임준오","h"
2016-08-07 00:28:16,"OI우형","hi"
2016-08-07 00:30:20,"홍인표","김연경이 누구임"
2016-08-07 00:30:42,"홍인표","연애인임?"
2016-08-07 00:31:27,"윤철민","ㄴㄴ"
2016-08-07 00:31:29,"정재원","배구국대"
2016-08-07 00:31:45,"정재원","사진"
2016-08-07 00:31:58,"정재원","난 펜싱 볼거다 이기야"
2016-08-07 00:32:09,"윤철민","ㅎ.ㅎ"
2016-08-07 00:32:25,"정재원","아람찡..."
2016-08-07 00:35:01,"윤철민","앙?"
2016-08-07 00:35:20,"OI우형","터키에서"
2016-08-07 00:35:21,"OI우형","뛰는"
2016-08-07 00:35:22,"OI우형","공격수"
2016-08-07 00:37:17,"정재원","?"
2016-08-07 00:37:27,"정재원","ㅁㅊ신아람 32강 탈락했었냐"'''

            print(type(talk_con))
            chat = Chat(request.form['title'], talk_con, session['user_id'], file_url)
            db.session.add(chat)
            db.session.commit()
    matrix = []
    name_count = {}
    word_count = {}
    date_count = {}

    f = open(cha.filename, 'r', encoding='utf8')
    csvReader = csv.reader(f)
    for row in csvReader:
        matrix.append(row)
    count = len(matrix)
    for name in matrix:
        if name[1] in name_count:
            name_count[name[1]] += 1
        else:
            name_count[name[1]] = 1
            user_count = 1
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
    sorted_date = sorted(date_count.items(), key=operator.itemgetter(0), reverse=True)
    print(matrix[1:3])
    print(sorted_name)
    print(sorted_word[0:20])
    sorted_word = sorted_word[0:20]
    user_counts = len(sorted_name) - 1
    f.close()
    return render_template('chart.html', name=sorted_name, word=sorted_word, date=sorted_date, title=chat_id,
                           user_count=user_counts)


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
    app.run(port=8080, debug=True, host="0.0.0.0")
