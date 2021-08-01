from datetime import datetime, timedelta
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta
from data_open import dataOpen
from data_calculate import percentage


def load_data(code, start_date):
    data = fdr.DataReader(code, start_date)
    return data["Close"]


def buy_etf(money, etf_price, last_etf_num, fee_rate, etf_rate):
    etf_num = money * etf_rate // etf_price
    etf_money = etf_num * etf_price
    etf_fee = (last_etf_num - etf_num) * etf_price * fee_rate if last_etf_num > etf_num else 0
    while etf_num > 0 and money < (etf_money + etf_fee):
        etf_num -= 1
        etf_money = etf_num * etf_price
        (last_etf_num - etf_num) * etf_price * fee_rate if last_etf_num > etf_num else 0
    money -= etf_money + etf_fee
    return money, etf_num, etf_money


def backtest(
    money: int,
    fee_rate: float,
    interval: int,
    etf_names: list,
    etf_codes: list,
    etf_rates: list,
    etf_colors: list,
    start_date: str,
):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    etf_datas = []
    for i in range(len(etf_codes)):
        etf_data = load_data(etf_codes[i], start_date)
        etf_datas.append(etf_data)
    df = pd.concat(etf_datas, axis=1, keys=[f"etf{i}" for i in range(1, len(etf_codes) + 1)])
    for i, line in enumerate(df.iloc[0]):
        if pd.isna(line):
            print(f"주어진 ETF 중 {i + 1}번째 ETF의 값이 없습니다. 기간을 확인하세요.")
            return
    new_df = pd.DataFrame()
    while start_date <= df.index[-1]:
        temp_date = start_date
        while temp_date not in df.index and temp_date < df.index[-1]:
            temp_date += timedelta(days=1)
        new_df = new_df.append(df.loc[temp_date])
        start_date += relativedelta(months=interval)

    etf_num = [0] * (len(etf_codes) + 1)
    etf_money = [0] * (len(etf_codes) + 1)

    backtest_df = pd.DataFrame()

    for each in new_df.index:
        for i in range(1, len(etf_codes) + 1):
            etf_price = new_df[f"etf{i}"][each]
            money += etf_num[i] * etf_price
        for i in range(1, len(etf_codes) + 1):
            etf_price = new_df[f"etf{i}"][each]
            money, etf_num_tmp, etf_money_tmp = buy_etf(
                money, etf_price, etf_num[i], fee_rate, etf_rates[i - 1]
            )
            etf_num[i] = etf_num_tmp
            etf_money[i] = etf_money_tmp
        total = money + sum(etf_money)
        backtest_df[each] = [int(total)]

    backtest_df = backtest_df.transpose()
    backtest_df.columns = [
        "backtest",
    ]
    print(backtest_df)
    backtest_df.to_csv("python-stockMarket/Backtest/" + "data_output.csv", mode="w")
    percentage(interval)

    final_df = pd.concat([new_df, backtest_df], axis=1)

    for i in range(1, len(etf_codes) + 1):
        final_df[f"etf{i}"] = final_df[f"etf{i}"] / final_df[f"etf{i}"][0]
    final_df["backtest"] = final_df["backtest"] / final_df["backtest"][0]

    for i in range(1, len(etf_codes) + 1):
        plt.plot(
            final_df[f"etf{i}"].index,
            final_df[f"etf{i}"],
            label=etf_names[i - 1],
            color=etf_colors[i - 1],
        )
    plt.plot(final_df["backtest"].index, final_df["backtest"], label="BACKTEST", color="violet")
    plt.legend(loc="upper left")
    plt.show()


start_date = "2019-01-01"
interval = 3
th, etf_names, etf_codes, etf_rates, etf_colors = dataOpen("data.csv")
if th:
    backtest(10_000_000, 0.002, interval, etf_names, etf_codes, etf_rates, etf_colors, start_date)
else:
    print("주식 비중의 합이 100이 아닙니다. 주식 비중을 확인하세요.")
