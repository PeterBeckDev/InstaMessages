import os
import time

from instagrapi import Client
import schedule


cl = Client()

# Prompt for login credentials
USERNAME = os.environ.get("IG_USERNAME")
PASSWORD = os.environ.get("IG_PASSWORD")
try:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings("insta_settings.json")  # Save session for next time
except Exception as e:
    print("Login failed:", e)
    exit(1)


def fetch_messages():
    try:
        threads = cl.direct_threads(amount=3)
        for thread in threads:
            print("📩 Thread with:", [u.username for u in thread.users])
            for msg in thread.messages[:3]:
                print(f"{cl.user_info_v1(msg.user_id).username}: {msg.text}")
    except Exception as e:
        print("Error fetching messages:", e)


# Poll every 5 minutes
schedule.every(5).minutes.do(fetch_messages)

print("Insta Bot started...")

while True:
    schedule.run_pending()
    time.sleep(1)