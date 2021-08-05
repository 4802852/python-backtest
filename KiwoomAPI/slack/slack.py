import requests
import json
import os

path = os.path.dirname(os.path.abspath(__file__))


def post_message(token, channel, text):
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        # headers={"Authorization": "Bearer " + token},
        data={"token": token, "channel": channel, "text": text},
    )
    if response.status_code == 200:
        print("sucessfully sent!")
    else:
        print("message fails..")


def to_slack(text):
    secret_file = path + "\secrets.json"
    with open(secret_file) as f:
        secrets = json.loads(f.read())
    myToken = secrets["Token"]
    channel = "#stock"
    post_message(myToken, channel, text)


# to_slack("hello! everybody")
