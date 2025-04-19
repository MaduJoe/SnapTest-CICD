from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import json
import inspect
from datetime import datetime
from dotenv import load_dotenv
from db import get_all_test_case_stats, init_db, get_all_reports, get_average_duration, get_report_by_id
from runner import run_test_case
import tests.functions as test_functions
import traceback

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Gemini API 설정
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
gemini_enabled = False

try:
    import google.generativeai as genai
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        gemini_enabled = True
    else:
        print("Warning: GOOGLE_API_KEY not found in .env file")
except ImportError:
    print("Warning: google.generativeai package not installed")
    pass

def get_test_cases():
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
                    print(f"Error reading file {filename}: {str(e)}")
    return cases

def get_test_functions():
    """tests/functions.py에서 사용 가능한 테스트 함수 목록을 가져옵니다."""
    test_funcs = []
    for name, func in inspect.getmembers(test_functions, inspect.isfunction):
        if name.endswith('_test'):  # _test로 끝나는 함수만 선택
            # 함수의 파라미터 정보 가져오기
            params = inspect.signature(func).parameters
            param_info = {
                'name': name,
                'parameters': list(params.keys())  # 파라미터 이름 목록
            }
            test_funcs.append(param_info)
    return test_funcs

@app.route('/')
def index():
    cases = get_test_cases()
    return render_template('index.html', cases=cases, gemini_enabled=gemini_enabled)

@app.route('/dashboard')
def dashboard():
    try:
        # 기본 변수 초기화
        stats = []
        reports = []
        avg_duration = 0.0
        status_filter = request.args.get('status')
        keyword = request.args.get('q')
        sort_order = request.args.get('sort', 'desc')  # 기본값은 최신순(desc)
        
        # 통계 데이터 가져오기
        stats = get_all_test_case_stats()
        
        # 리포트 데이터 가져오기 (최근 20개)
        reports = get_all_reports()
        print(f"[DEBUG] Loaded {len(reports)} reports from database")
        
        # ID 기준으로 내림차순 정렬 (기본값)
        if sort_order == 'desc':
            reports.sort(key=lambda x: x['id'], reverse=True)  # 최신순 (ID 내림차순)
        else:
            reports.sort(key=lambda x: x['id'])  # 오래된순 (ID 오름차순)
        
        # 평균 실행 시간 계산
        avg_duration = get_average_duration()
        
        # 필터링
        if status_filter:
            reports = [r for r in reports if r['status'] == status_filter]
        
        if keyword:
            reports = [r for r in reports if keyword.lower() in r['test_case'].lower() 
                     or keyword.lower() in r['description'].lower()]
        
        # 차트 데이터 준비
        pass_count = 0
        fail_count = 0
        
        # 모든 값이 문자열 또는 숫자인지 확인하고 안전하게 변환
        for stat in stats:
            stat['test_case'] = str(stat.get('test_case', ''))
            stat['total_runs'] = int(stat.get('total_runs', 0))
            stat['pass_count'] = int(stat.get('pass_count', 0))
            stat['fail_count'] = int(stat.get('fail_count', 0))
            stat['last_run'] = str(stat.get('last_run', ''))
            stat['success_rate'] = float(stat.get('success_rate', 0.0))
            pass_count += stat['pass_count']
            fail_count += stat['fail_count']
        
        labels = ['FAIL', 'PASS']
        values = [fail_count, pass_count]
        
        # 테스트 케이스 통계를 test_case_stats로 이름 변경 (템플릿과 일치시키기 위해)
        test_case_stats = []
        for stat in stats:
            test_case_stats.append({
                'test_case': stat['test_case'],
                'run_count': stat['total_runs'],
                'pass_count': stat['pass_count'],
                'fail_count': stat['fail_count'],
                'success_rate': stat['success_rate'],
                'last_run': stat['last_run']
            })
        
        # 리포트 데이터 제한 (최대 20개)
        reports = reports[:20]
        
        print(f"[DEBUG] Rendering dashboard with {len(reports)} reports")
            
        return render_template(
            'dashboard.html', 
            test_case_stats=test_case_stats,
            reports=reports,
            avg_duration=avg_duration,
            status_filter=status_filter,
            keyword=keyword,
            sort_order=sort_order,
            labels=labels,
            values=values
        )
        
    except Exception as e:
        print(f"[DEBUG] Dashboard error: {str(e)}")
        print(traceback.format_exc())
        flash(f'대시보드 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        # 최소한의 안전한 데이터로 템플릿 렌더링
        return render_template(
            'dashboard.html', 
            test_case_stats=[],
            reports=[],
            avg_duration=0.0,
            status_filter=None,
            keyword=None,
            sort_order='desc',  # 기본값은 최신순
            labels=['FAIL', 'PASS'],
            values=[0, 0]
        )

@app.route('/run', methods=['POST'])
def run_tests():
    try:
        selected_cases = request.form.getlist('selected_cases')
        print(f"[DEBUG] Selected test cases: {selected_cases}")
        
        results = []
        for case in selected_cases:
            print(f"[DEBUG] Running case: {case}")
            result = run_test_case(case)
            print(f"[DEBUG] Test result: {result}")
            
            if result:
                # 결과를 안전하게 처리
                try:
                    # 결과를 JSON으로 직렬화했다가 다시 파싱하여 안전성 검증
                    result_json = json.dumps(result)
                    parsed_result = json.loads(result_json)
                    results.append(parsed_result)
                    print(f"[DEBUG] Successfully processed result")
                except Exception as e:
                    print(f"[DEBUG] Error processing result: {str(e)}")
                    error_result = {
                        "test_case": {"name": case},
                        "result": {
                            "status": "ERROR",
                            "error": f"Result processing error: {str(e)}",
                            "result": ""
                        }
                    }
                    results.append(error_result)
        
        print(f"[DEBUG] All results processed. Redirecting to dashboard.")
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f"[DEBUG] Critical error in run_tests: {str(e)}")
        print(traceback.format_exc())
        flash(f'테스트 실행 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/delete_case/<filename>')
