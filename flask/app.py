#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template,  session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SelectField, SubmitField, StringField
from wtforms.validators import DataRequired
import auth_public
import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
# manager = Manager(app)
# moment = Moment(app)

conn = psycopg2.connect(database=auth_public.db, host=auth_public.host, user=auth_public.user, password=auth_public.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def intToStr(list):
    """ iz int 1 dobit ("1", "1") """
    string_list = []
    for number in list:
        string_list.append((str(number), str(number)))
    return string_list

# years=[('2017', '2017'), ('2018', '2018')]

def poizvedba1(nPlovov):
    str = "CREATE TEMPORARY TABLE delni2 AS SELECT DISTINCT plov_1.sailno, plov_1.ime," \
          " plov_1.spol, plov_1.leto_rojstva, klubi_plovi2.ime_kluba, plov_1.tocke_plov AS tocke_plov1"
    for i in range(nPlovov):
        if (i+1)>=2: str+=", plov_{0}.tocke_plov AS tocke_plov{0} ".format(i+1)
    str+="from plov_1 JOIN (SELECT klub.ime AS ime_kluba," \
         " idtekmovalec, plov_idplov, sailno FROM klub JOIN clanstvo" \
         " ON klub.idklub = clanstvo.klub_idklub JOIN tekmovalec" \
         " ON clanstvo.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec" \
         " JOIN tocke_plovi ON tocke_plovi.tekmovalec_idtekmovalec" \
         " = tekmovalec.idtekmovalec) AS klubi_plovi2 ON klubi_plovi2.sailno" \
         " = plov_1.sailno "
    for i in range(nPlovov):
        if (i + 1) >= 2: str += "JOIN plov_{0} ON plov_1.sailno = plov_{0}.sailno ".format(i + 1)
    str+="; " + poizvedba2(nPlovov)
    # print("str: ", str)
    return str

def poizvedba2(nPlovov):
    uvrsceni_data = uvrsceni(nPlovov)
    str2 = r"SELECT DISTINCT *, ( 0"
    for i in range(nPlovov):
        str2 += r"+ CASE WHEN tocke_plov{0}~E'^\\d+$' THEN tocke_plov{0}::integer ELSE {1} END".format(i + 1, uvrsceni_data[i])
    str2 += r") - greatest("

    for i in range(nPlovov):
        str2 += r"CASE WHEN tocke_plov{0}~E'^\\d+$' THEN tocke_plov{0}::integer ELSE {1} END,".format(i + 1,
                                                                                                      uvrsceni_data[i])

    str2 += r"0) AS net, ( 0"

    for i in range(nPlovov):
        str2 += r"+ CASE WHEN tocke_plov{0}~E'^\\d+$' THEN tocke_plov{0}::integer ELSE {1} END".format(i + 1,
                                                                                                       uvrsceni_data[i])

    str2 += r") AS tot FROM delni2 ORDER BY net ASC, tot ASC"

    for i in range(nPlovov):
        str2 += r", tocke_plov{} ASC".format(i + 1)
    str2 += r";"
    return str2

def uvrsceni(nPlovov):
    uvrsceni = []
    for i in range(nPlovov):
        cur.execute(r"SELECT count(DISTINCT tocke_plov)+1 FROM plov_{0} WHERE tocke_plov~E'^\\d+$'".format(i + 1))
        for element in cur:  # SAMO 1 popravi!
            # print('uvrsceni: ', element)
            uvrsceni.append(element[0])
    return uvrsceni

def all_data():
    '''Funkcija ki izvede poizvedbe po vseh regatah in podate uredi v slovar s ključi jader(ker je bilo tako najenostavneje)
     vrednosti pa so seznami seznamov podatkov po regatah kot je naveedeno spodaj.

    Oblika vrnjenega slovarja:
    ključ: jadro
    vsebina: [[podatki 1. regate], [podatki 2. regate], ..]
    notranji seznam: [podatki n. regate ] = [jadro, id_regate, mesto tekmovalca, točke tekmovalca, koef_regate, tocke_prvega, tocke_zadnjega]
    '''
    id_regate = []
    cur.execute("SELECT idregata FROM regata")
    for elment in cur:
        id_regate.append(elment[0])

    data = {}
    for id_reg in id_regate:
        # ------------------------------------------------------------------------------------------
        cur.execute("SELECT idplov FROM plov WHERE regata_idregata = {}".format(id_reg))
        nPlovov = 0
        idPlovi = []
        for element in cur:
            nPlovov += 1
            idPlovi.append(element[0])

        # cur.execute("CREATE TEMPORARY TABLE klubi_plovi AS SELECT klub.ime AS ime_kluba, idtekmovalec,"
        #             " plov_idplov FROM klub JOIN clanstvo ON klub.idklub = clanstvo.klub_idklub"
        #             " JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec"
        #             " JOIN tocke_plovi ON tocke_plovi.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec;")
        for i in range(nPlovov):
            cur.execute("CREATE TEMPORARY TABLE plov_{0} AS SELECT sailno, ime, spol, leto_rojstva, ime_kluba,"
                        " COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi JOIN tekmovalec"
                        " ON tekmovalec_idtekmovalec = idtekmovalec JOIN klubi_plovi ON"
                        " klubi_plovi.idtekmovalec = tekmovalec.idtekmovalec AND klubi_plovi.plov_idplov = {1}"
                        " WHERE tocke_plovi.plov_idplov = {1} ORDER BY tocke;"
                        "SELECT * FROM plov_{0};".format(i + 1, idPlovi[i]))

        cur.execute(poizvedba1(nPlovov))
        data_regata = []
        i = 1
        for element in cur:
            data_regata.append(
                [i, element[0], element[1].title(), element[2], element[3], element[4], element[5], element[6]])
            for j in range(nPlovov):
                data_regata[-1].append(element[7 + j])
            i += 1
        data[id_reg] = data_regata
        # konec
        global conn
        global cur
        conn = psycopg2.connect(database=auth_public.db, host=auth_public.host, user=auth_public.user, password=auth_public.password)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # onemogocimo transakcije
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return sort_tekmovalci(data)

def sort_tekmovalci(data):
    "pomožna funkcija ki vrne končno obliko opisano pri funkciji all_data()"
    tekmovalci_dict={}
    for (id_reg, data_regata) in data.items():
        cur.execute("SELECT koeficient FROM regata WHERE  idregata = {}".format(id_reg))
        for element in cur: # to je redundant!
            koef_regate = element[0]
        tocke_prvega = data_regata[0][-2]

        tocke_zadnjega = data_regata[-1][-2]
        for list in data_regata:
            zacasna = tekmovalci_dict.get(list[1], []) # id je jadro!!!
            zacasna.append([list[1], id_reg, list[0], list[-2], koef_regate, tocke_prvega, tocke_zadnjega]) #TU SE LAHKO DODa se podatke plovov! #jadro id regate, mesto tekmovalca, točke tekmovalca, ...
            tekmovalci_dict[list[1]] = zacasna
    return tekmovalci_dict

def tocke(koef, zadnji, prvi, tocke):
    return koef*(50 +50*(zadnji-tocke)/(zadnji-prvi))

# class RegateForm(FlaskForm):
#     cur.execute("SELECT zacetek FROM regata")
#     years = []
#     for date in cur:
#         years.append(date[0].year)
#     years=sorted(set(years))
#     years=intToStr(years)
#     select_years = SelectField('leto',choices=years, validators=[DataRequired()])
#     # regate=[] # podatki iz baze
#     # select_regata = SelectField('regata', choices=regate, validators=[DataRequired()])
#     submit = SubmitField('Izberi')

class RegateForm(FlaskForm):
    cur.execute("SELECT ime, zacetek, idregata FROM regata")
    regate=[]
    for regata in cur:
        zacasna = str(regata[0]) + ' ' + str(regata[1].day) + '.' + str(regata[1].month) + '.' + str(regata[1].year)
        regate.append((str(regata[2]), zacasna))
    select_regata = SelectField('regata', choices=regate, validators=[DataRequired()])
    submit = SubmitField('Izberi')

class JadralecForm(FlaskForm):
    insert_jadralec = StringField('Vnesite ime jadralca', validators=[DataRequired()])
    submit = SubmitField('Išči')

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
    global conn
    global cur
    conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # onemogocimo transakcije
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/regate', methods=['GET', 'POST'])
def regate():
    form = RegateForm()
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
        # isKriterijska = element[2]
        startDate = '{}.{}.{}'.format(element[3].day, element[3].month, element[3].year)
        endDate = '{}.{}.{}'.format(element[4].day, element[4].month, element[4].year)
        # koeficient = element[5]
        klub = element[7]

    cur.execute("SELECT idplov FROM plov WHERE regata_idregata = {}".format(id))
    nPlovov = 0
    idPlovi=[]
    for element in cur:
        nPlovov+=1
        idPlovi.append(element[0])

    data_plovi = []
    # cur.execute("CREATE TEMPORARY TABLE klubi_plovi AS SELECT klub.ime AS ime_kluba, idtekmovalec,"
    #             " plov_idplov FROM klub JOIN clanstvo ON klub.idklub = clanstvo.klub_idklub"
    #             " JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec"
    #             " JOIN tocke_plovi ON tocke_plovi.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec;")
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
            data_plov.append(Plov(j, element[0],element[1].title(),element[2],element[3],element[4],element[5]))
            j+=1
        data_plovi.append(data_plov)
    cur.execute(poizvedba1(nPlovov))
    data_regata = []
    i = 1
    for element in cur:
        data_regata.append([i, element[0], element[1].title(), element[2], element[3], element[4], element[5], element[6]])
        for j in range(nPlovov):
            data_regata[-1].append(element[7+j])
        i += 1

    global conn
    global cur
    conn = psycopg2.connect(database=auth_public.db, host=auth_public.host, user=auth_public.user, password=auth_public.password)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return render_template('regate_view.html', title=title, klub=klub, startDate=startDate,
                           endDate=endDate, nPlovov = [i+1 for i in range(nPlovov)] ,data_regata=data_regata, data_plovi = data_plovi)

@app.route('/jadralci', methods=['GET', 'POST'])
def jadralci():
    jadralec_name = None
    form = JadralecForm()
    if form.validate_on_submit():
        jadralec_name = form.insert_jadralec.data
        cur.execute("SELECT idtekmovalec, ime  FROM tekmovalec WHERE ime='{}'".format(jadralec_name))
        for element in cur:
            jadralec_id = element[0]
        session['jadralec_id'] = jadralec_id
        return redirect(url_for('jadralci_view', jadralec_id=session.get('jadralec_id')))
    return render_template('jadralci.html', form=form, form_type="inline")

@app.route('/jadralci/<jadralec_id>')
def jadralci_view(jadralec_id):
    id = int(jadralec_id)
    cur.execute("SELECT sailno, tekmovalec.ime, spol, leto_rojstva, klub.ime AS ime_kluba FROM klub JOIN clanstvo"
                " ON klub.idklub = clanstvo.klub_idklub JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = "
                "tekmovalec.idtekmovalec WHERE tekmovalec_idtekmovalec = {}".format(id))
    for element in cur:  # to je redundant!
        sail_no = element[0]
        ime = element[1]
        spol = element[2]
        leto_rojstva = element[3]
        klub = element[4]

    tekmovalci_dict = all_data()
    print("tekmovalci_dict: ", tekmovalci_dict)
    data=[] # tabela ki se jo na koncu prikaže na strani
    return render_template('jadralci_view.html', ime=ime, sail_no = sail_no ,klub=klub, spol = spol, leto_rojstva =leto_rojstva, data= data)

@app.route('/lestvica')
def lestvica():
    tekmovalci_dict = all_data()
    data=[]
    slovenci=[]
    for jadro in tekmovalci_dict:
        if jadro[:3] == "SLO":
            slovenci.append(tekmovalci_dict[jadro])
    for jadralec in slovenci:
        sailno = jadralec[0][0]
        cur.execute("SELECT sailno, tekmovalec.ime, spol, leto_rojstva, klub.ime AS ime_kluba FROM klub JOIN clanstvo"
                    " ON klub.idklub = clanstvo.klub_idklub JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = "
                    "tekmovalec.idtekmovalec WHERE sailno = '{}'".format(sailno))
        for element in cur:
            ime=element[1]
            spol=element[2]
            leto_rojstva=element[3]
            klub=element[4]
            zacasna = [ime, spol, leto_rojstva, klub]
        vsota=0
        for regata in jadralec:
            pike=regata[3]
            koef=regata[4]
            prvi=regata[5]
            zadnji=regata[6]
            # zacasna.append(tocke(koef, zadnji, prvi, tocke))
            vsota+=tocke(koef, zadnji, prvi, pike)
        zacasna.append(round(vsota,2))
        data.append(zacasna)

    # uredi po vrstici v seznamu
    data.sort(key=lambda x: x[-1])
    data_sorted= list(reversed(data))
    data_final=[]
    for i in range(len(data_sorted)):
        data_final.append([i+1]+data_sorted[i])
    return render_template('lestvica.html', data=data_final)

############################################
# Program
#if __name__ == '__main__': app.run(debug=True,host='0.0.0.0', port=5000)
if __name__ == '__main__': app.run(debug=True, port=5000)
