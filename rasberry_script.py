import requests,json

def main():
    #url = "http://127.0.0.1:5000/api/update-gps"
    url = "https://mohamedsulaiman.pythonanywhere.com/api/update-gps"
    lat = 55
    long = 55
    bus_id = 1
    gps = "55,55"
    data = dict()
    data = {"bus_id" : bus_id, "lat":lat , "long":long , "gps" : gps}
    reply = requests.post(url=url , json = data )
    print(reply)
    return 


def pico():
    url = "http://127.0.0.1:5000/api/update-rfid-pico"
    bus_id = "1"
    card = "[147, 139, 245, 0]"

    url = "https://mohamedsulaiman.pythonanywhere.com/api/update-rfid-pico"
    data = {"bus_id" : bus_id, "card" : card}
    reply = requests.post(url=url , json = data )
    print(reply.content)
    print("Done")


pico()
    


