from SheetHandler import SheetHandler
from ConnectSheet import ConnectSheet
from backend import Backend
import json
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api
import time

# pip3 install --user gspread
# pip3 install --user --upgrade google-api-python-client
# pip3 install --user --upgrade oauth2client

sh = SheetHandler()
ch = ConnectSheet()
bc = Backend()

# TOKEN = '8ad32e817674dece5ea1137f90a6c168bed3b643d467f785d3a50a1474d6ae2cfc1a2144684fa70a60677'  # testing
# group_id = 196530881  # testing
TOKEN = 'efa8f72bc9f5aab07245dbc8eb42f58551b1c56be06fc8ac549a92db582a9dfbd6866d44351067cd08534'  # release
group_id = 198604544  # release

"""
https://console.cloud.google.com/compute/instances?project=euroexpress
tmux ls
tmux a -t 0 (whereas 0 - session id)
:1,%d - to delete all lines in vim
"""

try:
    vk = vk_api.VkApi(token=TOKEN)
    vk._auth_token()
    vk.get_api()
    longpoll = VkBotLongPoll(vk, group_id)
    FOO_MESSAGE = 'HELLO'
except Exception as e:
    print("Kaput " + str(e))
    print("Reconnecting to VK")
    time.sleep(3)

def get_button(label, color):
    return {
        'action': {
            'type': 'text',
            'payload': "{\"button\": \"" + "1" + "\"}",
            'label': label
        },
        'color': color
    }


# --- Keyboards ---

keyboardMain = {
    'one_time': False,
    'buttons': [
        [get_button('Сёдня пары', 'primary'),
         get_button('Завтра пары', 'primary'), get_button('Черта', 'primary')],

        [get_button('К какой нам завтра паре?', 'primary')],

        [get_button('Эта неделя', 'positive'), get_button('Следующая неделя', 'positive')],
        [get_button('Клава иди в сраку', 'negative')]
    ]
}
keyboardMain = json.dumps(keyboardMain, ensure_ascii=False).encode('utf-8')
keyboardMain = str(keyboardMain.decode('utf-8'))

keyboardHide = {
    'one_time': True,
    'buttons': [
        [get_button('Убрать', 'negative')]
    ]
}
keyboardHide = json.dumps(keyboardHide, ensure_ascii=False).encode('utf-8')
keyboardHide = str(keyboardHide.decode('utf-8'))

keyboardThisWeek = {
    'one_time': False,
    'buttons': [
        [get_button('Понедельник пары', 'primary'), get_button('Вторник пары', 'primary'),
         get_button('Среду пары', 'primary')],
        [get_button('Четверг пары', 'primary'), get_button('Пятницу пары', 'primary'),
         get_button('На главную', 'negative')]
    ]
}
keyboardThisWeek = json.dumps(keyboardThisWeek, ensure_ascii=False).encode('utf-8')
keyboardThisWeek = str(keyboardThisWeek.decode('utf-8'))

keyboardNextWeek = {
    'one_time': False,
    'buttons': [
        [get_button('Понедельник на следующей неделе пары', 'primary'),
         get_button('Вторник на следующей неделе пары', 'primary'),
         get_button('Среду на следующей неделе пары', 'primary')],
        [get_button('Четверг на следующей неделе пары', 'primary'),
         get_button('Пятницу на следующей неделе пары', 'primary'), get_button('На главную', 'negative')]
    ]
}
keyboardNextWeek = json.dumps(keyboardNextWeek, ensure_ascii=False).encode('utf-8')
keyboardNextWeek = str(keyboardNextWeek.decode('utf-8'))


# --- Keyboards ---

def send_message(id, text):
    vk.method("messages.send", {"peer_id": id, "message": text, "random_id": 0})


def send_keyboard(id, keyboard):
    vk.method("messages.send", {"peer_id": id, "message": 'Ок', "random_id": 0, 'keyboard': keyboard})


def hahaList(str):
    list = []
    strToAppend = ''
    count = 1

    for char in str:
        if count < 3 or count > 4:
            if count > 4:
                list.append(strToAppend)
                strToAppend = ''
                count = 1
            strToAppend += char
            count += 1
        else:
            if count == 3:
                list.append(strToAppend)
                strToAppend = ''
            strToAppend += char
            count += 1

    return list


