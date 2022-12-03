from email import message
from multiprocessing.sharedctypes import Value
from time import time
from unicodedata import name
from flask import Blueprint, render_template, request, flash, jsonify , redirect, url_for
from flask_login import login_required, current_user
from .models import  Ticket, User , Conductor_details , Route, Scratch_card , Site_settings , Helpdesk_recharge, Trip  , Fare
from . import db
import json , requests , random , datetime
import webbrowser
from werkzeug.security import generate_password_hash, check_password_hash

from twilio.rest import Client
ACCOUNT_SID = "AC7f9029cb62c986a4c38b0ef0bb395a27" 

# END OF IMPORTS
views = Blueprint('views', __name__)
#....................................................................................
@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)

@views.route('/about', methods=['GET', 'POST'])
def about():
    return render_template("about.html", user=current_user)

#....................................................................................

#.........................USER FUNCTIONS...........................................................
@views.route('/user-home', methods=['GET', 'POST'])
@login_required
def user_home():
    return render_template("user_home.html" , user = current_user)


@views.route('/user-enquire-route', methods=['GET', 'POST'])
@login_required
def user_enquire_route():
    if request.method =="POST":
        boarding_stop = request.form.get('boarding_stop')
        destination_stop = request.form.get("boarding_stop")
        routes = Route.query.all()
        possible_route_id = list()
        for route in routes : 
            data = route.start +"," +route.stops + "," + route.end
            data = data.split(",")
            l = len(data)
            i = 0
            board_index = dest_index = -1
            while(i < l - 1):
                if data[i] == boarding_stop:
                    board_index = i
                if data[i] == destination_stop:
                    dest_index = i
                i += 1
            if board_index > dest_index or board_index == -1 or dest_index == -1:
                break
            else:
                possible_route_id.append(route.route_id)

        trips = Trip.query.filter_by(status = "A").all()
        return render_template("user_enquire_route.html" , user = current_user , trips = trips , boarding_stop = boarding_stop , destination_stop = destination_stop,
                                        possible_route_id = possible_route_id)
    return render_template("user_enquire_route.html" , user = current_user )


@views.route('/user-travel-history', methods=['GET', 'POST'])
@login_required
def user_travel_history():
    trips = Ticket.query.filter_by(passenger_account_number = current_user.account_number).all()
    return render_template("user_travel_history.html" , user = current_user, trips = trips)



@views.route('/user-wallet', methods=['GET', 'POST'])
@login_required
def user_wallet():
    if request.method == "POST":
        id = request.form.get('card_number')
        security_hash = request.form.get('security_hash')
        card = Scratch_card.query.filter_by(card_number = id ).first()
        if card.status == "U":
            flash("Card has already been used !!!" , category="error")
            return render_template("user_wallet.html", user = current_user)
        elif card.security_hash != security_hash:
            flash("Wrong security hash !!!",category="error")
        card.status = "U"
        card.user_id = current_user.id
        date = datetime.datetime.now()
        date = str(date.strftime("%c"))
        card.date = date
        current_user.balance += card.value
        db.session.commit()
        flash("{0} Rupess recharged  successfully !!!".format(card.value) , category="success")
    history = current_user.scratch_cards
    help = current_user.helpdesk_recharges
    return render_template("user_wallet.html" , user = current_user , history=history , help = help )





@views.route('/utility-view-route-map/<route>', methods=['GET', 'POST'])
@login_required
def utility_view_route_map(route):
    flash(route)
    return render_template("view_route_map.html" ,user = current_user, route = route)



#.................................CONDUCTOR FUNCTIONS .............................................

@views.route('/conductor-home', methods=['GET', 'POST'])
@login_required
def conductor_home():
    conductor_details = Conductor_details.query.filter_by(conductor_id = current_user.id).first()
    return render_template("conductor_home.html" , user = current_user,cd = conductor_details)



