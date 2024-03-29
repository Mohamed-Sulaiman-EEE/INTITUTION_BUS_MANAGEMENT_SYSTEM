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
from .models import Student_details , Working_day , Site_settings , Route , Location_reference , Bus_data, Conductor_details , Trips , Tickets , Distance_data , Cards, Alerts
from twilio.rest import Client
from sqlalchemy.sql import func
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
    home_stop = student_details.home_phase
    lat2 = Location_reference.query.filter_by(name = home_stop).first().lat
    long2 = Location_reference.query.filter_by(name = home_stop).first().long

   
    if trips:
        if trips[0].status != "COMPLETED":
            trip = trips[0]
            phase = routes[0].phases.split(",")
            route=routes[0]
            lat=Bus_data.query.filter_by(no = trip.bus_id).first().lat
            long=Bus_data.query.filter_by(no = trip.bus_id).first().long
            
            distance = get_distance(float(lat) , float(long) , float(lat2) , float(long2))
        else:
            trip  = trips[1]
            phase = routes[1].phases.split(",")
            route = routes[1]
            lat=Bus_data.query.filter_by(no = trip.bus_id).first().lat
            long=Bus_data.query.filter_by(no = trip.bus_id).first().long
            distance = get_distance(float(lat) , float(long) , float(lat2) , float(long2))
    else:
        trip = None
        lat = long=phase=route= None

    return render_template("student_home.html" , user = current_user , w = working_day , trip=trip , phase = phase , route=route , lat=lat,long=long,distance = distance)



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
    tickets  = Tickets.query.filter_by(user_id = current_user.id).all()
    route_id = Student_details.query.filter_by(id=current_user.id).first()
    route_id = route_id.route
    trips = Trips.query.filter_by(route_id = route_id).all()
    working_days = Working_day.query.all()
    return render_template("student_trip_history.html" , user = current_user , tickets = tickets , trips = trips , working_days = working_days)



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
    ss = Site_settings.query.all()
    trips = Trips.query.filter_by(working_day=w.day)
    alerts = Alerts.query.all()

    return render_template("admin_home.html" , user = current_user, w = w , ss= ss , trips=trips , alerts = alerts)


@views.route('/admin-user-management', methods=['GET', 'POST'])
@login_required
def admin_user_management():
    students = User.query.filter_by(type = "S").all()
    student_details = Student_details.query.all()
    return render_template("admin_user_management.html" , user = current_user , students= students , student_details=student_details )


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
    routes = Route.query.all()
    buses = Bus_data.query.all()
    locations = Location_reference.query.all()
    return render_template("admin_fleet_management.html" , user = current_user , routes = routes, buses = buses , locations = locations )



@views.route('/admin-financial-stats', methods=['GET', 'POST'])
@login_required
def admin_finanacial_stats():
    routes = ['A' , 'B' , 'C' , 'D']
    tickets = Tickets.query.all()
    def generate_report():
        data = []
        for route in routes:
            row = []
            distance_sum = 0
            fare_sum = 0
            for ticket in tickets:
                if ticket.route_id == route:
                    distance_sum+=ticket.distance
                    fare_sum += ticket.fare
            row.append(route)
            row.append(distance_sum)
            row.append(fare_sum)
            data.append(row)
        return data

    data = generate_report()
    
    return render_template("admin_financial_stats.html" , user = current_user,data=data )



@views.route('/admin-emulator', methods=['GET', 'POST'])
@login_required
def admin_emulator():
    working_day = Site_settings.query.filter_by(key="current_working_day").first().value
    current_trip = Trips.query.filter_by(working_day = working_day,bus_id=1).all()
    queryM = current_trip[0].status
    queryE = current_trip[1].status
    if  queryM != 'COMPLETED':
        trip = current_trip[0]
    elif queryM =="COMPLETED" and queryE !="COMPLETED" :
        trip=current_trip[1]
    else:
        trip = None

    if trip :
        bus = Bus_data.query.filter_by(no = trip.bus_id).first()
    else:
        bus = None
    current_phase = trip.current_phase

    return render_template("admin_emulator.html" , user = current_user , trip = trip  , bus = bus , current_phase=current_phase)



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
    def alert_conductor():
        msg = "@Conductor_Alert !!!\nNew trip has been assigned for you ....\nWorking day :{0}\nRoute ID:{1}\nBus No :{2}\n".format(working_day,route_id,bus_id)
        cd = Conductor_details.query.filter_by(conductor_id = conductor_id).first()
        chatID= cd.chat_id
        sendMessage(chatID=chatID , message=msg)
    alert_conductor()
    
    return jsonify({})


