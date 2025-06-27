from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
from commands.init_db import init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

# Creating a database connection and creating a table.
mysql = init_db(app)

# Check if the user is logged in.
def is_logged_in():
    def _is_logged_id(f):
        @wraps(f)
        def __is_logged_in(*args, **kwargs):
            if 'user' in session:
                return f(*args, **kwargs)
            else:
                flash('Unauthorized, Please login', 'danger')
                return redirect(url_for('auth'))
        return __is_logged_in
    return _is_logged_id

# Routes
@app.route('/dashboard')
@is_logged_in()
def dashboard():
    return render_template('index.html') 

@app.route('/')
def index():
    return render_template('auth/login.html')

@app.route('/auth')
def auth():
    return render_template('auth/login.html')
    

    
# Import controllers
from controllers.user import *
from controllers.dataset import *
from controllers.apriory import *

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
