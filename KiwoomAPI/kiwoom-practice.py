from pykiwoom.kiwoom import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

state = kiwoom.GetConnectState()  # 연결상태 확인
if state == 0:
    print("미연결")
elif state == 1:
    print("연결완료")


# account_num = kiwoom.GetLoginInfo("ACCOUNT_CNT")  # 전체 계좌수
# accounts = kiwoom.GetLoginInfo("ACCNO")  # 전체 계좌 리스트
# user_id = kiwoom.GetLoginInfo("USER_ID")  # 사용자 ID
# user_name = kiwoom.GetLoginInfo("USER_NAME")  # 사용자명
# keyboard = kiwoom.GetLoginInfo("KEY_BSECGB")  # 키보드보안 해지여부
# firewall = kiwoom.GetLoginInfo("FIREW_SECGB")  # 방화벽 설정 여부

# print(account_num)
# print(accounts)
# print(user_id)
# print(user_name)
# print(keyboard)
# print(firewall)


"""
0 코스피 3 ELW 4 뮤푸얼펀드 5 신주인수권 6 리츠 8 ETF 9 하이얼펀드 10 코스닥 30 K-OTC 50 코넥스
"""
# kospi = kiwoom.GetCodeListByMarket("0")
# kosdaq = kiwoom.GetCodeListByMarket("10")
# etf = kiwoom.GetCodeListByMarket("8")

# print(len(kospi), kospi)
# print(len(kosdaq), kosdaq)
# print(len(etf), etf)

# name = kiwoom.GetMasterCodeName("005930")  # 종목명 얻기: 삼성전자
# print(name)


# # 주식계좌
# accounts = kiwoom.GetLoginInfo("ACCNO")
# stock_account = accounts[0]

# # 삼성전자, 10주, 시장가주문 매수
# kiwoom.SendOrder("시장가매수", "0101", stock_account, 1, "005930", 10, 0, "03", "")

# # 주식계좌
# accounts = kiwoom.GetLoginInfo("ACCNO")
# stock_account = accounts[0]

# # 삼성전자, 10주, 시장가주문 매도
# kiwoom.SendOrder("시장가매도", "0101", stock_account, 2, "005930", 10, 0, "03", "")


df = kiwoom.block_request("opt10001", 종목코드="005930", output="주식기본정보", next=0)
for lin in df:
    print(lin)
