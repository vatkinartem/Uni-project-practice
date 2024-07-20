import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
import os
import asyncio
import listOfAdmins
import DB
from enum import Enum
import math

# list of storages, you can use any storage
from telebot.asyncio_storage import StateMemoryStorage
# new feature for states.
from telebot.asyncio_handler_backends import State, StatesGroup

from telebot import types

class CONST_SEARCH(Enum):
    MAX_ON_PAGE = 20

bot = AsyncTeleBot('TOKEN', state_storage=StateMemoryStorage())
pid = os.getpid()
print('Tel-Bot.py running with pid ' + str(pid))

listOfUsersSearch = dict({"users" : {}})

class MyState(StatesGroup):
    surname = State()
    prepodId = State()

class isPrivateChatMsg(telebot.asyncio_filters.SimpleCustomFilter):
    key='is_private_chat_msg'
    @staticmethod
    async def check(message: types.Message):
        result = message.chat.type
        return result == 'private'
    
class isPrivateChatCallback(telebot.asyncio_filters.SimpleCustomFilter):
    key='is_private_chat_callback'
    @staticmethod
    async def check(callback: types.CallbackQuery):
        result = callback.message.chat.type
        return result == 'private'
    
async def isAdmin(id: int):
    return id in listOfAdmins.idOfAdmins



@bot.message_handler(commands=['start'], is_private_chat_msg=True)
async def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    menuBtn = types.InlineKeyboardButton(text='Меню',callback_data='backToMainMenu')
    markup.add(menuBtn)
    await bot.send_message(message.chat.id, 'Приветствуем вас в боте *Найди ФИО преподавателя ГУАП*.\n\
Напишите /help для вывода всех команд.', reply_markup=markup, parse_mode='MARKDOWN')


async def updateDataBase(message):
    await bot.send_message(message.chat.id, 'Обновляем базу данных', parse_mode='MARKDOWN')
    listOfFound = await DB.updateDB()
    
    strResult = 'Список преподавателей (или просто количество, если записей много):\n'
    strListOfFound = ''
    lenght = len(listOfFound)
    if lenght <= 10:
        for i in range(0, lenght):
            strListOfFound += f'{i}\t{listOfFound[i][1]}\n'
    else:
        strListOfFound += f'Всего записей {lenght}'
    
    strResult += strListOfFound
    await bot.send_message(text= strResult, chat_id=message.chat.id, parse_mode='MARKDOWN')


@bot.message_handler(commands=['menu'], is_private_chat_msg=True)
async def menu(message):
    await bot.delete_state(user_id=message.chat.id, chat_id=message.chat.id)
    # main menu interface
    markup = types.InlineKeyboardMarkup(row_width=3)
    helpBtn = types.InlineKeyboardButton(text='Help', callback_data='helpMenu')
    searchBtn = types.InlineKeyboardButton(text='Поиск', callback_data='searchMenu')
    descriptionBtn = types.InlineKeyboardButton(text='Описание', callback_data='descriptionMenu')
    markup.add(helpBtn, descriptionBtn)
    markup.add(searchBtn)
    if await isAdmin(message.chat.id):
        updateDBBtn = types.InlineKeyboardButton(text='Обновить Базу', callback_data='updateDB')
        markup.add(updateDBBtn)
    await bot.send_message(message.chat.id, '*Меню*', reply_markup=markup, parse_mode='MARKDOWN')


@bot.message_handler(commands=['help'], is_private_chat_msg=True)
async def help(message):
    await bot.send_message(chat_id= message.chat.id, text= '*Список доступных команд*\n\
/start - для запуска/перезапуска бота\n\
/help - для вывода команд бота\n\
/description - для вывода описания\n\
/menu - для вывода меню\n\
/search - для поиска ФИО преподавателя по фамилии', parse_mode='MARKDOWN')


@bot.message_handler(commands=['description'], is_private_chat_msg=True)
async def description(message):
    await bot.send_message(message.chat.id, '''*Описание*\nПриветствуем вас в боте *Найди ФИО преподавателя ГУАП*.\n\
У всех, наверняка, бывало такое, что вы, по воле случая забывали _Имя-Отчество_ преподавателя, однако вам в срочном порядке необходимо к нему обратится - \
лабораторную сдать, вопрос задать, курсовую или даже *дипломную работу* защитить. \
Но при это вы не хотите использовать банальные _"Извините..."_ _"Можно вас спросить..."_ _"Я к вам тут защититься пришёл..."_ и прочие трюки.\n\
В таком случаее наш бот специально для *ВАС*. Попимо полных *ФИО*, бот также предоставляет дополнительные, _менее важные_, в сравнении с *ФИО* данные.\n\
Ибо с этим знаниями вы будете управлять своим Будущим.''', parse_mode='MARKDOWN')


