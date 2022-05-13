from distutils.log import error
import email
from email import message
from pickle import TRUE
from click import edit
from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user

from website.departments import department
from .models import AnnualHoliday, Department, Holiday, User
from . import db
import json
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from typing import Final

HOLIDAY_REQUESTED: Final = 0
HOLIDAY_ACCEPTED: Final = 1
HOLIDAY_DECLINED: Final = 2

acceptance = Blueprint('acceptance', __name__)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


@acceptance.route('/accept', methods=['GET'])
@login_required
def accept():
    if current_user.is_boss == 1:
        return render_template("accept.html", user=current_user)
    else:
        flash('Nincs hozzá jogosultságod!', category='error')
        return redirect("/")


@acceptance.route('/acceptcheck', methods=['GET', 'POST'])
@login_required
def acceptcheck():
    result = True
    message = ''

    holiday = json.loads(request.data)
    holidayID = holiday['holidayID']

    holiday = Holiday.query.get(holidayID)

    print ('holiday',holiday)

    checkHoliday = AnnualHoliday.query.filter_by(user_id = holiday.user_id, year = holiday.start_date.year).first()
    if checkHoliday is not None:
        holidaySum = Holiday.query.with_entities(
             func.sum(Holiday.work_days).label("sum_work_days")
         ).filter(  Holiday.status==HOLIDAY_ACCEPTED,
                    Holiday.user_id==holiday.user_id, 
                    Holiday.start_date >= datetime(holiday.start_date.year,1,1,0,0,0), 
                    Holiday.end_date <= datetime(holiday.start_date.year,12,31,23,59,59) ).first()
        if holidaySum.sum_work_days is not None:
            if checkHoliday.days_off < holidaySum.sum_work_days + holiday.work_days:
                result = False
                message = 'A dolgozónak már nem maradt ennyi szabadnapja.'
    else:
        result = False
        message = 'A dolgozónak még nincs rögzítve az éves szadagsága.'

    print ('checkHoliday',checkHoliday)
    print ('holidaySum', holidaySum)

    checkUser = User.query.get(holiday.user_id)
    checkDepartment = Department.query.get(checkUser.department_id)
    min_employees = checkDepartment.min_employees
    employeeCount = User.query.with_entities(
            func.count().label("count_emp")
         ).filter(  User.is_active==1,
                    User.department_id==checkUser.department_id ).first()
    count_emp = employeeCount.count_emp

    checkDate = True
    for single_date in daterange(holiday.start_date, holiday.end_date + timedelta(days=1)):
        print(single_date.strftime("%Y-%m-%d"))
        dayCount = Holiday.query.join('user').with_entities(
            func.count().label("count_day")
         ).filter(User.department_id==checkUser.department_id).filter(  Holiday.status==HOLIDAY_ACCEPTED,
                    Holiday.start_date <= single_date, 
                    Holiday.end_date >= single_date).first()
        
        print(dayCount.count_day)
        if ((count_emp - dayCount.count_day) <= min_employees ):
            checkDate = False
            message = message + single_date.strftime("%Y-%m-%d") + ', '
    if not checkDate:
        result = True
        message = 'A létszám minimum alá csökken az alábbi napokon: ' + message[:-2]

    print(message)

    return json.dumps({'success':result,'message':message})




@acceptance.route('/acceptlist', methods=['GET'])
@login_required
def acceptlist():
    result = []
    holidays = Holiday.query.all()
    for holiday in holidays:
        result.append({
				'start': str(holiday.start_date),
				'end': str(holiday.end_date),
				'name': holiday.user.first_name,
				'id': str(holiday.id),
                'user_id': holiday.user_id,
                'workdays': holiday.work_days,
                'custom_class': 'bar-status_' + str(holiday.status) 
                })
    return json.dumps(result)



@acceptance.route('/acceptstatus', methods=['POST'])
@login_required
def acceptstatus():
    result = True
    message = ''


    holiday = json.loads(request.data)
    holidayID = holiday['holidayID']
    status = holiday['status']

    try:
        holidayID = int(holidayID)
    except Exception as e:
        result = False
        message = 'Hibás ID ( ' + str(e) + ' )'

    try:
        status = int(status)
    except Exception as e:
        result = False
        message = 'Hibás státusz ( ' + str(e) + ' )'
    
    if result:
        holiday = Holiday.query.get(holidayID)
        holiday.status = status
        db.session.commit()

    return json.dumps({'success':result,'message':message})


