@views.route('utility/delete-trip' , methods = ['POST'])
def delete_trip():
    data = json.loads(request.data)
    print(data)
    trip = Trips.query.filter_by(trip_id = data["trip_id"]).first()
    working_day = Working_day.query.filter_by(day = trip.working_day).first()
    working_day.trips_created = "N"
    db.session.delete(trip)
    db.session.commit()
    return jsonify({})

@views.route('utility/delete-location' , methods = ['DELETE'])
def delete_location():
    data = json.loads(request.data)
    location_id = data["location_id"]
    location = Location_reference.query.filter_by(id = location_id).first()
    db.session.delete(location)
    db.session.commit()
    return jsonify({})

@views.route('utility/delete-ticket' , methods = ['POST'])
def delete_ticket():
    data = json.loads(request.data)
    ticket = Tickets.query.filter_by(id = data["ticket_id"]).first()
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({})

@views.route('utility/add-location' , methods=['POST'])
def add_location():
    data = json.loads(request.data)
    name = data['name']
    lat = data['lat']
    long = data['long']
    print(data)
    gps = lat + "," + long
    location = Location_reference(name=name , lat = lat , long=long, gps=gps)
    db.session.add(location)
    db.session.commit()
    return jsonify({})



@views.route('utility/change-route' , methods =["POST"])
@login_required
def change_route():
    data = json.loads(request.data)
    print(data)
    sd = Student_details.query.filter_by(id = current_user.id).first()
    sd.route = data["route_id"]
    db.session.commit()
    return jsonify({})


@views.route('utility/increment-working-day' ,methods=["POST"])
def increment_working_day():
    working_day = Site_settings.query.filter_by(key="current_working_day").first()
    v = int(working_day.value)
    working_day.value = v + 1
    db.session.commit()
    return jsonify({})

@views.route('utility/resolve-alert' ,  methods = {'POST'})
def resolve_alert():
    data = json.loads(request.data)
    id = data["id"]
    alert = Alerts.query.filter_by(id=id).first()
    alert.status = "Resolved"
    db.session.commit()
    return jsonify({})

@views.route('utility/bus-breakdown-alert' , methods =['POST'])
def bus_breakdown_alert():
    data = json.loads(request.data)
    id = data["bus_id"]
    working_day = Site_settings.query.filter_by(key="current_working_day").first().value
    d = datetime.datetime.now().strftime("%X")
    description = "Bus no {0} is facing a breakdown at {1} !!!".format(id,d)
    admin_alert(description)
    new_alert=Alerts(working_day=working_day , type='Bus BreakDown Alert' , time=d , description = description,status="Unresolved")
    db.session.add(new_alert)
    db.session.commit()
    return jsonify({})





@views.route('utility/toggle-notification-settings' , methods = ["POST"])
@login_required
def toggle_notification_settings():
    data = json.loads(request.data)
    option = data["option"]
    print(option)
    sd = Student_details.query.filter_by(id=current_user.id).first()
    if sd.alrt_s_before_stop == "Y":
        sd.alrt_s_before_stop = "N"
        db.session.commit()
    else:
        sd.alrt_s_before_stop = "Y" 
        db.session.commit()
    return jsonify({})

#...................................API.................................................


