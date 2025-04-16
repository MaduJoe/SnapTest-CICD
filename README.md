# 🧪 TOSSIFY QA

**TOSSIFY QA**는 테스트 케이스 생성부터 실행, 결과 분석, 보고서 생성까지 QA 업무 전반을 자동화하는 플랫폼입니다.
효율적이고 체계적인 QA 프로세스를 통해 소프트웨어 품질을 향상시키는 것을 목표로 합니다.

## 🌟 주요 기능

* 🔄 **자동화된 테스트 관리 및 실행**
  * 테스트 케이스 CRUD 및 배치 실행
  * 백그라운드 큐 시스템을 통한 비동기 테스트 처리
  * 일일 전체 테스트 자동 스케줄링

* 📊 **데이터 분석 및 시각화**
  * 직관적인 대시보드로 테스트 결과 모니터링
  * 테스트 케이스별 성공률 및 통계 데이터
  * 세부 리포트 및 로그 분석

* 🤖 **AI 기반 테스트 케이스 생성**
  * OpenAI API를 활용한 자동 테스트 케이스 생성
  * 복잡한 테스트 시나리오 자동화

## 🧱 시스템 아키텍처

```
[웹 브라우저] <---- HTTP ----> [Flask 웹 서버 (app.py)]
                                 |         |
                                 |         |
[테스트 케이스 저장소] <-------> |         | <--------> [데이터베이스 (SQLite)]
   (cases/*.json)                |         |                (tossify.db)
                                 |         |
                                 v         v
                            [테스트 실행 엔진]
                          (runner.py, tests/functions.py)
                                 |
                                 v
                            [백그라운드 워커]
                            (background_worker.py)
                                 |
                                 v
                            [테스트 리포트]
                             (reports/)
```

## 🔄 데이터 흐름

1. 사용자가 웹 UI를 통해 테스트 케이스를 생성하거나 기존 케이스를 선택하여 실행합니다.
2. 선택된 테스트 케이스는 큐(Queue)에 추가되어 백그라운드 워커가 비동기적으로 처리합니다.
3. 테스트 실행 엔진이 케이스별 테스트 함수를 호출하고 결과를 수집합니다.
4. 테스트 결과는 데이터베이스에 저장되고 JSON 형식의 보고서로도 출력됩니다.
5. 사용자는 대시보드를 통해 전체 테스트 현황과 상세 리포트를 확인할 수 있습니다.

## 📁 프로젝트 구조

```
tossify-qa/
├── app.py                  # 메인 Flask 애플리케이션 (웹 서버 및 라우팅)
├── db.py                   # 데이터베이스 연결 및 조작 함수
├── runner.py               # 테스트 케이스 실행 핵심 로직
├── background_worker.py    # 백그라운드 테스트 실행 및 스케줄링
├── utils.py                # 유틸리티 함수
├── tossify.db              # SQLite 데이터베이스
├── cases/                  # 테스트 케이스 (JSON 형식)
├── reports/                # 테스트 실행 결과 리포트
├── tests/                  # 테스트 로직 및 함수
│   └── functions.py        # 테스트 함수 모음
├── templates/              # Flask HTML 템플릿
│   ├── index.html          # 홈페이지
│   ├── dashboard.html      # 결과 대시보드
│   ├── reports.html        # 리포트 목록
│   ├── report_detail.html  # 상세 리포트
│   ├── add_case.html       # 테스트 케이스 추가
│   ├── edit_case.html      # 테스트 케이스 편집
│   └── ai_case_form.html   # AI 기반 케이스 생성
└── static/                 # 정적 파일 (CSS, JS, 이미지 등)
```

## 🧩 핵심 컴포넌트

### 1. 웹 애플리케이션 (app.py)
- Flask 기반 웹 서버로 사용자 인터페이스 제공
- 테스트 케이스 관리, 실행, 리포트 조회 등의 라우팅 처리
- OpenAI API를 활용한 AI 기반 테스트 케이스 생성 기능

### 2. 데이터베이스 관리 (db.py)
- SQLite 데이터베이스 초기화 및 연결 
- 테스트 결과 및 통계 데이터 저장/조회
- 테스트 케이스별 실행 통계 관리

### 3. 테스트 실행 엔진 (runner.py)
- 테스트 케이스 파일(JSON) 로드 및 파싱
- 동적 테스트 함수 호출 및 실행 결과 수집
- 리포트 생성 및 저장

### 4. 백그라운드 워커 (background_worker.py)
- 비동기 테스트 실행을 위한 큐 시스템
- 일일 자동 테스트 스케줄링
- 다중 테스트의 병렬 처리

### 5. 테스트 함수 (tests/functions.py)
- 실제 테스트 로직이 구현된 함수 모음
- 각 테스트 케이스에서 지정된 함수 호출
- 결과 검증 및 상태 반환

## 🔍 테스트 케이스 형식

테스트 케이스는 JSON 형식으로 저장되며 다음과 같은 구조를 갖습니다:

```json
{
  "name": "테스트 케이스 이름",
  "description": "테스트 케이스에 대한 설명",
  "test_function": "호출할 테스트 함수 이름",
  "parameters": {
    "param1": "값1",
    "param2": "값2",
    "expected": "기대 결과값"
  }
}
```

## 🚀 시작하기

### 사전 요구사항
- Python 3.8 이상
- Flask 및 관련 패키지
- OpenAI API 키 (AI 기능 사용 시)

### 설치 및 실행
```bash
# 저장소 복제
git clone https://github.com/yourusername/tossify-qa.git
cd tossify-qa

# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
python app.py
```

### 접속 방법
기본적으로 http://localhost:5000 에서 웹 인터페이스에 접속할 수 있습니다.

## 📝 사용 방법

1. **테스트 케이스 작성**: 
   - 웹 인터페이스의 "Add Case" 메뉴를 통해 수동으로 작성
   - AI 기능을 사용하여 자동 생성
   - JSON 파일을 직접 `cases/` 디렉토리에 추가

2. **테스트 실행**:
   - 홈페이지에서 실행할 테스트 케이스 선택 후 "Run" 버튼 클릭
   - 백그라운드에서 테스트가 실행되며 결과는 자동으로 저장

3. **결과 확인**:
   - 대시보드에서 전체 테스트 현황 및 통계 확인
   - 개별 리포트 페이지에서 상세 결과 및 로그 조회
   - 필요시 로그 파일 다운로드 가능

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📞 연락처

**Jaekeun Cho**  
�� jaekeunv@gmail.com 
