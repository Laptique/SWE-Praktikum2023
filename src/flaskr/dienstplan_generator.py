from datetime import datetime, date, time, timedelta
import sqlite3
from flaskr.utils import getDateFromString, getStringFromDate, getTimeFromString, getStringFromTime
from flaskr.db import get_db

# generiert alle dienstpläne für die mitarbeiter
# ist idempotent
def generate_dienstplaene():
    print("Generating Dienstpläne")

    db = get_db()

    today = date.today()
    today_str = getStringFromDate(today) # example: 2023-05-12

    #daten der mitarbeiter aus der db importieren
    alle_mitarbeiter = db.cursor().execute("SELECT * FROM Mitarbeiter WHERE Rolle != 'Verwaltung'").fetchall()

    #daten der kunden aus der db importieren
    kunden = db.cursor().execute("SELECT * FROM Kunde").fetchall()

    # löscht alle abgesatgten besuche z.B. wenn ein mitarbeiter/kunde krankgeschrieben wurde
    deleteCanceledBesuche()

    ##Tagesplan erstellen##
    for mitarbeiter in alle_mitarbeiter:
        #print("Generating Dienstplan for " + mitarbeiter["Vorname"] + " " + mitarbeiter["Nachname"])

        mitarbeiter_id = mitarbeiter["MB_ID"]
        mitarbeiter_rolle = mitarbeiter["Rolle"]

        #besuche aus der db importieren
        besuche = db.execute("SELECT * FROM Besuche WHERE Datum = ? AND Mitarbeiter_ID = ?", [today_str, mitarbeiter_id]).fetchall()
        #krankmeldungen aus der db importieren
        krankmeldungen_mitarbeiter = db.cursor().execute("SELECT * FROM Dienstbefreiung_Mitarbeiter WHERE Mitarbeiter_ID = ?", [mitarbeiter_id]).fetchall()

        if istKrankgeschrieben(krankmeldungen_mitarbeiter, today):
            continue

        # arbeitszeit startet um 8 uhr
        hour = 8
        minute = 0
        # arbeitszeit geht bis 16 uhr
        while hour < 16:

            if mitarbeiter_rolle == "Mobil":
                # 30min fahrzeit
                hour, minute = addMinutes(hour, minute, 30)

            besuch_startzeit = time(hour, minute)
            besuch_startzeit_str = getStringFromTime(besuch_startzeit)

            # besuch dauert 30 min
            hour, minute = addMinutes(hour, minute, 30)

            # check ob ein besuch eintrag schon existiert
            besuch = findBesuchForTime(besuche, besuch_startzeit)

            # wenn besuch schon existiert, mit nächster stunde weiter machen
            if besuch != None:
                #print(besuch_startzeit_str, ": Besuch alredy exists")
                continue

            # kunden für besuch finden
            passender_kunde = findKunde(kunden, besuche, today, besuch_startzeit, mitarbeiter["Rolle"])

            if passender_kunde == None:
                # kein passender kunde gefunden, freizeit.
                #print(besuch_startzeit_str, ": No maching Kunde found")
                continue

            # neuen besuch eintrag erstellen
            besuch = (passender_kunde["Kunden_ID"], mitarbeiter_id, today_str, besuch_startzeit_str)
            #print(besuch_startzeit_str, ": Adding Besuch", besuch)

            # besuch in db inserten
            db.execute("INSERT INTO Besuche (Kunden_ID, Mitarbeiter_ID, Datum, Uhrzeit) VALUES(?, ?, ?, ?)", besuch)
            db.commit()

            # besuche aktualisieren
            besuche = db.execute("SELECT * FROM Besuche WHERE Datum = ? AND Mitarbeiter_ID = ?", [today_str, mitarbeiter_id]).fetchall()

# findet ein besuch an der angegebenen urzeit
def findBesuchForTime(besuche, uhrzeitToFind):
    for besuch in besuche:

        uhrzeit_str = besuch["Uhrzeit"]
        uhrzeit = getTimeFromString(uhrzeit_str)
        
        if uhrzeit == uhrzeitToFind:
            return besuch
        
    return None

# findet einen passenden kunden, für einen besuch
def findKunde(kunden, besuche, today, uhrzeit, rolle):
    db = get_db()
    for kunde in kunden:
        kunden_id = kunde["Kunden_ID"]
        kunde_rolle = kunde["Rolle"]
        krankmeldungen_kunde = db.cursor().execute("SELECT * FROM Krankschreibung_Kunde WHERE Kunden_ID = ?", [kunden_id]).fetchall()

        # checken wieviele besuche der kunde heute schon hat
        if not checkBesucheProTag(today, kunden_id, kunde["Besuche_Pro_Tag"]):
            #print("Kunde ", kunden_id, " no match, appointments per day already satisfied")
            continue

        # checken ob der letzte besuch mindestens 2 stunden her ist (damit man nicht den selben kunden 2 mal hintereinander besucht)
        if not checkBesuch2HoursDistance(besuche, kunden_id, uhrzeit):
            #print("Kunde ", kunden_id, " no match, last appointment was withing 2 hours")
            continue

        # checken ob kunde auch nicht krankgeschrieben ist
        if istKrankgeschrieben(krankmeldungen_kunde, today):
            #print("Kunde ", kunden_id, " no match, is ill")
            continue

        # checken ob kunde die richtige pflegekategorie(ambulant/stationär) hat
        if not checkKundeHasCorrectRole(kunde["Rolle"], rolle):
            #print("Kunde ", kunden_id, " no match, has invalid role ", kunde_rolle, ", employee is " + rolle)
            continue

        # passender kunde gefunden
        return kunde
    # kein passender kunde gefunden
    return None

