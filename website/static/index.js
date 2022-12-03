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