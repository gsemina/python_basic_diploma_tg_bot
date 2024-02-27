from telebot.types import Message
import random
from loader import bot


echo_answers = {
    1: 'Не понимаю, что вы хотели этим сказать.',
    2: 'А это здесь при чем?',
    3: 'Это точно сообщение для меня?',
    4: 'Над этим надо серьезно подумать, вернемся к нашему диалогу :)',
    5: 'Давайте лучше вопросы по существу',
    6: 'Я думаю, мы еще вернемся к этой теме',
    7: 'Спасибо за этот вопрос! Я давно его ждал. Но я думаю вы и так знаете ответ',
    8: 'Возможно вы ошиблись, попробуйте еще раз',
    9: 'Что то пошло не так',
    10: 'Сегодня хорошая погода, ой, так мы ж про отели говорили'
}
@bot.message_handler(func=lambda message: True)
def bot_echo(message: Message) -> None:
    if message.text == 'привет':
        bot.reply_to(message, f'Реагируем на слово "привет", '
                              f'И вам {message.from_user.full_name} - Привет!')
    else:
        answer = echo_answers[random.randint(1, len(echo_answers))]
        bot.reply_to(message, answer)
