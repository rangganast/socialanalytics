from flask import Flask, render_template, redirect, request, session, abort, url_for
from datetime import datetime, timedelta
import locale
import psycopg2
import urllib
import urllib3
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

# app = Flask(__name__, static_folder='static/')
app = Flask(__name__, static_folder='/app/static/')
app.config['SECRET_KEY'] = 'pbkdf2:sha256:150000$tD7V40IU$60ffd25fd78e9f3930e8fcbb3375580d6cd5a4e4c3798047cc611fe9e9366b0e'

# connection = psycopg2.connect(host='localhost',
#                                 port='5432',
#                                 user='postgres',
#                                 password='root',
#                                 database='socialanalytics')

connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                port='5432',
                                user='eqftcddubymbhj',
                                password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                database='d51hcp79u206q8')

cursor = connection.cursor()
names_query = "SELECT name FROM links_list"
cursor.execute(names_query)

names_result = cursor.fetchall()

names = []
for tup in names_result:
    names.append(tup[0])

@app.route('/', methods=["GET", "POST"])
def home():
    if 'login' in session:
        # connection = psycopg2.connect(host='localhost',
        #             port='5432',
        #             user='postgres',
        #             password='root',
        #             database='socialanalytics')

        connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                        port='5432',
                                        user='eqftcddubymbhj',
                                        password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                        database='d51hcp79u206q8')

        cursor = connection.cursor()

        yesterday = datetime.now() - timedelta(days=1)
        
        socials = ['Instagram', 'Twitter', 'Youtube', 'Facebook']

        if request.method == "POST":
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')

            main_table_custom = {}
            for social in socials:
                name = social.lower()

                columns_query = """SELECT column_name
                FROM information_schema.columns 
                WHERE table_name = '""" + name + """';"""

                cursor.execute(columns_query)

                columns_result = cursor.fetchall()

                columns = []
                for column in columns_result:
                    if column[0] == 'id':
                        pass
                    else:
                        columns.append(column[0])

                select_query = "SELECT * FROM " + name + " WHERE date BETWEEN '" + date1 + "' AND '" + date2 + "';"
                cursor.execute(select_query)

                select_result = cursor.fetchall()

                body_table = []
                for tup in select_result:
                    tup = list(tup)
                    del tup[0]

                    d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
                    d = d.strftime("%d/%m/%Y")
                    tup[0] = d

                    body_table.append(tup)

                main_table_custom[social] = [columns, body_table]

            connection.close()

            return render_template('home.html', main_table_custom=main_table_custom, tanggal1=tanggal1, tanggal2=tanggal2)

        main_table = {}
        for social in socials:
            name = social.lower()

            columns_query = """SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = '""" + name + """';"""

            cursor.execute(columns_query)

            columns_result = cursor.fetchall()

            columns = []
            for column in columns_result:
                if column[0] == 'id':
                    pass
                else:
                    columns.append(column[0])

            select_query = "SELECT * FROM " + name + " ORDER BY date DESC LIMIT 10"
            cursor.execute(select_query)

            select_result = cursor.fetchall()

            body_table = []
            for tup in select_result:
                tup = list(tup)
                del tup[0]

                d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")
                tup[0] = d

                body_table.append(tup)

            main_table[social] = [columns, body_table]

        connection.close()

        return render_template('home.html', main_table=main_table)
    else:
        abort(404)

# LOGIN SECTION

@app.route('/login', methods=["GET", "POST"])
def login():
    if 'login' in session:
        return redirect(url_for('twitter_report'))
    else:
        # if request.method == 'POST':
        #     engine = create_engine("postgresql+psycopg2://postgres:root@localhost/socialanalytics")
            engine = create_engine("postgres://eqftcddubymbhj:3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367@ec2-174-129-18-210.compute-1.amazonaws.com:5432/d51hcp79u206q8")
            db = scoped_session(sessionmaker(bind=engine))

            username = request.form.get('username')
            password = request.form.get('password')

            usernamedata = db.execute("SELECT username FROM users WHERE username='" + username + "'").fetchone()
            passworddata = db.execute("SELECT password FROM users WHERE username='" + username + "'").fetchone()

            if usernamedata == None:
                super_usernamedata = db.execute("SELECT superusername FROM superusers WHERE superusername='" + username + "'").fetchone()
                super_passworddata = db.execute("SELECT password FROM superusers WHERE superusername='" + username + "'").fetchone()
                
                if super_usernamedata == None:
                    error_msg = 'Username atau password salah'
                    return render_template('login.html', error_msg=error_msg)
                else:
                    for data in super_passworddata:
                        if check_password_hash(data, password) == False:
                            error_msg = 'Username atau password salah'
                            return render_template('login.html', error_msg=error_msg)
                        else:
                            session["login"] = True
                            session["username"] = username
                            session["superuser"] = True
                            return redirect(url_for('twitter_report'))

                error_msg = 'Username atau password salah'
                return render_template('login.html', error_msg=error_msg)

            else:
                for data in passworddata:
                    if check_password_hash(data, password) == False:
                        error_msg = 'Username atau password salah'
                        return render_template('login.html', error_msg=error_msg)
                    else:
                        session["login"] = True
                        session["username"] = username
                        return redirect(url_for('twitter_report'))

        return render_template('login.html')

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.pop('login', None)
    session.pop('username', None)
    if 'superuser' in session:
        session.pop('superuser', None)

    return redirect(url_for('login'))

