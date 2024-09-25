from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 브라우저 옵션 설정 (헤드리스 모드 등)
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음 (옵션)

# ChromeDriver 경로 설정
driver_path = "C:/dev/chromedriver-win64/chromedriver.exe"  # 크롬 드라이버 경로로 변경하세요
service = Service(driver_path)

# WebDriver 초기화
driver = webdriver.Chrome(service=service, options=chrome_options)

# 웹페이지 로드
url = 'https://naver.com'  # 실제 URL로 변경하세요
driver.get(url)

# 명시적 대기 - 최대 10초 동안 'Pagination_text__bLpKw' 클래스가 나타날 때까지 대기
try:
    # CSS 선택자 사용 - 클래스 이름이 'Pagination_text__'로 시작하는 모든 태그 선택
    span_tags = driver.find_elements(By.CSS_SELECTOR, "[class^='DailyBoardView-module__weather_temperature___']")

    # 모든 태그 출력
    for tag in span_tags:
        print(tag.text)  # 태그의 텍스트 내용 출력

except Exception as e:
    print("태그를 찾지 못했습니다:", e)

# 브라우저 닫기
driver.quit()
