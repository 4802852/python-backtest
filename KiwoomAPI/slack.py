import requests


def post_message(token, channel, text):
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer " + token},
        data={"channel": channel, "text": text},
    )
    if response.status_code == 200:
        print("sucessfully sent!")
    else:
        print("message fails..")


def to_slack(text):
    myToken = "xoxb-2321365875831-2321373078791-9WfIaobjQVYgRnRjiDLKyLKr"
    channel = "#stock"
    post_message(myToken, channel, text)


# to_slack("hello!")