@bot.message_handler(commands=['search'], is_private_chat_msg=True)
async def search(message):
    await bot.delete_state(user_id=message.chat.id, chat_id=message.chat.id)
    await bot.send_message(text='*Поиск преподавателя*\nВведите _Фамилию_ преподавателя полность `иванов` или частично `ива`.\n/menu - для прекращения поиска', chat_id=message.chat.id, parse_mode='MARKDOWN')
    await bot.set_state(user_id=message.chat.id, state=MyState.surname, chat_id=message.chat.id)


@bot.callback_query_handler(func=lambda callback: True, is_private_chat_callback=True)
async def callback_message(callback):
    if callback.data == 'backToMainMenu':
        await mainMenu(callback.message)
    elif (callback.data == 'searchLeftBtn') or (callback.data == 'searchRightBtn'):
        await scrollingSearch(callback.message, callback.data)
    elif callback.data == 'searchMenu':
        await searchMenu(callback.message)
    elif callback.data == 'helpMenu':
        await helpMenu(callback.message)
    elif callback.data == 'descriptionMenu':
        await descriptionMenu(callback.message)
    elif callback.data == 'updateDB':
        await updateDataBase(callback.message)


async def helpMenu(message):
    markup = types.InlineKeyboardMarkup()
    mainMenuBtn = types.InlineKeyboardButton(text='Назад в меню', callback_data='backToMainMenu')
    markup.add(mainMenuBtn)
    await bot.edit_message_text(text='*Список доступных команд*\n\
/start - для запуска/перезапуска бота\n\
/help - для вывода команд бота\n\
/description - для вывода описания\n\
/menu - для вывода меню\n\
/search - для поиска ФИО преподавателя по фамилии', chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup, parse_mode='MARKDOWN')


async def descriptionMenu(message):
    markup =types.InlineKeyboardMarkup()
    mainMenuBtn = types.InlineKeyboardButton(text='Назад в меню', callback_data='backToMainMenu')
    markup.add(mainMenuBtn)
    await bot.edit_message_text(text='''*Описание*\nПриветствуем вас в боте *Найди ФИО преподавателя ГУАП*.\n\
У всех, наверняка, бывало такое, что вы, по воле случая забывали _Имя-Отчество_ преподавателя, однако вам в срочном порядке необходимо к нему обратится - \
лабораторную сдать, вопрос задать, курсовую или даже *дипломную работу* защитить. \
Но при это вы не хотите использовать банальные _"Извините..."_ _"Можно вас спросить..."_ _"Я к вам тут защититься пришёл..."_ и прочие трюки.\n\
В таком случаее наш бот специально для *ВАС*. Попимо полных *ФИО*, бот также предоставляет дополнительные, _менее важные_, в сравнении с *ФИО* данные.\n\
Ибо с этим знаниями вы будете управлять своим Будущим.''', chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup, parse_mode='MARKDOWN')


async def mainMenu(message):
    await bot.delete_state(user_id=message.chat.id, chat_id=message.chat.id)
    # main menu interface
    markup = types.InlineKeyboardMarkup(row_width=3)
    helpBtn = types.InlineKeyboardButton(text='Help', callback_data='helpMenu')
    searchBtn = types.InlineKeyboardButton(text='Поиск', callback_data='searchMenu')
    descriptionBtn = types.InlineKeyboardButton(text='Описание', callback_data='descriptionMenu')
    markup.add(helpBtn, descriptionBtn)
    markup.add(searchBtn)
    if await isAdmin(message.chat.id):
        updateDBBtn = types.InlineKeyboardButton(text='Обновить Базу', callback_data='updateDB')
        getIdBtn = types.InlineKeyboardButton(text='Print Id', callback_data='getId')
        markup.add(updateDBBtn)
    await bot.edit_message_text(text='*Меню*', chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup, parse_mode='MARKDOWN')


async def searchMenu(message):
    await bot.delete_state(user_id=message.chat.id, chat_id=message.chat.id)
    markup =types.InlineKeyboardMarkup()
    mainMenuBtn = types.InlineKeyboardButton(text='Назад в меню', callback_data='backToMainMenu')
    markup.add(mainMenuBtn)
    await bot.edit_message_text(text='*Поиск преподавателя*\nВведите _Фамилию_ преподавателя полность `Иванов` или частично `Ива` (или `ива`)\n/menu - для прекращения поиска', chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup, parse_mode='MARKDOWN')
    await bot.set_state(user_id=message.chat.id, state=MyState.surname, chat_id=message.chat.id)


