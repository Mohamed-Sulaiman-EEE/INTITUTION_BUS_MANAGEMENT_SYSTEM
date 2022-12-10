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
  let gps = position.coords.latitude +"," + position.coords.longitude;
  let lat = position.coords.latitude;
  let long = position.coords.longitude;
  fetch("/conductor-utility-refresh-gps", 
  {
    method: "POST",
    body: JSON.stringify({ gps : gps , lat :lat , long:  long }),
  }
  ).then((_res) => {
    window.location.href = "/conductor-current-trip";
  });
}

//-------- REFRESH GPS-----------







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