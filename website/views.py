from email import message
from multiprocessing.sharedctypes import Value
from time import time
from unicodedata import name
from flask import Blueprint, render_template, request, flash, jsonify , redirect, url_for
from flask_login import login_required, current_user
from .models import User
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
def index():
    return render_template("index.html", user=current_user)



#....................................................................................

#.........................STUDENT FUNCTIONS...........................................................

@views.route('/student-home', methods=['GET', 'POST'])
@login_required
def student_home():
    return render_template("student_home.html" , user = current_user)


#.................................CONDUCTOR FUNCTIONS .............................................

@views.route('/conductor-home', methods=['GET', 'POST'])
@login_required
def conductor_home():
    return render_template("conductor_home.html" , user = current_user)

#...................................ADMI FUNCTIONS.................................................

@views.route('/admin-home', methods=['GET', 'POST'])
@login_required
def admin_home():
    return render_template("admin_home.html" , user = current_user )

#....................................................................................



'''



@views.route('/utility-view-route-map/<route>', methods=['GET', 'POST'])
@login_required
def utility_view_route_map(route):
    flash(route)
    return render_template("view_route_map.html" ,user = current_user, route = route)




def generate_account_details(current_user):
    l = 5-len(str(current_user.id))
    prefix = "0"*l + str(current_user.id)
    no = "AAAAA" + prefix
    current_user.account_number = no
    current_user.type = "C"
    db.session.commit()
    



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