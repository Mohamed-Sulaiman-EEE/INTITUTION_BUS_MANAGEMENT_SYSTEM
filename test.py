import requests

url = "https://mohamedsulaiman.pythonanywhere.com/"

x = requests.get(url)
print(len(x))