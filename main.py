import getpass
import sqlite3
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext,
    ConversationHandler, CallbackQueryHandler, PreCheckoutQueryHandler
)
import logging

# Ask for bot token (masked input)
BOT_TOKEN = getpass.getpass("Enter your Telegram Bot Token: ")
print("Bot token received. Starting bot...")

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

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Use /register to sign up for the event.")

async def register(update: Update, context: CallbackContext):
    await update.message.reply_text("Please enter your full name:")
    return NAME

async def name(update: Update, context: CallbackContext):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Enter your team name:")
    return TEAM

async def team(update: Update, context: CallbackContext):
    context.user_data['team'] = update.message.text
    await update.message.reply_text("Enter your registration ID:")
    return REG_ID

async def reg_id(update: Update, context: CallbackContext):
    context.user_data['registration_id'] = update.message.text
    await update.message.reply_text(
        "Click the button below to pay €5.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Pay Now", pay=True)]
        ])
    )
    return PAYMENT

async def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    c.execute("INSERT INTO registrations (user_id, name, team, registration_id, paid) VALUES (?, ?, ?, ?, 1)",
              (user_id, context.user_data['name'], context.user_data['team'], context.user_data['registration_id']))
    conn.commit()
    await update.message.reply_text("Payment successful! You are registered.")
    return ConversationHandler.END

async def list_registrations(update: Update, context: CallbackContext):
    if update.message.from_user.id != YOUR_ADMIN_ID:
        await update.message.reply_text("You are not authorized to access this.")
        return
    c.execute("SELECT name, team, registration_id FROM registrations WHERE paid = 1")
    rows = c.fetchall()
    msg = "Registered Users:\n" + "\n".join([f"{r[0]} ({r[1]}) - ID: {r[2]}" for r in rows])
    await update.message.reply_text(msg)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, team)],
            REG_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_id)],
            PAYMENT: [
                PreCheckoutQueryHandler(precheckout_callback),
                MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)
            ],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("list_registrations", list_registrations))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
