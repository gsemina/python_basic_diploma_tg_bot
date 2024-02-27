from loader import bot
from telebot.types import Message, InputMediaPhoto
from loguru import logger
import database
from states.user_states import UserInputState


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """
        Ответ на команду /history
        Выдает историю запросов данного пользователя.
        : param message : Message
        : return : None
    """
    logger.info('Выбрана команда history!')
    queries = database.search_query_history.read_query(message.chat.id)
    logger.info(f'Получены данные из таблицы query:\n {queries}')
    for item in queries:
        bot.send_message(message.chat.id, f"({item[0]}). "
                                          f"Дата и время: {item[1]}. Вы вводили город: {item[2]}")
    bot.set_state(message.chat.id, UserInputState.history_select)
    bot.send_message(message.from_user.id, "Введите номер интересующего вас варианта: ")


@bot.message_handler(state=UserInputState.history_select)
def input_city(message: Message) -> None:
    """
        Пользователь вводит номер запроса из списка.
        Проверяем корректность ввода. Если не верный ввод (нет номера или не цифра)
        просим повторить ввод.
        Если все корректно - выдача в чат результата.
        : param message : Message
        : return : None
    """
    if message.text.isdigit():
        queries = database.search_query_history.read_query(message.chat.id)
        number_query = []
        photo_need = ''
        for item in queries:
            number_query.append(item[0])
            if int(message.text) == item[0] and item[3] == 'yes':
                photo_need = 'yes'

        if photo_need != 'yes':
            bot.send_message(message.chat.id, 'Пользователь выбирал вариант "без фото"')

        if int(message.text) in number_query:
            history_dict = database.search_query_history.get_history_response(message.text)
            logger.info('Выдаем результаты из базы данных')
            for hotel in history_dict.items():
                medias = []
                caption = f"Название отеля: {hotel[1]['name']}]\n " \
                          f"Адрес отеля: {hotel[1]['address']}" \
                          f"\nСтоимость проживания в " \
                          f"сутки $: {hotel[1]['price']}\n" \
                          f"Расстояние до центра: {hotel[1]['distance']}"
                urls = hotel[1]['images']
                if photo_need == 'yes':
                    for number, url in enumerate(urls):
                        if number == 0:
                            medias.append(InputMediaPhoto(media=url, caption=caption))
                        else:
                            medias.append(InputMediaPhoto(media=url))
                    bot.send_media_group(message.chat.id, medias)
                else:
                    bot.send_message(message.chat.id, caption)
        else:
            bot.send_message(message.chat.id,
                             'Ошибка! Данных нет в списке! Повторите ввод!')
    else:
        bot.send_message(message.chat.id,
                         'Ошибка! Необходимо ввести число из списка! Повторите ввод!')
