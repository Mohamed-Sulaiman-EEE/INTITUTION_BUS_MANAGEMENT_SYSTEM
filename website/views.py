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
    w = Site_settings.query.filter_by(key="current_working_day").first().value
    working_day = Working_day.query.filter_by(day=w).first()
    student_details = Student_details.query.filter_by(id = current_user.id).first()
    routes = Route.query.filter_by(route_id = student_details.route).all()
    trips = Trips.query.filter_by(working_day=w , route_id = student_details.route).all()
   
    if trips:
        if trips[0].status != "COMPLETED":
            trip = trips[0]
            phase = routes[0].phases.split(",")
            route=routes[0]
            lat=Bus_data.query.filter_by(no = trip.bus_id).first().lat
            long=Bus_data.query.filter_by(no = trip.bus_id).first().long
        else:
            trip  = trips[1]
            phase = routes[1].phases.split(",")
            route = routes[1]
            lat=Bus_data.query.filter_by(no = trip.bus_id).first().lat
            long=Bus_data.query.filter_by(no = trip.bus_id).first().long
   


    return render_template("student_home.html" , user = current_user , w = working_day , trip=trip , phase = phase , route=route , lat=lat,long=long)



@views.route('/student-profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    student_detail = Student_details.query.filter_by(id = current_user.id).first()
    return render_template("student_profile.html" , user = current_user,
    student_detail = student_detail)



@views.route('/student-notification-settings', methods=['GET', 'POST'])
@login_required
def student_notification_settings():
    sd = Student_details.query.filter_by(id=current_user.id).first()
    return render_template("student_notification_settings.html" , user = current_user , sd = sd)



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
    working_day = Site_settings.query.filter_by(key="current_working_day").first().value
    w = Working_day.query.filter_by(day=working_day).first()

    return render_template("admin_home.html" , user = current_user, w = w )


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
    '''
    Function to create working days in batch of 5 
    '''
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
    route1= Route.query.filter_by(route_id = route_id , session = "M").first()
    route2= Route.query.filter_by(route_id = route_id , session = "E").first()
    start1 = route1.start
    start2 = route2.start
    print(start1,start2)
    new_trip_M = Trips(working_day=working_day, route_id=route_id,conductor_id=conductor_id,bus_id= bus_id,session="M",current_phase=start1,start_time="XX:YY:ZZ" ,end_time  = "XX:YY:ZZ" , status = "CREATED" )
    new_trip_E = Trips(working_day=working_day, route_id=route_id,conductor_id=conductor_id,bus_id= bus_id,session="E",current_phase=start2,start_time="XX:YY:ZZ",end_time  = "XX:YY:ZZ" , status = "CREATED" )
    db.session.add(new_trip_M)
    db.session.add(new_trip_E)
    w = Working_day.query.filter_by(day=working_day).first()
    w.trips_created="Y"
    db.session.commit()
    
    return jsonify({})

@views.route('utility/increment-working-day' ,methods=["POST"])
def increment_working_day():
    working_day = Site_settings.query.filter_by(key="current_working_day").first()
    v = int(working_day.value)
    working_day.value = v + 1
    db.session.commit()
    
    return jsonify({})


#...................................API.................................................


@views.route('api/update-gps' , methods = ['POST' , 'GET'])
def update_gps():
    data = json.loads(request.data)
    #print(data)
    bus_id = int(data["bus_id"])
    bus = Bus_data.query.filter_by(no = bus_id).first()
    bus.lat = data["lat"]
    bus.long = data["long"]
    bus.gps = data["gps"]
    db.session.commit()

    def logGPS():
        f = open("logGPS.txt", "a")
        D = datetime.datetime.now().strftime("%X")
        f.write(D + ": ")
        f.write(str(bus_id))
        f.write("/ ")
        f.write(data["gps"])
        f.write("\n")
        f.close()
    logGPS()

    # DO ALL STUFF AFTER GPS UPDATE
    status = "OK"

    check_phase(bus_id)

    return jsonify({"status":status})

def check_phase(bus_id):
    bus = Bus_data.query.filter_by(no = bus_id).first()
    working_day = Site_settings.query.filter_by(key="current_working_day").first().value
    current_trip = Trips.query.filter_by(working_day = working_day,bus_id=bus_id).all()
    queryM = current_trip[0].status
    queryE = current_trip[1].status
    if  queryM == 'INITIATED':
        trip = current_trip[0]
    elif queryM =="COMPLETED" and queryE =="INITIATED" :
        trip=current_trip[1]
    else:
        trip = None

    if trip :
        route = Route.query.filter_by(route_id= trip.route_id).first()
        phases = route.phases
        phases = phases.split(",")
        curr_phase = trip.current_phase
        curr_index = phases.index(curr_phase)


        if curr_index != len(phases)-1:
            nxt_phase = phases[curr_index+1]
            #curr_position = Location_reference.query.filter_by(name=curr_phase).first()
            nxt_position = Location_reference.query.filter_by(name=nxt_phase).first()
            if isOnRadius(bus.lat , bus.long , nxt_position.lat,nxt_position.long):
                trip.current_phase = nxt_phase
                db.session.commit()
                print(">>>>>>PHASE UPDATED SUCCESSFULLY !!!!") 
            else:
                print(">>>> NO UPDATES !!! \n")
        else:
            trip.status = "COMPLETED"
            d = datetime.datetime.now().strftime("%X")
            trip.end_time = d
            db.session.commit()
    else:
        print(">>>> NO TRIP ACTIVE")

def isOnRadius(curr_lat,curr_long, nxt_lat,nxt_long):
    limit = 0.007
    curr_lat=float(curr_lat)
    curr_long=float(curr_long)
    nxt_lat=float(nxt_lat)
    nxt_long=float(nxt_long)
    print(curr_lat , curr_long , nxt_lat , nxt_long)
    print(abs(curr_lat-nxt_lat))
    print(abs(curr_long-nxt_long))
    if abs(curr_lat-nxt_lat) <= limit or abs(curr_long-nxt_long) <=limit:
        return True
    else: 
        return False



#.........................................................................................................


@views.route('api/update-rfid' , methods = ['POST' , 'GET'])
def update_rfid():
    data = json.loads(request.data)
    working_day = Site_settings.query.filter_by(key="current_working_day").first().value
    bus_id = int(data["bus_id"])
    rfid = data["rfid"]
    print(data)
    
    def logRFID():
        f = open("logRFID.txt", "a")
        D = datetime.datetime.now().strftime("%X")
        f.write(D + ": ")
        f.write(data["bus_id"])
        f.write("/ ")
        f.write(data["rfid"])
        f.write("\n")
        f.close()
    logRFID()
    current_trip = Trips.query.filter_by(working_day = working_day,bus_id=bus_id).all()
    queryM = current_trip[0].status
    queryE = current_trip[1].status
    if  queryM != 'COMPLETED':
        trip = current_trip[0]
    elif queryM == "COMPLETED"  :
        trip=current_trip[1]
    elif queryE == "COMPLETED" and queryM=="COMPLETED":
        trip = None
    if trip :
        user = User.query.filter_by(rfid_number = rfid).first()
        if user.type == "C" or user.type == "A":
            print("fck")
            d = datetime.datetime.now().strftime("%X")
            print(d)
            if trip.status == "CREATED":
                trip.status = "INITIATED"
                
                trip.start_time = d 
                db.session.commit()
            
        else:

            print("STUDENT FUNCTION")
    return jsonify({})
    




            




#........................MESSAGING SERVICES......................








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