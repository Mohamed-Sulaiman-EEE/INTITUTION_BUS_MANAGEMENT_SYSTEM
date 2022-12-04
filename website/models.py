from multiprocessing.sharedctypes import Value
from tkinter.tix import INTEGER

#from website.views import conductor_home
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(25))
    phone_number = db.Column(db.String(15))
    type = db.Column(db.String(1))
    rfid_number = db.Column(db.String(10))

class Student(db.Model , UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(1))
    parents_phone = db.Column(db.String(15))

class Conductor(db.Model , UserMixin):
    id = db.Column(db.Integer, primary_key=True)



class Route(db.Model):
    id = db.Column(db.String(1), primary_key=True)
    start = db.Column(db.String(10))
    end = db.Column(db.String(10))
    phases = db.Column(db.String(250))

class Gps_data(db.Model):
    bus_no = db.Column(db.String(1), primary_key=True)
    lat = id = db.Column(db.String(20), primary_key=True)
    long = id = db.Column(db.String(20), primary_key=True)
    gps = lat = id = db.Column(db.String(20), primary_key=True)


class Bus_details(db.Model):
    bus_no = db.Column(db.String(1), primary_key=True)
    plate_number = db.Column(db.String(10))


class Location_reference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    lat = id = db.Column(db.String(20), primary_key=True)
    long = id = db.Column(db.String(20), primary_key=True)
    gps = lat = id = db.Column(db.String(20), primary_key=True)




#............................NEW .....................................


'''

class Conductor_details(db.Model, UserMixin):
    conductor_id = db.Column(db.Integer , primary_key = True)
    bus_no = db.Column(db.String(10))
    current_trip_id = db.Column(db.Integer)
    routes_assigned = db.Column(db.String(100))


class Route(db.Model):
    route_id = db.Column(db.Text , primary_key = True)
    start =db.Column(db.String(100))
    end =db.Column(db.String(100))
    stops = db.Column(db.String(100))


    
class Site_settings(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    scratch_card_run = db.Column(db.Integer)
    auth = db.Column(db.String)

class Helpdesk_recharge(db.Model,UserMixin):
    id = db.Column(db.Integer , primary_key = True)
    value = db.Column(db.Integer)
    date = db.Column(db.String(100))
    account_number = db.Column(db.String(10) , db.ForeignKey('user.account_number'))


class Trip(db.Model,UserMixin):
    trip_id = db.Column(db.Integer , primary_key = True)
    route_id = db.Column(db.String(100))
    conductor_id = db.Column(db.Integer , db.ForeignKey('user.id'))
    date = db.Column(db.String(100))
    collection = db.Column(db.Integer)
    ticket_run = db.Column(db.Integer)
    start_time =db.Column(db.String(100))
    end_time = db.Column(db.String(100))
    status =db.Column(db.String(1))
    current_passengers= db.Column(db.Integer)
    current_stop = db.Column(db.String)
    bus_no = db.Column(db.String)
    gps = db.Column(db.String(100))
    gps_update_time = db.Column(db.String)
    tickets = db.relationship('Ticket')
    lat = db.Column(db.String)
    long = db.Column(db.String)


'''