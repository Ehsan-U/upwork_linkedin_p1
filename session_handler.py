from playwright.sync_api import sync_playwright
from copy import deepcopy
import re
import json


class Session_Handler():
    start_url = 'https://www.linkedin.com/login'


    def init_playwright(self):
        self.play = sync_playwright().start()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
        viewport = {"width": 1280, "height": 800}
        browser_options = {
            "headless": False,
            "args": [
                "--disable-blink-features=AutomationControlled",  # Disable flag indicating automated browser
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
            "channel": "chrome"
        }
        self.browser = self.play.chromium.launch(**browser_options)
        self.context = self.browser.new_context(user_agent=user_agent, viewport=viewport)
        self.page = self.context.new_page()


    @staticmethod
    def to_scrapy(cookies_list):
        return {cookie["name"]: cookie["value"] for cookie in cookies_list}


    def save_cookies(self, cookies):
        with open("session.json", 'w') as f:
            json.dump(cookies, f)
            print(" [+] session saved!")


    def login(self):
        self.init_playwright()
        try:
            self.page.goto(self.start_url)
            input("Complete the login and press enter:")
        except TimeoutError:
            pass
        else:
            cookies= self.to_scrapy(self.page.context.cookies())
            config = {
                'cookies': deepcopy(cookies),
            }
            self.save_cookies(config)
            self.logged_in = True
        finally:
            self.play.stop()



session = Session_Handler()
session.login()