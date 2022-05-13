from distutils.log import error
import email
from pickle import TRUE
from click import edit
from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .models import Department, AnnualHoliday, User
from . import db
import json
import datetime


annualholidays = Blueprint('annualholidays', __name__)

@annualholidays.route('/annualholiday/add', methods=['GET', 'POST'])
@login_required
def annualHolidayAdd():
    if request.method == 'POST':
        userid = request.form.get('userid')
        year = request.form.get('year')
        days_off = request.form.get('days_off')
        try:
            year = int(year)
            currentDateTime = datetime.datetime.now()
            date = currentDateTime.date()
            currentyear = int(date.strftime("%Y"))
            if (year >= currentyear) and (year <= (currentyear + 1)):
                try:
                    days_off = int(days_off)
                    if (days_off > 0) and (days_off < 366):
                        checkHoliday = AnnualHoliday.query.filter_by(user_id = userid, year=year).first()
                        if checkHoliday is None:
                            annualholiday = AnnualHoliday(user_id=userid, year = year, days_off = days_off)
                            db.session.add(annualholiday)
                            db.session.commit()
                            flash('Éves szabadság rögzítve', category='success')
                            return redirect("/annualholiday")
                        else:
                            flash('Már van erre az évre a dolgozónak szabadság rögzítve', category='error')
                    else:
                       flash('Napok száma 1 és 365 között lehet', category='error')
                except:
                    flash('Érvénytelen szabadnap szám', category='error')
            else:
                flash('Az évszám idei, vagy jövő évi lehet', category='error')
        except:
            flash('Érvénytelen évszám', category='error')
    users = User.query.all()
    return render_template("annualholiday_add.html", user=current_user, users=users)


@annualholidays.route('/annualholiday', methods=['GET', 'POST'])
@login_required
def annualHoliday():
    if current_user.is_boss == 1:
        annualHoliday = AnnualHoliday.query.all()
        return render_template("annualholiday.html", user=current_user, holidays=annualHoliday )
    else:
        flash('Nincs hozzá jogosultságod!', category='error')
        return redirect("/")


@annualholidays.route('/annualholiday/edit/<int:annualholiday_id>', methods=['GET', 'POST'])
@login_required
def annualHolidayEdit(annualholiday_id):
    if request.method == 'POST':
        days_off = request.form.get('days_off')
        try:
            days_off = int(days_off)
            if (days_off > 0) and (days_off < 366):
                annualHoliday = AnnualHoliday.query.get(annualholiday_id)
                if annualHoliday is not None:
                    annualHoliday.days_off = days_off
                    db.session.commit()
                    flash('Éves szabadság rögzítve', category='success')
                    return redirect("/annualholiday")
                else:
                    flash('Nem sikerült megtalálni a módosítandó éves szabadságot', category='error')
            else:
               flash('Napok száma 1 és 365 között lehet', category='error')
        except:
            flash('Érvénytelen szabadnap szám', category='error')
    else:
        if request.method == 'GET':
            annualHoliday = AnnualHoliday.query.get(annualholiday_id)
            if annualHoliday:
                return render_template("annualholiday_edit.html", user=current_user, holiday=annualHoliday)
            else:
                flash('Invalid annualHolidayID for edit', category='error')
    return render_template("annualholiday_edit.html", user=current_user)


@annualholidays.route('/delete-annualholiday', methods=['POST'])
def delete_annualholiday():
    holiday = json.loads(request.data)
    holidayId = holiday['annualHolidayId']
    holiday = AnnualHoliday.query.get(holidayId)
    if holiday:
        db.session.delete(holiday)
        db.session.commit()

    return jsonify({})
