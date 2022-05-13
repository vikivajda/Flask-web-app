from distutils.log import error
from pickle import TRUE
from click import edit
from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .models import Department, User
from . import db
from werkzeug.security import generate_password_hash


users = Blueprint('users', __name__)


@users.route('/usermanagement', methods=['GET', 'POST'])
@login_required
def usermanagement():
    if current_user.is_boss == 1:
        users = User.query.all()
        admin_is_it = False
    else:
        flash('Nincs hozzá jogosultságod!', category='error')
        return redirect("/")

    for user in users:
        admin_is_it = user.is_boss == 1
        if admin_is_it:
            break
    if not admin_is_it:
        new_user = User(email='admin@ceg.hu', first_name='admin', password=generate_password_hash('admin', method='sha256'),is_boss=1)
        db.session.add(new_user)
        db.session.commit()
        users = User.query.all()

    return render_template("usermanagement.html", user=current_user, users=users)
    

@users.route('/usermanagement/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def usermanagementEdit(user_id):
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        is_boss = request.form.get('is_boss')
        is_active = request.form.get('is_active')
        email = request.form.get('email')
        department = request.form.get('departmentid')
        #print(first_name, is_boss, email, department, is_active)
        try:
            is_boss = int(is_boss)
            if (len(first_name) > 0):
                if (len(email) > 2):
                    usr = User.query.get(user_id)
                    if usr is not None:
                        usr.first_name = first_name
                        usr.is_boss = is_boss
                        usr.is_active = is_active
                        usr.email = email
                        if department is not None:
                            department = int(department)
                            usr.department_id = department
                        db.session.commit()
                        flash('Sikeres módosítás', category='success') 
                        return redirect("/usermanagement")
                    else:
                        flash('Nem sikerült megtalálni a felhaszálót', category='error')
                else:
                    flash('Túl rövid email cím', category='error') 
            else:
                flash('Túl rövid név', category='error') 
        except  Exception as e:
            flash('Nem sikerült a módosítás. Oka: ' + str(e), category='error') 
            
    userm = User.query.get(user_id)
    if not userm:
        flash('Invalid UserID for edit', category='error')
        return redirect("/usermanagement")
    else:
        departments = Department.query.all()
        return render_template("usermanagement_edit.html", user=current_user, userm=userm, departments=departments)

