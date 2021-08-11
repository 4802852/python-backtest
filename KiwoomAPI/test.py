# import datetime

symbols = {"123", "234", "345", "456"}
# dict = {}
# for i in range(len(symbols)):
#     dict[symbols[i]] = [0, 0, 0]
# print(dict)
# dict["234"][2] = 1
# print(dict)
# accum = ";".join(symbols) + ";"
# print(accum)
# print(type(accum))

# for symbol in symbols:
#     print(type(symbol))
#     print(symbol)

# t_now = datetime.datetime.now()
# t_now = t_now.replace(hour=20, minute=19)
# today = t_now.strftime("%H%M")
# print(today)

# import os

# path = os.path.dirname(os.path.abspath(__file__))
# print(path)

# symbols = set(symbols)
print(symbols)
symbols.add("123")
print(symbols)
symbols.add("567")
print(symbols)
symbols.add("345")
print(symbols)

for i in symbols:
    print(i)
print(len(symbols))

empty_set = {1, 2}
if empty_set:
    print(1)
else:
    print(0)
