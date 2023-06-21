import datetime
from flask import Blueprint, abort,flash, make_response, render_template, redirect, url_for, request
from flaskr import dienstplan_generator
from flaskr.db import get_db
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/dienstplan')
@login_required
def dienstplan():
    db = get_db()
    date_str = request.args.get("date", type=str)
    generate = request.args.get("generate", type=bool)

    # wenn kein datum angegeben wurde, heutiges datum verwenden
    if date_str == None:
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    if generate:
        dienstplan_generator.generate_dienstplaene()
    
    # besuche aus datenbank laden
    appointments = db.execute("""SELECT *
                            FROM Besuche
                            INNER JOIN Kunde ON Besuche.Kunden_ID = Kunde.Kunden_ID
                            INNER JOIN Adresse ON Kunde.Adresse = Adresse.Adresse_ID
                            WHERE Mitarbeiter_ID = ? AND Datum = ?""", [current_user.ID, date]).fetchall()

    print("found ", len(appointments), " appointments")
    
    return render_template("dienstplan.html", appointments=appointments, Mitarbeiter=current_user, date=date)




#Ansicht der Krankschreibungen
@main.route('/verwaltung', methods=["GET","POST"])
@main.route('/verwaltung/<mbPT>', methods=["GET","POST"])
@login_required
def verwaltung(mbPT=None):
    if current_user.Rolle != "Verwaltung":
        abort(403)

    cursor = get_db().cursor()
    mb_krankmeldung = """SELECT Mitarbeiter.Vorname, Mitarbeiter.Nachname, Dienstbefreiung_Mitarbeiter.Start_Datum, Dienstbefreiung_Mitarbeiter.Ende_Datum 
            FROM Dienstbefreiung_Mitarbeiter JOIN Mitarbeiter ON Mitarbeiter.MB_ID = Dienstbefreiung_Mitarbeiter.Mitarbeiter_ID;"""
    pt_krankmeldung = """ SELECT Kunde.Vorname, Kunde.Nachname, Krankschreibung_Kunde.Start_Datum, Krankschreibung_Kunde.Ende_Datum
            FROM Krankschreibung_Kunde JOIN Kunde ON Kunde.Kunden_ID = Krankschreibung_Kunde.Kunden_ID;"""


    if mbPT == 'MB':
        result = list(cursor.execute(mb_krankmeldung).fetchall())
        krank = "Mitarbeiter"
    else:
        result = list(cursor.execute(pt_krankmeldung).fetchall())
        krank = "Patienten"
    getRaum()
    return render_template("verwaltung.html", Mitarbeiter=current_user, result=result, krank=krank)





@main.route('/krankMB')
@login_required
def krankMB():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    return render_template("krankMB.html", Mitarbeiter=current_user)


@main.route('/krankPT')
@login_required
def krankPT():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    return render_template("krankPT.html")

#Eintragung der Mitarbeiter Krankschreibung
@main.route('/krankMB', methods=["POST"])
@login_required
def krankMB_post():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    Vorname = request.form.get('Vorname').strip()
    Nachname = request.form.get('Nachname').strip()
    VonDatum = request.form.get('VonDatum').strip()
    EndeDatum = request.form.get('EndeDatum').strip()

    ID_cmd = "SELECT MB_ID FROM Mitarbeiter WHERE Vorname=? AND Nachname=?;"

    conn = get_db()
    cursor = conn.cursor()

    ID = cursor.execute(ID_cmd, [Vorname,Nachname] ).fetchone()
    #Existiert Mitarbeiter?
    if not ID:
        flash("Nutzer nicht gefunden")
        return redirect(url_for('main.krankMB'))

    #Schreibe Krankschreibung
    sql_command = "INSERT INTO Dienstbefreiung_Mitarbeiter(Mitarbeiter_ID, Start_Datum, Ende_Datum) VALUES ( ?, ?, ?);"
    cursor.execute(sql_command, [str(ID[0]), VonDatum, EndeDatum])
    conn.commit()

    return redirect(url_for('main.verwaltung'))

