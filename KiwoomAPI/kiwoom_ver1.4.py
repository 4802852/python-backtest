import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime
from config.errCode import *
from slack.slack import *


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 500, 340)
        self.setWindowTitle("변동성 돌파전략")
        self.symbol_list = ["233740", "251340", "122630", "252670"]
        self.symbol_dict = {}  # [name, range, target, hold, quantity, target_quantity]
        self.bought_list = set([])
        self.target_buy_count = len(self.symbol_list) if len(self.symbol_list) < 5 else 5
        self.buy_percent = 1 / self.target_buy_count

        self.overnight = True

        for symbol in self.symbol_list:
            self.symbol_dict[symbol] = ["", 0, 0, False, 0, 0]

        self.amount = None
        self.account = None
        self.on_market = None  # "0": 장 시작 전, "3": 장 중, "2": 장후 동시호가, "4": 장 마감
        self.on_trade = None  # 0: 09:05 전, 1: 09:05~15:15, 2: 15:15 이후

        self.t_now = datetime.datetime.now()
        self.t_9 = self.t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        self.t_start = self.t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        self.t_sell = self.t_now.replace(hour=15, minute=15, second=0, microsecond=0)
        self.t_day = datetime.datetime.today().weekday()

        self.plain_text_edit = QPlainTextEdit(self)
        self.plain_text_edit.setReadOnly(True)
        self.plain_text_edit.move(10, 10)
        self.plain_text_edit.resize(480, 280)

        self.timer = QTimer(self)
        self.timer.start(10000)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timeout_run)

        self.timer_ten = QTimer(self)
        ten_minute = 1000 * 60 * 60
        self.timer_ten.start(10000)
        self.timer_ten.setInterval(ten_minute)
        self.timer_ten.timeout.connect(self.timeout_ten)

        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self._handler_login)
        self.ocx.OnReceiveTrData.connect(self._handler_tr_data)
        self.ocx.OnReceiveRealData.connect(self._handler_real_data)
        self.ocx.OnReceiveChejanData.connect(self._handler_chejan_data)

        self.login_event_loop = QEventLoop()
        self.CommConnect()  # 로그인이 될 때까지 대기
        self.run(self.symbol_list)

    def CommConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        self.login_event_loop.exec_()

    def run(self, symbol_list):
        accounts = self.GetLoginInfo("ACCNO")
        self.account = accounts.split(";")[1]
        self.plain_text_edit.appendPlainText(f"현재 계좌번호: {self.account}")

        self.subscribe_market_time("1")

        self.request_opw00004()  # 계좌 평가 현황 조회
        self.request_opt10075()  # 미체결 조회

        for i, symbol in enumerate(self.symbol_list):
            self.subscribe_stock_conclusion(str(i + 1), symbol)

        for symbol in symbol_list:
            self.request_opt10081(symbol)  # 종목 별 전일 정보 조회
        self.request_opw00001()  # 예수금 조회

        self.btn1 = QPushButton("전량 매도", self)
        self.btn1.move(10, 300)
        self.btn1.clicked.connect(self.btn_clicked)

        today = self.get_today()
        to_slack(today + " 주가 조회 시작")

    def btn_clicked(self):
        if self.on_trade == None:
            self.plain_text_edit.appendPlainText("매도 실패: 현재 장중이 아닙니다.")
        else:
            self.sell_all(self.bought_list)

    def sleep(self, time):
        loop = QEventLoop()
        QTimer.singleShot(time, loop.quit)
        loop.exec_()

    def get_today(self):
        today = self.t_now.strftime("%Y%m%d %H:%M")
        return today

    def timeout_run(self):
        self.t_now = datetime.datetime.now()
        if self.t_day == (5 or 6):
            print("오늘은 ", "토요일" if self.t_day == 5 else "일요일", "입니다.")
            QCoreApplication.instance().quit()
        if self.t_9 < self.t_now < self.t_start:
            self.on_trade = 0
            if self.bought_list:
                self.sell_all(self.bought_list)
                self.plain_text_edit.appendPlainText("전일 보유량 시장가 매도 완료")
        elif self.t_sell < self.t_now < self.t_sell.replace(minute=20):
            self.on_trade = 2
            if self.bought_list and not self.overnight:
                self.sell_all(self.bought_list)
                self.plain_text_edit.appendPlainText("금일 매수량 시장가 매도 완료")
        elif self.t_start < self.t_now < self.t_sell:
            self.on_trade = 1

    def timeout_ten(self):
        if self.on_trade == 1:
            today = self.get_today()
            info = f"{today} 주식 현재가 감시중"
            self.plain_text_edit.appendPlainText(info)
            to_slack(info)  # slack 감시중 확인

    def GetLoginInfo(self, tag):
        data = self.ocx.dynamicCall("GetLoginInfo(QString)", tag)
        return data

    def _handler_login(self, err_code):
        if err_code == 0:
            self.plain_text_edit.appendPlainText("로그인 완료")
        else:
            if err_code == -106:  # 사용자가 강제로 키움api 프로그램을 종료하였을 경우
                print("에러 내용 :", errors(err_code)[1])
                QCoreApplication.instance().quit()
            print("로그인에 실패하였습니다.")
            print("에러 내용 :", errors(err_code)[1])
            QCoreApplication.instance().quit()
        self.login_event_loop.exit()

    def _handler_tr_data(self, screen_no, rqname, trcode, record, next):
        if rqname == "예수금조회":
            주문가능금액 = self.GetCommData(trcode, rqname, 0, "주문가능금액")
            주문가능금액 = int(주문가능금액)
            if self.bought_list:
                self.target_buy_count = (
                    len(self.symbol_list) if len(self.symbol_list) < 5 else 5
                ) - len(self.bought_list)
                self.buy_percent = 1 / self.target_buy_count
            self.amount = int(주문가능금액 * (self.buy_percent))
            self.plain_text_edit.appendPlainText(f"주문가능금액: {주문가능금액} 1종목당 투자금액: {self.amount}")

        elif rqname == "계좌평가현황":
            rows = self.GetRepeatCnt(trcode, rqname)
            for i in range(rows):
                종목코드 = self.GetCommData(trcode, rqname, i, "종목코드")[1:]
                보유수량 = self.GetCommData(trcode, rqname, i, "보유수량")
                self.bought_list.add(종목코드)
                self.symbol_dict[종목코드][3] = True
                self.symbol_dict[종목코드][4] = int(보유수량)

        elif rqname == "실시간미체결요청":
            rows = self.GetRepeatCnt(trcode, rqname)
            for i in range(rows):
                종목코드 = self.GetCommData(trcode, rqname, i, "종목코드")
                종목명 = self.GetCommData(trcode, rqname, i, "종목명")
                주문수량 = self.GetCommData(trcode, rqname, i, "주문수량")
                미체결수량 = self.GetCommData(trcode, rqname, i, "미체결수량")
                self.symbol_dict[종목코드][3] = True
                self.symbol_dict[종목코드][4] = int(주문수량 - 미체결수량)
                self.plain_text_edit.appendPlainText(f"{종목명} {미체결수량}/{주문수량} 미체결")

        elif rqname == "매수":
            pass

        elif rqname == "매도":
            pass

        else:
            t_now = datetime.datetime.now()
            today = t_now.strftime("%Y%m%d")
            일자 = self.GetCommData(trcode, rqname, 0, "일자")

            # 장시작 후 TR 요청하는 경우 0번째 row에 당일 일봉 데이터가 존재함
            if 일자 != today:
                고가 = self.GetCommData(trcode, rqname, 0, "고가")
                저가 = self.GetCommData(trcode, rqname, 0, "저가")
            else:
                일자 = self.GetCommData(trcode, rqname, 1, "일자")
                고가 = self.GetCommData(trcode, rqname, 1, "고가")
                저가 = self.GetCommData(trcode, rqname, 1, "저가")

            prev_day_range = int(고가) - int(저가)
            self.symbol_dict[rqname][1] = prev_day_range
            info = (
                f"{self.symbol_dict[rqname][0]} 일자: {일자} 고가: {고가} 저가: {저가} 전일변동: {prev_day_range}"
            )
            self.plain_text_edit.appendPlainText(info)

    def GetRepeatCnt(self, trcode, rqname):
        ret = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def GetMasterCodeName(self, code):
        name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return name

    def request_opt10081(self, target_code):
        now = datetime.datetime.now()
        today = now.strftime("%Y%m%d")
        self.SetInputValue("종목코드", target_code)
        self.SetInputValue("기준일자", today)
        self.SetInputValue("수정주가구분", 1)
        self.CommRqData(target_code, "opt10081", 0, "9000")

    def request_opw00001(self):
        self.SetInputValue("계좌번호", self.account)
        self.SetInputValue("비밀번호", "")
        self.SetInputValue("비밀번호입력매체구분", "00")
        self.SetInputValue("조회구분", 2)
        self.CommRqData("예수금조회", "opw00001", 0, "9001")

    def request_opw00004(self):
        self.SetInputValue("계좌번호", self.account)
        self.SetInputValue("비밀번호", "")
        self.SetInputValue("상장폐지조회구분", 0)
        self.SetInputValue("비밀번호입력매체구분", "00")
        self.CommRqData("계좌평가현황", "opw00004", 0, "9002")

    def request_opt10075(self):
        self.SetInputValue("계좌번호", self.account)
        self.SetInputValue("전체종목구분", "0")
        self.SetInputValue("매매구분", "2")
        self.SetInputValue("체결구분", "1")
        self.CommRqData("실시간미체결요청", "opt10075", 0, "9003")

    # 실시간 타입을 위한 메소드
    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        self.ocx.dynamicCall(
            "SetRealReg(QString, QString, QString, QString)",
            screen_no,
            code_list,
            fid_list,
            real_type,
        )

    def GetCommRealData(self, code, fid):
        data = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return data

    def DisConnectRealData(self, screen_no):
        self.ocx.dynamicCall("DisConnectRealData(QString)", screen_no)

    # 실시간 이벤트 처리 핸들러
    def _handler_real_data(self, code, real_type, real_data):
        if real_type == "장시작시간":
            장운영구분 = self.GetCommRealData(code, 215)
            if 장운영구분 == ("2" or "4"):
                QCoreApplication.instance().quit()
                print("장 종료 - 프로그램 종료")
            self.on_market = 장운영구분

        elif real_type == "주식체결":
            if self.on_trade == 1:
                if len(self.bought_list) >= self.target_buy_count:
                    # add 목표 수량보다 많을 경우 pass
                    pass
                else:
                    # 현재가
                    현재가 = self.GetCommRealData(code, 10)
                    현재가 = abs(int(현재가))  # +100, -100
                    체결시간 = self.GetCommRealData(code, 20)

                    # 목표가 계산
                    # TR 요청을 통한 전일 range가 계산되었고 아직 당일 목표가가 계산되지 않았다면
                    if self.symbol_dict[code][1] != 0 and self.symbol_dict[code][2] == 0:
                        시가 = self.GetCommRealData(code, 16)
                        시가 = abs(int(시가))  # +100, -100
                        code_target = int(시가 + (self.symbol_dict[code][1] * 0.4))
                        self.symbol_dict[code][2] = code_target
                        self.plain_text_edit.appendPlainText(
                            f"{self.symbol_dict[code][0]} 목표가 계산됨: {code_target}"
                        )

                    # 매수시도
                    # 당일 매수하지 않았고
                    # TR 요청과 Real을 통한 목표가가 설정되었고
                    # TR 요청을 통해 잔고조회가 되었고
                    # 현재가가 목표가가 이상이면
                    if (
                        self.symbol_dict[code][3] is False
                        and self.symbol_dict[code][2]
                        and self.amount is not None
                        and 현재가 >= self.symbol_dict[code][2]
                    ):
                        self.symbol_dict[code][3] = True
                        quantity = int(self.amount / 현재가)
                        self.symbol_dict[code][5] = quantity
                        self.SendOrder("매수", "8000", self.account, 1, code, quantity, 0, "03", "")
                        info = f"{self.symbol_dict[code][0]} 시간: {체결시간} 목표가: {self.symbol_dict[code][2]} 현재가: {현재가} 시장가 매수 진행 수량: {quantity}"
                        self.plain_text_edit.appendPlainText(info)
                        to_slack(info)

    def _handler_chejan_data(self, gubun, item_cnt, fid_list):
        if gubun == "1":  # 잔고통보'
            매수매도구분 = self.GetChejanData("946")
            if 매수매도구분 == "2":  # 매수 잔고 변동
                종목코드 = self.GetChejanData("9001")[1:]
                종목명 = self.GetChejanData("302").strip()
                보유수량 = self.GetChejanData("930")
                매입단가 = self.GetChejanData("931")
                self.symbol_dict[종목코드][4] = int(보유수량)
                self.bought_list.add(종목코드)
                self.plain_text_edit.appendPlainText(f"{종목명} 매입단가: {매입단가} 보유수량: {보유수량}")
                if self.symbol_dict[종목코드][4] == self.symbol_dict[종목코드][5]:
                    to_slack(
                        f"{종목명} 목표가: {self.symbol_dict[종목코드][2]} 매입단가: {매입단가} 수량: {보유수량} 체결 완료"
                    )
            elif 매수매도구분 == "1":  # 매도 잔고 변동
                pass

    def sell_all(self, bought_list):
        today = self.get_today()
        to_slack(today + " 전량 매도 진행")
        for symbol in bought_list:
            self.SendOrder(
                "매도",
                "8001",
                self.account,
                2,
                symbol,
                self.symbol_dict[symbol][4],
                0,
                "03",
                "",
            )
            self.symbol_dict[symbol][3] = False
            self.symbol_dict[symbol][4] = 0
        self.bought_list = set([])
        self.sleep(10000)
        self.request_opw00001()

    def subscribe_stock_conclusion(self, screen_no, symbol):
        self.SetRealReg(screen_no, symbol, "20", 1)
        name = self.GetMasterCodeName(symbol)
        self.symbol_dict[symbol][0] = name
        self.plain_text_edit.appendPlainText(f"{name} 주식체결 구독신청")

    def subscribe_market_time(self, screen_no):
        self.SetRealReg(screen_no, "", "215", 0)
        self.plain_text_edit.appendPlainText("장시작시간 구독신청")

    # TR 요청을 위한 메소드
    def SetInputValue(self, id, value):
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)

    def CommRqData(self, rqname, trcode, next, screen_no):
        self.ocx.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            rqname,
            trcode,
            next,
            screen_no,
        )

    def GetCommData(self, trcode, rqname, index, item):
        data = self.ocx.dynamicCall(
            "GetCommData(QString, QString, int, QString)", trcode, rqname, index, item
        )
        return data.strip()

    def SendOrder(self, rqname, screen, accno, order_type, code, quantity, price, hoga, order_no):
        self.ocx.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            [rqname, screen, accno, order_type, code, quantity, price, hoga, order_no],
        )

    def GetChejanData(self, fid):
        data = self.ocx.dynamicCall("GetChejanData(int)", fid)
        return data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
