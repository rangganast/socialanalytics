from flask import Flask
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
import locale
import psycopg2
import urllib

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=13, minute=55)
def twitter():
    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
    # connection = psycopg2.connect(host='localhost',
    #                             port='5432',
    #                             user='postgres',
    #                             password='root',
    #                             database='socialanalytics')

    connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                    port='5432',
                                    user='eqftcddubymbhj',
                                    password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                    database='d51hcp79u206q8')

    cursor = connection.cursor()

    yesterday = datetime.now() - timedelta(days=1)
    
    date_query = "INSERT INTO twitter (date) VALUES(%s) ON CONFLICT DO NOTHING"
    cursor.execute(date_query, (yesterday.strftime("%Y-%m-%d"),))

    connection.commit()
    
    links_query = "SELECT name, twitter FROM links_list"
    cursor.execute(links_query)

    link_result = cursor.fetchall()

    twitter_dict = {}

    for tup in link_result:
        twitter_dict[tup[0]] = tup[1]

    for name, link in twitter_dict.items():
        if link == None:
            pass
        else:
            req = urllib.request.Request(link, headers={'User-Agent': "Magic Browser"})
            con = urllib.request.urlopen(req)
            soup = BeautifulSoup(con.read(), 'lxml')

            divs = soup.findAll('div', {'style': 'width: 150px; float: left;'})
            for div in divs[-1].find_all('a'):
                div.decompose()


            for div in divs[-1]:
                if '\n' in div:
                    pass
                else:
                    if 'K' in div:
                        div = div.replace('K', '')
                        div = float(div)
                        div = div * 1000
                        div = int(div)

                        insert_query = "UPDATE twitter SET " + name + " = %s WHERE date='" + yesterday.strftime("%Y-%m-%d") + "';"
                        cursor.execute(insert_query, (div,))

                        connection.commit()

                    else:
                        insert_query = "UPDATE twitter SET " + name + " = %s WHERE date='" + yesterday.strftime("%Y-%m-%d") + "';"
                        cursor.execute(insert_query, (locale.atoi(div),))

                        connection.commit()

    connection.close()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=13, minute=55)
def instagram():
    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
    # connection = psycopg2.connect(host='localhost',
    #                             port='5432',
    #                             user='postgres',
    #                             password='root',
    #                             database='socialanalytics')

    connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                    port='5432',
                                    user='eqftcddubymbhj',
                                    password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                    database='d51hcp79u206q8')

    cursor = connection.cursor()

    yesterday = datetime.now() - timedelta(days=1)
    
    date_query = "INSERT INTO instagram (date) VALUES(%s) ON CONFLICT DO NOTHING"
    cursor.execute(date_query, (yesterday.strftime("%Y-%m-%d"),))

    connection.commit()

    links_query = "SELECT name, instagram FROM links_list"
    cursor.execute(links_query)

    link_result = cursor.fetchall()

    instagram_dict = {}

    for tup in link_result:
        instagram_dict[tup[0]] = tup[1]

    for name, link in instagram_dict.items():
        if link == None:
            pass
        else:
            req = urllib.request.Request(
                link, headers={'User-Agent': "Magic Browser"})
            con = urllib.request.urlopen(req)
            soup = BeautifulSoup(con.read(), 'lxml')

            divs = soup.findAll('div', {'style': 'width: 120px; float: left;'})

            for div in divs[-2]:
                if '\n' in div:
                    pass
                else:
                    if 'K' in div:
                        div = div.replace('K', '')
                        div = float(div)
                        div = div * 1000
                        div = int(div)

                        insert_query = "UPDATE instagram SET " + name + " = %s WHERE date='" + yesterday.strftime("%Y-%m-%d") + "';"
                        cursor.execute(insert_query, (div,))

                        connection.commit()
                    else:

                        insert_query = "UPDATE instagram SET " + name + " = %s WHERE date='" + yesterday.strftime("%Y-%m-%d") + "';"
                        cursor.execute(insert_query, (locale.atoi(div),))

                        connection.commit()

    connection.close()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=13, minute=55)
