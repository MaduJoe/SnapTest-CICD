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

# 테스트 함수 동적 로딩

def get_test_function(name):
    spec = importlib.util.spec_from_file_location("functions", "tests/functions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, name)

# 테스트 케이스 실행

def run_test_case(filename):
    start_time = time.time()
    logs = ""
    test_case = {}

    try:
        filepath = os.path.join("cases", filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"{filepath} 파일이 존재하지 않습니다.")

        with open(filepath, 'r') as f:
            test_case = json.load(f)

        test_func = get_test_function(test_case["test_function"])

        log_stream = io.StringIO()
        with contextlib.redirect_stdout(log_stream):
            result = test_func(**test_case["parameters"])
        logs = log_stream.getvalue()

        name = test_case.get("name", filename)
        if name.endswith(".json"):
            name = name[:-5]

        status = result.get("status", "PASS")
        description = test_case.get("description", "").strip()

    except Exception as e:
        logs = logs or ""
        duration = time.time() - start_time
        name = test_case.get("name", filename)
        if name.endswith(".json"):
            name = name[:-5]

        report = {
            "test_case": name.strip(),
            "description": test_case.get("description", "Execution Failed").strip(),
            "status": "FAIL",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "log": logs,
            "timestamp": datetime.now().isoformat(),
            "duration": round(duration, 3)
        }

        save_report(report)
        update_test_case_stats(report["test_case"], report["status"], report["timestamp"])
        return

    duration = time.time() - start_time
    report = {
        "test_case": name.strip(),
        "description": description,
        "status": status,
        "output": result,
        "log": logs,
        "timestamp": datetime.now().isoformat(),
        "duration": round(duration, 3)
    }

    save_report(report)
    update_test_case_stats(report["test_case"], report["status"], report["timestamp"])

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
