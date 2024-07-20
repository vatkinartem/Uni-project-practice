import json
import sqlite3
import importFromSiteScript
import asyncio

connection = sqlite3.connect('DataBase.sql')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS prepods (id INTEGER PRIMARY KEY AUTOINCREMENT, fio varchar (50), mail varchar (70), phone varchar (50), auditorium varchar (100), photo varchar (50))')
connection.commit()
cursor.close()
connection.close()

async def searchBySurname(key:str):
    connection = sqlite3.connect('DataBase.sql')
    cursor = connection.cursor()
    cursor.execute(f"SELECT id, fio FROM prepods WHERE fio LIKE ('{key}' || '%')")
    listOfFound = cursor.fetchall()
    cursor.close()
    connection.close()
    return listOfFound

async def searchById(prepod_id:int):
    connection = sqlite3.connect('DataBase.sql')
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM prepods WHERE id = {prepod_id}")
    foundPrepod = cursor.fetchone()
    cursor.close()
    connection.close()
    return foundPrepod

async def searchByListOfIds(prepod_id_list:list):
    connection = sqlite3.connect('DataBase.sql')
    cursor = connection.cursor()
    list_string = '('
    for id in prepod_id_list:
        list_string += f'{id},'
    list_string = list_string.strip(',') + ')'
    cursor.execute(f"SELECT * FROM prepods WHERE id IN {list_string}")
    foundPrepod = cursor.fetchall()
    cursor.close()
    connection.close()
    return foundPrepod

async def  getDataFromSite():
    
    #importFromSiteScript.updateDBFromSite()
    
    with open('data.json', mode='r', encoding='utf-8') as file_object:
        listOfPrepods = json.load(file_object)
    file_object.close()
    return listOfPrepods

async def addLines(listOfPrepods:json.JSONDecoder):
    connection = sqlite3.connect('DataBase.sql')
    cursor = connection.cursor()
    numOfFailed = 0
    for prepod in listOfPrepods["prepod"]:
        if prepod["fio"] != '':
            cursor.execute('''INSERT INTO prepods (fio, mail, phone, auditorium, photo) VALUES ('%s', '%s', '%s', '%s', '%s')''' % (prepod["fio"], prepod["mail"], prepod["phone"] , prepod["auditorium"], prepod["photo"]))
            connection.commit()
        else:
            numOfFailed += 1
    
    print(f'Failed to download {numOfFailed} entries')
    cursor.close()
    connection.close()

async def updateDB():
    connection = sqlite3.connect('DataBase.sql')
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS prepods')
    connection.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS prepods (id INTEGER PRIMARY KEY AUTOINCREMENT, fio varchar (50), mail varchar (70), phone varchar (50), auditorium varchar (100), photo varchar (50))')
    connection.commit()
    cursor.close()
    connection.close()
    
    listOfPrepods = await getDataFromSite()
    await addLines(listOfPrepods)
    
    connection = sqlite3.connect('DataBase.sql')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM prepods")
    listOfFound = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return listOfFound
    