# 🧪 TOSSIFY QA

**TOSSIFY QA**는 테스트 케이스 생성부터 실행, 결과 분석, 보고서 생성까지 QA 업무 전반을 자동화하는 플랫폼입니다.
효율적이고 체계적인 QA 프로세스를 통해 소프트웨어 품질을 향상시키는 것을 목표로 합니다.

---

## 주요 기능

* 🤖 **자동화된 테스트 케이스 관리**
* 🌐 **다양한 환경에서의 테스트 실행**
* 📊 **실시간 테스트 결과 모니터링**
* ✍️ **직관적인 테스트 케이스 편집**
* 🧾 **상세한 테스트 리포트 생성**
* 🔄 **CI/CD 파이프라인 통합**

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | Python, FastAPI |
| Frontend | React, TypeScript |
| Database | PostgreSQL |
| Testing | Pytest, Selenium |
| CI/CD | GitHub Actions |
| Documentation | Swagger/OpenAPI |

---

## 시작하기

### 사전 요구사항

* Python 3.8+
* Node.js 16+
* PostgreSQL 13+

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/tossify-qa.git
cd tossify-qa

# Python 의존성 설치
pip install -r requirements.txt

# Node.js 의존성 설치
npm install
```

### 환경 설정

1. `.env` 파일 생성:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/tossify_qa
API_KEY=your_api_key
```

2. 데이터베이스 마이그레이션:
```bash
python manage.py migrate
```

### 실행

```bash
# 백엔드 서버 실행
python app.py

# 프론트엔드 개발 서버 실행
npm run dev
```

---

## 프로젝트 구조

```
tossify-qa/
├── app/                  # 백엔드 애플리케이션
│   ├── api/             # API 엔드포인트
│   ├── models/          # 데이터베이스 모델
│   └── services/        # 비즈니스 로직
├── frontend/            # 프론트엔드 애플리케이션
│   ├── components/      # React 컴포넌트
│   ├── pages/          # 페이지 컴포넌트
│   └── utils/          # 유틸리티 함수
├── tests/              # 테스트 코드
└── docs/               # 문서
```

---

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🧭 시스템 아키텍처 및 흐름도

```
[User - Web Browser]
      │
      ▼
[Flask Web UI (HTML Templates)]
      │
      ├── 테스트케이스 선택 및 실행 요청
      │
      └─▶ Flask 백엔드 서버 (app.py)
              │
              ├── 테스트 케이스 파일 로딩 (cases/*.json)
              ├── 실행 요청을 큐에 저장 (test_queue)
              │
              ▼
      [Background Worker (background_worker.py)]
              │
              └─▶ Test Runner 실행 (runner.py)
                      │
                      ├── 외부 API 호출 (필요 시)
                      ├── 로그 생성 및 결과 기록
                      └── DB에 테스트 결과 저장
                              │
                              ▼
                    [PostgreSQL DB]
                        ▲       ▲
                        │       └── CRUD 처리 (db.py)
                        │
      [Flask Web UI]
              │
              ├── 대시보드에서 결과 조회
              ├── 리포트 다운로드
              └── 테스트케이스 등록/편집/삭제

(OpenAI API 연동 시)
      │
      └─▶ OpenAI API 호출 (자동 테스트케이스 생성 등)
```

## 연락처

**Jaekeun Cho**  
📧 jaekeunv@gmail.com  
🔗 GitHub: [github.com/yourusername](https://github.com/yourusername)

---
