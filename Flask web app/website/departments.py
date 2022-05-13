from distutils.log import error
from pickle import TRUE
from click import edit
from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .models import Department, User
from . import db
import json
import datetime


departments = Blueprint('departments', __name__)



@departments.route('/department/add', methods=['GET', 'POST'])
@login_required
def departmentAdd():
     if request.method == 'POST':
        department = request.form.get('department')
        employee = request.form.get('min_employees')
        try:
            employee = int(employee)
            if (employee > 0) and (employee < 100):
                if len(department) < 1:
                    flash('A terület név túl rövid!', category='error')
                else:
                    new_department = Department(data=department, min_employees=employee)
                    db.session.add(new_department)
                    db.session.commit()
                    flash('Új terület hozzáadva!', category='success')
                    return redirect("/department")
            else:
                flash('A dolgozók száma 0 és 100 között legyen!', category='error')
        except:
            flash('A dolgozók száma 0 és 100 között legyen!', category='error')
     return render_template("department_add.html", user=current_user)


@departments.route('/department', methods=['GET', 'POST'])
@login_required
def department():
    if current_user.is_boss == 1:
        department = Department.query.all()
        return render_template("department.html", user=current_user, departments=department )
    else:
        flash('Nincs hozzá jogosultságod!', category='error')
        return redirect("/")


@departments.route('/department/edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
def departmentEdit(department_id):
     
    if request.method == 'POST':
        department = request.form.get('department')
        employee = request.form.get('min_employees')
        id = request.form.get('departmentID')
        try:
            employee = int(employee)
            id = int(id)
            if (employee > 0) and (employee < 100):
                if len(department) < 1:
                    flash('A terület név túl rövid!!', category='error')
                else:
                    edit_department = Department.query.filter_by(id=id).first()
                    edit_department.data = department
                    edit_department.min_employees = employee
                    db.session.commit()

                    flash('A terület módosítása sikerült!', category='success')
                    return redirect("/department")
            else:
                flash('A megadott szám nem elfogadható', category='error')
        except:
            flash('A megadott szám nem elfogadható', category='error')
    else:
        if request.method == 'GET':
            department = Department.query.get(department_id)
            if department:
                return render_template("department_edit.html", user=current_user, department=department)
            else:
                flash('Invalid department ID for edit', category='error')
                return render_template("department_edit.html", user=current_user)


@departments.route('/delete-department', methods=['POST'])
def delete_department():
    department = json.loads(request.data)
    departmentId = department['departmentId']
    department = Department.query.get(departmentId)
    if department:
        db.session.delete(department)
        db.session.commit()
    return jsonify({})