@views.route('/conductor-current-trip', methods=['GET', 'POST'])
@login_required
def conductor_current_trip ():
    conductor_details = Conductor_details.query.filter_by(conductor_id = current_user.id).first()
    if conductor_details.current_trip_id :
        trip = Trip.query.filter_by(trip_id= conductor_details.current_trip_id).first()
        route = Route.query.filter_by(route_id = trip.route_id ).first() 
        # To display Only ahead stops
        display_stops = route.start +"," +route.stops + "," + route.end 
        display_stops = display_stops.split(",")
        curr_stop = trip.current_stop
        curr_index = display_stops.index(curr_stop)
        display_stops = display_stops[curr_index+1:]
        #flash("Loaded Args")
        #ONLY AHEAD STOPS
        if request.method=="POST":
            #flash("post request")
            passenger_account_number = request.form.get('account_number')
            destination_stop = request.form.get('to')
            no = int(request.form.get('no'))
            if destination_stop == None : 
                flash("No more Bookings !!!")
                #return redirect(url_for('views.conductor_current_trip'))
                return render_template("conductor_current_trip.html" , user = current_user, cd = conductor_details,trip = trip ,route=route,display_stops = display_stops)
            if  passenger_account_number and destination_stop and no :
                #flash("gotcha")
                if destination_stop == None:
                    flash("No more Bookings !!!")
                    #return redirect(url_for('views.conductor_current_trip'))
                    return render_template("conductor_current_trip.html" , user = current_user, cd = conductor_details,trip = trip ,route=route,display_stops = display_stops)

                def generate_fare(route = route , trip = trip , destination_stop = destination_stop ):
                    data = route.start +"," + route.stops + "," + route.end
                    data = data.split(",")
                    curr_stop = trip.current_stop
                    curr_index = 0
                    dest_index = 0
                    for i in range(len(data)):
                        if data[i] == curr_stop:
                            curr_index = i
                        if data[i] == destination_stop:
                            dest_index = i
                    fare = 0
                    while curr_index != dest_index:
                        next_stop = data[curr_index+1]
                        sprint = Fare.query.filter_by(from_=curr_stop , to = next_stop).first()
                        if sprint :
                            fare = fare + sprint.price
                            curr_index +=1
                            curr_stop = data[curr_index]
                    return fare

                fare = generate_fare(route = route , trip = trip ,destination_stop=destination_stop )
                fare = fare*no

                passenger = User.query.filter_by(account_number = passenger_account_number).first()

                if passenger == None:
                    flash("User Not Found")
                    return render_template("conductor_current_trip.html" , user = current_user, cd = conductor_details,trip = trip ,route=route,display_stops = display_stops)
                    #return redirect(url_for('views.conductor_home'))
                elif passenger.balance < fare:
                    flash("Insufficinet Balance !!!")
                    return render_template("conductor_current_trip.html" , user = current_user, cd = conductor_details,trip = trip ,route=route,display_stops = display_stops)
                #Check balance properly
                else: 
                    #flash("Legit User")
                    trip.ticket_run = trip.ticket_run + 1
                    prefix_len = 9 - len(str(trip.trip_id))
                    postfix_len = 3- len(str(trip.ticket_run))
                    ticket_id = "T" + "0"*prefix_len + str(trip.trip_id)+ "0"*postfix_len + str(trip.ticket_run)

                    date_time = datetime.datetime.now()
                    date = str(date_time.strftime('%x'))
                    time = str(date_time.strftime('%X'))


                    ticket = Ticket(ticket_id= ticket_id ,
                                    trip_id= trip.trip_id ,
                                    passenger_account_number = passenger_account_number,
                                    route = route.route_id,
                                    boarding_stop = trip.current_stop,
                                    destination_stop = destination_stop,
                                    no = no,
                                    fare = fare,
                                    date = date, 
                                    time = time)

                    db.session.add(ticket)
                    trip.current_passengers = trip.current_passengers  + no
                    trip.collection = trip.collection + fare
                    passenger.balance = passenger.balance - fare
                    current_user.balance = current_user.balance + fare
                    ss = Site_settings.query.first()
                    AUTH_TOKEN = ss.auth 
                    P = passenger.phone_number
                    def send_sms(phone, message):
                        client = Client(ACCOUNT_SID, AUTH_TOKEN)
                        print(phone)
                        F = "+18315766483"
                        P = phone
                        message = client.messages.create(body= message, from_= F,  to = P )
                    current_stop = trip.current_stop
                    message = "Ticket booked ! From :{0} , To : {1} , Fare : {2} , No : {3}  ".format(current_stop , destination_stop , fare , no )
                    #send_sms(phone = P , message = message)
                    try :
                        send_sms(phone = P , message = message)
                        flash("Message Sent successfully :)")
                    except:
                        flash("Message Coudlnt be Sent :(")

                    db.session.commit()
                    flash("Booked Ticket Successfully !!!")
            
            else:
                #flash("Enter details")
                return redirect(url_for('views.conductor_current_trip'))
                #return render_template("conductor_current_trip.html" , user = current_user, cd = conductor_details,trip = trip ,route=route,display_stops = display_stops)
        #flash("Hmm")
        return render_template("conductor_current_trip.html" , user = current_user, cd = conductor_details,trip = trip ,route=route,display_stops = display_stops)
    flash("No Current Trips !!!")
    return render_template("conductor_current_trip.html" , user = current_user, cd = conductor_details)


@views.route('/conductor-my-trips', methods=['GET', 'POST'])
@login_required
def conductor_my_trips():
    trips = Trip.query.filter_by(conductor_id = current_user.id).all()
    conductor_details = Conductor_details.query.filter_by(conductor_id = current_user.id).first()
    return render_template("conductor_my_trips.html" , user = current_user , trips = trips, cd= conductor_details )