# REPORT SECTION

@app.route('/twitter_report', methods=["GET", "POST"])
def twitter_report():
    if 'login' in session:
        # connection = psycopg2.connect(host='localhost',
        #                         port='5432',
        #                         user='postgres',
        #                         password='root',
        #                         database='socialanalytics')

        connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                        port='5432',
                                        user='eqftcddubymbhj',
                                        password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                        database='d51hcp79u206q8')

        cursor = connection.cursor()

        columns_query = """SELECT column_name
        FROM information_schema.columns 
        WHERE table_name = 'twitter';"""

        cursor.execute(columns_query)

        columns_result = cursor.fetchall()

        columns = []
        for column in columns_result:
            if column[0] == 'id':
                pass
            else:
                columns.append(column[0])

        select_query = "SELECT * FROM twitter ORDER BY date DESC LIMIT 10"
        cursor.execute(select_query)

        select_result = cursor.fetchall()

        body_table = []
        for tup in select_result:
            tup = list(tup)
            del tup[0]

            d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
            d = d.strftime("%d/%m/%Y")
            tup[0] = d

            body_table.append(tup)

        if request.method == "POST":
            accName = request.form.get('namaAkun')
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')

            select_query = "SELECT date, " + accName + " FROM twitter WHERE date BETWEEN '" + date1 + "' AND '" + date2 + "';"
            cursor.execute(select_query)

            select_result = cursor.fetchall()

            date = []
            followers = []
            for tup in select_result:
                d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")

                date.append(d)
                followers.append(tup[1])
        
            connection.close()

            return render_template('report.html', title='Twitter', names=names, accName=accName, tanggal1=tanggal1, tanggal2=tanggal2, date=date, followers=followers)

        connection.close()

        return render_template('report.html', title='Twitter', names=names, columns=columns, body_table=body_table)

    else:
        abort(404)

@app.route('/instagram_report', methods=["GET", "POST"])
def instagram_report():
    if 'login' in session:
        # connection = psycopg2.connect(host='localhost',
        #                         port='5432',
        #                         user='postgres',
        #                         password='root',
        #                         database='socialanalytics')

        connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                        port='5432',
                                        user='eqftcddubymbhj',
                                        password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                        database='d51hcp79u206q8')

        cursor = connection.cursor()

        columns_query = """SELECT column_name
        FROM information_schema.columns 
        WHERE table_name = 'instagram';"""

        cursor.execute(columns_query)

        columns_result = cursor.fetchall()

        columns = []
        for column in columns_result:
            if column[0] == 'id':
                pass
            else:
                columns.append(column[0])

        select_query = "SELECT * FROM instagram ORDER BY date DESC LIMIT 10"
        cursor.execute(select_query)

        select_result = cursor.fetchall()

        body_table = []
        for tup in select_result:
            tup = list(tup)
            del tup[0]

            d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
            d = d.strftime("%d/%m/%Y")
            tup[0] = d

            body_table.append(tup)

        if request.method == "POST":
            accName = request.form.get('namaAkun')
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')

            select_query = "SELECT date, " + accName + " FROM instagram WHERE date BETWEEN '" + date1 + "' AND '" + date2 + "';"
            cursor.execute(select_query)

            select_result = cursor.fetchall()

            connection.close()

            date = []
            followers = []
            for tup in select_result:
                d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")

                date.append(d)
                followers.append(tup[1])
        
            return render_template('report.html', title='Instagram', names=names, accName=accName, tanggal1=tanggal1, tanggal2=tanggal2, date=date, followers=followers)

        return render_template('report.html', title='Instagram', names=names, columns=columns, body_table=body_table)
    
    else:
        abort(404)

