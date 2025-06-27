from app import app, mysql, is_logged_in
from flask import render_template, request, redirect, url_for, session, flash, abort
from models.users import User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login_form'))
            if session['user']['role'] != role:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/users')
@is_logged_in()
@role_required('admin')
def index_user():
    # list users        
    users = User.get_all(mysql)

    # return users with index.html
    return render_template('users/index.html', users=users)    

@app.route('/users/create')
@is_logged_in()
@role_required('admin')
def create_user():
    # return create.html
    return render_template('users/create.html')

@app.route('/users/store', methods=['POST'])
@is_logged_in()
@role_required('admin')
def store_user():
    # get data from form
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    # insert data to database
    User.store(mysql, name, email, generate_password_hash(password, method='pbkdf2:sha256'), role)

    # redirect to users
    return redirect(url_for('index_user'))

@app.route('/users/<int:id>')
@is_logged_in()
@role_required('admin')
def show_user(id):
    # show user
    user = User.get_by_id(mysql, id)

    # return user with show.html
    return render_template('users/edit.html', user=user)

@app.route('/users/<int:id>/edit')
@is_logged_in()
@role_required('admin')
def edit_user(id):
    # edit user
    user = User.get_by_id(mysql, id)

    # return user with edit.html
    return render_template('users/edit.html', user=user)

@app.route('/users/<int:id>/update', methods=['POST'])
@is_logged_in()
@role_required('admin')
def update_user(id):
    # get data from form
    name = request.form['name']
    email = request.form['email']
    role = request.form['role']

    # update user
    User.update(mysql, id, name, email, role)

    # return user with show.html
    return redirect(url_for('show_user', id=id))

@app.route('/users/<int:id>/delete')
@is_logged_in()
@role_required('admin')
def delete_user(id):
    # delete user
    User.delete(mysql, id)

    # return users with index.html
    return redirect(url_for('index_user'))

@app.route('/auth/login', methods=['GET'])
def login_form():
    # render login page
    return render_template('auth/login.html')

@app.route('/auth/login', methods=['POST'])
def login():
    # get data from form
    username = request.form['username']
    password = request.form['password']

    # check if user exists
    user = User.get_by_username(mysql, username)

    # if user exists
    if user:
        # check if password is correct        
        if check_password_hash(user['password'], password):
            # set the session
            session['user'] = user
            # redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('index_user'))
            else:
                return redirect(url_for('dashboard'))
        else:
            # return login with error
            return render_template('auth/login.html', error='Incorrect password')
    else:
        # return login with error
        return render_template('auth/login.html', error='User not found')

@app.route('/auth/logout', methods=['GET', 'POST'])
def logout():
    # logout user
    session.clear()
    return redirect(url_for('login_form'))

@app.route('/auth/register', methods=['GET'])
def register_form():
    # return register.html
    return render_template('auth/register.html')

@app.route('/auth/register', methods=['POST'])
def register():
    # Registration is disabled
    flash('Registration is currently disabled', 'info')
    return redirect(url_for('auth'))

@app.route('/create_admin')
def create_admin():
    # Create admin user for testing
    try:
        User.store(mysql, 'admin', 'admin@admin.com', generate_password_hash('admin123', method='pbkdf2:sha256'), 'admin')
        return "Admin user created successfully"
    except Exception as e:
        return f"Error creating admin user: {str(e)}"

    