@views.route('/conductor-view-details/<trip_id>', methods=['GET', 'POST'])
@login_required
def conductor_view_details (trip_id):
    trip = Trip.query.filter_by(trip_id=trip_id).first()
    route = Route.query.filter_by(route_id = trip.route_id ).first()
    tickets = trip.tickets
    return render_template("conductor_view_details.html" , user = current_user, trip=trip, route=route , tickets = tickets)


@views.route('/conductor-utility-create-trip/<route_id>', methods=['GET' , 'POST'])
@login_required
def conductor_utility_create_trip(route_id):
    conductor_details = Conductor_details.query.filter_by(conductor_id = current_user.id).first()
    if conductor_details.current_trip_id is not None:
        flash("Complete the present trip !!!")
        return render_template("conductor_home.html" , user = current_user,cd = conductor_details)
    route = Route.query.filter_by(route_id = route_id).first()
    date_time = datetime.datetime.now()
    date = str(date_time.strftime('%x'))
    start_time = str(date_time.strftime('%X'))
    end_time="XX:XX:XX"
    trip = Trip(route_id= route_id ,
                conductor_id = current_user.id , 
                collection = 0,
                ticket_run =0,
                status = "A",
                current_passengers = 0,
                current_stop = route.start,
                date = date ,
                start_time = start_time,
                end_time = end_time ,
                bus_no = conductor_details.bus_no,
                gps = "0,0",
                lat = "0",
                long = "0",
                gps_update_time = "00:00:00" )
    db.session.add(trip)
    db.session.commit()
    conductor_details.current_trip_id = trip.trip_id
    db.session.commit()
    flash("Trip created succesfully ")
    return redirect(url_for('views.conductor_current_trip'))
    



@views.route('/conductor-utility-next-stop/<trip_id>', methods=['GET' , 'POST'])
@login_required
def conductor_utility_next_stop(trip_id):
    '''
    Before next stop , 
    1 >> Check if this is last stop
    2 >> Reduce current passengers who get down at next stop whn reached 
    '''

    conductor_details = Conductor_details.query.filter_by(conductor_id = current_user.id).first()
    if conductor_details.current_trip_id is not None:
        trip = Trip.query.filter_by(trip_id = trip_id).first()
        route = Route.query.filter_by(route_id=trip.route_id).first()
        data = route.start +"," + route.stops + "," + route.end
        data = data.split(",")
        curr_index = data.index(trip.current_stop)
        
        if curr_index == len(data)-1 :
            flash('Final Stop Reached!!!')
            return redirect(url_for('views.conductor_current_trip'))
        else:
            trip.current_stop = data[curr_index+1]
        #STOP UPDATED

        #UPDATING CURRENT PASSENGERS
        ticket = Ticket.query.filter_by(trip_id = trip.trip_id).all()
        get_down_ppl = 0
        for t in ticket:
            if t.destination_stop == data[curr_index+1]:
                get_down_ppl = get_down_ppl + t.no
        trip.current_passengers = trip.current_passengers - get_down_ppl
        db.session.commit()
        flash("Geared UP !!!")
        return redirect(url_for('views.conductor_current_trip'))
    return redirect(url_for('views.conductor_current_trip'))



@views.route('/conductor-utility-end-trip/<trip_id>', methods=['GET' , 'POST'])
@login_required
def conductor_utility_end_trip(trip_id):
    conductor_details = Conductor_details.query.filter_by(conductor_id = current_user.id).first()
    if conductor_details.current_trip_id is not None:
        conductor_details.current_trip_id = None
        trip = Trip.query.filter_by(trip_id = trip_id).first()
        trip.status ="I"
        end_time = str(datetime.datetime.now().strftime("%X"))
        trip.end_time = end_time
        current_user.balance = current_user.balance +  trip.collection
        db.session.commit()
        flash("Trip ended Successfully !!! ")
        return render_template("conductor_home.html" , user = current_user,cd = conductor_details)
    return redirect(url_for('views.conductor_current_trip'))




@views.route('/conductor-utility-refresh-gps', methods=['POST'])
def conductor_utility_refresh_gps():
    data = json.loads(request.data);
    gps = data["gps"]    
    lat = data["lat"]
    long = data["long"]
    cd = Conductor_details.query.filter_by(conductor_id = current_user.id).first()
    trip_id = cd.current_trip_id
    trip = Trip.query.filter_by(trip_id = trip_id).first()
    date_time = datetime.datetime.now()
    date = str(date_time.strftime('%x'))
    update_time = str(date_time.strftime('%X'))
    trip.gps = gps
    trip.lat = lat
    trip.long = long
    trip.gps_update_time = update_time 
    db.session.commit()
    flash("Refreshed GPS")
    return jsonify({})



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
    

