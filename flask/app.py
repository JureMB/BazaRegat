#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template,  session, redirect, url_for, flash
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

        cur.execute("SELECT tekmovalec.sailno, tekmovalec.ime, tekmovalec.spol, tekmovalec.leto_rojstva, ime_kluba, "
                    "array_to_string(array_agg(coalesce(tocke::text, posebnosti) ORDER BY st_plova ASC), ',') AS tocke_plovi, "
                    "(sum(efektivne_tocke) - max(efektivne_tocke))::int AS net, "
                    "sum(efektivne_tocke)::int AS tot "
                    "FROM efektivne_tocke JOIN plov ON plov_idplov = plov.idplov "
                    "JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec "
                    "JOIN klubi_plovi ON klubi_plovi.idtekmovalec = tekmovalec_idtekmovalec AND klubi_plovi.plov_idplov = plov.idplov "
                    "WHERE regata_idregata = %s "
                    "GROUP BY tekmovalec_idtekmovalec, ime_kluba, tekmovalec.sailno, tekmovalec.ime, tekmovalec.spol, tekmovalec.leto_rojstva "
                    "ORDER BY net ASC, tot ASC,"
                    "array_agg(efektivne_tocke ORDER BY st_plova ASC) ASC, array_agg(coalesce(tocke::text, posebnosti) ORDER BY st_plova ASC) ASC ",
                    [id_reg])
        data_regata = []
        i = 1
        for element in cur:
            data_regata.append([i, element[0], element[1].title(), element[2], element[3], element[4]] + list(
                element[5].split(',')) + [element[6], element[7]])
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
        cur.execute("SELECT koeficient FROM regata WHERE  idregata = %s", [id_reg])
        for element in cur: # to je redundant!
            koef_regate = element[0]
        tocke_prvega = data_regata[0][-2]

        tocke_zadnjega = data_regata[-1][-2]
        for list in data_regata:
            zacasna = tekmovalci_dict.get(list[1], []) # id je jadro!!!
            zacasna.append([list[1], id_reg, list[0], list[-2], koef_regate, tocke_prvega, tocke_zadnjega])
            tekmovalci_dict[list[1]] = zacasna
    return tekmovalci_dict

def tocke(koef, zadnji, prvi, tocke):
    return koef*(50 +50*(zadnji-tocke)/(zadnji-prvi))

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
    conn = psycopg2.connect(database=auth_public.db, host=auth_public.host, user=auth_public.user, password=auth_public.password)
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
        session['regata_id'] = regata_id
        return redirect(url_for('regate_view', regata_id=session.get('regata_id')))
    return render_template('regate.html', form=form, form_type="inline")

@app.route('/regate/<regata_id>')
def regate_view(regata_id):
    id = int(regata_id)
    cur.execute("SELECT *, (SELECT ime FROM KLUB WHERE idklub = klub_idklub) FROM regata WHERE idregata = %s", [id])
    for element in cur: # to je redundant!
        title = element[1]
        # isKriterijska = element[2]
        startDate = '{}.{}.{}'.format(element[3].day, element[3].month, element[3].year)
        endDate = '{}.{}.{}'.format(element[4].day, element[4].month, element[4].year)
        # koeficient = element[5]
        klub = element[7]

    cur.execute("SELECT idplov FROM plov WHERE regata_idregata = %s", [id])
    nPlovov = 0
    idPlovi=[]
    for element in cur:
        nPlovov+=1
        idPlovi.append(element[0])

    data_plovi = []

    for i in range(nPlovov):
        idPlov = idPlovi[i]
        cur.execute("SELECT sailno, ime, spol, leto_rojstva, ime_kluba,"
                    " COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi JOIN tekmovalec"
                    " ON tekmovalec_idtekmovalec = idtekmovalec JOIN klubi_plovi ON"
                    " klubi_plovi.idtekmovalec = tekmovalec.idtekmovalec AND klubi_plovi.plov_idplov = %s"
                    " WHERE tocke_plovi.plov_idplov = %s ORDER BY tocke;"
                    "", (idPlov, idPlov))
        data_plov=[]
        j=1
        for element in cur:
            data_plov.append(Plov(j, element[0],element[1].title(),element[2],element[3],element[4],element[5]))
            j+=1
        data_plovi.append(data_plov)

    cur.execute("SELECT tekmovalec.sailno, tekmovalec.ime, tekmovalec.spol, tekmovalec.leto_rojstva, ime_kluba, "
                "array_to_string(array_agg(coalesce(tocke::text, posebnosti) ORDER BY st_plova ASC), ',') AS tocke_plovi, "
                "(sum(efektivne_tocke) - max(efektivne_tocke))::int AS net, "
                "sum(efektivne_tocke)::int AS tot "
                "FROM efektivne_tocke JOIN plov ON plov_idplov = plov.idplov "
                "JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec "
                "JOIN klubi_plovi ON klubi_plovi.idtekmovalec = tekmovalec_idtekmovalec AND klubi_plovi.plov_idplov = plov.idplov "
                "WHERE regata_idregata = %s "
                "GROUP BY tekmovalec_idtekmovalec, ime_kluba, tekmovalec.sailno, tekmovalec.ime, tekmovalec.spol, tekmovalec.leto_rojstva "
                "ORDER BY net ASC, tot ASC,"
                "array_agg(efektivne_tocke ORDER BY st_plova ASC) ASC, array_agg(coalesce(tocke::text, posebnosti) ORDER BY st_plova ASC) ASC ", [id])

    data_regata = []
    i = 1
    for element in cur:
        data_regata.append([i, element[0], element[1].title(), element[2], element[3], element[4]] + list(element[5].split(',')) + [element[6], element[7]])
        i += 1

    global conn
    global cur
    conn = psycopg2.connect(database=auth_public.db, host=auth_public.host, user=auth_public.user, password=auth_public.password)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return render_template('regate_view.html', title=title, klub=klub, startDate=startDate,
                           endDate=endDate, nPlovov = [i+1 for i in range(nPlovov)] ,data_regata=data_regata, data_plovi = data_plovi, id=id)

