from email import message
from multiprocessing.sharedctypes import Value
from time import time
from unicodedata import name
from flask import Blueprint, render_template, request, flash, jsonify , redirect, url_for
from flask_login import login_required, current_user
from .models import User
from . import db
import json , requests , random , datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Student_details , Working_day , Site_settings , Route , Location_reference , Bus_data, Conductor_details , Trips
from twilio.rest import Client
ACCOUNT_SID = "AC7f9029cb62c986a4c38b0ef0bb395a27" 

# END OF IMPORTS
views = Blueprint('views', __name__)
#....................................................................................
@views.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html", user=current_user)



#....................................................................................

#.........................STUDENT FUNCTIONS...........................................................

@views.route('/student-home', methods=['GET', 'POST'])
@login_required
def student_home():
    return render_template("student_home.html" , user = current_user)



@views.route('/student-profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    student_detail = Student_details.query.filter_by(id = current_user.id).first()
    return render_template("student_profile.html" , user = current_user,
    student_detail = student_detail)



@views.route('/student-notification-settings', methods=['GET', 'POST'])
@login_required
def student_notification_settings():
    return render_template("student_notification_settings.html" , user = current_user)



@views.route('/student-trip-history', methods=['GET', 'POST'])
@login_required
def student_trip_history():
    return render_template("student_trip_history.html" , user = current_user)



#.................................CONDUCTOR FUNCTIONS .............................................

@views.route('/conductor-home', methods=['GET', 'POST'])
@login_required
def conductor_home():
    return render_template("conductor_home.html" , user = current_user)




@views.route('/conductor-current-trip', methods=['GET', 'POST'])
@login_required
def conductor_current_trip():
    return render_template("conductor_current_trip.html" , user = current_user)



@views.route('/conductor-trip-history', methods=['GET', 'POST'])
@login_required
def conductor_trip_history():
    return render_template("conductor_trip_history.html" , user = current_user)




#...................................ADMIN FUNCTIONS.................................................

@views.route('/admin-home', methods=['GET', 'POST'])
@login_required
def admin_home():
    return render_template("admin_home.html" , user = current_user )


@views.route('/admin-user-management', methods=['GET', 'POST'])
@login_required
def admin_user_management():
    return render_template("admin_user_management.html" , user = current_user )


@views.route('/admin-trip-management', methods=['GET', 'POST'])
@login_required
def admin_trip_management():
    working_days = Working_day.query.all()
    routes = Route.query.all()
    bus_data = Bus_data.query.all()
    conductor_details= Conductor_details.query.all()
    trips = Trips.query.all()

    return render_template("admin_trip_management.html" , user = current_user , 
                        working_days = working_days , routes = routes , bus_data=bus_data , conductor_details=conductor_details , trips=trips )


@views.route('/admin-fleet-management', methods=['GET', 'POST'])
@login_required
def admin_fleet_management():
    return render_template("admin_fleet_management.html" , user = current_user )



@views.route('/admin-financial-stats', methods=['GET', 'POST'])
@login_required
def admin_finanacial_stats():
    return render_template("admin_financial_stats.html" , user = current_user )



@views.route('/admin-emulator', methods=['GET', 'POST'])
@login_required
def admin_emulator():
    return render_template("admin_emulator.html" , user = current_user )



#...................................UTILITY FUNCTIONS.................................................

@views.route('utility/week-book' , methods = ['POST','GET'])
@login_required
def week_book():
    data = json.loads(request.data)
    week_starting_date = data["week_starting_date"]
    monday = data["monday"]
    tuesday = data["tuesday"]
    wednesday = data["wednesday"]
    thursday = data["thursday"]
    friday = data["friday"]
    print(data)
    working_day_run = Site_settings.query.filter_by(key="working_day_run").first()
    if week_starting_date:
        date = week_starting_date.split("-")
        date = datetime.datetime(int(date[0]),int(date[1]),int(date[2]))
        if monday :
            create_trip( date+datetime.timedelta(days=1))
            working_day_run.value = int(working_day_run.value)+1
        if tuesday :
            create_trip( date+datetime.timedelta(days=2))
            working_day_run.value = int(working_day_run.value)+1
        if wednesday :
            create_trip( date+datetime.timedelta(days=3))
            working_day_run.value = int(working_day_run.value)+1
        if thursday :
            create_trip( date+datetime.timedelta(days=4))
            working_day_run.value = int(working_day_run.value)+1
        if friday :
            create_trip( date+datetime.timedelta(days=5))
            working_day_run.value = int(working_day_run.value)+1
        db.session.commit()
       
    return jsonify({})

def create_trip(date):
    new = Working_day(date = date.strftime("%x") , trips_created = "N" , week_day = date.strftime("%a"))
    db.session.add(new)

@views.route('utility/create-trips' , methods = ['POST' , 'GET'])
@login_required
def create_trips():
    data = json.loads(request.data)
    working_day = data["working_day"]
    route_id = data["route_id"]
    conductor_id=data["conductor_id"]
    bus_id = data["bus_id"]
    new_trip_M = Trips(working_day=working_day, route_id=route_id,conductor_id=conductor_id,bus_id= bus_id,session="M",current_phase="",start_time="XX:YY:ZZ" ,end_time  = "XX:YY:ZZ" , status = "CREATED" )
    new_trip_E = Trips(working_day=working_day, route_id=route_id,conductor_id=conductor_id,bus_id= bus_id,session="E",current_phase="",start_time="XX:YY:ZZ",end_time  = "XX:YY:ZZ" , status = "CREATED" )
    db.session.add(new_trip_M)
    db.session.add(new_trip_E)
    db.session.commit()
    return jsonify({})



#...................................API.................................................




'''



@views.route('/utility-view-route-map/<route>', methods=['GET', 'POST'])
@login_required
def utility_view_route_map(route):
    flash(route)
    return render_template("view_route_map.html" ,user = current_user, route = route)




@views.route('/utility-view-map/<trip_id>', methods=['GET' , 'POST'])
@login_required
def utility_view_map(trip_id):
    trip = Trip.query.filter_by(trip_id = trip_id).first()
    gps = trip.gps
    flash(gps)
    #base_url = "https://www.google.com/maps/@?api=1&map_action=map&cenetr=" //Without Pointer
    base_url = "https://www.google.com/maps/search/?api=1&query=" # with Pointer
    url = base_url +gps
    webbrowser.open_new(url)
    return redirect(url_for('views.conductor_current_trip'))
    


@views.route('/test-js', methods=['POST'])
def test_js():
    data = json.loads(request.data)
    gps = data["gps"]
    flash(gps)
    return jsonify({})

'''