import scrapy
from scrapy.crawler import CrawlerProcess
import json
import re
from constant import HEADERS, CONTACT_HEADERS, X_Li_Track
from scrapy import signals
from copy import deepcopy
from datetime import datetime
from urlextract import URLExtract
from pprint import pprint
from urllib.parse import urlparse
import pytz
from jsonpath_ng import jsonpath, parse




class Linkedin_Scraper(scrapy.Spider):
    name = 'insta_spider'
    link_extractor = URLExtract()
    email_regx = re.compile('[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', re.IGNORECASE)
    search_endpoint = 'https://www.linkedin.com:443/voyager/api/graphql?' + 'includeWebMetadata=true&variables=(start:{},origin:SWITCH_SEARCH_VERTICAL,query:(keywords:{},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.0814efb14ee283f3e918ff9608d705fd'
    contacts_endpoint = 'https://www.linkedin.com/voyager/api/graphql?variables=(memberIdentity:{})&&queryId=voyagerIdentityDashProfiles.84cab0be7183be5d0b8e79cd7d5ffb7b'
    profile_endpoint = 'https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{})&&queryId=voyagerIdentityDashProfileCards.b3af3663609a423adeca8d1019a6f19b'
    profile_endpoint_2 = 'https://www.linkedin.com:443/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{},sectionType:skills,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.1a6f6d936902bb480940179c442456b2'
    email_regx = re.compile('[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', re.IGNORECASE)


    def start_requests(self):
        for keyword in self.keywords:
            headers = self.update_headers(keyword=keyword)
            yield scrapy.Request(url=self.search_endpoint.format(0, keyword.get('keyword')), headers=headers, cookies=self.session_cookies, callback=self.parse, cb_kwargs=dict(keyword=keyword), dont_filter=True)

            
    async def parse(self, response, keyword):
        for element in response.json().get('included', {}):
            if element.get('template'):
                username = element.get('navigationUrl').split('?')[0].split('/')[-1]
                personName = element.get('title').get('text') if element.get('title') else ''
                followers = self.get_followers(element)
                if followers > keyword.get('minimumNumberofSubscribers'):
                    channelDescription = element.get("summary").get("text") if element.get('summary') else ''
                    emailfromChannelDescription = ", ".join(self.email_regx.findall(channelDescription))
                    location = element.get("secondarySubtitle").get('text') if element.get("secondarySubtitle") else ''
                    channelId = re.search('(?:fsd_profile\:)(.*?)(?:,SEARCH_SRP)', element.get('entityUrn')).group(1)
                    profile_detail = await self.get_profile_detail(channelId, username)
                    item = {
                        "keyword": keyword.get('keyword'),
                        "iDOutRequest": keyword.get('iDOutRequest'),
                        "channelId": channelId,
                        "channelURL": f"https://www.linkedin.com/in/{username}/",
                        "channelName": personName,
                        "channelDescription": channelDescription,
                        "emailfromChannelDescription": emailfromChannelDescription,
                        "location": location,
                        "metric_Subscribers": followers,
                    }
                    item.update(profile_detail)
                    yield item
# 

    async def get_profile_detail(self, channelId, username):
        url = self.profile_endpoint.format(channelId)
        headers = self.update_headers(username=username, track=True)
        response = await self.crawler.engine.download(scrapy.Request(url, headers=headers, cookies=self.session_cookies, dont_filter=True))
        about = self.get_value(response, 'about')
        experience = self.get_value(response, ',experience,en')
        education = self.get_value(response, ',education,')
        languages = self.get_value(response, ',languages,')
        # skills
        response = await self.crawler.engine.download(scrapy.Request(self.profile_endpoint_2.format(channelId), headers=headers, cookies=self.session_cookies, dont_filter=True))
        skills = self.get_value(response, 'skills')
        return dict(about=about, experience=experience, education=education, languages=languages, skills=skills)
    

    def update_headers(self, keyword=None, username=None, track=None):
        if keyword:
            headers = deepcopy(HEADERS)
            headers['Referer'] = f'https://www.linkedin.com/search/results/people/?keywords={keyword.get("keyword")}&origin=GLOBAL_SEARCH_HEADER'
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


    def get_followers(self, element):
        try:
            followers_text = element.get("insightsResolutionResults", {})[0].get('simpleInsight', {}).get('title', {}).get("text", '')
        except IndexError:
            return 0
        else:
            followers = self.convert_subscribers(followers_text.split('followers')[0].strip()) if 'followers' in followers_text else 0
            return followers

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


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Linkedin_Scraper, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider
    

    def spider_opened(self, spider):
        with open("session.json", 'r') as f:
            config = json.load(f)
            self.session_cookies = config.get("cookies")
            
    

crawler = CrawlerProcess(settings={
    "HTTPCACHE_ENABLED": True,
    "DOWNLOAD_DELAY": 10,
    "CONCURRENT_REQUESTS": 1,
})
crawler.crawl(Linkedin_Scraper, keywords=[{"keyword":'Bill Gates',"iDOutRequest":1, "minimumNumberofSubscribers":5, "lastUploadCutoffDate":100}])
crawler.start()