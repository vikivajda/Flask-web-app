from distutils.log import error
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

views = Blueprint('views', __name__)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/holidayadd', methods=['GET', 'POST'])
@login_required
def holidayadd():
    result = True
    message = ''
    try:
        startDate = request.form.get('startDate')
        startDate = datetime.fromisoformat(startDate)
    except Exception as e:
        result = False
        message = 'Hibás kezdő dátum. ( ' + str(e) + ' )'

    try:
        endDate = request.form.get('endDate')
        endDate = datetime.fromisoformat(endDate)
    except Exception as e:
        result = False
        message = 'Hibás záró dátum. ( ' + str(e) + ' )'

    if endDate < startDate:
        result = False
        message = 'Hibás időszak. A záródátum korábbi mint a kezdődátum.'

    if endDate.year != startDate.year:
        result = False
        message = 'Hibás időszak. A záródátum éve nem egyezik meg a  kezdődátum évével.'

    try:
        workDays = request.form.get('workDays')
        workDays = int(workDays)
    except Exception as e:
        result = False
        message = 'Hibás a napok száma. ( ' + str(e) + ' )'


    if result and ((workDays < 1) or (1 + (endDate - startDate).days < workDays)):
        result = False
        message = 'Hibás a napok száma. 1 és a naptári napok száma között lehet.'
    
    checkHoliday = AnnualHoliday.query.filter_by(user_id = current_user.id, year = startDate.year).first()
    if checkHoliday is not None:
        holidaySum = Holiday.query.with_entities(
             func.sum(Holiday.work_days).label("sum_work_days")
         ).filter(  Holiday.status==HOLIDAY_ACCEPTED,
                    Holiday.user_id==current_user.id, 
                    Holiday.start_date >= datetime(startDate.year,1,1,0,0,0), 
                    Holiday.end_date <= datetime(startDate.year,12,31,23,59,59) ).first()
        if holidaySum.sum_work_days is not None:
            if checkHoliday.days_off < holidaySum.sum_work_days + workDays:
                result = False
                message = 'A dolgozónak már nem maradt ennyi szabadnapja.'
    else:
        result = False
        message = 'A dolgozónak még nincs rögzítve az éves szadagsága.'

    checkDepartment = Department.query.filter_by(id = current_user.department_id).first()
    min_employees = checkDepartment.min_employees
    employeeCount = User.query.with_entities(
            func.count().label("count_emp")
         ).filter(  User.is_active==1,
                    User.department_id==current_user.department_id ).first()
    count_emp = employeeCount.count_emp

    checkDate = True
    for single_date in daterange(startDate, endDate + timedelta(days=1)):
        dayCount = Holiday.query.join('user').with_entities(
            func.count().label("count_day")
         ).filter(User.department_id==current_user.department_id).filter(  Holiday.status==HOLIDAY_ACCEPTED,
                    Holiday.start_date <= single_date, 
                    Holiday.end_date >= single_date).first()
        
        if ((count_emp - dayCount.count_day) <= min_employees ):
            checkDate = False
            message = message + single_date.strftime("%Y-%m-%d") + ', '
    if not checkDate:
        result = True
        message = 'A létszám minimum alá csökken az alábbi napokon: ' + message[:-2]


    checkDate = True
    for single_date in daterange(startDate, endDate + timedelta(days=1)):
        dayCount = Holiday.query.join('user').with_entities(
            func.count().label("count_day")
         ).filter(User.id==current_user.id).filter(
                    Holiday.start_date <= single_date, 
                    Holiday.end_date >= single_date).first()
        
        if (dayCount.count_day > 0 ):
            checkDate = False
            message = message + single_date.strftime("%Y-%m-%d") + ', '
    if not checkDate:
        result = False
        message = 'Már van szabadság igény az alábbi napokon: ' + message[:-2]

    if result:
        holiday = Holiday( user_id=current_user.id, start_date = startDate, end_date=endDate, work_days = workDays, status=HOLIDAY_REQUESTED)
        db.session.add(holiday)
        db.session.commit()
        #msg = Message(
         #       'Hello',
          #      sender = '',
           #     recipients = ['victory.vajda@gmail.com']
            #   )
    #msg.body = 'Flask mail'
    #mail.send(msg)
    return json.dumps({'success':result,'message':message})




@views.route('/holidaylist', methods=['GET'])
@login_required
def holidaylist():
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
                'readonly': (holiday.user_id != current_user.id),
                'custom_class': 'bar-status_' + str(holiday.status)
                })
    return json.dumps(result)



