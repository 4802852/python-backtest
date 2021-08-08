import pandas as pd
import datetime
from RSIget import *
from slack.slack import *


def data_open_rsi(filename):
    global path
    today = datetime.datetime.now().strftime("%Y%m%d")
    df = pd.read_csv(path + '/' + filename)
    try:
        df.insert(4,today,0)
    except:
        pass
    for i in range(len(df)):
        df.loc[i, today], df.loc[i, 'price'] = get_rsi(df.loc[i, 'symbol'])
        if float(df.loc[i, 'base_rsi']) >= float(df.loc[i, today]):
            df.loc[i, 'go'] = True
        else:
            df.loc[i, 'go'] = False
    df.to_csv(path + '/' + filename, index=False)
    is_go = df['go'] == True
    to_go = df[is_go]
    go_list = to_go.values.tolist()
    for line in go_list:
        info1 = f'{line[0]} 종목 RSI {line[4]} 기준 RSI {line[3]} 매수 가능'
        info2 = f'현재가 ${line[2]} 40분할 * 2주 최소 투자금액 ${float(line[2]) * 40 * 2} 약 {int(float(line[2]) * 40 * 2 * 1100)}원'
        to_slack(info1)
        to_slack(info2)


path = os.path.dirname(os.path.abspath(__file__))
data_open_rsi('symbol_list.csv')
