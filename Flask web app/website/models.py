from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    is_boss = db.Column(db.Integer,nullable=False, default=0)
    is_active = db.Column(db.Integer,nullable=False, default=1)

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    departments = db.relationship('Department')
    annualholidays = db.relationship('AnnualHoliday', back_populates="user")
    holidays = db.relationship('Holiday', back_populates="user")

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    min_employees = db.Column(db.Integer)

class AnnualHoliday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    days_off = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', back_populates="annualholidays") #, backref=db.backref('users', lazy=True)

class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime(timezone=True))
    end_date = db.Column(db.DateTime(timezone=True))
    work_days = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Integer)
    user = db.relationship('User', back_populates="holidays")
