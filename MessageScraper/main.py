from instagrapi import Client
from getpass import getpass

# Initialize the client
cl = Client()

# Prompt for login credentials
username = input("Instagram username: ")
password = input("Instagram password: ")

# Optional: Save session locally
#cl.load_settings("insta_settings.json")

try:
    cl.login(username, password)
    cl.dump_settings("insta_settings.json")  # Save session for next time
except Exception as e:
    print("Login failed:", e)
    exit(1)

# Fetch recent direct threads (DMs)
threads = cl.direct_threads(amount=5)

# Display message summaries
for thread in threads:
    print("\n📩 Thread with:", [user.username for user in thread.users])
    for message in thread.messages[:5]:  # Show last 5 messages
        sender = cl.user_info_v1(message.user_id).username

        print(f"{sender}: {message.text or '[Non-text message]'}")