def delete_case(filename):
    try:
        filepath = os.path.join('cases', filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            flash('테스트 케이스가 삭제되었습니다.', 'success')
        else:
            flash('테스트 케이스를 찾을 수 없습니다.', 'error')
    except Exception as e:
        flash(f'삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/add_case', methods=['GET', 'POST'])
def add_case():
    if request.method == 'POST':
        try:
            case = {
                'name': request.form['name'],
                'description': request.form['description'],
                'test_function': request.form['test_function'],
                'parameters': json.loads(request.form['parameters'])
            }
            
            filename = case['name'].replace(' ', '_') + '.json'
            os.makedirs('cases', exist_ok=True)
            with open(os.path.join('cases', filename), 'w', encoding='utf-8') as f:
                json.dump(case, f, indent=2, ensure_ascii=False)
            
            flash('테스트 케이스가 성공적으로 추가되었습니다.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'테스트 케이스 추가 중 오류가 발생했습니다: {str(e)}', 'error')
            test_functions = get_test_functions()
            return render_template('add_case.html', test_functions=test_functions)
        
    test_functions = get_test_functions()
    return render_template('add_case.html', test_functions=test_functions)

@app.route('/edit_case/<filename>', methods=['GET', 'POST'])
def edit_case(filename):
    filepath = os.path.join('cases', filename)
    
    if request.method == 'POST':
        try:
            case = {
                'name': request.form['name'],
                'description': request.form['description'],
                'test_function': request.form['test_function'],
                'parameters': json.loads(request.form['parameters'])
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(case, f, indent=2, ensure_ascii=False)
            
            flash('테스트 케이스가 수정되었습니다.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'테스트 케이스 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        case = json.load(f)
        case['filename'] = filename
    
    # 파라미터 JSON 문자열 생성 시 ensure_ascii=False 사용
    case['parameters_json'] = json.dumps(case.get('parameters', {}), indent=2, ensure_ascii=False)
    
    test_functions = get_test_functions()
    return render_template('edit_case.html', case=case, test_functions=test_functions)

def create_test_function(case_info):
    """테스트 케이스 정보를 바탕으로 테스트 함수 파일을 생성/수정합니다."""
    function_name = case_info['test_function']
    parameters = case_info.get('parameters', {})
    test_logic = case_info.get('test_logic', 'True')
    description = case_info.get('description', '')
    
    # 함수 코드 생성
    function_code = f'''
def {function_name}({', '.join(parameters.keys())}):
    """
    {description}
    """
    print(f"Running test: {description}")
    try:
        # 테스트 로직 실행
        print(f"Executing test logic: {test_logic}")
        result = eval("{test_logic}")
        
        if not result:
            return {{"status": "FAIL", "message": "Test condition not met"}}
            
        return {{"status": "PASS", "result": str(result)}}
    except Exception as e:
        return {{"status": "FAIL", "error": str(e)}}
'''
    
    # tests/functions.py 파일에 함수 추가
    with open('tests/functions.py', 'a', encoding='utf-8') as f:
        f.write('\n' + function_code)

@app.route('/ai_case', methods=['GET', 'POST'])
def generate_case_with_ai():
    if not gemini_enabled:
        return "Gemini API가 설정되지 않았습니다. GOOGLE_API_KEY 환경 변수를 설정해주세요.", 400
        
    if request.method == 'POST':
        prompt = request.form['prompt']
        
        # Gemini를 사용하여 테스트 케이스 생성
        system_prompt = """
당신은 테스트 케이스와 테스트 함수를 생성하는 AI 도우미입니다.
주어진 설명을 바탕으로 다음 형식의 JSON을 생성해주세요.
테스트 함수명은 설명에 맞게 새롭게 생성해야 하며, 기존 함수를 재사용하지 않습니다.
함수명은 설명적이어야 하며 _test로 끝나야 합니다.

중요: test_logic은 반드시 실행 가능한 Python 코드여야 하며, 문자열이나 설명이 아닌 실제 코드여야 합니다.

{
    "name": "테스트 케이스의 간단한 이름",
    "description": "테스트의 상세 설명",
    "test_function": "새롭게_생성할_테스트_함수명_test",
    "parameters": {
        "param1": "기본값1",
        "param2": "기본값2",
        "expected": "기대값"
    },
    "test_logic": "param1 + param2 == expected"  # 실제 실행 가능한 Python 코드여야 함
}

예시:
입력: "두 수를 더했을 때 음수가 나오는지 검증"
출력: {
    "name": "음수 덧셈 테스트",
    "description": "두 수를 더했을 때 음수가 나오는지 확인하는 테스트",
    "test_function": "addition_negative_result_test",
    "parameters": {
        "x": -5,
        "y": 3,
        "expected": -2
    },
    "test_logic": "x + y == expected and (x + y) < 0"  # 실제 실행 가능한 Python 코드
}

주의사항:
1. test_logic은 반드시 실행 가능한 Python 코드여야 합니다
2. 문자열이나 설명이 아닌 실제 코드를 생성해야 합니다
3. 모든 변수는 파라미터로 전달된 값을 사용해야 합니다
"""
        
        try:
            response = model.generate_content(system_prompt + "\n\n사용자 요청: " + prompt)
            response_text = response.text.strip()
            
            # 코드 블록 제거
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "")
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "")
            
            response_text = response_text.strip()
            case = json.loads(response_text)
            
            # test_logic이 실제 Python 코드인지 검증
            try:
                compile(case['test_logic'], '<string>', 'eval')
            except SyntaxError:
                raise ValueError("생성된 test_logic이 유효한 Python 코드가 아닙니다")
            
            # 테스트 함수 생성
            create_test_function(case)
            
            # 파일로 저장
            filename = case['name'].replace(' ', '_') + '.json'
            os.makedirs('cases', exist_ok=True)
            with open(os.path.join('cases', filename), 'w', encoding='utf-8') as f:
                json.dump(case, f, indent=2, ensure_ascii=False)
            
            flash('테스트 케이스와 함수가 생성되었습니다.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f"Error generating test case: {str(e)}")
            print(f"Response text: {response_text if 'response_text' in locals() else 'No response'}")
            flash(f'테스트 케이스 생성 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('ai_case_form.html', gemini_enabled=gemini_enabled)
            
    return render_template('ai_case_form.html', gemini_enabled=gemini_enabled)

@app.route('/view_report/<int:report_id>')
def view_report(report_id):
    try:
        report = get_report_by_id(report_id)
        if not report:
            flash('리포트를 찾을 수 없습니다.', 'error')
            return redirect(url_for('dashboard'))
        return render_template('view_report.html', report=report)
    except Exception as e:
        print(f"[DEBUG] View report error: {str(e)}")
        flash(f'리포트 조회 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/delete_report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    try:
        from db import delete_report_by_id
        delete_report_by_id(report_id)
        flash('리포트가 삭제되었습니다.', 'success')
    except Exception as e:
        print(f"[DEBUG] Delete report error: {str(e)}")
        flash(f'리포트 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

@app.route('/api/reports')
def api_reports():
    try:
        # 파라미터 가져오기
        status_filter = request.args.get('status')
        keyword = request.args.get('q')
        sort_order = request.args.get('sort', 'desc')  # 기본값은 최신순(desc)
        
        # 통계 데이터 가져오기
        stats = get_all_test_case_stats()
        
        # 리포트 데이터 가져오기
        reports = get_all_reports()
        
        # ID 기준으로 내림차순 정렬 (기본값)
        if sort_order == 'desc':
            reports.sort(key=lambda x: x['id'], reverse=True)  # 최신순 (ID 내림차순)
        else:
            reports.sort(key=lambda x: x['id'])  # 오래된순 (ID 오름차순)
        
        # 필터링
        if status_filter:
            reports = [r for r in reports if r['status'] == status_filter]
        
        if keyword:
            reports = [r for r in reports if keyword.lower() in r['test_case'].lower() 
                     or keyword.lower() in r['description'].lower()]
        
        # 차트 데이터 준비
        pass_count = 0
        fail_count = 0
        
        for stat in stats:
            pass_count += int(stat.get('pass_count', 0))
            fail_count += int(stat.get('fail_count', 0))
        
        # 평균 실행 시간 계산
        avg_duration = get_average_duration()
        
        # 리포트 데이터 제한 (최대 20개)
        reports = reports[:20]
        
        # HTML 부분만 렌더링
        reports_html = render_template('reports_partial.html', reports=reports)
        
        # JSON으로 데이터 반환
        return jsonify({
            'html': reports_html,
            'avg_duration': avg_duration,
            'chart': {
                'labels': ['FAIL', 'PASS'],
                'values': [fail_count, pass_count]
            }
        })
        
    except Exception as e:
        print(f"[DEBUG] API reports error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/ci_reports')
def ci_reports():
    """GitHub Actions 테스트 실행 결과 목록을 표시합니다."""
    
    # GitHub API를 통해 워크플로우 실행 결과 가져오기
    repo = "MaduJoe/SnapTest-CICD"  # 적절히 변경
    token = os.environ.get("GITHUB_TOKEN", "")
    
    print(f"Fetching workflow runs from GitHub API")
    print(f"Using authentication: {'Yes' if token else 'No'}")
    
    url = f"https://api.github.com/repos/{repo}/actions/runs"
    headers = {"Authorization": f"token {token}"} if token else {}
    
    try:
        import requests
        response = requests.get(url, headers=headers)
        print(f"API Response status: {response.status_code}")
        
        workflows = []
        if response.status_code == 200:
            data = response.json()
            print(f"Total workflow runs found: {len(data.get('workflow_runs', []))}")
            workflows = data.get("workflow_runs", [])
            
            # 디버깅을 위해 첫 번째 워크플로우 실행의 일부 정보 출력
            if workflows:
                first_run = workflows[0]
                print(f"First workflow: {first_run.get('name')} (ID: {first_run.get('id')})")
                print(f"Status: {first_run.get('status')}, Conclusion: {first_run.get('conclusion')}")
            
            return render_template('ci_reports.html', workflows=workflows, github_repo=repo)
        else:
            error_msg = f"Error fetching data: {response.status_code}"
            if response.status_code == 401:
                error_msg += " - Authorization failed. Check your token."
            elif response.status_code == 404:
                error_msg += f" - Repository '{repo}' not found or you don't have access."
            
            print(error_msg)
            try:
                print(f"Error response: {response.json()}")
            except:
                print("Could not parse error response as JSON")
                
            # API 호출에 실패한 경우 로컬 파일 기반 보고서로 대체
            reports = []
            
            # reports 디렉토리가 존재하면 파일 목록을 가져옵니다
            if os.path.exists('reports'):
                json_files = [f for f in os.listdir('reports') if f.startswith('test_report_') and f.endswith('.json')]
                
                # 최신 파일부터 정렬
                json_files.sort(reverse=True)
                
                for idx, filename in enumerate(json_files):
                    try:
                        with open(os.path.join('reports', filename), 'r', encoding='utf-8') as f:
                            results = json.load(f)
                            
                            # 파일명에서 타임스탬프 추출
                            timestamp = filename.replace('test_report_', '').replace('.json', '')
                            formatted_timestamp = f"{timestamp[0:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
                            
                            # 통계 계산
                            total_tests = len(results)
                            pass_count = sum(1 for r in results if r['result']['status'] == 'PASS')
                            fail_count = total_tests - pass_count
                            success_rate = round((pass_count / total_tests * 100) if total_tests > 0 else 0, 2)
                            
                            reports.append({
                                'id': idx + 1,
                                'filename': filename,
                                'timestamp': formatted_timestamp,
                                'total_tests': total_tests,
                                'pass_count': pass_count,
                                'fail_count': fail_count,
                                'success_rate': success_rate
                            })
                    except Exception as e:
                        print(f"Error processing CI report {filename}: {str(e)}")
            
            # GitHub 저장소 정보 (있는 경우)
            github_repo = os.getenv('GITHUB_REPOSITORY', repo)
            
            # 에러 메시지와 함께 기존 템플릿 사용
            flash(error_msg, 'error')
            return render_template('ci_reports.html', reports=reports, github_repo=github_repo, workflows=[])
    
    except Exception as e:
        print(f"Error in ci_reports route: {str(e)}")
        flash(f"GitHub API 호출 중 오류가 발생했습니다: {str(e)}", "error")
        
        # 오류 발생 시 로컬 파일 기반 보고서로 대체
        reports = []
        
        # reports 디렉토리가 존재하면 파일 목록을 가져옵니다
        if os.path.exists('reports'):
            json_files = [f for f in os.listdir('reports') if f.startswith('test_report_') and f.endswith('.json')]
            
            # 최신 파일부터 정렬
            json_files.sort(reverse=True)
            
            for idx, filename in enumerate(json_files):
                try:
                    with open(os.path.join('reports', filename), 'r', encoding='utf-8') as f:
                        results = json.load(f)
                        
                        # 파일명에서 타임스탬프 추출
                        timestamp = filename.replace('test_report_', '').replace('.json', '')
                        formatted_timestamp = f"{timestamp[0:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
                        
                        # 통계 계산
                        total_tests = len(results)
                        pass_count = sum(1 for r in results if r['result']['status'] == 'PASS')
                        fail_count = total_tests - pass_count
                        success_rate = round((pass_count / total_tests * 100) if total_tests > 0 else 0, 2)
                        
                        reports.append({
                            'id': idx + 1,
                            'filename': filename,
                            'timestamp': formatted_timestamp,
                            'total_tests': total_tests,
                            'pass_count': pass_count,
                            'fail_count': fail_count,
                            'success_rate': success_rate
                        })
                except Exception as e:
                    print(f"Error processing CI report {filename}: {str(e)}")
        
        # GitHub 저장소 정보 (있는 경우)
        github_repo = os.getenv('GITHUB_REPOSITORY', repo)
        
        return render_template('ci_reports.html', reports=reports, github_repo=github_repo, workflows=[])

@app.route('/ci_reports/<int:report_id>')
def view_ci_report(report_id):
    """특정 GitHub Actions 테스트 실행 결과의 상세 내용을 표시합니다."""
    
    # reports 디렉토리가 존재하는지 확인합니다
    if not os.path.exists('reports'):
        flash('테스트 보고서 디렉토리가 존재하지 않습니다.', 'error')
        return redirect(url_for('ci_reports'))
    
    # 모든 JSON 보고서 파일 찾기
    json_files = [f for f in os.listdir('reports') if f.startswith('test_report_') and f.endswith('.json')]
    json_files.sort(reverse=True)
    
    # 해당 ID의 보고서가 존재하는지 확인
    if report_id <= 0 or report_id > len(json_files):
        flash('존재하지 않는 보고서 ID입니다.', 'error')
        return redirect(url_for('ci_reports'))
    
    filename = json_files[report_id - 1]
    
    try:
        with open(os.path.join('reports', filename), 'r', encoding='utf-8') as f:
            results = json.load(f)
            
            # 파일명에서 타임스탬프 추출
            timestamp = filename.replace('test_report_', '').replace('.json', '')
            formatted_timestamp = f"{timestamp[0:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
            
            # 통계 계산
            total_tests = len(results)
            pass_count = sum(1 for r in results if r['result']['status'] == 'PASS')
            fail_count = total_tests - pass_count
            success_rate = round((pass_count / total_tests * 100) if total_tests > 0 else 0, 2)
            
            # 테스트 결과 형식 정리
            test_results = []
            for result in results:
                test_results.append({
                    'name': result['test_case']['name'],
                    'function': result['test_case']['test_function'],
                    'status': result['result']['status'],
                    'details': result['result'].get('result', ''),
                    'error': result['result'].get('error', '')
                })
            
            report = {
                'id': report_id,
                'filename': filename,
                'timestamp': formatted_timestamp,
                'total_tests': total_tests,
                'pass_count': pass_count,
                'fail_count': fail_count,
                'success_rate': success_rate,
                'test_results': test_results,
                'branch': os.getenv('GITHUB_REF', '').replace('refs/heads/', ''),
                'commit_hash': os.getenv('GITHUB_SHA', ''),
                'workflow_run_url': os.getenv('GITHUB_SERVER_URL', '') + '/' + os.getenv('GITHUB_REPOSITORY', '') + '/actions/runs/' + os.getenv('GITHUB_RUN_ID', '') if os.getenv('GITHUB_RUN_ID') else None
            }
            
            return render_template('view_ci_report.html', report=report)
    except Exception as e:
        flash(f'보고서를 읽는 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('ci_reports'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 