@views.route('api/update-gps' , methods = ['POST' , 'GET'])
def update_gps():
    data = json.loads(request.data)
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
        evening_trip= True
        trip=current_trip[1]
    else:
        trip = None

    if trip :
        route = Route.query.filter_by(route_id= trip.route_id , session = trip.session).first()
        phases = route.phases
        phases = phases.split(",")
        #sendMessage(chatID="1113524785" , message=phases)
        curr_phase = trip.current_phase
        curr_index = phases.index(curr_phase)

        # print(curr_phase)
        if curr_index != len(phases)-1:
            nxt_phase = phases[curr_index+1]
            #curr_position = Location_reference.query.filter_by(name=curr_phase).first()
            nxt_position = Location_reference.query.filter_by(name=nxt_phase).first()
            if isOnRadius(bus.lat , bus.long , nxt_position.lat,nxt_position.long):
                trip.current_phase = nxt_phase
                db.session.commit()
                print(">>>>>>PHASE UPDATED SUCCESSFULLY !!!!") 
                test_alert(nxt_phase)
                if trip.session == "M":
                    alert_phase_updated( route = trip.route_id  , curr_phase = trip.current_phase)
                    alert_stop_reached(route = trip.route_id  , curr_phase = trip.current_phase)
            else:
                print(">>>> NO UPDATES !!! \n")
        else:
            def generate_fare():
                tickets = Tickets.query.filter_by(trip_id = trip.trip_id).all()
                per_km_price = 4
                for t in tickets:
                    fare = t.distance * per_km_price
                    t.fare = fare
                    db.session.commit()
                    fareAlert(trip.trip_id)
            generate_fare()
            d = datetime.datetime.now().strftime("%X")
            trip.end_time = d
            trip.status = "COMPLETED"
            db.session.commit()
            def alertParents():
                if trip.session == "M":
                    tickets = Tickets.query.filter_by(trip_id = trip.trip_id).all()
                    for t in tickets:
                        out_time = datetime.datetime.now().strftime("%X")
                        sd = Student_details.query.filter_by(id = t.user_id).first()
                        msg = "@Parent_Alert !!!\nBus has reached TCE at {0}".format(out_time)
                        parent_chat_id = sd.parent_chat_id
                        sendMessage(chatID=parent_chat_id , message=msg)
                        t.out_time = out_time
                        t.status= "OUT"
                        db.session.commit()
            alertParents()
            if evening_trip:
                def check_missing_child():
                    morning_trip = current_trip[0]
                    evening_trip = current_trip[1]
                    morning_trip_id = morning_trip.trip_id
                    evening_trip_id = evening_trip.trip_id

                    morning_tickets = Tickets.query.filter_by(trip_id = morning_trip_id )
                    evening_tickets = Tickets.query.filter_by(trip_id = evening_trip_id)
                    for m_ticket in morning_tickets:
                        lost = True
                        for e_ticket in evening_tickets:
                            if m_ticket.user_id == e_ticket.user_id:
                                lost = False
                        if lost :
                            user_id = m_ticket.user_id
                            name = User.query.filter_by(id = user_id).first().name
                            sd = Student_details.query.filter_by(id = user_id).first()
                            msg = "@Parent_Alert !!!Your Child {0} hasnt boarded the return trip !!!\n".format(name)
                            parent_chat_id = sd.parent_chat_id
                            sendMessage(chatID=parent_chat_id , message=msg)
                            create_missing_child_alert(name=name , id=user_id)

                check_missing_child()
    else:
        print(">>>> NO TRIP ACTIVE")

def isOnRadius(curr_lat,curr_long, nxt_lat,nxt_long):
    limit = 0.00215
    curr_lat=float(curr_lat)
    curr_long=float(curr_long)
    nxt_lat=float(nxt_lat)
    nxt_long=float(nxt_long)
    print("*********************************************")
    print(curr_lat , curr_long , nxt_lat , nxt_long)
    print(f'{abs(curr_lat-nxt_lat):5f}')
    print(f'{abs(curr_long-nxt_long):5f}')
    print("*********************************************")
    if abs(curr_lat-nxt_lat) <= limit and abs(curr_long-nxt_long) <=limit:
        return True
    else: 
        return False



#.........................................................................................................


