import os
import json
import sys
from datetime import datetime
import importlib
import xml.etree.ElementTree as ET

def run_test_case(filename):
    """테스트 케이스 파일을 실행하고 결과를 반환합니다."""
    try:
        # 파일 읽기
        with open(os.path.join('cases', filename), 'r', encoding='utf-8') as f:
            case = json.load(f)
        
        # 테스트 함수 가져오기
        module = importlib.import_module('tests.functions')
        test_func = getattr(module, case['test_function'])
        
        # 파라미터 가져오기
        params = case.get('parameters', {})
        
        # 테스트 실행
        start_time = datetime.now()
        result = test_func(**params)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 결과 반환
        return {
            'test_case': case,
            'result': result,
            'duration': duration,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        # 오류 발생시
        return {
            'test_case': {'name': filename, 'test_function': 'unknown'},
            'result': {'status': 'ERROR', 'error': str(e)},
            'duration': 0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    # 테스트 결과 디렉토리 생성
    os.makedirs('reports', exist_ok=True)

    # 테스트 케이스 목록 로드
    cases = []
    if os.path.exists('cases'):
        for filename in os.listdir('cases'):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join('cases', filename), 'r', encoding='utf-8') as f:
                        case = json.load(f)
                        case['filename'] = filename
                        cases.append(case)
                except Exception as e:
                    print(f'Error reading file {filename}: {str(e)}')
    else:
        print('Cases directory not found')
        
    print(f'Found {len(cases)} test cases')

    # 테스트 실행
    results = []
    for case in cases:
        print(f'Running test case: {case.get("name", "Unknown")}')
        result = run_test_case(case['filename'])
        results.append(result)
        print(f'Test result: {result["result"]["status"]}')

    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'reports/test_report_{timestamp}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f'Test report saved to {report_file}')

    # XML 보고서 생성
    generate_xml_report(results)
    
    # HTML 보고서 생성
    generate_html_report(results)

def generate_xml_report(results):
    """XML 형식의 테스트 결과 보고서를 생성합니다."""
    # XML 루트 요소 생성
    test_suite = ET.Element('testsuite')
    test_suite.set('name', 'TestAutomation')
    test_suite.set('tests', str(len(results)))
    test_suite.set('errors', str(sum(1 for r in results if r['result'].get('status') == 'ERROR')))
    test_suite.set('failures', str(sum(1 for r in results if r['result'].get('status') == 'FAIL')))
    test_suite.set('skipped', '0')
    test_suite.set('timestamp', datetime.now().isoformat())
    
    for result in results:
        test_case_name = result['test_case'].get('name', 'Unknown')
        test_function = result['test_case'].get('test_function', 'Unknown')
        status = result['result'].get('status', 'UNKNOWN')
        
        test_case = ET.SubElement(test_suite, 'testcase')
        test_case.set('name', test_case_name)
        test_case.set('classname', test_function)
        test_case.set('time', str(result.get('duration', 0)))
        
        if status == 'FAIL':
            failure = ET.SubElement(test_case, 'failure')
            failure.set('message', result['result'].get('error', 'Test failed'))
            failure.text = str(result['result'])
        elif status == 'ERROR':
            error = ET.SubElement(test_case, 'error')
            error.set('message', result['result'].get('error', 'Test error'))
            error.text = str(result['result'])
    
    # XML 파일 저장
    tree = ET.ElementTree(test_suite)
    xml_report = os.path.join('reports', 'test_report.xml')
    tree.write(xml_report, encoding='utf-8', xml_declaration=True)
    
    print(f'XML report generated: {xml_report}')

def generate_html_report(results):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Automation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .header {{ margin-bottom: 20px; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        .summary {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Automation Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h3>Summary</h3>
        <p>Total Tests: {len(results)}</p>
        <p>Passed: <span class="pass">{sum(1 for r in results if r['result']['status'] == 'PASS')}</span></p>
        <p>Failed: <span class="fail">{sum(1 for r in results if r['result']['status'] in ['FAIL', 'ERROR'])}</span></p>
        <p>Success Rate: {sum(1 for r in results if r['result']['status'] == 'PASS') / len(results) * 100 if results else 0:.2f}%</p>
    </div>
    
    <h3>Test Results</h3>
    <table>
        <thead>
            <tr>
                <th>Test Case</th>
                <th>Function</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
        </thead>
        <tbody>
"""

    for result in results:
        test_case_name = result['test_case'].get('name', 'Unknown')
        test_function = result['test_case'].get('test_function', 'Unknown')
        status = result['result']['status']
        status_class = 'pass' if status == 'PASS' else 'fail'
        details = result['result'].get('result', '') or result['result'].get('error', '')
        
        html += f"""
        <tr>
            <td>{test_case_name}</td>
            <td>{test_function}</td>
            <td class="{status_class}">{status}</td>
            <td>{details}</td>
        </tr>
        """

    html += """
        </tbody>
    </table>
</body>
</html>
"""

    # HTML 파일 저장
    html_report = os.path.join('reports', 'test_report.html')
    with open(html_report, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'HTML report generated: {html_report}')

if __name__ == '__main__':
    main() 