#Eintragung der Patienten Krankschreibungen
@main.route('/krankPT', methods=["POST"])
@login_required
def krankPT_post():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    Vorname = request.form.get('Vorname').strip()
    Nachname = request.form.get('Nachname').strip()
    VonDatum = request.form.get('VonDatum').strip()
    EndeDatum = request.form.get('EndeDatum').strip()
    
    ID_cmd = "SELECT Kunden_ID FROM Kunde WHERE Vorname=? AND Nachname=?;"

    conn = get_db()
    cursor = conn.cursor()
    ID = cursor.execute(ID_cmd, [Vorname, Nachname]).fetchone()
    #Existiert Patient?
    if not ID:
        flash("Patient nicht gefunden")
        return redirect(url_for('main.krankPT'))

    #Schreibe Krankschreibung
    sql_command = "INSERT INTO Krankschreibung_Kunde(Kunden_ID, Start_Datum, Ende_Datum) VALUES ( ?, ?, ?);"
    cursor.execute(sql_command, [str(ID[0]), VonDatum, EndeDatum])
    conn.commit()


    return redirect(url_for('main.verwaltung'))


#Liste der Patienten
@main.route('/patienten-liste')
@login_required
def patienten_liste():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    result = list(get_db().execute("SELECT * FROM Kunde INNER JOIN Adresse ON Kunde.Adresse = Adresse.Adresse_ID").fetchall())
    return render_template('liste.html', Mitarbeiter=current_user, result=result, personen_type="Patienten")

#Liste der Mitarbeiter
@main.route('/mitarbeiter-liste')
@login_required
def mitarbeiter_liste():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    result = list(get_db().execute("SELECT * FROM Mitarbeiter INNER JOIN Adresse ON Mitarbeiter.Adresse = Adresse.Adresse_ID").fetchall())
    return render_template('liste.html', Mitarbeiter=current_user, result=result, personen_type="Mitarbeiter")

@main.route('/anmeldenMB')
@login_required
def anmeldenMB():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    return render_template("anmeldenMB.html")

#meldet Mitarbeiter in Datenbank an
@main.route('/anmeldenMB', methods=["POST"])
@login_required
def anmeldenMB_post():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    Vorname = request.form.get('Vorname').strip()
    Nachname = request.form.get('Nachname').strip()
    Position = request.form.get('Position')
    Strasse = request.form.get('Straße').strip()
    HNum = request.form.get('Hausnummer').strip()
    PLZ = request.form.get('PLZ').strip()
    Ort = request.form.get('Ort').strip()

    
    AdresseID = setAdressegetID(Strasse, HNum, PLZ, Ort)

    sql_command = "INSERT INTO Mitarbeiter(Vorname, Nachname, Rolle, Adresse) VALUES (?, ?, ?, ?);"
    con = get_db()
    cursor = con.cursor()

    cursor.execute(sql_command, [Vorname, Nachname, str(Position), AdresseID])
    con.commit()

    return redirect(url_for('main.mitarbeiter_liste'))


@main.route('/anmeldenPT')
@login_required
def anmeldenPT():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    return render_template("anmeldenPT.html")

#meldet Patienten in Datenbank an
@main.route('/anmeldenPT', methods=["POST"])
@login_required
def anmeldenPT_post():
    if current_user.Rolle != "Verwaltung":
        abort(403)

    Vorname = request.form.get('Vorname').strip()
    Nachname = request.form.get('Nachname').strip()
    Rolle = request.form.get('Rolle')
    Nummer = request.form.get('Nummer').strip()
    Besuche = request.form.get('Besuche')
    Strasse = request.form.get('Straße').strip()
    HNum = request.form.get('Hausnummer').strip()
    PLZ = request.form.get('PLZ').strip()
    Ort = request.form.get('Ort').strip()
    
    if Rolle == "Stationaer":
        RaumNummer = getRaum() # get free Room as local patient
        AdresseID = setRoomgetID(RaumNummer)
    else:
        AdresseID = setAdressegetID(Strasse, HNum, PLZ, Ort)

    sql_command = "INSERT INTO Kunde(Vorname, Nachname, TelefonNummer, Rolle, Besuche_Pro_Tag, Adresse) VALUES (?, ?, ?, ?, ?, ?);" 
    sql_liste = [Vorname, Nachname, Nummer,Rolle, Besuche, AdresseID]


    #sql_command = "INSERT INTO Kunde(Vorname, Nachname, TelefonNummer, Rolle, Besuche_Pro_Tag) VALUES(?, ?, ?, ?, ?);"
    con = get_db()
    cursor = con.cursor()
    res = cursor.execute(sql_command, sql_liste)
    print(res)
    con.commit()

    return redirect(url_for('main.patienten_liste'))


