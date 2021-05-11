from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, random
from vk_api import VkUpload

import csv
import io
import urllib.request
import pandas as pd

from threading import Thread
import threading
import time
import datetime

import func

mytoken = "176208331f7f19f9f0daad341f1d74c9e929c7470ef4419837e0ee9da7203a67f966c05687bb9d3611291"

vkAuthorize = vk_api.VkApi(token=mytoken)   # Подключаемся к группе
vkAuthorize._auth_token()
api = vkAuthorize.get_api()

session_api = vkAuthorize.get_api()
longpoll = VkLongPoll(vkAuthorize)  # Лонгпулл для ожидания сообщений

# Подгружаем картинки на сервер в вк, можно грузить 7000 картинок за день
image1 = "rec.jpg"
image2 = "pro.jpg"
upload = VkUpload(vkAuthorize)
attachments1 = []
upload_image = upload.photo_messages(photos=image1)[0]
attachments1.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))
attachments2 = []
upload_image = upload.photo_messages(photos=image2)[0]
attachments2.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))


def hi(user_id):
    vkAuthorize.method("messages.send", {"user_id": user_id, "message": "Привет, друг!",
                                "random_id": random.randint(1, 1000)})
    return 1


def recomend(user_id):
    vkAuthorize.method("messages.send", {"user_id": user_id, "message": "У меня есть инфографик, который расскажешь про все особенности сдачи крови:",
                                "random_id": random.randint(1, 1000), 'attachment': ','.join(attachments1)})
    vkAuthorize.method("messages.send", {"user_id": user_id, "message": "Если тебе интересно, я могу также:  Рассказать"
                                                                        " про ПРОТИВОПОКАЗАНИЯ для донора. Помочь, если"
                                                                        " нужна срочная КОНСУЛЬТАЦИЯ.",
                                         "random_id": random.randint(1, 1000)})
    return 1


def contra(user_id):
    vkAuthorize.method("messages.send", {"user_id": user_id, "message": "У меня есть инфографик, который расскажешь про все противопоказания для донора:",
                                "random_id": random.randint(1, 1000), 'attachment': ','.join(attachments2)})
    vkAuthorize.method("messages.send", {"user_id": user_id, "message": "Если тебе интересно, я могу также:  Рассказать"
                                                                        " про РЕКОМЕНДАЦИИ для донора. Помочь, если"
                                                                        " нужна срочная КОНСУЛЬТАЦИЯ.",
                                         "random_id": random.randint(1, 1000)})
    return 1


def default_case(user_id):
    vkAuthorize.method("messages.send", {"user_id": user_id,
                                "message": "К сожалению, я просто программа "
                                           "и могу ответить тебе только на перечисленные ранее сообщения :с",
                                "random_id": random.randint(1, 1000)})
    return 2


