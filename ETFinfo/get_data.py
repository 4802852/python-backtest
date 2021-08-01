import csv
import requests
from bs4 import BeautifulSoup


def data_open(filename):
    f = open("python-stockMarket/ETFinfo/" + filename, "r", encoding="UTF-8")
    rdr = csv.reader(f)
    list = []
    for i, line in enumerate(rdr):
        if i == 0:
            continue
        list.append(line)
    return list


def crawling(list):
    new_list = []
    for line in list:
        etf_url = "https://finance.naver.com/item/coinfo.nhn?code=" + str(line[3])
        raw = requests.get(etf_url)
        soup = BeautifulSoup(raw.text, "html.parser")

        first_table = soup.find("iframe", {"id": "coinfo_cp"})
        print(first_table)


list = data_open("data.csv")
crawling(list)
