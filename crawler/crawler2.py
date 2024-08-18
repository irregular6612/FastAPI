import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))
url = 'https://zeus.gist.ac.kr/sys/lecture/lecture_open.do'

#response = requests.get(url)

driver.get(url)

time.sleep(3)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
print(soup)


    