def admin(user_id):
    link = 'link'
    waittime_sec = 0
    vkAuthorize.method("messages.send", {"user_id": user_id,
                                         "message": "Введи пароль:",
                                         "random_id": random.randint(1, 1000)})
    while True:
        count_messages = 0  # Принят запрос на рассылку, ждём пароль
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                admin_messages = vkAuthorize.method("messages.getConversations", {"offset": 0, "count": 20,
                                                                            "filter": "unanswered"})
                if admin_messages["count"] >= 1:
                    new_admin_user_id = admin_messages['items'][0]['last_message']['from_id']
                    if (new_admin_user_id == user_id) & (count_messages == 0):

                        text = admin_messages['items'][0]['last_message']['text']
                        if text.lower() == 'донор':
                            vkAuthorize.method("messages.send", {"user_id": user_id,
                                                                 "message": "Верный пароль. Напиши дату и время "
                                                                                "дня донора в формате "
                                                                                "*год, месяц, число, час, минута*. "
                                                                                "К примеру: 2021, 5, 1, 9, 30. "
                                                                                "Что будет означать, 9:30, первого мая,"
                                                                                " 2021 года",
                                                                 "random_id": random.randint(1, 1000)})
                            count_messages = 1  # Пароль проверен, ждём ссылку
                        else:
                            vkAuthorize.method("messages.send", {"user_id": user_id,
                                                                 "message": "Неверный пароль.",
                                                                 "random_id": random.randint(1, 1000)})
                            return
                    else:
                        if (new_admin_user_id == user_id) & (count_messages == 2):
                            text = admin_messages['items'][0]['last_message']['text']
                            delit_vk = 'https://docs.google.com/'
                            check = text.find(delit_vk) # Проверяем формат отправленной ссылки
                            if check != -1:
                                link = text
                                handler(waittime_sec, link, user_id)
                                return
                            else:
                                vkAuthorize.method("messages.send", {"user_id": user_id,
                                                                     "message": "Неверная ссылка.",
                                                                     "random_id": random.randint(1, 1000)})
                                return
                        else:
                            if (new_admin_user_id == user_id) & (count_messages == 1):
                                text = admin_messages['items'][0]['last_message']['text']
                                try:
                                    dt = time.strptime(text, '%Y, %m, %d, %H, %M')  # Проверяем формат указанного времени
                                    time_sec = time.time()
                                    dt_sec = time.mktime(dt)
                                    if dt_sec > time_sec:
                                        waittime_sec = dt_sec - time_sec
                                        vkAuthorize.method("messages.send", {"user_id": user_id,
                                                                             "message": "Запомнил дату и временя. "
                                                                                        "Жду ссылку на excel файл "
                                                                                        "google-form'ы в формате: https://docs.google.com/...",
                                                                             "random_id": random.randint(1, 1000)})

                                        count_messages = 2  # Дата верна, ждём ссылку
                                    else:
                                        vkAuthorize.method("messages.send", {"user_id": user_id,
                                                                             "message": "Указанная дата уже прошла!",
                                                                             "random_id": random.randint(1, 1000)})
                                        return
                                except ValueError:
                                    vkAuthorize.method("messages.send", {"user_id": user_id,
                                                                         "message": "Дата и время введены неверно",
                                                                         "random_id": random.randint(1, 1000)})
                                    return
                            else:
                                if text.lower() == 'рассылка':
                                    vkAuthorize.method("messages.send", {"user_id": user_id,
                                                                         "message": "Уже есть рассылка",
                                                                         "random_id": random.randint(1, 1000)})
                                else:
                                    if admin_messages["count"] >= 1:
                                        answer(admin_messages)


def answer(messages):
    text = messages['items'][0]['last_message']['text']
    user_id = messages['items'][0]['last_message']['from_id']

    if text.lower() == 'привет':
        hi(user_id)
    else:
        if text.lower() == 'рекомендации':
            recomend(user_id)
        else:
            if text.lower() == 'противопоказания':
                contra(user_id)
            else:
                if text.lower() == 'рассылка':
                    test = threading.active_count()
                    if test > 1:
                        vkAuthorize.method("messages.send", {"user_id": user_id,
                                                             "message": "Рассылка уже готова",
                                                             "random_id": random.randint(1, 1000)})
                    else:
                        mailThread1 = Thread(target=admin, args=(user_id,))
                        mailThread1.start()
                        mailThread1.join()
                else:
                    if text.lower() == 'консультация':
                        vkAuthorize.method("messages.send", {"user_id": user_id,
                                                             "message": "Если есть вопросы можешь"
                                                                        " задать их Саше: https://vk.com/id_sanchitos",
                                                             "random_id": random.randint(1, 1000)})
                    else:
                        if text.lower() == 'тест':
                            testl(user_id)
                        else:
                            default_case(user_id)