while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.object.text.lower()
                id = event.object.peer_id

                if 'на следующей неделе' in message and 'пары' in message:
                    if 'понедельник' in message:
                        send_message(id, bc.byDayNext(0))

                    elif 'вторник' in message:
                        send_message(id, bc.byDayNext(1))

                    elif 'сред' in message:
                        send_message(id, bc.byDayNext(2))

                    elif 'четверг' in message:
                        send_message(id, bc.byDayNext(3))

                    elif 'пятниц' in message:
                        send_message(id, bc.byDayNext(4))

                # --

                elif 'пары' in message and not "на следующей неделе" in message:
                    if 'сёдня' in message or 'сегодня' in message:
                        send_message(id, bc.AllForToday())
                    elif 'завтра' in message:
                        send_message(id, bc.tomorrowClasses())
                    elif 'понедельник' in message:
                        send_message(id, bc.byDay(0))
                    elif 'вторник' in message:
                        send_message(id, bc.byDay(1))
                    elif 'сред' in message:
                        send_message(id, bc.byDay(2))
                    elif 'четверг' in message:
                        send_message(id, bc.byDay(3))
                    elif 'пятниц' in message:
                        send_message(id, bc.byDay(4))

                elif 'черт' in message:
                    send_message(id, 'Сегодня смотрим ' + bc.whatLine())

                # --

                elif 'к какой' in message and 'паре' in message:
                    if 'завтра' in message:
                        send_message(id, bc.getFirstClassTomorrow())

                    elif 'в понедельник' in message:
                        if 'на следующей неделе' in message:
                            send_message(id, bc.getFirstClassByDayNext(0))
                        else:
                            send_message(id, bc.getFirstClassByDay(0))

                    elif 'во вторник' in message:
                        if 'на следующей неделе' in message:
                            send_message(id, bc.getFirstClassByDayNext(1))
                        else:
                            send_message(id, bc.getFirstClassByDay(1))

                    elif 'в среду' in message:
                        if 'на следующей неделе' in message:
                            send_message(id, bc.getFirstClassByDayNext(2))
                        else:
                            send_message(id, bc.getFirstClassByDay(2))

                    elif 'в четверг' in message:
                        if 'на следующей неделе' in message:
                            send_message(id, bc.getFirstClassByDayNext(3))
                        else:
                            send_message(id, bc.getFirstClassByDay(3))

                    elif 'в пятницу' in message:
                        if 'на следующей неделе' in message:
                            send_message(id, bc.getFirstClassByDayNext(4))
                        else:
                            send_message(id, bc.getFirstClassByDay(4))

                    else:
                        send_message(id, bc.getFirstClassToday())

                # --

                elif 'биткоин' in message or 'биток' in message or 'btc' in message:
                    r = requests.get('https://blockchain.info/ticker').json()
                    btc_usd = round(r['USD']['15m'], 0)
                    btc_usd = '{:,}'.format(btc_usd)
                    btc_rub = round(r['RUB']['15m'], 0)
                    result = round(btc_rub * 0.00039600, 0)
                    btc_rub = '{:,}'.format(btc_rub)

                    message_toSend = f'Биткоин стоит ${btc_usd}\nА в рублях - {btc_rub} руб.\n{result} - 1350 = {result - 1350}'
                    send_message(id, message_toSend)

                # --

                elif 'эта неделя' in message:
                    send_keyboard(id, keyboardThisWeek)

                elif 'следующая неделя' in message:
                    send_keyboard(id, keyboardNextWeek)

                elif 'на главную' in message:
                    send_keyboard(id, keyboardMain)

                elif 'покежь клаву' in message:
                    send_keyboard(id, keyboardMain)

                elif 'убери клаву' in message:
                    send_keyboard(id, keyboardHide)

                elif 'клава иди в сраку' in message:
                    send_keyboard(id, keyboardHide)

                # --

                elif ("ссылка" in message or "ссылки" in message):
                    # send_message(id,
                    #              """
                    #              чтобы включить бота, когда он сдох, надо перейти по этой сслыке:
                    #             https://www.pythonanywhere.com/user/Neykuratick/files/home/Neykuratick/main.py?edit
                    #
                    #             логин: neykuratick
                    #             пароль: qq3CRVcwJT8eA.q (он гуглом был сгенерирован)
                    #
                    #             дальше надо нажать на кнопку ">>> Run" в верхнем правом углу и подождать, пока запустится.
                    #             Чтоб было удобней копировать с телефона, я пароль в новом сообщении напишу
                    #
                    #              """)

                    # send_message(id, "qq3CRVcwJT8eA.q")

                    send_message(id, "https://console.cloud.google.com/compute/instances?project=euroexpress")
                elif 'ха' in message:
                    hahasCount = 0
                    hahasList = hahaList(message)

                    for ha in hahasList:
                        if ha == 'ха' or ha == 'хх' or ha == 'ах':
                            hahasCount += 1

                    if 2 < hahasCount <= 4:
                        send_message(id, 'Смешно')

                    elif 4 < hahasCount <= 7:
                        send_message(id, 'ыхвахывхывхыхвыавхавых бляяя')

                    elif hahasCount > 7:
                        send_message(id, '1010101010101110101001 - НАСТОЛЬКО СИЛЬНО Я ОРУ ЫВХАЫХВАХЫВАХЫ')

                elif 'скотина' in message and 'бот' in message:
                    # print(event.object)
                    if event.object.from_id == 232444433:
                        send_message(id, 'прости человек, я буду стараться лучше')
                    else:
                        send_message(id, 'пашол в срачку, кожанная коробка')

                elif " бля" in message or " хуй" in message or " пизд" in message:
                    send_message(id, 'ъуъ, не матерись, сука блеать')

                elif "седня" in message and "пары" in message:
                    send_message(id, 'Кирилл с Мефодием старались, придумывсали букавы а ты вот так вот знчит к ним относишься, да? Напоминаю, что у нас помимо е есть еще ё!!!')

                # if "heroku" in message:
                #     send_message(id, 'Хуёку, блять')

                elif 'за' in message and 'мат' in message and ('извини' in message or 'извени' in message or 'прости' in message or 'сорян' in message):
                    send_message(id, 'Привет, это Замат. Я прощаю тебя, но больше так не будь')

    except Exception as e:
        print("У нас ашыбка " + str(e))
        print("Reconnecting to vk servers")
        time.sleep(3)