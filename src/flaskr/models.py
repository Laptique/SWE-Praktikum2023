from flask_login import UserMixin, login_user
import sqlite3
from . import db#, login_manager
class Mitarbeiter(UserMixin):
    def __init__(self, ID, Vorname, Nachname, Rolle):
        self.ID = ID
        self.Vorname = Vorname
        self.Nachname = Nachname
        self.authenticated = False
        self.Rolle = Rolle

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.is_active()

    def get_id(self):
        #cursor = db.get_db().cursor
        return self.ID

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
'''
@login_manager.user_loader
def load_user(user_id):
    conn = db.get_db()
    curs = conn.cursor()
    curs.execute(f"SELECT MB_ID, Vorname, Nachname FROM Mitarbeiter WHERE MB_ID='{user_id}';")
    result = curs.fetchone()
    if result is None:
        return None
    else:
        return Mitarbeiter(int(result[0]), result[1], result[2])
        '''
