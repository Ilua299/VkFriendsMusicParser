from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pickle
import time
import json

class friendsVkMusicParser():

    def __init__(self,login,password):
        self.login = login
        self.password = password

    def save_cookie(self, driver, path):
        with open(path, 'wb') as filehandler:
            pickle.dump(driver.get_cookies(), filehandler)

    def load_cookie(self, driver, path):
        with open(path, 'rb') as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                driver.add_cookie(cookie)

    def openChrome(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        driver = webdriver.Chrome(service=Service("driver/chromedriver.exe"),options=chrome_options)
        return driver

    def logination(self):
        driver = self.openChrome()
        driver.get("https://vk.com/")
        driver.find_element(By.ID, "index_email").send_keys(self.login)
        driver.find_element(By.ID, "index_pass").send_keys(self.password)
        driver.find_element(By.ID, "index_login_button").click()
        WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID, "l_aud")))
        self.save_cookie(driver,"cookies/cookie.pkl")
        driver.quit()

    def scrollToEnd(self,driver):
        currentHeight = 0
        maxHeight = 1
        while (currentHeight != maxHeight):
            currentHeight = driver.execute_script("return document.documentElement.scrollHeight")
            driver.execute_script("window.scrollTo(0, " + str(currentHeight) + ");")
            time.sleep(0.7)
            maxHeight = driver.execute_script("return document.documentElement.scrollHeight")


    def getMyMusic(self):
        driver = self.openChrome()
        driver.get("https://vk.com/")
        self.load_cookie(driver, "cookies/cookie.pkl")
        driver.get("https://vk.com/")
        current_url = driver.current_url
        driver.find_element(By.ID, "l_aud").click()
        WebDriverWait(driver, 100).until(EC.url_changes(current_url))
        myMusicUrl = driver.current_url
        myMusicUrl +="?section=all"
        driver.get(myMusicUrl)
        time.sleep(1)
        self.scrollToEnd(driver)
        soup = bs(driver.page_source,'html.parser')
        tracks = soup.find('div', class_= 'CatalogBlock__content CatalogBlock__my_audios CatalogBlock__layout--list').findAll('div', class_='audio_row_content _audio_row_content')
        myMusicList= []
        for track in tracks:
            myMusicList.append([track.find('div', class_ = 'audio_row__performer_title').find('a').text, track.find('div', class_ = 'audio_row__title _audio_row__title').find('a').text])
        myMusicDicr = {}
        myMusicDicr["music"] = myMusicList
        with open('files/myMusic.json', 'w', encoding="UTF-16") as file:
            json.dump(myMusicDicr, file, indent=4, ensure_ascii=False)
        driver.quit()

    def getFriendsMusic(self):
        driver = self.openChrome()
        driver.set_page_load_timeout(100)
        driver.get("https://vk.com/")
        self.load_cookie(driver, "cookies/cookie.pkl")
        driver.get("https://vk.com/friends")
        self.scrollToEnd(driver)
        soup = bs(driver.page_source, 'html.parser')
        friends = soup.find('div', id="list_content").findAll('div', class_="friends_user_row friends_user_row--fullRow")
        friends_list = []
        for friend in friends:
            dict = {}
            dict["name"] = friend.find('div', class_="friends_field friends_field_title").find("a").text
            dict["href"] = "https://vk.com" + friend.find('div', class_="friends_field friends_field_title").find("a").get("href")
            friends_list.append(dict)
        for friend in friends_list:
            driver.get(friend["href"])
            current_url = driver.current_url
            #driver.find_element(By.XPATH, "//div[@id='profile_audios']/a").click()
            soup = bs(driver.page_source, 'html.parser')
            audioLink = soup.find('div', id='profile_audios')
            if audioLink:
                driver.get("https://vk.com" + audioLink.find("a").get("href"))
                WebDriverWait(driver, 100).until(EC.url_changes(current_url))
                self.scrollToEnd(driver)
                soup = bs(driver.page_source, 'html.parser')
                tracks = soup.findAll('div', class_='audio_row_content _audio_row_content')
                friend_music_list = []
                for track in tracks:
                    friend_music_list.append([track.find('div', class_='audio_row__performer_title').find('a').text,track.find('div', class_='audio_row__title _audio_row__title').find('a').text])
                friend["music"] = friend_music_list
            else:
                friend["music"] = "closed"


        with open('files/friendsMusic.json', 'w', encoding="UTF-16") as file:
            json.dump(friends_list, file, indent=4, ensure_ascii=False)
        driver.quit()

    def similarMusic(self):
        with open('files/myMusic.json', 'r', encoding="UTF-16") as json_file:
            mySongs = json.loads(json_file.read())
        with open('files/friendsMusic.json', 'r', encoding="UTF-16") as json_file:
            friendsSongs = json.loads(json_file.read())

        similar_music = []
        for friend in friendsSongs:
            dict = {}
            music = []
            dict["name"] = friend["name"]
            for song in friend["music"]:
                if song in mySongs["music"]:
                    music.append(song)
            dict["similar_music"] = music
            similar_music.append(dict)
        with open('files/similarMusic.json', 'w', encoding="UTF-16") as json_file:
            json.dump(similar_music, json_file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    scrapper = friendsVkMusicParser("Log", "Pass")
    scrapper.logination()
    scrapper.getMyMusic()
    scrapper.getFriendsMusic()
    scrapper.similarMusic()