# checken wieviele besuche der kunde heute schon hatte
def checkBesucheProTag(today, kunden_id, kunden_besuche_pro_tag):
    db = get_db()
    today_str = getStringFromDate(today)
    kunden_besuche_count = db.execute("SELECT COUNT(*) FROM Besuche WHERE Datum = ? AND Kunden_ID = ?", [today_str, kunden_id]).fetchone()[0]
    # wenn kunde schon alle besuche pro tag hat return False
    return kunden_besuche_count < kunden_besuche_pro_tag

def checkBesuch2HoursDistance(besuche, kunden_id: str, uhrzeit: time):
    for besuch in besuche:
        
        if besuch["Kunden_ID"] != kunden_id:
            continue

        letzter_besuch_uhrzeit_str = besuch["Uhrzeit"]
        letzter_besuch_uhrzeit = getTimeFromString(letzter_besuch_uhrzeit_str)

        min_uhrzeit = time(letzter_besuch_uhrzeit.hour + 2, letzter_besuch_uhrzeit.minute)
        
        if uhrzeit < min_uhrzeit:
            return False
    return True

def checkKundeHasCorrectRole(kunde_rolle, mitarbeiter_rolle):
    if mitarbeiter_rolle == "Stationaer":
        return kunde_rolle == "Stationaer"
    elif mitarbeiter_rolle == "Mobil":
        return kunde_rolle == "Ambulant"
    return False

def istKrankgeschrieben(krankschreibungen, today: date):
    for krankschreibung in krankschreibungen:

        start_date = getDateFromString(krankschreibung["Start_Datum"])
        end_date = getDateFromString(krankschreibung["ENDE_Datum"])

        if today >= start_date and today <= end_date:
            return True

    return False

# löscht alle abgesatgten besuche z.B. wenn ein mitarbeiter/kunde krankgeschrieben wurde
def deleteCanceledBesuche():
    print("Deleting canceled Besuche")
    db = get_db()
    today = date.today()

    krankmeldungen_mitarbeiter = db.cursor().execute("SELECT * FROM Dienstbefreiung_Mitarbeiter").fetchall()

    for krankschreibung in krankmeldungen_mitarbeiter:

        mitarbeiter_id = krankschreibung["Mitarbeiter_ID"]
        start_date = getDateFromString(krankschreibung["Start_Datum"])
        end_date = getDateFromString(krankschreibung["ENDE_Datum"])

        if today < start_date or today > end_date:
            continue

        #print("Found Mitarbeiter Krankmeldung ", krankschreibung["Start_Datum"], " ", krankschreibung["ENDE_Datum"])

        deleteBesuche(mitarbeiter_id, None, start_date, end_date)

    krankmeldungen_kunden = db.cursor().execute("SELECT * FROM Krankschreibung_Kunde").fetchall()

    for krankschreibung in krankmeldungen_kunden:

        kunden_id = krankschreibung["Kunden_ID"]
        start_date = getDateFromString(krankschreibung["Start_Datum"])
        end_date = getDateFromString(krankschreibung["ENDE_Datum"])

        if today < start_date or today > end_date:
            continue

        deleteBesuche(None, kunden_id, start_date, end_date)




# löscht besuche von einem mitarbeiter in einem bestimmten zeitraum
def deleteBesuche(mitarbeiter_id, kunden_id, start_date: date, end_date: date):
    db = get_db()

    today = date.today()
    current_date = start_date 

    while current_date <= end_date:
        # überspringen wenn datum in der vergangenheit liegt
        if current_date < today:
            continue

        current_date_str = getStringFromDate(current_date)

        #print("delete besuche ", current_date_str)

        if mitarbeiter_id != None:
            db.execute("DELETE FROM Besuche WHERE Mitarbeiter_ID = ? AND Datum = ?", [mitarbeiter_id, current_date_str])
        elif kunden_id != None:
            db.execute("DELETE FROM Besuche WHERE Kunden_ID = ? AND Datum = ?", [kunden_id, current_date_str])

        db.commit()

        current_date += timedelta(days=1)

def addMinutes(hour, minute, amount):
    # gibt keine andere möglichkeit weil python scheiße ist
    minute = minute + amount
    hour = hour + int(minute / 60)
    minute = minute % 60
    return hour, minute
        