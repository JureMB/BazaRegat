#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template,  session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SelectField, SubmitField, StringField
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


def intToStr(list):
    """ iz int 1 dobit ("1", "1") """
    string_list = []
    for number in list:
        string_list.append((str(number), str(number)))
    return string_list

# years=[('2017', '2017'), ('2018', '2018')]

class RegateForm(FlaskForm):
    cur.execute("SELECT zacetek FROM regata")
    years = []
    for date in cur:
        years.append(date[0].year)
    years=sorted(set(years))
    years=intToStr(years)
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
    select_regata = SelectField('regata', choices=regate, validators=[DataRequired()])
    submit = SubmitField('Izberi')

class JadralecForm:
    insert_jadralec = StringField('Vnesite ime jadralca', validators=[DataRequired()])
    submit = SubmitField('Išči')
class Regata(object):
    def __init__(self,mesto, salino, ime, spol, leto_rojstva, klub, prvi, drugi, tretji, cetrti, net, tot):
        self.mesto=mesto
        self.salino=salino
        self.ime=ime
        self.spol=spol
        self.leto_rojstva=leto_rojstva
        self.klub = klub
        self.prvi=prvi
        self.drugi=drugi
        self.tretji=tretji
        self.cetrti=cetrti
        self.net=net
        self.tot=tot

class Plov(object):
    def __init__(self, mesto, salino, ime, spol, leto_rojstva, klub, tocke):
        self.mesto=mesto
        self.salino=salino
        self.ime=ime
        self.spol=spol
        self.leto_rojstva=leto_rojstva
        self.klub = klub
        self.tocke=tocke


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
    cur.execute("SELECT *, (SELECT ime FROM KLUB WHERE idklub = klub_idklub) FROM regata WHERE idregata = {}".format(id))
    for element in cur: # to je redundant!
        title = element[1]
        isKriterijska = element[2]
        startDate = '{}.{}.{}'.format(element[3].day, element[3].month, element[3].year)
        endDate = '{}.{}.{}'.format(element[4].day, element[4].month, element[4].year)
        koeficient = element[5]
        klub = element[7]

    cur.execute("SELECT idplov FROM plov WHERE regata_idregata ={}".format(id))
    nPlovov = 0
    idPlovi=[]
    for element in cur:
        nPlovov+=1
        idPlovi.append(element[0])

    cur.execute("SELECT * FROM rezultati_nikola")
    data_regata=[]
    i=1
    for element in cur:
        # print(element)
        data_regata.append(Regata(i, element[0],element[1].title(),element[2],element[3],element[4],element[5],
                                  element[6],element[7],element[8],element[9], element[10]))
        i+=1

    data_plovi = []
    cur.execute("CREATE TEMPORARY TABLE klubi_plovi AS SELECT klub.ime AS ime_kluba, idtekmovalec,"
                " plov_idplov FROM klub JOIN clanstvo ON klub.idklub = clanstvo.klub_idklub"
                " JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec"
                " JOIN tocke_plovi ON tocke_plovi.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec;")

    for i in range(nPlovov):
        cur.execute("CREATE TEMPORARY TABLE plov_{0} AS SELECT sailno, ime, spol, leto_rojstva, ime_kluba,"
                    " COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi JOIN tekmovalec"
                    " ON tekmovalec_idtekmovalec = idtekmovalec JOIN klubi_plovi ON"
                    " klubi_plovi.idtekmovalec = tekmovalec.idtekmovalec AND klubi_plovi.plov_idplov = {1}"
                    " WHERE tocke_plovi.plov_idplov = {1} ORDER BY tocke;"
                    "SELECT * FROM plov_{0};".format(i+1, idPlovi[i]))
        data_plov=[]
        j=1
        for element in cur:
            print(element)
            data_plov.append(Plov(j, element[0],element[1].title(),element[2],element[3],element[4],element[5]))
            j+=1
        data_plovi.append(data_plov)


    # cur.execute("SELECT * FROM rezultati_nikola_2plov")
    # data_plov2 = []
    # i = 1
    # for element in cur:
    #     # print(element)
    #     data_plov2.append(Plov(i, element[0],element[1].title(),element[2],element[3],element[4],element[5]))
    #     i += 1
    #
    # cur.execute("SELECT * FROM rezultati_nikola_3plov")
    # data_plov3 = []
    # i = 1
    # for element in cur:
    #     # print(element)
    #     data_plov3.append(Plov(i, element[0],element[1].title(),element[2],element[3],element[4],element[5]))
    #     i += 1
    #
    # cur.execute("SELECT * FROM rezultati_nikola_4plov")
    # data_plov4 = []
    # i = 1
    # for element in cur:
    #     # print(element)
    #     data_plov4.append(Plov(i, element[0],element[1].title(),element[2],element[3],element[4],element[5]))
    #     i += 1
    return render_template('regate_view.html', title=title, klub=klub, startDate=startDate,
                           endDate=endDate, nPlovov = [i+1 for i in range(nPlovov)] ,data_regata=data_regata, data_plovi = data_plovi)


@app.route('/jadralci', methods=['GET', 'POST'])
def jadralci():
    form = JadralecForm()
    if form.validate_on_submit():
        jadralec_name = form.insert_jadralec.data
        session['jadralec_name'] = jadralec_name
        return redirect(url_for('jadralce_view', jadralec_name=session.get('jadralce_name')))
    return render_template('jadralci.html', form=form, form_type="inline")

@app.route('/lestvica')
def lestvica():
    cur.execute("SELECT * FROM rezultati_nikola")
    data = []
    i = 1
    for element in cur:
        data.append(Regata(i, element[0], element[1].title(), element[2], element[3], element[4], element[5],
                                  element[6], element[7], element[8], element[9], element[10]))
        i += 1
    return render_template('lestvica.html', data=data)
@app.route('/test')
def test():
    return render_template('test.html')
############################################
# Program
#if __name__ == '__main__': app.run(debug=True,host='0.0.0.0', port=5000)
if __name__ == '__main__': app.run(debug=True, port=5000)
