from loader import bot
from telebot.types import Message, Dict
from telebot import types
from loguru import logger


@logger.catch
def city_choice_keyboard(message: Message, possible_cities: Dict) -> None:
    """
    Функция, которая создает клавиатуру для выбора города из списка найденных городов.
    :param city_list: Список городов.
    :return: Inline клавиатуру.
    """
    keyboards_cities = types.InlineKeyboardMarkup()
    for key, value in possible_cities.items():
        keyboards_cities.add(types.InlineKeyboardButton(text=value["regionNames"],
                                                        callback_data=value["gaiaId"]))
    bot.send_message(message.from_user.id,
                     "Пожалуйста, выберите город", reply_markup=keyboards_cities)


@logger.catch
def photo_selection(message: Message) -> None:
    """Клавиатура для выбора фотографий 'да' или 'нет '
    """
    logger.info('Вывод кнопок о необходимости фотографий пользователю. ')
    keyboard_yes_no = types.InlineKeyboardMarkup()
    keyboard_yes_no.add(types.InlineKeyboardButton(text='ДА', callback_data='yes'))
    keyboard_yes_no.add(types.InlineKeyboardButton(text='НЕТ', callback_data='no'))
    bot.send_message(message.chat.id, "Нужно вывести фотографии?", reply_markup=keyboard_yes_no)


def history_queries(message: Message, records: list) -> None:
    """
    Формируем клавиатуру, чтобы пользователь мог выбрать нужную ему дату и город из истории поиска.
   : param message : Message
    : param records : lict записи из базы данных о том что искал пользователь.
    : return : None
    """
    keyboards_queries = types.InlineKeyboardMarkup()
    for item in records:
        caption = f"Дата запроса: {item[1]}, Введен город: {item[2]}"
        keyboards_queries.add(types.InlineKeyboardButton(text=caption, callback_data=item[1]))
    bot.send_message(message.from_user.id, "Пожалуйста, выберите интересующий вас запрос",
                     reply_markup=keyboards_queries)
