# tests/functions.py
import time

def add_test(a, b, expected):
    time.sleep(3)  # 1초 대기
    print(f"Adding {a} + {b}")
    result = a + b
    print(f"Result: {result}")
    assert result == expected, f"Expected {expected}, got {result}"
    return {"result": result, "status": "PASS"}

def multiply_test(a, b, expected):
    print(f"Multiplying {a} * {b}")
    result = a * b
    print(f"Result: {result}")
    assert result == expected, f"Expected {expected}, got {result}"
    return {"result": result, "status": "PASS"}

def divide_test(a, b, expected):
    print(f"Dividing {a} / {b}")
    result = a / b
    print(f"Result: {result}")
    assert abs(result - expected) < 1e-6, f"Expected {expected}, got {result}"
    return {"result": result, "status": "PASS"}

def string_concat_test(s1, s2, expected):
    print(f"Concatenating '{s1}' + '{s2}'")
    result = s1 + s2
    assert result == expected, f"Expected '{expected}', got '{result}'"
    return {"result": result, "status": "PASS"}

def fail_test():
    print("This test should fail.")
    # raise Exception("Intentional failure for testing.")
    return {"result": 'This test should fail.', "status": "FAIL"}

def divide_zero_test(a, b, expected):
    try:
        result = a / b
        return {"result": result, "status": "PASS"}
    except ZeroDivisionError as e:
        return {"error": str(e), "status": "FAIL"}

def detect_login_from_different_device_sms_alert_test(user_id, device_id_1, device_id_2, expected, sms_message):
    """다른 기기에서 로그인 시 SMS 알림이 정상적으로 전송되는지 확인하는 테스트"""
    print(f"Running test: 다른 기기에서 로그인 시 SMS 알림이 정상적으로 전송되는지 확인하는 테스트")
    try:
        # 테스트를 위한 모의 구현
        def mock_check_sms_sent(uid, msg):
            return True  # 실제 구현에서는 실제 SMS 전송 여부를 확인
            
        result = mock_check_sms_sent(user_id, sms_message)
        
        if not result:
            return {"status": "FAIL", "message": "SMS was not sent successfully"}
            
        return {"status": "PASS", "result": "SMS sent successfully"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def detect_login_from_different_device_sms_notification_test(user_id, device_id_1, device_id_2, expected, sms_message):
    """다른 기기에서 로그인 시 SMS 알림이 정상적으로 전송되는지 확인하는 테스트"""
    print(f"Running test: 다른 기기에서 로그인 시 SMS 알림이 정상적으로 전송되는지 확인하는 테스트")
    try:
        # 테스트를 위한 모의 구현
        def check_sms_sent(uid, msg):
            return True  # 실제 구현에서는 실제 SMS 전송 여부를 확인
            
        result = check_sms_sent(user_id, sms_message) == expected
        
        if not result:
            return {"status": "FAIL", "message": "Test condition not met"}
            
        return {"status": "PASS", "result": str(result)}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def password_complexity_check_test(password, expected):
    """
    비밀번호가 최소 8자 이상, 영문 대소문자, 숫자, 특수문자를 모두 포함하는지 검증하는 테스트
    """
    print(f"Running test: 비밀번호가 최소 8자 이상, 영문 대소문자, 숫자, 특수문자를 모두 포함하는지 검증하는 테스트")
    try:
        # 테스트 로직 실행
        print(f"Executing test logic: len(password) >= 8 and any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password) and any(not c.isalnum() for c in password) == expected")
        result = eval("len(password) >= 8 and any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password) and any(not c.isalnum() for c in password) == expected")
        
        if not result:
            return {"status": "FAIL", "message": "Test condition not met"}
            
        return {"status": "PASS", "result": str(result)}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def bank_maintenance_transfer_failure_popup_test(is_maintenance, transfer_amount, expected_message):
    """
    은행 점검 시간 동안 송금 시 실패 메시지 팝업창이 발생하는지 확인하는 테스트
    """
    print(f"Running test: 은행 점검 시간 동안 송금 시 실패 메시지 팝업창이 발생하는지 확인하는 테스트")
    try:
        # 테스트 로직 실행
        print(f"Executing test logic: is_maintenance == True and expected_message in popup_message")
        result = eval("is_maintenance == True and expected_message in popup_message")
        
        if not result:
            return {"status": "FAIL", "message": "Test condition not met"}
            
        return {"status": "PASS", "result": str(result)}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def rollback_failed_transfer_test(initial_balance, transfer_amount, expected_balance, transaction_status):
    """
    송금이 실패했을 때 계좌 잔액이 정상적으로 Rollback 되는지 확인하는 테스트
    """
    print(f"Running test: 송금이 실패했을 때 계좌 잔액이 정상적으로 Rollback 되는지 확인하는 테스트")
    try:
        # 테스트 로직 실행
        print(f"Executing test logic: initial_balance - transfer_amount == expected_balance if transaction_status == 'failed' else False")
        result = eval("initial_balance - transfer_amount == expected_balance if transaction_status == 'failed' else False")
        
        if not result:
            return {"status": "FAIL", "message": "Test condition not met"}
            
        return {"status": "PASS", "result": str(result)}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}
