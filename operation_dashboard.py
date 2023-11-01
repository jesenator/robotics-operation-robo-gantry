import requests
import json
import re
import sys


base_url = "https://api.notion.com/v1/"

# page_id = "46d83e9fa02c4c7fac84e4b7410e8fbe"
headers = {"Authorization": secret, "Notion-Version": "2022-06-28", "Content-Type": "application/json"}

CODE_BLOCK = "eb65971500e948f6b1343fce4da42a32"


import paho.mqtt.client as mqtt
import time

broker_address = "broker.hivemq.com"
def callback(source, user, message):
    msg = message.payload.decode()
    new_line = msg + ": "
    info = msg.split(" ")
    x = 200 * int(info[0]) / 1023 - 100
    y = 200 * int(info[1]) / 1023 - 100
    thresh_high = 5
    thresh_low = -5
    print(x)
    print(y)
    if x > thresh_high:
        new_line += "going forwards "
    elif x < thresh_low:
        new_line += "going backwards "
    if y > thresh_high:
        new_line += "going right "
    elif y < thresh_low:
        new_line += "going left "

    btns = info[2:]
    if btns[0] == "1":
        new_line += "picking up "
    if btns[1] == "1":
        new_line += "gantry left "
    if btns[2] == "1":
        new_line += "gantry right "
    if btns[3] == "1":
        new_line += "dropping down "
    print(new_line)
    response = requests.get(base_url + "blocks/" + CODE_BLOCK, headers=headers)
    # print(response)
    block = response.json()
    # print(json.dumps(block, indent=4))
    print("==========")
    new_code = block["code"]["rich_text"][0]["text"]["content"] + "\n" + new_line
    block["code"]["rich_text"][0]["text"]["content"] = new_code

    data = {
        "code": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": new_code,
                    }
                }
            ]
        }
    }
    # print(json.dumps(block, indent=4))
    response = requests.patch(base_url + "blocks/" + CODE_BLOCK, json=data, headers=headers)
    # print(response.text)


client = mqtt.Client("operation_dashboard_")
client.on_message = callback
client.connect(broker_address)
client.loop_start()
client.subscribe('chrisrogers/')

time.sleep(10000)
client.loop_stop()
client.disconnect()
sys.exit()
