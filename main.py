from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
from query import CRUD
from datetime import datetime, timedelta
from selenium.webdriver import Keys

# 크롬 드라이버 자동 설치 및 설정
service = Service(ChromeDriverManager().install())
app = FastAPI()
query = CRUD()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def bring_movie_name():
    # 스크롤 횟수 설정

    driver = webdriver.Chrome(service=service)
    driver.get("https://pedia.watcha.com/ko-KR/staffmades/gsm872YZNo")
    scroll_limit = 3
    for _ in range(scroll_limit):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    movie_elements = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "ZADAQaiR"))
    )
    # 영화 제목 가져오기
    movie_names = [element.text for element in movie_elements]
    driver.quit()

    return movie_names


async def bring_naver_review(movie_name: str):
    driver = webdriver.Chrome(service=service)
    url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=" + movie_name + "+관람평"
    driver.get(url)

    try:
        r = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[4]/ul/li')))
    except Exception as e:
        r = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[3]/div[4]/ul/li')))
        print(f"페이지 로딩 또는 크롤링 실패: {e.__class__.__name__}")
    # 데이터 크롤링
    try:
        reviews = r
        review_list = []
        for review in reviews:
            try:
                r = review.find_element(By.CLASS_NAME, "_text")
                review_list.append(r.text)
            except Exception as e:
                print(f"리뷰 처리 중 오류 발생: {e}")
    except Exception as e:
        print(f"페이지 로딩 또는 크롤링 실패: {e}")

    finally:
        driver.quit()

    return review_list


async def bring_review(movie_names):
    driver = webdriver.Chrome(service=service)
    all_reviews = {}

    for movie_name in movie_names:
        review_list = []

        # 영화 제목으로 검색
        url = f"https://pedia.watcha.com/ko-KR/search?query={movie_name}"
        driver.get(url)

        try:
            # 영화 요소 로드될 때까지 대기
            movies = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".jSJzhUhk.qz3Mr8mt"))
            )
            review_list.append(movies[0].text)
            movies[0].click()

            # "더보기" 버튼 클릭 가능해질 때까지 대기
            more_button_selector = "#root > div:nth-child(1) > section > div > div:nth-child(2) > section > section:nth-child(2) > header > div > div > a"
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, more_button_selector))
            ).click()

            # 리뷰 요소 로드될 때까지 대기
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".B79Ex5Ar"))
            )

            # 페이지 스크롤하여 리뷰 로드
            scroll_limit = 3
            for _ in range(scroll_limit):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                # 리뷰 수집
            reviews = driver.find_elements(By.CSS_SELECTOR, ".B79Ex5Ar")
            for review in reviews:
                review_text = review.text.replace("\n", "").replace("\\", "").replace("\u003E", "").replace("\u003C",
                                                                                                            "")
                review_list.append(review_text)

            all_reviews[movie_name] = review_list

        except TimeoutException:
            print(f'영화 "{movie_name}"를 찾을 수 없습니다.')
        except Exception as e:
            print(f'오류 발생: {e.__class__.__name__}')

    driver.quit()
    return all_reviews


@app.get("/")
async def root():
    movies = query.get_movies()  # 무비들 DB에서 가져옴 투플
    print(movies)
    if len(movies) == 0:  # 가져온 무비들이 없으면?
        result = await bring_movie_name()  # 크롤링 하기
        query.insert_movie(result)  # 그리고 인서트
        return result
    else:  # DB에서 온게 있으면?

        # if movies[0][1] >= datetime.now() - timedelta(hours=3):
        #     # 3시간 안 지남
        return [movie[0] for movie in movies if movie and movie[0].strip()]
        # else:
        #     # 3시간 지남
        #     result = await bring_movie_name()  # 크롤링 하기
        #     query.insert_movie(result)  # 그리고 인서트
        #     return result


@app.get("/review-watcha")
async def get_review(name: str):
    # name으로 movie에서 movie테이블의 movie_name이 name인 movie_code와
    # review 테이블의 movie_code가 일치하는게 있는지 찾는다.
    reviews = query.get_review(name, 'watcha')
    if reviews:
        # 3 시간 확인
        if reviews[0][1] >= datetime.now() - timedelta(hours=3):
            # 안 지났으면?
            return [review[0] for review in reviews]
        else:
            # 지났으면?
            result = await bring_review([name])
            query.insert_review(result[name], name, 'watcha')
            return result[name]
    else:
        # 아예 처음
        result = await bring_review([name])
        query.insert_review(result[name], name, 'watcha')
        return result[name]


@app.get("/review-naver")
async def get_naver_review(name: str):
    reviews = query.get_review(name, 'naver')
    if reviews:
        if reviews[0][1] >= datetime.now() - timedelta(hours=3):
            return [review[0] for review in reviews]
        else:
            result = await bring_naver_review(name)
            query.insert_review(result, name, 'naver')
            return result
    else:
        result = await bring_naver_review(name)
        query.insert_review(result, name, 'naver')
        return result


@app.get("/main/{movie_name}")
async def root(movie_name: str):
    def get_movie():
        try:
            r = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[4]/ul/li')))
            return r
        except Exception as e:
            r = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[3]/div[4]/ul/li')))
            print(f"페이지 로딩 또는 크롤링 실패: {e.__class__.__name__}")
            return r

    driver = webdriver.Chrome(service=service)
    url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=" + movie_name + "+관람평"
    driver.get(url)

    # 데이터 크롤링
    try:
        reviews = get_movie()
        review_list = []
        for review in reviews:
            try:
                r = review.find_element(By.CLASS_NAME, "_text")
                review_list.append(r.text)
                print("-" * 40)
            except Exception as e:
                print(f"리뷰 처리 중 오류 발생: {e}")
    except Exception as e:
        print(f"페이지 로딩 또는 크롤링 실패: {e}")

    finally:
        driver.quit()

    return review_list


@app.get("/watcha/{movie_name}")
async def getWatchaReview(movie_name: str):
    driver = webdriver.Chrome(service=service)
    url = "https://pedia.watcha.com/ko-KR"
    driver.get(url)
    review_list = []

    e = driver.find_element(By.XPATH, '//*[@id="desktop-search-field"]')
    e.send_keys(movie_name)
    e.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    '//*[@id="root"]/div[1]/section/section/div[2]/div[1]/section/section[2]/div[1]/ul/li[1]/a/div[1]/div[1]/img'))
    )
    a = driver.find_elements(By.XPATH,
                             '//*[@id="root"]/div[1]/section/section/div[2]/div[1]/section/section[2]/div[1]/ul/li[1]/a/div[1]/div[1]/img')
    a[0].click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="root"]/div[1]/section/div/div[2]/section/section[2]/ul/li[1]'))
    )
    driver.find_element(By.XPATH,
                        '//*[@id="root"]/div[1]/section/div/div[2]/section/section[2]/header/div/div/a').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.B79Ex5Ar'))
    )

    b = driver.find_elements(By.CSS_SELECTOR, '.B79Ex5Ar')

    for i in b:
        print(i.text)
        review_list.append(i.text)
    return review_list


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
