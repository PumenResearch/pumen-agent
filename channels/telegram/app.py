"""
Telegram bot integration module for the Pumen Agent.

This module initializes and runs a Telegram bot that interacts with users.
It sets up command and message handlers, allowing the bot to receive input
and eventually pass it to the Pumen Agent's decision engine for processing.
"""

import os
import sys
import logging

try:
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
except ImportError:
    print("Please install python-telegram-bot: pip install python-telegram-bot")
    sys.exit(1)

from channels.telegram.handlers import handle_start_command, handle_text_message, handle_provider_command, handle_model_command, handle_callback_query


def start_telegram_bot() -> None:
    """
    Initialize and start the Telegram bot application.

    This function retrieves the bot token from the environment variables,
    configures the necessary handlers (start command and text messages),
    and starts the polling loop to listen for incoming updates.

    Returns:
        None
    """
    print("Starting Telegram Bot...")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN is not configured in the .env file.")
        print("Please add TELEGRAM_BOT_TOKEN=your_bot_token to .env")
        return

    # Adjust the logging level for the underlying httpx library to reduce noise
    logging.getLogger("httpx").setLevel(logging.INFO)

    from telegram import BotCommand
    
    async def post_init(application) -> None:
        await application.bot.set_my_commands([
            BotCommand("start", "Bắt đầu trò chuyện với Pumen Agent"),
            BotCommand("provider", "Thay đổi nhà cung cấp (VD: /provider openai)"),
            BotCommand("model", "Thay đổi model (VD: /model gpt-4o)")
        ])

    app = ApplicationBuilder().token(token).post_init(post_init).build()

    app.add_handler(CommandHandler("start", handle_start_command))
    app.add_handler(CommandHandler("provider", handle_provider_command))
    app.add_handler(CommandHandler("model", handle_model_command))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print("Telegram bot is running. Press Ctrl+C to stop.")
    app.run_polling()
