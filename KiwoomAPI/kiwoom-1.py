import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime
import time
from config.errCode import *


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle("변동성 돌파전략")
        self.symbol_list = ["229200"]
        self.symbol_dict = {}  # [name, range, target, hold, previous_day_quantity]
        self.bought_list = []
        target_buy_count = len(self.symbol_list) if len(self.symbol_list) < 5 else 5
        self.buy_percent = 1 / target_buy_count

        for symbol in self.symbol_list:
            self.symbol_dict[symbol] = ["", 0, 0, False, 0]

        self.amount = None
        self.account = None
        self.hold = None
        self.on_market = None

        t_now = datetime.datetime.now()
        self.t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        self.t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)

        self.plain_text_edit = QPlainTextEdit(self)
        self.plain_text_edit.setReadOnly(True)
        self.plain_text_edit.move(10, 10)
        self.plain_text_edit.resize(380, 280)

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
        self.account = accounts.split(";")[0]
        self.plain_text_edit.appendPlainText(f"현재 계좌번호: {self.account}")

        self.subscribe_market_time("1")

        for symbol in symbol_list:
            self.request_opt10081(symbol)  # 종목 별 전일 정보 조회
        self.request_opw00004()  # 계좌 평가 현황 조회

        start = 1
        while start:
            t_now = datetime.datetime.now()
            if self.on_market == "0":
                self.plain_text_edit.appendPlainText("장 시작 전입니다.")
            elif self.on_market == ("2" or "4"):
                QCoreApplication.instance().quit()
                print("장 종료되었습니다.")
            elif self.on_market == "3":
                if t_now < self.t_start:
                    if self.bought_list:
                        self.sell_all(self.bought_list)
                elif self.t_start < t_now < self.t_sell:
                    start = 0
            time.sleep(10)

        self.request_opw00001()  # 예수금 조회

        # 주식체결 (실시간)
        for i, symbol in enumerate(self.symbol_list):
            self.subscribe_stock_conclusion(str(i + 1), symbol)

    def GetLoginInfo(self, tag):
        data = self.ocx.dynamicCall("GetLoginInfo(QString)", tag)
        return data

    def _handler_login(self, err_code):
        if err_code == 0:
            self.plain_text_edit.appendPlainText("로그인 완료")
        else:
            if err_code == -106:  # 사용자가 강제로 키움api 프로그램을 종료하였을 경우
                self.plain_text_edit.appendPlainText(errors(err_code)[1])
                sys.exit(0)
            self.plain_text_edit.appendPlainText("로그인에 실패하였습니다.")
            self.plain_text_edit.appendPlainText("에러 내용 :", errors(err_code)[1])
            sys.exit(0)
        self.login_event_loop.exit()

    def _handler_tr_data(self, screen_no, rqname, trcode, record, next):
        if rqname == "예수금조회":
            주문가능금액 = self.GetCommData(trcode, rqname, 0, "주문가능금액")
            주문가능금액 = int(주문가능금액)
            self.amount = int(주문가능금액 * self.buy_percent)
            self.plain_text_edit.appendPlainText(f"주문가능금액: {주문가능금액} 투자금액: {self.amount}")

        elif rqname == "계좌평가현황":
            rows = self.GetRepeatCnt(trcode, rqname)
            for i in range(rows):
                종목코드 = self.GetCommData(trcode, rqname, i, "종목코드")
                보유수량 = self.GetCommData(trcode, rqname, i, "보유수량")
                self.bought_list.append(종목코드)
                self.symbol_dict[종목코드[1:]][4] = int(보유수량)

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
            info = f"{rqname} / 일자: {일자} 고가: {고가} 저가: {저가} 전일변동: {prev_day_range}"
            self.plain_text_edit.appendPlainText(info)

    def GetRepeatCnt(self, trcode, rqname):
        ret = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

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
            if 장운영구분 == "3":
                self.on_market = 장운영구분
            elif 장운영구분 == ("2" or "4"):
                self.on_market = 장운영구분
                QCoreApplication.instance().quit()
                print("메인 윈도우 종료")

        elif real_type == "주식체결":
            t_now = datetime.datetime.now()

            if self.t_sell < t_now:
                if self.bought_list:
                    self.sell_all(self.bought_list)
                time.sleep(10)
                QCoreApplication.instance().quit()
                print("메인 윈도우 종료")
            else:
                # 현재가
                현재가 = self.GetCommRealData(code, 10)
                현재가 = abs(int(현재가))  # +100, -100
                체결시간 = self.GetCommRealData(code, 20)

                # 목표가 계산
                # TR 요청을 통한 전일 range가 계산되었고 아직 당일 목표가가 계산되지 않았다면
                if self.symbol_dict[code][1] and self.symbol_dict[code][2] == 0:
                    시가 = self.GetCommRealData(code, 16)
                    시가 = abs(int(시가))  # +100, -100
                    code_target = int(시가 + (self.range * 0.4))
                    self.symbol_dict[code][2] = code_target
                    self.plain_text_edit.appendPlainText(f"{code} 목표가 계산됨: {code_target}")

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
                    self.SendOrder("매수", "8000", self.account, 1, code, quantity, 0, "03", "")
                    self.plain_text_edit.appendPlainText(
                        f"{self.symbol_dict[code][0]} 시장가 매수 진행 수량: {quantity}"
                    )
                    self.bought_list.append(code)

                # 로깅
                self.plain_text_edit.appendPlainText(
                    f"{self.symbol_dict[code][0]} 시간: {체결시간} 목표가: {self.symbol_dict[code][2]} 현재가: {현재가} 보유여부: {self.symbol_dict[code][3]}"
                )

    def _handler_chejan_data(self, gubun, item_cnt, fid_list):
        if "gubun" == "1":  # 잔고통보
            예수금 = self.GetChejanData("951")
            self.amount = int(예수금)
            self.plain_text_edit.appendPlainText(f"투자금액 업데이트 됨: {self.amount}")

    def sell_all(self, bought_list):
        for symbol in bought_list:
            self.SendOrder(
                "매도",
                "8001",
                self.account,
                2,
                symbol,
                self.symbol_list[symbol][4],
                0,
                "03",
                "",
            )
        self.bought_list = []

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