@app.route('/youtube_report', methods=["GET", "POST"])
def youtube_report():
    if 'login' in session:
        # connection = psycopg2.connect(host='localhost',
        #                         port='5432',
        #                         user='postgres',
        #                         password='root',
        #                         database='socialanalytics')

        connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                        port='5432',
                                        user='eqftcddubymbhj',
                                        password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                        database='d51hcp79u206q8')

        cursor = connection.cursor()

        columns_query = """SELECT column_name
        FROM information_schema.columns 
        WHERE table_name = 'youtube';"""

        cursor.execute(columns_query)

        columns_result = cursor.fetchall()

        columns = []
        for column in columns_result:
            if column[0] == 'id':
                pass
            else:
                columns.append(column[0])

        select_query = "SELECT * FROM youtube ORDER BY date DESC LIMIT 10"
        cursor.execute(select_query)

        select_result = cursor.fetchall()

        body_table = []
        for tup in select_result:
            tup = list(tup)
            del tup[0]

            d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
            d = d.strftime("%d/%m/%Y")
            tup[0] = d

            body_table.append(tup)

        if request.method == "POST":
            accName = request.form.get('namaAkun')
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')

            select_query = "SELECT date, " + accName + " FROM youtube WHERE date BETWEEN '" + date1 + "' AND '" + date2 + "';"
            cursor.execute(select_query)

            select_result = cursor.fetchall()

            connection.close()

            date = []
            followers = []
            for tup in select_result:
                d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")

                date.append(d)
                followers.append(tup[1])
        
            return render_template('report.html', title='Youtube', names=names, accName=accName, tanggal1=tanggal1, tanggal2=tanggal2, date=date, followers=followers)

        return render_template('report.html', title='Youtube', names=names, columns=columns, body_table=body_table)
    
    else:
        abort(404)

@app.route('/facebook_report', methods=["GET", "POST"])
def facebook_report():
    if 'login' in session:
        # connection = psycopg2.connect(host='localhost',
        #                         port='5432',
        #                         user='postgres',
        #                         password='root',
        #                         database='socialanalytics')

        connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                        port='5432',
                                        user='eqftcddubymbhj',
                                        password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                        database='d51hcp79u206q8')

        cursor = connection.cursor()

        columns_query = """SELECT column_name
        FROM information_schema.columns 
        WHERE table_name = 'facebook';"""

        cursor.execute(columns_query)

        columns_result = cursor.fetchall()

        columns = []
        for column in columns_result:
            if column[0] == 'id':
                pass
            else:
                columns.append(column[0])

        select_query = "SELECT * FROM facebook ORDER BY date DESC LIMIT 10"
        cursor.execute(select_query)

        select_result = cursor.fetchall()

        body_table = []
        for tup in select_result:
            tup = list(tup)
            del tup[0]

            d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
            d = d.strftime("%d/%m/%Y")
            tup[0] = d

            body_table.append(tup)

        if request.method == "POST":
            accName = request.form.get('namaAkun')
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')

            select_query = "SELECT date, " + accName + " FROM facebook WHERE date BETWEEN '" + date1 + "' AND '" + date2 + "';"
            cursor.execute(select_query)

            select_result = cursor.fetchall()

            connection.close()

            date = []
            followers = []
            for tup in select_result:
                d = datetime.strptime(str(tup[0]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")

                date.append(d)
                followers.append(tup[1])
        
            return render_template('report.html', title='Facebook', names=names, accName=accName, tanggal1=tanggal1, tanggal2=tanggal2, date=date, followers=followers)

        return render_template('report.html', title='Facebook', names=names, columns=columns, body_table=body_table)

    else:
        abort(404)

# ADD SECTION

@app.route('/twitter_add', methods=["GET", "POST"])
def twitter_add():
    return render_template('add.html', title='Twitter', names=names)

@app.route('/instagram_add', methods=["GET", "POST"])
def instagram_add():
    return render_template('add.html', title='Instagram', names=names)

@app.route('/youtube_add', methods=["GET", "POST"])
def youtube_add():
    return render_template('add.html', title='Youtube', names=names)

@app.route('/facebook_add', methods=["GET", "POST"])
def facebook_add():
    return render_template('add.html', title='Facebook', names=names)

# USER MANAGEMENT SECTION

if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
