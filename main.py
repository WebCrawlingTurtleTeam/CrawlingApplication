import pymysql.err
import selenium
from selenium.webdriver.common.by import By

from db_connect import DB
from chrom_driver import Driver

# 1. .env 파일에서 DB 정보 입력
# 2. db.excute("sql문") 하면 sql 가능
# 3. 변수 = db.result() 하면 SELECT문 결과가 버퍼에서 나와서 변수에 드감
# 4. db.commit() 하면 commit ( db.rollback() 가능 )
# 5. 코드 마지막에 db.close()로 통로 닫아줘야 함
try:
    db = DB()
    driver = Driver().driver
    driver.get('https://www.naver.com/')

    # CSS 선택자 사용 - 클래스 이름이 'DailyBoardView-module__weather_temperature___로 시작하는 모든 태그 선택
    span_tags = driver.find_elements(By.CSS_SELECTOR, "[class^='DailyBoardView-module__weather_temperature___']")

    # 모든 태그 출력
    for tag in span_tags:
        print(tag.text)  # 태그의 텍스트 내용 출력

    driver.quit()
    db.close()
except pymysql.err.OperationalError:
    print('DB 연결 설정이 잘못되었습니다. .env 파일을 확인하세요.')
