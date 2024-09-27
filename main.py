import tkinter as tk
from selenium.webdriver.common.by import By
from db_connect import DB
from chrom_driver import Driver
from tkinter import messagebox as msg

win = tk.Tk()
win.title("프로그램")
win.geometry("500x500+500+150")
win.resizable(False, False)

db = DB()
driver = Driver().driver
driver.get('https://www.naver.com/')

# 스크롤 만들거 프레임
main_frame = tk.Frame(win)
main_frame.pack(fill=tk.BOTH, expand=1)

# 스크롤 가능하게 캔버스 만드
canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# 스크롤바 만들고 캔버스에 연결하기
scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)


# 스크롤 가능 영역을 정해주기
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


# 스크롤 가능한 프레임 생성
scrollable_frame = tk.Frame(canvas)

# 캔버스에 프레임 추가
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# 스크롤 가능한 영역을 동적으로 설정
scrollable_frame.bind("<Configure>", on_frame_configure)


# 검색 결과 레이블을 생성하는 함수
def create_label_from_search_result(text):
    new_label = tk.Label(scrollable_frame, text=text, anchor="w", justify="left")
    new_label.pack(padx=5, pady=5, anchor="w")


# 검색 함수
def search_class_name():
    user_input = entry.get()
    tags = driver.find_elements(By.CSS_SELECTOR, "[class^='" + user_input + "']")

    # 검색 결과 처리
    if tags:
        clear_labels()  # 기존 레이블 삭제
        for tag in tags:
            create_label_from_search_result(tag.text)  # 새로운 레이블 생성
            print(tag.text)  # 출렫
    else:
        msg.showerror("에러", "검색 결과가 없습니다.")


def clear_labels():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()


# 입력 필드와 버튼 생성
entry = tk.Entry(win, width=50)
button = tk.Button(win, text="클래스 이름으로 검색하기", command=search_class_name)

entry.pack(pady=10)
button.pack(pady=10)

win.mainloop()

driver.quit()
db.close()