@views.route('api/update-rfid' , methods = ['POST' , 'GET'])
def update_rfid():
    data = json.loads(request.data)
    working_day = Site_settings.query.filter_by(key="current_working_day").first().value
    bus_id = int(data["bus_id"])
    card = data["card"]
    
    if card != None:
        #black box message
        rfid = Cards.query.filter_by(card = card ).first().data
        msg = "@Black_Box\nIncoming Data:{0}\nRFID Number:{1}".format(data,rfid)
        sendMessage(chatID="1113524785" , message=msg)

    else:
        rfid = data["rfid"]
    
    def logRFID():
        f = open("logRFID.txt", "a")
        D = datetime.datetime.now().strftime("%X")
        f.write(D + ": ")
        f.write(data["bus_id"])
        f.write("/ ")
        f.write(rfid)
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
        if user :
            if user.type == "C" or user.type == "A":
                if trip.status == "CREATED":
                    trip.status = "INITIATED"
                    db.session.commit()
                    if trip.session == "M":
                        alert_M_trip_initiated(route= trip.route_id,  bus =trip.bus_id)
                    elif trip.session=="E":
                        alert_E_trip_initiated(route = trip.route_id , bus=trip.bus_id)
                        
                    d = datetime.datetime.now().strftime("%X")
                    trip.start_time = d 
                    db.session.commit()
                    return jsonify({"STATUS":"TRIP INITIATED"})
                
            else:
                print("STUDENT FUNCTION")
                student_details= Student_details.query.filter_by(id = user.id).first()
                
                if student_details.route == trip.route_id:
                    #valid student
                    #check incoming or outgoing
                    ticket = Tickets.query.filter_by(trip_id = trip.trip_id , user_id = user.id).first()
                    
                    if ticket == None:
                        print("Gonna book ticket")
                        #incoming
                        #book_ticket
                        in_time = datetime.datetime.now().strftime("%X")
                        route = student_details.route
                        end_stop = Route.query.filter_by(route_id = route).first().end
                        end_stop_location = Location_reference.query.filter_by(name = end_stop).first()
                        lat1 = end_stop_location.lat
                        long1 = end_stop_location.long
                        # distance_data = Distance_data.query.filter_by(route_id = trip.route_id , stop = student_details.home_phase).first() 
                        home_stop = student_details.home_phase
                        lat2 = Location_reference.query.filter_by(name = home_stop).first().lat
                        long2 = Location_reference.query.filter_by(name = home_stop).first().long
                        distance_data = get_distance(float(lat1) , float(long1),  float(lat2),float(long2) )
                        new_ticket = Tickets(user_id = user.id , 
                                        trip_id = trip.trip_id,
                                        rfid_number = user.rfid_number,
                                        in_time = in_time , 
                                        out_time="XX:YY:ZZ",
                                        status = "IN",
                                        route_id = trip.route_id,
                                        distance = distance_data,
                                        fare = 0)
                        db.session.add(new_ticket)
                        db.session.commit()
                        name = user.name
                        bus_no = trip.bus_id
                        parent_chat_id = student_details.parent_chat_id
                        #alert_boarded_bus(name=name ,parent_chat_id = parent_chat_id , bus_no = bus_no  )
                        msg = "@Parent_Alert \n {0} has boarded on bus no {1} @ {2}".format(name , bus_no , in_time)
                        sendMessage(chatID=parent_chat_id , message=msg)
                        status = "OK"
                        return jsonify({"STATUS" : status})
                    else:
                        #outgoing
                        out_time = datetime.datetime.now().strftime("%X")
                        ticket.out_time = out_time
                        ticket.status= "OUT"
                        db.session.commit()
                        #send parent message got down
                        name = user.name
                        bus_no = trip.bus_id
                        parent_chat_id = student_details.parent_chat_id
                        #alert_boarded_bus(name=name ,parent_chat_id = parent_chat_id , bus_no = bus_no  )
                        msg = "@Parent_Alert \n{0} has got down from bus no {1} @ {2}".format(name , bus_no , out_time)
                        sendMessage(chatID=parent_chat_id , message=msg)
                        status = "OK"
                        return jsonify({"STATUS" : "OK"})
                    
                else:
                    return jsonify({"STATUS" : "DENIED"})

        else:
            print("Non valid User !!!")
            return jsonify({"STATUS" : "DENIED"})
    
    return jsonify({"STATUS" : "DENIED"})