#...................................ADMI FUNCTIONS.................................................

@views.route('/admin-home', methods=['GET', 'POST'])
@login_required
def admin_home():
    return render_template("admin_home.html" , user = current_user )

#....................................................................................

@views.route('/admin-manage-routes', methods=['GET', 'POST'])
@login_required
def admin_manage_routes():
    if request.method == "POST":
        route_id =  request.form.get('route_id') 
        start =  request.form.get('start') 
        end =  request.form.get('end') 
        stops =  request.form.get('stops')
        new_route = Route(route_id=route_id , start=start , end = end , stops = stops)
        db.session.add(new_route)
        db.session.commit()
        flash("Route added successfully !!!")
    route = Route.query.all()
    return render_template("admin_manage_routes.html" , user = current_user , route=route)


@views.route('/admin-manage-conductors', methods=['GET', 'POST'])
@login_required
def admin_manage_conductors():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        bus_no = request.form.get('bus_no')
        routes_assigned = request.form.get('routes_assigned')
        
        conductor = User.query.filter_by(email=email).first()
        if conductor:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 2:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_conductor = User(email=email, 
                                name= name ,
                                phone_number= phone_number ,  
                                password=generate_password_hash(password1, method='sha256') , 
                                balance = 0 , 
                                type = "C" )
            db.session.add(new_conductor)
            db.session.commit()
            cd = Conductor_details(conductor_id = new_conductor.id , 
                                    bus_no = bus_no , 
                                    routes_assigned = routes_assigned ,
                                    current_trip_id = None
                                     )
            db.session.add(cd)
            generate_account_details(new_conductor)
            db.session.commit()
            flash("Conductor added successfully !!!")
            return redirect(url_for('views.admin_home'))

    conductors = User.query.filter_by(type = "C").all()
    cd = Conductor_details.query.all()
    return render_template("admin_manage_conductors.html" , user = current_user ,conductors = conductors , cd = cd)


@views.route('/admin-wallet-recharge', methods=['GET', 'POST'])
@login_required
def admin_wallet_recharge():
    ss= Site_settings.query.first()
    scr = ss
    if request.method== "POST":
        no = request.form.get('no') 
        value = request.form.get('value')
        account_number = request.form.get('account_number')
        val = request.form.get('val')
        if account_number and val :
            flash("Recharged successfully ")
            val = int(val)
            user = User.query.filter_by(account_number=account_number).first()
            date = datetime.datetime.now()
            date = str(date.strftime("%c"))
            help = Helpdesk_recharge(account_number = user.account_number , value = val , date = date)
            user.balance = user.balance + val
            db.session.add(help)
            db.session.commit()
            passenger = user
            return render_template("admin_wallet_recharge.html" , user = current_user , scr = scr,passenger=passenger)

        if no and value :
            no = int(no)
            value= int(value)
            ss= Site_settings.query.all()
            scr = ss[0].scratch_card_run
            
            for i in range(1, no+1):
                card_num = scr + i
                security_hash =random.randint(10000 , 99999)
                card = Scratch_card(card_number = card_num , security_hash=security_hash , value = value , status = "N" ,user_id = current_user.id)
                db.session.add(card)
                db.session.commit()
                if i == no:
                    ss[0].scratch_card_run = i + scr  
                    db.session.commit()
            flash("Cards generated successfully !!!")
    
    return render_template("admin_wallet_recharge.html" , user = current_user , scr = scr)



@views.route("/admin-utility-view-scratch-cards" , methods = ['GET','POST'] )
@login_required
def admin_utility_view_scratch_cards():
    scratch_cards = Scratch_card.query.filter_by(status="N").all()
    return render_template("admin_view_scratch_cards.html" , user= current_user , scratch_cards = scratch_cards)



@views.route('/camera', methods=['GET', 'POST'])
def camera():
    return render_template("camera.html" )






def generate_account_details(current_user):
    l = 5-len(str(current_user.id))
    prefix = "0"*l + str(current_user.id)
    no = "AAAAA" + prefix
    current_user.account_number = no
    current_user.type = "C"
    db.session.commit()
    






@views.route('/test-js', methods=['POST'])
def test_js():
    data = json.loads(request.data)
    gps = data["gps"]
    flash(gps)
    return jsonify({})




@views.route("/load-image" ,  methods = ['POST'])
def load_image():
    data = json.loads(request.data)
    img = data['data']
    print(img)
    #img.save("image.png")
    #webbrowser.open_new(str(img))
    return jsonify({})



@views.route("/utility-book-ticket" , methods = ["POST"])
def book_ticket():
    pass