@views.route('/holidayedit', methods=['POST'])
@login_required
def holidayedit():
    result = True
    message = ''

    try:
        holidayID = request.form.get('holidayID')
        holidayID = int(holidayID)
    except Exception as e:
        result = False
        message = 'Hibás ID ( ' + str(e) + ' )'

    try:
        startDate = request.form.get('startDate')
        startDate = datetime.fromisoformat(startDate)
    except Exception as e:
        result = False
        message = 'Hibás kezdő dátum. ( ' + str(e) + ' )'

    try:
        endDate = request.form.get('endDate')
        endDate = datetime.fromisoformat(endDate)
    except Exception as e:
        result = False
        message = 'Hibás záró dátum. ( ' + str(e) + ' )'

    if endDate < startDate:
        result = False
        message = 'Hibás időszak. A záródátum korábbi mint a kezdődátum.'

    if endDate.year != startDate.year:
        result = False
        message = 'Hibás időszak. A záródátum éve nem egyezik meg a  kezdődátum évével.'

    try:
        workDays = request.form.get('workDays')
        workDays = int(workDays)
    except Exception as e:
        result = False
        message = 'Hibás a napok száma. ( ' + str(e) + ' )'


    if result and ((workDays < 1) or (1 + (endDate - startDate).days < workDays)):
        result = False
        message = 'Hibás a napok száma. 1 és a naptári napok száma között lehet.'
    
    checkHoliday = AnnualHoliday.query.filter_by(user_id = current_user.id, year = startDate.year).first()
    if checkHoliday is not None:
        holidaySum = Holiday.query.with_entities(
             func.sum(Holiday.work_days).label("sum_work_days")
         ).filter(  Holiday.status==HOLIDAY_ACCEPTED,
                    Holiday.id!=holidayID, 
                    Holiday.user_id==current_user.id, 
                    Holiday.start_date >= datetime(startDate.year,1,1,0,0,0), 
                    Holiday.end_date <= datetime(startDate.year,12,31,23,59,59) ).first()
        if holidaySum.sum_work_days is not None:
            if checkHoliday.days_off < holidaySum.sum_work_days + workDays:
                result = False
                message = 'A dolgozónak már nem maradt ennyi szabadnapja.'
    else:
        result = False
        message = 'A dolgozónak még nincs rögzítve az éves szadagsága.'

    checkDepartment = Department.query.filter_by(id = current_user.department_id).first()
    min_employees = checkDepartment.min_employees
    employeeCount = User.query.with_entities(
            func.count().label("count_emp")
         ).filter(  User.is_active==1,
                    User.department_id==current_user.department_id ).first()
    count_emp = employeeCount.count_emp

    checkDate = True
    for single_date in daterange(startDate, endDate + timedelta(days=1)):
        dayCount = Holiday.query.join('user').with_entities(
            func.count().label("count_day")
         ).filter(User.department_id==current_user.department_id).filter(  Holiday.status==HOLIDAY_ACCEPTED,
                    Holiday.id!=holidayID, 
                    Holiday.start_date <= single_date, 
                    Holiday.end_date >= single_date).first()
        
        if ((count_emp - dayCount.count_day) <= min_employees ):
            checkDate = False
            message = message + single_date.strftime("%Y-%m-%d") + ', '
    if not checkDate:
        result = False
        message = 'A létszám minimum alá csökken az alábbi napokon: ' + message[:-2]


    checkDate = True
    for single_date in daterange(startDate, endDate + timedelta(days=1)):
        dayCount = Holiday.query.join('user').with_entities(
            func.count().label("count_day")
         ).filter(User.id==current_user.id).filter(
                    Holiday.id!=holidayID, 
                    Holiday.start_date <= single_date, 
                    Holiday.end_date >= single_date).first()
        
        if (dayCount.count_day > 0 ):
            checkDate = False
            message = message + single_date.strftime("%Y-%m-%d") + ', '
    if not checkDate:
        result = False
        message = 'Már van szabadság igény az alábbi napokon: ' + message[:-2]


    if result:
        holiday = Holiday.query.get(holidayID)
        holiday.start_date = startDate
        holiday.end_date = endDate
        holiday.work_days = workDays
        db.session.commit()

    return json.dumps({'success':result,'message':message})




@views.route('/delete-holiday', methods=['POST'])
def delete_holiday():
    holiday = json.loads(request.data)
    holidayId = holiday['holidayID']
    holiday = Holiday.query.get(holidayId)
    if holiday:
        db.session.delete(holiday)
        db.session.commit()
    return jsonify({})

