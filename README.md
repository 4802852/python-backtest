# python-backtest

Coding Study for Stock Trading

1. Kiwoom API 자동 매매 프로그램 (변동성 돌파 전략)

### Kiwoom API 자동매매 프로그램

키움 OpenAPI 구동을 위한 32bit 환경 필요

ver1.0

1. 주어진 종목 코드들 전일 변동폭 정보 획득
1. 변동성 돌파 전략 조건 충족 시 시장가 매수
1. 15시15분 전량 시장가 매도
1. 키움 모의투자에서는 지정가, 시장가 매수매도만 가능하여 시장가로 진행, 차후 실제 매매에서는 최유리FOK 거래 요청하여 매수매도 체결정보 확인하여 보유 여부 갱신 예정

ver1.1

1. QTimer 기능 추가하여 시간 별 행동 세분화
2. 윈도우 스케줄러 등록 대비 알고리즘 추가(주말에 실행 시 자동 종료 등)
3. 목표가 돌파하여 매수 요청되었을 때와 실제로 주문이 체결되었을 때 변수를 분리하여, 지정가 주문하게 되더라도 에러 없음. (매수 요청되어 추가 매수는 이루어지지 않지만 체결되지 않으면 차후 매도 요청도 되지 않음.)
4. 장 중 에러 떴을 때의 조건. 미체결주문이 있는 상태에서 프로그램이 실행되면 미체결 주문을 확인하여 같은 종목이 추가로 주문되지 않도록 구분.

ver1.2

1. 주요 정보 Slack을 통해 공유

ver2.0 (예정)

1. 전일 변동성만 적용함으로써 전일 변동성이 작을 경우, 조금만 상승해도 매수 진행됨. 즉, 충분한 돌파가 이루어지지 않은 매수로 인한 단점 존재. 이를 보정하기 위한 추가 매수 조건 필요. → 최근 일정 기간의 변동성의 평균을 이용하여 k값 보정.
2. 1을 진행하기 위한 최근 변동성 자료 필요 → DB를 구성하여 매일 DB 갱신.