def handler(waittime_sec, link, user_id):
    # Добавление и редактура ссылки на excel файл googleform
    dobav = '/export?format=csv'
    delit = '/edit#gid'
    #url = 'https://docs.google.com/spreadsheets/d/1_-LjG3VudCecebSTGGaxl1MmHbqpxwLR0ImKnt-1Yrc/edit#gid=1171990370'
    url = link
    try:
        ind = url.rfind(delit)
        url = url[:ind] + dobav
    except Exception:
        print('Ой, ссылка не обработалась')
    print(url)

    # Читаем excel файл
    start_list_id = []  # Храним обработанный id из googleform
    try:
        df = pd.read_csv(url)  # Читаем url
        vkAuthorize.method("messages.send", {"user_id": user_id,
                                             "message": "Ссылка верна. В нужное время все будут оповещены!",
                                             "random_id": random.randint(1, 1000)})
    except Exception:
        vkAuthorize.method("messages.send", {"user_id": user_id,
                                             "message": "Я не смог прочитать ссылку",
                                             "random_id": random.randint(1, 1000)})
    name_column = 'Ссылка на личную страницу Вконтакте'  # Название колонки с id вк
    new_df = df[[name_column]]  # Выберем из датафрейма столбец и сохраним в новый датафрейм
    new_df.to_csv('output.csv', index=False)  # Экспорт в CSV файл
    with open("output.csv", encoding='utf-8') as r_file:
        reader = csv.reader(r_file)
        count = 0
        for row in reader:
            if count == 0:
                print(row[0])
            else:
                stroka = str(row)  # Обрабатываем введенный id-ответ
                delit_vk = 'https://vk.com/'
                check = stroka.find(delit_vk)
                if check != -1:
                    stroka = stroka[check + 15:]
                    delit_vk = '\']'
                    check = stroka.find(delit_vk)
                    stroka = stroka[:check]
                    delit_vk = 'id'
                    check = stroka.find(delit_vk)
                    if check != -1:
                        stroka = stroka[check + 2:]
                        start_list_id.append(stroka)
                    else:
                        start_list_id.append(stroka)

            count = count + 1

    end_list_id = []  # Формируем информацию id о пользователях
    name_list = []  # Имена пользователей
    count = 0
    for val in start_list_id:
        print(val)
        user = api.users.get(user_ids=val)  # Достаём инфу о пользователе по id или по shortname
        userId = user[0]  # элемент из list, который dict
        print(userId)
        end_list_id.append(userId['id'])  # dict['id']
        name_list.append(userId['first_name'])
        print(end_list_id[count])
        count = count + 1

    thread2 = Thread(target=mailing, args=(waittime_sec, end_list_id, name_list,))
    thread2.start()


def mailing(waittime_sec, end_list_id, name_list):
    count = 0

    for val in end_list_id:
        try:
            vkAuthorize.method("messages.send", {"user_id": val, "message": name_list[
                                                                                count] + " ты решил принять участие в донорском движении. Я дам ряд советов которые поспособствуют комфортной сдачи крови.",
                                                 "random_id": random.randint(1, 1000)})
            vkAuthorize.method("messages.send", {"user_id": val,
                                                 "message": "Вот общий перечень рекомендаций. Их придерживаются все доноры: ",
                                                 "random_id": random.randint(1, 1000),
                                                 'attachment': ','.join(attachments1)})
            vkAuthorize.method("messages.send", {"user_id": val,
                                                 "message": func.message1,
                                                 "random_id": random.randint(1, 1000)})
        except Exception:
            print("Id: ", val, " - ", name_list[count], " не разрешил(a) рассылку")
        count = count + 1

    delta = round(waittime_sec - 86400)    # За сутки
    print(delta)
    if delta > 0:
        rasmes(delta, end_list_id, func.message2)

    delta = round(waittime_sec - 10800)  # За 3 часа
    print(delta)
    if delta > 0:
        rasmes(delta, end_list_id, func.message3)

    delta = round(waittime_sec - 3600)  # За 1 час
    print(delta)
    if delta > 0:
        rasmes(delta, end_list_id, func.message4)

    delta = round(waittime_sec + 7200)  # После двух часов
    rasmes(delta, end_list_id, func.message5)


def rasmes(delta, end_list_id, mes):
    time.sleep(delta)
    for val in end_list_id:
        try:
            vkAuthorize.method("messages.send", {"user_id": val,
                                                 "message": func.mes,
                                                 "random_id": random.randint(1, 1000)})
        except Exception:
            print("Id: ", val, " не разрешил(a) рассылку")



def testl(user_id):
    test1 = threading.enumerate()
    print(test1)
    test = threading.active_count()
    print(test)

    vkAuthorize.method("messages.send", {"user_id": user_id, "message": "Тестим",
                                         "random_id": random.randint(1, 1000)})
    return


def main():
    while True:
        messages = vkAuthorize.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unanswered"})
        if messages["count"] >= 1:
            answer(messages)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                messages = vkAuthorize.method("messages.getConversations", {"offset": 0, "count": 20,
                                                                            "filter": "unanswered"})
                if messages["count"] >= 1:
                    answer(messages)


main()