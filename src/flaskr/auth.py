from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
import sqlite3
from flask_login import login_user, logout_user, current_user, login_required
from .models import Mitarbeiter


auth = Blueprint('auth', __name__)

@auth.route('/')
@auth.route('/login')
def login():
    return render_template('index.html')


@auth.route('/login', methods=['POST'])
def login_post():
    
    Nachname = request.form.get('Nachname')
    Passwort = request.form.get('Passwort')
    cursor = db.get_db().cursor() 
    cursor.execute(f"Select MB_ID, Vorname, Nachname, Rolle  FROM Mitarbeiter WHERE Nachname='{Nachname}';")
    result = cursor.fetchone()
    
    if not result:
        flash('Account existiert nicht')
        return redirect(url_for('auth.login'))

    user_ID, user_Vorname, user_Nachname, user_Rolle = list(result)
    user = Mitarbeiter(user_ID, user_Vorname, user_Nachname, user_Rolle)
    #db_user = load_user(user.Nachname) 
    
    if user.Nachname != Nachname or Passwort != "12345":
        flash("Falscher Name oder Passwort")
        return redirect(url_for('auth.login'))
    elif user.Rolle == "Verwaltung":
        login_user(user)
        return redirect(url_for('main.verwaltung'))
    else:
        login_user(user)
        return redirect(url_for('main.dienstplan'))


@auth.route('/logout')
@login_required
def logout():
    lol = logout_user()# gibt True aus wenn erfolgreich
    if lol:
        flash('Erfolgreich ausgeloggt.') 
    return redirect(url_for('auth.login'))
