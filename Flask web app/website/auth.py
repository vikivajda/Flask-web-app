from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.is_active == 1:
                if check_password_hash(user.password, password):
                    flash('Sikeres bejelentkezés!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Helytelen jelszó.', category='error')
            else:
                flash('Inaktív felhasználó.', category='error')
        else:
            flash('Helytelen email.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Már van fiókja.', category='error')
        elif len(email) < 4:
            flash('Email legyen hosszabb 3 karakternél!', category='error')
        elif len(first_name) < 2:
            flash('Név legyen hosszabb 1 karakternél!', category='error')
        elif password1 != password2:
            flash('A jelszó nem egyezik.', category='error')
        elif len(password1) < 7:
            flash('A jelszó legyen legalább 7 karakteres!.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
            password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)