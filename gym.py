import requests
import time
import subprocess
from datetime import datetime


with open('token.txt', 'r') as file:
    ACCESS_TOKEN = file.read().strip()

PUSHBULLET_API_URL = "https://api.pushbullet.com/v2/pushes"

def get_pushes():
    headers = {
        "Access-Token": ACCESS_TOKEN
    }
    params = {
        "active": "true"
    }
    response = requests.get(PUSHBULLET_API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json().get("pushes", [])
    else:
        print(f"Error fetching pushes: {response.status_code}")
        return []

def delete_push(push_iden):
    url = f"{PUSHBULLET_API_URL}/{push_iden}"
    headers = {
        "Access-Token": ACCESS_TOKEN
    }
    response = requests.delete(url, headers=headers)
    if response.status_code != 200:
        print(f"Error deleting push {push_iden}: {response.status_code}")
        print(response.text)

def unlock_pc():
    command = r'"C:\Program Files\Cold Turkey\Cold Turkey Blocker.exe" -stop Gym'
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def lock_pc():
    command = r'"C:\Program Files\Cold Turkey\Cold Turkey Blocker.exe" -start Gym'
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def validate_time():
    current_time = datetime.now()
    return (
        current_time.hour == 4 and
        current_time.minute == 0 and
        current_time.second < 6
    )

def locked_mode():
    lock_pc()
    while True:
        pushes = get_pushes()
        for push in pushes:
            title = push.get("title", "")
            body = push.get("body", "")
            print(f"{title} - {body}! Unlocking.")

            if title == "Unlock Signal" and "Bluetooth connected to car" in body:
                unlock_pc()
                delete_push(push["iden"])
                unlocked_mode()
        time.sleep(60)
def unlocked_mode():
    while True:
        if validate_time():
            locked_mode()
        time.sleep(5)

print("Starting up")

unlocked_mode()
