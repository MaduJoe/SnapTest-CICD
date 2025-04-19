# 리팩토링된 runner.py
import os
import json
import time
import io
import traceback
import contextlib
import importlib.util
from datetime import datetime
from db import insert_report, update_test_case_stats
import tests.functions as test_functions
# 순환 참조 제거
# from background_worker import start_scheduler

# 테스트 함수 동적 로딩

def get_test_function(name):
    spec = importlib.util.spec_from_file_location("functions", "tests/functions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, name)

# 테스트 케이스 실행

def run_test_case(filename):
    """테스트 케이스를 실행하고 결과를 저장합니다."""
    print(f"[DEBUG] Running test case: {filename}")
    
    try:
        # 테스트 케이스 파일 읽기
        with open(os.path.join('cases', filename), 'r', encoding='utf-8') as f:
            case = json.load(f)
            print(f"[DEBUG] Loaded test case: {case}")
        
        # 테스트 함수 가져오기
        test_func = getattr(test_functions, case['test_function'])
        print(f"[DEBUG] Found test function: {test_func.__name__}")
        
        # 파라미터 준비
        params = case.get('parameters', {})
        print(f"[DEBUG] Parameters: {params}")
        
        # 테스트 실행
        start_time = datetime.now()
        logs = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(logs):
                result = test_func(**params)
            
            log_content = logs.getvalue()
            print(f"[DEBUG] Raw test result: {result}")
            print(f"[DEBUG] Log content: {log_content}")
            
            if not isinstance(result, dict):
                result = {"status": "FAIL", "error": "Test function did not return a valid result dictionary"}
            
            # 결과를 안전하게 직렬화 가능한 형식으로 변환
            safe_result = {
                "status": str(result.get("status", "FAIL")),
                "result": str(result.get("result", "")),
                "error": str(result.get("error", ""))
            }
            print(f"[DEBUG] Processed result: {safe_result}")
            
        except Exception as e:
            print(f"[DEBUG] Test execution error: {str(e)}")
            error_traceback = traceback.format_exc()
            log_content = logs.getvalue()
            safe_result = {
                "status": "FAIL",
                "error": str(e),
                "result": ""
            }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 테스트 케이스 통계 업데이트
        update_test_case_stats(
            test_case_name=case.get('name', filename),
            status=safe_result['status'],
            timestamp=str(end_time)
        )
        
        # 데이터베이스에 리포트 저장
        report = {
            "test_case": case.get('name', filename),
            "description": case.get('description', ''),
            "status": safe_result['status'],
            "output": safe_result['result'],
            "error": safe_result.get('error', ''),
            "traceback": error_traceback if 'error_traceback' in locals() else '',
            "log": log_content if 'log_content' in locals() else '',
            "timestamp": str(end_time),
            "duration": duration
        }
        
        # 리포트를 DB에 저장
        insert_report(report)
        print(f"[DEBUG] Report saved to database")
        
        # 결과 데이터 준비
        result_data = {
            "test_case": {
                "name": str(case.get('name', '')),
                "description": str(case.get('description', '')),
                "test_function": str(case.get('test_function', '')),
                "parameters": {str(k): str(v) for k, v in params.items()}
            },
            "result": safe_result,
            "execution_time": str(duration),
            "timestamp": str(end_time)
        }
        
        print(f"[DEBUG] Final result data: {result_data}")
        
        # 결과 저장
        results_dir = 'results'
        os.makedirs(results_dir, exist_ok=True)
        
        result_filename = f"{os.path.splitext(filename)[0]}_{end_time.strftime('%Y%m%d_%H%M%S')}.json"
        result_path = os.path.join(results_dir, result_filename)
        
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Result saved to: {result_path}")
            
        return result_data
        
    except Exception as e:
        print(f"[DEBUG] Critical error in run_test_case: {str(e)}")
        print(traceback.format_exc())
        error_result = {
            "test_case": {
                "name": filename,
                "description": "Error running test case",
                "test_function": "",
                "parameters": {}
            },
            "result": {
                "status": "ERROR",
                "error": str(e),
                "result": ""
            },
            "execution_time": "0",
            "timestamp": str(datetime.now())
        }
        return error_result

# 리포트 저장 (DB + JSON)

def save_report(report):
    print(f"[DEBUG] Saving report: {report['test_case']}")
    insert_report(report)

    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = report['test_case'].replace(' ', '_').replace('/', '_')
    filename = os.path.join("reports", f"{timestamp}_{safe_name}.json")

    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

# 지연 임포트를 통한 스케줄러 시작 함수
def init_scheduler():
    """앱 시작 시 호출하여 스케줄러를 시작합니다."""
    try:
        from background_worker import start_scheduler
        start_scheduler()
        print("[INFO] Background scheduler started successfully")
    except ImportError as e:
        print(f"[WARNING] Could not start background scheduler: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Error starting background scheduler: {str(e)}")
