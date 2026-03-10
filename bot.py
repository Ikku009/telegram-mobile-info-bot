"""
Telegram Mobile Info Bot
Retrieves detailed information about phone numbers
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mobile_info import get_phone_info

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env file")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    welcome_text = """
🤖 Welcome to Mobile Info Bot!

I can retrieve detailed information about phone numbers from around the world.

📞 How to use:
1. Send `/info <phone_number>` - Get detailed phone information
2. Or just send a phone number directly

📱 Examples:
• /info +1234567890
• /info +919876543210
• /info +441234567890

✨ Features:
• ✅ Country & Region detection
• ✅ Carrier information
• ✅ Number type detection
• ✅ International support (250+ countries)

Send /help for more information.
    """
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
📖 Help & Commands

/start - Start the bot
/help - Show this help message
/info <phone_number> - Get phone information

📱 Phone Number Format:
Use international format with country code:
• +1234567890 (recommended)
• Make sure to include the + sign

🌍 Supported Countries:
The bot works with phone numbers from 250+ countries worldwide.

📊 Information Provided:
• Formatted Number
• Country
• Region/State
• Carrier/Provider
• Number Type (Mobile, Fixed Line, etc.)

⚠️ Note:
Phone numbers must be in valid international format with country code.
Some regions may have limited carrier information.
    """
    await update.message.reply_text(help_text)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /info command"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a phone number.\n\n"
            "Usage: /info <phone_number>\n"
            "Example: /info +1234567890"
        )
        return
    
    phone_number = context.args[0]
    await process_phone_number(update, phone_number)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle direct phone number messages"""
    text = update.message.text.strip()
    
    # Check if message looks like a phone number
    if text.startswith('+') or text.isdigit():
        await process_phone_number(update, text)
    else:
        await update.message.reply_text(
            "📱 Please send a valid phone number or use /help for commands."
        )


async def process_phone_number(update: Update, phone_number: str) -> None:
    """Process and display phone information"""
    try:
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        # Get phone information
        info = get_phone_info(phone_number)
        
        if info['success']:
            # Format response
            response = f"""
📱 Phone Information

📍 Formatted: {info['formatted']}
🌍 Country: {info['country']}
🏙️ Region: {info['region']}
📡 Carrier: {info['carrier']}
📞 Type: {info['type']}
✅ Valid: {'Yes' if info['valid'] else 'No'}
            """
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(
                f"❌ Error: {info['error']}\n\n"
                "Please use international format: +1234567890"
            )
    except Exception as e:
        logger.error(f"Error processing phone number: {e}")
        await update.message.reply_text(
            "❌ An error occurred while processing your request.\n"
            "Please try again with a valid phone number."
        )


def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the Bot
    print("🤖 Bot is running... Press Ctrl+C to stop")
    application.run_polling()


if __name__ == '__main__':
    main()
