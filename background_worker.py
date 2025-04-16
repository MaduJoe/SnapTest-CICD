# background_worker.py

# import threading
# import time
from queue import Queue
# from runner import run_test_case

import schedule
import time
import threading
from runner import run_test_case
import os

def run_all_tests():
    print("[자동 실행] 전체 테스트 시작")
    for filename in os.listdir("cases"):
        if filename.endswith(".json"):
            run_test_case(filename)

# def scheduler_loop():
#     schedule.every().day.at("00:00").do(run_all_tests)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

def scheduler_loop():
    # 실제 서비스에서는 아래 라인을 주석 처리하고 자정 실행으로 변경하세요
    # schedule.every(10).seconds.do(run_all_tests)  # 🔁 테스트를 위해 10초마다 자동 실행
    schedule.every().day.at("01:01").do(run_all_tests)

    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()

test_queue = Queue()

# 백그라운드에서 큐를 처리할 워커 함수
def worker():
    while True:
        if not test_queue.empty():
            filename = test_queue.get()
            print(f"[Worker] Running test: {filename}")
            run_test_case(filename)
        else:
            time.sleep(1)  # 큐가 비었으면 잠깐 쉼

# 워커 스레드를 백그라운드에서 시작
def start_background_worker():
    t = threading.Thread(target=worker, daemon=True)
    t.start()
