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
