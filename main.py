from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler, PreCheckoutQueryHandler
import logging
import sqlite3
import getpass

# Ask for bot token (masked input)
BOT_TOKEN = getpass.getpass("Enter your Telegram Bot Token: ")
PAYMENT_PROVIDER_TOKEN = "YOUR_STRIPE_PROVIDER_TOKEN"

print("Telegram API token received. Starting bot...")

# Database Setup
conn = sqlite3.connect("registrations.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    team TEXT,
    registration_id TEXT,
    paid BOOLEAN
)
""")
conn.commit()

# States
NAME, TEAM, REG_ID, PAYMENT = range(4)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Use /register to sign up for the event.")

def register(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter your full name:")
    return NAME

def name(update: Update, context: CallbackContext):
    context.user_data['name'] = update.message.text
    update.message.reply_text("Enter your team name:")
    return TEAM

def team(update: Update, context: CallbackContext):
    context.user_data['team'] = update.message.text
    update.message.reply_text("Enter your ID at https://rating.chgk.info :")
    return REG_ID

def reg_id(update: Update, context: CallbackContext):
    context.user_data['registration_id'] = update.message.text
    update.message.reply_text("Click the button below to pay €5 in advance.",
                              reply_markup=InlineKeyboardMarkup([
                                  [InlineKeyboardButton("Pay Now", pay=True)]
                              ]))
    return PAYMENT

def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    if query.invoice_payload == "Event Registration":
        query.answer(ok=True)
    else:
        query.answer(ok=False, error_message="Something went wrong. Try again!")

def successful_payment(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    c.execute("INSERT INTO registrations (user_id, name, team, registration_id, paid) VALUES (?, ?, ?, ?, 1)",
              (user_id, context.user_data['name'], context.user_data['team'], context.user_data['registration_id']))
    conn.commit()
    update.message.reply_text("Payment successful! You are registered.")
    return ConversationHandler.END

def list_registrations(update: Update, context: CallbackContext):
    if update.message.from_user.id != YOUR_ADMIN_ID:
        update.message.reply_text("You are not authorized to access this.")
        return
    c.execute("SELECT name, team, registration_id FROM registrations WHERE paid = 1")
    rows = c.fetchall()
    msg = "Registered Users:\n" + "\n".join([f"{r[0]} ({r[1]}) - ID: {r[2]}" for r in rows])
    update.message.reply_text(msg)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            TEAM: [MessageHandler(Filters.text & ~Filters.command, team)],
            REG_ID: [MessageHandler(Filters.text & ~Filters.command, reg_id)],
            PAYMENT: [PreCheckoutQueryHandler(precheckout_callback),
                      MessageHandler(Filters.successful_payment, successful_payment)],
        },
        fallbacks=[]
    )
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("list_registrations", list_registrations))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
