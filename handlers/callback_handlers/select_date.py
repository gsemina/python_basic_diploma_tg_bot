from loader import bot
from loguru import logger
import datetime
from states.user_states import UserInputState
from keyboards.calendar.telebot_calendar import CallbackData, Calendar
import handlers.low_high_best
from telebot.types import CallbackQuery
from utils.display_data import display_data


calendar = Calendar()
calendar_callback = CallbackData("calendar", "action", "year", "month", "day")


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix))
def input_date(call: CallbackQuery) -> None:
    """
    Пользователь нажал кнопку на календаре.
    Сравниваем эту дату с текущей. Дата заезда не должна быть ранее, чем сегодня
    Дата выезда не может быть меньше, либо равна, дате заезда.
    : param call : CallbackQuery нажатие на кнопку получения даты в календаре.
    : return : None
    """
    name, action, year, month, day = call.data.split(calendar_callback.sep)
    calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)

    if action == 'DAY':
        logger.info('Пользователь выбрал дату, проверяем ')
        month = edit_month_day(month)
        day = edit_month_day(day)
        select_date = year + month + day

        now_year, now_month, now_day = datetime.datetime.now().strftime('%Y.%m.%d').split('.')
        now = now_year + now_month + now_day

        bot.set_state(call.message.chat.id, UserInputState.input_date)
        with bot.retrieve_data(call.message.chat.id) as data:
            if 'checkInDate' in data:
                checkin = int(data['checkInDate']['year']
                              + data['checkInDate']['month']
                              + data['checkInDate']['day'])
                if int(select_date) > checkin:
                    logger.info('Ввод и сохранение даты выезда.')
                    data['checkOutDate'] = {'day': day, 'month': month, 'year': year}
                    # далее две переменные-заглушки, чтобы не было ошибки при получении словаря с отелями
                    data['start_distance_to_center'] = 0   # начало диапазона расстояния от центра
                    data['end_distance_to_center'] = 0  # конец диапазона расстояния от центра
                    if data['sort'] == 'DISTANCE':
                        bot.set_state(call.message.chat.id, UserInputState.start_distance_to_center)
                        bot.send_message(call.message.chat.id,
                                         'Введите начало диапазона расстояния от центра '
                                                               '(от 0 миль).')
                    else:
                        display_data(call.message, data)
                else:
                    bot.send_message(call.message.chat.id,
                                     'Дата выезда должна быть больше даты заезда! '
                                     'Повторите выбор даты!')
                    handlers.low_high_best.my_calendar(call.message, 'выезда')
            else:
                if int(select_date) >= int(now):
                    logger.info('Ввод и сохранение даты заезда.')
                    data['checkInDate'] = {'day': day, 'month': month, 'year': year}
                    handlers.low_high_best.my_calendar(call.message, 'выезда')
                else:
                    bot.send_message(call.message.chat.id,
                                     'Дата заезда должна быть больше или равна сегодняшней дате! '
                                     'Повторите выбор даты!')
                    handlers.low_high_best.my_calendar(call.message, 'заезда')


def edit_month_day(number: str) -> str:
    """
    Преобразование формата числа месяца или дня из формата 1..9 в формат 01..09
    : param number : str, число месяца или дня
    : return number : str
    """
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if int(number) in numbers:
        number = '0' + number
    return number
