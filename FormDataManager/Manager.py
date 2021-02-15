import requests
import urllib
from bs4 import BeautifulSoup

class Manager:
    def __init__(self, URL, Cookies=None):
        self.URL = URL
        r = requests.get(URL, cookies=Cookies)
        self.Soup = BeautifulSoup(r.text, "html.parser")
        self.Dictionary = {}
        self.Session = requests.Session();

    def FetchParamsByID(self, *params):
        for param in params:
            value = self.Soup.find_all(id=param, limit=1)
            self.Dictionary[param] = value[0].get("value")

    def AddParams(self, key, value):
        self.Dictionary[key] = value

    def Post(self, Cookies=None):
        return self.Session.post(self.URL, cookies=Cookies, data=self.Dictionary, allow_redirects=False)