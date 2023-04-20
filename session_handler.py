from selenium.webdriver import ChromeOptions, Chrome
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json 
import re
from copy import deepcopy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException



class Session_Handler():
    start_url = 'https://www.linkedin.com/login'


    def init_selenium(self):
        s=Service(ChromeDriverManager().install())
        systm = os.getlogin()
        opt = ChromeOptions()
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        opt.add_argument("--profile-directory=Default")
        opt.add_argument(f"--user-data-dir=C:\\Users\\{systm}\\AppData\\Local\\Google\\Chrome\\User Data\\")
        self.driver = Chrome(service=s, options=opt)


    @staticmethod
    def to_scrapy(cookies_list):
        return {cookie["name"]: cookie["value"] for cookie in cookies_list}


    def save_cookies(self, cookies):
        with open("session.json", 'w') as f:
            json.dump(cookies, f)


    def get_cookies(self):
        self.init_selenium()
        try:
            self.driver.get(self.start_url)
            self.driver.find_element(By.XPATH, "//button[@aria-label='Sign in']")
        except NoSuchElementException:
            cookies= self.to_scrapy(self.driver.get_cookies())
            config = {
                'cookies': deepcopy(cookies),
            }
            self.save_cookies(config)
        except Exception:
            pass
        finally:
            self.driver.close()


session = Session_Handler()
session.get_cookies()




