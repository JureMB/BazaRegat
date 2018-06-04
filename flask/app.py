#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template,  session, redirect, url_for
from flask_bootstrap import Bootstrap
# from flask_moment import Moment
# from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SelectField, SubmitField
from wtforms.validators import DataRequired
import auth
import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
# manager = Manager(app)
# moment = Moment(app)

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def intToStr(list): #iz int 1 dobit ("1", "1")
    string_list = []
    for number in list:
        string_list.append((str(number), str(number)))
    return string_list

years=[('2017', '2017'), ('2018', '2018')]

class RegateForm(FlaskForm):
    cur.execute("SELECT zacetek FROM regata")
    years = []
    for date in cur:
        years.append(date[0].year)
    years=sorted(set(years))
    years=intToStr(years)
    print(years)
    select_years = SelectField('leto',choices=years, validators=[DataRequired()])
    # regate=[] # podatki iz baze
    # select_regata = SelectField('regata', choices=regate, validators=[DataRequired()])
    submit = SubmitField('Izberi')

class ZacasniForm(FlaskForm):
    cur.execute("SELECT ime, zacetek, idregata FROM regata")
    regate=[]
    for regata in cur:
        zacasna = str(regata[0]) + ' ' + str(regata[1].day) + '.' + str(regata[1].month) + '.' + str(regata[1].year)
        regate.append((str(regata[2]), zacasna))
    print(regate)
    select_regata = SelectField('regata', choices=regate, validators=[DataRequired()])
    submit = SubmitField('Izberi')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/regate', methods=['GET', 'POST'])
def regate():
    form = ZacasniForm()
    if form.validate_on_submit():
        regata_id = form.select_regata.data
        print(regata_id)
        # regata_no_spaces =""
        # for char in regata:
        #     if (char == " " or char == "."):
        #         if not (regata_no_spaces[-1]=="_"):
        #             regata_no_spaces += "_"
        #     else: regata_no_spaces += char
        # session['regata'] = regata_no_spaces
        # session['regata_long'] = regata
        session['regata_id'] = regata_id
        # print(session['regata'])
        return redirect(url_for('regate_view', regata_id=session.get('regata_id')))
    return render_template('regate.html', form=form, form_type="inline")

@app.route('/regate/<regata_id>')
def regate_view(regata_id):
    id = int(regata_id)
    cur.execute("SELECT * FROM regata WHERE idregata = {}".format(id))
    for element in cur: # to je redundant!
        title = element[1]
        isKriterijska = element[2]
        startDate_temp = str(element[3])
        startDate = ''
        for char in startDate_temp:
            if char == '-': startDate+='.'
            else: startDate += char
        endDate_temp = str(element[4])
        endDate = ''
        for char in endDate_temp:
            if char == '-':
                endDate += '.'
            else:
                endDate += char
        koeficient = element[5]
        klub = element[6]

    print(title)
    return render_template('regate_view.html', title=title, klub=klub, startDate=startDate, endDate=endDate)


@app.route('/jadralci')
def jadralci():
    return render_template('jadralci.html')

@app.route('/lestvica')
def lestvica():
    return render_template('lestvica.html')


############################################
# Program
if __name__ == '__main__': app.run(debug=True,host='0.0.0.0', port=5000)
