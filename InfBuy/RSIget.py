from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import pandas as pd
import numpy as np


def get_fundamentals(symbol):
    print ('Getting data for ' + symbol)

    url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    html = soup(webpage, "html.parser")

    fundamentals = pd.read_html(str(html), attrs = {'class': 'snapshot-table2'})[0]

    fundamentals.columns = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    colOne = []
    colLength = len(fundamentals)
    for k in np.arange(0, colLength, 2):
        colOne.append(fundamentals[f'{k}'])
    attrs = pd.concat(colOne, ignore_index=True)

    colTwo = []
    colLength = len(fundamentals)
    for k in np.arange(1, colLength, 2):
        colTwo.append(fundamentals[f'{k}'])
    vals = pd.concat(colTwo, ignore_index=True)

    fundamentals = pd.DataFrame()
    fundamentals['Attributes'] = attrs
    fundamentals['Values'] = vals
    fundamentals = fundamentals.set_index('Attributes')
    return fundamentals


def get_rsi(symbol):
    fundamentals = get_fundamentals(symbol)
    return fundamentals.loc['RSI (14)'].Values, fundamentals.loc['Price'].Values


# symbol = 'WEBL'
# rsi = get_rsi(symbol)
    