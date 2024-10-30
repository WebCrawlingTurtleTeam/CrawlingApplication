import os
import pandas as pd
from selenium import webdriver #module 
from selenium.webdriver.common.keys import Keys #enter key
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By 

import time #화면 일시 정지

query_txt = input('영화명 :')
path = r"./chromedriver-win64/chromedriver.exe"  # 드라이버 경로

service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)

driver.get('https://pedia.watcha.com/ko-KR')

time.sleep(1)
textbox = driver.find_element(By.XPATH,'//*[@id="root"]/div/div[1]/header/nav/div/div/ul/li[5]/div/div/form/label/input')
textbox.click()

element = driver.find_element_by_name("searchKeyword")
element.send_keys(query_txt + "\n")

time.sleep(2)
blank_click = driver.find_element_by_xpath('/html/body/div/div/div[1]/section/section/div[1]/div')
blank_click.click()

movie_click = driver.find_element_by_xpath('/html/body/div/div/div[1]/section/section/div[3]/div[1]/section/section[1]/div/div[1]/div/ul/li[1]/a/div[1]/div[1]/img')
movie_click.click()

time.sleep(2)
driver.execute_script("window.scrollTo(0, 1000)")
#한계점 발견 -> 높이는 절대적인 것이 아니라 상대적. 모니터 해상도 따라 숫자 조정할 필요가 있음

more_view = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/section/div/div[2]/div/div/div/div[1]/div[1]/div/div/section[5]/div[1]/div/header/div/div/a')
more_view.click()

last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    #끝까지 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    #대기
    time.sleep(1)

    #스크롤 내린 후 스크롤 높이 다시 가져옴
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

time.sleep(5)

data = pd.DataFrame(data=[], columns=['movie_title', 'writer_name','star_grade'])

def get_movie_reviews(driver, data, k):
    
    movie_title = query_txt
    writer_name = driver.find_elements_by_css_selector('.css-1agoci2')
    star_grade = driver.find_elements_by_css_selector('.css-yqs4xl')
       
    for i in range(k):
        tmp = []
        tmp.append(movie_title)
        tmp.append(writer_name[i].text)
        tmp.append(star_grade[i].text)
        
        tmp = pd.DataFrame(data=[tmp], columns=data.columns)
        data = pd.concat([data,tmp])
    
    print(movie_title + " 리뷰 수집 완료")
    
    return data

review = get_movie_reviews(driver, data, 21)

review = review[~review['star_grade'].str.contains("보고싶어요", na=False, case=False)]

review['star_grade'] = pd.to_numeric(review['star_grade'], downcast='float') #숫자형 변환

review = review.append({'movie_title' : query_txt, 'writer_name' : '평균', 'star_grade' : review['star_grade'].mean()}, ignore_index=True)
review = review.round(2)
print(review)

review.to_csv('./test.csv', sep=',', na_rep='NaN', encoding='utf-8-sig', mode='a', header=False, index=True)
#mode='a' : 누적 저장, seperator : 구분자, na_rep : 결측값 표기, encoding : 문자 깨짐 방지, header=False : 칼럼제목 표기X
print(query_txt + " 리뷰 저장 완료")