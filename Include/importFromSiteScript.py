import bs4
from bs4 import BeautifulSoup
import json
import my_suai_auth_data
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time 

def updateDBFromSite():
    prepod_object_list = getDataFromSite()
    formingJSON(prepod_object_list)

def getDataFromSite():
    
    prepod_object_list = dict({"prepod": list([])})
    
    login = my_suai_auth_data.auth_data.login
    password = my_suai_auth_data.auth_data.password
    linkToSite = 'https://pro.guap.ru'
    linkToAuthForm ='https://pro.guap.ru/oauth/login'
    linkToPrepodsList = 'https://pro.guap.ru/inside/student/professors?page=1'

    options = webdriver.ChromeOptions()
    options.add_argument(argument="user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url=linkToAuthForm)
        time.sleep(1)
        driver.get(url=driver.current_url)
        
        email_input = driver.find_element(By.NAME, 'username')
        email_input.clear()
        email_input.send_keys(login)
        time.sleep(0.1)
        
        pass_input = driver.find_element(By.NAME, 'password')
        pass_input.clear()
        pass_input.send_keys(password)
        time.sleep(0.1)
        
        driver.find_element(By.NAME, 'login').click()
        
        
        driver.get(url=linkToPrepodsList)
        time.sleep(0.3)
        
        soup = BeautifulSoup(driver.page_source, features='lxml')
        listOfPageBtns = soup.find_all('a', {'class': 'page-link'})
        numOfPrepodPages = int(listOfPageBtns[4].contents[0])
        
        for page in range(0, numOfPrepodPages):
            soup = BeautifulSoup(driver.page_source, features='lxml')
            PrepodList = soup.find_all('h5', {'class': 'mb-sm-1 fw-semibold'})
            for prepod in PrepodList:
                linkToPrepodInList = linkToSite + prepod.contents[1].get('href')
                driver.get(url=linkToPrepodInList)
                time.sleep(0.01)
                prepod_object = parsePageToPrepodInfo(driver.page_source)
                if prepod_object['prepod'][0]['fio'] != '':
                    prepod_object_list["prepod"].extend(prepod_object["prepod"])
                driver.back()
                time.sleep(0.01)
            
            listOfPageBtns = soup.find_all('a', {'class': 'page-link'})
            linkToNextPage = linkToSite + listOfPageBtns[len(listOfPageBtns)-1].get('href')
            driver.get(url=linkToNextPage)
            time.sleep(0.01)
        
        
    except Exception as exept:
        print(exept)
    finally:
        pass
    return prepod_object_list


def parsePageToPrepodInfo(file:str):
    soup = BeautifulSoup(file, features='lxml')
    
    baseLink = 'https://pro.guap.ru'
    
    (fio, mail, phone, auditorium, photo) = (str(),str(),str(),str(),str())
    
    try:
        fio = soup.find('h3', {'id':'fio'}).contents[0].strip()
        listOf_MPA = soup.find_all('div', {'class':'card shadow-sm'})[1].find_all('div', {'class':'list-group-item'})
        listOf_MPA
        for item in listOf_MPA:
            try:
                for item_field in item.contents:
                    try:
                        if item_field.contents[0] == 'Email':
                            mail = item.contents[5].contents[0].strip(' ').strip('\n')
                        if item_field.contents[0] == 'Аудитория':
                            auditorium = item.contents[5].contents[0].strip(' ').strip('\n')
                        if item_field.contents[0] == 'Телефон':
                            phone = item.contents[5].contents[0].strip(' ').strip('\n')
                    except Exception as exept:
                        pass
            except Exception as exept:
                pass
        
        photo = soup.find('div', {'class':'profile_image_wrap profile_image_lg outline-primary mb-3'}, ).find_all('img', {'class':'profile_image'})[0].get('src')
    except Exception as exept:
        print(exept)
    
    prepod_object = {
        "prepod": 
            [
                {
                    "fio": fio,
                    "mail": mail,
                    "phone": phone,
                    "auditorium": auditorium,
                    "photo": baseLink + photo
                }
            ]
        }
    
    return prepod_object


def formingJSON(listOfPrepods:dict):
    
    with open('data.json', mode='w', encoding='utf-8') as file_json:
        json.dump(listOfPrepods, file_json, ensure_ascii=False, indent=4)
    return None
