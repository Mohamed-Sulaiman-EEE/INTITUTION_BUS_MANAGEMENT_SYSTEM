from fileinput import filename
from importlib.metadata import metadata
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        
        if user:
            type = user.type
            if type != "S":
                flash("You dont belong here")
                return render_template("student_login.html", user = current_user)

            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.student_home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    
    return render_template("student_login.html", user = current_user)


@auth.route('/conductor-login', methods=['GET', 'POST'])
def conductor_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        type = user.type
        if type != "C":
            flash("You dont belong here")
            return render_template("conductor_login.html", user = current_user)
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.conductor_home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("conductor_login.html", user = current_user)


    
@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        type = user.type
        if type != "A":
            flash("You dont belong here ")
            return render_template("admin_login.html", user = current_user)
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.admin_home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    
    return render_template("admin_login.html", user = current_user)


def generate_account_details(current_user):
    l = 5-len(str(current_user.id))
    prefix = "0"*l + str(current_user.id)
    no = "TCE" + prefix
    current_user.rfid_number = no
    db.session.commit()
    


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.index'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 2:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, name= name ,phone_number= phone_number ,  password=generate_password_hash(
                password1, method='sha256') , type = "S")
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            generate_account_details(current_user)
            flash('Account created!', category='success')
            return redirect(url_for('views.student_home'))

    return render_template("sign_up.html", user=current_user)


