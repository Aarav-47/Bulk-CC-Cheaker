import telebot
import requests
import logging

# Telegram bot token
TELEGRAM_API_TOKEN = '7412108066:AAFN2c9wyHqnWvEcUcSwtQ55olzSwwAfveo'
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Admin user ID
ADMIN_USER_ID = 6746135992

# Replace with your actual CC Checker API details
API_URL = "https://api.stripe.com/v1/tokens"  # Replace with the actual API endpoint
API_KEY = "api.stripe.com"  # Replace with your actual API key

# Logger setup
logging.basicConfig(level=logging.INFO)

# Welcome message with buttons
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    btn_checkcc = telebot.types.InlineKeyboardButton(text="Check Single CC", callback_data="checkcc")
    btn_bulkcheck = telebot.types.InlineKeyboardButton(text="Bulk Check", callback_data="bulkcheck")
    btn_generatecc = telebot.types.InlineKeyboardButton(text="Generate CC", callback_data="generatecc")
    keyboard.add(btn_checkcc, btn_bulkcheck, btn_generatecc)
    
    bot.send_message(message.chat.id, "Welcome to Aarav's Bulk CC Checker! Choose an option:", reply_markup=keyboard)

# Handle button clicks
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.message.chat.id
    
    if call.data == "checkcc":
        bot.send_message(user_id, "Enter the CC details in the format: number expiry(mm/yy) cvv")
        bot.register_next_step_handler(call.message, process_cc_details)
    elif call.data == "bulkcheck":
        if user_id == ADMIN_USER_ID:
            bot.send_message(user_id, "Please upload the .txt file containing CC details (one per line in the format: number expiry(mm/yy) cvv).")
            bot.register_next_step_handler(call.message, process_bulk_file)
        else:
            bot.send_message(user_id, "You are not authorized to use this feature. Please contact admin @AarAv047 for approval.")
    elif call.data == "generatecc":
        cc_number, expiry, cvv = generate_cc()
        bot.send_message(user_id, f"Generated CC:\nNumber: {cc_number}\nExpiry: {expiry}\nCVV: {cvv}")

# Function to check a single credit card
def check_cc(cc_number, expiry, cvv):
    try:
        payload = {
            "cc_number": cc_number,
            "expiry": expiry,
            "cvv": cvv
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_URL, json=payload, headers=headers)
        response_data = response.json()
        return response_data.get("status")  # Adjust based on the API response structure
    except Exception as e:
        return f"Error: {e}"

# Process single CC details
def process_cc_details(message):
    try:
        cc_details = message.text.split()
        if len(cc_details) != 3:
            bot.send_message(message.chat.id, "Invalid format. Please use: number expiry(mm/yy) cvv")
            return
        
        cc_number, expiry, cvv = cc_details
        result = check_cc(cc_number, expiry, cvv)
        
        if result == "approved":
            bot.send_message(message.chat.id, f"✅ Approved: {cc_number}")
        else:
            bot.send_message(message.chat.id, f"❌ Declined: {cc_number}")
    except Exception as e:
        logging.error(f"Error in process_cc_details: {e}")
        bot.send_message(message.chat.id, "An error occurred while checking the card. Please try again.")

# Process bulk file
def process_bulk_file(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_content = downloaded_file.decode('utf-8')

        approved = []
        declined = []

        for line in file_content.splitlines():
            cc_details = line.split()
            if len(cc_details) == 3:
                cc_number, expiry, cvv = cc_details
                result = check_cc(cc_number, expiry, cvv)
                if result == "approved":
                    approved.append(cc_number)
                else:
                    declined.append(cc_number)

        # Build the response message
        approved_list = "\n".join(approved)
        declined_list = "\n".join(declined)
        response_msg = f"✅ Approved Cards:\n{approved_list}\n\n❌ Declined Cards:\n{declined_list}"
        
        bot.send_message(message.chat.id, response_msg)
    else:
        bot.send_message(message.chat.id, "No file uploaded. Please try again.")

# Function to generate a CC (Dummy Example)
def generate_cc():
    # Implement a real CC generation logic or integrate with an API
    return "4111111111111111", "12/25", "123"

# Start the bot
bot.polling()
