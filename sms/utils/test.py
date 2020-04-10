import requests

url = "https://nexmo-nexmo-messaging-v1.p.rapidapi.com/number/buy"

payload = ""
headers = {
    'x-rapidapi-host': "nexmo-nexmo-messaging-v1.p.rapidapi.com",
    'x-rapidapi-key': "d17184ba66msha12975be81e29f7p1df72ejsnf392c2aa9daa",
    'content-type': "application/x-www-form-urlencoded"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)