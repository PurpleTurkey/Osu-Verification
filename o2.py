import requests

url = "https://osu.ppy.sh/oauth/authorize?client_id=7680"

x = requests.get(url)
print(x)