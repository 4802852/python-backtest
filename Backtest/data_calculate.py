import csv


def percentage(interval):
    f = open(
        "python-stockMarket/Backtest/" + "data_output.csv",
        "r",
        encoding="utf-8",
    )
    rdr = csv.reader(f)
    year_interval = 12 / interval
    data = []
    for line in rdr:
        data.append(line)
    f.close()
    data.pop(0)
    data2 = []
    mean = []
    for i, line in enumerate(data):
        if i % year_interval != 0 and i != len(data) - 1:
            continue
        data2.append(line)
    for i, [date, money] in enumerate(data2):
        if i == 0:
            money_init = int(money)
            date_old = date
            money_old = int(money)
            continue
        rate = round((int(money) - money_old) / money_old * 100, 2)
        mean.append(rate)
        print(f"{date_old} 시작 1년간 수익률 : {rate}%")
        date_old = date
        money_old = int(money)
    rate = round((money_old - money_init) / money_init * 100, 2)
    print(f"기간 중 총 수익률 : {rate}%")
    mean_num = round(sum(mean) / len(mean), 2)
    print(f"기간 중 평균 연간 수익률 : {mean_num}%")


# interval = 1
# percentage(interval)
