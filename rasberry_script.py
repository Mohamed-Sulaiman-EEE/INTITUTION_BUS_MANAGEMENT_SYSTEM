import requests,json

def main():
    url = "http://127.0.0.1:5000/api/update-gps"
    lat = 55
    long = 55
    bus_id = 1
    data = dict()
    data = {"bus_id" : bus_id, "lat":lat , "long":long}
    reply = requests.post(url=url , json = data )
    return 

main()