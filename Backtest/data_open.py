import csv


def dataOpen(filename):
    f = open(
        "python-stockMarket/Backtest/" + filename,
        "r",
        encoding="utf-8",
    )
    rdr = csv.reader(f)
    etf_names = []
    etf_codes = []
    etf_rates = []
    etf_colors = []
    for i, line in enumerate(rdr):
        if i == 0:
            continue
        etf_names.append(line[0])
        etf_codes.append(line[1])
        etf_rates.append(int(line[2]))
        etf_colors.append(line[3])
    f.close()
    if sum(etf_rates) != 100:
        return False, etf_names, etf_codes, etf_rates, etf_colors
    else:
        new_etf_rates = []
        mod = 100
        for i in range(len(etf_rates)):
            new_etf_rates.append(etf_rates[i] / mod)
            mod -= etf_rates[i]
        return True, etf_names, etf_codes, new_etf_rates, etf_colors


# dataOpen()