def youtube():
    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
    # connection = psycopg2.connect(host='localhost',
    #                             port='5432',
    #                             user='postgres',
    #                             password='root',
    #                             database='socialanalytics')

    connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                    port='5432',
                                    user='eqftcddubymbhj',
                                    password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                    database='d51hcp79u206q8')

    cursor = connection.cursor()

    yesterday = datetime.now() - timedelta(days=1)

    date_query = "INSERT INTO youtube (date) VALUES(%s) ON CONFLICT DO NOTHING"
    cursor.execute(date_query, (yesterday.strftime("%Y-%m-%d"),))

    connection.commit()

    links_query = "SELECT name, youtube FROM links_list"
    cursor.execute(links_query)

    link_result = cursor.fetchall()

    youtube_dict = {}

    for tup in link_result:
        youtube_dict[tup[0]] = tup[1]

    for name, link in youtube_dict.items():
        if link == None:
            pass
        else:
            req = urllib.request.Request(
                link, headers={'User-Agent': "Magic Browser"})
            con = urllib.request.urlopen(req)
            soup = BeautifulSoup(con.read(), 'lxml')

            divs = soup.findAll('div', {'style': 'width: 140px; float: left;'})
            for div in divs[-2].find_all('a'):
                div.decompose()

            for div in divs[-2]:
                if '\n' in div:
                    pass
                else:
                    if 'K' in div:
                        div = div.replace('K', '')
                        div = float(div)
                        div = div * 1000
                        div = int(div)

                        insert_query = "UPDATE youtube SET " + name + " = %s WHERE date='" + yesterday.strftime("%Y-%m-%d") + "';"
                        cursor.execute(insert_query, (div,))

                        connection.commit()

                    else:
                        insert_query = "UPDATE youtube SET " + name + " = %s WHERE date='" + yesterday.strftime("%Y-%m-%d") + "';"
                        cursor.execute(insert_query, (locale.atoi(div),))

                        connection.commit()

    connection.close()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=13, minute=55)
def facebook():
    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
    # connection = psycopg2.connect(host='localhost',
    #                             port='5432',
    #                             user='postgres',
    #                             password='root',
    #                             database='socialanalytics')

    connection = psycopg2.connect(host='ec2-174-129-18-210.compute-1.amazonaws.com',
                                    port='5432',
                                    user='eqftcddubymbhj',
                                    password='3705cdefc407327451a047ea12704db9d87bb675f3bccc298729e085ca2b6367',
                                    database='d51hcp79u206q8')

    cursor = connection.cursor()

    yesterday = datetime.now() - timedelta(days=1)

    date_query = "INSERT INTO facebook (date) VALUES(%s) ON CONFLICT DO NOTHING"
    cursor.execute(date_query, (yesterday.strftime("%Y-%m-%d"),))

    connection.commit()

    links_query = "SELECT name, facebook FROM links_list"
    cursor.execute(links_query)

    link_result = cursor.fetchall()

    facebook_dict = {}

    for tup in link_result:
        facebook_dict[tup[0]] = tup[1]

    for name, link in facebook_dict.items():
        if link == None:
            pass
        else:
            req = urllib.request.Request(
                link, headers={'User-Agent': "Magic Browser"})
            con = urllib.request.urlopen(req)
            soup = BeautifulSoup(con.read(), 'lxml')

            divs = soup.findAll('div', {'style': 'width: 120px; float: left;'})

            for div in divs[-2]:
                if '\n' in div:
                    pass
                else:
                    if 'K' in div:
                        div = div.replace('K', '')
                        div = float(div)
                        div = div * 1000
                        div = int(div)

                        insert_query = "UPDATE facebook SET " + name + " = %s WHERE date='" + yesterday.strftime("%Y-%m-%d") + "';"
                        cursor.execute(insert_query, (div,))

                        connection.commit()

                    else:
                        insert_query = "UPDATE facebook SET " + name + " = %s WHERE date='" + yesterday.strftime("%Y-%m-%d") + "';"
                        cursor.execute(insert_query, (locale.atoi(div),))

                        connection.commit()

    connection.close()

sched.start()
