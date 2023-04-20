import argparse
import json
import random
import re
import time
import requests
from constant import *
from copy import deepcopy
from datetime import datetime
from urlextract import URLExtract
from pprint import pprint
from urllib.parse import urlparse
import pytz
from jsonpath_ng import jsonpath, parse
from traceback import print_exc



class Linkedin_Scraper():
    name = 'insta_spider'
    result_counter = 0
    link_extractor = URLExtract()
    email_regx = re.compile('[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', re.IGNORECASE)
    search_endpoint = SEARCH_ENDPOINT
    contacts_endpoint = CONTACTS_ENDPOINT
    profile_endpoint = PROFILE_ENDPOINT
    profile_endpoint_2 = PROFILE_ENDPOINT_2
    sleep_range = (5.0, 10.0)


    def request(self, method, url, **kwargs):
        try:
            self.go_sleep(self.sleep_range)
            response = requests.request(method, url, **kwargs)
        except Exception:
            return None
        else:
            return response


    def load_session(self):
        with open("session.json", 'r') as f:
            config = json.load(f)
            self.session_cookies = config.get("cookies")


    def parse(self, response, keyword, iDOutRequest, minimumNumberofSubscribers, lastUploadCutoffDate, maxResults):
        for element in response.json().get('included', {}):
            try:
                if element.get('template'):
                    username = element.get('navigationUrl').split('?')[0].split('/')[-1]
                    personName = element.get('title').get('text') if element.get('title') else ''
                    followers = self.get_followers(element)
                    if (followers > minimumNumberofSubscribers) and (personName != 'LinkedIn Member'):
                        channelDescription = element.get("summary").get("text") if element.get('summary') else ''
                        emailfromChannelDescription = ", ".join(self.email_regx.findall(channelDescription))
                        location = element.get("secondarySubtitle").get('text') if element.get("secondarySubtitle") else ''
                        channelId = re.search('(?:fsd_profile\:)(.*?)(?:,SEARCH_SRP)', element.get('entityUrn')).group(1)
                        profile_detail = self.get_profile_detail(channelId, username)
                        item = {
                            "keyword": keyword,
                            "iDOutRequest": iDOutRequest,
                            "channelId": channelId,
                            "channelURL": f"https://www.linkedin.com/in/{username}/",
                            "channelName": personName,
                            "channelDescription": channelDescription,
                            "emailfromChannelDescription": emailfromChannelDescription,
                            "location": location,
                            "metric_Subscribers": followers,
                        }
                        item.update(profile_detail)
                        if self.result_counter >= maxResults:
                            self.logger.info(" [+] Limit reached")
                            break 
                        self.result_counter += 1
                        url = self.contacts_endpoint.format(channelId)
                        headers = self.update_headers(username=username)
                        response = self.request('GET', url, headers=headers, cookies=self.session_cookies)
                        contacts = self.parse_contacts(response)
                        item.update(contacts)
                        pprint(item)
            except Exception as e:
                # print_exc()
                pass
        if self.result_counter < maxResults:
            print(" [+] Next Page")
            self.start += 10
            url=self.search_endpoint.format(self.start, keyword)
            headers = self.update_headers(keyword=keyword)
            response = self.request('GET', url, headers=headers, cookies=self.session_cookies)
            self.parse(response, keyword, iDOutRequest, minimumNumberofSubscribers, lastUploadCutoffDate, maxResults)


    def get_followers(self, element):
        try:
            followers_text = element.get("insightsResolutionResults", {})[0].get('simpleInsight', {}).get('title', {}).get("text", '')
        except IndexError:
            return 0
        else:
            followers = self.convert_subscribers(followers_text.split('followers')[0].strip()) if 'followers' in followers_text else 0
            return followers


    def parse_contacts(self, response):
        try:
            person = response.json().get('included', [{}])[0]
            phone = person.get('phoneNumbers')
            email = person.get('emailAddress').get('emailAddress') if person.get('emailAddress') else ''
            website = person.get('websites')[0].get('url') if person.get('websites') else ''
            contactInfo = f'{"".join(phone) if isinstance(phone, list) else phone},{website},{email}'
            return {'contactInfo': contactInfo.strip(','), "emailfromContactInfo": email}
        except Exception as e:
            # print_exc()
            return {}
        


    def get_profile_detail(self, channelId, username):
        try:
            url = self.profile_endpoint.format(channelId)
            headers = self.update_headers(username=username, track=True)
            response = self.request('GET', url, headers=headers, cookies=self.session_cookies)
            about = self.get_value(response, 'about')
            experience = self.get_value(response, ',experience,en')
            education = self.get_value(response, ',education,')
            languages = self.get_value(response, ',languages,')
            # skills
            url = self.profile_endpoint_2.format(channelId)
            response = self.request('GET', url, headers=headers, cookies=self.session_cookies)
            skills = self.get_value(response, 'skills')
            return dict(about=about, experience=experience, education=education, languages=languages, skills=skills)
        except Exception as e:
            # print_exc()
            return {}


    def update_headers(self, keyword=None, username=None, track=None):
        if keyword:
            headers = deepcopy(HEADERS)
            headers['Referer'] = f'https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER'
        elif username:
            headers = deepcopy(CONTACT_HEADERS)
            if track:
                headers['X-Li-Track'] = X_Li_Track
            headers['Referer'] = f'https://www.linkedin.com/in/{username}/overlay/contact-info/'
        headers['Csrf-Token'] = self.session_cookies.get("JSESSIONID").replace('"','')
        return headers


    def get_value(self, response, key):
        if key != 'skills':
            for element in response.json().get('included', {}):
                if key in element.get('entityUrn', '').lower():
                    return ", ".join(self.from_jsonpath_expr(element))
        elif key == 'skills':
            skills = []
            for element in response.json().get('included', {}):
                skills += self.from_jsonpath_expr(element)
            return ", ".join(list(set(skills)))
        return ''


    @staticmethod
    def convert_subscribers(subscribers: str) -> int:
        subscribers = subscribers.lower()
        multiplier = 1
        if subscribers[-1] == 'k':
            multiplier = 1000
            subscribers = subscribers[:-1]
        elif subscribers[-1] == 'm':
            multiplier = 1000000
            subscribers = subscribers[:-1]
        elif subscribers[-1] == 'b':
            multiplier = 1000000000
            subscribers = subscribers[:-1]
        try:
            number = float(subscribers)
        except ValueError:
            return 0
        return int(number * multiplier)


    @staticmethod
    def from_jsonpath_expr(element):
        def process_value(value):
            if isinstance(value, dict):
                nested_result = [process_value(v.value) for v in jsonpath_expr.find(value)]
                return ", ".join(nested_result)
            return value
        jsonpath_expr = parse("$..text")
        result = [process_value(match.value) for match in jsonpath_expr.find(element)]
        return list(filter(None, result))


    @staticmethod
    def to_date(timestamp):
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


    @staticmethod
    def days_between(date1, date2):
        date1_obj = datetime.strptime(date1, '%Y-%m-%d')
        date2_obj = datetime.strptime(date2, '%Y-%m-%d')
        delta = date2_obj - date1_obj
        return delta.days
    

    @staticmethod
    def to_us_eastern(date_str):
        given_date = datetime.strptime(date_str, "%Y-%m-%d")
        us_eastern = pytz.timezone('US/Eastern')
        localized_date = us_eastern.localize(given_date)
        formatted_date = localized_date.strftime('%Y-%m-%d %H:%M:%S %Z')
        return formatted_date


    @staticmethod
    def go_sleep(sleep_range):
        sleep_time = random.uniform(*sleep_range)
        time.sleep(sleep_time)


    @classmethod
    def globalize(cls, keyword):
        for key, value in keyword.items():
            setattr(cls, key, value)


    def crawl(self, keywords):
        self.load_session()
        if self.session_cookies:
            for keyword in keywords:
                self.start = 0
                self.globalize(keyword)
                headers = self.update_headers(keyword=self.keyword)
                url=self.search_endpoint.format(self.start, self.keyword)
                response = self.request('GET', url, headers=headers, cookies=self.session_cookies)
                if response:
                    self.parse(response, **keyword)


crawler = Linkedin_Scraper()
crawler.crawl(keywords=[{"keyword":'ahmad',"iDOutRequest":1, "minimumNumberofSubscribers":-1, "lastUploadCutoffDate":10, 'maxResults':10}])