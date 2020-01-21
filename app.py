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
        return redirect('login')

# LOGIN SECTION

@app.route('/login', methods=["GET", "POST"])
def login():
    if 'login' in session:
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            # engine = create_engine("postgresql+psycopg2://postgres:root@localhost/socialanalytics")
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
                            return redirect(url_for('home'))

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
                        return redirect(url_for('home'))

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

            return render_template('report.html', title='Twitter', names=columns[1:], accName=accName, tanggal1=tanggal1, tanggal2=tanggal2, date=date, followers=followers)

        connection.close()

        return render_template('report.html', title='Twitter', names=columns[1:], columns=columns, body_table=body_table)

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
        
            return render_template('report.html', title='Instagram', names=columns[1:], accName=accName, tanggal1=tanggal1, tanggal2=tanggal2, date=date, followers=followers)

        return render_template('report.html', title='Instagram', names=columns[1:], columns=columns, body_table=body_table)
    
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
        
            return render_template('report.html', title='Youtube', names=columns[1:], accName=accName, tanggal1=tanggal1, tanggal2=tanggal2, date=date, followers=followers)

        return render_template('report.html', title='Youtube', names=columns[1:], columns=columns, body_table=body_table)
    
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
        
            return render_template('report.html', title='Facebook', names=columns[1:], accName=accName, tanggal1=tanggal1, tanggal2=tanggal2, date=date, followers=followers)

        return render_template('report.html', title='Facebook', names=columns[1:], columns=columns, body_table=body_table)

    else:
        abort(404)

# ADD SECTION

