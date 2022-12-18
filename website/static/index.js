function week_book(){
  
  let week_starting_day = document.getElementById("week_starting_day").value;

  
if (document.getElementById("monday").checked)
{
  monday = 1;
}
if (document.getElementById("tuesday").checked)
{
  tuesday = 2;
}
if (document.getElementById("wednesday").checked)
{
  wednesday = 3;
}
if (document.getElementById("thursday").checked)
{
  thursday = 4;
}
if (document.getElementById("friday").checked)
{
  friday = 5;
}
  fetch("utility/week-book",
  {
    method:"POST",
    body : JSON.stringify({week_starting_date : week_starting_day ,
      monday : monday, tuesday : tuesday ,wednesday:wednesday , thursday:thursday , friday:friday
     })
  }).then((_res) => {
    location.reload()
  });
}





function create_trips(){
  let working_day = document.getElementById("working_day").value
  let route_id = document.getElementById("route_id").value
  let conductor_id =  document.getElementById("conductor_id").value
  let bus_id =  document.getElementById("bus_id").value
  fetch("utility/create-trips",
  {
    method:"POST",
    body : JSON.stringify({working_day : working_day , route_id:route_id, conductor_id:conductor_id , bus_id : bus_id
     })
  })
}


function check_gps()
{
  let lat = document.getElementById("lat").value;
  let long = document.getElementById("long").value;
  let gps = lat + "," + long;
  lat = parseFloat(lat);
  long = parseFloat(long);
  let bus_id = 1;
  fetch("api/update-gps",
  {
    method:"POST",
    body : JSON.stringify({ "bus_id" : bus_id , "lat" : lat , "long"  : long , "gps" : gps })
  })
}






function test_js(trip_id , a) 
{
  console.log(trip_id);
  test = 55;
  fetch("/test-js", 
  {
    method: "POST",
    body: JSON.stringify({ trip_id : trip_id , a : a , test : test  }),
  }
  ).then((_res) => {
    window.location.href = "/conductor-home";
  });;
}


//-------- REFRESH GPS-----------
function refreshGPS() {
  //alert("Refreshing GPS Auto!");
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
    
  } else {
    x.innerHTML = "Geolocation is not supported by this browser.";
  }
  
}

function showPosition(position) {
  let bus_id = 1
  let gps = position.coords.latitude +"," + position.coords.longitude;
  let lat = position.coords.latitude;
  let long = position.coords.longitude;
  fetch("/api/update-gps", 
  {
    method: "POST",
    body: JSON.stringify({ bus_id :bus_id , gps : gps , lat :lat , long:  long }),
  }
  )
}

//-------- REFRESH GPS-----------


function start()
{
  refreshGPS();
  let x = document.getElementById("count")
  x.innerHTML= parseInt(x.innerHTML) + 1
}


function checkRFID()
{
  let rfid = document.getElementById("rfid").value
  let bus_id = document.getElementById("bus_id").value
  fetch("/api/update-rfid", 
  {
    method: "POST",
    body: JSON.stringify({ bus_id :bus_id , rfid:rfid }),
  }
  )

}

function increment_working_day()
{
  fetch("/utility/increment-working-day", 
  {
    method: "POST",
    body: JSON.stringify({}),
  }).then((_res) => {
    window.location.href = "/admin-home";
  });;
}



function newTab(lat , long){
  let base_url = "https://www.google.com/maps/search/?api=1&query=";
  let target_url = base_url + lat + "," + long;
  console.log(target_url);
  //alert(target_url);
  window.open(target_url, "_blank");
}



function book_ticket(){
  
  let account_number = document.getElementById("account_number").value;
  let destination = document.getElementById("to").value;
  let no = document.getElementById("no").value;
  console.log(account_number);
}



function delete_trip()
{
  let trip_id = 55;
  fetch("/utility/delete-trip", 
  {
    method: "POST",
    body: JSON.stringify({ trip_id : trip_id }),
  }
  )

}

function toggle_notification_settings()
{
  let opti = "hii";
  fetch("/utility/toggle-notification-settings",  
  {
    method: "POST",
    body: JSON.stringify({settings:opti}),
  }).then((_res) => {
    window.location.href = "/student-notification-settings";
  });;
  
}



function add_student()
{
  fetch("/admin-home",  
  {
    method: "GET",
    body: JSON.stringify({}),
  }
  )
}