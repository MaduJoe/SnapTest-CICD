# background_worker.py

# import threading
# import time
from queue import Queue
# from runner import run_test_case

import schedule
import time
import threading
import os

# 워커 상태 추적을 위한 전역 변수들
worker_running = False
processed_count = 0

def run_all_tests():
    """
    모든 테스트 케이스를 실행합니다.
    """
    print("[자동 실행] 전체 테스트 시작")
    # 지연 임포트(lazy import)를 사용하여 순환 참조 방지
    from runner import run_test_case
    
    for filename in os.listdir("cases"):
        if filename.endswith(".json"):
            run_test_case(filename)

# def scheduler_loop():
#     schedule.every().day.at("00:00").do(run_all_tests)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

def scheduler_loop():
    """
    스케줄러 루프를 실행합니다.
    """
    # 실제 서비스에서는 아래 라인을 주석 처리하고 자정 실행으로 변경하세요
    # schedule.every(10).seconds.do(run_all_tests)  # 🔁 테스트를 위해 10초마다 자동 실행
    schedule.every().day.at("01:01").do(run_all_tests)

    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    """
    백그라운드 스케줄러를 시작합니다.
    """
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    print("[INFO] Scheduler thread started")

test_queue = Queue()

# 백그라운드에서 큐를 처리할 워커 함수
def worker():
    """
    큐에 추가된 테스트를 실행하는 워커 함수
    """
    global worker_running, processed_count
    worker_running = True
    
    # 마지막 작업 완료 시간을 추적
    last_activity_time = time.time()
    
    while True:
        if not test_queue.empty():
            filename = test_queue.get()
            print(f"[Worker] Running test: {filename}")
            # 지연 임포트(lazy import)
            from runner import run_test_case
            run_test_case(filename)
            processed_count += 1
            # 작업을 처리했으므로 마지막 활동 시간 업데이트
            last_activity_time = time.time()
        else:
            # 큐가 비었고 일정 시간(10초) 동안 새 작업이 없으면 워커 상태를 '대기 중'으로 변경
            # 또는 작업이 처리된 적이 있고 큐가 비었으면 5초만 기다린 후 완료 상태로 변경
            current_time = time.time()
            idle_timeout = 5 if processed_count > 0 else 10
            
            if current_time - last_activity_time > idle_timeout:
                if processed_count > 0:
                    print(f"[Worker] No tasks for {idle_timeout} seconds after processing {processed_count} tasks, setting status to idle")
                else:
                    print(f"[Worker] No tasks for {idle_timeout} seconds, setting status to idle")
                worker_running = False
            
            time.sleep(1)  # 큐가 비었으면 잠깐 쉼

# 워커 스레드를 백그라운드에서 시작
def start_background_worker():
    """
    백그라운드 워커 스레드를 시작합니다.
    """
    global worker_running
    
    # 이미 실행 중이면 다시 시작하지 않음
    if worker_running:
        print("[INFO] Background worker is already running")
        return
        
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    worker_running = True
    print("[INFO] Background worker thread started")

# 워커 상태 확인 함수
def get_worker_status():
    """
    워커가 실행 중인지 상태를 반환합니다.
    """
    global worker_running
    return worker_running

# 큐 크기 확인 함수
def get_queue_size():
    """
    현재 큐에 대기 중인 작업의 수를 반환합니다.
    """
    return test_queue.qsize()

# 처리된 작업 수 확인 함수
def get_processed_count():
    """
    워커가 처리한 작업의 수를 반환합니다.
    """
    global processed_count
    return processed_count

# 큐와 카운터 초기화 함수
def reset_queue_and_counter():
    """
    큐와 처리 카운터를 초기화합니다.
    """
    global processed_count
    with test_queue.mutex:
        test_queue.queue.clear()
    processed_count = 0
    return True

if __name__ == "__main__":
    # 독립 실행 시 테스트
    print("Starting background worker test...")
    start_background_worker()
    
    # 테스트를 위해 큐에 작업 추가
    if os.path.exists('cases'):
        for filename in os.listdir('cases')[:2]:  # 처음 2개 테스트만 실행
            if filename.endswith('.json'):
                test_queue.put(filename)
                print(f"Added {filename} to queue")
    
    # 메인 스레드 유지
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test stopped.")