@views.route('/api/update-rfid-pico' , methods = ["POST", "GET"])
def update_rfid_pico():
    data = json.loads(request.data)
    card = data["card"]
    bus_id = data["bus_id"]
    rfid = Cards.query.filter_by(card = card ).first().data
    
    url = "https://mohamedsulaiman.pythonanywhere.com/api/update-rfid"
    data = {"bus_id" : bus_id, "rfid":rfid}
    sendMessage(chatID="1113524785" , message=rfid)
    reply = requests.post(url=url , json = data )
    print(reply)
    return reply

#........................MESSAGING SERVICES......................


def sendMessage(chatID , message):
    
    apiToken = Site_settings.query.filter_by(key = "bot_token").first().value
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        logMESSAGE(response.text)
    except Exception as e:
        print(e)
    


def alert_M_trip_initiated(route , bus):
    msg = "Trip {0} has been initiated !!!  \nTodays bus no :{1}".format(route , bus)
    students = Student_details.query.filter_by(route=route).all()
    for s in students:
        chatID = s.student_chat_id
        sendMessage(chatID=chatID , message = msg)
    
def alert_E_trip_initiated(route , bus):
    msg = "Trip {0} has been initiated !!! \nBus will depart in 15 mins !!!\nBoard on bus No : {1}  ".format(route , bus)
    students = Student_details.query.filter_by(route= route ).all()
    for s in students:
        chatID = s.student_chat_id
        sendMessage(chatID=chatID , message = msg)

def alert_boarded_bus(name , parent_chat_id , bus_no):
    msg = "{0} has boarded on bus no {1}".format(name , bus_no)
    sendMessage(chatID=parent_chat_id , message=msg)


def alert_phase_updated(route,curr_phase):
    students = Student_details.query.filter_by(route = route, trigger_phase = curr_phase).all()
    for s in students:
        msg = "Bus has reached {0} !!! ".format(curr_phase)
        sendMessage(chatID=s.student_chat_id , message=msg)

    pass 


def alert_stop_reached(route,curr_phase):
    students = Student_details.query.filter_by(route = route, home_phase = curr_phase).all()
    for s in students:
        msg = "Bus has reached your stop - {0} !!! ".format(curr_phase)
        sendMessage(chatID=s.student_chat_id , message=msg)
    
def fareAlert(trip_id):
    tickets = Tickets.query.filter_by(trip_id = trip_id).all()
    for t in tickets:
        sd = Student_details.query.filter_by(id = t.user_id).first()
        msg = "Trip has been completed !!! \nToday's fare is Rs.{0}".format(t.fare)
        chatID = sd.student_chat_id
        sendMessage(chatID=chatID , message=msg)

def create_missing_child_alert(name , id):
    working_day = Site_settings.query.filter_by(key="current_working_day").first().value
    d = datetime.datetime.now().strftime("%X")
    description = "Student {0} of ID {1} is missing in return trip!!!".format(name,id)
    admin_alert(description)
    new_alert=Alerts(working_day=working_day , type='Student Missing Alert' , time=d , description = description,status="Unresolved")
    db.session.add(new_alert)
    db.session.commit()

def test_alert(phase):
    msg = "@Phase_Update_Alert \n {0} stop has been  reached ".format(phase)
    sendMessage(chatID="1113524785" , message=msg)
    #sendMessage(chatID="1809270475" , message=msg)


def admin_alert(msg):
    sendMessage(chatID="1113524785" , message=msg)

def logMESSAGE(response):
    f = open("logMESSAGE.txt", "a")
    D = datetime.datetime.now().strftime("%X")
    f.write(D + ": ")
    f.write(response)
    f.write("\n")
    f.close()


@views.route('/test' , methods=["POST" , "GET"])
@login_required
def test():
    flash("test")
    return render_template("admin_home.html")



def get_distance(lat1 , lon1 , lat2 , lon2):
    import math
    R = 6371 
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return round(distance  , 2)

#...............EMULATOR.....................




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