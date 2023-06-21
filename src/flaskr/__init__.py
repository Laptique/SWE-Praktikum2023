import os
from . import db
from flask import Flask
from flask_login import LoginManager
import sqlite3
from .models import Mitarbeiter

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='2922_ara_420%ara',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # ensure the instance folder for the database exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    #init login_manager
    login_manager.init_app(app)
    
    #init db 
    from . import db
    db.init_app(app)

    # create dienstpläne
    #from flaskr import dienstplan_generator
    #with app.app_context():
    #    dienstplan_generator.generate_dienstplaene()

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for error parts of app
    from .errors import not_found, forbidden
    app.register_error_handler(404, not_found)
    app.register_error_handler(403, forbidden)


    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        #return User.query.get(int(user_id))
        #conn = sqlite3.connect('../instance/flaskr.sqlite')
        conn = db.get_db()
        curs = conn.cursor()
        curs.execute(f"SELECT MB_ID, Vorname, Nachname, Rolle FROM Mitarbeiter WHERE MB_ID='{user_id}';")
        result = curs.fetchone()
        if result is None:
            return None
        else:
            return Mitarbeiter(int(result["MB_ID"]), result["Vorname"], result["Nachname"], result["Rolle"])


    return app
