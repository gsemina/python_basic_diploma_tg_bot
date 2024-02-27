from telebot.types import Message
from loader import bot
from config_data.config import DEFAULT_COMMANDS



@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    bot.reply_to(message, f"Привет, {message.from_user.full_name}! ")
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))


