import requests
from bs4 import BeautifulSoup


def get_exchange_rate():
    url = 'https://finance.daum.net/exchanges'
    raw = requests.get(url)
    soup = BeautifulSoup(raw.text, 'html.parser')
    rate = soup.find('#boxContents > div.tableB > div.box_contents > div > table > tbody > tr.first > td:nth-child(3) > span')
    print(rate)


get_exchange_rate()