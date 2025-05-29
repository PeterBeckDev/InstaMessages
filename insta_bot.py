import os
import time
import random
from instagrapi import Client
import schedule
import mysql.connector
from datetime import datetime
from instagrapi.exceptions import ChallengeRequired

cl = Client()
cl.load_settings("insta_settings.json")

USERNAME = os.environ.get("IG_USERNAME")
PASSWORD = os.environ.get("IG_PASSWORD")

db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "instagram_bot")
)
cursor = db.cursor()

#Logging In
try:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings("insta_settings.json")  # Save session for next time
except Exception as e:
    print("Login failed:", e)
    exit(1)

##Database Functions:
def save_user(user):
    cursor.execute("REPLACE INTO users (id, username, full_name) VALUES (%s, %s, %s)",
                   (user.pk, user.username, user.full_name))
    db.commit()

def save_thread(thread):
    cursor.execute("REPLACE INTO threads (id, title, last_updated) VALUES (%s, %s, %s)",
                   (thread.id, thread.title or "", datetime.utcnow()))
    db.commit()

def save_message(msg, thread_id):
    cursor.execute("REPLACE INTO messages (id, thread_id, user_id, text, timestamp) VALUES (%s, %s, %s, %s, %s)",
                   (msg.id, thread_id, msg.user_id, msg.text or "", datetime.utcfromtimestamp(msg.timestamp)))
    db.commit()

def user_exists(user_id):
    cursor.execute("SELECT 1 FROM users WHERE id = %s LIMIT 1", (user_id,))
    return cursor.fetchone() is not None

def fetch_messages():
    ###Need to check if first message is the same as the most recent message in DB
    try:
        # Random sleep before fetching (jitter)
        jitter = random.uniform(2, 6)
        print(f"Waiting {jitter:.2f}s before starting message fetch...")
        time.sleep(jitter)

        initial_thread = cl.direct_threads(amount=1)
        first_message = initial_thread[0]
        x=2
        if x==1: ##change to see if first message is in db already
            print("hi")#stop
        else:
            threads = cl.direct_threads(amount=5)
            for thread in threads:
                if not (user_exists(thread.users[0].pk)):
                    save_user(thread.users[0])
                print("📩 Thread with:", thread.users[0].username)

                # Add small delay between reading each message (anti-bot pacing)
                for msg in thread.messages[:random.randint(2, 4)]:
                    sender = cl.user_info_v1(msg.user_id).username
                    print(f"{sender}: {msg.text}")
                    time.sleep(random.uniform(1.5, 3.0))  # Delay per message

    except Exception as e:
        print("Error fetching messages:", e)

# Randomize the polling interval by rescheduling job every time
def reschedule():
    interval = random.randint(4, 7)  # 4–7 minute intervals
    print(f"📆 Next fetch in {interval} minutes")
    schedule.every(interval).minutes.do(run_fetch_and_reschedule)

def run_fetch_and_reschedule():
    fetch_messages()
    schedule.clear()
    reschedule()

# Kick off first fetch + randomized scheduling
reschedule()

print("🤖 Insta Bot started with randomized timing...")

while True:
    schedule.run_pending()
    time.sleep(1)