@app.route('/jadralci', methods=['GET', 'POST'])
def jadralci():
    jadralec_name = None
    form = JadralecForm()
    prikazi_opozorilo = False
    if form.validate_on_submit():
        old_id = session.get('jadralec_id')
        if old_id is not None:
            prikazi_opozorilo = True
        jadralec_name = form.insert_jadralec.data
        try:
            cur.execute("SELECT idtekmovalec, ime  FROM tekmovalec WHERE ime = %s", [jadralec_name.title()])
            for element in cur:
                jadralec_id = element[0]
            session['jadralec_id'] = jadralec_id
        except Exception:
            try:
                cur.execute("SELECT idtekmovalec, ime  FROM tekmovalec WHERE ime = %s", [jadralec_name.upper()])
                for element in cur:
                    jadralec_id = element[0]
                session['jadralec_id'] = jadralec_id
            except Exception:
                print(prikazi_opozorilo)
                return render_template('jadralci.html', form=form, form_type="inline", prikazi_opozorilo=prikazi_opozorilo)
        print(prikazi_opozorilo)
        return redirect(url_for('jadralci_view', jadralec_id=session.get('jadralec_id')))
    print(prikazi_opozorilo)
    return render_template('jadralci.html', form=form, form_type="inline", prikazi_opozorilo=prikazi_opozorilo)

@app.route('/jadralci/<jadralec_id>')
def jadralci_view(jadralec_id):
    id = int(jadralec_id)
    cur.execute("SELECT sailno, tekmovalec.ime, spol, leto_rojstva, klub.ime AS ime_kluba FROM klub JOIN clanstvo"
                " ON klub.idklub = clanstvo.klub_idklub JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = "
                "tekmovalec.idtekmovalec WHERE tekmovalec_idtekmovalec = %s", [id])
    for element in cur:  # to je redundant!
        sail_no = element[0]
        ime = element[1]
        spol = element[2]
        leto_rojstva = element[3]
        klub = element[4]

    tekmovalci_dict = all_data()
    rezultati_tekmovalec = tekmovalci_dict[sail_no]
    cur.execute("SELECT idregata, ime FROM regata")
    regate_dict = {}
    for element in cur:
        regate_dict[element[0]]=element[1]
    rezultat = []
    values=[]
    labels=[]
    values2=[]
    for element in rezultati_tekmovalec:
        values.append(element[2])
        values2.append(element[3])
        labels.append(regate_dict[element[1]])
        rezultat.append([regate_dict[element[1]],element[2],element[3]])

    data=[] # tabela ki se jo na koncu prikaže na strani
    return render_template('jadralci_view.html', ime=ime, sail_no = sail_no ,klub=klub, spol = spol, leto_rojstva =leto_rojstva,labels=labels, values =values,values2=values2, n=len(labels) )

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
                    "tekmovalec.idtekmovalec WHERE sailno = %s", [sailno])
        for element in cur:
            ime=element[1]
            spol=element[2]
            leto_rojstva=element[3]
            klub=element[4]
            zacasna = [ime, spol, leto_rojstva, klub]
        vsota_zacasna=[]
        for regata in jadralec:
            pike=regata[3]
            koef=regata[4]
            prvi=regata[5]
            zadnji=regata[6]
            # zacasna.append(tocke(koef, zadnji, prvi, tocke))
            vsota_zacasna.append(tocke(koef, zadnji, prvi, pike))
            vsota_zacasna.sort()
        vsota = vsota_zacasna[-4:]
        zacasna.append(round(sum(vsota),2))
        data.append(zacasna)

    # uredi po vrstici v seznamu
    data.sort(key=lambda x: x[-1])
    data_sorted= list(reversed(data))
    data_final=[]
    id_list=[]
    for i in range(len(data_sorted)):
        data_final.append([i+1]+data_sorted[i])
        cur.execute("SELECT idtekmovalec, ime  FROM tekmovalec WHERE ime=%s", [data_sorted[i][0]])
        for element in cur:
            id_list.append(element[0])
    print(id_list)
    return render_template('lestvica.html', data=data_final, id_list=id_list)

############################################
# Program
#if __name__ == '__main__': app.run(debug=True,host='0.0.0.0', port=5000)
if __name__ == '__main__': app.run(debug=True, port=8000)