@app.route('/twitter_add', methods=["GET", "POST"])
def twitter_add():
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

        if 'tambahAkun' in request.form and request.method == 'POST':
            akun = request.form.get('namaAkun')
            link = request.form.get('linkInput')

            columns_query = """SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'twitter';"""

            cursor.execute(columns_query)

            columns_result = cursor.fetchall()

            columns = []
            for column in columns_result:
                columns.append(column[0])

            if akun in columns:
                return redirect(url_for('twitter_add', alert='account_exists'))
            else:
                select_query = "SELECT name FROM createdate WHERE name='" + akun + "';"
                cursor.execute(select_query)

                select_result = cursor.fetchone()

                if select_result == None:
                    insert_query = "INSERT INTO createdate(name, twitter) VALUES (%s, %s)"
                    cursor.execute(insert_query, (akun, datetime.now().strftime("%Y-%m-%d"),))

                    connection.commit()

                else:
                    update_query = "UPDATE createdate SET twitter=%s WHERE name='" + akun + "';"
                    cursor.execute(update_query, (datetime.now().strftime("%Y-%m-%d"),))

                    connection.commit()

                select_query2 = "SELECT name FROM links_list WHERE name='" + akun + "';"
                cursor.execute(select_query2)

                select_result2 = cursor.fetchone()

                if select_result2 == None:
                    insert_query2 = "INSERT INTO links_list(name, twitter) VALUES(%s, %s)"
                    cursor.execute(insert_query2, (akun, link,))

                    connection.commit()

                else:
                    update_query2 = "UPDATE links_list SET twitter=%s WHERE name=%s;"
                    cursor.execute(update_query2, (link, akun,))

                    connection.commit()

                insert_query3 = "ALTER TABLE twitter ADD COLUMN " + akun + " BIGINT;"
                cursor.execute(insert_query3)

                connection.commit()

                return redirect(url_for('twitter_add', alert='add_success'))

        # if 'hapus' in request.form and request.method == 'POST':
        #     name = request.form.get('hapusAkun')

        #     delete_query1 = "UPDATE createdate SET twitter=null WHERE name='" + name + "';"
        #     cursor.execute(delete_query1)

        #     connection.commit()

        #     delete_query2 = "UPDATE links_list SET twitter=null WHERE name='" + name + "';"
        #     cursor.execute(delete_query2)

        #     connection.commit()

        #     delete_query3 = "ALTER TABLE twitter DROP COLUMN " + name + ";"
        #     cursor.execute(delete_query3)

        #     connection.commit()

        #     check_delete1 = "SELECT twitter, instagram, youtube, facebook FROM createdate WHERE name='" + name + "';"
        #     cursor.execute(check_delete1)

        #     check_result1 = cursor.fetchone()

        #     if not all(check_result1):
        #         delete = "DELETE FROM createdate WHERE name='" + name + "';"
        #         cursor.execute(delete)

        #         connection.commit()
        #     else:
        #         pass

        #     check_delete2 = "SELECT twitter, instagram, youtube, facebook FROM links_list WHERE name='" + name + "';"
        #     cursor.execute(check_delete1)

        #     check_result2 = cursor.fetchone()

        #     if not all(check_result2):
        #         delete = "DELETE FROM links_list WHERE name='" + name + "';"
        #         cursor.execute(delete)

        #         connection.commit()
        #     else:
        #         pass

        #     return redirect(url_for('twitter_add'))

        if 'filter' in request.form and request.method == 'POST':
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')
        
            date_query = "SELECT name, twitter FROM createdate WHERE twitter BETWEEN '" + date1 + "' AND '" + date2 + "';"
            cursor.execute(date_query)

            date_result = cursor.fetchall()

            names = []
            dates = []
            for tup in date_result:
                names.append(tup[0])

                if tup[1] == None:
                    dates.append(tup[1])
                else:
                    d = datetime.strptime(str(tup[1]), "%Y-%m-%d")
                    d = d.strftime("%d/%m/%Y")
                    dates.append(d)

            return render_template('add.html', title='Twitter', names=names, dates=dates, tanggal1=tanggal1, tanggal2=tanggal2)

        date_query = "SELECT name, twitter FROM createdate ORDER BY twitter DESC LIMIT 5;"
        cursor.execute(date_query)

        date_result = cursor.fetchall()

        names = []
        dates = []
        for tup in date_result:
            names.append(tup[0])

            if tup[1] == None:
                dates.append(tup[1])
            else:
                d = datetime.strptime(str(tup[1]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")
                dates.append(d)

        return render_template('add.html', title='Twitter', names=names, dates=dates)
    else:
        abort(404)

@app.route('/instagram_add', methods=["GET", "POST"])
def instagram_add():
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

        if 'tambahAkun' in request.form and request.method == 'POST':
            akun = request.form.get('namaAkun')
            link = request.form.get('linkInput')

            columns_query = """SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'instagram';"""

            cursor.execute(columns_query)

            columns_result = cursor.fetchall()

            columns = []
            for column in columns_result:
                columns.append(column[0])

            if akun in columns:
                return redirect(url_for('instagram_add', alert='account_exists'))
            else:
                select_query = "SELECT name FROM createdate WHERE name='" + akun + "';"
                cursor.execute(select_query)

                select_result = cursor.fetchone()

                if select_result == None:
                    insert_query = "INSERT INTO createdate(name, instagram) VALUES (%s, %s)"
                    cursor.execute(insert_query, (akun, datetime.now().strftime("%Y-%m-%d"),))

                    connection.commit()

                else:
                    update_query = "UPDATE createdate SET instagram=%s WHERE name='" + akun + "';"
                    cursor.execute(update_query, (datetime.now().strftime("%Y-%m-%d"),))

                    connection.commit()

                select_query2 = "SELECT name FROM links_list WHERE name='" + akun + "';"
                cursor.execute(select_query2)

                select_result2 = cursor.fetchone()

                if select_result2 == None:
                    insert_query2 = "INSERT INTO links_list(name, instagram) VALUES(%s, %s)"
                    cursor.execute(insert_query2, (akun, link,))

                    connection.commit()

                else:
                    update_query2 = "UPDATE links_list SET instagram=%s WHERE name=%s;"
                    cursor.execute(update_query2, (link, akun,))

                    connection.commit()

                insert_query3 = "ALTER TABLE instagram ADD COLUMN " + akun + " BIGINT;"
                cursor.execute(insert_query3)

                connection.commit()

                return redirect(url_for('instagram_add', alert='add_success'))

        if 'filter' in request.form and request.method == 'POST':
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')
        
            date_query = "SELECT name, instagram FROM createdate WHERE instagram BETWEEN '" + date1 + "' AND '" + date2 + "';"
            cursor.execute(date_query)

            date_result = cursor.fetchall()

            names = []
            dates = []
            for tup in date_result:
                names.append(tup[0])

                if tup[1] == None:
                    dates.append(tup[1])
                else:
                    d = datetime.strptime(str(tup[1]), "%Y-%m-%d")
                    d = d.strftime("%d/%m/%Y")
                    dates.append(d)

            return render_template('add.html', title='Instagram', names=names, dates=dates, tanggal1=tanggal1, tanggal2=tanggal2)

        date_query = "SELECT name, instagram FROM createdate ORDER BY instagram DESC LIMIT 5;"
        cursor.execute(date_query)

        date_result = cursor.fetchall()

        names = []
        dates = []
        for tup in date_result:
            names.append(tup[0])

            if tup[1] == None:
                dates.append(tup[1])
            else:
                d = datetime.strptime(str(tup[1]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")
                dates.append(d)

        return render_template('add.html', title='Instagram', names=names, dates=dates)
    else:
        abort(404)

@app.route('/youtube_add', methods=["GET", "POST"])
def youtube_add():
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

        if 'tambahAkun' in request.form and request.method == 'POST':
            akun = request.form.get('namaAkun')
            link = request.form.get('linkInput')

            columns_query = """SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'youtube';"""

            cursor.execute(columns_query)

            columns_result = cursor.fetchall()

            columns = []
            for column in columns_result:
                columns.append(column[0])

            if akun in columns:
                return redirect(url_for('youtube_add', alert='account_exists'))
            else:
                select_query = "SELECT name FROM createdate WHERE name='" + akun + "';"
                cursor.execute(select_query)

                select_result = cursor.fetchone()

                if select_result == None:
                    insert_query = "INSERT INTO createdate(name, youtube) VALUES (%s, %s)"
                    cursor.execute(insert_query, (akun, datetime.now().strftime("%Y-%m-%d"),))

                    connection.commit()

                else:
                    update_query = "UPDATE createdate SET youtube=%s WHERE name='" + akun + "';"
                    cursor.execute(update_query, (datetime.now().strftime("%Y-%m-%d"),))

                    connection.commit()

                select_query2 = "SELECT name FROM links_list WHERE name='" + akun + "';"
                cursor.execute(select_query2)

                select_result2 = cursor.fetchone()

                if select_result2 == None:
                    insert_query2 = "INSERT INTO links_list(name, youtube) VALUES(%s, %s)"
                    cursor.execute(insert_query2, (akun, link,))

                    connection.commit()

                else:
                    update_query2 = "UPDATE links_list SET youtube=%s WHERE name=%s;"
                    cursor.execute(update_query2, (link, akun,))

                    connection.commit()

                insert_query3 = "ALTER TABLE youtube ADD COLUMN " + akun + " BIGINT;"
                cursor.execute(insert_query3)

                connection.commit()

                return redirect(url_for('youtube_add', alert='add_success'))

        if 'filter' in request.form and request.method == 'POST':
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')
        
            date_query = "SELECT name, youtube FROM createdate WHERE youtube BETWEEN '" + date1 + "' AND '" + date2 + "';"
            cursor.execute(date_query)

            date_result = cursor.fetchall()

            names = []
            dates = []
            for tup in date_result:
                names.append(tup[0])

                if tup[1] == None:
                    dates.append(tup[1])
                else:
                    d = datetime.strptime(str(tup[1]), "%Y-%m-%d")
                    d = d.strftime("%d/%m/%Y")
                    dates.append(d)

            return render_template('add.html', title='Youtube', names=names, dates=dates, tanggal1=tanggal1, tanggal2=tanggal2)

        date_query = "SELECT name, youtube FROM createdate ORDER BY youtube DESC LIMIT 5;"
        cursor.execute(date_query)

        date_result = cursor.fetchall()

        names = []
        dates = []
        for tup in date_result:
            names.append(tup[0])

            if tup[1] == None:
                dates.append(tup[1])
            else:
                d = datetime.strptime(str(tup[1]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")
                dates.append(d)

        return render_template('add.html', title='Youtube', names=names, dates=dates)
    else:
        abort(404)

@app.route('/facebook_add', methods=["GET", "POST"])
def facebook_add():
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

        if 'tambahAkun' in request.form and request.method == 'POST':
            akun = request.form.get('namaAkun')
            link = request.form.get('linkInput')

            columns_query = """SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'facebook';"""

            cursor.execute(columns_query)

            columns_result = cursor.fetchall()

            columns = []
            for column in columns_result:
                columns.append(column[0])

            if akun in columns:
                return redirect(url_for('facebook_add', alert='account_exists'))
            else:
                select_query = "SELECT name FROM createdate WHERE name='" + akun + "';"
                cursor.execute(select_query)

                select_result = cursor.fetchone()

                if select_result == None:
                    insert_query = "INSERT INTO createdate(name, facebook) VALUES (%s, %s)"
                    cursor.execute(insert_query, (akun, datetime.now().strftime("%Y-%m-%d"),))

                    connection.commit()

                else:
                    update_query = "UPDATE createdate SET facebook=%s WHERE name='" + akun + "';"
                    cursor.execute(update_query, (datetime.now().strftime("%Y-%m-%d"),))

                    connection.commit()

                select_query2 = "SELECT name FROM links_list WHERE name='" + akun + "';"
                cursor.execute(select_query2)

                select_result2 = cursor.fetchone()

                if select_result2 == None:
                    insert_query2 = "INSERT INTO links_list(name, facebook) VALUES(%s, %s)"
                    cursor.execute(insert_query2, (akun, link,))

                    connection.commit()

                else:
                    update_query2 = "UPDATE links_list SET facebook=%s WHERE name=%s;"
                    cursor.execute(update_query2, (link, akun,))

                    connection.commit()

                insert_query3 = "ALTER TABLE facebook ADD COLUMN " + akun + " BIGINT;"
                cursor.execute(insert_query3)

                connection.commit()

                return redirect(url_for('facebook_add', alert='add_success'))

        if 'filter' in request.form and request.method == 'POST':
            tanggal1 = request.form.get('tanggal1')
            tanggal2 = request.form.get('tanggal2')

            date1 = datetime.strptime(tanggal1, '%d/%m/%Y')
            date1 = date1.strftime('%Y-%m-%d')

            date2 = datetime.strptime(tanggal2, '%d/%m/%Y')
            date2 = date2.strftime('%Y-%m-%d')
        
            date_query = "SELECT name, facebook FROM createdate WHERE facebook BETWEEN '" + date1 + "' AND '" + date2 + "';"
            cursor.execute(date_query)

            date_result = cursor.fetchall()

            names = []
            dates = []
            for tup in date_result:
                names.append(tup[0])

                if tup[1] == None:
                    dates.append(tup[1])
                else:
                    d = datetime.strptime(str(tup[1]), "%Y-%m-%d")
                    d = d.strftime("%d/%m/%Y")
                    dates.append(d)

            return render_template('add.html', title='Facebook', names=names, dates=dates, tanggal1=tanggal1, tanggal2=tanggal2)

        date_query = "SELECT name, facebook FROM createdate ORDER BY facebook DESC LIMIT 5;"
        cursor.execute(date_query)

        date_result = cursor.fetchall()

        names = []
        dates = []
        for tup in date_result:
            names.append(tup[0])

            if tup[1] == None:
                dates.append(tup[1])
            else:
                d = datetime.strptime(str(tup[1]), "%Y-%m-%d")
                d = d.strftime("%d/%m/%Y")
                dates.append(d)

        return render_template('add.html', title='Facebook', names=names, dates=dates)
    else:
        abort(404)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