@main.route('/confirm')
@main.route('/confirm/<ID>-<mbPT>')
@login_required
def confirm(ID, mbPT):
    if current_user.Rolle != "Verwaltung":
        abort(403)

    print(ID)
    print(mbPT)
    return render_template('confirmation.html', ID=ID, mbPT=mbPT)

#Ausbaufähig aber macht seinen Job, damit man nicht blind Einträge löscht
@main.route('/confirm/<ID>-<mbPT>', methods=["POST"])
@login_required
def confirm_post(ID, mbPT):
    if current_user.Rolle != "Verwaltung":
        abort(403)

    
    print(mbPT)
    if mbPT =="Patienten":
        Tabelle = "Kunde"
        T_ID = "Kunden_ID"
    else:
        Tabelle = "Mitarbeiter"
        T_ID = "MB_ID"

    confirm = request.form.get('Valid')
    if confirm != "ENTFERNEN":
        flash("Falsches PW!")
    else:
        print(type(Tabelle))
        print(type(T_ID))
        print(type(ID))
        con = get_db()
        cursor = con.cursor()
        #cursor.execute("DELETE FROM ? WHERE ?=?;", [Tabelle, T_ID, ID])
        tempSQL = f"DELETE FROM {Tabelle} WHERE {T_ID} = {ID};"
        print(tempSQL)
        cursor.execute(tempSQL)
        con.commit()


    return redirect(url_for('main.patienten_liste'))

def existsUser(Vorname, Nachname, mbPT):
    con = get_db()
    cursor = con.cursor()

    print(Vorname)
    print(Nachname)
    print(mbPT)
    if mbPT == "Mitarbeiter":
        ID = "MB_ID"
        Tabelle = "Mitarbeiter"
        sql_command = "SELECT MB_ID FROM Mitarbeiter WHERE Vorname=? AND Nachname=?;"
    else:
        ID = "Kunden_ID"
        Tabelle = "Kunde"
        sql_command = "SELECT Kunden_ID FROM Kunde WHERE Vorname=? AND Nachname=?;"
    result = cursor.execute(sql_command, [Vorname, Nachname ]).fetchone()
    if not result:
        return False

    return True
    
#bekomme Freien Raum der noch nicht benutzt wird
def getRaum():
    raumListe = [ x for x in range(1,150)  ]
    cursor = get_db().cursor()
    result = list(cursor.execute("SELECT Wohnraum FROM Adresse;").fetchall())
    belegteRaume = []
    for i in result:
        belegteRaume.append( i[0])
    
    diffList = list(set(raumListe).difference(belegteRaume))

    if diffList:
        return diffList[0]
    else:
        return None

#returned Adresse - falls Adresse nicht existiert -> neuer Eintrag
def setAdressegetID(Strasse, HNum, PLZ, Stadt):
    con = get_db()
    cursor = con.cursor()
    adresse = [ Strasse, HNum, PLZ, Stadt ]
    sql_select = "SELECT Adresse_ID FROM Adresse WHERE Strasse=? AND Hausnummer=? AND PLZ=? AND Ort=?;"
    res = cursor.execute(sql_select, adresse).fetchone() 
    if not res:
        cursor.execute("INSERT INTO Adresse(Strasse, Hausnummer, PLZ, Ort) VALUES (?,?,?,?);",adresse)
        con.commit()
        res = list(cursor.execute(sql_select, adresse).fetchone())
        return res[0]
    else:
        res = list(res)
        return res[0]


#returned Adresse der Klinik mit gesetzter Raumnummer
def setRoomgetID(Room):
    AdresseKlinik = [ "Reinarzstraße", "49", 47805, "Krefeld" ]
    AdresseKlinik.append(Room)
    con = get_db()
    cursor = con.cursor()

    cursor.execute( "INSERT INTO Adresse(Straße, Hausnummer, PLZ, Ort, Wohnraum) VALUES (?, ?, ?, ?, ? );", AdresseKlinik )
    con.commit()
    res = list(cursor.execute("SELECT Adresse_ID FROM Adresse WHERE Wohnraum=? AND Straße='Reinarzstraße';", [Room]  ).fetchone())

    return res[0]
