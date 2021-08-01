import FinanceDataReader as fdr
from data_open import dataOpen


def load_price(code):
    data = fdr.DataReader(code)
    return data["Close"][-1]


def rebalance(money: int, etf_names: list, etf_codes: list, etf_rates: list):
    etf_price = []
    for code in etf_codes:
        etf_price.append(load_price(code))
    etf_num = [0] * len(etf_codes)
    for i in range(len(etf_codes)):
        money_now = money * etf_rates[i]
        etf_num[i] = money_now // etf_price[i]
        money -= etf_num[i] * etf_price[i]
    for name, num, price in zip(etf_names, etf_num, etf_price):
        print(f"{name} / {price}원 / {int(num)}주 / {int(price * num)}원")
    print(f"리밸런스 후 남은 현금: {money}원")


total_money = int(input("현재 평가 총액: "))
th, etf_names, etf_codes, etf_rates, etf_colors = dataOpen("data.csv")
if th:
    rebalance(total_money, etf_names, etf_codes, etf_rates)
else:
    print("주식 비중의 합이 100이 아닙니다. 주식 비중을 확인하세요.")
