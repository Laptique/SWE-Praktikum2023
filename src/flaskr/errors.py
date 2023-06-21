from flask import render_template

def not_found(error):
    return render_template('errors/404.html'), 404

def forbidden(error):
    return render_template('errors/403.html'), 403