@bot.message_handler(state=MyState.surname, is_private_chat_msg=True, is_digit=False)
async def findPrepodBySurnameInDB(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['surname'] = message.text.strip().lower().capitalize()
    
    global listOfUsersSearch
    listOfFound = await DB.searchBySurname(data['surname'])
    
    numOfIds = len(listOfFound)
    numOfPages = math.ceil(numOfIds / CONST_SEARCH.MAX_ON_PAGE.value)
    curPage = 0
    num_of_id_on_page = 0
    first_id_on_page_id = 0
    last_id_on_page_id = 0
    
    if numOfIds <= 0 :
        curPage = 0
    else:
        curPage = 1
        if curPage < numOfPages:
            num_of_id_on_page = CONST_SEARCH.MAX_ON_PAGE.value 
        else:
            num_of_id_on_page = numOfIds - (CONST_SEARCH.MAX_ON_PAGE.value * (curPage - 1))
            
        first_id_on_page_id = (curPage - 1) * CONST_SEARCH.MAX_ON_PAGE.value
        last_id_on_page_id = first_id_on_page_id + num_of_id_on_page - 1
    
    strResult = 'Список совпадений:\n'
    strListOfFound = ''
    listOfId = []
    for i in range(0, num_of_id_on_page, 1):
        strListOfFound += f'`{i + first_id_on_page_id + 1}`\t{listOfFound[i][1]}\n'
        listOfId.append(listOfFound[i][0])
    for i in range(last_id_on_page_id + 1, numOfIds, 1):
        listOfId.append(listOfFound[i][0])
    numOfPages = math.ceil(numOfIds / CONST_SEARCH.MAX_ON_PAGE.value)
    
    tempUserData = {f"{str(message.chat.id)}": {'history':listOfId, 'curPage':curPage}}
    listOfUsersSearch["users"].update( tempUserData )
    
    if numOfPages > 1:
        markup = types.InlineKeyboardMarkup(row_width=3)
        searchLeftBtn = types.InlineKeyboardButton(text='◀️', callback_data='searchLeftBtn')
        searchMiddleBtn = types.InlineKeyboardButton(text=f' {curPage} / {numOfPages} ', callback_data='doNothing')
        searchRightBtn = types.InlineKeyboardButton(text='▶️', callback_data='searchRightBtn')
        markup.add(searchLeftBtn, searchMiddleBtn, searchRightBtn)
        
    strResult += strListOfFound
    if numOfIds > CONST_SEARCH.MAX_ON_PAGE.value:
        # Меняем стейт на prepodId (выбор id)
        await bot.set_state(user_id=message.chat.id, state=MyState.prepodId, chat_id=message.chat.id)
        await bot.send_message(text= strResult, chat_id=message.chat.id, parse_mode='MARKDOWN', reply_markup=markup)
        await bot.send_message(text='''Выберите *ID* преподавателя из полученного списка совпадений.\n/menu - закончить выбор. /search - повторить поиск''', chat_id=message.chat.id, parse_mode='MARKDOWN')
    elif (numOfIds <= CONST_SEARCH.MAX_ON_PAGE.value) and (numOfIds > 0):
        # Меняем стейт на prepodId (выбор id)
        await bot.set_state(user_id=message.chat.id, state=MyState.prepodId, chat_id=message.chat.id)
        await bot.send_message(text= strResult, chat_id=message.chat.id, parse_mode='MARKDOWN')
        await bot.send_message(text='''Выберите *ID* преподавателя из полученного списка совпадений.\n/menu - закончить выбор. /search - повторить поиск''', chat_id=message.chat.id, parse_mode='MARKDOWN')
    elif numOfIds == 0:
        strResult += 'Ничего не найдено'
        await bot.send_message(text= strResult, chat_id=message.chat.id, parse_mode='MARKDOWN')
        await bot.send_message(text='''Повторите ввод Фамилии преподавателя\n/menu - закончить выбор. /search - повторить поиск''', chat_id=message.chat.id, parse_mode='MARKDOWN')
    
@bot.message_handler(state=MyState.prepodId, is_private_chat_msg=True, is_digit=True)
async def displayPrepodById(message):
    global listOfUsersSearch
    async with bot.retrieve_data(message.chat.id, message.chat.id) as data:
        data['prepodId'] = message.text.strip()
    
    chosenId = int(data['prepodId']) - 1
    lenOfListOfUsersSearch = len(listOfUsersSearch["users"][f"{str(message.chat.id)}"]["history"])
    
    if (chosenId >= 0) and (chosenId < lenOfListOfUsersSearch):
        await bot.send_message(text=f'''Вы выбрали преподавателя под *ID {chosenId + 1}*\n/menu - закончить выбор. /search - повторить поиск''', chat_id=message.chat.id, parse_mode='MARKDOWN')
        foundPrepod = await DB.searchById(listOfUsersSearch["users"][f"{str(message.chat.id)}"]["history"][chosenId])
        await bot.send_message(text=f'''*ФИО*: {foundPrepod[1]}\n*Почта*: {foundPrepod[2]}\n*Телефон*: {foundPrepod[3]}\n*Аудитория*: {foundPrepod[4]}\n''', chat_id=message.chat.id, parse_mode='MARKDOWN')
        avatar = open(foundPrepod[5], 'rb')
        await bot.send_photo(chat_id=message.chat.id, photo=avatar)
    elif (chosenId < 0) or (chosenId >= lenOfListOfUsersSearch):
        await bot.send_message(text='''Ошибка в выборе индекса. Такого индекса нет.''', chat_id=message.chat.id, parse_mode='MARKDOWN')
    
    await bot.send_message(text='''Можете продолжить выбирать\n/menu - закончить выбор. /search - повторить поиск''', chat_id=message.chat.id, parse_mode='MARKDOWN')


@bot.message_handler(state=MyState.prepodId, is_private_chat_msg=True, is_digit=False)
async def findSurnameInDB(message):
    await bot.send_message(text='''*ID* имеет *целочисленную* положительную форму записи, посему введите *целое* число больше 0.\n/menu - закончить выбор. /search - повторить поиск''', chat_id=message.chat.id, parse_mode='MARKDOWN')

async def scrollingSearch(message, CallBackData):
    global listOfUsersSearch
    if (listOfUsersSearch["users"].get(f'{message.chat.id}') == None):
        await bot.send_message(message.chat.id, text= 'Ваша _история_ поиска пуста.\nЗапустите поиск /search , чтобы её переписать.\n', parse_mode='MARKDOWN')
        return
    numOfIds = len(listOfUsersSearch["users"][f'{message.chat.id}']["history"])
    if (numOfIds == 0):
        await bot.send_message(message.chat.id, text= 'Ваша _история_ поиска пуста.\nЗапустите поиск /search , чтобы её переписать.\n', parse_mode='MARKDOWN')
        return
    curPage = listOfUsersSearch["users"][f'{message.chat.id}']["curPage"]
    numOfPages = math.ceil(numOfIds / CONST_SEARCH.MAX_ON_PAGE.value)
    if numOfPages == 1:
        return
    
    if CallBackData == "searchRightBtn":
        if (curPage + 1) > numOfPages:
            curPage = 1
            listOfUsersSearch["users"][f'{message.chat.id}']["curPage"] = curPage
        else:
            curPage += 1
            listOfUsersSearch["users"][f'{message.chat.id}']["curPage"] = curPage
    elif CallBackData == "searchLeftBtn":
        if (curPage - 1) == 0:
            curPage = numOfPages
            listOfUsersSearch["users"][f'{message.chat.id}']["curPage"] = curPage
        else:
            curPage -= 1
            listOfUsersSearch["users"][f'{message.chat.id}']["curPage"] = curPage
    
    if curPage < numOfPages:
        num_of_id_on_page = CONST_SEARCH.MAX_ON_PAGE.value 
    else:
        num_of_id_on_page = numOfIds - (CONST_SEARCH.MAX_ON_PAGE.value * (curPage - 1))
        
    first_id_on_page_id = (curPage - 1) * CONST_SEARCH.MAX_ON_PAGE.value
    last_id_on_page_id = first_id_on_page_id + num_of_id_on_page - 1
    
    listOfFound = await DB.searchByListOfIds(listOfUsersSearch["users"][f'{message.chat.id}']["history"][first_id_on_page_id:last_id_on_page_id+1])
    
    strResult = 'Список совпадений:\n'
    strListOfFound = ''
    for i in range(0, num_of_id_on_page, 1):
        strListOfFound += f'`{i + first_id_on_page_id + 1}`\t{listOfFound[i][1]}\n'
    strResult += strListOfFound
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    searchLeftBtn = types.InlineKeyboardButton(text='◀️', callback_data='searchLeftBtn')
    searchMiddleBtn = types.InlineKeyboardButton(text=f' {curPage} / {numOfPages} ', callback_data='doNothing')
    searchRightBtn = types.InlineKeyboardButton(text='▶️', callback_data='searchRightBtn')
    markup.add(searchLeftBtn, searchMiddleBtn, searchRightBtn)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=strResult, reply_markup=markup, parse_mode='MARKDOWN', timeout=1)


@bot.message_handler(content_types=['text', 'sticker', 'pinned_message', 'photo', 'audio'], is_private_chat_msg=True)
async def default(message):
    await bot.send_message(message.chat.id, text= 'Моя твоя не понимать\n', parse_mode='MARKDOWN', reply_to_message_id=message.message_id) 

    
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())
bot.add_custom_filter(isPrivateChatMsg())
bot.add_custom_filter(isPrivateChatCallback())

asyncio.run(bot.polling(none_stop=True, timeout=300))

