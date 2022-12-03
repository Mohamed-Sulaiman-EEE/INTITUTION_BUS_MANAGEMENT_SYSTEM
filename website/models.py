from multiprocessing.sharedctypes import Value
from tkinter.tix import INTEGER

#from website.views import conductor_home
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    phone_number = db.Column(db.String(15))
    type = db.Column(db.String(1))
    account_number = db.Column(db.String(10))
    balance = db.Column(db.Integer)
    scratch_cards = db.relationship('Scratch_card')
    helpdesk_recharges = db.relationship('Helpdesk_recharge')
    trips = db.relationship('Trip')
    #tickets = db.relationship('Ticket')


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

class Scratch_card(db.Model,UserMixin):
    id = db.Column(db.Integer , primary_key = True)
    card_number =db.Column(db.Integer)
    security_hash = db.Column(db.Integer)
    value = db.Column(db.Integer)
    status = db.Column(db.String(1))
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'))
    date = db.Column(db.String(10))
    
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
    #conductor_details = db.relationship('Conductor_details')


class Fare(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    from_ = db.Column(db.String)
    to = db.Column(db.String)
    price = db.Column(db.Integer)
    routes = db.Column(db.String)

class Ticket(db.Model,UserMixin):
    ticket_id = db.Column(db.String(100), primary_key = True)
    trip_id = db.Column(db.Integer , db.ForeignKey('trip.trip_id'))
    #user_id = db.Column(db.Integer , db.ForeignKey('user.id'))
    #passenger_account_number =  db.Column(db.Integer , db.ForeignKey('user.account_number'))
    passenger_account_number =  db.Column(db.String)
    route = db.Column(db.String(100))
    boarding_stop = db.Column(db.String(100))
    destination_stop = db.Column(db.String(100))
    date = db.Column(db.String(100))
    time = db.Column(db.String(100))
    no = db.Column(db.Integer)
    fare = db.Column(db.Integer)


