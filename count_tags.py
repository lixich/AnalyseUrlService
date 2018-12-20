import json
from bs4 import BeautifulSoup
import requests

def make_request(url):
    try:
        r = requests.get(url)
        if r.ok:
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
    except:
        pass
    return ''

def calculate(soup):
    if type(soup) == BeautifulSoup and soup.find('html'):
        res = {}
        tags = set(soup.findAll())
        for tag in tags:
            res[tag.name] = len(soup.findAll(tag.name))
        return res
    else:
        return {}

def get(url):
    html = make_request(url)
    if html:
        return calculate(html)
    else:
        return {}
